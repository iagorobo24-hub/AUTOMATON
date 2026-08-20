import hashlib
from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.live_execution.adapter import LiveExchangeAdapter
from app.live_execution.policy import ensure_emergency_stop_baseline, get_active_live_policy
from app.live_execution.rules import validate_live_intent_rules
from app.models.live_execution import LiveEmergencyStop, LiveOrderIntent, LiveReconciliation


def _utcnow():
    return datetime.now(timezone.utc)


def deterministic_client_order_id(*, candidate_id: int, symbol: str, side: str, source_event_id: str) -> str:
    raw = f"live-v1|{candidate_id}|{symbol.upper()}|{side.upper()}|{source_event_id}"
    return "live:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:56]


class LiveReadinessService:
    def __init__(self, session: Session, adapter: LiveExchangeAdapter):
        self.session = session
        self.adapter = adapter

    def prepare_intent(self, *, candidate_id: int, source_event_id: str, symbol: str, side: str, quantity: Decimal,
                       reference_price: Decimal, projected_symbol_exposure: Decimal,
                       projected_portfolio_exposure: Decimal, deployable_capital: Decimal) -> LiveOrderIntent:
        client_order_id = deterministic_client_order_id(candidate_id=candidate_id, symbol=symbol, side=side, source_event_id=source_event_id)
        existing = self.session.exec(select(LiveOrderIntent).where(LiveOrderIntent.client_order_id == client_order_id)).first()
        if existing is not None:
            return existing

        stop = ensure_emergency_stop_baseline(self.session)
        policy = get_active_live_policy(self.session)
        reasons: list[str] = []
        if stop.active:
            reasons.append("EMERGENCY_STOP_ACTIVE")
        reasons.extend(validate_live_intent_rules(
            policy=policy, rules=self.adapter.get_symbol_rules(symbol), quantity=quantity,
            reference_price=reference_price, projected_symbol_exposure=projected_symbol_exposure,
            projected_portfolio_exposure=projected_portfolio_exposure, deployable_capital=deployable_capital,
        ))
        intent = LiveOrderIntent(
            candidate_id=candidate_id, client_order_id=client_order_id, source_event_id=source_event_id,
            symbol=symbol.upper(), side=side.upper(), quantity=quantity, reference_price=reference_price,
            requested_notional=quantity * reference_price, projected_symbol_exposure=projected_symbol_exposure,
            projected_portfolio_exposure=projected_portfolio_exposure,
            status="BLOCKED" if reasons else "PREPARED", reason_code=reasons[0] if reasons else "OK",
        )
        self.session.add(intent); self.session.commit(); self.session.refresh(intent)
        return intent

    def activate_emergency_stop(self, reason: str) -> LiveEmergencyStop:
        reason = reason.strip()
        if not reason:
            raise ValueError("Emergency-stop reason is required")
        state = ensure_emergency_stop_baseline(self.session)
        state.active = True; state.reason = reason; state.updated_at = _utcnow()
        self.session.add(state); self.session.commit(); self.session.refresh(state)
        return state

    def resolve_reconciliation(self, reconciliation_id: int, reason: str) -> LiveReconciliation:
        reason = reason.strip()
        if not reason:
            raise ValueError("Reconciliation resolution reason is required")
        record = self.session.get(LiveReconciliation, reconciliation_id)
        if record is None:
            raise ValueError("Live reconciliation not found")
        if record.status != "RECOVERY_REQUIRED":
            raise ValueError("Only RECOVERY_REQUIRED reconciliation can be explicitly resolved")
        record.status = "RESOLVED"
        record.details = f"{record.details}\nOPERATOR_RESOLUTION: {reason}".strip()
        self.session.add(record); self.session.commit(); self.session.refresh(record)
        return record

    def clear_emergency_stop(self, reason: str) -> LiveEmergencyStop:
        reason = reason.strip()
        if not reason:
            raise ValueError("Emergency-stop clear reason is required")
        unresolved = self.session.exec(select(LiveReconciliation).where(LiveReconciliation.status == "RECOVERY_REQUIRED")).first()
        if unresolved is not None:
            raise ValueError("Cannot clear emergency stop while Live recovery is unresolved")
        state = ensure_emergency_stop_baseline(self.session)
        state.active = False; state.reason = f"CLEARED: {reason}"; state.updated_at = _utcnow()
        self.session.add(state); self.session.commit(); self.session.refresh(state)
        return state
