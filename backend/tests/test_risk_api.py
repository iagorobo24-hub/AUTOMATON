from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.database import get_session
from app.main import app
from app.models.risk import RiskProfile
from app.risk.bootstrap import ensure_active_risk_profile


@pytest.fixture
def setup_app():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def _get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _get_session
    with Session(engine) as session:
        ensure_active_risk_profile(session)
    yield engine
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)


@pytest.mark.asyncio
async def test_risk_status_and_active_profile_are_exposed(setup_app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        status = await client.get("/api/risk/status")
        profile = await client.get("/api/risk/profiles/active")
    assert status.status_code == 200
    assert status.json()["mode"] == "authoritative_phase_4"
    assert status.json()["profile_version"] == "risk-v1"
    assert status.json()["paper_gate_required"] is True
    assert status.json()["automated_trading"] is False
    assert profile.status_code == 200
    assert profile.json()["max_order_notional"] == "250.00000000"


@pytest.mark.asyncio
async def test_pause_and_resume_toggle_global_circuit_breaker(setup_app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        paused = await client.post("/api/risk/pause")
        resumed = await client.post("/api/risk/resume")
    assert paused.status_code == 200
    assert paused.json()["paused"] is True
    assert resumed.status_code == 200
    assert resumed.json()["paused"] is False
    with Session(setup_app) as session:
        profile = session.exec(select(RiskProfile).where(RiskProfile.active == True)).one()
        assert profile.paused is False
