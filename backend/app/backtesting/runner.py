import hashlib
import inspect
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.backtesting.execution import (
    BacktestExecutionError,
    BacktestExecutionPolicy,
    BacktestFill,
    BacktestLedger,
)
from app.backtesting.metrics import EquitySample, compute_metrics
from app.models.backtesting import (
    BacktestCandle,
    BacktestDataset,
    BacktestEquityPoint,
    BacktestRun,
    BacktestRunEvidence,
    BacktestTrade,
)
from app.services import strategies as strategies_module
from app.services.strategies import get_strategy

ZERO = Decimal("0")


class BacktestRunError(ValueError):
    pass


def strategy_source_sha256() -> str:
    """Fingerprint active strategy source; fail closed if source is unavailable."""
    try:
        source = inspect.getsource(strategies_module)
    except (OSError, TypeError) as exc:
        raise BacktestRunError("active strategy source is unavailable for fingerprinting") from exc
    normalized = source.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BacktestRunConfig:
    initial_capital: Decimal = Decimal("1000")
    fee_bps: Decimal = Decimal("10")
    slippage_bps: Decimal = Decimal("10")
    position_fraction: Decimal = Decimal("0.25")
    strategy_version: str = "baseline-v1"
    risk_profile_version: str = "backtest-risk-v1"
    code_commit: str | None = None

    def policy(self) -> BacktestExecutionPolicy:
        return BacktestExecutionPolicy(
            fee_bps=Decimal(self.fee_bps),
            slippage_bps=Decimal(self.slippage_bps),
            position_fraction=Decimal(self.position_fraction),
        )


def recover_interrupted_runs(session: Session) -> int:
    """Invalidate stale RUNNING evidence after restart; never silently resume it."""
    runs = session.exec(select(BacktestRun).where(BacktestRun.status == "RUNNING")).all()
    if not runs:
        return 0
    now = datetime.now(timezone.utc)
    for run in runs:
        run.status = "INVALID"
        run.failure_reason = "INTERRUPTED_RESTART"
        run.completed_at = now
        session.add(run)
    session.commit()
    return len(runs)


class BacktestRunner:
    def __init__(self, session: Session):
        self.session = session

    def _dataset(self, dataset_id: int) -> BacktestDataset:
        dataset = self.session.get(BacktestDataset, dataset_id)
        if dataset is None:
            raise BacktestRunError("backtest dataset not found")
        if dataset.status != "READY":
            raise BacktestRunError("backtest dataset is not READY")
        return dataset

    def _candles(self, dataset_id: int) -> list[BacktestCandle]:
        candles = self.session.exec(
            select(BacktestCandle)
            .where(BacktestCandle.dataset_id == dataset_id)
            .order_by(BacktestCandle.ordinal)
        ).all()
        if len(candles) < 2:
            raise BacktestRunError("backtest requires at least two candles")
        return candles

    def _persist_trade(self, *, run_id: int, fill: BacktestFill, signal_candle_time: datetime | None) -> BacktestTrade:
        trade = BacktestTrade(
            run_id=run_id,
            side=fill.side,
            signal_candle_time=signal_candle_time,
            execution_candle_time=fill.observed_at,
            quantity=fill.quantity,
            market_price=fill.market_price,
            fill_price=fill.fill_price,
            fee=fill.fee,
            realized_pnl=fill.realized_pnl,
            exit_reason=fill.exit_reason,
        )
        self.session.add(trade)
        return trade

    def _persist_equity(
        self,
        *,
        run_id: int,
        ordinal: int,
        candle_time: datetime,
        ledger: BacktestLedger,
        mark_price: Decimal,
        high_water: Decimal,
    ) -> tuple[BacktestEquityPoint, Decimal]:
        mark = ledger.mark(mark_price)
        new_high = max(high_water, mark.equity)
        drawdown = ZERO if new_high <= ZERO else max(ZERO, (new_high - mark.equity) / new_high)
        point = BacktestEquityPoint(
            run_id=run_id,
            ordinal=ordinal,
            candle_time=candle_time,
            cash=mark.cash,
            market_value=mark.market_value,
            equity=mark.equity,
            exposure=mark.exposure,
            drawdown=drawdown,
        )
        self.session.add(point)
        return point, new_high

    def run(self, dataset_id: int, strategy_id: str, config: BacktestRunConfig | None = None) -> BacktestRun:
        config = config or BacktestRunConfig()
        dataset = self._dataset(dataset_id)
        candles = self._candles(dataset_id)
        try:
            strategy = get_strategy(strategy_id)
        except ValueError as exc:
            raise BacktestRunError(str(exc)) from exc

        initial = Decimal(config.initial_capital)
        if initial <= ZERO:
            raise BacktestRunError("initial_capital must be positive")
        policy = config.policy()
        strategy_digest = strategy_source_sha256()

        run = BacktestRun(
            dataset_id=dataset.id,
            dataset_sha256=dataset.content_sha256,
            strategy_id=strategy_id,
            strategy_version=config.strategy_version,
            execution_policy=policy.version,
            initial_capital=initial,
            fee_bps=policy.fee_bps,
            slippage_bps=policy.slippage_bps,
            position_fraction=policy.position_fraction,
            risk_profile_version=config.risk_profile_version,
            code_commit=config.code_commit,
            status="RUNNING",
            initial_equity=initial,
        )
        self.session.add(run)
        self.session.flush()
        self.session.add(BacktestRunEvidence(run_id=run.id, strategy_code_sha256=strategy_digest))
        self.session.commit()
        self.session.refresh(run)

        ledger = BacktestLedger(initial_capital=initial)
        history: list[float] = []
        fills: list[BacktestFill] = []
        equity_samples: list[EquitySample] = []
        high_water = initial
        pending_signal: tuple[str, datetime] | None = None

        try:
            for ordinal, candle in enumerate(candles):
                if pending_signal is not None:
                    signal, signal_time = pending_signal
                    if signal == "BUY" and ledger.position_quantity == ZERO:
                        fill = ledger.buy(symbol=dataset.symbol, market_price=Decimal(candle.open), observed_at=candle.open_time, policy=policy)
                        fills.append(fill)
                        self._persist_trade(run_id=run.id, fill=fill, signal_candle_time=signal_time)
                    elif signal == "SELL" and ledger.position_quantity > ZERO:
                        fill = ledger.sell(symbol=dataset.symbol, market_price=Decimal(candle.open), observed_at=candle.open_time, policy=policy)
                        fills.append(fill)
                        self._persist_trade(run_id=run.id, fill=fill, signal_candle_time=signal_time)

                point, high_water = self._persist_equity(
                    run_id=run.id,
                    ordinal=ordinal,
                    candle_time=candle.close_time,
                    ledger=ledger,
                    mark_price=Decimal(candle.close),
                    high_water=high_water,
                )
                equity_samples.append(EquitySample(equity=point.equity, exposure=point.exposure))
                history.append(float(candle.close))
                pending_signal = (strategy.calcular_señal(history), candle.close_time)

            if ledger.position_quantity > ZERO:
                final_candle = candles[-1]
                fill = ledger.sell(
                    symbol=dataset.symbol,
                    market_price=Decimal(final_candle.close),
                    observed_at=final_candle.close_time,
                    policy=policy,
                    exit_reason="DATASET_END_EXIT",
                )
                fills.append(fill)
                self._persist_trade(run_id=run.id, fill=fill, signal_candle_time=None)
                point, high_water = self._persist_equity(
                    run_id=run.id,
                    ordinal=len(candles),
                    candle_time=final_candle.close_time,
                    ledger=ledger,
                    mark_price=Decimal(final_candle.close),
                    high_water=high_water,
                )
                equity_samples.append(EquitySample(equity=point.equity, exposure=point.exposure, counts_for_exposure=False))

            final_equity = ledger.cash if ledger.position_quantity == ZERO else ledger.equity(Decimal(candles[-1].close))
            metrics = compute_metrics(initial_capital=initial, final_equity=final_equity, trades=fills, equity_points=equity_samples)
            run.final_equity = metrics.final_equity
            run.net_pnl = metrics.net_pnl
            run.net_return = metrics.net_return
            run.trade_count = metrics.trade_count
            run.round_trip_count = metrics.round_trip_count
            run.wins = metrics.wins
            run.losses = metrics.losses
            run.win_rate = metrics.win_rate
            run.average_win = metrics.average_win
            run.average_loss = metrics.average_loss
            run.expectancy = metrics.expectancy
            run.gross_profit = metrics.gross_profit
            run.gross_loss = metrics.gross_loss
            run.profit_factor = metrics.profit_factor
            run.max_drawdown = metrics.max_drawdown
            run.total_fees = metrics.total_fees
            run.exposure_fraction = metrics.exposure_fraction
            run.forced_exit_count = metrics.forced_exit_count
            run.status = "COMPLETED"
            run.completed_at = datetime.now(timezone.utc)
            self.session.add(run)
            self.session.commit()
            self.session.refresh(run)
            return run
        except (BacktestExecutionError, ValueError, ArithmeticError) as exc:
            run.status = "INVALID"
            run.failure_reason = str(exc)[:256]
            run.completed_at = datetime.now(timezone.utc)
            self.session.add(run)
            self.session.commit()
            raise BacktestRunError(str(exc)) from exc
