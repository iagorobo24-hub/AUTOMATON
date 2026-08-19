from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.accounting.service import AccountingService
from app.market_data.contracts import Quote
from app.models import Agent, AgentStatus, StrategyEnum
from app.risk.bootstrap import ensure_active_risk_profile
from app.risk.service import RiskService

NOW = datetime(2026, 8, 19, 17, 0, tzinfo=timezone.utc)


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _quote(price="100", observed_at=NOW):
    return Quote(symbol="BTC/USDT", price=Decimal(price), observed_at=observed_at,
                 received_at=observed_at, provider="fixture_real", provider_symbol="BTCUSDT",
                 timestamp_source="provider")


def _account(session, capital="1000"):
    agent = Agent(nombre="RISK", presupuesto_inicial=float(capital), presupuesto_actual=float(capital), estrategia=StrategyEnum.S1)
    session.add(agent); session.commit(); session.refresh(agent)
    account = AccountingService(session).create_account(agent.id, Decimal(capital))
    return agent, account


def test_risk_allows_buy_inside_risk_v1_limits_and_persists_decision():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _agent, account = _account(session)
        profile = ensure_active_risk_profile(session)
        decision = RiskService(session, clock=lambda: NOW).evaluate(
            account_id=account.id, symbol="BTC/USDT", side="BUY", quantity=Decimal("1"),
            quote=_quote(), market_prices={"BTC/USDT": Decimal("100")}, profile=profile,
        )
        assert decision.decision == "ALLOW"
        assert decision.reason_code == "ALLOW"
        assert decision.profile_version == "risk-v1"
        assert decision.requested_notional == Decimal("100")


def test_risk_rejects_order_notional_and_stale_quote():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _agent, account = _account(session)
        service = RiskService(session, clock=lambda: NOW)
        profile = ensure_active_risk_profile(session)
        too_large = service.evaluate(account_id=account.id, symbol="BTC/USDT", side="BUY",
            quantity=Decimal("3"), quote=_quote(), market_prices={"BTC/USDT": Decimal("100")}, profile=profile)
        assert too_large.decision == "REJECT"
        assert too_large.reason_code == "MAX_ORDER_NOTIONAL"
        stale = service.evaluate(account_id=account.id, symbol="BTC/USDT", side="BUY",
            quantity=Decimal("1"), quote=_quote(observed_at=NOW-timedelta(seconds=31)),
            market_prices={"BTC/USDT": Decimal("100")}, profile=profile)
        assert stale.decision == "REJECT"
        assert stale.reason_code == "STALE_MARKET_DATA"


def test_paused_or_inactive_agent_fails_closed():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent, account = _account(session)
        profile = ensure_active_risk_profile(session)
        profile.paused = True; session.add(profile); session.commit()
        decision = RiskService(session, clock=lambda: NOW).evaluate(account_id=account.id,
            symbol="BTC/USDT", side="BUY", quantity=Decimal("1"), quote=_quote(),
            market_prices={"BTC/USDT": Decimal("100")}, profile=profile)
        assert decision.reason_code == "RISK_PAUSED"
        profile.paused = False; agent.estado = AgentStatus.MUERTO; session.add_all([profile, agent]); session.commit()
        decision = RiskService(session, clock=lambda: NOW).evaluate(account_id=account.id,
            symbol="BTC/USDT", side="BUY", quantity=Decimal("1"), quote=_quote(),
            market_prices={"BTC/USDT": Decimal("100")}, profile=profile)
        assert decision.reason_code == "AGENT_INACTIVE"
