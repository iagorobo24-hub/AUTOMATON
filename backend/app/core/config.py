from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from enum import Enum
import secrets


class TradingMode(str, Enum):
    PAPER = "paper"
    LIVE = "live"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Automaton Orchestrator"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    MONGO_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "automaton_db"
    
    SECRET_KEY: str = ""  # REQUIRED: Set via .env file (generate with: python -c "import secrets; print(secrets.token_hex(32))")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24 * 7
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    EMERGENT_LLM_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    TRADING_MODE: TradingMode = TradingMode.PAPER
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    BINANCE_TESTNET: bool = True
    
    PAPER_TRADING: bool = True
    PAPER_INITIAL_BALANCE: float = 10000.0
    
    MAX_CONCURRENT_TRADES: int = 10
    MAX_POSITION_SIZE_PERCENT: float = 10.0
    DEFAULT_STOP_LOSS_PERCENT: float = 2.0
    DEFAULT_TAKE_PROFIT_PERCENT: float = 4.0
    
    AUTO_REPLICATION_ENABLED: bool = True
    MIN_ROI_TO_REPLICATE: float = 50.0
    MAX_AGENT_CHILDREN: int = 10
    REPLICATION_CHECK_INTERVAL_SECONDS: int = 60
    
    MAX_DRAWDOWN_PERCENT: float = 80.0
    CIRCUIT_BREAKER_THRESHOLD: int = 5
    
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    
    ENABLE_NOTIFICATIONS: bool = True
    NOTIFICATION_EMAIL: str = ""
    
    REDIS_URL: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_live_trading(self) -> bool:
        return self.TRADING_MODE == TradingMode.LIVE
    
    def validate_for_live_trading(self) -> tuple[bool, str]:
        """Validate config allows live trading"""
        if self.TRADING_MODE != TradingMode.LIVE:
            return False, "Trading mode is not set to LIVE"
        
        if not self.BINANCE_API_KEY or not self.BINANCE_SECRET_KEY:
            return False, "Binance API keys not configured"
        
        if self.is_production and self.DEBUG:
            return False, "DEBUG mode must be False in production"
        
        return True, "OK"


settings = Settings()