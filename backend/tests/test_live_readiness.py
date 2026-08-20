from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.backtesting.runner import strategy_source_sha256
from app.live_execution.adapter import DisabledLiveAdapter
from app.live_execution.policy import bootstrap_live_policy, ensure_emergency_stop_baseline
from app.live_execution.readiness import LiveReadinessEvaluator
from app.models import LiveReconciliation, RiskProfile, StrategyCandidate


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _risk():
    return RiskProfile(
        name="Risk", version="risk-v1", active=True, paused=False,
        max_order_notional=Decimal("100"), max_order_equity_pct=Decimal("0.25"),
        max_total_exposure_pct=Decimal("0.80"), max_symbol_exposure_pct=Decimal("0.40"),
        max_open_positions=4, max_realized_loss_pct=Decimal("0.10"),
        max_drawdown_pct=Decimal("0.15"), max_quote_age_seconds=30,
    )


def test_architecture_can_be_ready_while_real_capital_remains_blocked():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_live_policy(session); ensure_emergency_stop_baseline(session)
        session.add(_risk())
        candidate = StrategyCandidate(
            study_id=1, evaluation_id=1, strategy_id="S1", strategy_version="baseline-v1",
            strategy_source_sha256=strategy_source_sha256(), status="PROMOTED",
        )
        session.add(candidate)
        session.add(LiveReconciliation(status="CLEAN", reason_code="MATCHED_READ_ONLY_STATE", details=""))
        session.commit(); session.refresh(candidate)

        result = LiveReadinessEvaluator(session, DisabledLiveAdapter()).evaluate(candidate.id)
        assert result.architecture_ready is True
        assert result.decision == "ARCHITECTURE_READY"
        assert result.real_capital_blocked is True


def test_readiness_fails_closed_without_candidate_and_on_emergency_stop():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_live_policy(session)
        stop = ensure_emergency_stop_baseline(session)
        session.add(_risk())
        session.add(LiveReconciliation(status="CLEAN", reason_code="MATCHED_READ_ONLY_STATE", details=""))
        stop.active = True; stop.reason = "operator"; session.add(stop); session.commit()

        result = LiveReadinessEvaluator(session, DisabledLiveAdapter()).evaluate(None)
        assert result.architecture_ready is False
        assert result.real_capital_blocked is True
        assert "PROMOTED_CANDIDATE_REQUIRED" in result.reason_codes
        assert "EMERGENCY_STOP_ACTIVE" in result.reason_codes
