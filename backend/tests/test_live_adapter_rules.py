from decimal import Decimal

from app.live_execution.adapter import DisabledLiveAdapter, SymbolRules
from app.live_execution.rules import validate_limit_price, validate_live_intent_rules
from app.models.live_execution import LivePolicy


def _policy():
    return LivePolicy(
        version="live-v1",
        max_deployable_capital=Decimal("100"),
        max_order_notional=Decimal("25"),
        max_symbol_exposure=Decimal("50"),
        max_portfolio_exposure=Decimal("100"),
        max_session_loss=Decimal("5"),
        max_drawdown=Decimal("0.05"),
        rollout_capital_fraction=Decimal("0.10"),
    )


def test_disabled_adapter_is_read_only_and_cannot_trade():
    adapter = DisabledLiveAdapter()
    caps = adapter.capabilities()
    assert caps.trading_enabled is False
    assert caps.credentials_present is False
    assert caps.withdrawals_enabled is False
    assert caps.trade_permission is False
    assert not hasattr(adapter, "create_order")
    assert not hasattr(adapter, "place_order")
    assert not hasattr(adapter, "submit_order")


def test_live_rules_enforce_venue_and_policy_limits():
    rules = SymbolRules("BTC/USDT", Decimal("0.001"), Decimal("0.10"), Decimal("10"))
    reasons = validate_live_intent_rules(
        policy=_policy(), rules=rules, quantity=Decimal("0.0035"), reference_price=Decimal("10000"),
        projected_symbol_exposure=Decimal("60"), projected_portfolio_exposure=Decimal("110"),
        deployable_capital=Decimal("101"),
    )
    assert "STEP_SIZE_VIOLATION" in reasons
    assert "MAX_ORDER_NOTIONAL_EXCEEDED" in reasons
    assert "MAX_SYMBOL_EXPOSURE_EXCEEDED" in reasons
    assert "MAX_PORTFOLIO_EXPOSURE_EXCEEDED" in reasons
    assert "MAX_DEPLOYABLE_CAPITAL_EXCEEDED" in reasons


def test_tick_size_is_validated_for_limit_price_contract():
    rules = SymbolRules("BTC/USDT", Decimal("0.001"), Decimal("0.10"), Decimal("10"))
    assert validate_limit_price(price=Decimal("100.05"), rules=rules) == ["TICK_SIZE_VIOLATION"]
    assert validate_limit_price(price=Decimal("100.10"), rules=rules) == []
