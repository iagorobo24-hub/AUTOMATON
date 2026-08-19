from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.accounting.service import AccountingService
from app.models import Agent, StrategyEnum
from app.models.paper_execution import PaperExecution, PaperRequest
from app.paper_execution.service import PaperExecutionService


NOW = datetime(2026, 8, 19, 14, 0, tzinfo=timezone.utc)


def _engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def _account(session: Session):
    agent = Agent(
        nombre="REQUEST-RECOVERY",
        presupuesto_inicial=1000,
        presupuesto_actual=1000,
        estrategia=StrategyEnum.S1,
    )
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return AccountingService(session).create_account(agent.id, Decimal("1000"))


def test_processing_request_without_execution_requires_manual_recovery_after_restart():
    engine = _engine()
    with Session(engine) as session:
        account = _account(session)
        request = PaperRequest(
            request_id="crash-before-execution",
            request_fingerprint="a" * 64,
            account_id=account.id,
            status="PROCESSING",
        )
        session.add(request)
        session.commit()
        request_id = request.id

    with Session(engine) as session:
        recovered = PaperExecutionService(session, clock=lambda: NOW).recover_requests()
        request = session.get(PaperRequest, request_id)
        assert recovered == {"completed": 0, "recovery_required": 1}
        assert request.status == "RECOVERY_REQUIRED"
        assert request.http_status == 409
        assert request.error_detail == "request interrupted before execution linkage; automatic retry blocked"


def test_processing_request_linked_to_filled_execution_becomes_completed():
    engine = _engine()
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
            status="FILLED",
        )
        session.add(execution)
        session.flush()
        request = PaperRequest(
            request_id="crash-after-execution",
            request_fingerprint="b" * 64,
            account_id=account.id,
            execution_id=execution.id,
            status="PROCESSING",
        )
        session.add(request)
        session.commit()
        request_id = request.id

    with Session(engine) as session:
        recovered = PaperExecutionService(session, clock=lambda: NOW).recover_requests()
        request = session.get(PaperRequest, request_id)
        assert recovered == {"completed": 1, "recovery_required": 0}
        assert request.status == "COMPLETED"
        assert request.http_status == 200
        assert request.error_detail is None
