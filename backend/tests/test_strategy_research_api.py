import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_research_status_declares_manual_evidence_research_without_optimizer_or_live():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/research/status")
    assert response.status_code == 200
    assert response.json() == {
        "mode": "strategy_research",
        "policy_version": "research-v1",
        "historical_methodology": "chronological_train_validation_oos_walk_forward",
        "forward_evidence": "phase_7_paper_required",
        "promotion": "manual_evidence_gated",
        "optimizer": False,
        "strategy_mutation": False,
        "live_execution_capability": False,
    }


def test_research_routes_exist_without_optimizer_mutation_or_live_surface():
    routes = {route.path for route in app.routes}
    expected = {
        "/api/research/status",
        "/api/research/policies/active",
        "/api/research/studies",
        "/api/research/studies/{study_id}",
        "/api/research/studies/{study_id}/windows",
        "/api/research/studies/{study_id}/evaluate",
        "/api/research/studies/{study_id}/evaluations",
        "/api/research/studies/{study_id}/promote",
        "/api/research/candidates",
    }
    assert expected <= routes
    assert "/api/research/optimize" not in routes
    assert "/api/research/mutate" not in routes
    assert "/api/research/live" not in routes
