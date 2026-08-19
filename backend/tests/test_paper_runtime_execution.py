from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.accounting.service import AccountingService
from app.market_data.contracts import Quote
from app.models import Agent, AgentStatus, PaperExecution, PaperRequest, RiskDecision, StrategyEnum
from app.paper_runtime.execution import execute_runtime_cycle
from app.paper_runtime.service import PaperRuntimeService
from app.models.paper_runtime import PaperRuntimeCycle
from app.risk.bootstrap import ensure_active_risk_profile

UTC = timezone.utc


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


class FakeMarketData:
    async def get_quote(self, symbol):
        return Quote(
            symbol=symbol, price=Decimal("100"), observed_at=datetime.now(UTC), received_at=datetime.now(UTC),
            provider="fixture_real", provider_symbol=symbol.replace("/", ""), timestamp_source="provider",
        )


def _setup(session):
    agent = Agent(nombre="auto", presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=StrategyEnum.S1, estado=AgentStatus.ACTIVO)
    session.add(agent); session.commit(); session.refresh(agent)
    account = AccountingService(session).create_account(agent.id, Decimal("1000"))
    ensure_active_risk_profile(session)
    runtime = PaperRuntimeService(session).create_session(name="auto", symbol="BTC/USDT", interval="1m", agent_ids=[agent.id])
    PaperRuntimeService(session).start(runtime.id)
    cycle = PaperRuntimeCycle(
        session_id=runtime.id, agent_id=agent.id, account_id=account.id, symbol="BTC/USDT", interval="1m",
        candle_close=datetime(2026, 8, 19, 20, 0, tzinfo=UTC), signal="BUY", outcome="INTENT_BUY",
    )
    session.add(cycle); session.commit(); session.refresh(cycle)
    return agent, account, runtime, cycle


@pytest.mark.asyncio
async def test_runtime_buy_flows_through_risk_paper_and_accounting():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent, account, runtime, cycle = _setup(session)
        result = await execute_runtime_cycle(session, cycle.id, FakeMarketData())
        assert result.outcome == "FILLED"
        assert result.request_id.startswith("runtime:")
        assert result.risk_decision_id is not None
        assert result.paper_execution_id is not None

        execution = session.get(PaperExecution, result.paper_execution_id)
        assert execution.origin == "strategy_runtime"
        assert execution.status == "FILLED"
        decision = session.get(RiskDecision, result.risk_decision_id)
        assert decision.decision == "ALLOW"
        request = session.exec(select(PaperRequest).where(PaperRequest.request_id == result.request_id)).one()
        assert request.status == "COMPLETED"


@pytest.mark.asyncio
async def test_replaying_same_runtime_cycle_cannot_create_second_execution():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent, account, runtime, cycle = _setup(session)
        first = await execute_runtime_cycle(session, cycle.id, FakeMarketData())
        second = await execute_runtime_cycle(session, cycle.id, FakeMarketData())
        assert second.paper_execution_id == first.paper_execution_id
        assert len(session.exec(select(PaperExecution)).all()) == 1
        assert len(session.exec(select(RiskDecision)).all()) == 1
