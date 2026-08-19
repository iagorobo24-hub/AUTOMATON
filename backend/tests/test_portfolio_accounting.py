from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.accounting.service import AccountingError, AccountingService
from app.models import Agent, StrategyEnum
from app.models.accounting import Account, Fill, Order, Position


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


def _agent(session: Session) -> Agent:
    agent = Agent(
        nombre="ACCOUNTING",
        presupuesto_inicial=1000,
        presupuesto_actual=1000,
        estrategia=StrategyEnum.S1,
    )
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def test_deposit_increases_funded_capital_and_cash_without_profit(engine):
    with Session(engine) as session:
        agent = _agent(session)
        service = AccountingService(session)
        account = service.create_account(agent.id, Decimal("1000"))

        service.deposit(account.id, Decimal("250"), reason="operator_funding")
        session.refresh(account)

        assert account.initial_capital == Decimal("1000")
        assert account.funded_capital == Decimal("1250")
        assert account.cash == Decimal("1250")
        assert account.realized_pnl == Decimal("0")
        assert account.fees_paid == Decimal("0")


def test_buy_fill_reduces_cash_and_builds_fee_inclusive_average_cost(engine):
    with Session(engine) as session:
        agent = _agent(session)
        service = AccountingService(session)
        account = service.create_account(agent.id, Decimal("1000"))
        order = service.create_order(account.id, "BTC/USDT", "BUY", Decimal("2"))

        service.apply_fill(
            order.id,
            quantity=Decimal("2"),
            price=Decimal("100"),
            fee=Decimal("2"),
            observed_at=datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        )

        position = session.exec(select(Position)).one()
        fill = session.exec(select(Fill)).one()
        session.refresh(account)
        session.refresh(order)

        assert account.cash == Decimal("798")
        assert account.fees_paid == Decimal("2")
        assert account.realized_pnl == Decimal("0")
        assert position.quantity == Decimal("2")
        assert position.average_cost == Decimal("101")
        assert order.status == "FILLED"
        assert fill.evidence_mode == "paper"


def test_partial_sell_realizes_net_pnl_once_and_preserves_remaining_cost_basis(engine):
    with Session(engine) as session:
        agent = _agent(session)
        service = AccountingService(session)
        account = service.create_account(agent.id, Decimal("1000"))
        buy = service.create_order(account.id, "BTC/USDT", "BUY", Decimal("2"))
        service.apply_fill(
            buy.id,
            quantity=Decimal("2"),
            price=Decimal("100"),
            fee=Decimal("2"),
            observed_at=datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        )
        sell = service.create_order(account.id, "BTC/USDT", "SELL", Decimal("1"))
        service.apply_fill(
            sell.id,
            quantity=Decimal("1"),
            price=Decimal("120"),
            fee=Decimal("1"),
            observed_at=datetime(2026, 8, 19, 12, 5, tzinfo=timezone.utc),
        )

        position = session.exec(select(Position)).one()
        session.refresh(account)

        assert account.cash == Decimal("917")
        assert account.fees_paid == Decimal("3")
        assert account.realized_pnl == Decimal("18")
        assert position.quantity == Decimal("1")
        assert position.average_cost == Decimal("101")

        snapshot = service.snapshot(account.id, {"BTC/USDT": Decimal("120")})
        assert snapshot.market_value == Decimal("120")
        assert snapshot.unrealized_pnl == Decimal("19")
        assert snapshot.equity == Decimal("1037")
        assert snapshot.exposure == Decimal("120")
        assert snapshot.reconciliation_delta == Decimal("0")


def test_full_close_zeroes_position_and_reconciles_equity(engine):
    with Session(engine) as session:
        agent = _agent(session)
        service = AccountingService(session)
        account = service.create_account(agent.id, Decimal("1000"))
        buy = service.create_order(account.id, "ETH/USDT", "BUY", Decimal("1"))
        service.apply_fill(
            buy.id,
            quantity=Decimal("1"),
            price=Decimal("200"),
            fee=Decimal("2"),
            observed_at=datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        )
        sell = service.create_order(account.id, "ETH/USDT", "SELL", Decimal("1"))
        service.apply_fill(
            sell.id,
            quantity=Decimal("1"),
            price=Decimal("250"),
            fee=Decimal("1"),
            observed_at=datetime(2026, 8, 19, 13, 0, tzinfo=timezone.utc),
        )

        position = session.exec(select(Position)).one()
        session.refresh(account)
        snapshot = service.snapshot(account.id, {})

        assert position.quantity == Decimal("0")
        assert position.average_cost == Decimal("0")
        assert account.cash == Decimal("1047")
        assert account.realized_pnl == Decimal("47")
        assert snapshot.equity == Decimal("1047")
        assert snapshot.reconciliation_delta == Decimal("0")


def test_accounting_rejects_oversell_and_insufficient_cash_without_partial_mutation(engine):
    with Session(engine) as session:
        agent = _agent(session)
        service = AccountingService(session)
        account = service.create_account(agent.id, Decimal("100"))
        expensive = service.create_order(account.id, "BTC/USDT", "BUY", Decimal("2"))

        with pytest.raises(AccountingError):
            service.apply_fill(
                expensive.id,
                quantity=Decimal("2"),
                price=Decimal("100"),
                fee=Decimal("1"),
                observed_at=datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
            )

        session.refresh(account)
        assert account.cash == Decimal("100")
        assert session.exec(select(Fill)).all() == []
        assert session.exec(select(Position)).all() == []

        sell = service.create_order(account.id, "BTC/USDT", "SELL", Decimal("1"))
        with pytest.raises(AccountingError):
            service.apply_fill(
                sell.id,
                quantity=Decimal("1"),
                price=Decimal("100"),
                fee=Decimal("1"),
                observed_at=datetime(2026, 8, 19, 12, 1, tzinfo=timezone.utc),
            )

        session.refresh(account)
        assert account.cash == Decimal("100")
        assert session.exec(select(Fill)).all() == []


def test_reload_from_persisted_records_preserves_reconciliation(engine):
    with Session(engine) as session:
        agent = _agent(session)
        service = AccountingService(session)
        account = service.create_account(agent.id, Decimal("500"))
        order = service.create_order(account.id, "SOL/USDT", "BUY", Decimal("2"))
        service.apply_fill(
            order.id,
            quantity=Decimal("2"),
            price=Decimal("50"),
            fee=Decimal("1"),
            observed_at=datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        )
        account_id = account.id

    with Session(engine) as reloaded_session:
        service = AccountingService(reloaded_session)
        snapshot = service.snapshot(account_id, {"SOL/USDT": Decimal("55")})
        assert snapshot.cash == Decimal("399")
        assert snapshot.market_value == Decimal("110")
        assert snapshot.unrealized_pnl == Decimal("9")
        assert snapshot.equity == Decimal("509")
        assert snapshot.reconciliation_delta == Decimal("0")


def test_reconcile_detects_tampered_cash_and_order_fill_mismatch(engine):
    with Session(engine) as session:
        agent = _agent(session)
        service = AccountingService(session)
        account = service.create_account(agent.id, Decimal("500"))
        order = service.create_order(account.id, "SOL/USDT", "BUY", Decimal("2"))
        service.apply_fill(
            order.id,
            quantity=Decimal("2"),
            price=Decimal("50"),
            fee=Decimal("1"),
            observed_at=datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        )

        account.cash += Decimal("10")
        order.filled_quantity = Decimal("1")
        session.add(account)
        session.add(order)
        session.commit()

        report = service.reconcile(account.id, {"SOL/USDT": Decimal("55")})

        assert report.ok is False
        assert "equity_identity_mismatch" in report.issues
        assert "order_fill_quantity_mismatch" in report.issues
