from decimal import Decimal

from sqlmodel import Session, select

from app.models.live_execution import LiveEmergencyStop, LivePolicy


def bootstrap_live_policy(session: Session) -> LivePolicy:
    existing = session.exec(select(LivePolicy).where(LivePolicy.version == "live-v1")).first()
    if existing is not None:
        return existing
    policy = LivePolicy(
        version="live-v1",
        active=True,
        max_deployable_capital=Decimal("100"),
        max_order_notional=Decimal("25"),
        max_symbol_exposure=Decimal("50"),
        max_portfolio_exposure=Decimal("100"),
        max_session_loss=Decimal("5"),
        max_drawdown=Decimal("0.05"),
        max_consecutive_execution_errors=3,
        stale_market_data_seconds=30,
        rollout_stage="CANARY",
        rollout_capital_fraction=Decimal("0.10"),
        manual_approval_required=True,
    )
    session.add(policy)
    session.commit()
    session.refresh(policy)
    return policy


def get_active_live_policy(session: Session) -> LivePolicy:
    policy = session.exec(select(LivePolicy).where(LivePolicy.active == True)).first()  # noqa: E712
    return policy or bootstrap_live_policy(session)


def ensure_emergency_stop_baseline(session: Session) -> LiveEmergencyStop:
    state = session.exec(select(LiveEmergencyStop).where(LiveEmergencyStop.singleton_key == "global")).first()
    if state is not None:
        return state
    state = LiveEmergencyStop(singleton_key="global", active=False)
    session.add(state)
    session.commit()
    session.refresh(state)
    return state
