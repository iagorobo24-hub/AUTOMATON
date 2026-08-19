import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.database import get_session
from app.main import app
from app.models import Agent, AgentStatus, StrategyEnum, Trade, TradeType
from app.services.agent_engine import AgentEngine


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
async def test_agents_active_contract_end_to_end(sqlite_engine):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/agents/",
            params={
                "nombre": "ADAN",
                "estrategia": "S1",
                "presupuesto": 1000,
                "umbral": 0.15,
            },
        )
        assert created.status_code == 200
        agent_id = created.json()["id"]

        listed = await client.get("/api/agents/")
        assert listed.status_code == 200
        assert listed.json()[0]["nombre"] == "ADAN"
        assert listed.json()[0]["estado"] == "ACTIVO"
        assert listed.json()[0]["trades_count"] is None
        assert listed.json()[0]["successful_trades"] is None
        assert listed.json()[0]["performance_evidence_valid"] is False

        deposited = await client.post(
            f"/api/agents/{agent_id}/deposit", params={"amount": 100}
        )
        assert deposited.status_code == 200
        assert deposited.json()["presupuesto_inicial"] == 1100
        assert deposited.json()["presupuesto_actual"] == 1100
        assert deposited.json()["profit"] is None

        simulated = await client.post(
            f"/api/agents/{agent_id}/simulate-trade", params={"profit": -10}
        )
        assert simulated.status_code == 404

        replicated = await client.post(f"/api/agents/{agent_id}/replicate")
        assert replicated.status_code == 200
        payload = replicated.json()
        assert payload["parent"]["estado"] == "REPLICADO"
        assert payload["replica"]["estado"] == "ACTIVO"
        assert payload["replica"]["padre_id"] == agent_id

        blocked = await client.post(
            f"/api/agents/{agent_id}/deposit", params={"amount": 100}
        )
        assert blocked.status_code == 409

        child_id = payload["replica"]["id"]
        killed = await client.delete(f"/api/agents/{child_id}")
        assert killed.status_code == 200
        assert killed.json()["estado"] == "MUERTO"
        assert killed.json()["presupuesto_actual"] == 0

        killed_again = await client.delete(f"/api/agents/{child_id}")
        assert killed_again.status_code == 409


@pytest.mark.asyncio
async def test_agents_reject_invalid_creation_values():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        whitespace_name = await client.post(
            "/api/agents/",
            params={"nombre": "   ", "estrategia": "S1", "presupuesto": 100},
        )
        assert whitespace_name.status_code == 422

        invalid_budget = await client.post(
            "/api/agents/",
            params={"nombre": "BAD", "estrategia": "S1", "presupuesto": 0},
        )
        assert invalid_budget.status_code == 422

        invalid_threshold = await client.post(
            "/api/agents/",
            params={
                "nombre": "BAD",
                "estrategia": "S1",
                "presupuesto": 100,
                "umbral": 1.5,
            },
        )
        assert invalid_threshold.status_code == 422


@pytest.mark.asyncio
async def test_agent_engine_remains_available_only_as_explicit_synthetic_test_utility(sqlite_engine, monkeypatch):
    class SellStrategy:
        def calcular_señal(self, _prices):
            return "SELL"

    monkeypatch.setattr(
        "app.services.agent_engine.get_strategy", lambda _strategy: SellStrategy()
    )

    with Session(sqlite_engine) as session:
        agent = Agent(
            nombre="TRADER",
            presupuesto_inicial=1000,
            presupuesto_actual=900,
            estrategia=StrategyEnum.S1,
            estado=AgentStatus.ACTIVO,
            umbral_replica=0.15,
        )
        session.add(agent)
        session.commit()
        session.refresh(agent)

        trade = Trade(
            agente_id=agent.id,
            precio_entrada=100,
            cantidad=1,
            tipo=TradeType.LONG,
        )
        session.add(trade)
        session.commit()

        engine = AgentEngine()
        engine.historial_precios["BTC"][-1] = 110
        await engine._procesar_agente(session, agent)
        session.commit()
        session.refresh(agent)

        assert agent.presupuesto_actual == pytest.approx(1010)
        closed_trade = session.exec(select(Trade).where(Trade.id == trade.id)).one()
        assert closed_trade.resultado == pytest.approx(10)


@pytest.mark.asyncio
async def test_agents_list_quarantines_pre_provenance_trade_counters(sqlite_engine):
    with Session(sqlite_engine) as session:
        agent = Agent(
            nombre="COUNTER",
            presupuesto_inicial=1000,
            presupuesto_actual=1000,
            estrategia=StrategyEnum.S1,
        )
        session.add(agent)
        session.commit()
        session.refresh(agent)
        session.add(Trade(agente_id=agent.id, precio_entrada=100, precio_salida=110, cantidad=1, tipo=TradeType.LONG, resultado=10))
        session.add(Trade(agente_id=agent.id, precio_entrada=100, precio_salida=90, cantidad=1, tipo=TradeType.LONG, resultado=-10))
        session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/agents/")

    assert response.status_code == 200
    payload = response.json()[0]
    assert payload["legacy_trades_count"] == 2
    assert payload["trades_count"] is None
    assert payload["successful_trades"] is None
    assert payload["performance_evidence_valid"] is False
    assert payload["evidence_mode"] == "legacy_unclassified"
