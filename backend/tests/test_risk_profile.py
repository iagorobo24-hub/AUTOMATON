from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.models.risk import RiskProfile
from app.risk.bootstrap import ensure_active_risk_profile


def _engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_risk_profile_bootstrap_is_idempotent_and_uses_risk_v1_defaults():
    engine = _engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        first = ensure_active_risk_profile(session)
        second = ensure_active_risk_profile(session)
        profiles = session.exec(select(RiskProfile)).all()

        assert first.id == second.id
        assert len(profiles) == 1
        assert first.version == "risk-v1"
        assert first.active is True
        assert first.paused is False
        assert first.max_order_notional == Decimal("250")
        assert first.max_order_equity_pct == Decimal("0.25")
        assert first.max_total_exposure_pct == Decimal("0.60")
        assert first.max_symbol_exposure_pct == Decimal("0.35")
        assert first.max_open_positions == 4
        assert first.max_realized_loss_pct == Decimal("0.10")
        assert first.max_drawdown_pct == Decimal("0.15")
        assert first.max_quote_age_seconds == 30
