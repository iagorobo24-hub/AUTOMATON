from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.backtesting.runner import strategy_source_sha256
from app.live_execution.adapter import AdapterCapabilities, SymbolRules
from app.live_execution.policy import bootstrap_live_policy, ensure_emergency_stop_baseline
from app.live_execution.service import LiveReadinessService
from app.models import LiveReconciliation, RiskProfile, StrategyCandidate

REAL_MARKET = {"provider": "test", "evidence_mode": "real", "synthetic_fallback": False, "execution_capability": False}


class ReadOnlyAdapter:
    def capabilities(self): return AdapterCapabilities("test", False, False, False, False)
    def get_symbol_rules(self, symbol): return SymbolRules(symbol, Decimal("0.001"), Decimal("0.10"), Decimal("10"))
    def get_balances(self): return {}
    def get_open_orders(self): return []
    def lookup_order(self, client_order_id): return None
    def get_positions(self): return []
    def get_fills(self): return []


def _engine(): return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _risk():
    return RiskProfile(
        name="Risk", version="risk-v1", active=True, paused=False,
        max_order_notional=Decimal("100"), max_order_equity_pct=Decimal("0.25"),
        max_total_exposure_pct=Decimal("0.80"), max_symbol_exposure_pct=Decimal("0.40"),
        max_open_positions=4, max_realized_loss_pct=Decimal("0.10"), max_drawdown_pct=Decimal("0.15"), max_quote_age_seconds=30,
    )


def _seed_candidate_and_gates(session):
    bootstrap_live_policy(session); ensure_emergency_stop_baseline(session)
    session.add(_risk())
    session.add(LiveReconciliation(status="CLEAN", reason_code="MATCHED_READ_ONLY_STATE", details=""))
    candidate = StrategyCandidate(
        study_id=1, evaluation_id=1, strategy_id="S1", strategy_version="baseline-v1",
        strategy_source_sha256=strategy_source_sha256(), status="PROMOTED",
    )
    session.add(candidate); session.commit(); session.refresh(candidate)
    return candidate


def _service(session): return LiveReadinessService(session, ReadOnlyAdapter(), REAL_MARKET)


def _prepare(service, candidate_id, source_event_id="cycle-1", quantity=Decimal("0.001"), side="BUY"):
    return service.prepare_intent(
        candidate_id=candidate_id, source_event_id=source_event_id, symbol="BTC/USDT", side=side,
        quantity=quantity, reference_price=Decimal("10000"),
        projected_symbol_exposure=Decimal("10"), projected_portfolio_exposure=Decimal("10"), deployable_capital=Decimal("10"),
    )


def test_prepare_intent_is_idempotent_only_for_identical_payload():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        candidate = _seed_candidate_and_gates(session); service = _service(session)
        first = _prepare(service, candidate.id); second = _prepare(service, candidate.id)
        assert first.id == second.id
        assert first.client_order_id.startswith("live:")
        assert len(first.intent_fingerprint) == 64
        assert first.status == "PREPARED"


def test_same_client_id_with_different_payload_fails_closed():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        candidate = _seed_candidate_and_gates(session); service = _service(session)
        _prepare(service, candidate.id, source_event_id="same-event", quantity=Decimal("0.001"))
        with pytest.raises(ValueError, match="idempotency conflict"):
            _prepare(service, candidate.id, source_event_id="same-event", quantity=Decimal("0.002"))


def test_prepare_intent_rejects_invalid_identity_fields():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        candidate = _seed_candidate_and_gates(session); service = _service(session)
        with pytest.raises(ValueError, match="source_event_id"):
            _prepare(service, candidate.id, source_event_id="   ")
        with pytest.raises(ValueError, match="BUY or SELL"):
            _prepare(service, candidate.id, source_event_id="bad-side", side="HOLD")


def test_prepare_intent_re_evaluates_and_rejects_stale_ready_state():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        candidate = _seed_candidate_and_gates(session); service = _service(session)
        _prepare(service, candidate.id, source_event_id="first")
        risk = session.query(RiskProfile).filter(RiskProfile.active == True).first()  # noqa: E712
        risk.paused = True; session.add(risk); session.commit()
        with pytest.raises(ValueError, match="RISK_PAUSED"):
            _prepare(service, candidate.id, source_event_id="after-risk-pause")


def test_emergency_stop_blocks_new_intent_before_persistence_and_clear_requires_recovery_resolution():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        candidate = _seed_candidate_and_gates(session); service = _service(session)
        service.activate_emergency_stop("operator test")
        with pytest.raises(ValueError, match="EMERGENCY_STOP_ACTIVE"):
            _prepare(service, candidate.id, "cycle-2")
        rec = LiveReconciliation(status="RECOVERY_REQUIRED", reason_code="TEST", details="uncertain")
        session.add(rec); session.commit(); session.refresh(rec)
        with pytest.raises(ValueError, match="recovery is unresolved"):
            service.clear_emergency_stop("reviewed")
        service.resolve_reconciliation(rec.id, "operator reconciled external evidence")
        cleared = service.clear_emergency_stop("recovery resolved")
        assert cleared.active is False
