from sqlmodel import Session, select

from app.backtesting.runner import strategy_source_sha256
from app.live_execution.adapter import LiveExchangeAdapter
from app.live_execution.policy import ensure_emergency_stop_baseline, get_active_live_policy
from app.models.live_execution import LiveReadinessEvaluation, LiveReconciliation
from app.models.paper_execution import PaperExecution, PaperRequest
from app.models.risk import RiskProfile
from app.models.strategy_research import StrategyCandidate


class LiveReadinessEvaluator:
    """Fail-closed technical readiness evaluator.

    It may classify architecture as ready for a future activation review, but
    every result keeps real-capital execution blocked.
    """

    def __init__(self, session: Session, adapter: LiveExchangeAdapter, market_data_status: dict):
        self.session = session
        self.adapter = adapter
        self.market_data_status = market_data_status

    def evaluate(self, candidate_id: int | None = None) -> LiveReadinessEvaluation:
        reasons: list[str] = []
        policy = get_active_live_policy(self.session)
        stop = ensure_emergency_stop_baseline(self.session)

        candidate = self.session.get(StrategyCandidate, candidate_id) if candidate_id is not None else None
        if candidate is None:
            reasons.append("PROMOTED_CANDIDATE_REQUIRED")
        elif candidate.status != "PROMOTED":
            reasons.append("CANDIDATE_NOT_PROMOTED")
        else:
            try:
                current_sha = strategy_source_sha256()
            except Exception:
                current_sha = None
                reasons.append("ACTIVE_STRATEGY_FINGERPRINT_UNAVAILABLE")
            if current_sha is not None and current_sha != candidate.strategy_source_sha256:
                reasons.append("STRATEGY_SOURCE_DRIFT")

        market = self.market_data_status or {}
        if market.get("evidence_mode") != "real" or market.get("synthetic_fallback") is not False:
            reasons.append("REAL_FAIL_CLOSED_MARKET_DATA_REQUIRED")
        if market.get("execution_capability") is not False:
            reasons.append("MARKET_DATA_MUST_NOT_EXECUTE")

        risk = self.session.exec(select(RiskProfile).where(RiskProfile.active == True)).first()  # noqa: E712
        if risk is None:
            reasons.append("ACTIVE_RISK_PROFILE_REQUIRED")
        elif risk.paused:
            reasons.append("RISK_PAUSED")

        if self.session.exec(select(PaperRequest).where(PaperRequest.status == "RECOVERY_REQUIRED")).first() is not None:
            reasons.append("PAPER_REQUEST_RECOVERY_UNRESOLVED")
        if self.session.exec(select(PaperExecution).where(PaperExecution.status == "RECOVERY_REQUIRED")).first() is not None:
            reasons.append("PAPER_EXECUTION_RECOVERY_UNRESOLVED")
        if self.session.exec(select(LiveReconciliation).where(LiveReconciliation.status == "RECOVERY_REQUIRED")).first() is not None:
            reasons.append("LIVE_RECOVERY_UNRESOLVED")

        if stop.active:
            reasons.append("EMERGENCY_STOP_ACTIVE")
        if policy.rollout_stage != "CANARY":
            reasons.append("ROLLOUT_STAGE_NOT_CANARY")
        if not policy.manual_approval_required:
            reasons.append("MANUAL_APPROVAL_REQUIRED")
        if policy.max_deployable_capital <= 0 or policy.max_order_notional <= 0:
            reasons.append("INVALID_LIVE_LIMITS")

        latest_reconciliation = self.session.exec(select(LiveReconciliation).order_by(LiveReconciliation.id.desc())).first()
        if latest_reconciliation is None:
            reasons.append("CLEAN_RECONCILIATION_REQUIRED")
        elif latest_reconciliation.status not in {"CLEAN", "RESOLVED"} and "LIVE_RECOVERY_UNRESOLVED" not in reasons:
            reasons.append("LIVE_RECOVERY_UNRESOLVED")

        caps = self.adapter.capabilities()
        if caps.trading_enabled:
            reasons.append("PHASE_10_ADAPTER_MUST_NOT_TRADE")
        if caps.withdrawals_enabled:
            reasons.append("WITHDRAWAL_PERMISSION_FORBIDDEN")

        architecture_ready = not reasons
        result = LiveReadinessEvaluation(
            candidate_id=candidate.id if candidate is not None else None,
            policy_version=policy.version,
            architecture_ready=architecture_ready,
            real_capital_blocked=True,
            decision="ARCHITECTURE_READY" if architecture_ready else "BLOCKED",
            reason_codes=",".join(reasons),
            reason=("Technical Live boundary satisfies live-v1; real capital remains disabled" if architecture_ready else "Live readiness blocked by one or more fail-closed gates"),
            strategy_source_sha256=(candidate.strategy_source_sha256 if candidate is not None else None),
        )
        self.session.add(result); self.session.commit(); self.session.refresh(result)
        return result
