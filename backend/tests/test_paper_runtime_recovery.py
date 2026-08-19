import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.accounting.service import AccountingService
from app.market_data.quality import MarketDataUnavailable
from app.models import Agent, AgentStatus, StrategyEnum
from app.paper_runtime.scheduler import run_runtime_once
from app.paper_runtime.service import PaperRuntimeService


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


class DownMarketData:
    async def get_candles(self, symbol, *, interval="1m", limit=100):
        raise MarketDataUnavailable("provider down")


def _runtime(session):
    agent = Agent(nombre="down", presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=StrategyEnum.S1, estado=AgentStatus.ACTIVO)
    session.add(agent); session.commit(); session.refresh(agent)
    AccountingService(session).create_account(agent.id, 1000)
    runtime = PaperRuntimeService(session).create_session(
        name="down", symbol="BTC/USDT", interval="1m", agent_ids=[agent.id], max_consecutive_failures=2,
    )
    PaperRuntimeService(session).start(runtime.id)
    return runtime


@pytest.mark.asyncio
async def test_repeated_provider_failures_mark_session_degraded_without_fake_data():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        runtime = _runtime(session)
        await run_runtime_once(session, runtime.id, DownMarketData())
        refreshed = session.get(type(runtime), runtime.id)
        assert refreshed.status == "RUNNING"
        assert refreshed.consecutive_failures == 1

        await run_runtime_once(session, runtime.id, DownMarketData())
        refreshed = session.get(type(runtime), runtime.id)
        assert refreshed.status == "DEGRADED"
        assert refreshed.consecutive_failures == 2
        assert "provider" in refreshed.last_error.lower()
