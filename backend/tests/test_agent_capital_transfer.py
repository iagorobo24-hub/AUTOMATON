from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.accounting.service import AccountingError, AccountingService
from app.models import Account, Agent, AgentStatus, LedgerEntry, StrategyEnum


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _agent(session: Session, name: str):
    agent = Agent(nombre=name, presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=StrategyEnum.S1, estado=AgentStatus.ACTIVO)
    session.add(agent); session.commit(); session.refresh(agent)
    return agent


def test_transfer_to_child_conserves_cash_and_funded_capital_and_creates_paired_ledger_entries():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        parent = _agent(session, "parent")
        child = _agent(session, "child")
        service = AccountingService(session)
        parent_account = service.create_account(parent.id, Decimal("1000"))

        parent_after, child_account = service.transfer_to_child(
            parent_account.id,
            child.id,
            Decimal("250"),
            reason="agent_replication",
        )

        assert parent_after.cash == Decimal("750")
        assert parent_after.funded_capital == Decimal("750")
        assert child_account.cash == Decimal("250")
        assert child_account.funded_capital == Decimal("250")
        assert parent_after.cash + child_account.cash == Decimal("1000")
        assert parent_after.funded_capital + child_account.funded_capital == Decimal("1000")

        entries = session.exec(select(LedgerEntry).order_by(LedgerEntry.id)).all()
        assert [(e.account_id, e.entry_type, e.amount) for e in entries[-2:]] == [
            (parent_after.id, "CAPITAL_TRANSFER_OUT", Decimal("-250")),
            (child_account.id, "CAPITAL_TRANSFER_IN", Decimal("250")),
        ]


def test_transfer_rejects_reserved_cash_or_amount_above_funded_capital():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        parent = _agent(session, "parent")
        child = _agent(session, "child")
        service = AccountingService(session)
        account = service.create_account(parent.id, Decimal("1000"))
        account.reserved_cash = Decimal("900")
        session.add(account); session.commit()

        with pytest.raises(AccountingError, match="available cash"):
            service.transfer_to_child(account.id, child.id, Decimal("250"), reason="agent_replication")

        account.reserved_cash = Decimal("0")
        account.funded_capital = Decimal("100")
        session.add(account); session.commit()
        with pytest.raises(AccountingError, match="funded capital"):
            service.transfer_to_child(account.id, child.id, Decimal("250"), reason="agent_replication")

        assert session.exec(select(Account).where(Account.agente_id == child.id)).first() is None


def test_transfer_rejects_existing_child_account_and_never_copies_positions():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        parent = _agent(session, "parent")
        child = _agent(session, "child")
        service = AccountingService(session)
        parent_account = service.create_account(parent.id, Decimal("1000"))
        service.create_account(child.id, Decimal("100"))

        with pytest.raises(AccountingError, match="already has"):
            service.transfer_to_child(parent_account.id, child.id, Decimal("250"), reason="agent_replication")
