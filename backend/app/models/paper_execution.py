from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel


MONEY = Numeric(28, 8)
QUANTITY = Numeric(36, 18)
BPS = Numeric(16, 8)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PaperExecution(SQLModel, table=True):
    __tablename__ = "paper_executions"
    __table_args__ = (
        UniqueConstraint("order_id", name="uq_paper_execution_order"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="portfolio_accounts.id", index=True)
    agent_id: int = Field(foreign_key="agents.id", index=True)
    order_id: int = Field(foreign_key="portfolio_orders.id", index=True)
    fill_id: Optional[int] = Field(default=None, foreign_key="portfolio_fills.id", index=True)
    symbol: str = Field(index=True, max_length=32)
    side: str = Field(max_length=8)
    requested_quantity: Decimal = Field(sa_column=Column(QUANTITY, nullable=False))
    origin: str = Field(default="operator", max_length=32)
    policy_version: str = Field(default="paper-v1", max_length=32)
    provider: str = Field(max_length=64)
    provider_symbol: str = Field(max_length=32)
    quote_observed_at: datetime
    quote_received_at: datetime
    market_price: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    fill_price: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    slippage_bps: Decimal = Field(sa_column=Column(BPS, nullable=False))
    fee_bps: Decimal = Field(sa_column=Column(BPS, nullable=False))
    fee: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    status: str = Field(default="PENDING", max_length=24)
    rejection_reason: Optional[str] = Field(default=None, max_length=256)
    evidence_mode: str = Field(default="paper", max_length=16)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class PaperRequest(SQLModel, table=True):
    __tablename__ = "paper_requests"
    __table_args__ = (
        UniqueConstraint("request_id", name="uq_paper_request_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: str = Field(index=True, max_length=128)
    request_fingerprint: str = Field(max_length=64)
    account_id: int = Field(foreign_key="portfolio_accounts.id", index=True)
    execution_id: Optional[int] = Field(default=None, foreign_key="paper_executions.id", index=True)
    status: str = Field(default="PROCESSING", max_length=24)
    http_status: int = Field(default=200)
    error_detail: Optional[str] = Field(default=None, max_length=256)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
