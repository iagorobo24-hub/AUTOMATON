from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel


MONEY = Numeric(28, 8)
QUANTITY = Numeric(36, 18)
RATIO = Numeric(18, 10)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RiskProfile(SQLModel, table=True):
    __tablename__ = "risk_profiles"
    __table_args__ = (UniqueConstraint("version", name="uq_risk_profile_version"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="Default Paper Risk", max_length=64)
    version: str = Field(index=True, max_length=32)
    active: bool = Field(default=True, index=True)
    paused: bool = Field(default=False)
    max_order_notional: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    max_order_equity_pct: Decimal = Field(sa_column=Column(RATIO, nullable=False))
    max_total_exposure_pct: Decimal = Field(sa_column=Column(RATIO, nullable=False))
    max_symbol_exposure_pct: Decimal = Field(sa_column=Column(RATIO, nullable=False))
    max_open_positions: int = Field(default=4)
    max_realized_loss_pct: Decimal = Field(sa_column=Column(RATIO, nullable=False))
    max_drawdown_pct: Decimal = Field(sa_column=Column(RATIO, nullable=False))
    max_quote_age_seconds: int = Field(default=30)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class RiskDecision(SQLModel, table=True):
    __tablename__ = "risk_decisions"

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="portfolio_accounts.id", index=True)
    agent_id: int = Field(foreign_key="agents.id", index=True)
    profile_id: int = Field(foreign_key="risk_profiles.id", index=True)
    profile_version: str = Field(max_length=32)
    symbol: str = Field(index=True, max_length=32)
    side: str = Field(max_length=8)
    quantity: Decimal = Field(sa_column=Column(QUANTITY, nullable=False))
    provider: str = Field(max_length=64)
    quote_observed_at: datetime
    market_price: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    requested_notional: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    equity: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    funded_capital: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    total_exposure_before: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    projected_total_exposure: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    symbol_exposure_before: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    projected_symbol_exposure: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    open_positions_before: int = Field(default=0)
    projected_open_positions: int = Field(default=0)
    realized_pnl: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    drawdown_pct: Decimal = Field(sa_column=Column(RATIO, nullable=False))
    decision: str = Field(index=True, max_length=8)
    reason_code: str = Field(index=True, max_length=64)
    reason: str = Field(max_length=256)
    consumed_at: Optional[datetime] = Field(default=None)
    paper_execution_id: Optional[int] = Field(default=None, foreign_key="paper_executions.id", index=True)
    created_at: datetime = Field(default_factory=utcnow)
