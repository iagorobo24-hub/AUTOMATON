from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel

RATIO = Numeric(18, 10)
MONEY = Numeric(28, 8)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EvolutionPolicy(SQLModel, table=True):
    __tablename__ = "evolution_policies"
    __table_args__ = (UniqueConstraint("version", name="uq_evolution_policy_version"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    version: str = Field(index=True, max_length=32)
    active: bool = Field(default=True, index=True)
    min_backtest_round_trips: int = Field(default=5)
    min_backtest_net_return: Decimal = Field(default=Decimal("0"), sa_column=Column(RATIO, nullable=False))
    min_backtest_expectancy: Decimal = Field(default=Decimal("0"), sa_column=Column(MONEY, nullable=False))
    max_backtest_drawdown: Decimal = Field(default=Decimal("0.15"), sa_column=Column(RATIO, nullable=False))
    min_paper_closed_trades: int = Field(default=3)
    min_paper_realized_pnl: Decimal = Field(default=Decimal("0"), sa_column=Column(MONEY, nullable=False))
    child_allocation_fraction: Decimal = Field(default=Decimal("0.25"), sa_column=Column(RATIO, nullable=False))
    created_at: datetime = Field(default_factory=utcnow)


class AgentFitnessEvaluation(SQLModel, table=True):
    __tablename__ = "agent_fitness_evaluations"

    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: int = Field(foreign_key="agents.id", index=True)
    policy_id: int = Field(foreign_key="evolution_policies.id", index=True)
    policy_version: str = Field(index=True, max_length=32)
    backtest_run_id: Optional[int] = Field(default=None, foreign_key="backtest_runs.id", index=True)
    strategy_id: str = Field(max_length=8)
    strategy_version: Optional[str] = Field(default=None, max_length=32)
    strategy_code_sha256: Optional[str] = Field(default=None, max_length=64)
    backtest_round_trips: Optional[int] = Field(default=None)
    backtest_net_return: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    backtest_expectancy: Optional[Decimal] = Field(default=None, sa_column=Column(MONEY, nullable=True))
    backtest_max_drawdown: Optional[Decimal] = Field(default=None, sa_column=Column(RATIO, nullable=True))
    paper_closed_trades: int = Field(default=0)
    paper_realized_pnl: Decimal = Field(default=Decimal("0"), sa_column=Column(MONEY, nullable=False))
    decision: str = Field(index=True, max_length=16)
    reason_codes: str = Field(max_length=512)
    consumed_by_lineage_id: Optional[int] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=utcnow)


class AgentLineage(SQLModel, table=True):
    __tablename__ = "agent_lineage"
    __table_args__ = (UniqueConstraint("child_agent_id", name="uq_agent_lineage_child"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_agent_id: int = Field(foreign_key="agents.id", index=True)
    child_agent_id: int = Field(foreign_key="agents.id", index=True)
    generation: int = Field(default=1)
    strategy_id: str = Field(max_length=8)
    strategy_version: str = Field(max_length=32)
    strategy_code_sha256: str = Field(max_length=64)
    policy_version: str = Field(max_length=32)
    fitness_evaluation_id: int = Field(foreign_key="agent_fitness_evaluations.id", index=True)
    allocated_capital: Decimal = Field(sa_column=Column(MONEY, nullable=False))
    created_at: datetime = Field(default_factory=utcnow)


class AgentLifecycleEvent(SQLModel, table=True):
    __tablename__ = "agent_lifecycle_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: int = Field(foreign_key="agents.id", index=True)
    event_type: str = Field(index=True, max_length=32)
    reason: str = Field(max_length=256)
    fitness_evaluation_id: Optional[int] = Field(default=None, foreign_key="agent_fitness_evaluations.id", index=True)
    lineage_id: Optional[int] = Field(default=None, foreign_key="agent_lineage.id", index=True)
    created_at: datetime = Field(default_factory=utcnow)
