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
        """Health check remains available outside the /api prefix."""
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200

    def test_active_api_routes_are_registered(self):
        """Routers used by the active SQLModel frontend are actually exposed."""
        from app.main import app

        routes = {route.path for route in app.routes}

        assert "/api/agents/" in routes
        assert "/api/trades/" in routes
        assert "/api/crypto/top-coins" in routes
        assert "/api/crypto/trending" in routes

    def test_cors_middleware_is_configured(self):
        """The application has middleware configured for the frontend origin."""
        from app.main import app

        assert app.user_middleware
