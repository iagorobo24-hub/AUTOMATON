from decimal import Decimal

from sqlmodel import Session, select

from app.models import Agent, AgentLifecycleEvent, EvolutionPolicy

POLICY_VERSION = "evolution-v1"


def bootstrap_evolution_policy(session: Session) -> EvolutionPolicy:
    existing = session.exec(
        select(EvolutionPolicy).where(EvolutionPolicy.version == POLICY_VERSION)
    ).first()
    if existing is not None:
        return existing

    policy = EvolutionPolicy(
        version=POLICY_VERSION,
        active=True,
        min_backtest_round_trips=5,
        min_backtest_net_return=Decimal("0"),
        min_backtest_expectancy=Decimal("0"),
        max_backtest_drawdown=Decimal("0.15"),
        min_paper_closed_trades=3,
        min_paper_realized_pnl=Decimal("0"),
        child_allocation_fraction=Decimal("0.25"),
    )
    session.add(policy)
    session.commit()
    session.refresh(policy)
    return policy


def bootstrap_lifecycle_baselines(session: Session) -> int:
    created = 0
    agents = session.exec(select(Agent)).all()
    for agent in agents:
        existing = session.exec(
            select(AgentLifecycleEvent).where(AgentLifecycleEvent.agent_id == agent.id)
        ).first()
        if existing is not None:
            continue
        session.add(
            AgentLifecycleEvent(
                agent_id=agent.id,
                event_type="LEGACY_BASELINE",
                reason="phase_6_existing_agent_baseline",
            )
        )
        created += 1
    if created:
        session.commit()
    return created


def active_evolution_policy(session: Session) -> EvolutionPolicy:
    policy = session.exec(
        select(EvolutionPolicy).where(EvolutionPolicy.active == True)  # noqa: E712
        .order_by(EvolutionPolicy.id.desc())
    ).first()
    if policy is None:
        policy = bootstrap_evolution_policy(session)
    return policy
