from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.accounting.service import AccountingService
from app.market_data.contracts import Quote
from app.models import Agent, StrategyEnum
from app.models.paper_execution import PaperExecution
from app.paper_execution.service import PaperExecutionError, PaperExecutionService


NOW = datetime(2026, 8, 19, 14, 0, tzinfo=timezone.utc)


def test_unresolved_recovery_state_blocks_new_paper_orders():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent = Agent(
            nombre="RECOVERY",
            presupuesto_inicial=1000,
            presupuesto_actual=1000,
            estrategia=StrategyEnum.S1,
        )
        session.add(agent)
        session.commit()
        session.refresh(agent)
        account = AccountingService(session).create_account(agent.id, Decimal("1000"))
        order = AccountingService(session).create_order(
            account.id, "BTC/USDT", "BUY", Decimal("1")
        )
        session.add(
            PaperExecution(
                account_id=account.id,
                agent_id=agent.id,
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
                status="RECOVERY_REQUIRED",
                rejection_reason="ambiguous_partial_accounting_state",
            )
        )
        session.commit()

        quote = Quote(
            symbol="BTC/USDT",
            price=Decimal("100"),
            observed_at=NOW,
            received_at=NOW,
            provider="fixture_real",
            provider_symbol="BTCUSDT",
            timestamp_source="provider",
        )
        with pytest.raises(PaperExecutionError, match="recovery"):
            PaperExecutionService(session, clock=lambda: NOW).execute_market_order(
                account_id=account.id,
                symbol="BTC/USDT",
                side="BUY",
                quantity=Decimal("1"),
                quote=quote,
                origin="operator",
            )
