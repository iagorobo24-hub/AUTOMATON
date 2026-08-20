from sqlmodel import Session, select

from app.live_execution.adapter import LiveExchangeAdapter
from app.models.live_execution import (
    LiveCircuitBreakerEvent,
    LiveOrderIntent,
    LiveOrderRecord,
    LiveReconciliation,
)


def reconcile_live_state(session: Session, adapter: LiveExchangeAdapter) -> LiveReconciliation:
    """Reconcile Phase 10 preparation records against read-only venue state.

    Phase 10 is intentionally incapable of transmission. Therefore any venue
    order/position/fill, any lookup match for a PREPARED client id, any
    trading-enabled adapter, or any persisted order record that claims a
    transmitted state is unexplained financial state and must fail closed.
    Nothing in this function retries, submits, cancels or adopts venue state.
    """
    prepared = list(session.exec(select(LiveOrderIntent).where(LiveOrderIntent.status == "PREPARED")))
    order_records = list(session.exec(select(LiveOrderRecord)))
    ambiguous: list[str] = []

    for intent in prepared:
        venue_order = adapter.lookup_order(intent.client_order_id)
        if venue_order is not None:
            ambiguous.append(f"LOOKUP:{intent.client_order_id}")

    for record in order_records:
        if record.status != "NOT_TRANSMITTED" or record.venue_order_id is not None:
            ambiguous.append(f"ORDER_RECORD:{record.client_order_id}:{record.status}")

    open_orders = adapter.get_open_orders()
    if open_orders:
        ambiguous.append(f"OPEN_ORDERS:{len(open_orders)}")
    positions = adapter.get_positions()
    if positions:
        ambiguous.append(f"POSITIONS:{len(positions)}")
    fills = adapter.get_fills()
    if fills:
        ambiguous.append(f"FILLS:{len(fills)}")

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
                reason="Live reconciliation observed unexplained or forbidden financial state",
            )
        )
    session.commit()
    session.refresh(record)
    return record
