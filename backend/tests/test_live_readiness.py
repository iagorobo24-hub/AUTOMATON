from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.backtesting.runner import strategy_source_sha256
from app.live_execution.adapter import AdapterCapabilities, DisabledLiveAdapter
from app.live_execution.policy import bootstrap_live_policy, ensure_emergency_stop_baseline
from app.live_execution.readiness import LiveReadinessEvaluator
from app.models import (
    LiveReconciliation,
    PaperRequest,
    ResearchEvaluation,
    ResearchStudy,
    RiskProfile,
    StrategyCandidate,
)

REAL_MARKET = {"provider": "test", "evidence_mode": "real", "synthetic_fallback": False, "execution_capability": False}


class MetadataAdapter(DisabledLiveAdapter):
    def __init__(self, *, trading=False, credentials=False, withdrawals=False, trade_permission=False):
        self._caps = AdapterCapabilities("metadata-test", trading, credentials, withdrawals, trade_permission)

    def capabilities(self):
        return self._caps


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _risk():
    return RiskProfile(
        name="Risk", version="risk-v1", active=True, paused=False,
        max_order_notional=Decimal("100"), max_order_equity_pct=Decimal("0.25"),
        max_total_exposure_pct=Decimal("0.80"), max_symbol_exposure_pct=Decimal("0.40"),
        max_open_positions=4, max_realized_loss_pct=Decimal("0.10"), max_drawdown_pct=Decimal("0.15"), max_quote_age_seconds=30,
    )


def _candidate(session, *, decision="PASS", source_sha=None):
    source_sha = source_sha or strategy_source_sha256()
    study = ResearchStudy(
        name="Live candidate study",
        strategy_id="S1",
        status="PROMOTED",
        strategy_version="baseline-v1",
        strategy_source_sha256=source_sha,
        execution_policy="backtest-v1",
        fee_bps=Decimal("10"),
        slippage_bps=Decimal("10"),
        position_fraction=Decimal("0.25"),
    )
    session.add(study); session.commit(); session.refresh(study)
    evaluation = ResearchEvaluation(
        study_id=study.id,
        policy_version="research-v1",
        decision=decision,
        reason_code="OK" if decision == "PASS" else "TEST_REJECT",
        reason="test",
        strategy_id="S1",
        strategy_version="baseline-v1",
        strategy_source_sha256=source_sha,
        historical_run_ids="1,2,3",
        forward_session_ids="1",
    )
    session.add(evaluation); session.commit(); session.refresh(evaluation)
    candidate = StrategyCandidate(
        study_id=study.id,
        evaluation_id=evaluation.id,
        strategy_id="S1",
        strategy_version="baseline-v1",
        strategy_source_sha256=source_sha,
        status="PROMOTED",
    )
    session.add(candidate); session.commit(); session.refresh(candidate)
    return candidate


def _seed_common(session):
    bootstrap_live_policy(session)
    ensure_emergency_stop_baseline(session)
    session.add(_risk())
    session.add(LiveReconciliation(status="CLEAN", reason_code="MATCHED_READ_ONLY_STATE", details=""))
    session.commit()


def test_architecture_can_be_ready_while_real_capital_remains_blocked():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_common(session)
        candidate = _candidate(session)
        result = LiveReadinessEvaluator(session, DisabledLiveAdapter(), REAL_MARKET).evaluate(candidate.id)
        assert result.architecture_ready is True
        assert result.decision == "ARCHITECTURE_READY"
        assert result.real_capital_blocked is True


def test_readiness_rejects_promoted_candidate_without_valid_pass_evidence():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_common(session)
        rejected_candidate = _candidate(session, decision="REJECT")
        result = LiveReadinessEvaluator(session, DisabledLiveAdapter(), REAL_MARKET).evaluate(rejected_candidate.id)
        assert result.architecture_ready is False
        assert "CANDIDATE_RESEARCH_EVIDENCE_NOT_PASS" in result.reason_codes


def test_readiness_rejects_orphan_promoted_candidate_even_when_sqlite_fk_is_not_enforced():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_common(session)
        orphan = StrategyCandidate(
            study_id=999,
            evaluation_id=999,
            strategy_id="S1",
            strategy_version="baseline-v1",
            strategy_source_sha256=strategy_source_sha256(),
            status="PROMOTED",
        )
        session.add(orphan); session.commit(); session.refresh(orphan)
        result = LiveReadinessEvaluator(session, DisabledLiveAdapter(), REAL_MARKET).evaluate(orphan.id)
        assert result.architecture_ready is False
        assert "CANDIDATE_RESEARCH_EVIDENCE_MISSING" in result.reason_codes


def test_readiness_fails_closed_without_candidate_and_on_emergency_stop():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_common(session)
        stop = ensure_emergency_stop_baseline(session)
        stop.active = True; stop.reason = "operator"; session.add(stop); session.commit()
        result = LiveReadinessEvaluator(session, DisabledLiveAdapter(), REAL_MARKET).evaluate(None)
        assert result.architecture_ready is False
        assert result.real_capital_blocked is True
        assert "PROMOTED_CANDIDATE_REQUIRED" in result.reason_codes
        assert "EMERGENCY_STOP_ACTIVE" in result.reason_codes


def test_readiness_rejects_paused_risk_and_paper_recovery():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_common(session)
        candidate = _candidate(session)
        risk = session.exec(select(RiskProfile).where(RiskProfile.active == True)).first()  # noqa: E712
        risk.paused = True
        session.add(risk)
        session.add(PaperRequest(
            request_id="recovery-test",
            request_fingerprint="f" * 64,
            account_id=999,
            status="RECOVERY_REQUIRED",
            http_status=409,
        ))
        session.commit()
        result = LiveReadinessEvaluator(session, DisabledLiveAdapter(), REAL_MARKET).evaluate(candidate.id)
        assert "RISK_PAUSED" in result.reason_codes
        assert "PAPER_REQUEST_RECOVERY_UNRESOLVED" in result.reason_codes
        assert result.architecture_ready is False


def test_readiness_requires_clean_reconciliation_not_manual_resolved_label():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_common(session)
        candidate = _candidate(session)
        session.add(LiveReconciliation(status="RESOLVED", reason_code="OPERATOR", details="legacy shortcut"))
        session.commit()
        result = LiveReadinessEvaluator(session, DisabledLiveAdapter(), REAL_MARKET).evaluate(candidate.id)
        assert result.architecture_ready is False
        assert "CLEAN_RECONCILIATION_REQUIRED" in result.reason_codes


def test_readiness_rejects_forbidden_or_incoherent_adapter_permissions():
    cases = (
        (MetadataAdapter(trading=True), "PHASE_10_ADAPTER_MUST_NOT_TRADE"),
        (MetadataAdapter(credentials=True, withdrawals=True, trade_permission=True), "WITHDRAWAL_PERMISSION_FORBIDDEN"),
        (MetadataAdapter(credentials=True, trade_permission=False), "INVALID_CREDENTIAL_PERMISSION_METADATA"),
        (MetadataAdapter(credentials=False, trade_permission=True), "INVALID_CREDENTIAL_PERMISSION_METADATA"),
    )
    for adapter, expected_reason in cases:
        engine = _engine(); SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            _seed_common(session)
            candidate = _candidate(session)
            result = LiveReadinessEvaluator(session, adapter, REAL_MARKET).evaluate(candidate.id)
            assert result.architecture_ready is False
            assert expected_reason in result.reason_codes


def test_readiness_rejects_synthetic_or_execution_capable_market_data_contract():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_common(session)
        bad_market = {"evidence_mode": "synthetic", "synthetic_fallback": True, "execution_capability": True}
        result = LiveReadinessEvaluator(session, DisabledLiveAdapter(), bad_market).evaluate(None)
        assert "REAL_FAIL_CLOSED_MARKET_DATA_REQUIRED" in result.reason_codes
        assert "MARKET_DATA_MUST_NOT_EXECUTE" in result.reason_codes
