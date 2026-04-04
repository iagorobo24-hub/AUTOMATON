from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from .enums import AgentType, AgentStatus

class Lineage(BaseModel):
    parent_id: Optional[str] = None
    root_ancestor_id: Optional[str] = None
    children_ids: List[str] = []
    siblings_ids: List[str] = []
    generation_depth: int = 0
    clone_count: int = 0
    total_descendants: int = 0

class Lifecycle(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    activated_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    death_at: Optional[datetime] = None
    death_reason: Optional[str] = None
    resurrection_count: int = 0
    total_uptime_hours: float = 0

class AgentFinances(BaseModel):
    initial_capital: float = 100.0
    current_balance: float = 100.0
    reserved_balance: float = 0
    available_balance: float = 100.0
    lifetime_deposited: float = 0
    lifetime_withdrawn: float = 0
    lifetime_fees_paid: float = 0
    currency: str = "USD"

class Performance(BaseModel):
    roi_percent: float = 0
    roi_24h: float = 0
    roi_7d: float = 0
    roi_30d: float = 0
    sharpe_ratio: float = 0
    sortino_ratio: float = 0
    max_drawdown_percent: float = 0
    win_rate: float = 0
    profit_factor: float = 0
    avg_trade_duration_hours: float = 0
    trades_per_day_avg: float = 0

class TradingStats(BaseModel):
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    open_positions: int = 0
    largest_win: float = 0
    largest_loss: float = 0
    avg_win: float = 0
    avg_loss: float = 0
    consecutive_wins_max: int = 0
    consecutive_losses_max: int = 0
    current_streak: int = 0
    streak_type: str = "none"

class TradingHours(BaseModel):
    enabled: bool = False
    start_utc: str = "00:00"
    end_utc: str = "23:59"
    timezone: str = "UTC"

class AgentConfig(BaseModel):
    strategy_id: Optional[str] = None
    risk_profile_id: Optional[str] = None
    auto_trade: bool = True
    max_concurrent_trades: int = 5
    default_position_size_percent: float = 5.0
    allowed_pairs: List[str] = ["BTC/USDT", "ETH/USDT"]
    blacklisted_pairs: List[str] = []
    trading_hours: TradingHours = TradingHours()

class ReplicationRules(BaseModel):
    auto_replicate: bool = True
    min_roi_to_replicate: float = 50.0
    min_trades_to_replicate: int = 100
    min_age_days: int = 7
    max_children: int = 10
    capital_split_ratio: float = 0.5
    inherit_strategy: bool = True
    inherit_risk_profile: bool = True
    mutation_enabled: bool = True
    mutation_rate: float = 0.1

class DeathRules(BaseModel):
    min_balance_usd: float = 1.0
    max_drawdown_percent: float = 80.0
    max_consecutive_losses: int = 20
    inactivity_days_to_die: int = 30

class AgentMetadata(BaseModel):
    tags: List[str] = []
    notes: str = ""
    created_by: Optional[str] = None
    last_modified_by: Optional[str] = None
    custom_data: Dict[str, Any] = {}

class Agent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    display_name: Optional[str] = None
    version: str = "1.0.0"
    
    agent_type: AgentType = AgentType.CRYPTO_TRADER
    agent_class: str = "trader"
    specialization: List[str] = ["BTC", "ETH"]
    generation: int = 1
    
    lineage: Lineage = Lineage()
    status: AgentStatus = AgentStatus.ACTIVE
    lifecycle: Lifecycle = Lifecycle()
    finances: AgentFinances = AgentFinances()
    performance: Performance = Performance()
    trading_stats: TradingStats = TradingStats()
    config: AgentConfig = AgentConfig()
    replication_rules: ReplicationRules = ReplicationRules()
    death_rules: DeathRules = DeathRules()
    metadata: AgentMetadata = AgentMetadata()
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
