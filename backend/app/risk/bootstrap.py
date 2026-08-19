from decimal import Decimal

from sqlmodel import Session, select

from app.models.risk import RiskProfile


RISK_V1_VERSION = "risk-v1"


def ensure_active_risk_profile(session: Session) -> RiskProfile:
    profile = session.exec(
        select(RiskProfile).where(RiskProfile.version == RISK_V1_VERSION)
    ).first()
    if profile is not None:
        return profile

    profile = RiskProfile(
        name="Default Paper Risk",
        version=RISK_V1_VERSION,
        active=True,
        paused=False,
        max_order_notional=Decimal("250"),
        max_order_equity_pct=Decimal("0.25"),
        max_total_exposure_pct=Decimal("0.60"),
        max_symbol_exposure_pct=Decimal("0.35"),
        max_open_positions=4,
        max_realized_loss_pct=Decimal("0.10"),
        max_drawdown_pct=Decimal("0.15"),
        max_quote_age_seconds=30,
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile
