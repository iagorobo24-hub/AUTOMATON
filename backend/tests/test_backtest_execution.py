from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.backtesting.execution import (
    BacktestExecutionError,
    BacktestExecutionPolicy,
    BacktestLedger,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_buy_and_sell_preserve_long_only_accounting_with_fees_and_slippage():
    ledger = BacktestLedger(initial_capital=Decimal("1000"))
    policy = BacktestExecutionPolicy(slippage_bps=Decimal("10"), fee_bps=Decimal("10"), position_fraction=Decimal("0.25"))

    buy = ledger.buy(symbol="BTC/USDT", market_price=Decimal("100"), observed_at=NOW, policy=policy)
    assert buy.side == "BUY"
    assert buy.fill_price == Decimal("100.1")
    assert buy.quantity > 0
    assert ledger.position_quantity == buy.quantity
    assert ledger.cash >= 0
    assert ledger.fees_paid == buy.fee

    sell = ledger.sell(symbol="BTC/USDT", market_price=Decimal("110"), observed_at=NOW, policy=policy)
    assert sell.side == "SELL"
    assert sell.fill_price == Decimal("109.89")
    assert ledger.position_quantity == Decimal("0")
    assert ledger.average_cost == Decimal("0")
    assert ledger.cash == ledger.equity(Decimal("110"))
    assert ledger.realized_pnl == sell.realized_pnl
    assert ledger.fees_paid == buy.fee + sell.fee


def test_backtest_v1_does_not_pyramid_or_sell_when_flat():
    ledger = BacktestLedger(initial_capital=Decimal("1000"))
    policy = BacktestExecutionPolicy()
    ledger.buy(symbol="BTC/USDT", market_price=Decimal("100"), observed_at=NOW, policy=policy)

    with pytest.raises(BacktestExecutionError, match="already long"):
        ledger.buy(symbol="BTC/USDT", market_price=Decimal("101"), observed_at=NOW, policy=policy)

    ledger.sell(symbol="BTC/USDT", market_price=Decimal("102"), observed_at=NOW, policy=policy)
    with pytest.raises(BacktestExecutionError, match="flat"):
        ledger.sell(symbol="BTC/USDT", market_price=Decimal("102"), observed_at=NOW, policy=policy)


def test_buy_sizing_reserves_compounded_execution_cost_and_never_makes_cash_negative():
    ledger = BacktestLedger(initial_capital=Decimal("100"))
    policy = BacktestExecutionPolicy(
        slippage_bps=Decimal("10"),
        fee_bps=Decimal("10"),
        position_fraction=Decimal("1"),
    )

    fill = ledger.buy(symbol="BTC/USDT", market_price=Decimal("100"), observed_at=NOW, policy=policy)

    assert fill.quantity > 0
    assert ledger.cash >= Decimal("0")
    assert ledger.cash < Decimal("0.00000001")


def test_mark_reports_cash_market_value_equity_and_exposure():
    ledger = BacktestLedger(initial_capital=Decimal("1000"))
    policy = BacktestExecutionPolicy(position_fraction=Decimal("0.25"))
    ledger.buy(symbol="BTC/USDT", market_price=Decimal("100"), observed_at=NOW, policy=policy)

    mark = ledger.mark(Decimal("120"))

    assert mark.cash == ledger.cash
    assert mark.market_value == ledger.position_quantity * Decimal("120")
    assert mark.equity == mark.cash + mark.market_value
    assert mark.exposure == mark.market_value
