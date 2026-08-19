from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.accounting.service import AccountingService
from app.market_data.contracts import Quote
from app.models import Agent, StrategyEnum
from app.risk.bootstrap import ensure_active_risk_profile
from app.risk.service import RiskService

NOW = datetime(2026, 8, 19, 17, 0, tzinfo=timezone.utc)


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _quote(symbol="BTC/USDT", price="100"):
    return Quote(symbol=symbol, price=Decimal(price), observed_at=NOW, received_at=NOW,
                 provider="fixture_real", provider_symbol=symbol.replace("/", ""), timestamp_source="provider")


def _setup(session):
    agent = Agent(nombre="LIMITS", presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=StrategyEnum.S1)
    session.add(agent); session.commit(); session.refresh(agent)
    account = AccountingService(session).create_account(agent.id, Decimal("1000"))
    profile = ensure_active_risk_profile(session)
    return account, profile


def _buy(session, account_id, symbol, quantity, price="100"):
    accounting = AccountingService(session)
    order = accounting.create_order(account_id, symbol, "BUY", Decimal(quantity))
    accounting.apply_fill(order.id, quantity=Decimal(quantity), price=Decimal(price), fee=Decimal("0"), observed_at=NOW)


def test_total_exposure_and_symbol_concentration_are_independent_limits():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        account, profile = _setup(session)
        _buy(session, account.id, "BTC/USDT", "4")
        service = RiskService(session, clock=lambda: NOW)
        total = service.evaluate(account_id=account.id, symbol="BTC/USDT", side="BUY", quantity=Decimal("2.1"),
            quote=_quote(), market_prices={"BTC/USDT": Decimal("100")}, profile=profile)
        assert total.reason_code == "MAX_TOTAL_EXPOSURE"
        concentration = service.evaluate(account_id=account.id, symbol="BTC/USDT", side="BUY", quantity=Decimal("1"),
            quote=_quote(), market_prices={"BTC/USDT": Decimal("100")}, profile=profile)
        assert concentration.reason_code == "MAX_SYMBOL_EXPOSURE"


def test_max_open_positions_is_enforced_after_other_exposure_checks_pass():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        account, profile = _setup(session)
        profile.max_open_positions = 1; session.add(profile); session.commit()
        _buy(session, account.id, "BTC/USDT", "1")
        decision = RiskService(session, clock=lambda: NOW).evaluate(
            account_id=account.id, symbol="ETH/USDT", side="BUY", quantity=Decimal("1"), quote=_quote("ETH/USDT"),
            market_prices={"BTC/USDT": Decimal("100"), "ETH/USDT": Decimal("100")}, profile=profile)
        assert decision.reason_code == "MAX_OPEN_POSITIONS"


def test_realized_loss_and_drawdown_fail_closed_for_new_buys():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        account, profile = _setup(session)
        account.realized_pnl = Decimal("-101"); account.cash = Decimal("899"); session.add(account); session.commit()
        loss = RiskService(session, clock=lambda: NOW).evaluate(account_id=account.id, symbol="BTC/USDT", side="BUY",
            quantity=Decimal("1"), quote=_quote(), market_prices={"BTC/USDT": Decimal("100")}, profile=profile)
        assert loss.reason_code == "MAX_REALIZED_LOSS"

        profile.max_realized_loss_pct = Decimal("1"); session.add(profile)
        account.realized_pnl = Decimal("-160"); account.cash = Decimal("840"); session.add(account); session.commit()
        drawdown = RiskService(session, clock=lambda: NOW).evaluate(account_id=account.id, symbol="BTC/USDT", side="BUY",
            quantity=Decimal("1"), quote=_quote(), market_prices={"BTC/USDT": Decimal("100")}, profile=profile)
        assert drawdown.reason_code == "MAX_DRAWDOWN"


def test_sell_reducing_existing_long_bypasses_size_and_loss_caps_but_not_integrity():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        account, profile = _setup(session)
        _buy(session, account.id, "BTC/USDT", "3")
        profile.max_order_notional = Decimal("1")
        profile.max_order_equity_pct = Decimal("0.001")
        profile.max_total_exposure_pct = Decimal("0.01")
        profile.max_symbol_exposure_pct = Decimal("0.01")
        session.add(profile); session.commit()
        decision = RiskService(session, clock=lambda: NOW).evaluate(account_id=account.id, symbol="BTC/USDT", side="SELL",
            quantity=Decimal("1"), quote=_quote(), market_prices={"BTC/USDT": Decimal("100")}, profile=profile)
        assert decision.decision == "ALLOW"
        oversell = RiskService(session, clock=lambda: NOW).evaluate(account_id=account.id, symbol="BTC/USDT", side="SELL",
            quantity=Decimal("4"), quote=_quote(), market_prices={"BTC/USDT": Decimal("100")}, profile=profile)
        assert oversell.reason_code == "OVERSELL"


def test_buy_cash_reserve_matches_compounded_paper_v1_slippage_and_fee():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        account, profile = _setup(session)
        account.initial_capital = Decimal("100.2")
        account.funded_capital = Decimal("100.2")
        account.cash = Decimal("100.2")
        session.add(account)
        profile.max_order_notional = Decimal("1000")
        profile.max_order_equity_pct = Decimal("2")
        profile.max_total_exposure_pct = Decimal("2")
        profile.max_symbol_exposure_pct = Decimal("2")
        session.add(profile)
        session.commit()

        decision = RiskService(session, clock=lambda: NOW).evaluate(
            account_id=account.id,
            symbol="BTC/USDT",
            side="BUY",
            quantity=Decimal("1"),
            quote=_quote(),
            market_prices={"BTC/USDT": Decimal("100")},
            profile=profile,
        )
        assert decision.reason_code == "INSUFFICIENT_CASH_RESERVE"
