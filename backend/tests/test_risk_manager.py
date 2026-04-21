"""
Tests for RiskManager
"""
import pytest
from datetime import datetime, timezone
from app.services.risk_manager import RiskManager


class TestRiskManager:
    """Test RiskManager logic"""

    @pytest.fixture
    def risk_manager(self):
        """Create RiskManager instance"""
        return RiskManager(db_service=None)

    def test_initial_state(self, risk_manager):
        """Initial state should be clean"""
        assert risk_manager._daily_loss_usd == 0.0
        assert risk_manager._circuit_breaker_active is False
        assert risk_manager._circuit_breaker_time is None
        assert risk_manager._portfolio_start_value == 0.0

    def test_set_portfolio_value(self, risk_manager):
        """Portfolio value should be set correctly"""
        risk_manager.set_portfolio_start_value(10000.0)
        assert risk_manager._portfolio_start_value == 10000.0

    def test_daily_loss_under_limit(self, risk_manager):
        """Should allow trading under daily limit"""
        risk_manager.set_portfolio_start_value(10000.0)
        # Gain of $100 (no loss)
        can_trade = not risk_manager.check_daily_loss(10100.0)
        assert can_trade is True

    def test_daily_loss_over_limit(self, risk_manager):
        """Should block trading over daily limit"""
        risk_manager.set_portfolio_start_value(10000.0)
        risk_manager.daily_loss_limit_percent = 0.02  # 2% = $200
        # Loss of $300 (> $200 limit)
        can_trade = not risk_manager.check_daily_loss(9700.0)
        assert can_trade is False

    def test_daily_loss_resets_new_day(self, risk_manager):
        """Daily loss should reset for new day"""
        risk_manager.set_portfolio_start_value(10000.0)
        risk_manager._daily_loss_usd = 100.0
        risk_manager._daily_loss_start = (
            datetime.now(timezone.utc).date().replace(day=1)  # First of month

        # Check as if today - should reset
        can_trade = not risk_manager.check_daily_loss(10000.0)
        assert risk_manager._daily_loss_usd == 0.0  # Reset

    def test_circuit_breaker_trigger(self, risk_manager):
        """Circuit breaker should trigger on drawdown"""
        risk_manager.set_portfolio_start_value(10000.0)
        risk_manager.circuit_breaker_drawdown = 0.15  # 15%

        # Drawdown of 20% (> 15%)
        triggered = risk_manager.check_circuit_breaker(8000.0)
        assert triggered is True
        assert risk_manager._circuit_breaker_active is True

    def test_circuit_breaker_prevents_trading(self, risk_manager):
        """Circuit breaker should block new positions"""
        risk_manager._circuit_breaker_active = True
        can_open = risk_manager.can_open_position(0)
        assert can_open is False

    def test_max_positions(self, risk_manager):
        """Should limit concurrent positions"""
        risk_manager.max_concurrent_positions = 3
        can_open = risk_manager.can_open_position(2)  # At limit
        assert can_open is False
        can_open = risk_manager.can_open_position(1)  # Under limit
        assert can_open is True

    def test_get_status(self, risk_manager):
        """Status should return all metrics"""
        risk_manager.set_portfolio_start_value(10000.0)
        status = risk_manager.get_status(9500.0)

        assert "portfolio_start_value" in status
        assert "current_portfolio_value" in status
        assert "circuit_breaker_active" in status
        assert status["portfolio_start_value"] == 10000.0
        assert status["current_portfolio_value"] == 9500.0

    def test_agent_loss_check(self, risk_manager):
        """Should check per-agent losses"""
        agent = {
            "name": "test_agent",
            "finances": {"initial_capital": 1000, "current_balance": 850}
        }
        risk_manager.agent_loss_limit_percent = 0.10  # 10%

        breached = risk_manager.check_agent_loss(agent)
        assert breached is True  # 15% loss > 10%

    def test_agent_loss_under_limit(self, risk_manager):
        """Should allow agent under limit"""
        agent = {
            "name": "test_agent",
            "finances": {"initial_capital": 1000, "current_balance": 950}
        }

        breached = risk_manager.check_agent_loss(agent)
        assert breached is False  # 5% loss < 10%


class TestRiskManagerPersistence:
    """Test RiskManager persistence (mock)"""

    @pytest.mark.asyncio
    async def test_load_state_no_db(self, risk_manager):
        """Should handle no DB gracefully"""
        await risk_manager.load_state()
        # Should not raise, just log warning

    @pytest.mark.asyncio
    async def test_save_state_no_db(self, risk_manager):
        """Should handle no DB gracefully"""
        await risk_manager.save_state()
        # Should not raise