"""
Strategy Beta - Range Scalper v2.0
Mean-reversion strategy for sideways/range-bound markets
Exploits consolidation ranges with 65% target win rate
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

from . import indicators as ta

logger = logging.getLogger(__name__)


class BetaRangeScalper:
    """
    Estrategia Beta: Range Scalper v2.0

    Explota consolidaciones laterales (rangos).
    - BTC debe estar lateral (no trending)
    - Rango >= 3% amplitud, >= 10 velas 4H
    - 2+ toques en soporte/resistencia
    - Score >= 5 puntos
    - SL: 1 * ATR fuera del rango
    - TP: 75-80% del rango hacia el extremo opuesto
    """

    NAME = "Beta - Range Scalper v2.0"
    TIMEFRAME = "1h"
    MIN_SCORE = 5

    def __init__(self):
        self.atr_period = 14
        self.rsi_period = 14
        self.min_range_amplitude = 0.02  # 2% reduced for 1h
        self.min_range_candles = 8  # Reduced from 10
        self.min_touches = 2
        self.risk_per_trade = 0.0075  # 0.75% of capital

    def _detect_range(self, klines: List[Dict]) -> Optional[Dict]:
        """Detect if price is in a range and find support/resistance levels"""
        if len(klines) < self.min_range_candles:
            return None

        recent = klines[-self.min_range_candles :]
        highs = [k["high"] for k in recent]
        lows = [k["low"] for k in recent]

        resistance = max(highs)
        support = min(lows)
        amplitude = (resistance - support) / support

        if amplitude < self.min_range_amplitude:
            return None

        # Count touches
        atr_val = ta.atr(
            [k["high"] for k in klines],
            [k["low"] for k in klines],
            [k["close"] for k in klines],
            self.atr_period,
        )
        if atr_val is None:
            return None

        tolerance = 0.3 * atr_val
        support_touches = sum(1 for l in lows if abs(l - support) <= tolerance)
        resistance_touches = sum(1 for h in highs if abs(h - resistance) <= tolerance)

        if support_touches < self.min_touches or resistance_touches < self.min_touches:
            return None

        return {
            "support": support,
            "resistance": resistance,
            "amplitude": amplitude,
            "support_touches": support_touches,
            "resistance_touches": resistance_touches,
        }

    def evaluate(
        self,
        symbol: str,
        klines: List[Dict],
        btc_klines: List[Dict],
        current_price: float,
        capital: float,
    ) -> Optional[Dict]:
        """Evaluate entry conditions for range scalping"""
        if len(klines) < 20:
            return None

        # === FILTRO A: BTC must be sideways ===
        btc_closes = [k["close"] for k in btc_klines]
        btc_ema20 = ta.ema(btc_closes, 20)
        btc_ema50 = ta.ema(btc_closes, 50)
        if btc_ema20 and btc_ema50:
            # If BTC has a clear trend, skip
            diff_pct = abs(btc_ema20[-1] - btc_ema50[-1]) / btc_ema50[-1]
            if diff_pct > 0.02:  # >2% divergence = trending
                return None

        # Check BTC not making big moves
        for i in range(-3, 0):
            if len(btc_closes) >= abs(i) + 1:
                candle_size = abs(btc_closes[i] - btc_closes[i - 1]) / btc_closes[i - 1]
                if candle_size > 0.015:  # >1.5% candle
                    return None

        # === FILTRO B: Detect range ===
        range_info = self._detect_range(klines)
        if range_info is None:
            return None

        closes = [k["close"] for k in klines]
        highs = [k["high"] for k in klines]
        lows = [k["low"] for k in klines]
        volumes = [k["volume"] for k in klines]
        atr_val = ta.atr(highs, lows, closes, self.atr_period)
        if atr_val is None or atr_val == 0:
            return None

        # Check volatility containment
        atr_20 = ta.atr(highs, lows, closes, 20)
        if atr_20 and atr_val > 2.0 * atr_20:
            return None  # Volatility too high for range

        # === Determine direction and score ===
        support = range_info["support"]
        resistance = range_info["resistance"]
        direction = None
        score = 0
        reasons = []

        # Check if near support (LONG)
        if abs(current_price - support) <= 0.3 * atr_val:
            direction = "LONG"

            # +2: Price precision at support
            score += 2
            reasons.append(f"Precio en soporte ({support:.2f})")

            # +2: Rejection candle (hammer/doji)
            last_kline = klines[-1]
            lower_wick = (
                last_kline["close"] - last_kline["low"]
                if last_kline["close"] > last_kline["low"]
                else last_kline["close"] - last_kline["low"]
            )
            body = abs(last_kline["close"] - last_kline["open"])
            if body > 0 and lower_wick > 2 * body:
                score += 2
                reasons.append("Vela de rechazo en soporte")

            # +1: RSI relatively oversold
            rsi_val = ta.rsi(closes, self.rsi_period)
            if rsi_val is not None:
                rsi_series = ta.rsi_series(closes, self.rsi_period)
                if rsi_series:
                    rsi_p30 = ta.percentile(rsi_series, 30)
                    if rsi_val < rsi_p30:
                        score += 1
                        reasons.append(f"RSI sobrevendido relativo ({rsi_val:.1f})")

            # +1: Volume exhaustion
            avg_vol = (
                sum(volumes[-30:]) / min(30, len(volumes))
                if len(volumes) >= 30
                else sum(volumes) / len(volumes)
            )
            if volumes[-1] < 0.8 * avg_vol:
                score += 1
                reasons.append("Agotamiento de volumen de venta")

            # +1: MACD recovery
            macd_data = ta.macd(closes)
            if macd_data["histogram"] < 0:
                if len(macd_data.get("macd_series", [])) >= 2:
                    macd_s = macd_data["macd_series"]
                    if macd_s[-1] > macd_s[-2]:
                        score += 1
                        reasons.append("MACD en recuperación")

        # Check if near resistance (SHORT)
        elif abs(current_price - resistance) <= 0.3 * atr_val:
            direction = "SHORT"
            score += 2
            reasons.append(f"Precio en resistencia ({resistance:.2f})")

            last_kline = klines[-1]
            upper_wick = last_kline["high"] - last_kline["close"]
            body = abs(last_kline["close"] - last_kline["open"])
            if body > 0 and upper_wick > 2 * body:
                score += 2
                reasons.append("Vela de rechazo en resistencia")

            rsi_val = ta.rsi(closes, self.rsi_period)
            if rsi_val is not None:
                rsi_series = ta.rsi_series(closes, self.rsi_period)
                if rsi_series:
                    rsi_p70 = ta.percentile(rsi_series, 70)
                    if rsi_val > rsi_p70:
                        score += 1
                        reasons.append(f"RSI sobrecomprado relativo ({rsi_val:.1f})")

            avg_vol = (
                sum(volumes[-30:]) / min(30, len(volumes))
                if len(volumes) >= 30
                else sum(volumes) / len(volumes)
            )
            if volumes[-1] < 0.8 * avg_vol:
                score += 1
                reasons.append("Agotamiento de volumen de compra")

            macd_data = ta.macd(closes)
            if macd_data["histogram"] > 0:
                macd_s = macd_data.get("macd_series", [])
                if len(macd_s) >= 2 and macd_s[-1] < macd_s[-2]:
                    score += 1
                    reasons.append("MACD perdiendo fuerza")

        if score < self.MIN_SCORE or direction is None:
            return None

        # === RISK CALCULATION ===
        if direction == "LONG":
            sl_price = support - atr_val
            tp_price = support + (resistance - support) * 0.78  # 78% of range
        else:
            sl_price = resistance + atr_val
            tp_price = resistance - (resistance - support) * 0.78

        risk_usd = capital * self.risk_per_trade
        sl_distance = abs(current_price - sl_price)
        position_size = risk_usd / sl_distance if sl_distance > 0 else 0
        position_value = position_size * current_price
        risk_reward = (
            abs(tp_price - current_price) / sl_distance if sl_distance > 0 else 0
        )

        return {
            "strategy": self.NAME,
            "symbol": symbol,
            "type": direction,
            "score": score,
            "reasons": reasons,
            "entry_price": current_price,
            "stop_loss": sl_price,
            "take_profit": tp_price,
            "position_size": position_size,
            "position_value": position_value,
            "risk_usd": risk_usd,
            "risk_reward": risk_reward,
            "atr": atr_val,
            "range_support": support,
            "range_resistance": resistance,
            "range_amplitude": range_info["amplitude"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def check_exit(
        self,
        position: Dict,
        klines: List[Dict],
        current_price: float,
    ) -> Optional[Dict]:
        """Check exit conditions for range position"""
        if len(klines) < 10:
            return None

        entry = position["entry_price"]
        sl = position["stop_loss"]
        tp = position.get("take_profit", 0)

        # Hard stop loss
        if position["type"] == "LONG" and current_price <= sl:
            return {
                "reason": "stop_loss",
                "price": current_price,
                "pnl_percent": (current_price - entry) / entry * 100,
            }
        if position["type"] == "SHORT" and current_price >= sl:
            return {
                "reason": "stop_loss",
                "price": current_price,
                "pnl_percent": (entry - current_price) / entry * 100,
            }

        # Take profit at 78% of range
        if position["type"] == "LONG" and current_price >= tp:
            return {
                "reason": "take_profit",
                "price": current_price,
                "pnl_percent": (current_price - entry) / entry * 100,
            }
        if position["type"] == "SHORT" and current_price <= tp:
            return {
                "reason": "take_profit",
                "price": current_price,
                "pnl_percent": (entry - current_price) / entry * 100,
            }

        # Breakout: range invalidation
        closes = [k["close"] for k in klines]
        volumes = [k["volume"] for k in klines]
        avg_vol = (
            sum(volumes[-30:]) / min(30, len(volumes)) if len(volumes) >= 30 else 1
        )
        support = position.get("range_support", 0)
        resistance = position.get("range_resistance", 0)

        if (
            resistance > 0
            and closes[-1] > resistance * 1.005
            and volumes[-1] > avg_vol * 1.5
        ):
            return {
                "reason": "range_breakout",
                "price": current_price,
                "pnl_percent": (current_price - entry) / entry * 100,
            }
        if support > 0 and closes[-1] < support * 0.995 and volumes[-1] > avg_vol * 1.5:
            return {
                "reason": "range_breakdown",
                "price": current_price,
                "pnl_percent": (current_price - entry) / entry * 100,
            }

        return None
