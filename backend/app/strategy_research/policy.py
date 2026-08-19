from decimal import Decimal

from sqlmodel import Session, select

from app.models.strategy_research import ResearchPolicy


def bootstrap_research_policy(session: Session) -> ResearchPolicy:
    existing = session.exec(
        select(ResearchPolicy).where(ResearchPolicy.version == "research-v1")
    ).first()
    if existing is not None:
        return existing
    policy = ResearchPolicy(
        version="research-v1",
        active=True,
        min_historical_windows=3,
        min_validation_round_trips=5,
        min_oos_round_trips=5,
        max_oos_drawdown=Decimal("0.15"),
        min_oos_profit_factor=Decimal("1.05"),
        max_relative_return_degradation=Decimal("0.50"),
        min_forward_closing_sells=3,
    )
    session.add(policy)
    session.commit()
    session.refresh(policy)
    return policy
