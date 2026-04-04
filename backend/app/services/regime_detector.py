"""
Regime Detector - Determines current market regime
Selects which strategy should be active based on market conditions
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timezone
from enum import Enum

from . import indicators as ta

logger = logging.getLogger(__name__)


class MarketRegime(str, Enum):
    TRENDING_BULL = "trending_bull"
    TRENDING_BEAR = "trending_bear"
    RANGING = "ranging"
    COMPRESSION = "compression"
    VOLATILE = "volatile"


class RegimeDetector:
    """
    Detects market regime to select the appropriate strategy:
    - TRENDING_BULL → Alpha (Momentum Rider)
    - RANGING → Beta (Range Scalper)
    - COMPRESSION → Gamma (Breakout Hunter)
    - TRENDING_BEAR → Stay in cash / reduce exposure
    - VOLATILE → Reduce position sizes across all strategies
    """

    def __init__(self):
        self.current_regime = MarketRegime.RANGING
        self.regime_history = []
        self.last_update = None

    def detect(
        self,
        btc_klines: list,
        market_data: Dict,
    ) -> MarketRegime:
        """
        Detect current market regime based on BTC analysis.
        Returns the detected regime.
        """
        if len(btc_klines) < 60:
            logger.warning(
                "Not enough BTC data for regime detection, defaulting to ranging"
            )
            self.current_regime = MarketRegime.RANGING
            return self.current_regime

        closes = [k["close"] for k in btc_klines]
        highs = [k["high"] for k in btc_klines]
        lows = [k["low"] for k in btc_klines]
        volumes = [k["volume"] for k in btc_klines]

        # === TREND DETECTION ===
        ema20 = ta.ema(closes, 20)
        ema50 = ta.ema(closes, 50)
        ema200 = ta.ema(closes, 200)

        current_price = closes[-1]
        is_above_ema200 = ema200 and current_price > ema200[-1]
        ema20_above_50 = ema20 and ema50 and ema20[-1] > ema50[-1]
        ema_divergence = (
            abs(ema20[-1] - ema50[-1]) / ema50[-1]
            if ema20 and ema50 and ema50[-1] > 0
            else 0
        )

        # === VOLATILITY ===
        atr_val = ta.atr(highs, lows, closes, 14)
        atr_50 = ta.atr(highs, lows, closes, 50)
        atr_ratio = atr_val / atr_50 if atr_val and atr_50 and atr_50 > 0 else 1.0

        # === VOLUME ANALYSIS ===
        avg_vol_7d = (
            sum(volumes[-42:]) / 7
            if len(volumes) >= 42
            else sum(volumes) / max(len(volumes), 1)
        )
        current_vol = volumes[-1]
        vol_ratio = current_vol / avg_vol_7d if avg_vol_7d > 0 else 1.0

        # === REGIME CLASSIFICATION ===
        # Check for extreme volatility first
        if atr_ratio > 2.0:
            regime = MarketRegime.VOLATILE
        # Check for compression (low volatility, tight range)
        elif atr_ratio < 0.55:
            bb = ta.bollinger_bands(closes)
            if bb["width"] > 0:
                regime = MarketRegime.COMPRESSION
            else:
                regime = MarketRegime.RANGING
        # Check for clear trend
        elif is_above_ema200 and ema20_above_50 and ema_divergence > 0.01:
            regime = MarketRegime.TRENDING_BULL
        elif not is_above_ema200 and not ema20_above_50 and ema_divergence > 0.01:
            regime = MarketRegime.TRENDING_BEAR
        # Default to ranging
        else:
            regime = MarketRegime.RANGING

        # Track regime changes
        if regime != self.current_regime:
            logger.info(f"Regime change: {self.current_regime.value} → {regime.value}")
            self.regime_history.append(
                {
                    "from": self.current_regime.value,
                    "to": regime.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "atr_ratio": atr_ratio,
                    "ema_divergence": ema_divergence,
                    "vol_ratio": vol_ratio,
                }
            )

        self.current_regime = regime
        self.last_update = datetime.now(timezone.utc)

        return regime

    def get_recommended_strategy(self) -> str:
        """Return the recommended strategy name for current regime"""
        mapping = {
            MarketRegime.TRENDING_BULL: "alpha",
            MarketRegime.TRENDING_BEAR: "none",
            MarketRegime.RANGING: "beta",
            MarketRegime.COMPRESSION: "gamma_watch",
            MarketRegime.VOLATILE: "none",
        }
        return mapping.get(self.current_regime, "none")

    def get_position_size_multiplier(self) -> float:
        """Return position size adjustment based on regime"""
        mapping = {
            MarketRegime.TRENDING_BULL: 1.0,
            MarketRegime.TRENDING_BEAR: 0.0,
            MarketRegime.RANGING: 0.75,
            MarketRegime.COMPRESSION: 0.5,
            MarketRegime.VOLATILE: 0.25,
        }
        return mapping.get(self.current_regime, 0.5)

    def get_status(self) -> Dict:
        """Get current regime status"""
        return {
            "regime": self.current_regime.value,
            "recommended_strategy": self.get_recommended_strategy(),
            "position_size_multiplier": self.get_position_size_multiplier(),
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "regime_changes": len(self.regime_history),
            "recent_changes": self.regime_history[-5:] if self.regime_history else [],
        }
