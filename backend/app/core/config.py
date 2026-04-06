from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "Automaton Orchestrator"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"

    MONGO_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "automaton_qwencli_db"

    EMERGENT_LLM_KEY: str = ""
    OPENAI_API_KEY: str = ""

    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    BINANCE_TESTNET: bool = True

    PAPER_TRADING: bool = True

    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"

    CORS_ORIGINS: List[str] = ["http://localhost:3001", "http://127.0.0.1:3001"]

    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
