from dataclasses import dataclass
from decimal import Decimal

from app.backtesting.execution import BacktestFill

ZERO = Decimal("0")


@dataclass(frozen=True)
class EquitySample:
    equity: Decimal
    exposure: Decimal
    counts_for_exposure: bool = True


@dataclass(frozen=True)
class BacktestMetrics:
    initial_equity: Decimal
    final_equity: Decimal
    net_pnl: Decimal
    net_return: Decimal
    trade_count: int
    round_trip_count: int
    wins: int
    losses: int
    win_rate: Decimal | None
    average_win: Decimal | None
    average_loss: Decimal | None
    expectancy: Decimal | None
    gross_profit: Decimal
    gross_loss: Decimal
    profit_factor: Decimal | None
    max_drawdown: Decimal
    total_fees: Decimal
    exposure_fraction: Decimal
    forced_exit_count: int


def compute_metrics(
    *,
    initial_capital: Decimal,
    final_equity: Decimal,
    trades: list[BacktestFill],
    equity_points: list[EquitySample],
) -> BacktestMetrics:
    initial = Decimal(initial_capital)
    final = Decimal(final_equity)
    if initial <= ZERO:
        raise ValueError("initial_capital must be positive")

    closes = [trade for trade in trades if trade.side == "SELL"]
    outcomes = [Decimal(trade.realized_pnl) for trade in closes]
    wins_values = [value for value in outcomes if value > ZERO]
    loss_values = [value for value in outcomes if value < ZERO]
    wins = len(wins_values)
    losses = len(loss_values)
    round_trips = len(outcomes)

    win_rate = Decimal(wins) / Decimal(round_trips) if round_trips else None
    average_win = sum(wins_values, ZERO) / Decimal(wins) if wins else None
    average_loss = sum(loss_values, ZERO) / Decimal(losses) if losses else None
    expectancy = sum(outcomes, ZERO) / Decimal(round_trips) if round_trips else None
    gross_profit = sum(wins_values, ZERO)
    gross_loss = -sum(loss_values, ZERO)
    profit_factor = gross_profit / gross_loss if gross_loss > ZERO else None

    high_water: Decimal | None = None
    max_drawdown = ZERO
    exposed = 0
    exposure_samples = 0
    for point in equity_points:
        equity = Decimal(point.equity)
        exposure = Decimal(point.exposure)
        if high_water is None or equity > high_water:
            high_water = equity
        if high_water and high_water > ZERO and equity < high_water:
            drawdown = (high_water - equity) / high_water
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        if point.counts_for_exposure:
            exposure_samples += 1
            if exposure > ZERO:
                exposed += 1

    exposure_fraction = (
        Decimal(exposed) / Decimal(exposure_samples) if exposure_samples else ZERO
    )
    total_fees = sum((Decimal(trade.fee) for trade in trades), ZERO)

    return BacktestMetrics(
        initial_equity=initial,
        final_equity=final,
        net_pnl=final - initial,
        net_return=(final - initial) / initial,
        trade_count=len(trades),
        round_trip_count=round_trips,
        wins=wins,
        losses=losses,
        win_rate=win_rate,
        average_win=average_win,
        average_loss=average_loss,
        expectancy=expectancy,
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        profit_factor=profit_factor,
        max_drawdown=max_drawdown,
        total_fees=total_fees,
        exposure_fraction=exposure_fraction,
        forced_exit_count=sum(1 for trade in trades if trade.exit_reason == "DATASET_END_EXIT"),
    )
