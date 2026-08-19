from datetime import datetime, timezone
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.accounting.service import AccountingService
from app.database import get_session
from app.main import app
from app.market_data.contracts import Quote
from app.market_data.router import get_market_data_service
from app.models import Agent, StrategyEnum
from app.models.accounting import Fill
from app.models.paper_execution import PaperExecution, PaperRequest


class CountingMarketData:
    name = "fixture_real"

    def __init__(self):
        self.calls = 0

    async def get_quote(self, _symbol: str) -> Quote:
        self.calls += 1
        now = datetime.now(timezone.utc)
        return Quote(
            symbol="BTC/USDT",
            price=Decimal("100"),
            observed_at=now,
            received_at=now,
            provider=self.name,
            provider_symbol="BTCUSDT",
            timestamp_source="provider",
        )


@pytest.fixture
def setup_app():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    provider = CountingMarketData()

    def _get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _get_session
    app.dependency_overrides[get_market_data_service] = lambda: provider

    with Session(engine) as session:
        agent = Agent(
            nombre="IDEMPOTENT",
            presupuesto_inicial=1000,
            presupuesto_actual=1000,
            estrategia=StrategyEnum.S1,
        )
        session.add(agent)
        session.commit()
        session.refresh(agent)
        account_id = AccountingService(session).create_account(
            agent.id, Decimal("1000")
        ).id

    yield engine, provider, account_id
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)


@pytest.mark.asyncio
async def test_same_request_id_returns_same_execution_without_second_fill(setup_app):
    engine, provider, account_id = setup_app
    transport = ASGITransport(app=app)
    params = {
        "request_id": "operator-001",
        "account_id": account_id,
        "symbol": "BTC-USDT",
        "side": "BUY",
        "quantity": "1",
    }

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post("/api/paper/orders/market", params=params)
        second = await client.post("/api/paper/orders/market", params=params)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    assert second.json()["idempotent_replay"] is True
    assert provider.calls == 1

    with Session(engine) as session:
        assert len(session.exec(select(PaperExecution)).all()) == 1
        assert len(session.exec(select(Fill)).all()) == 1


@pytest.mark.asyncio
async def test_request_id_cannot_be_reused_for_different_order_payload(setup_app):
    engine, _provider, account_id = setup_app
    transport = ASGITransport(app=app)
    base = {
        "request_id": "operator-002",
        "account_id": account_id,
        "symbol": "BTC-USDT",
        "side": "BUY",
    }

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post(
            "/api/paper/orders/market", params={**base, "quantity": "1"}
        )
        conflict = await client.post(
            "/api/paper/orders/market", params={**base, "quantity": "2"}
        )

    assert first.status_code == 200
    assert conflict.status_code == 409
    assert "request_id" in conflict.json()["detail"]

    with Session(engine) as session:
        assert len(session.exec(select(PaperExecution)).all()) == 1
        assert len(session.exec(select(Fill)).all()) == 1


@pytest.mark.asyncio
async def test_rejected_financial_request_is_idempotent_and_links_rejection(setup_app):
    engine, provider, account_id = setup_app
    transport = ASGITransport(app=app)
    params = {
        "request_id": "operator-rejected",
        "account_id": account_id,
        "symbol": "BTC-USDT",
        "side": "BUY",
        "quantity": "20",
    }

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post("/api/paper/orders/market", params=params)
        second = await client.post("/api/paper/orders/market", params=params)

    assert first.status_code == 409
    assert second.status_code == 409
    assert second.json()["detail"] == first.json()["detail"]
    assert provider.calls == 1

    with Session(engine) as session:
        executions = session.exec(select(PaperExecution)).all()
        requests = session.exec(select(PaperRequest)).all()
        assert len(executions) == 1
        assert executions[0].status == "REJECTED"
        assert len(requests) == 1
        assert requests[0].execution_id == executions[0].id
        assert requests[0].status == "COMPLETED"
        assert requests[0].http_status == 409


@pytest.mark.asyncio
async def test_whitespace_request_id_is_rejected_before_market_or_financial_state(setup_app):
    engine, provider, account_id = setup_app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/paper/orders/market",
            params={
                "request_id": "   ",
                "account_id": account_id,
                "symbol": "BTC-USDT",
                "side": "BUY",
                "quantity": "1",
            },
        )

    assert response.status_code == 422
    assert provider.calls == 0
    with Session(engine) as session:
        assert session.exec(select(PaperRequest)).all() == []
        assert session.exec(select(PaperExecution)).all() == []
        assert session.exec(select(Fill)).all() == []
