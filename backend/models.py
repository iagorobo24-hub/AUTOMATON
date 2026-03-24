"""
Automaton Orchestrator - Database Models
Complete schema for self-replicating crypto trading agents
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


# ==================== ENUMS ====================

class AgentType(str, Enum):
    CRYPTO_TRADER = "crypto_trader"
    BUSINESS_SCOUT = "business_scout"
    MARKET_ANALYZER = "market_analyzer"
    HYBRID = "hybrid"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    REPLICATING = "replicating"
    DYING = "dying"
    DEAD = "dead"
    PAUSED = "paused"
    HIBERNATING = "hibernating"


class TradeSide(str, Enum):
    LONG = "long"
    SHORT = "short"


class TradeStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class SignalType(str, Enum):
    ENTRY = "entry"
    EXIT = "exit"
    ALERT = "alert"


class TrendType(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"


class VolatilityRegime(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


# ==================== SUB-MODELS ====================

class Lineage(BaseModel):
    """Agent family tree and hierarchy"""
    parent_id: Optional[str] = None
    root_ancestor_id: Optional[str] = None
    children_ids: List[str] = []
    siblings_ids: List[str] = []
    generation_depth: int = 0
    clone_count: int = 0
    total_descendants: int = 0


class Lifecycle(BaseModel):
    """Agent lifecycle timestamps"""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    activated_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    death_at: Optional[datetime] = None
    death_reason: Optional[str] = None  # bankruptcy | manual | performance | risk_breach
    resurrection_count: int = 0
    total_uptime_hours: float = 0


class AgentFinances(BaseModel):
    """Agent financial state"""
    initial_capital: float = 100.0
    current_balance: float = 100.0
    reserved_balance: float = 0
    available_balance: float = 100.0
    lifetime_deposited: float = 0
    lifetime_withdrawn: float = 0
    lifetime_fees_paid: float = 0
    currency: str = "USD"


class Performance(BaseModel):
    """Agent performance metrics"""
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
    """Agent trading statistics"""
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
    """Trading hours configuration"""
    enabled: bool = False
    start_utc: str = "00:00"
    end_utc: str = "23:59"
    timezone: str = "UTC"


class AgentConfig(BaseModel):
    """Agent configuration"""
    strategy_id: Optional[str] = None
    risk_profile_id: Optional[str] = None
    auto_trade: bool = True
    max_concurrent_trades: int = 5
    default_position_size_percent: float = 5.0
    allowed_pairs: List[str] = ["BTC/USDT", "ETH/USDT"]
    blacklisted_pairs: List[str] = []
    trading_hours: TradingHours = TradingHours()


class ReplicationRules(BaseModel):
    """Rules for agent self-replication"""
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
    """Rules for agent termination"""
    min_balance_usd: float = 1.0
    max_drawdown_percent: float = 80.0
    max_consecutive_losses: int = 20
    inactivity_days_to_die: int = 30


class AgentMetadata(BaseModel):
    """Agent metadata"""
    tags: List[str] = []
    notes: str = ""
    created_by: Optional[str] = None
    last_modified_by: Optional[str] = None
    custom_data: Dict[str, Any] = {}


# ==================== MAIN MODELS ====================

class Agent(BaseModel):
    """Main Agent Model - Self-replicating trading agent"""
    model_config = ConfigDict(extra="ignore")
    
    # Identification
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    display_name: Optional[str] = None
    version: str = "1.0.0"
    
    # Classification
    agent_type: AgentType = AgentType.CRYPTO_TRADER
    agent_class: str = "trader"
    specialization: List[str] = ["BTC", "ETH"]
    generation: int = 1
    
    # Hierarchy
    lineage: Lineage = Lineage()
    
    # State
    status: AgentStatus = AgentStatus.ACTIVE
    lifecycle: Lifecycle = Lifecycle()
    
    # Financial
    finances: AgentFinances = AgentFinances()
    
    # Performance
    performance: Performance = Performance()
    trading_stats: TradingStats = TradingStats()
    
    # Configuration
    config: AgentConfig = AgentConfig()
    replication_rules: ReplicationRules = ReplicationRules()
    death_rules: DeathRules = DeathRules()
    
    # Metadata
    metadata: AgentMetadata = AgentMetadata()
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IndicatorConfig(BaseModel):
    """Technical indicator configuration"""
    name: str
    params: Dict[str, Any]
    weight: float = 1.0


class EntryCondition(BaseModel):
    """Entry condition for strategy"""
    indicator: str
    condition: str
    value: Optional[Any] = None
    params: Dict[str, Any] = {}
    required: bool = True


class EntryRules(BaseModel):
    """Strategy entry rules"""
    conditions: List[EntryCondition] = []
    min_conditions_met: int = 1
    confirmation_candles: int = 1


class PartialExit(BaseModel):
    """Partial exit configuration"""
    at_percent: float
    close_percent: float


class TakeProfit(BaseModel):
    """Take profit configuration"""
    type: str = "percentage"
    value: float = 5.0
    partial_exits: List[PartialExit] = []


class TrailingStop(BaseModel):
    """Trailing stop configuration"""
    enabled: bool = False
    activation_percent: float = 1.5
    trail_percent: float = 1.0


class StopLoss(BaseModel):
    """Stop loss configuration"""
    type: str = "percentage"
    value: float = 2.0
    trailing: TrailingStop = TrailingStop()


class TimeExit(BaseModel):
    """Time-based exit"""
    enabled: bool = False
    max_hours: int = 48


class ExitRules(BaseModel):
    """Strategy exit rules"""
    take_profit: TakeProfit = TakeProfit()
    stop_loss: StopLoss = StopLoss()
    time_exit: TimeExit = TimeExit()


class TrendFilter(BaseModel):
    """Trend filter for strategy"""
    enabled: bool = True
    indicator: str = "EMA_200"
    condition: str = "price_above"


class MarketFilters(BaseModel):
    """Market filters for strategy"""
    min_volume_24h_usd: float = 1000000
    min_market_cap_usd: float = 100000000
    max_spread_percent: float = 0.5
    avoid_during_news: bool = True
    trend_filter: TrendFilter = TrendFilter()


class BacktestResults(BaseModel):
    """Strategy backtest results"""
    period_tested: str = ""
    total_trades: int = 0
    win_rate: float = 0
    profit_factor: float = 0
    max_drawdown: float = 0
    sharpe_ratio: float = 0
    annual_return_percent: float = 0


class StrategyInheritance(BaseModel):
    """Strategy inheritance configuration"""
    is_template: bool = False
    parent_strategy_id: Optional[str] = None
    derived_count: int = 0
    is_locked: bool = False
    shareable: bool = True


class Strategy(BaseModel):
    """Trading Strategy Model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    version: str = "1.0.0"
    
    # Classification
    type: str = "momentum"  # momentum | mean_reversion | arbitrage | trend_following | scalping
    timeframe: str = "4h"
    complexity: str = "intermediate"
    
    # Inheritance
    inheritance: StrategyInheritance = StrategyInheritance()
    
    # Technical indicators
    indicators: List[IndicatorConfig] = []
    
    # Rules
    entry_rules: EntryRules = EntryRules()
    exit_rules: ExitRules = ExitRules()
    market_filters: MarketFilters = MarketFilters()
    
    # Results
    backtest_results: BacktestResults = BacktestResults()
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TradeEntry(BaseModel):
    """Trade entry details"""
    order_id: Optional[str] = None
    price: float
    quantity: float
    value_usd: float
    fee: float = 0
    fee_currency: str = "USDT"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    slippage_percent: float = 0


class TradeExit(BaseModel):
    """Trade exit details"""
    order_id: Optional[str] = None
    price: float = 0
    quantity: float = 0
    value_usd: float = 0
    fee: float = 0
    fee_currency: str = "USDT"
    timestamp: Optional[datetime] = None
    slippage_percent: float = 0
    exit_reason: Optional[str] = None  # take_profit | stop_loss | trailing_stop | manual | signal | time_exit


class TradeResult(BaseModel):
    """Trade result calculations"""
    pnl_usd: float = 0
    pnl_percent: float = 0
    net_pnl_usd: float = 0
    net_pnl_percent: float = 0
    is_winner: bool = False
    duration_seconds: int = 0
    duration_formatted: str = ""


class RiskManagement(BaseModel):
    """Trade risk management details"""
    initial_stop_loss: float = 0
    initial_take_profit: float = 0
    risk_reward_ratio: float = 0
    position_size_percent: float = 0
    max_risk_usd: float = 0


class MarketContext(BaseModel):
    """Market context at time of trade"""
    trend: TrendType = TrendType.SIDEWAYS
    volatility: VolatilityRegime = VolatilityRegime.MEDIUM
    btc_dominance: float = 0
    fear_greed_index: int = 50
    volume_24h_change_percent: float = 0


class TradeSignal(BaseModel):
    """Signal that triggered the trade"""
    signal_id: str
    indicator: str
    value: Any
    condition_met: str


class Trade(BaseModel):
    """Trade Model - Individual trading operation"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trade_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    strategy_id: Optional[str] = None
    
    # Identification
    symbol: str
    base_asset: str
    quote_asset: str
    exchange: str = "binance"
    
    # Type
    side: TradeSide = TradeSide.LONG
    type: str = "market"
    trade_category: str = "spot"
    
    # Entry/Exit
    entry: TradeEntry
    exit: Optional[TradeExit] = None
    
    # Result
    result: TradeResult = TradeResult()
    
    # Risk
    risk_management: RiskManagement = RiskManagement()
    
    # Context
    market_context: MarketContext = MarketContext()
    signals: List[TradeSignal] = []
    
    # Status
    status: TradeStatus = TradeStatus.OPEN
    notes: str = ""
    tags: List[str] = []
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None


class PositionQuantity(BaseModel):
    """Position quantity breakdown"""
    initial: float
    current: float
    closed: float = 0


class PositionPrices(BaseModel):
    """Position price tracking"""
    entry_avg: float
    current: float
    highest: float
    lowest: float


class UnrealizedPnL(BaseModel):
    """Unrealized PnL tracking"""
    usd: float = 0
    percent: float = 0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ActiveOrder(BaseModel):
    """Active order details"""
    order_id: Optional[str] = None
    price: float
    type: str


class TrailingStopOrder(BaseModel):
    """Trailing stop order"""
    enabled: bool = False
    callback_rate: float = 2.0
    activation_price: float = 0


class ActiveOrders(BaseModel):
    """All active orders for position"""
    stop_loss: Optional[ActiveOrder] = None
    take_profit: Optional[ActiveOrder] = None
    trailing_stop: TrailingStopOrder = TrailingStopOrder()


class Position(BaseModel):
    """Open Position Model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    position_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    trade_id: str
    
    symbol: str
    side: TradeSide
    status: str = "open"
    
    quantity: PositionQuantity
    prices: PositionPrices
    unrealized_pnl: UnrealizedPnL = UnrealizedPnL()
    active_orders: ActiveOrders = ActiveOrders()
    
    opened_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_update: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    age_hours: float = 0


class AssetBalance(BaseModel):
    """Balance for a single asset"""
    total: float = 0
    available: float = 0
    reserved: float = 0
    in_orders: float = 0
    value_usd: float = 0


class TransactionSummary(BaseModel):
    """Wallet transaction summary"""
    total_deposits: float = 0
    total_withdrawals: float = 0
    total_trading_fees: float = 0
    total_funding_fees: float = 0
    net_trading_pnl: float = 0


class WalletLimits(BaseModel):
    """Wallet limits"""
    max_position_value_usd: float = 500
    max_daily_loss_usd: float = 100
    daily_loss_used: float = 0
    daily_reset_at: Optional[datetime] = None


class Wallet(BaseModel):
    """Agent Wallet Model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    
    balances: Dict[str, AssetBalance] = {}
    total_value_usd: float = 0
    last_valuation_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    transaction_summary: TransactionSummary = TransactionSummary()
    limits: WalletLimits = WalletLimits()
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PositionLimits(BaseModel):
    """Position limits for risk profile"""
    max_position_size_percent: float = 5
    max_positions_concurrent: int = 3
    max_exposure_single_asset_percent: float = 20
    max_exposure_correlated_assets_percent: float = 40


class LossLimits(BaseModel):
    """Loss limits for risk profile"""
    max_loss_per_trade_percent: float = 2
    max_daily_loss_percent: float = 5
    max_weekly_loss_percent: float = 10
    max_monthly_loss_percent: float = 20
    max_drawdown_percent: float = 25


class BreachActions(BaseModel):
    """Actions on limit breach"""
    on_daily_limit: str = "pause_trading"
    on_weekly_limit: str = "pause_trading"
    on_drawdown_limit: str = "stop_and_notify"
    cooldown_hours: int = 24


class VolatilityAdjustments(BaseModel):
    """Volatility-based adjustments"""
    enabled: bool = True
    high_volatility_reduction: float = 0.5
    low_volatility_increase: float = 1.2


class RiskProfile(BaseModel):
    """Risk Profile Model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    risk_profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    
    is_template: bool = False
    parent_profile_id: Optional[str] = None
    inheritable: bool = True
    
    position_limits: PositionLimits = PositionLimits()
    loss_limits: LossLimits = LossLimits()
    breach_actions: BreachActions = BreachActions()
    volatility_adjustments: VolatilityAdjustments = VolatilityAdjustments()
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SignalSource(BaseModel):
    """Signal source information"""
    type: str  # indicator | pattern | ai_analysis | news
    name: str
    strategy_id: Optional[str] = None


class SignalDetails(BaseModel):
    """Signal details"""
    indicator_values: Dict[str, Any] = {}
    reasoning: str = ""
    timeframe: str = "4h"


class SuggestedPrices(BaseModel):
    """Signal suggested prices"""
    entry: float
    stop_loss: float
    take_profit: List[float] = []
    risk_reward: float = 0


class SignalConsumer(BaseModel):
    """Agent that consumed the signal"""
    agent_id: str
    consumed_at: datetime
    action_taken: str
    trade_id: Optional[str] = None


class Signal(BaseModel):
    """Trading Signal Model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    
    type: SignalType = SignalType.ENTRY
    direction: TradeSide = TradeSide.LONG
    strength: float = 0.5
    
    source: SignalSource
    details: SignalDetails = SignalDetails()
    suggested_prices: Optional[SuggestedPrices] = None
    
    consumed_by: List[SignalConsumer] = []
    
    valid_until: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Ticker(BaseModel):
    """Market ticker data"""
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
    """OHLCV candle"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketIndicators(BaseModel):
    """Pre-calculated market indicators"""
    rsi_14: float = 50
    macd: Dict[str, float] = {}
    ema_20: float = 0
    ema_50: float = 0
    ema_200: float = 0
    atr_14: float = 0
    bollinger: Dict[str, float] = {}
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MarketAnalysis(BaseModel):
    """Market analysis"""
    trend: TrendType = TrendType.SIDEWAYS
    trend_strength: float = 0.5
    support_levels: List[float] = []
    resistance_levels: List[float] = []
    volatility_regime: VolatilityRegime = VolatilityRegime.MEDIUM
    market_phase: str = "accumulation"


class OrderbookSummary(BaseModel):
    """Orderbook summary"""
    bid_volume_10_levels: float = 0
    ask_volume_10_levels: float = 0
    imbalance_ratio: float = 1.0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MarketData(BaseModel):
    """Market Data Model - Shared across agents"""
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


class LineageTreeNode(BaseModel):
    """Node in the agent family tree"""
    agent_id: str
    name: str
    generation: int
    created_at: datetime
    status: AgentStatus
    roi: float = 0
    death_reason: Optional[str] = None
    children: List["LineageTreeNode"] = []


class LineageStats(BaseModel):
    """Statistics for entire lineage"""
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
    """Record of a genetic mutation"""
    generation: int
    agent_id: str
    mutation_type: str
    parameter: str
    original_value: Any
    mutated_value: Any
    result: str = "unknown"


class LineageGenetics(BaseModel):
    """Genetic information for lineage"""
    original_strategy_id: Optional[str] = None
    mutation_history: List[MutationRecord] = []
    successful_mutations: int = 0
    failed_mutations: int = 0


class AgentLineage(BaseModel):
    """Agent Lineage Model - Family tree"""
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


# Update forward reference
LineageTreeNode.model_rebuild()


class AuditActor(BaseModel):
    """Actor that performed the action"""
    type: str  # agent | orchestrator | user | system
    id: str
    name: str


class AuditTarget(BaseModel):
    """Target of the action"""
    type: str
    id: str
    name: str


class AuditLog(BaseModel):
    """Audit Log Model - Immutable event records"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    event_type: str
    event_category: str  # lifecycle | trading | financial | config | system
    
    actor: AuditActor
    target: Optional[AuditTarget] = None
    
    details: Dict[str, Any] = {}
    result: str = "success"
    error_message: Optional[str] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    hash: Optional[str] = None


class GlobalMetrics(BaseModel):
    """Global orchestrator metrics"""
    total_agents: int = 0
    active_agents: int = 0
    total_capital_managed: float = 0
    daily_pnl: float = 0
    weekly_pnl: float = 0
    monthly_pnl: float = 0
    system_health: float = 1.0


class GlobalLimits(BaseModel):
    """Global orchestrator limits"""
    max_agents: int = 100
    max_capital_per_agent: float = 10000
    max_daily_loss_total: float = 5000
    emergency_stop_drawdown: float = 20


class TaskQueue(BaseModel):
    """Orchestrator task queue"""
    pending_replications: int = 0
    pending_terminations: int = 0
    pending_rebalances: int = 0


class LLMStats(BaseModel):
    """LLM usage statistics"""
    tokens_used_today: int = 0
    tokens_used_month: int = 0
    cost_estimate_month: float = 0
    primary_model: str = "gpt-4o"
    fallback_models: List[str] = ["gpt-4o-mini"]


class OrchestratorState(BaseModel):
    """Orchestrator State Model"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    orchestrator_id: str = "main"
    
    status: str = "active"
    mode: str = "auto"  # auto | semi_auto | manual | maintenance
    
    global_metrics: GlobalMetrics = GlobalMetrics()
    global_limits: GlobalLimits = GlobalLimits()
    task_queue: TaskQueue = TaskQueue()
    llm_stats: LLMStats = LLMStats()
    
    last_health_check: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== REQUEST/RESPONSE MODELS ====================

class AgentCreateRequest(BaseModel):
    """Request to create a new agent"""
    name: str
    agent_type: AgentType = AgentType.CRYPTO_TRADER
    initial_capital: float = 100.0
    specialization: List[str] = ["BTC", "ETH"]
    strategy_id: Optional[str] = None
    risk_profile_id: Optional[str] = None
    parent_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class AgentReplicateRequest(BaseModel):
    """Request to replicate an agent"""
    capital_split_ratio: float = 0.5
    mutation_enabled: bool = True
    mutation_rate: float = 0.1
    custom_name: Optional[str] = None


class TradeCreateRequest(BaseModel):
    """Request to create/open a trade"""
    agent_id: str
    symbol: str
    side: TradeSide
    quantity: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy_id: Optional[str] = None


class TradeCloseRequest(BaseModel):
    """Request to close a trade"""
    exit_price: float
    exit_reason: str = "manual"


class StrategyCreateRequest(BaseModel):
    """Request to create a strategy"""
    name: str
    description: str = ""
    type: str = "momentum"
    timeframe: str = "4h"
    indicators: List[IndicatorConfig] = []
    parent_strategy_id: Optional[str] = None
