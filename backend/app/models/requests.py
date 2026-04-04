from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .enums import AgentType, TradeSide

class AgentCreateRequest(BaseModel):
    name: str
    agent_type: AgentType = AgentType.CRYPTO_TRADER
    initial_capital: float = 100.0
    specialization: List[str] = ["BTC", "ETH"]
    strategy_id: Optional[str] = None
    risk_profile_id: Optional[str] = None
    parent_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class AgentReplicateRequest(BaseModel):
    capital_split_ratio: float = 0.5
    mutation_enabled: bool = True
    mutation_rate: float = 0.1
    custom_name: Optional[str] = None

class TradeCreateRequest(BaseModel):
    agent_id: str
    symbol: str
    side: TradeSide
    quantity: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy_id: Optional[str] = None

class TradeCloseRequest(BaseModel):
    exit_price: float
    exit_reason: str = "manual"

class StrategyCreateRequest(BaseModel):
    name: str
    description: str = ""
    type: str = "momentum"
    timeframe: str = "4h"
    indicators: List[Dict[str, Any]] = []
    parent_strategy_id: Optional[str] = None
