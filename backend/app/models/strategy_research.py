from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.models.backtesting import UTCDateTime

RATIO = Numeric(18, 10)
MONEY = Numeric(28, 8)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utc_column(*, nullable: bool = False):
    return Column(UTCDateTime(), nullable=nullable)


class ResearchPolicy(SQLModel, table=True):
    __tablename__ = "research_policies"
    __table_args__ = (UniqueConstraint("version", name="uq_research_policy_version"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    version: str = Field(index=True, max_length=32)
    active: bool = Field(default=True, index=True)
    min_historical_windows: int = Field(default=3)
    min_validation_round_trips: int = Field(default=5)
    min_oos_round_trips: int = Field(default=5)
    max_oos_drawdown: Decimal = Field(default=Decimal("0.15"), sa_column=Column(RATIO, nullable=False))
    min_oos_profit_factor: Decimal = Field(default=Decimal("1.05"), sa_column=Column(RATIO, nullable=False))
    max_relative_return_degradation: Decimal = Field(default=Decimal("0.50"), sa_column=Column(RATIO, nullable=False))
    min_forward_closing_sells: int = Field(default=3)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class ResearchStudy(SQLModel, table=True):
    __tablename__ = "research_studies"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=128)
    strategy_id: str = Field(index=True, max_length=8)
    policy_version: str = Field(default="research-v1", index=True, max_length=32)
    status: str = Field(default="DRAFT", index=True, max_length=24)
    notes: Optional[str] = Field(default=None, max_length=512)
    strategy_version: Optional[str] = Field(default=None, max_length=32)
    strategy_source_sha256: Optional[str] = Field(default=None, index=True, max_length=64)
    execution_policy: Optional[str] = Field(default=None, max_length=32)
    fee_bps: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    slippage_bps: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    position_fraction: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())
    updated_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class ResearchWindow(SQLModel, table=True):
    __tablename__ = "research_windows"
    __table_args__ = (
        UniqueConstraint("study_id", "backtest_run_id", name="uq_research_study_run"),
        UniqueConstraint("study_id", "ordinal", name="uq_research_study_ordinal"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    study_id: int = Field(foreign_key="research_studies.id", index=True)
    backtest_run_id: int = Field(foreign_key="backtest_runs.id", index=True)
    role: str = Field(index=True, max_length=16)
    ordinal: int
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class ResearchEvaluation(SQLModel, table=True):
    __tablename__ = "research_evaluations"

    id: Optional[int] = Field(default=None, primary_key=True)
    study_id: int = Field(foreign_key="research_studies.id", index=True)
    policy_version: str = Field(index=True, max_length=32)
    decision: str = Field(index=True, max_length=16)
    reason_code: str = Field(index=True, max_length=64)
    reason: str = Field(max_length=512)
    strategy_id: str = Field(max_length=8)
    strategy_version: str = Field(max_length=32)
    strategy_source_sha256: str = Field(index=True, max_length=64)
    historical_run_ids: str = Field(max_length=512)
    forward_session_ids: Optional[str] = Field(default=None, max_length=512)
    validation_net_return: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    validation_expectancy: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    oos_net_return: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    oos_expectancy: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    oos_max_drawdown: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    oos_profit_factor: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    forward_closing_sells: int = Field(default=0)
    forward_realized_pnl: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class StrategyCandidate(SQLModel, table=True):
    __tablename__ = "strategy_candidates"
    __table_args__ = (
        UniqueConstraint(
            "strategy_id", "strategy_version", "strategy_source_sha256",
            name="uq_strategy_candidate_identity",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    study_id: int = Field(foreign_key="research_studies.id", index=True)
    evaluation_id: int = Field(foreign_key="research_evaluations.id", index=True)
    strategy_id: str = Field(index=True, max_length=8)
    strategy_version: str = Field(max_length=32)
    strategy_source_sha256: str = Field(index=True, max_length=64)
    status: str = Field(default="PROMOTED", index=True, max_length=16)
    operator_note: Optional[str] = Field(default=None, max_length=512)
    promoted_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())
