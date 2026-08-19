from decimal import Decimal

from sqlmodel import Session, select

from app.models import Account, Agent, LedgerEntry


def ensure_accounting_baseline(session: Session) -> int:
    """Create clean Phase 2 accounts for pre-accounting agents.

    Historical ``presupuesto_actual`` is deliberately ignored because it may
    contain synthetic/unverified PnL. ``presupuesto_inicial`` is the safest
    available funded-capital baseline from the legacy model.
    """
    created = 0
    agents = session.exec(select(Agent)).all()
    for agent in agents:
        existing = session.exec(
            select(Account).where(Account.agente_id == agent.id)
        ).first()
        if existing is not None:
            continue

        funded = Decimal(str(agent.presupuesto_inicial))
        if funded <= 0:
            continue

        account = Account(
            agente_id=agent.id,
            initial_capital=funded,
            funded_capital=funded,
            cash=funded,
        )
        session.add(account)
        session.flush()
        session.add(
            LedgerEntry(
                account_id=account.id,
                entry_type="BASELINE_FUNDING",
                amount=funded,
                reason="phase_2_legacy_reset_excludes_unverified_pnl",
            )
        )
        created += 1

    if created:
        session.commit()
    return created
