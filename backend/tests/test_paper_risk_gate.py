from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.accounting.service import AccountingService
from app.market_data.contracts import Quote
from app.models import Agent, StrategyEnum
from app.models.accounting import Fill, Order
from app.models.paper_execution import PaperRequest
from app.models.risk import RiskDecision, RiskProfile
from app.paper_execution.service import PaperExecutionError, PaperExecutionService
from app.risk.bootstrap import ensure_active_risk_profile
from app.risk.service import RiskService

NOW = datetime(2026, 8, 19, 17, 0, tzinfo=timezone.utc)


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _quote():
    return Quote(symbol="BTC/USDT", price=Decimal("100"), observed_at=NOW, received_at=NOW,
                 provider="fixture_real", provider_symbol="BTCUSDT", timestamp_source="provider")


def _account(session):
    agent = Agent(nombre="PAPER-RISK", presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=StrategyEnum.S1)
    session.add(agent); session.commit(); session.refresh(agent)
    return AccountingService(session).create_account(agent.id, Decimal("1000"))


def _allow(session, account_id):
    profile = ensure_active_risk_profile(session)
    return RiskService(session, clock=lambda: NOW).evaluate(account_id=account_id, symbol="BTC/USDT",
        side="BUY", quantity=Decimal("1"), quote=_quote(),
        market_prices={"BTC/USDT": Decimal("100")}, profile=profile)


def test_risk_approved_execution_consumes_decision_once():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        account = _account(session)
        decision = _allow(session, account.id)
        service = PaperExecutionService(session, clock=lambda: NOW)
        result = service.execute_market_order(account_id=account.id, symbol="BTC/USDT", side="BUY",
            quantity=Decimal("1"), quote=_quote(), origin="operator", risk_decision=decision)
        session.refresh(decision)
        assert result.fill_id is not None
        assert decision.consumed_at is not None
        assert decision.paper_execution_id == result.execution_id
        assert len(session.exec(select(Fill)).all()) == 1
        with pytest.raises(PaperExecutionError, match="consumed"):
            service.execute_market_order(account_id=account.id, symbol="BTC/USDT", side="BUY",
                quantity=Decimal("1"), quote=_quote(), origin="operator", risk_decision=decision)


def test_rejected_or_mismatched_risk_decision_cannot_execute():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        account = _account(session)
        profile = ensure_active_risk_profile(session)
        rejected = RiskService(session, clock=lambda: NOW).evaluate(account_id=account.id, symbol="BTC/USDT",
            side="BUY", quantity=Decimal("3"), quote=_quote(), market_prices={"BTC/USDT": Decimal("100")}, profile=profile)
        service = PaperExecutionService(session, clock=lambda: NOW)
        with pytest.raises(PaperExecutionError, match="ALLOW"):
            service.execute_market_order(account_id=account.id, symbol="BTC/USDT", side="BUY",
                quantity=Decimal("3"), quote=_quote(), origin="operator", risk_decision=rejected)
        allowed = _allow(session, account.id)
        with pytest.raises(PaperExecutionError, match="match"):
            service.execute_market_order(account_id=account.id, symbol="BTC/USDT", side="BUY",
                quantity=Decimal("2"), quote=_quote(), origin="operator", risk_decision=allowed)


def test_paper_execution_cannot_bypass_risk():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        account = _account(session)
        request = PaperRequest(
            request_id="no-risk-bypass",
            request_fingerprint="a" * 64,
            account_id=account.id,
            status="PROCESSING",
        )
        session.add(request); session.commit(); session.refresh(request)

        with pytest.raises(PaperExecutionError, match="Risk authorization"):
            PaperExecutionService(session, clock=lambda: NOW).execute_market_order(
                account_id=account.id,
                symbol="BTC/USDT",
                side="BUY",
                quantity=Decimal("1"),
                quote=_quote(),
                origin="operator",
                request=request,
                risk_decision=None,
            )

        assert session.exec(select(Order)).all() == []
        assert session.exec(select(Fill)).all() == []


def test_pause_after_allow_invalidates_unconsumed_risk_authorization():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        account = _account(session)
        decision = _allow(session, account.id)
        profile = session.get(RiskProfile, decision.profile_id)
        profile.paused = True
        session.add(profile)
        session.commit()

        with pytest.raises(PaperExecutionError, match="no longer active"):
            PaperExecutionService(session, clock=lambda: NOW).execute_market_order(
                account_id=account.id,
                symbol="BTC/USDT",
                side="BUY",
                quantity=Decimal("1"),
                quote=_quote(),
                origin="operator",
                risk_decision=decision,
            )

        session.refresh(decision)
        assert decision.consumed_at is None
        assert decision.paper_execution_id is None
        assert session.exec(select(Order)).all() == []
        assert session.exec(select(Fill)).all() == []
