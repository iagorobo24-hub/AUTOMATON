from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.accounting.service import AccountingService
from app.market_data.contracts import Quote
from app.models import Agent, AgentStatus, StrategyEnum
from app.paper_execution.service import PaperExecutionError, PaperExecutionService


NOW = datetime(2026, 8, 19, 14, 0, tzinfo=timezone.utc)


def _quote(symbol: str) -> Quote:
    return Quote(
        symbol=symbol,
        price=Decimal("100"),
        observed_at=NOW,
        received_at=NOW,
        provider="fixture_real",
        provider_symbol=symbol.replace("/", ""),
        timestamp_source="provider",
    )


def _engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def test_paper_execution_requires_symbol_quote_currency_to_match_account_currency():
    engine = _engine()
    with Session(engine) as session:
        agent = Agent(
            nombre="CURRENCY",
            presupuesto_inicial=1000,
            presupuesto_actual=1000,
            estrategia=StrategyEnum.S1,
        )
        session.add(agent)
        session.commit()
        session.refresh(agent)
        account = AccountingService(session).create_account(agent.id, Decimal("1000"))

        with pytest.raises(PaperExecutionError, match="account currency"):
            PaperExecutionService(session, clock=lambda: NOW).execute_market_order(
                account_id=account.id,
                symbol="ETH/BTC",
                side="BUY",
                quantity=Decimal("1"),
                quote=_quote("ETH/BTC"),
            )


def test_dead_agent_account_cannot_execute_new_paper_orders():
    engine = _engine()
    with Session(engine) as session:
        agent = Agent(
            nombre="DEAD",
            presupuesto_inicial=1000,
            presupuesto_actual=1000,
            estrategia=StrategyEnum.S1,
            estado=AgentStatus.MUERTO,
        )
        session.add(agent)
        session.commit()
        session.refresh(agent)
        account = AccountingService(session).create_account(agent.id, Decimal("1000"))

        with pytest.raises(PaperExecutionError, match="active agent"):
            PaperExecutionService(session, clock=lambda: NOW).execute_market_order(
                account_id=account.id,
                symbol="BTC/USDT",
                side="BUY",
                quantity=Decimal("1"),
                quote=_quote("BTC/USDT"),
            )
