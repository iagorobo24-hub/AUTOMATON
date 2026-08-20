import hashlib
from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.backtesting.runner import strategy_source_sha256
from app.live_execution.adapter import LiveExchangeAdapter
from app.live_execution.policy import ensure_emergency_stop_baseline, get_active_live_policy
from app.live_execution.readiness import LiveReadinessEvaluator
from app.live_execution.rules import validate_live_intent_rules
from app.models.live_execution import LiveEmergencyStop, LiveOrderIntent, LiveReconciliation
from app.models.strategy_research import StrategyCandidate


def _utcnow():
    return datetime.now(timezone.utc)


def _canonical_decimal(value: Decimal) -> str:
    return format(value.normalize(), "f")


def deterministic_client_order_id(*, candidate_id: int, symbol: str, side: str, source_event_id: str) -> str:
    raw = f"live-v1|{candidate_id}|{symbol.upper()}|{side.upper()}|{source_event_id}"
    return "live:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:56]


def live_intent_fingerprint(
    *,
    candidate_id: int,
    policy_version: str,
    source_event_id: str,
    symbol: str,
    side: str,
    quantity: Decimal,
    reference_price: Decimal,
    projected_symbol_exposure: Decimal,
    projected_portfolio_exposure: Decimal,
    deployable_capital: Decimal,
) -> str:
    canonical = "|".join(
        (
            "live-intent-v1",
            str(candidate_id),
            policy_version,
            source_event_id,
            symbol.upper(),
            side.upper(),
            _canonical_decimal(quantity),
            _canonical_decimal(reference_price),
            _canonical_decimal(projected_symbol_exposure),
            _canonical_decimal(projected_portfolio_exposure),
            _canonical_decimal(deployable_capital),
        )
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class LiveReadinessService:
    def __init__(self, session: Session, adapter: LiveExchangeAdapter, market_data_status: dict | None = None):
        self.session = session
        self.adapter = adapter
        self.market_data_status = market_data_status

    def _require_fresh_ready_candidate(self, candidate_id: int) -> StrategyCandidate:
        candidate = self.session.get(StrategyCandidate, candidate_id)
        if candidate is None or candidate.status != "PROMOTED":
            raise ValueError("Promoted StrategyCandidate is required for Live intent preparation")
        if strategy_source_sha256() != candidate.strategy_source_sha256:
            raise ValueError("Strategy source drift blocks Live intent preparation")
        if self.market_data_status is None:
            raise ValueError("Fresh Market Data status is required for Live intent preparation")

        readiness = LiveReadinessEvaluator(
            self.session,
            self.adapter,
            self.market_data_status,
        ).evaluate(candidate_id)
        if not readiness.architecture_ready:
            raise ValueError(
                f"Fresh ARCHITECTURE_READY evaluation is required before Live intent preparation: {readiness.reason_codes}"
            )
        if readiness.real_capital_blocked is not True:
            raise ValueError("Phase 10 readiness invariant violated: real capital must remain blocked")
        return candidate

    def prepare_intent(
        self,
        *,
        candidate_id: int,
        source_event_id: str,
        symbol: str,
        side: str,
        quantity: Decimal,
        reference_price: Decimal,
        projected_symbol_exposure: Decimal,
        projected_portfolio_exposure: Decimal,
        deployable_capital: Decimal,
    ) -> LiveOrderIntent:
        source_event_id = source_event_id.strip()
        symbol = symbol.strip().upper()
        side = side.strip().upper()
        if not source_event_id:
            raise ValueError("Live intent source_event_id is required")
        if not symbol:
            raise ValueError("Live intent symbol is required")
        if side not in {"BUY", "SELL"}:
            raise ValueError("Live intent side must be BUY or SELL")

        self._require_fresh_ready_candidate(candidate_id)
        policy = get_active_live_policy(self.session)
        client_order_id = deterministic_client_order_id(
            candidate_id=candidate_id,
            symbol=symbol,
            side=side,
            source_event_id=source_event_id,
        )
        fingerprint = live_intent_fingerprint(
            candidate_id=candidate_id,
            policy_version=policy.version,
            source_event_id=source_event_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            reference_price=reference_price,
            projected_symbol_exposure=projected_symbol_exposure,
            projected_portfolio_exposure=projected_portfolio_exposure,
            deployable_capital=deployable_capital,
        )
        existing = self.session.exec(
            select(LiveOrderIntent).where(LiveOrderIntent.client_order_id == client_order_id)
        ).first()
        if existing is not None:
            if existing.intent_fingerprint != fingerprint:
                raise ValueError("Live intent idempotency conflict: same client id with different payload")
            return existing

        stop = ensure_emergency_stop_baseline(self.session)
        reasons: list[str] = []
        if stop.active:
            reasons.append("EMERGENCY_STOP_ACTIVE")
        reasons.extend(
            validate_live_intent_rules(
                policy=policy,
                rules=self.adapter.get_symbol_rules(symbol),
                quantity=quantity,
                reference_price=reference_price,
                projected_symbol_exposure=projected_symbol_exposure,
                projected_portfolio_exposure=projected_portfolio_exposure,
                deployable_capital=deployable_capital,
            )
        )
        intent = LiveOrderIntent(
            candidate_id=candidate_id,
            client_order_id=client_order_id,
            intent_fingerprint=fingerprint,
            source_event_id=source_event_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            reference_price=reference_price,
            requested_notional=quantity * reference_price,
            projected_symbol_exposure=projected_symbol_exposure,
            projected_portfolio_exposure=projected_portfolio_exposure,
            status="BLOCKED" if reasons else "PREPARED",
            reason_code=reasons[0] if reasons else "OK",
        )
        self.session.add(intent)
        self.session.commit()
        self.session.refresh(intent)
        return intent

    def activate_emergency_stop(self, reason: str) -> LiveEmergencyStop:
        reason = reason.strip()
        if not reason:
            raise ValueError("Emergency-stop reason is required")
        state = ensure_emergency_stop_baseline(self.session)
        state.active = True
        state.reason = reason
        state.updated_at = _utcnow()
        self.session.add(state)
        self.session.commit()
        self.session.refresh(state)
        return state

    def clear_emergency_stop(self, reason: str) -> LiveEmergencyStop:
        reason = reason.strip()
        if not reason:
            raise ValueError("Emergency-stop clear reason is required")
        unresolved = self.session.exec(
            select(LiveReconciliation).where(LiveReconciliation.status == "RECOVERY_REQUIRED")
        ).first()
        if unresolved is not None:
            raise ValueError("Cannot clear emergency stop while Live recovery is unresolved")
        state = ensure_emergency_stop_baseline(self.session)
        state.active = False
        state.reason = f"CLEARED: {reason}"
        state.updated_at = _utcnow()
        self.session.add(state)
        self.session.commit()
        self.session.refresh(state)
        return state
