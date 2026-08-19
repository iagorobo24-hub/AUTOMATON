from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.accounting.service import AccountingService
from app.database import get_session
from app.main import app
from app.market_data.contracts import Quote
from app.market_data.quality import MarketDataUnavailable
from app.market_data.router import get_market_data_service
from app.models import Agent, StrategyEnum
from app.models.accounting import Fill, Position
from app.models.paper_execution import PaperExecution


NOW = datetime.now(timezone.utc)


class RealFixtureMarketData:
    name = "fixture_real"

    def status(self):
        return {
            "provider": self.name,
            "evidence_mode": "real",
            "synthetic_fallback": False,
            "execution_capability": False,
        }

    async def get_quote(self, _symbol: str) -> Quote:
        return Quote(
            symbol="BTC/USDT",
            price=Decimal("100"),
            observed_at=NOW,
            received_at=NOW + timedelta(milliseconds=10),
            provider=self.name,
            provider_symbol="BTCUSDT",
            timestamp_source="provider",
        )


class UnavailableMarketData(RealFixtureMarketData):
    async def get_quote(self, _symbol: str) -> Quote:
        raise MarketDataUnavailable("provider down")


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def app_db(engine):
    def _get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _get_session
    app.dependency_overrides[get_market_data_service] = lambda: RealFixtureMarketData()
    yield engine
    app.dependency_overrides.clear()


def _account_id(engine) -> int:
    with Session(engine) as session:
        agent = Agent(
            nombre="PAPER-API",
            presupuesto_inicial=1000,
            presupuesto_actual=1000,
            estrategia=StrategyEnum.S1,
        )
        session.add(agent)
        session.commit()
        session.refresh(agent)
        return AccountingService(session).create_account(
            agent.id, Decimal("1000")
        ).id


@pytest.mark.asyncio
async def test_operator_market_order_fetches_real_quote_and_persists_virtual_fill(app_db):
    account_id = _account_id(app_db)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/paper/orders/market",
            params={
                "account_id": account_id,
                "symbol": "BTC-USDT",
                "side": "BUY",
                "quantity": "1",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["evidence_mode"] == "paper"
    assert payload["origin"] == "operator"
    assert payload["provider"] == "fixture_real"
    assert payload["symbol"] == "BTC/USDT"
    assert payload["market_price"] == "100"
    assert payload["policy_version"] == "paper-v1"

    with Session(app_db) as session:
        assert len(session.exec(select(PaperExecution)).all()) == 1
        assert len(session.exec(select(Fill)).all()) == 1
        assert session.exec(select(Position)).one().quantity == Decimal("1")


@pytest.mark.asyncio
async def test_provider_failure_returns_503_and_creates_no_financial_state(app_db):
    account_id = _account_id(app_db)
    app.dependency_overrides[get_market_data_service] = lambda: UnavailableMarketData()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/paper/orders/market",
            params={
                "account_id": account_id,
                "symbol": "BTC-USDT",
                "side": "BUY",
                "quantity": "1",
            },
        )

    assert response.status_code == 503
    with Session(app_db) as session:
        assert session.exec(select(PaperExecution)).all() == []
        assert session.exec(select(Fill)).all() == []


@pytest.mark.asyncio
async def test_paper_api_is_operator_only_and_has_no_live_execution_surface(app_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        status = await client.get("/api/paper/status")

    assert status.status_code == 200
    assert status.json() == {
        "mode": "paper",
        "market_data": "real_only",
        "capital": "virtual_only",
        "order_type": "market_only",
        "origin": "operator_only_until_risk",
        "live_execution_capability": False,
        "synthetic_fallback": False,
        "policy_version": "paper-v1",
        "slippage_bps": "10",
        "fee_bps": "10",
    }

    routes = {route.path for route in app.routes}
    assert "/api/paper/orders/market" in routes
    assert "/api/paper/executions" in routes
    assert "/api/paper/live" not in routes
    assert "/api/paper/automation/start" not in routes
