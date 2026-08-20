from decimal import Decimal

from app.live_execution.adapter import SymbolRules
from app.models.live_execution import LivePolicy


def _is_multiple(value: Decimal, increment: Decimal) -> bool:
    if increment <= 0:
        return False
    return value % increment == 0


def validate_live_intent_rules(
    *,
    policy: LivePolicy,
    rules: SymbolRules | None,
    quantity: Decimal,
    reference_price: Decimal,
    projected_symbol_exposure: Decimal,
    projected_portfolio_exposure: Decimal,
    deployable_capital: Decimal,
) -> list[str]:
    reasons: list[str] = []
    if rules is None:
        reasons.append("SYMBOL_RULES_UNAVAILABLE")
        return reasons
    if quantity <= 0 or reference_price <= 0:
        reasons.append("INVALID_QUANTITY_OR_PRICE")
        return reasons
    if not _is_multiple(quantity, rules.step_size):
        reasons.append("STEP_SIZE_VIOLATION")
    notional = quantity * reference_price
    if notional < rules.min_notional:
        reasons.append("MIN_NOTIONAL_VIOLATION")
    if notional > policy.max_order_notional:
        reasons.append("MAX_ORDER_NOTIONAL_EXCEEDED")
    if projected_symbol_exposure > policy.max_symbol_exposure:
        reasons.append("MAX_SYMBOL_EXPOSURE_EXCEEDED")
    if projected_portfolio_exposure > policy.max_portfolio_exposure:
        reasons.append("MAX_PORTFOLIO_EXPOSURE_EXCEEDED")
    if deployable_capital > policy.max_deployable_capital:
        reasons.append("MAX_DEPLOYABLE_CAPITAL_EXCEEDED")
    return reasons


def validate_limit_price(*, price: Decimal, rules: SymbolRules | None) -> list[str]:
    if rules is None:
        return ["SYMBOL_RULES_UNAVAILABLE"]
    if price <= 0:
        return ["INVALID_PRICE"]
    if not _is_multiple(price, rules.tick_size):
        return ["TICK_SIZE_VIOLATION"]
    return []
