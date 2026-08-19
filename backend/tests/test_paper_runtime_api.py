import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.accounting.service import AccountingService
from app.database import get_session
from app.main import app
from app.models import Agent, AgentStatus, StrategyEnum
from app.paper_runtime.scheduler import get_runtime_scheduler


class FakeScheduler:
    def __init__(self): self.spawned = []; self.cancelled = []
    def spawn(self, session_id): self.spawned.append(session_id)
    def cancel(self, session_id): self.cancelled.append(session_id)


@pytest.mark.asyncio
async def test_runtime_api_creates_and_controls_virtual_only_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent = Agent(nombre="api-runtime", presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=StrategyEnum.S1, estado=AgentStatus.ACTIVO)
        session.add(agent); session.commit(); session.refresh(agent)
        AccountingService(session).create_account(agent.id, 1000)
        agent_id = agent.id

    def override_session():
        with Session(engine) as session: yield session
    scheduler = FakeScheduler()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_runtime_scheduler] = lambda: scheduler
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            status = await client.get("/api/runtime/status")
            assert status.status_code == 200
            assert status.json()["capital"] == "virtual_only"
            assert status.json()["live_execution_capability"] is False
            assert status.json()["auto_replication"] is False

            created = await client.post("/api/runtime/sessions", params={
                "name": "continuous", "symbol": "BTC/USDT", "interval": "1m", "agent_ids": agent_id,
            })
            assert created.status_code == 200
            session_id = created.json()["id"]

            started = await client.post(f"/api/runtime/sessions/{session_id}/start")
            assert started.status_code == 200
            assert started.json()["status"] == "RUNNING"
            assert scheduler.spawned == [session_id]

            paused = await client.post(f"/api/runtime/sessions/{session_id}/pause")
            assert paused.status_code == 200
            assert paused.json()["status"] == "PAUSED"
            assert scheduler.cancelled == [session_id]

            resumed = await client.post(f"/api/runtime/sessions/{session_id}/resume")
            assert resumed.status_code == 200
            assert resumed.json()["status"] == "RUNNING"
            stopped = await client.post(f"/api/runtime/sessions/{session_id}/stop")
            assert stopped.status_code == 200
            assert stopped.json()["status"] == "STOPPED"
    finally:
        app.dependency_overrides.clear()
