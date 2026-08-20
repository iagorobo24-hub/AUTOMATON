from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.live_execution.policy import bootstrap_live_policy, ensure_emergency_stop_baseline
from app.models import LiveEmergencyStop, LivePolicy


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def test_live_v1_bootstrap_is_idempotent_and_conservative():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        first = bootstrap_live_policy(session)
        second = bootstrap_live_policy(session)
        assert first.id == second.id
        assert first.version == "live-v1"
        assert first.max_deployable_capital == Decimal("100")
        assert first.max_order_notional == Decimal("25")
        assert first.max_symbol_exposure == Decimal("50")
        assert first.max_portfolio_exposure == Decimal("100")
        assert first.max_session_loss == Decimal("5")
        assert first.max_drawdown == Decimal("0.05")
        assert first.rollout_stage == "CANARY"
        assert first.rollout_capital_fraction == Decimal("0.10")
        assert first.manual_approval_required is True
        assert len(session.exec(select(LivePolicy)).all()) == 1


def test_emergency_stop_baseline_is_singleton_and_inactive():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        first = ensure_emergency_stop_baseline(session)
        second = ensure_emergency_stop_baseline(session)
        assert first.id == second.id
        assert first.active is False
        assert len(session.exec(select(LiveEmergencyStop)).all()) == 1
