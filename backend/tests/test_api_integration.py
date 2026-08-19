"""API integration tests"""
import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.integration
class TestAPI:
    @pytest.mark.asyncio
    async def test_health_endpoint_reports_phase_6_evolution_contract(self):
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "runtime_mode": "transition",
            "synthetic_engine": "disabled",
            "market_data": "real_contract_available",
            "accounting": "authoritative_phase_2",
            "risk": "authoritative_phase_4",
            "paper_trading": "operator_only_phase_4",
            "backtesting": "evidence_phase_5",
            "agent_evolution": "evidence_phase_6",
            "automated_trading": "blocked_until_phase_7_runtime",
            "live_execution": "disabled",
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
        assert payload["market_data_mode"] == "real_contract_available"
        assert payload["accounting_mode"] == "authoritative_phase_2"
        assert payload["risk_mode"] == "authoritative_phase_4"
        assert payload["paper_trading"] == "operator_only_phase_4"
        assert payload["backtesting"] == "evidence_phase_5"
        assert payload["agent_evolution"] == "evidence_phase_6"
        assert payload["automated_trading"] == "blocked_until_phase_7_runtime"
        assert payload["live_execution"] == "disabled"
        assert "precios_actuales" not in payload
        assert "profit_total" not in payload

    def test_active_api_routes_include_evolution_backtesting_and_risk_gated_paper_but_not_live_or_automation(self):
        from app.main import app

        routes = {route.path for route in app.routes}
        assert "/api/agents/" in routes
        assert "/api/agents/{agent_id}/deposit" in routes
        assert "/api/agents/{agent_id}/replicate" in routes
        assert "/api/agents/{agent_id}/simulate-trade" not in routes
        assert "/api/market-data/status" in routes
        assert "/api/accounting/agents/{agent_id}" in routes
        assert "/api/risk/status" in routes
        assert "/api/risk/profiles/active" in routes
        assert "/api/risk/decisions" in routes
        assert "/api/risk/pause" in routes
        assert "/api/risk/resume" in routes
        assert "/api/paper/status" in routes
        assert "/api/paper/orders/market" in routes
        assert "/api/paper/executions" in routes
        assert "/api/backtests/status" in routes
        assert "/api/backtests/datasets" in routes
        assert "/api/backtests/datasets/{dataset_id}" in routes
        assert "/api/backtests/runs" in routes
        assert "/api/backtests/runs/{run_id}" in routes
        assert "/api/evolution/status" in routes
        assert "/api/evolution/policies/active" in routes
        assert "/api/evolution/agents/{agent_id}/fitness" in routes
        assert "/api/evolution/agents/{agent_id}/lineage" in routes
        assert "/api/paper/automation/start" not in routes
        assert "/api/paper/live" not in routes
        assert "/api/backtests/optimize" not in routes
        assert "/api/evolution/automation/start" not in routes
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
