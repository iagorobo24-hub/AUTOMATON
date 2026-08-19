"""API integration tests"""
import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.integration
class TestAPI:
    """API endpoint tests"""

    @pytest.mark.asyncio
    async def test_health_endpoint_reports_synthetic_isolation(self):
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "runtime_mode": "transition",
            "synthetic_engine": "disabled",
            "paper_trading": "not_implemented",
        }

    @pytest.mark.asyncio
    async def test_runtime_state_does_not_publish_synthetic_financial_metrics(self):
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/estado")

        assert response.status_code == 200
        payload = response.json()
        assert payload["runtime_mode"] == "transition"
        assert payload["synthetic_engine"] == "disabled"
        assert payload["financial_evidence"] == "unavailable"
        assert "precios_actuales" not in payload
        assert "profit_total" not in payload

    def test_active_api_routes_are_registered_without_manual_pnl_mutation(self):
        from app.main import app

        routes = {route.path for route in app.routes}

        assert "/api/agents/" in routes
        assert "/api/agents/{agent_id}/replicate" in routes
        assert "/api/agents/{agent_id}/deposit" in routes
        assert "/api/agents/{agent_id}/simulate-trade" not in routes
        assert "/api/agents/crear" not in routes
        assert "/api/trades/" in routes
        assert "/api/trades/stats" in routes
        assert "/api/crypto/top-coins" in routes
        assert "/api/crypto/trending" in routes
        assert "/api/estado" in routes

    def test_legacy_system_and_trading_routers_stay_out_of_sqlmodel_runtime(self):
        from app.main import app

        routes = {route.path for route in app.routes}

        assert "/api/system/mode" not in routes
        assert "/api/system/reset-agents" not in routes
        assert "/api/trading/engine/status" not in routes
        assert "/api/trading/engine/start" not in routes
        assert "/api/trading/mode" not in routes
        assert "/ws/trading" not in routes

    def test_cors_middleware_is_configured(self):
        from app.main import app

        assert app.user_middleware
