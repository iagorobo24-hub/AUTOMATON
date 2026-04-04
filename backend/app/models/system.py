from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from .enums import AgentStatus, TrendType, VolatilityRegime, NotificationType, NotificationPriority

# --- Notification Models ---
class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    message: str
    icon: str = "bell"
    color: str = "primary"
    link: Optional[str] = None
    agent_id: Optional[str] = None
    trade_id: Optional[str] = None
    read: bool = False
    dismissed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class ActivityEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    title: str
    description: str
    icon: str
    color: str = "primary"
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    amount: Optional[float] = None
    link: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = {}

# --- Market Data Models ---
class Ticker(BaseModel):
    price: float
    bid: float = 0
    ask: float = 0
    spread_percent: float = 0
    volume_24h: float = 0
    change_24h_percent: float = 0
    high_24h: float = 0
    low_24h: float = 0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OHLCV(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class MarketIndicators(BaseModel):
    rsi_14: float = 50
    macd: Dict[str, float] = {}
    ema_20: float = 0
    ema_50: float = 0
    ema_200: float = 0
    atr_14: float = 0
    bollinger: Dict[str, float] = {}
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MarketAnalysis(BaseModel):
    trend: TrendType = TrendType.SIDEWAYS
    trend_strength: float = 0.5
    support_levels: List[float] = []
    resistance_levels: List[float] = []
    volatility_regime: VolatilityRegime = VolatilityRegime.MEDIUM
    market_phase: str = "accumulation"

class OrderbookSummary(BaseModel):
    bid_volume_10_levels: float = 0
    ask_volume_10_levels: float = 0
    imbalance_ratio: float = 1.0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MarketData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    exchange: str = "binance"
    ticker: Ticker
    ohlcv_1h: List[OHLCV] = []
    ohlcv_4h: List[OHLCV] = []
    ohlcv_1d: List[OHLCV] = []
    indicators: MarketIndicators = MarketIndicators()
    analysis: MarketAnalysis = MarketAnalysis()
    orderbook_summary: OrderbookSummary = OrderbookSummary()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Lineage Models ---
class LineageTreeNode(BaseModel):
    agent_id: str
    name: str
    generation: int
    created_at: datetime
    status: AgentStatus
    roi: float = 0
    death_reason: Optional[str] = None
    children: List["LineageTreeNode"] = []

class LineageStats(BaseModel):
    total_agents: int = 0
    active_agents: int = 0
    dead_agents: int = 0
    replicating_agents: int = 0
    max_generation: int = 0
    total_capital_managed: float = 0
    combined_roi: float = 0
    best_performer_id: Optional[str] = None
    survival_rate: float = 0

class MutationRecord(BaseModel):
    generation: int
    agent_id: str
    mutation_type: str
    parameter: str
    original_value: Any
    mutated_value: Any
    result: str = "unknown"

class LineageGenetics(BaseModel):
    original_strategy_id: Optional[str] = None
    mutation_history: List[MutationRecord] = []
    successful_mutations: int = 0
    failed_mutations: int = 0

class AgentLineage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lineage_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    root_agent_id: str
    root_agent_name: str
    tree: LineageTreeNode
    stats: LineageStats = LineageStats()
    genetics: LineageGenetics = LineageGenetics()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

LineageTreeNode.model_rebuild()

# --- Audit Models ---
class AuditActor(BaseModel):
    type: str
    id: str
    name: str

class AuditTarget(BaseModel):
    type: str
    id: str
    name: str

class AuditLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    event_category: str
    actor: AuditActor
    target: Optional[AuditTarget] = None
    details: Dict[str, Any] = {}
    result: str = "success"
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    hash: Optional[str] = None

# --- Orchestrator Models ---
class GlobalMetrics(BaseModel):
    total_agents: int = 0
    active_agents: int = 0
    total_capital_managed: float = 0
    daily_pnl: float = 0
    weekly_pnl: float = 0
    monthly_pnl: float = 0
    system_health: float = 1.0

class GlobalLimits(BaseModel):
    max_agents: int = 100
    max_capital_per_agent: float = 10000
    max_daily_loss_total: float = 5000
    emergency_stop_drawdown: float = 20

class TaskQueue(BaseModel):
    pending_replications: int = 0
    pending_terminations: int = 0
    pending_rebalances: int = 0

class LLMStats(BaseModel):
    tokens_used_today: int = 0
    tokens_used_month: int = 0
    cost_estimate_month: float = 0
    primary_model: str = "gpt-4o"
    fallback_models: List[str] = ["gpt-4o-mini"]

class OrchestratorState(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    orchestrator_id: str = "main"
    status: str = "active"
    mode: str = "auto"
    global_metrics: GlobalMetrics = GlobalMetrics()
    global_limits: GlobalLimits = GlobalLimits()
    task_queue: TaskQueue = TaskQueue()
    llm_stats: LLMStats = LLMStats()
    last_health_check: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
