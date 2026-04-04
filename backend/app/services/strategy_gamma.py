"""
Strategy Gamma - Breakout Hunter v2.0
Captures explosive directional moves after prolonged volatility compression
Low win rate (35-42%) but asymmetric R/R makes it profitable
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

from . import indicators as ta

logger = logging.getLogger(__name__)


class GammaBreakoutHunter:
    """
    Estrategia Gamma: Breakout Hunter v2.0

    Captura movimientos violentos tras compresión de volatilidad.
    - Liquidez extrema: volumen 7d > $15M
    - BTC EMA20 > EMA50 en 4H
    - Compresión: ATR(10)/ATR(50) < 0.55 por 8+ velas
    - Score >= 7 puntos
    - SL: vuelta al rango (-1.5%)
    - Trailing: 1.5 * ATR tras +2 * ATR
    - Time exit: 72h sin +2 ATR → cerrar
    """

    NAME = "Gamma - Breakout Hunter v2.0"
    TIMEFRAME = "1h"
    MIN_SCORE = 7

    def __init__(self):
        self.atr_fast = 10
        self.atr_slow = 50
        self.compression_threshold = 0.55
        self.compression_min_candles = 8
        self.risk_per_trade = 0.01  # 1% of capital
        self.trailing_atr_mult = 1.5
        self.time_exit_hours = 72
        self.min_atr_profit = 2.0

    def _check_compression(self, klines: List[Dict]) -> bool:
        """Check if price has been in volatility compression"""
        if len(klines) < self.atr_slow + self.compression_min_candles:
            return False

        highs = [k["high"] for k in klines]
        lows = [k["low"] for k in klines]
        closes = [k["close"] for k in klines]

        # Check ATR ratio for last N candles
        compression_count = 0
        for i in range(len(closes) - self.compression_min_candles, len(closes)):
            atr_fast_val = ta.atr(
                highs[: i + 1], lows[: i + 1], closes[: i + 1], self.atr_fast
            )
            atr_slow_val = ta.atr(
                highs[: i + 1], lows[: i + 1], closes[: i + 1], self.atr_slow
            )
            if atr_fast_val and atr_slow_val and atr_slow_val > 0:
                ratio = atr_fast_val / atr_slow_val
                if ratio < self.compression_threshold:
                    compression_count += 1

        return compression_count >= self.compression_min_candles

    def _check_bollinger_squeeze(self, closes: List[float]) -> bool:
        """Check if Bollinger Bands are at lowest 20 percentile"""
        if len(closes) < 120:
            return True  # Assume squeeze if not enough data

        bbw_values = []
        for i in range(100, len(closes) + 1):
            bb = ta.bollinger_bands(closes[:i])
            bbw_values.append(bb["width"])

        if not bbw_values:
            return True

        current_bbw = ta.bollinger_bands(closes)["width"]
        p20 = ta.percentile(bbw_values, 20)
        return current_bbw <= p20 * 1.1

    def evaluate(
        self,
        symbol: str,
        klines: List[Dict],
        btc_klines: List[Dict],
        current_price: float,
        capital: float,
    ) -> Optional[Dict]:
        """Evaluate breakout entry conditions"""
        if len(klines) < 60:
            return None

        closes = [k["close"] for k in klines]
        highs = [k["high"] for k in klines]
        lows = [k["low"] for k in klines]
        volumes = [k["volume"] for k in klines]

        # === FILTRO A: Liquidity ===
        quote_volumes = [
            k.get("quote_volume", k["volume"] * closes[i]) for i, k in enumerate(klines)
        ]
        avg_daily_volume = sum(quote_volumes[-42:]) / 7  # Last 7 days (42 4h candles)
        if avg_daily_volume < 15000000:  # $15M minimum
            return None

        # === FILTRO B: BTC alignment ===
        btc_closes = [k["close"] for k in btc_klines]
        btc_ema20 = ta.ema(btc_closes, 20)
        btc_ema50 = ta.ema(btc_closes, 50)
        if not btc_ema20 or not btc_ema50:
            return None
        if btc_ema20[-1] <= btc_ema50[-1]:
            return None  # BTC not in uptrend

        # === FILTRO C: Compression ===
        if not self._check_compression(klines):
            return None
        if not self._check_bollinger_squeeze(closes):
            return None

        # === DETECT BREAKOUT ===
        # Find resistance level (highest of last 20 candles)
        resistance_20 = ta.highest(highs, 20)
        if resistance_20 is None:
            return None

        # Check if price just broke above resistance
        if closes[-1] <= resistance_20:
            return None  # No breakout yet

        # === SCORING ===
        score = 0
        reasons = []

        # +2: Historical recent breakout
        score += 2
        reasons.append(f"Rotura de máximo de 20 velas ({resistance_20:.2f})")

        # +2: Volume anomaly
        avg_volume = (
            sum(volumes[-30:]) / min(30, len(volumes))
            if len(volumes) >= 30
            else sum(volumes) / len(volumes)
        )
        if volumes[-1] > 2.0 * avg_volume:
            score += 2
            reasons.append(
                f"Anomalía de volumen ({volumes[-1] / avg_volume:.1f}x media)"
            )
        else:
            score += 1
            reasons.append("Volumen por encima de la media")

        # +1: Volatility expansion
        atr_val = ta.atr(highs, lows, closes, 14)
        if atr_val:
            sum_last_5_atr = 0
            for i in range(len(closes) - 5, len(closes)):
                a = ta.atr(highs[: i + 1], lows[: i + 1], closes[: i + 1], 14)
                if a:
                    sum_last_5_atr += a
            if atr_val > sum_last_5_atr:
                score += 1
                reasons.append("Expansión de volatilidad en vela de ruptura")

        # +1: Intra-candle dominance
        last_kline = klines[-1]
        body = abs(last_kline["close"] - last_kline["open"])
        total_range = last_kline["high"] - last_kline["low"]
        if total_range > 0 and body / total_range > 0.6:
            score += 1
            reasons.append("Cierre fuerte cerca del máximo")

        # +2: Compression validated (already passed filter C)
        score += 2
        reasons.append("Compresión previa validada")

        if score < self.MIN_SCORE:
            return None

        # === RISK CALCULATION ===
        # Limit order at 0.2% pullback
        limit_entry = current_price * 0.998
        # Hard stop: back into range
        sl_price = resistance_20 * 0.985  # 1.5% below breakout
        sl_distance = limit_entry - sl_price

        risk_usd = capital * self.risk_per_trade
        position_size = risk_usd / sl_distance if sl_distance > 0 else 0
        position_value = position_size * limit_entry

        # Next resistance target (8-10% minimum)
        tp_distance = current_price * 0.10  # Assume 10% target
        risk_reward = tp_distance / sl_distance if sl_distance > 0 else 0

        return {
            "strategy": self.NAME,
            "symbol": symbol,
            "type": "LONG",
            "score": score,
            "reasons": reasons,
            "entry_price": limit_entry,
            "stop_loss": sl_price,
            "take_profit": current_price + tp_distance,
            "position_size": position_size,
            "position_value": position_value,
            "risk_usd": risk_usd,
            "risk_reward": risk_reward,
            "atr": atr_val,
            "resistance_level": resistance_20,
            "order_type": "limit_pullback",
            "order_timeout_minutes": 45,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def check_exit(
        self,
        position: Dict,
        klines: List[Dict],
        current_price: float,
    ) -> Optional[Dict]:
        """Check exit conditions for breakout position"""
        entry = position["entry_price"]
        sl = position["stop_loss"]
        atr_val = position.get("atr", 0)
        opened_at = position.get("opened_at", "")

        # Hard stop: back into range
        if current_price <= sl:
            return {
                "reason": "stop_loss_cancelation",
                "price": current_price,
                "pnl_percent": (current_price - entry) / entry * 100,
            }

        # Trailing stop after +2 ATR
        if atr_val > 0:
            highest = position.get("highest_price", entry)
            if current_price >= entry + self.min_atr_profit * atr_val:
                trailing_sl = highest - self.trailing_atr_mult * atr_val
                if current_price <= trailing_sl:
                    return {
                        "reason": "trailing_stop",
                        "price": current_price,
                        "pnl_percent": (current_price - entry) / entry * 100,
                    }

        # Time-based exit: 72 hours without +2 ATR profit
        if opened_at:
            try:
                opened_time = datetime.fromisoformat(opened_at.replace("Z", "+00:00"))
                hours_open = (
                    datetime.now(timezone.utc) - opened_time
                ).total_seconds() / 3600
                if hours_open >= self.time_exit_hours:
                    min_profit = entry + self.min_atr_profit * (
                        atr_val or (entry * 0.02)
                    )
                    if current_price < min_profit:
                        return {
                            "reason": "time_exit_zombie",
                            "price": current_price,
                            "pnl_percent": (current_price - entry) / entry * 100,
                        }
            except (ValueError, TypeError):
                pass

        return None
