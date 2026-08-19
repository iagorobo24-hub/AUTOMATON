from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, UniqueConstraint
from sqlmodel import Field, SQLModel

from app.models.backtesting import UTCDateTime


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utc_column(*, nullable: bool = False):
    return Column(UTCDateTime(), nullable=nullable)


class PaperRuntimeSession(SQLModel, table=True):
    __tablename__ = "paper_runtime_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=128)
    symbol: str = Field(index=True, max_length=32)
    interval: str = Field(max_length=16)
    policy_version: str = Field(default="runtime-v1", max_length=32)
    status: str = Field(default="CREATED", index=True, max_length=32)
    poll_seconds: int = Field(default=15)
    max_consecutive_failures: int = Field(default=5)
    consecutive_failures: int = Field(default=0)
    heartbeat_at: Optional[datetime] = Field(default=None, sa_column=utc_column(nullable=True))
    last_cycle_at: Optional[datetime] = Field(default=None, sa_column=utc_column(nullable=True))
    last_error: Optional[str] = Field(default=None, max_length=256)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())
    started_at: Optional[datetime] = Field(default=None, sa_column=utc_column(nullable=True))
    stopped_at: Optional[datetime] = Field(default=None, sa_column=utc_column(nullable=True))
    updated_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class PaperRuntimeAgent(SQLModel, table=True):
    __tablename__ = "paper_runtime_agents"
    __table_args__ = (
        UniqueConstraint("session_id", "agent_id", name="uq_runtime_session_agent"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="paper_runtime_sessions.id", index=True)
    agent_id: int = Field(foreign_key="agents.id", index=True)
    enabled: bool = Field(default=True)
    last_candle_close: Optional[datetime] = Field(default=None, sa_column=utc_column(nullable=True))
    last_signal: Optional[str] = Field(default=None, max_length=8)
    last_outcome: Optional[str] = Field(default=None, max_length=64)
    last_cycle_id: Optional[int] = Field(default=None, index=True)
    updated_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class PaperRuntimeCycle(SQLModel, table=True):
    __tablename__ = "paper_runtime_cycles"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "agent_id",
            "candle_close",
            name="uq_runtime_cycle_session_agent_candle",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="paper_runtime_sessions.id", index=True)
    agent_id: int = Field(foreign_key="agents.id", index=True)
    account_id: int = Field(foreign_key="portfolio_accounts.id", index=True)
    symbol: str = Field(index=True, max_length=32)
    interval: str = Field(max_length=16)
    candle_close: datetime = Field(sa_column=Column(UTCDateTime(), nullable=False, index=True))
    signal: str = Field(max_length=8)
    outcome: str = Field(index=True, max_length=64)
    request_id: Optional[str] = Field(default=None, index=True, max_length=128)
    risk_decision_id: Optional[int] = Field(default=None, foreign_key="risk_decisions.id", index=True)
    paper_execution_id: Optional[int] = Field(default=None, foreign_key="paper_executions.id", index=True)
    error_detail: Optional[str] = Field(default=None, max_length=256)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())


class PaperRuntimeEvent(SQLModel, table=True):
    __tablename__ = "paper_runtime_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="paper_runtime_sessions.id", index=True)
    event_type: str = Field(index=True, max_length=64)
    reason: str = Field(max_length=256)
    created_at: datetime = Field(default_factory=utcnow, sa_column=utc_column())
