from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.pool import StaticPool

from app.accounting.bootstrap import ensure_accounting_baseline
from app.models import Agent, StrategyEnum
from app.models.accounting import Account, LedgerEntry


def test_existing_agent_bootstrap_uses_funded_baseline_not_legacy_current_balance():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        agent = Agent(
            nombre="LEGACY",
            presupuesto_inicial=1000,
            presupuesto_actual=1375,
            estrategia=StrategyEnum.S1,
        )
        session.add(agent)
        session.commit()
        session.refresh(agent)

        created = ensure_accounting_baseline(session)
        assert created == 1

        account = session.exec(select(Account).where(Account.agente_id == agent.id)).one()
        assert account.initial_capital == 1000
        assert account.funded_capital == 1000
        assert account.cash == 1000
        assert account.realized_pnl == 0

        entry = session.exec(
            select(LedgerEntry).where(LedgerEntry.account_id == account.id)
        ).one()
        assert entry.entry_type == "BASELINE_FUNDING"
        assert entry.reason == "phase_2_legacy_reset_excludes_unverified_pnl"

        assert ensure_accounting_baseline(session) == 0
