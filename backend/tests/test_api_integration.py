"""API integration tests"""
import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.integration
class TestAPI:
    @pytest.mark.asyncio
    async def test_health_endpoint_reports_phase_10_readiness_contract(self):
        from app.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["runtime_mode"] == "transition"
        assert data["synthetic_engine"] == "disabled"
        assert data["market_data"] == "real_contract_available"
        assert data["accounting"] == "authoritative_phase_2"
        assert data["risk"] == "authoritative_phase_4"
        assert data["paper_trading"] == "autonomous_phase_7"
        assert data["backtesting"] == "evidence_phase_5"
        assert data["agent_evolution"] == "evidence_phase_6"
        assert data["paper_runtime"] == "runtime_phase_7"
        assert data["strategy_research"] == "evidence_phase_8"
        assert data["legacy_pruning"] == "pruned_phase_9"
        assert data["automated_trading"] == "paper_enabled_phase_7"
        assert data["live_execution"] == "readiness_phase_10"
        assert data["real_capital_execution"] == "disabled"

    @pytest.mark.asyncio
    async def test_runtime_state_does_not_publish_synthetic_or_live_execution_metrics(self):
        from app.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/estado")
        assert response.status_code == 200
        payload = response.json()
        assert payload["market_data_mode"] == "real_contract_available"
        assert payload["accounting_mode"] == "authoritative_phase_2"
        assert payload["risk_mode"] == "authoritative_phase_4"
        assert payload["live_execution"] == "readiness_phase_10"
        assert payload["real_capital_execution"] == "disabled"
        assert "precios_actuales" not in payload
        assert "profit_total" not in payload

    def test_active_api_routes_include_live_readiness_but_no_live_order_activation(self):
        from app.main import app
        routes = {route.path for route in app.routes}
        for path in (
            "/api/market-data/status", "/api/risk/status", "/api/paper/status", "/api/backtests/status",
            "/api/evolution/status", "/api/runtime/status", "/api/research/status", "/api/live/status",
            "/api/live/policy", "/api/live/readiness", "/api/live/readiness/evaluate",
            "/api/live/emergency-stop", "/api/live/emergency-stop/clear", "/api/live/reconciliations",
            "/api/live/reconciliations/{reconciliation_id}/resolve",
        ):
            assert path in routes
        for forbidden in (
            "/api/paper/live", "/api/backtests/optimize", "/api/research/optimize", "/api/research/mutate",
            "/api/research/live", "/api/live/orders", "/api/live/activate", "/api/live/credentials",
            "/api/evolution/automation/start", "/api/evolution/automation/replicate",
        ):
            assert forbidden not in routes

    def test_legacy_system_and_trading_routers_stay_out_of_sqlmodel_runtime(self):
        from app.main import app
        routes = {route.path for route in app.routes}
        for path in (
            "/api/system/mode", "/api/system/reset-agents", "/api/trading/engine/status", "/api/trading/engine/start",
            "/api/trading/mode", "/api/simulation/status", "/api/auth/token", "/api/payments/create-session", "/ws/trading",
        ):
            assert path not in routes

    def test_cors_middleware_is_configured(self):
        from app.main import app
        assert app.user_middleware
