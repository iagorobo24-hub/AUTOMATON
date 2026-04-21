"""
Risk Manager - Centralized risk control with circuit breaker
Protects capital across all agents and strategies
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Centralized risk management:
    - Daily loss limit: 2% of total portfolio
    - Per-agent loss limit: 10% of agent capital
    - Max concurrent positions: 3
    - Circuit breaker: if drawdown > 15%, pause everything
    - Cooldown period after breach
    """

    def __init__(self, db_service=None):
        self.db_service = db_service
        self.daily_loss_limit_percent = 0.02  # 2%
        self.agent_loss_limit_percent = 0.10  # 10%
        self.max_concurrent_positions = 3
        self.circuit_breaker_drawdown = 0.15  # 15%
        self.cooldown_hours = 24
        self._daily_loss_start = datetime.now(timezone.utc).date()
        self._daily_loss_usd = 0.0
        self._circuit_breaker_active = False
        self._circuit_breaker_time = None
        self._portfolio_start_value = 0.0

    def set_portfolio_start_value(self, value: float):
        """Set the starting portfolio value for drawdown calculation"""
        self._portfolio_start_value = value

    def check_daily_loss(self, current_portfolio_value: float) -> bool:
        """Check if daily loss limit has been breached"""
        today = datetime.now(timezone.utc).date()
        if today != self._daily_loss_start:
            self._daily_loss_start = today
            self._daily_loss_usd = 0.0

        if self._portfolio_start_value <= 0:
            return False

        daily_pnl = current_portfolio_value - self._portfolio_start_value
        if daily_pnl < 0:
            self._daily_loss_usd = abs(daily_pnl)
            limit = self._portfolio_start_value * self.daily_loss_limit_percent
            if self._daily_loss_usd >= limit:
                logger.warning(
                    f"Daily loss limit breached: ${self._daily_loss_usd:.2f} / ${limit:.2f}"
                )
                return True

        return False

    def check_agent_loss(self, agent: Dict) -> bool:
        """Check if an agent has exceeded its loss limit"""
        initial = agent.get("finances", {}).get("initial_capital", 0)
        current = agent.get("finances", {}).get("current_balance", 0)
        if initial <= 0:
            return False

        loss_percent = (initial - current) / initial
        if loss_percent >= self.agent_loss_limit_percent:
            logger.warning(
                f"Agent {agent.get('name', 'unknown')} loss limit breached: "
                f"{loss_percent * 100:.1f}% / {self.agent_loss_limit_percent * 100:.1f}%"
            )
            return True
        return False

    def check_circuit_breaker(self, current_portfolio_value: float) -> bool:
        """Check if circuit breaker should be triggered"""
        if self._portfolio_start_value <= 0:
            return False

        drawdown = (
            self._portfolio_start_value - current_portfolio_value
        ) / self._portfolio_start_value

        if (
            drawdown >= self.circuit_breaker_drawdown
            and not self._circuit_breaker_active
        ):
            self._circuit_breaker_active = True
            self._circuit_breaker_time = datetime.now(timezone.utc)
            logger.critical(
                f"CIRCUIT BREAKER ACTIVATED! Drawdown: {drawdown * 100:.1f}%"
            )
            return True

        # Check if cooldown has passed
        if self._circuit_breaker_active and self._circuit_breaker_time:
            elapsed = (
                datetime.now(timezone.utc) - self._circuit_breaker_time
            ).total_seconds() / 3600
            if elapsed >= self.cooldown_hours:
                current_drawdown = (
                    self._portfolio_start_value - current_portfolio_value
                ) / self._portfolio_start_value
                if current_drawdown < self.circuit_breaker_drawdown * 0.5:
                    self._circuit_breaker_active = False
                    self._circuit_breaker_time = None
                    logger.info("Circuit breaker reset after cooldown")

        return self._circuit_breaker_active

    def can_open_position(self, current_positions: int = 0) -> bool:
        """Check if we can open a new position"""
        if self._circuit_breaker_active:
            return False
        if current_positions >= self.max_concurrent_positions:
            return False
        return True

    def get_status(self, current_portfolio_value: float) -> Dict:
        """Get current risk status"""
        drawdown = 0
        if self._portfolio_start_value > 0:
            drawdown = max(
                0,
                (self._portfolio_start_value - current_portfolio_value)
                / self._portfolio_start_value,
            )

        daily_limit = (
            self._portfolio_start_value * self.daily_loss_limit_percent
            if self._portfolio_start_value > 0
            else 0
        )

        return {
            "circuit_breaker_active": self._circuit_breaker_active,
            "circuit_breaker_time": self._circuit_breaker_time.isoformat()
            if self._circuit_breaker_time
            else None,
            "current_drawdown_percent": round(drawdown * 100, 2),
            "circuit_breaker_threshold_percent": self.circuit_breaker_drawdown * 100,
            "daily_loss_usd": round(self._daily_loss_usd, 2),
            "daily_loss_limit_usd": round(daily_limit, 2),
            "max_concurrent_positions": self.max_concurrent_positions,
            "agent_loss_limit_percent": self.agent_loss_limit_percent * 100,
            "cooldown_hours": self.cooldown_hours,
            "portfolio_start_value": round(self._portfolio_start_value, 2),
            "current_portfolio_value": round(current_portfolio_value, 2),
        }

    def record_trade_result(self, pnl: float):
        """Record a trade result for daily tracking"""
        self._daily_loss_usd = max(0, self._daily_loss_usd - pnl)

    # =========================================================================
    # Persistence Methods (survives restart)
    # =========================================================================

    async def load_state(self):
        """Load state from MongoDB on startup"""
        if not self.db_service:
            logger.warning("No DB service, skipping state load")
            return

        try:
            state = await self.db_service.risk_state.find_one({"type": "risk_manager"})
            if state:
                # Restore daily loss tracking
                self._daily_loss_start = state.get("daily_loss_start")
                if isinstance(self._daily_loss_start, str):
                    from datetime import date
                    self._daily_loss_start = date.fromisoformat(self._daily_loss_start)

                # Check if we need to reset for new day
                today = datetime.now(timezone.utc).date()
                if self._daily_loss_start != today:
                    self._daily_loss_usd = 0.0
                    self._daily_loss_start = today
                    logger.info("New day detected, reset daily loss tracking")

                self._daily_loss_usd = state.get("daily_loss_usd", 0.0)
                self._portfolio_start_value = state.get("portfolio_start_value", 0.0)

                # Restore circuit breaker state
                cb_time = state.get("circuit_breaker_time")
                if cb_time:
                    if isinstance(cb_time, str):
                        self._circuit_breaker_time = datetime.fromisoformat(cb_time)
                    else:
                        self._circuit_breaker_time = cb_time
                    self._circuit_breaker_active = state.get("circuit_breaker_active", False)

                    logger.info(f"Restored circuit breaker: active={self._circuit_breaker_active}")
                else:
                    self._circuit_breaker_active = False
                    self._circuit_breaker_time = None

                logger.info("RiskManager state loaded from database")
            else:
                logger.info("No existing risk state, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load risk state: {e}")

    async def save_state(self):
        """Save state to MongoDB after changes"""
        if not self.db_service:
            return

        try:
            await self.db_service.risk_state.update_one(
                {"type": "risk_manager"},
                {
                    "$set": {
                        "type": "risk_manager",
                        "daily_loss_start": self._daily_loss_start.isoformat() if self._daily_loss_start else None,
                        "daily_loss_usd": self._daily_loss_usd,
                        "portfolio_start_value": self._portfolio_start_value,
                        "circuit_breaker_active": self._circuit_breaker_active,
                        "circuit_breaker_time": self._circuit_breaker_time.isoformat() if self._circuit_breaker_time else None,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to save risk state: {e}")
