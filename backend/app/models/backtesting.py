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


class BacktestDataset(SQLModel, table=True):
    __tablename__ = "backtest_datasets"
    __table_args__ = (
        UniqueConstraint("content_sha256", name="uq_backtest_dataset_sha256"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True, max_length=32)
    interval: str = Field(index=True, max_length=16)
    provider: str = Field(index=True, max_length=64)
    requested_start: datetime
    requested_end: datetime
    actual_start: datetime
    actual_end: datetime
    candle_count: int
    content_sha256: str = Field(index=True, max_length=64)
    status: str = Field(default="READY", index=True, max_length=16)
    created_at: datetime = Field(default_factory=utcnow)


class BacktestCandle(SQLModel, table=True):
    __tablename__ = "backtest_candles"
    __table_args__ = (
        UniqueConstraint("dataset_id", "ordinal", name="uq_backtest_candle_ordinal"),
        UniqueConstraint("dataset_id", "open_time", name="uq_backtest_candle_open_time"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: int = Field(foreign_key="backtest_datasets.id", index=True)
    ordinal: int = Field(index=True)
    symbol: str = Field(max_length=32)
    interval: str = Field(max_length=16)
    open_time: datetime = Field(index=True)
    close_time: datetime
    open: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    high: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    low: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    close: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    volume: Decimal = Field(sa_column=Column(QUANTITY, nullable=False))
    provider: str = Field(max_length=64)
    provider_symbol: str = Field(max_length=32)
