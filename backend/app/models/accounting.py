from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel


MONEY = Numeric(28, 8)
QUANTITY = Numeric(36, 18)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Account(SQLModel, table=True):
    __tablename__ = "portfolio_accounts"
    __table_args__ = (UniqueConstraint("agente_id", name="uq_portfolio_account_agent"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    agente_id: int = Field(foreign_key="agents.id", index=True)
    currency: str = Field(default="USDT", max_length=16)
    initial_capital: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    funded_capital: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    cash: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    reserved_cash: Decimal = Field(default=Decimal("0"), sa_column=Column(MONEY, nullable=False))
    realized_pnl: Decimal = Field(default=Decimal("0"), sa_column=Column(MONEY, nullable=False))
    fees_paid: Decimal = Field(default=Decimal("0"), sa_column=Column(MONEY, nullable=False))
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Order(SQLModel, table=True):
    __tablename__ = "portfolio_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="portfolio_accounts.id", index=True)
    symbol: str = Field(index=True, max_length=32)
    side: str = Field(max_length=8)
    order_type: str = Field(default="MARKET", max_length=16)
    status: str = Field(default="PENDING", max_length=24)
    requested_quantity: Decimal = Field(sa_column=Column(QUANTITY, nullable=False))
    filled_quantity: Decimal = Field(default=Decimal("0"), sa_column=Column(QUANTITY, nullable=False))
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Fill(SQLModel, table=True):
    __tablename__ = "portfolio_fills"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="portfolio_orders.id", index=True)
    account_id: int = Field(foreign_key="portfolio_accounts.id", index=True)
    symbol: str = Field(index=True, max_length=32)
    side: str = Field(max_length=8)
    quantity: Decimal = Field(sa_column=Column(QUANTITY, nullable=False))
    price: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    fee: Decimal = Field(default=Decimal("0"), sa_column=Column(MONEY, nullable=False))
    observed_at: datetime
    evidence_mode: str = Field(default="paper", max_length=16)
    created_at: datetime = Field(default_factory=utcnow)


class Position(SQLModel, table=True):
    __tablename__ = "portfolio_positions"
    __table_args__ = (
        UniqueConstraint("account_id", "symbol", name="uq_portfolio_position_account_symbol"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="portfolio_accounts.id", index=True)
    symbol: str = Field(index=True, max_length=32)
    quantity: Decimal = Field(default=Decimal("0"), sa_column=Column(QUANTITY, nullable=False))
    average_cost: Decimal = Field(default=Decimal("0"), sa_column=Column(MONEY, nullable=False))
    realized_pnl: Decimal = Field(default=Decimal("0"), sa_column=Column(MONEY, nullable=False))
    updated_at: datetime = Field(default_factory=utcnow)


class LedgerEntry(SQLModel, table=True):
    __tablename__ = "portfolio_ledger"

    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="portfolio_accounts.id", index=True)
    entry_type: str = Field(max_length=32)
    amount: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    reason: str = Field(max_length=128)
    created_at: datetime = Field(default_factory=utcnow)
