import pytest
import asyncio
from typing import Generator
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    settings = MagicMock()
    settings.PROJECT_NAME = "Test Automaton"
    settings.VERSION = "1.0.0"
    settings.DEBUG = True
    settings.MONGO_URL = "mongodb://localhost:27017"
    settings.DB_NAME = "test_automaton"
    settings.SECRET_KEY = "test-secret-key"
    settings.JWT_ALGORITHM = "HS256"
    settings.JWT_EXPIRATION_MINUTES = 60
    settings.CORS_ORIGINS = ["http://localhost:3000"]
    settings.TRADING_MODE = "paper"
    settings.PAPER_TRADING = True
    settings.PAPER_INITIAL_BALANCE = 10000.0
    settings.MAX_CONCURRENT_TRADES = 10
    settings.MAX_POSITION_SIZE_PERCENT = 10.0
    settings.AUTO_REPLICATION_ENABLED = True
    settings.MIN_ROI_TO_REPLICATE = 50.0
    return settings

@pytest.fixture
def mock_agent():
    """Mock trading agent"""
    agent = MagicMock()
    agent.id = "test_agent_001"
    agent.name = "Test Agent"
    agent.strategy = "momentum"
    agent.initial_capital = 1000.0
    agent.current_balance = 1500.0
    agent.is_active = True
    agent.replication_enabled = True
    return agent

@pytest.fixture
def mock_trade():
    """Mock trade"""
    trade = MagicMock()
    trade.id = "trade_001"
    trade.agent_id = "test_agent_001"
    trade.symbol = "BTCUSDT"
    trade.side = "buy"
    trade.quantity = 0.01
    trade.entry_price = 50000.0
    trade.status = "open"
    return trade

@pytest.fixture
def mock_order():
    """Mock order"""
    order = MagicMock()
    order.id = "order_001"
    order.symbol = "BTCUSDT"
    order.side = "buy"
    order.quantity = 0.01
    order.price = 50000.0
    order.status = "filled"
    return order

@pytest.fixture
def sample_agent_data():
    """Sample agent data for tests"""
    return {
        "name": "Test Agent",
        "strategy": "momentum",
        "initial_capital": 1000.0,
        "max_position_size_percent": 10.0,
        "stop_loss_percent": 2.0,
        "take_profit_percent": 4.0,
    }

@pytest.fixture
def sample_strategy_config():
    """Sample strategy config"""
    return {
        "name": "momentum",
        "parameters": {
            "rsi_period": 14,
            "rsi_overbought": 70,
            "rsi_oversold": 30,
            "ma_period": 20,
        }
    }

@pytest.fixture
def auth_token():
    """Generate test JWT token"""
    import jwt
    from datetime import datetime, timedelta
    payload = {
        "sub": "test_user",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, "test-secret-key", algorithm="HS256")

@pytest.fixture
async def mock_db():
    """Mock database"""
    db = AsyncMock()
    db.users = AsyncMock()
    db.agents = AsyncMock()
    db.trades = AsyncMock()
    return db