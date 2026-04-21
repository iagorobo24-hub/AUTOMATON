"""
Tests for configuration and environment
"""
import pytest
from app.core.config import settings, TradingMode


class TestConfig:
    """Test configuration settings"""

    def test_settings_exists(self):
        """Settings should load without errors"""
        assert settings is not None
        assert settings.PROJECT_NAME == "Automaton Orchestrator"

    def test_trading_mode_defaults(self):
        """Default trading mode should be paper"""
        assert settings.TRADING_MODE == TradingMode.PAPER
        assert settings.PAPER_TRADING is True

    def test_mongo_url_configured(self):
        """MongoDB URL should be configured"""
        assert settings.MONGO_URL is not None
        assert "mongodb" in settings.MONGO_URL.lower()

    def test_secret_key_not_empty(self):
        """SECRET_KEY should be loaded from environment"""
        # After fix, should be from .env or empty (requiring user to set)
        assert settings.SECRET_KEY is not None

    def test_cors_origins_list(self):
        """CORS origins should be a list"""
        assert isinstance(settings.CORS_ORIGINS, list)

    def test_is_production(self):
        """Production check should work"""
        # In dev, should not be production
        assert settings.is_production is False

    def test_risk_limits_configured(self):
        """Risk limits should be configured"""
        assert settings.MAX_CONCURRENT_TRADES > 0
        assert settings.MAX_POSITION_SIZE_PERCENT > 0
        assert settings.DEFAULT_STOP_LOSS_PERCENT > 0


class TestRiskValidation:
    """Test risk configuration validation"""

    def test_validate_live_trading_without_keys(self):
        """Should not allow live trading without API keys"""
        valid, msg = settings.validate_for_live_trading()
        assert valid is False
        assert "Binance" in msg or "LIVE" in msg