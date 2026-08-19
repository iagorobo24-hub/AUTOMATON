from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.accounting.service import AccountingService
from app.agent_evolution.policy import bootstrap_evolution_policy
from app.agent_evolution.service import AgentEvolutionService, EvolutionError
from app.models import (
    Account,
    Agent,
    AgentFitnessEvaluation,
    AgentLifecycleEvent,
    AgentLineage,
    AgentStatus,
    StrategyEnum,
)


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _parent(session: Session, *, status=AgentStatus.ACTIVO):
    agent = Agent(
        nombre="parent",
        presupuesto_inicial=1000,
        presupuesto_actual=1000,
        estrategia=StrategyEnum.S1,
        estado=status,
        umbral_replica=0.15,
    )
    session.add(agent); session.commit(); session.refresh(agent)
    account = AccountingService(session).create_account(agent.id, Decimal("1000"))
    return agent, account


def _evaluation(session: Session, agent: Agent, decision="PASS"):
    policy = bootstrap_evolution_policy(session)
    evaluation = AgentFitnessEvaluation(
        agent_id=agent.id,
        policy_id=policy.id,
        policy_version=policy.version,
        backtest_run_id=1 if decision == "PASS" else None,
        strategy_id=agent.estrategia.value,
        strategy_version="baseline-v1" if decision == "PASS" else None,
        strategy_code_sha256="f" * 64 if decision == "PASS" else None,
        backtest_round_trips=6 if decision == "PASS" else None,
        backtest_net_return=Decimal("0.04") if decision == "PASS" else None,
        backtest_expectancy=Decimal("1.5") if decision == "PASS" else None,
        backtest_max_drawdown=Decimal("0.08") if decision == "PASS" else None,
        paper_closed_trades=4 if decision == "PASS" else 0,
        paper_realized_pnl=Decimal("12") if decision == "PASS" else Decimal("0"),
        decision=decision,
        reason_codes="PASS" if decision == "PASS" else "PAPER_TRADES_INSUFFICIENT",
    )
    session.add(evaluation); session.commit(); session.refresh(evaluation)
    return evaluation


def test_replication_rejects_inactive_parent_before_money_moves(monkeypatch):
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        parent, account = _parent(session, status=AgentStatus.MUERTO)
        with pytest.raises(EvolutionError, match="active"):
            AgentEvolutionService(session).replicate(parent.id)
        session.refresh(account)
        assert account.cash == Decimal("1000")
        assert len(session.exec(select(AgentLineage)).all()) == 0


def test_replication_rejects_fitness_reject_without_creating_child(monkeypatch):
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        parent, account = _parent(session)
        rejected = _evaluation(session, parent, "REJECT")
        monkeypatch.setattr("app.agent_evolution.service.FitnessService.evaluate", lambda self, agent_id: rejected)

        with pytest.raises(EvolutionError, match="fitness rejected"):
            AgentEvolutionService(session).replicate(parent.id)

        assert session.exec(select(Agent).where(Agent.padre_id == parent.id)).all() == []
        session.refresh(account)
        assert account.cash == Decimal("1000")
        assert rejected.consumed_by_lineage_id is None


def test_replication_transfers_25_percent_and_persists_lineage_without_mutating_strategy(monkeypatch):
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        parent, parent_account = _parent(session)
        passed = _evaluation(session, parent, "PASS")
        monkeypatch.setattr("app.agent_evolution.service.FitnessService.evaluate", lambda self, agent_id: passed)

        result = AgentEvolutionService(session).replicate(parent.id)

        child = result.child
        lineage = result.lineage
        session.refresh(parent); session.refresh(parent_account); session.refresh(passed)
        child_account = session.exec(select(Account).where(Account.agente_id == child.id)).one()

        assert result.allocated_capital == Decimal("250")
        assert parent.estado == AgentStatus.ACTIVO
        assert child.estado == AgentStatus.ACTIVO
        assert child.estrategia == parent.estrategia == StrategyEnum.S1
        assert child.padre_id == parent.id
        assert child_account.cash == Decimal("250")
        assert child_account.funded_capital == Decimal("250")
        assert parent_account.cash == Decimal("750")
        assert parent_account.funded_capital == Decimal("750")
        assert lineage.parent_agent_id == parent.id
        assert lineage.child_agent_id == child.id
        assert lineage.generation == 1
        assert lineage.strategy_version == "baseline-v1"
        assert lineage.strategy_code_sha256 == "f" * 64
        assert passed.consumed_by_lineage_id == lineage.id

        events = session.exec(select(AgentLifecycleEvent).order_by(AgentLifecycleEvent.id)).all()
        assert {(e.agent_id, e.event_type) for e in events} == {
            (parent.id, "REPLICATED_TO"),
            (child.id, "REPLICATED_FROM"),
        }


def test_each_replication_requires_a_fresh_pass_evaluation(monkeypatch):
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        parent, account = _parent(session)
        calls = []

        def fresh(self, agent_id):
            evaluation = _evaluation(session, parent, "PASS")
            calls.append(evaluation.id)
            return evaluation

        monkeypatch.setattr("app.agent_evolution.service.FitnessService.evaluate", fresh)
        first = AgentEvolutionService(session).replicate(parent.id)
        second = AgentEvolutionService(session).replicate(parent.id)

        assert calls[0] != calls[1]
        assert first.lineage.fitness_evaluation_id != second.lineage.fitness_evaluation_id
        assert first.allocated_capital == Decimal("250")
        assert second.allocated_capital == Decimal("187.5")
        session.refresh(account)
        assert account.cash == Decimal("562.5")
        assert account.funded_capital == Decimal("562.5")
