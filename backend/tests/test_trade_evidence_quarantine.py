import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.database import get_session
from app.main import app
from app.models import Agent, Trade, TradeType


@pytest.fixture
def sqlite_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def override_session(sqlite_engine):
    def _get_test_session():
        with Session(sqlite_engine) as session:
            yield session

    app.dependency_overrides[get_session] = _get_test_session
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_legacy_trades_are_preserved_but_not_valid_financial_evidence(sqlite_engine):
    with Session(sqlite_engine) as session:
        agent = Agent(
            nombre="LEGACY",
            presupuesto_inicial=1000,
            presupuesto_actual=1010,
        )
        session.add(agent)
        session.commit()
        session.refresh(agent)
        session.add(
            Trade(
                agente_id=agent.id,
                precio_entrada=100,
                precio_salida=110,
                cantidad=1,
                tipo=TradeType.LONG,
                resultado=10,
            )
        )
        session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        listed = await client.get("/api/trades/")
        stats = await client.get("/api/trades/stats")

    assert listed.status_code == 200
    assert listed.json()[0]["evidence_mode"] == "legacy_unclassified"
    assert listed.json()[0]["evidence_valid"] is False

    assert stats.status_code == 200
    payload = stats.json()
    assert payload["legacy_records"] == 1
    assert payload["legacy_closed_records"] == 1
    assert payload["evidence_valid"] is False
    assert payload["profit_total"] is None
    assert payload["win_rate_percent"] is None
