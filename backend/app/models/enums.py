from enum import Enum

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

class NotificationType(str, Enum):
    AGENT_CREATED = "agent_created"
    AGENT_REPLICATED = "agent_replicated"
    AGENT_DYING = "agent_dying"
    AGENT_DEAD = "agent_dead"
    TRADE_OPENED = "trade_opened"
    TRADE_CLOSED = "trade_closed"
    TRADE_WIN = "trade_win"
    TRADE_LOSS = "trade_loss"
    PAYMENT_RECEIVED = "payment_received"
    ALERT_LOW_BALANCE = "alert_low_balance"
    ALERT_HIGH_DRAWDOWN = "alert_high_drawdown"
    ALERT_REPLICATION_READY = "alert_replication_ready"
    SYSTEM_INFO = "system_info"
    OPPORTUNITY_DETECTED = "opportunity_detected"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
