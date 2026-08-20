from decimal import Decimal, ROUND_DOWN

from app.live_execution.adapter import SymbolRules
from app.models.live_execution import LivePolicy


def _is_multiple(value: Decimal, increment: Decimal) -> bool:
    if increment <= 0:
        return False
    return value % increment == 0


def normalize_quantity_down(quantity: Decimal, step_size: Decimal) -> Decimal:
    """Normalize to venue step size without ever increasing requested exposure."""
    if quantity <= 0:
        return Decimal("0")
    if step_size <= 0:
        raise ValueError("step_size must be positive")
    steps = (quantity / step_size).to_integral_value(rounding=ROUND_DOWN)
    return steps * step_size


def validate_live_policy(policy: LivePolicy) -> list[str]:
    reasons: list[str] = []
    if not policy.active:
        reasons.append("INACTIVE_LIVE_POLICY")
    money_limits = (
        policy.max_deployable_capital,
        policy.max_order_notional,
        policy.max_symbol_exposure,
        policy.max_portfolio_exposure,
        policy.max_session_loss,
    )
    if any(value <= 0 for value in money_limits):
        reasons.append("INVALID_LIVE_MONEY_LIMITS")
    if not (Decimal("0") < policy.max_drawdown <= Decimal("1")):
        reasons.append("INVALID_LIVE_DRAWDOWN_LIMIT")
    if policy.max_consecutive_execution_errors <= 0:
        reasons.append("INVALID_EXECUTION_ERROR_LIMIT")
    if policy.stale_market_data_seconds <= 0:
        reasons.append("INVALID_STALE_DATA_LIMIT")
    if not (Decimal("0") < policy.rollout_capital_fraction <= Decimal("1")):
        reasons.append("INVALID_ROLLOUT_FRACTION")
    if policy.max_order_notional > policy.max_deployable_capital:
        reasons.append("ORDER_LIMIT_EXCEEDS_DEPLOYABLE_CAPITAL")
    if policy.max_symbol_exposure > policy.max_portfolio_exposure:
        reasons.append("SYMBOL_LIMIT_EXCEEDS_PORTFOLIO_LIMIT")
    return reasons


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
    reasons = validate_live_policy(policy)
    if rules is None:
        reasons.append("SYMBOL_RULES_UNAVAILABLE")
        return reasons
    if quantity <= 0 or reference_price <= 0:
        reasons.append("INVALID_QUANTITY_OR_PRICE")
        return reasons
    if projected_symbol_exposure < 0 or projected_portfolio_exposure < 0:
        reasons.append("INVALID_PROJECTED_EXPOSURE")
    if deployable_capital < 0:
        reasons.append("INVALID_DEPLOYABLE_CAPITAL")
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
    rollout_capital_ceiling = policy.max_deployable_capital * policy.rollout_capital_fraction
    if deployable_capital > rollout_capital_ceiling:
        reasons.append("ROLLOUT_CAPITAL_FRACTION_EXCEEDED")
    return reasons


def validate_limit_price(*, price: Decimal, rules: SymbolRules | None) -> list[str]:
    if rules is None:
        return ["SYMBOL_RULES_UNAVAILABLE"]
    if price <= 0:
        return ["INVALID_PRICE"]
    if not _is_multiple(price, rules.tick_size):
        return ["TICK_SIZE_VIOLATION"]
    return []
