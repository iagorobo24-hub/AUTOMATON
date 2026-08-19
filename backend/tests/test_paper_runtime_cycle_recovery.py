from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.accounting.service import AccountingService
from app.models import Agent, AgentStatus, PaperRequest, PaperRuntimeCycle, StrategyEnum
from app.paper_runtime.execution import reconcile_runtime_cycles, runtime_request_id
from app.paper_runtime.service import PaperRuntimeService

UTC = timezone.utc


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def test_intent_without_paper_request_is_abandoned_after_restart_not_reexecuted():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent = Agent(nombre="crash", presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=StrategyEnum.S1, estado=AgentStatus.ACTIVO)
        session.add(agent); session.commit(); session.refresh(agent)
        account = AccountingService(session).create_account(agent.id, Decimal("1000"))
        runtime = PaperRuntimeService(session).create_session(name="crash", symbol="BTC/USDT", interval="1m", agent_ids=[agent.id])
        cycle = PaperRuntimeCycle(
            session_id=runtime.id, agent_id=agent.id, account_id=account.id, symbol="BTC/USDT", interval="1m",
            candle_close=datetime(2026, 8, 19, 20, 0, tzinfo=UTC), signal="BUY", outcome="INTENT_BUY",
        )
        session.add(cycle); session.commit(); session.refresh(cycle)
        cycle.request_id = runtime_request_id(cycle); session.add(cycle); session.commit()

        changed = reconcile_runtime_cycles(session)
        assert changed == 1
        session.refresh(cycle)
        assert cycle.outcome == "ABANDONED_RECOVERY"
        assert "no Paper request" in cycle.error_detail
