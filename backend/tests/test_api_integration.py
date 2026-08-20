"""API integration tests"""
import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.integration
class TestAPI:
    @pytest.mark.asyncio
    async def test_health_endpoint_reports_phase_9_pruned_runtime_contract(self):
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
            "paper_trading": "autonomous_phase_7",
            "backtesting": "evidence_phase_5",
            "agent_evolution": "evidence_phase_6",
            "paper_runtime": "runtime_phase_7",
            "strategy_research": "evidence_phase_8",
            "legacy_pruning": "pruned_phase_9",
            "automated_trading": "paper_enabled_phase_7",
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
        assert payload["paper_trading"] == "autonomous_phase_7"
        assert payload["backtesting"] == "evidence_phase_5"
        assert payload["agent_evolution"] == "evidence_phase_6"
        assert payload["paper_runtime"] == "runtime_phase_7"
        assert payload["strategy_research"] == "evidence_phase_8"
        assert payload["legacy_pruning"] == "pruned_phase_9"
        assert payload["automated_trading"] == "paper_enabled_phase_7"
        assert payload["live_execution"] == "disabled"
        assert "precios_actuales" not in payload
        assert "profit_total" not in payload

    def test_active_api_routes_include_research_but_not_legacy_optimizer_mutation_or_live(self):
        from app.main import app

        routes = {route.path for route in app.routes}
        assert "/api/agents/" in routes
        assert "/api/agents/{agent_id}/deposit" in routes
        assert "/api/agents/{agent_id}/replicate" in routes
        assert "/api/agents/{agent_id}/simulate-trade" not in routes
        assert "/api/market-data/status" in routes
        assert "/api/accounting/agents/{agent_id}" in routes
        assert "/api/risk/status" in routes
        assert "/api/paper/status" in routes
        assert "/api/paper/orders/market" in routes
        assert "/api/paper/executions" in routes
        assert "/api/backtests/status" in routes
        assert "/api/evolution/status" in routes
        assert "/api/runtime/status" in routes
        assert "/api/runtime/sessions" in routes
        assert "/api/research/status" in routes
        assert "/api/research/policies/active" in routes
        assert "/api/research/studies" in routes
        assert "/api/research/studies/{study_id}/windows" in routes
        assert "/api/research/studies/{study_id}/evaluate" in routes
        assert "/api/research/studies/{study_id}/promote" in routes
        assert "/api/research/candidates" in routes
        assert "/api/paper/live" not in routes
        assert "/api/backtests/optimize" not in routes
        assert "/api/research/optimize" not in routes
        assert "/api/research/mutate" not in routes
        assert "/api/research/live" not in routes
        assert "/api/evolution/automation/start" not in routes
        assert "/api/evolution/automation/replicate" not in routes
        assert "/api/estado" in routes

    def test_legacy_system_and_trading_routers_stay_out_of_sqlmodel_runtime(self):
        from app.main import app

        routes = {route.path for route in app.routes}
        assert "/api/system/mode" not in routes
        assert "/api/system/reset-agents" not in routes
        assert "/api/trading/engine/status" not in routes
        assert "/api/trading/engine/start" not in routes
        assert "/api/trading/mode" not in routes
        assert "/api/simulation/status" not in routes
        assert "/api/auth/token" not in routes
        assert "/api/payments/create-session" not in routes
        assert "/ws/trading" not in routes

    def test_cors_middleware_is_configured(self):
        from app.main import app
        assert app.user_middleware
