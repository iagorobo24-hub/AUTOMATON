"""
Strategy Alpha - Momentum Rider v2.0
Trend-following strategy that captures bullish trends in crypto
Uses BTC macro filter, ATR-based stops, trailing stops
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

from . import indicators as ta

logger = logging.getLogger(__name__)


class AlphaMomentumRider:
    """
    Estrategia Alpha: Momentum Rider v2.0

    Captura tendencias alcistas consolidadas.
    - Filtro BTC: precio > EMA200 en 4H
    - ATR-based position sizing (1% riesgo)
    - Trailing stops a 1.5x ATR
    - TP parcial a 2x ATR (50% posicion)
    - Score de entrada >= 5 puntos
    """

    NAME = "Alpha - Momentum Rider v2.0"
    TIMEFRAME = "1h"
    MIN_SCORE = 5

    def __init__(self):
        self.atr_period = 14
        self.rsi_period = 14
        self.btc_ema_period = 50  # Reduced for testnet/limited data
        self.atr_sl_multiplier = 1.5
        self.atr_tp_multiplier = 2.0
        self.partial_close_percent = 0.5
        self.trailing_atr_mult = 1.5
        self.risk_per_trade = 0.01  # 1% of capital

    def evaluate(
        self,
        symbol: str,
        klines: List[Dict],
        btc_klines: List[Dict],
        current_price: float,
        capital: float,
    ) -> Optional[Dict]:
        """
        Evaluate entry conditions for a symbol.
        Returns signal dict if score >= MIN_SCORE, else None.
        """
        if len(klines) < 30:
            return None

        closes = [k["close"] for k in klines]
        highs = [k["high"] for k in klines]
        lows = [k["low"] for k in klines]
        volumes = [k["volume"] for k in klines]

        # === FILTRO A: BTC Macro ===
        btc_closes = [k["close"] for k in btc_klines]
        btc_ema200 = ta.ema(btc_closes, self.btc_ema_period)
        if not btc_ema200:
            return None
        btc_current = btc_closes[-1]
        if btc_current < btc_ema200[-1]:
            return None  # BTC below EMA200, skip

        # Check BTC crash protection
        for i in range(-8, 0):
            if len(btc_closes) >= abs(i) + 1:
                candle_drop = (btc_closes[i] - btc_closes[i - 1]) / btc_closes[i - 1]
                if candle_drop < -0.04:  # >4% drop in single candle
                    return None

        # === FILTRO B: Volatility Expansion ===
        atr_val = ta.atr(highs, lows, closes, self.atr_period)
        if atr_val is None or atr_val == 0:
            return None

        atr_60d_values = []
        for i in range(60, len(closes)):
            a = ta.atr(highs[: i + 1], lows[: i + 1], closes[: i + 1], self.atr_period)
            if a:
                atr_60d_values.append(a)
        atr_p25 = ta.percentile(atr_60d_values, 25) if atr_60d_values else atr_val * 0.5
        if atr_val < atr_p25:
            return None  # Compression detected, skip

        # Check minimum range
        last_5_amplitude = (
            sum(abs(closes[i] - closes[i - 1]) for i in range(-5, 0)) / closes[-1]
        )
        if last_5_amplitude < 0.015:  # 1.5% minimum
            return None

        # === SCORING ===
        score = 0
        reasons = []

        # +2: Media structure
        ema20 = ta.ema(closes, 20)
        ema50 = ta.ema(closes, 50)
        if ema20 and ema50 and closes[-1] > ema20[-1] and ema20[-1] > ema50[-1]:
            score += 2
            reasons.append("Estructura de medias alcista")

        # +2: Higher highs / higher lows
        if ta.is_higher_highs(closes, highs, 3):
            score += 2
            reasons.append("Máximos y mínimos crecientes")

        # +1: RSI momentum
        rsi_val = ta.rsi(closes, self.rsi_period)
        if rsi_val is not None:
            rsi_prev = (
                ta.rsi(closes[:-1], self.rsi_period)
                if len(closes) > self.rsi_period + 1
                else None
            )
            if rsi_prev is not None and rsi_val > rsi_prev:
                score += 1
                reasons.append(f"RSI en pendiente positiva ({rsi_val:.1f})")

        # +1: MACD confirmation
        macd_data = ta.macd(closes)
        if macd_data["histogram"] > 0:
            hist_series = macd_data.get("histogram_series", [])
            if len(hist_series) >= 2:
                if hist_series[-1] >= hist_series[-2]:
                    score += 1
                    reasons.append("MACD histogram positivo y creciente")
            else:
                score += 1
                reasons.append("MACD histogram positivo")

        # +1: Volume adjusted
        avg_volume = (
            sum(volumes[-30:]) / min(30, len(volumes))
            if len(volumes) >= 30
            else sum(volumes) / len(volumes)
        )
        current_volume = volumes[-1]
        if current_volume > 1.2 * avg_volume:
            score += 1
            reasons.append(
                f"Volumen superior a la media ({current_volume / avg_volume:.1f}x)"
            )

        if score < self.MIN_SCORE:
            return None

        # === RISK CALCULATION ===
        sl_distance = self.atr_sl_multiplier * atr_val
        sl_price = current_price - sl_distance
        tp_price = current_price + self.atr_tp_multiplier * atr_val
        risk_usd = capital * self.risk_per_trade
        position_size = risk_usd / sl_distance if sl_distance > 0 else 0
        position_value = position_size * current_price
        risk_reward = (
            (tp_price - current_price) / (current_price - sl_price)
            if sl_price < current_price
            else 0
        )

        return {
            "strategy": self.NAME,
            "symbol": symbol,
            "type": "LONG",
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
            "rsi": rsi_val,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def check_exit(
        self,
        position: Dict,
        klines: List[Dict],
        current_price: float,
    ) -> Optional[Dict]:
        """
        Check exit conditions for an open position.
        Returns exit reason dict if should close, else None.
        """
        if len(klines) < 20:
            return None

        closes = [k["close"] for k in klines]
        highs = [k["high"] for k in klines]
        lows = [k["low"] for k in klines]
        atr_val = ta.atr(highs, lows, closes, self.atr_period)
        if atr_val is None:
            return None

        entry = position["entry_price"]
        sl = position["stop_loss"]
        highest_price = position.get("highest_price", entry)

        # Hard stop loss hit
        if current_price <= sl:
            return {
                "reason": "stop_loss",
                "price": current_price,
                "pnl_percent": (current_price - entry) / entry * 100,
            }

        # Partial TP at 2x ATR
        tp_level = entry + self.atr_tp_multiplier * atr_val
        if current_price >= tp_level and not position.get("partial_closed", False):
            return {
                "reason": "partial_take_profit",
                "price": current_price,
                "close_percent": self.partial_close_percent,
                "pnl_percent": (current_price - entry) / entry * 100,
            }

        # Trailing stop (after partial close or if price moved up)
        if current_price > entry:
            trailing_sl = highest_price - self.trailing_atr_mult * atr_val
            if current_price <= trailing_sl:
                return {
                    "reason": "trailing_stop",
                    "price": current_price,
                    "pnl_percent": (current_price - entry) / entry * 100,
                }

        # Emergency exit: bearish divergence
        rsi_val = ta.rsi(closes, self.rsi_period)
        if rsi_val is not None and rsi_val < 30:
            return {
                "reason": "rsi_oversold_divergence",
                "price": current_price,
                "pnl_percent": (current_price - entry) / entry * 100,
            }

        # Score dropped below 3
        quick_check = self.evaluate(
            symbol=position["symbol"],
            klines=klines,
            btc_klines=klines,
            current_price=current_price,
            capital=1000,
        )
        if quick_check and quick_check["score"] < 3:
            return {
                "reason": "score_dropped",
                "price": current_price,
                "pnl_percent": (current_price - entry) / entry * 100,
            }

        return None
