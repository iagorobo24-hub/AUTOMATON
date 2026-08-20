from sqlmodel import Session, select

from app.live_execution.adapter import LiveExchangeAdapter
from app.models.live_execution import LiveCircuitBreakerEvent, LiveOrderIntent, LiveReconciliation


def reconcile_live_state(session: Session, adapter: LiveExchangeAdapter) -> LiveReconciliation:
    """Reconcile persisted Live-preparation state against read-only venue state.

    Phase 10 never transmits orders. Any venue observation for a prepared client id
    is therefore ambiguous and fails closed rather than being adopted or replayed.
    """
    prepared = list(session.exec(select(LiveOrderIntent).where(LiveOrderIntent.status == "PREPARED")))
    ambiguous: list[str] = []
    for intent in prepared:
        venue_order = adapter.lookup_order(intent.client_order_id)
        if venue_order is not None:
            ambiguous.append(intent.client_order_id)

    caps = adapter.capabilities()
    if caps.trading_enabled:
        ambiguous.append("ADAPTER_TRADING_ENABLED_DURING_PHASE_10")

    status = "RECOVERY_REQUIRED" if ambiguous else "CLEAN"
    reason_code = "UNEXPECTED_VENUE_STATE" if ambiguous else "MATCHED_READ_ONLY_STATE"
    record = LiveReconciliation(
        status=status,
        reason_code=reason_code,
        details=",".join(ambiguous),
    )
    session.add(record)
    if ambiguous:
        session.add(
            LiveCircuitBreakerEvent(
                event_type="RECONCILIATION_BLOCK",
                reason_code=reason_code,
                reason="Live reconciliation observed ambiguous or forbidden venue state",
            )
        )
    session.commit()
    session.refresh(record)
    return record
