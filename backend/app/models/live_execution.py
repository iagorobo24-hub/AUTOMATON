from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.models.backtesting import UTCDateTime

MONEY = Numeric(28, 8)
QUANTITY = Numeric(36, 18)
RATIO = Numeric(18, 10)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utc_column(*, nullable: bool = False):
    return Column(UTCDateTime(), nullable=nullable)


class LivePolicy(SQLModel, table=True):
    __tablename__ = "live_policies"
    __table_args__ = (UniqueConstraint("version", name="uq_live_policy_version"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    version: str = Field(index=True, max_length=32)
    active: bool = Field(default=True, index=True)
    max_deployable_capital: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    max_order_notional: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    max_symbol_exposure: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    max_portfolio_exposure: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    max_session_loss: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    max_drawdown: Decimal = Field(sa_column=Column(RATIO, nullable=False))
    max_consecutive_execution_errors: int = Field(default=3)
    stale_market_data_seconds: int = Field(default=30)
    rollout_stage: str = Field(default="CANARY", max_length=16)
    rollout_capital_fraction: Decimal = Field(sa_column=Column(RATIO, nullable=False))
    manual_approval_required: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class LiveReadinessEvaluation(SQLModel, table=True):
    __tablename__ = "live_readiness_evaluations"

    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: Optional[int] = Field(default=None, foreign_key="strategy_candidates.id", index=True)
    policy_version: str = Field(index=True, max_length=32)
    architecture_ready: bool = Field(default=False, index=True)
    real_capital_blocked: bool = Field(default=True)
    decision: str = Field(index=True, max_length=32)
    reason_codes: str = Field(default="", max_length=1024)
    reason: str = Field(default="", max_length=1024)
    strategy_source_sha256: Optional[str] = Field(default=None, max_length=64)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class LiveOrderIntent(SQLModel, table=True):
    __tablename__ = "live_order_intents"
    __table_args__ = (UniqueConstraint("client_order_id", name="uq_live_intent_client_order_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: int = Field(foreign_key="strategy_candidates.id", index=True)
    client_order_id: str = Field(index=True, max_length=80)
    source_event_id: str = Field(index=True, max_length=128)
    symbol: str = Field(index=True, max_length=32)
    side: str = Field(max_length=8)
    quantity: Decimal = Field(sa_column=Column(QUANTITY, nullable=False))
    reference_price: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    requested_notional: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    projected_symbol_exposure: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    projected_portfolio_exposure: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    status: str = Field(default="PREPARED", index=True, max_length=32)
    reason_code: str = Field(default="OK", max_length=64)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class LiveOrderRecord(SQLModel, table=True):
    __tablename__ = "live_order_records"
    id: Optional[int] = Field(default=None, primary_key=True)
    intent_id: int = Field(foreign_key="live_order_intents.id", index=True)
    client_order_id: str = Field(index=True, max_length=80)
    venue_order_id: Optional[str] = Field(default=None, index=True, max_length=128)
    status: str = Field(default="NOT_TRANSMITTED", index=True, max_length=32)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class LiveFillRecord(SQLModel, table=True):
    __tablename__ = "live_fill_records"
    id: Optional[int] = Field(default=None, primary_key=True)
    order_record_id: int = Field(foreign_key="live_order_records.id", index=True)
    venue_fill_id: str = Field(index=True, max_length=128)
    quantity: Decimal = Field(sa_column=Column(QUANTITY, nullable=False))
    price: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class LiveReconciliation(SQLModel, table=True):
    __tablename__ = "live_reconciliations"
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(index=True, max_length=32)
    reason_code: str = Field(index=True, max_length=64)
    details: str = Field(default="", max_length=2048)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class LiveCircuitBreakerEvent(SQLModel, table=True):
    __tablename__ = "live_circuit_breaker_events"
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(index=True, max_length=32)
    reason_code: str = Field(index=True, max_length=64)
    reason: str = Field(max_length=512)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class LiveEmergencyStop(SQLModel, table=True):
    __tablename__ = "live_emergency_stop"
    __table_args__ = (UniqueConstraint("singleton_key", name="uq_live_emergency_singleton"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    singleton_key: str = Field(default="global", max_length=16)
    active: bool = Field(default=False, index=True)
    reason: Optional[str] = Field(default=None, max_length=512)
    updated_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())
