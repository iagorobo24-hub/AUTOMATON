from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.accounting.service import AccountingService
from app.market_data.contracts import Candle
from app.models import Agent, AgentStatus, Position, StrategyEnum
from app.paper_runtime.cycle import evaluate_agent_cycle
from app.paper_runtime.service import PaperRuntimeService

UTC = timezone.utc


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _candles(count=20):
    start = datetime(2026, 8, 19, 18, 0, tzinfo=UTC)
    return [
        Candle(
            symbol="BTC/USDT", interval="1m",
            open_time=start + timedelta(minutes=i),
            close_time=start + timedelta(minutes=i + 1),
            open=Decimal(100 + i), high=Decimal(101 + i), low=Decimal(99 + i), close=Decimal(100 + i),
            volume=Decimal("1"), provider="fixture_real", provider_symbol="BTCUSDT",
        )
        for i in range(count)
    ]


class FakeMarketData:
    async def get_candles(self, symbol, *, interval="1m", limit=100):
        return _candles(min(limit, 20))


class FixedStrategy:
    def __init__(self, signal): self.signal = signal
    def calcular_señal(self, prices): return self.signal


def _setup(session):
    agent = Agent(nombre="cycle", presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=StrategyEnum.S1, estado=AgentStatus.ACTIVO)
    session.add(agent); session.commit(); session.refresh(agent)
    account = AccountingService(session).create_account(agent.id, Decimal("1000"))
    runtime = PaperRuntimeService(session).create_session(name="r", symbol="BTC/USDT", interval="1m", agent_ids=[agent.id])
    PaperRuntimeService(session).start(runtime.id)
    return agent, account, runtime


@pytest.mark.asyncio
async def test_same_closed_candle_is_evaluated_once(monkeypatch):
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent, account, runtime = _setup(session)
        monkeypatch.setattr("app.paper_runtime.cycle.get_strategy", lambda _: FixedStrategy("HOLD"))
        first = await evaluate_agent_cycle(session, runtime.id, agent.id, FakeMarketData())
        second = await evaluate_agent_cycle(session, runtime.id, agent.id, FakeMarketData())
        assert first.outcome == "NO_ACTION_HOLD"
        assert second is None


@pytest.mark.asyncio
async def test_buy_sell_and_position_guards(monkeypatch):
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent, account, runtime = _setup(session)
        monkeypatch.setattr("app.paper_runtime.cycle.get_strategy", lambda _: FixedStrategy("BUY"))
        buy = await evaluate_agent_cycle(session, runtime.id, agent.id, FakeMarketData())
        assert buy.outcome == "INTENT_BUY"

        # New session gives a fresh candle namespace for the same market observation.
        PaperRuntimeService(session).stop(runtime.id)
        runtime2 = PaperRuntimeService(session).create_session(name="r2", symbol="BTC/USDT", interval="1m", agent_ids=[agent.id])
        PaperRuntimeService(session).start(runtime2.id)
        session.add(Position(account_id=account.id, symbol="BTC/USDT", quantity=Decimal("1"), average_cost=Decimal("100")))
        session.commit()
        guarded = await evaluate_agent_cycle(session, runtime2.id, agent.id, FakeMarketData())
        assert guarded.outcome == "NO_ACTION_ALREADY_LONG"

        PaperRuntimeService(session).stop(runtime2.id)
        runtime3 = PaperRuntimeService(session).create_session(name="r3", symbol="BTC/USDT", interval="1m", agent_ids=[agent.id])
        PaperRuntimeService(session).start(runtime3.id)
        monkeypatch.setattr("app.paper_runtime.cycle.get_strategy", lambda _: FixedStrategy("SELL"))
        sell = await evaluate_agent_cycle(session, runtime3.id, agent.id, FakeMarketData())
        assert sell.outcome == "INTENT_SELL"
