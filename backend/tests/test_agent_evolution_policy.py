from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.agent_evolution.policy import bootstrap_evolution_policy, bootstrap_lifecycle_baselines
from app.models import Agent, AgentLifecycleEvent, AgentStatus, EvolutionPolicy, StrategyEnum


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def test_evolution_v1_bootstrap_is_idempotent_and_conservative():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        first = bootstrap_evolution_policy(session)
        second = bootstrap_evolution_policy(session)

        assert first.id == second.id
        assert first.version == "evolution-v1"
        assert first.active is True
        assert first.min_backtest_round_trips == 5
        assert first.min_backtest_net_return == Decimal("0")
        assert first.min_backtest_expectancy == Decimal("0")
        assert first.max_backtest_drawdown == Decimal("0.15")
        assert first.min_paper_closed_trades == 3
        assert first.min_paper_realized_pnl == Decimal("0")
        assert first.child_allocation_fraction == Decimal("0.25")
        assert len(session.exec(select(EvolutionPolicy)).all()) == 1


def test_legacy_agents_receive_one_baseline_lifecycle_event_without_fabricated_lineage():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent = Agent(
            nombre="legacy",
            presupuesto_inicial=1000,
            presupuesto_actual=1000,
            estrategia=StrategyEnum.S1,
            estado=AgentStatus.ACTIVO,
        )
        session.add(agent); session.commit(); session.refresh(agent)

        assert bootstrap_lifecycle_baselines(session) == 1
        assert bootstrap_lifecycle_baselines(session) == 0

        events = session.exec(select(AgentLifecycleEvent).where(AgentLifecycleEvent.agent_id == agent.id)).all()
        assert len(events) == 1
        assert events[0].event_type == "LEGACY_BASELINE"
        assert events[0].reason == "phase_6_existing_agent_baseline"
        assert events[0].fitness_evaluation_id is None
        assert events[0].lineage_id is None
