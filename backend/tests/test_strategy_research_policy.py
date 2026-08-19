from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.models import ResearchPolicy
from app.strategy_research.policy import bootstrap_research_policy


def test_research_v1_bootstrap_is_idempotent_and_persists_exact_gates():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        first = bootstrap_research_policy(session)
        second = bootstrap_research_policy(session)
        assert first.id == second.id
        rows = session.exec(select(ResearchPolicy)).all()
        assert len(rows) == 1
        policy = rows[0]
        assert policy.version == "research-v1"
        assert policy.min_historical_windows == 3
        assert policy.min_validation_round_trips == 5
        assert policy.min_oos_round_trips == 5
        assert policy.max_oos_drawdown == Decimal("0.15")
        assert policy.min_oos_profit_factor == Decimal("1.05")
        assert policy.max_relative_return_degradation == Decimal("0.50")
        assert policy.min_forward_closing_sells == 3
        assert policy.active is True
