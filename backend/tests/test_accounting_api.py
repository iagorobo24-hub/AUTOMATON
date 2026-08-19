import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.database import get_session
from app.main import app


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


@pytest.fixture(autouse=True)
def override_session(engine):
    def _session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _session
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_accounting_account_endpoint_exposes_authoritative_cash_and_ledger():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/agents/",
            params={"nombre": "A1", "estrategia": "S1", "presupuesto": 500},
        )
        agent_id = created.json()["id"]
        await client.post(f"/api/agents/{agent_id}/deposit", params={"amount": 50})

        response = await client.get(f"/api/accounting/agents/{agent_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["account"]["currency"] == "USDT"
    assert payload["account"]["initial_capital"] == "500.00000000"
    assert payload["account"]["funded_capital"] == "550.00000000"
    assert payload["account"]["cash"] == "550.00000000"
    assert payload["account"]["realized_pnl"] == "0E-8"
    assert payload["positions"] == []
    assert [entry["entry_type"] for entry in payload["ledger"]] == [
        "INITIAL_FUNDING",
        "DEPOSIT",
    ]


@pytest.mark.asyncio
async def test_accounting_api_does_not_offer_fill_or_order_mutation_routes():
    routes = {route.path for route in app.routes}

    assert "/api/accounting/agents/{agent_id}" in routes
    assert "/api/accounting/orders" not in routes
    assert "/api/accounting/fills" not in routes
    assert "/api/accounting/execute" not in routes
