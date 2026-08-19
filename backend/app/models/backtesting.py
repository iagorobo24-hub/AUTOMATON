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


class BacktestRun(SQLModel, table=True):
    __tablename__ = "backtest_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: int = Field(foreign_key="backtest_datasets.id", index=True)
    dataset_sha256: str = Field(index=True, max_length=64)
    strategy_id: str = Field(index=True, max_length=8)
    strategy_version: str = Field(default="baseline-v1", max_length=32)
    execution_policy: str = Field(default="backtest-v1", max_length=32)
    initial_capital: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    fee_bps: Decimal = Field(sa_column=Column(RATIO, nullable=False))
    slippage_bps: Decimal = Field(sa_column=Column(RATIO, nullable=False))
    position_fraction: Decimal = Field(sa_column=Column(RATIO, nullable=False))
    risk_profile_version: str = Field(default="backtest-risk-v1", max_length=32)
    code_commit: Optional[str] = Field(default=None, max_length=64)
    status: str = Field(default="RUNNING", index=True, max_length=24)
    failure_reason: Optional[str] = Field(default=None, max_length=256)
    initial_equity: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    final_equity: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    net_pnl: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    net_return: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    trade_count: Optional[int] = Field(default=None)
    round_trip_count: Optional[int] = Field(default=None)
    wins: Optional[int] = Field(default=None)
    losses: Optional[int] = Field(default=None)
    win_rate: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    average_win: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    average_loss: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    expectancy: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    gross_profit: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    gross_loss: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    profit_factor: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    max_drawdown: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    total_fees: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    exposure_fraction: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    forced_exit_count: Optional[int] = Field(default=None)
    started_at: datetime = Field(default_factory=utcnow)
    completed_at: Optional[datetime] = Field(default=None)


class BacktestTrade(SQLModel, table=True):
    __tablename__ = "backtest_trades"

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="backtest_runs.id", index=True)
    side: str = Field(max_length=8)
    signal_candle_time: Optional[datetime] = Field(default=None)
    execution_candle_time: datetime = Field(index=True)
    quantity: Decimal = Field(sa_column=Column(QUANTITY, nullable=False))
    market_price: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    fill_price: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    fee: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    realized_pnl: Decimal = Field(default=Decimal("0"), sa_column=Column(MONEY, nullable=False))
    exit_reason: Optional[str] = Field(default=None, max_length=64)


class BacktestEquityPoint(SQLModel, table=True):
    __tablename__ = "backtest_equity_points"
    __table_args__ = (
        UniqueConstraint("run_id", "ordinal", name="uq_backtest_equity_ordinal"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="backtest_runs.id", index=True)
    ordinal: int
    candle_time: datetime = Field(index=True)
    cash: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    market_value: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    equity: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    exposure: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    drawdown: Decimal = Field(sa_column=Column(RATIO, nullable=False))
