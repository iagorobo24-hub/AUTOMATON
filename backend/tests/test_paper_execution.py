from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.accounting.service import AccountingService
from app.market_data.contracts import Quote
from app.models import Agent, StrategyEnum
from app.models.accounting import Account, Fill, Order, Position
from app.models.paper_execution import PaperExecution
from app.paper_execution.service import (
    PaperExecutionError,
    PaperExecutionPolicy,
    PaperExecutionService,
)


NOW = datetime(2026, 8, 19, 14, 0, tzinfo=timezone.utc)


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


def _account(session: Session, capital: Decimal = Decimal("1000")) -> Account:
    agent = Agent(
        nombre="PAPER",
        presupuesto_inicial=float(capital),
        presupuesto_actual=float(capital),
        estrategia=StrategyEnum.S1,
    )
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return AccountingService(session).create_account(agent.id, capital)


def _quote(price: str = "100", *, observed_at: datetime = NOW) -> Quote:
    return Quote(
        symbol="BTC/USDT",
        price=Decimal(price),
        observed_at=observed_at,
        received_at=observed_at + timedelta(milliseconds=100),
        provider="fixture_real",
        provider_symbol="BTCUSDT",
        timestamp_source="provider",
    )


def test_market_buy_uses_deterministic_slippage_fee_and_accounting(engine):
    with Session(engine) as session:
        account = _account(session)
        service = PaperExecutionService(
            session,
            policy=PaperExecutionPolicy(slippage_bps=Decimal("10"), fee_bps=Decimal("10")),
            clock=lambda: NOW,
        )

        result = service.execute_market_order(
            account_id=account.id,
            symbol="BTC/USDT",
            side="BUY",
            quantity=Decimal("2"),
            quote=_quote(),
            origin="operator",
        )

        session.refresh(account)
        order = session.get(Order, result.order_id)
        fill = session.get(Fill, result.fill_id)
        execution = session.exec(select(PaperExecution)).one()
        position = session.exec(select(Position)).one()

        assert result.market_price == Decimal("100")
        assert result.fill_price == Decimal("100.1")
        assert result.fee == Decimal("0.2002")
        assert order.status == "FILLED"
        assert fill.evidence_mode == "paper"
        assert fill.price == Decimal("100.1")
        assert account.cash == Decimal("799.5998")
        assert position.quantity == Decimal("2")
        assert position.average_cost == Decimal("100.2001")
        assert execution.provider == "fixture_real"
        assert execution.quote_observed_at == NOW
        assert execution.policy_version == "paper-v1"
        assert execution.status == "FILLED"
        assert execution.origin == "operator"


def test_market_sell_uses_adverse_slippage_and_realizes_net_pnl(engine):
    with Session(engine) as session:
        account = _account(session)
        accounting = AccountingService(session)
        buy = accounting.create_order(account.id, "BTC/USDT", "BUY", Decimal("1"))
        accounting.apply_fill(
            buy.id,
            quantity=Decimal("1"),
            price=Decimal("100"),
            fee=Decimal("0"),
            observed_at=NOW - timedelta(minutes=1),
        )
        service = PaperExecutionService(
            session,
            policy=PaperExecutionPolicy(slippage_bps=Decimal("10"), fee_bps=Decimal("10")),
            clock=lambda: NOW,
        )

        result = service.execute_market_order(
            account_id=account.id,
            symbol="BTC/USDT",
            side="SELL",
            quantity=Decimal("1"),
            quote=_quote("120"),
            origin="operator",
        )

        session.refresh(account)
        position = session.exec(select(Position)).one()
        assert result.fill_price == Decimal("119.88")
        assert result.fee == Decimal("0.11988")
        assert account.realized_pnl == Decimal("19.76012")
        assert account.cash == Decimal("1019.76012")
        assert position.quantity == Decimal("0")


def test_execution_rejects_non_real_or_stale_quote_before_creating_financial_records(engine):
    with Session(engine) as session:
        account = _account(session)
        service = PaperExecutionService(session, clock=lambda: NOW)
        stale = _quote(observed_at=NOW - timedelta(seconds=31))

        with pytest.raises(PaperExecutionError, match="stale"):
            service.execute_market_order(
                account_id=account.id,
                symbol="BTC/USDT",
                side="BUY",
                quantity=Decimal("1"),
                quote=stale,
                origin="operator",
            )

        assert session.exec(select(Order)).all() == []
        assert session.exec(select(Fill)).all() == []
        assert session.exec(select(PaperExecution)).all() == []


def test_execution_rejects_quote_symbol_mismatch(engine):
    with Session(engine) as session:
        account = _account(session)
        service = PaperExecutionService(session, clock=lambda: NOW)

        with pytest.raises(PaperExecutionError, match="symbol"):
            service.execute_market_order(
                account_id=account.id,
                symbol="ETH/USDT",
                side="BUY",
                quantity=Decimal("1"),
                quote=_quote(),
                origin="operator",
            )


def test_accounting_failure_is_persisted_as_rejected_without_fill(engine):
    with Session(engine) as session:
        account = _account(session, Decimal("50"))
        service = PaperExecutionService(session, clock=lambda: NOW)

        with pytest.raises(PaperExecutionError, match="insufficient cash"):
            service.execute_market_order(
                account_id=account.id,
                symbol="BTC/USDT",
                side="BUY",
                quantity=Decimal("1"),
                quote=_quote("100"),
                origin="operator",
            )

        executions = session.exec(select(PaperExecution)).all()
        orders = session.exec(select(Order)).all()
        assert len(executions) == 1
        assert executions[0].status == "REJECTED"
        assert "insufficient cash" in executions[0].rejection_reason
        assert len(orders) == 1
        assert orders[0].status == "CANCELLED"
        assert session.exec(select(Fill)).all() == []


def test_persisted_execution_and_accounting_survive_session_reload(engine):
    with Session(engine) as session:
        account = _account(session)
        service = PaperExecutionService(session, clock=lambda: NOW)
        result = service.execute_market_order(
            account_id=account.id,
            symbol="BTC/USDT",
            side="BUY",
            quantity=Decimal("1"),
            quote=_quote(),
            origin="operator",
        )
        account_id = account.id
        execution_id = result.execution_id

    with Session(engine) as session:
        execution = session.get(PaperExecution, execution_id)
        assert execution.status == "FILLED"
        assert execution.order_id is not None
        assert execution.fill_id is not None
        report = AccountingService(session).reconcile(
            account_id, {"BTC/USDT": Decimal("100")}
        )
        assert report.ok is True


def test_recovery_links_fill_if_crash_happened_after_accounting_commit(engine):
    with Session(engine) as session:
        account = _account(session)
        accounting = AccountingService(session)
        order = accounting.create_order(account.id, "BTC/USDT", "BUY", Decimal("1"))
        execution = PaperExecution(
            account_id=account.id,
            agent_id=account.agente_id,
            order_id=order.id,
            symbol="BTC/USDT",
            side="BUY",
            requested_quantity=Decimal("1"),
            origin="operator",
            policy_version="paper-v1",
            provider="fixture_real",
            provider_symbol="BTCUSDT",
            quote_observed_at=NOW,
            quote_received_at=NOW,
            market_price=Decimal("100"),
            fill_price=Decimal("100.1"),
            slippage_bps=Decimal("10"),
            fee_bps=Decimal("10"),
            fee=Decimal("0.1001"),
            status="PENDING",
        )
        session.add(execution)
        session.commit()
        session.refresh(execution)
        fill = accounting.apply_fill(
            order.id,
            quantity=Decimal("1"),
            price=Decimal("100.1"),
            fee=Decimal("0.1001"),
            observed_at=NOW,
        )
        execution_id = execution.id
        fill_id = fill.id

    with Session(engine) as session:
        recovered = PaperExecutionService(session, clock=lambda: NOW).recover_pending()
        execution = session.get(PaperExecution, execution_id)
        assert recovered == {"filled": 1, "cancelled": 0}
        assert execution.status == "FILLED"
        assert execution.fill_id == fill_id


def test_recovery_cancels_unfilled_pending_order_instead_of_reexecuting(engine):
    with Session(engine) as session:
        account = _account(session)
        order = AccountingService(session).create_order(
            account.id, "BTC/USDT", "BUY", Decimal("1")
        )
        execution = PaperExecution(
            account_id=account.id,
            agent_id=account.agente_id,
            order_id=order.id,
            symbol="BTC/USDT",
            side="BUY",
            requested_quantity=Decimal("1"),
            origin="operator",
            policy_version="paper-v1",
            provider="fixture_real",
            provider_symbol="BTCUSDT",
            quote_observed_at=NOW,
            quote_received_at=NOW,
            market_price=Decimal("100"),
            fill_price=Decimal("100.1"),
            slippage_bps=Decimal("10"),
            fee_bps=Decimal("10"),
            fee=Decimal("0.1001"),
            status="PENDING",
        )
        session.add(execution)
        session.commit()
        execution_id = execution.id
        order_id = order.id

    with Session(engine) as session:
        recovered = PaperExecutionService(session, clock=lambda: NOW).recover_pending()
        execution = session.get(PaperExecution, execution_id)
        order = session.get(Order, order_id)
        assert recovered == {"filled": 0, "cancelled": 1}
        assert execution.status == "CANCELLED"
        assert execution.rejection_reason == "recovered_unfilled_after_restart"
        assert order.status == "CANCELLED"
        assert session.exec(select(Fill)).all() == []
