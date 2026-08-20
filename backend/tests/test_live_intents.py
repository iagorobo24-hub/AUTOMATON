from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.live_execution.adapter import AdapterCapabilities, SymbolRules
from app.live_execution.policy import bootstrap_live_policy
from app.live_execution.service import LiveReadinessService
from app.models import LiveReconciliation


class ReadOnlyAdapter:
    def capabilities(self):
        return AdapterCapabilities("test", False, False, False, False)
    def get_symbol_rules(self, symbol):
        return SymbolRules(symbol, Decimal("0.001"), Decimal("0.10"), Decimal("10"))
    def get_balances(self): return {}
    def get_open_orders(self): return []
    def lookup_order(self, client_order_id): return None
    def get_positions(self): return []
    def get_fills(self): return []


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _prepare(service):
    return service.prepare_intent(
        candidate_id=1, source_event_id="cycle-1", symbol="BTC/USDT", side="BUY",
        quantity=Decimal("0.001"), reference_price=Decimal("10000"),
        projected_symbol_exposure=Decimal("10"), projected_portfolio_exposure=Decimal("10"),
        deployable_capital=Decimal("10"),
    )


def test_prepare_intent_is_idempotent_and_never_transmitted():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_live_policy(session)
        service = LiveReadinessService(session, ReadOnlyAdapter())
        first = _prepare(service); second = _prepare(service)
        assert first.id == second.id
        assert first.client_order_id.startswith("live:")
        assert first.status == "PREPARED"


def test_emergency_stop_blocks_new_intents_and_clear_requires_clean_recovery():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_live_policy(session)
        service = LiveReadinessService(session, ReadOnlyAdapter())
        service.activate_emergency_stop("operator test")
        blocked = _prepare(service)
        assert blocked.status == "BLOCKED"
        assert blocked.reason_code == "EMERGENCY_STOP_ACTIVE"
        session.add(LiveReconciliation(status="RECOVERY_REQUIRED", reason_code="TEST", details="uncertain")); session.commit()
        with pytest.raises(ValueError, match="recovery is unresolved"):
            service.clear_emergency_stop("reviewed")
