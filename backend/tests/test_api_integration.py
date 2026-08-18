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
    async def test_health_endpoint(self):
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200

    def test_active_api_routes_are_registered(self):
        from app.main import app

        routes = {route.path for route in app.routes}

        assert "/api/agents/" in routes
        assert "/api/agents/{agent_id}/replicate" in routes
        assert "/api/agents/{agent_id}/deposit" in routes
        assert "/api/agents/{agent_id}/simulate-trade" in routes
        assert "/api/agents/crear" not in routes
        assert "/api/trades/" in routes
        assert "/api/crypto/top-coins" in routes
        assert "/api/crypto/trending" in routes

    def test_cors_middleware_is_configured(self):
        from app.main import app

        assert app.user_middleware
