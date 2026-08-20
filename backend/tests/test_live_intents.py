from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.backtesting.runner import strategy_source_sha256
from app.live_execution.adapter import AdapterCapabilities, SymbolRules
from app.live_execution.policy import bootstrap_live_policy
from app.live_execution.service import LiveReadinessService
from app.models import LiveReadinessEvaluation, LiveReconciliation, StrategyCandidate


class ReadOnlyAdapter:
    def capabilities(self): return AdapterCapabilities("test", False, False, False, False)
    def get_symbol_rules(self, symbol): return SymbolRules(symbol, Decimal("0.001"), Decimal("0.10"), Decimal("10"))
    def get_balances(self): return {}
    def get_open_orders(self): return []
    def lookup_order(self, client_order_id): return None
    def get_positions(self): return []
    def get_fills(self): return []


def _engine(): return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _seed_ready_candidate(session):
    candidate = StrategyCandidate(
        study_id=1, evaluation_id=1, strategy_id="S1", strategy_version="baseline-v1",
        strategy_source_sha256=strategy_source_sha256(), status="PROMOTED",
    )
    session.add(candidate); session.commit(); session.refresh(candidate)
    session.add(LiveReadinessEvaluation(
        candidate_id=candidate.id, policy_version="live-v1", architecture_ready=True,
        real_capital_blocked=True, decision="ARCHITECTURE_READY", reason_codes="", reason="test",
        strategy_source_sha256=candidate.strategy_source_sha256,
    )); session.commit()
    return candidate


def _prepare(service, candidate_id, source_event_id="cycle-1", quantity=Decimal("0.001"), side="BUY"):
    return service.prepare_intent(
        candidate_id=candidate_id, source_event_id=source_event_id, symbol="BTC/USDT", side=side,
        quantity=quantity, reference_price=Decimal("10000"),
        projected_symbol_exposure=Decimal("10"), projected_portfolio_exposure=Decimal("10"), deployable_capital=Decimal("10"),
    )


def test_prepare_intent_is_idempotent_only_for_identical_payload():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_live_policy(session); candidate = _seed_ready_candidate(session)
        service = LiveReadinessService(session, ReadOnlyAdapter())
        first = _prepare(service, candidate.id); second = _prepare(service, candidate.id)
        assert first.id == second.id
        assert first.client_order_id.startswith("live:")
        assert len(first.intent_fingerprint) == 64
        assert first.status == "PREPARED"


def test_same_client_id_with_different_payload_fails_closed():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_live_policy(session); candidate = _seed_ready_candidate(session)
        service = LiveReadinessService(session, ReadOnlyAdapter())
        _prepare(service, candidate.id, source_event_id="same-event", quantity=Decimal("0.001"))
        with pytest.raises(ValueError, match="idempotency conflict"):
            _prepare(service, candidate.id, source_event_id="same-event", quantity=Decimal("0.002"))


def test_prepare_intent_rejects_invalid_identity_fields():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_live_policy(session); candidate = _seed_ready_candidate(session)
        service = LiveReadinessService(session, ReadOnlyAdapter())
        with pytest.raises(ValueError, match="source_event_id"):
            _prepare(service, candidate.id, source_event_id="   ")
        with pytest.raises(ValueError, match="BUY or SELL"):
            _prepare(service, candidate.id, source_event_id="bad-side", side="HOLD")


def test_prepare_intent_rejects_candidate_without_architecture_ready_evidence():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_live_policy(session)
        candidate = StrategyCandidate(study_id=1, evaluation_id=1, strategy_id="S1", strategy_version="baseline-v1", strategy_source_sha256=strategy_source_sha256(), status="PROMOTED")
        session.add(candidate); session.commit(); session.refresh(candidate)
        with pytest.raises(ValueError, match="ARCHITECTURE_READY"):
            _prepare(LiveReadinessService(session, ReadOnlyAdapter()), candidate.id)


def test_emergency_stop_blocks_new_intents_and_clear_requires_clean_recovery():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_live_policy(session); candidate = _seed_ready_candidate(session)
        service = LiveReadinessService(session, ReadOnlyAdapter())
        service.activate_emergency_stop("operator test")
        blocked = _prepare(service, candidate.id, "cycle-2")
        assert blocked.status == "BLOCKED"
        assert blocked.reason_code == "EMERGENCY_STOP_ACTIVE"
        rec = LiveReconciliation(status="RECOVERY_REQUIRED", reason_code="TEST", details="uncertain")
        session.add(rec); session.commit(); session.refresh(rec)
        with pytest.raises(ValueError, match="recovery is unresolved"):
            service.clear_emergency_stop("reviewed")
        service.resolve_reconciliation(rec.id, "operator reconciled external evidence")
        cleared = service.clear_emergency_stop("recovery resolved")
        assert cleared.active is False
