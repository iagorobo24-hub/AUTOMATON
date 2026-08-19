from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

ZERO = Decimal("0")
ONE = Decimal("1")
BPS = Decimal("10000")


class BacktestExecutionError(ValueError):
    pass


@dataclass(frozen=True)
class BacktestExecutionPolicy:
    slippage_bps: Decimal = Decimal("10")
    fee_bps: Decimal = Decimal("10")
    position_fraction: Decimal = Decimal("0.25")
    version: str = "backtest-v1"

    def __post_init__(self):
        if Decimal(self.slippage_bps) < ZERO:
            raise ValueError("slippage_bps cannot be negative")
        if Decimal(self.fee_bps) < ZERO:
            raise ValueError("fee_bps cannot be negative")
        if not ZERO < Decimal(self.position_fraction) <= ONE:
            raise ValueError("position_fraction must be in (0, 1]")
        if not self.version.strip():
            raise ValueError("execution policy version is required")


@dataclass(frozen=True)
class BacktestFill:
    side: str
    symbol: str
    quantity: Decimal
    market_price: Decimal
    fill_price: Decimal
    fee: Decimal
    observed_at: datetime
    realized_pnl: Decimal = ZERO
    exit_reason: str | None = None


@dataclass(frozen=True)
class BacktestMark:
    cash: Decimal
    market_value: Decimal
    equity: Decimal
    exposure: Decimal


class BacktestLedger:
    """Isolated long-only accounting for historical evidence.

    It mirrors active Accounting invariants without creating active Account,
    Order, Fill or Position rows.
    """

    def __init__(self, *, initial_capital: Decimal):
        initial = Decimal(initial_capital)
        if initial <= ZERO:
            raise BacktestExecutionError("initial_capital must be positive")
        self.initial_capital = initial
        self.cash = initial
        self.position_symbol: str | None = None
        self.position_quantity = ZERO
        self.average_cost = ZERO
        self.realized_pnl = ZERO
        self.fees_paid = ZERO

    @staticmethod
    def _price(value: Decimal) -> Decimal:
        value = Decimal(value)
        if value <= ZERO:
            raise BacktestExecutionError("market_price must be positive")
        return value

    @staticmethod
    def _time(value: datetime) -> datetime:
        if value.tzinfo is None:
            raise BacktestExecutionError("observed_at must be timezone-aware")
        return value.astimezone(timezone.utc)

    @staticmethod
    def _fill_price(side: str, market_price: Decimal, policy: BacktestExecutionPolicy) -> Decimal:
        slip = Decimal(policy.slippage_bps) / BPS
        if side == "BUY":
            return market_price * (ONE + slip)
        return market_price * (ONE - slip)

    def equity(self, market_price: Decimal) -> Decimal:
        price = self._price(market_price)
        return self.cash + self.position_quantity * price

    def mark(self, market_price: Decimal) -> BacktestMark:
        price = self._price(market_price)
        market_value = self.position_quantity * price
        return BacktestMark(
            cash=self.cash,
            market_value=market_value,
            equity=self.cash + market_value,
            exposure=market_value,
        )

    def buy(
        self,
        *,
        symbol: str,
        market_price: Decimal,
        observed_at: datetime,
        policy: BacktestExecutionPolicy,
    ) -> BacktestFill:
        if self.position_quantity > ZERO:
            raise BacktestExecutionError("backtest-v1 is already long; pyramiding is disabled")
        price = self._price(market_price)
        observed = self._time(observed_at)
        canonical = symbol.strip().upper()
        if "/" not in canonical:
            raise BacktestExecutionError("symbol must use BASE/QUOTE format")

        fill_price = self._fill_price("BUY", price, policy)
        fee_rate = Decimal(policy.fee_bps) / BPS
        allocation = self.cash * Decimal(policy.position_fraction)
        quantity = allocation / (fill_price * (ONE + fee_rate))
        if quantity <= ZERO:
            raise BacktestExecutionError("calculated buy quantity is not positive")
        fee = quantity * fill_price * fee_rate
        total_cost = quantity * fill_price + fee
        if total_cost > self.cash:
            raise BacktestExecutionError("insufficient backtest cash")

        self.cash -= total_cost
        self.position_symbol = canonical
        self.position_quantity = quantity
        self.average_cost = total_cost / quantity
        self.fees_paid += fee
        return BacktestFill(
            side="BUY",
            symbol=canonical,
            quantity=quantity,
            market_price=price,
            fill_price=fill_price,
            fee=fee,
            observed_at=observed,
        )

    def sell(
        self,
        *,
        symbol: str,
        market_price: Decimal,
        observed_at: datetime,
        policy: BacktestExecutionPolicy,
        exit_reason: str | None = None,
    ) -> BacktestFill:
        if self.position_quantity <= ZERO:
            raise BacktestExecutionError("backtest ledger is flat")
        canonical = symbol.strip().upper()
        if canonical != self.position_symbol:
            raise BacktestExecutionError("sell symbol does not match open long")
        price = self._price(market_price)
        observed = self._time(observed_at)
        fill_price = self._fill_price("SELL", price, policy)
        fee_rate = Decimal(policy.fee_bps) / BPS
        quantity = self.position_quantity
        fee = quantity * fill_price * fee_rate
        net_proceeds = quantity * fill_price - fee
        realized = net_proceeds - quantity * self.average_cost

        self.cash += net_proceeds
        self.realized_pnl += realized
        self.fees_paid += fee
        self.position_quantity = ZERO
        self.position_symbol = None
        self.average_cost = ZERO
        return BacktestFill(
            side="SELL",
            symbol=canonical,
            quantity=quantity,
            market_price=price,
            fill_price=fill_price,
            fee=fee,
            observed_at=observed,
            realized_pnl=realized,
            exit_reason=exit_reason,
        )
