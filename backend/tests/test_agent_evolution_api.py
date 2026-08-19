import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.database import get_session
from app.main import app
from app.models import AgentLifecycleEvent


@pytest.fixture
def app_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _session
    yield engine
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)


@pytest.mark.asyncio
async def test_evolution_status_exposes_evidence_gate_without_auto_or_live_capability(app_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/evolution/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "evidence_phase_6"
    assert payload["policy_version"] == "evolution-v1"
    assert payload["replication"] == "evidence_gated_manual"
    assert payload["strategy_mutation"] == "disabled"
    assert payload["automated_trading"] == "disabled"
    assert payload["live_execution"] == "disabled"


@pytest.mark.asyncio
async def test_agent_creation_and_kill_persist_explicit_lifecycle_reasons(app_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post("/api/agents/", params={"nombre": "lifecycle", "estrategia": "S1", "presupuesto": 1000})
        assert created.status_code == 200
        agent_id = created.json()["id"]
        killed = await client.delete(f"/api/agents/{agent_id}", params={"reason": "operator_experiment_complete"})
        assert killed.status_code == 200

    with Session(app_db) as session:
        events = session.exec(select(AgentLifecycleEvent).where(AgentLifecycleEvent.agent_id == agent_id).order_by(AgentLifecycleEvent.id)).all()
        assert [(event.event_type, event.reason) for event in events] == [
            ("CREATED", "operator_creation"),
            ("KILLED", "operator_experiment_complete"),
        ]


@pytest.mark.asyncio
async def test_fitness_endpoint_persists_reject_when_evidence_is_missing_and_lineage_is_empty(app_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post("/api/agents/", params={"nombre": "candidate", "estrategia": "S1", "presupuesto": 1000})
        agent_id = created.json()["id"]

        evaluation = await client.post(f"/api/evolution/agents/{agent_id}/fitness")
        assert evaluation.status_code == 200
        assert evaluation.json()["decision"] == "REJECT"
        assert "BACKTEST_EVIDENCE_MISSING" in evaluation.json()["reason_codes"]

        history = await client.get(f"/api/evolution/agents/{agent_id}/fitness")
        assert history.status_code == 200
        assert len(history.json()) == 1

        lineage = await client.get(f"/api/evolution/agents/{agent_id}/lineage")
        assert lineage.status_code == 200
        assert lineage.json() == {"as_parent": [], "as_child": None}
