from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from .enums import TradeSide, TradeStatus, SignalType, TrendType, VolatilityRegime

# --- Strategy Models ---
class IndicatorConfig(BaseModel):
    name: str
    params: Dict[str, Any]
    weight: float = 1.0

class EntryCondition(BaseModel):
    indicator: str
    condition: str
    value: Optional[Any] = None
    params: Dict[str, Any] = {}
    required: bool = True

class EntryRules(BaseModel):
    conditions: List[EntryCondition] = []
    min_conditions_met: int = 1
    confirmation_candles: int = 1

class PartialExit(BaseModel):
    at_percent: float
    close_percent: float

class TakeProfit(BaseModel):
    type: str = "percentage"
    value: float = 5.0
    partial_exits: List[PartialExit] = []

class TrailingStop(BaseModel):
    enabled: bool = False
    activation_percent: float = 1.5
    trail_percent: float = 1.0

class StopLoss(BaseModel):
    type: str = "percentage"
    value: float = 2.0
    trailing: TrailingStop = TrailingStop()

class TimeExit(BaseModel):
    enabled: bool = False
    max_hours: int = 48

class ExitRules(BaseModel):
    take_profit: TakeProfit = TakeProfit()
    stop_loss: StopLoss = StopLoss()
    time_exit: TimeExit = TimeExit()

class TrendFilter(BaseModel):
    enabled: bool = True
    indicator: str = "EMA_200"
    condition: str = "price_above"

class MarketFilters(BaseModel):
    min_volume_24h_usd: float = 1000000
    min_market_cap_usd: float = 100000000
    max_spread_percent: float = 0.5
    avoid_during_news: bool = True
    trend_filter: TrendFilter = TrendFilter()

class BacktestResults(BaseModel):
    period_tested: str = ""
    total_trades: int = 0
    win_rate: float = 0
    profit_factor: float = 0
    max_drawdown: float = 0
    sharpe_ratio: float = 0
    annual_return_percent: float = 0

class StrategyInheritance(BaseModel):
    is_template: bool = False
    parent_strategy_id: Optional[str] = None
    derived_count: int = 0
    is_locked: bool = False
    shareable: bool = True

class Strategy(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    version: str = "1.0.0"
    type: str = "momentum"
    timeframe: str = "4h"
    complexity: str = "intermediate"
    inheritance: StrategyInheritance = StrategyInheritance()
    indicators: List[IndicatorConfig] = []
    entry_rules: EntryRules = EntryRules()
    exit_rules: ExitRules = ExitRules()
    market_filters: MarketFilters = MarketFilters()
    backtest_results: BacktestResults = BacktestResults()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Trade Models ---
class TradeEntry(BaseModel):
    order_id: Optional[str] = None
    price: float
    quantity: float
    value_usd: float
    fee: float = 0
    fee_currency: str = "USDT"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    slippage_percent: float = 0

class TradeExit(BaseModel):
    order_id: Optional[str] = None
    price: float = 0
    quantity: float = 0
    value_usd: float = 0
    fee: float = 0
    fee_currency: str = "USDT"
    timestamp: Optional[datetime] = None
    slippage_percent: float = 0
    exit_reason: Optional[str] = None

class TradeResult(BaseModel):
    pnl_usd: float = 0
    pnl_percent: float = 0
    net_pnl_usd: float = 0
    net_pnl_percent: float = 0
    is_winner: bool = False
    duration_seconds: int = 0
    duration_formatted: str = ""

class RiskManagement(BaseModel):
    initial_stop_loss: float = 0
    initial_take_profit: float = 0
    risk_reward_ratio: float = 0
    position_size_percent: float = 0
    max_risk_usd: float = 0

class MarketContext(BaseModel):
    trend: TrendType = TrendType.SIDEWAYS
    volatility: VolatilityRegime = VolatilityRegime.MEDIUM
    btc_dominance: float = 0
    fear_greed_index: int = 50
    volume_24h_change_percent: float = 0

class TradeSignalRef(BaseModel):
    signal_id: str
    indicator: str
    value: Any
    condition_met: str

class Trade(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trade_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    strategy_id: Optional[str] = None
    symbol: str
    base_asset: str
    quote_asset: str
    exchange: str = "binance"
    side: TradeSide = TradeSide.LONG
    type: str = "market"
    trade_category: str = "spot"
    entry: TradeEntry
    exit: Optional[TradeExit] = None
    result: TradeResult = TradeResult()
    risk_management: RiskManagement = RiskManagement()
    market_context: MarketContext = MarketContext()
    signals: List[TradeSignalRef] = []
    status: TradeStatus = TradeStatus.OPEN
    notes: str = ""
    tags: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None

# --- Position Models ---
class PositionQuantity(BaseModel):
    initial: float
    current: float
    closed: float = 0

class PositionPrices(BaseModel):
    entry_avg: float
    current: float
    highest: float
    lowest: float

class UnrealizedPnL(BaseModel):
    usd: float = 0
    percent: float = 0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ActiveOrder(BaseModel):
    order_id: Optional[str] = None
    price: float
    type: str

class TrailingStopOrder(BaseModel):
    enabled: bool = False
    callback_rate: float = 2.0
    activation_price: float = 0

class ActiveOrders(BaseModel):
    stop_loss: Optional[ActiveOrder] = None
    take_profit: Optional[ActiveOrder] = None
    trailing_stop: TrailingStopOrder = TrailingStopOrder()

class Position(BaseModel):
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

# --- Signal Models ---
class SignalSource(BaseModel):
    type: str
    name: str
    strategy_id: Optional[str] = None

class SignalDetails(BaseModel):
    indicator_values: Dict[str, Any] = {}
    reasoning: str = ""
    timeframe: str = "4h"

class SuggestedPrices(BaseModel):
    entry: float
    stop_loss: float
    take_profit: List[float] = []
    risk_reward: float = 0

class SignalConsumer(BaseModel):
    agent_id: str
    consumed_at: datetime
    action_taken: str
    trade_id: Optional[str] = None

class Signal(BaseModel):
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
