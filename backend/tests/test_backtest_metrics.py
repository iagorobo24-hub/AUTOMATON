from decimal import Decimal

from app.backtesting.metrics import compute_metrics
from app.backtesting.execution import BacktestFill
from app.backtesting.metrics import EquitySample


def test_metrics_cover_return_round_trips_drawdown_fees_and_exposure():
    trades = [
        BacktestFill(side="BUY", symbol="BTC/USDT", quantity=Decimal("1"), market_price=Decimal("100"), fill_price=Decimal("100"), fee=Decimal("1"), observed_at=None),
        BacktestFill(side="SELL", symbol="BTC/USDT", quantity=Decimal("1"), market_price=Decimal("110"), fill_price=Decimal("110"), fee=Decimal("1"), observed_at=None, realized_pnl=Decimal("8")),
        BacktestFill(side="BUY", symbol="BTC/USDT", quantity=Decimal("1"), market_price=Decimal("120"), fill_price=Decimal("120"), fee=Decimal("1"), observed_at=None),
        BacktestFill(side="SELL", symbol="BTC/USDT", quantity=Decimal("1"), market_price=Decimal("115"), fill_price=Decimal("115"), fee=Decimal("1"), observed_at=None, realized_pnl=Decimal("-7"), exit_reason="DATASET_END_EXIT"),
    ]
    equity = [
        EquitySample(equity=Decimal("1000"), exposure=Decimal("0")),
        EquitySample(equity=Decimal("1020"), exposure=Decimal("250")),
        EquitySample(equity=Decimal("990"), exposure=Decimal("200")),
        EquitySample(equity=Decimal("1001"), exposure=Decimal("0")),
    ]

    result = compute_metrics(
        initial_capital=Decimal("1000"),
        final_equity=Decimal("1001"),
        trades=trades,
        equity_points=equity,
    )

    assert result.net_pnl == Decimal("1")
    assert result.net_return == Decimal("0.001")
    assert result.trade_count == 4
    assert result.round_trip_count == 2
    assert result.wins == 1
    assert result.losses == 1
    assert result.win_rate == Decimal("0.5")
    assert result.average_win == Decimal("8")
    assert result.average_loss == Decimal("-7")
    assert result.expectancy == Decimal("0.5")
    assert result.gross_profit == Decimal("8")
    assert result.gross_loss == Decimal("7")
    assert result.profit_factor == Decimal("8") / Decimal("7")
    assert result.max_drawdown == Decimal("30") / Decimal("1020")
    assert result.total_fees == Decimal("4")
    assert result.exposure_fraction == Decimal("0.5")
    assert result.forced_exit_count == 1


def test_forced_close_bookkeeping_point_does_not_dilute_time_in_market():
    equity = [
        EquitySample(equity=Decimal("1000"), exposure=Decimal("0")),
        EquitySample(equity=Decimal("1010"), exposure=Decimal("200")),
        EquitySample(equity=Decimal("1015"), exposure=Decimal("0")),
        EquitySample(equity=Decimal("1014"), exposure=Decimal("0"), counts_for_exposure=False),
    ]

    result = compute_metrics(
        initial_capital=Decimal("1000"),
        final_equity=Decimal("1014"),
        trades=[],
        equity_points=equity,
    )

    assert result.exposure_fraction == Decimal("1") / Decimal("3")


def test_metrics_keep_undefined_ratios_null_when_no_closed_round_trips():
    result = compute_metrics(
        initial_capital=Decimal("1000"),
        final_equity=Decimal("1000"),
        trades=[],
        equity_points=[EquitySample(equity=Decimal("1000"), exposure=Decimal("0"))],
    )

    assert result.round_trip_count == 0
    assert result.win_rate is None
    assert result.average_win is None
    assert result.average_loss is None
    assert result.expectancy is None
    assert result.profit_factor is None
