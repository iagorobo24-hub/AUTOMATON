from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.backtesting.datasets import DatasetValidationError, persist_dataset
from app.backtesting.providers.binance_history import BinanceHistoricalDataProvider
from app.backtesting.runner import BacktestRunConfig, BacktestRunError, BacktestRunner
from app.database import get_session
from app.market_data.quality import MarketDataQualityError, MarketDataUnavailable
from app.models.backtesting import BacktestDataset, BacktestEquityPoint, BacktestRun, BacktestTrade

router = APIRouter()


def get_historical_provider() -> BinanceHistoricalDataProvider:
    return BinanceHistoricalDataProvider()


def _decimal(value: Decimal | None) -> str | None:
    return None if value is None else format(Decimal(value), "f")


def _dataset_payload(dataset: BacktestDataset) -> dict:
    return {
        "id": dataset.id,
        "symbol": dataset.symbol,
        "interval": dataset.interval,
        "provider": dataset.provider,
        "requested_start": dataset.requested_start.isoformat(),
        "requested_end": dataset.requested_end.isoformat(),
        "actual_start": dataset.actual_start.isoformat(),
        "actual_end": dataset.actual_end.isoformat(),
        "candle_count": dataset.candle_count,
        "content_sha256": dataset.content_sha256,
        "status": dataset.status,
        "created_at": dataset.created_at.isoformat(),
    }


def _run_payload(run: BacktestRun) -> dict:
    return {
        "id": run.id,
        "dataset_id": run.dataset_id,
        "dataset_sha256": run.dataset_sha256,
        "strategy_id": run.strategy_id,
        "strategy_version": run.strategy_version,
        "execution_policy": run.execution_policy,
        "initial_capital": _decimal(run.initial_capital),
        "fee_bps": _decimal(run.fee_bps),
        "slippage_bps": _decimal(run.slippage_bps),
        "position_fraction": _decimal(run.position_fraction),
        "risk_profile_version": run.risk_profile_version,
        "code_commit": run.code_commit,
        "status": run.status,
        "failure_reason": run.failure_reason,
        "initial_equity": _decimal(run.initial_equity),
        "final_equity": _decimal(run.final_equity),
        "net_pnl": _decimal(run.net_pnl),
        "net_return": _decimal(run.net_return),
        "trade_count": run.trade_count,
        "round_trip_count": run.round_trip_count,
        "wins": run.wins,
        "losses": run.losses,
        "win_rate": _decimal(run.win_rate),
        "average_win": _decimal(run.average_win),
        "average_loss": _decimal(run.average_loss),
        "expectancy": _decimal(run.expectancy),
        "gross_profit": _decimal(run.gross_profit),
        "gross_loss": _decimal(run.gross_loss),
        "profit_factor": _decimal(run.profit_factor),
        "max_drawdown": _decimal(run.max_drawdown),
        "total_fees": _decimal(run.total_fees),
        "exposure_fraction": _decimal(run.exposure_fraction),
        "forced_exit_count": run.forced_exit_count,
        "started_at": run.started_at.isoformat(),
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
    }


@router.get("/status")
def status() -> dict:
    return {
        "evidence_mode": "backtest",
        "historical_market_data": "real_only",
        "dataset_policy": "immutable_sha256",
        "execution_policy": "backtest-v1",
        "strategy_version": "baseline-v1",
        "deterministic": True,
        "lookahead_policy": "signal_close_t_execute_open_t_plus_1",
        "live_execution_capability": False,
        "synthetic_fallback": False,
        "optimizer": "not_implemented",
    }


@router.post("/datasets")
async def create_dataset(
    symbol: str = Query(min_length=3),
    interval: str = Query(default="1m", min_length=2, max_length=8),
    start: datetime = Query(),
    end: datetime = Query(),
    session: Session = Depends(get_session),
    provider: BinanceHistoricalDataProvider = Depends(get_historical_provider),
) -> dict:
    try:
        candles = await provider.fetch_candles(symbol, interval, start, end)
        dataset = persist_dataset(
            session,
            symbol=symbol,
            interval=interval,
            requested_start=start,
            requested_end=end,
            candles=candles,
        )
    except MarketDataUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except MarketDataQualityError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except DatasetValidationError as exc:
        status_code = 409 if "already exists" in str(exc) else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return _dataset_payload(dataset)


@router.get("/datasets")
def list_datasets(
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[dict]:
    datasets = session.exec(
        select(BacktestDataset).order_by(BacktestDataset.id.desc()).limit(limit)
    ).all()
    return [_dataset_payload(item) for item in datasets]


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, session: Session = Depends(get_session)) -> dict:
    dataset = session.get(BacktestDataset, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="backtest dataset not found")
    return _dataset_payload(dataset)


@router.post("/runs")
def create_run(
    dataset_id: int = Query(gt=0),
    strategy_id: str = Query(min_length=2, max_length=8),
    initial_capital: Decimal = Query(default=Decimal("1000"), gt=0),
    fee_bps: Decimal = Query(default=Decimal("10"), ge=0),
    slippage_bps: Decimal = Query(default=Decimal("10"), ge=0),
    position_fraction: Decimal = Query(default=Decimal("0.25"), gt=0, le=1),
    session: Session = Depends(get_session),
) -> dict:
    dataset = session.get(BacktestDataset, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="backtest dataset not found")
    try:
        run = BacktestRunner(session).run(
            dataset_id,
            strategy_id,
            BacktestRunConfig(
                initial_capital=initial_capital,
                fee_bps=fee_bps,
                slippage_bps=slippage_bps,
                position_fraction=position_fraction,
            ),
        )
    except BacktestRunError as exc:
        if "Unknown strategy" in str(exc):
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _run_payload(run)


@router.get("/runs")
def list_runs(
    dataset_id: int | None = None,
    strategy_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[dict]:
    statement = select(BacktestRun)
    if dataset_id is not None:
        statement = statement.where(BacktestRun.dataset_id == dataset_id)
    if strategy_id is not None:
        statement = statement.where(BacktestRun.strategy_id == strategy_id)
    runs = session.exec(statement.order_by(BacktestRun.id.desc()).limit(limit)).all()
    return [_run_payload(run) for run in runs]


@router.get("/runs/{run_id}")
def get_run(run_id: int, session: Session = Depends(get_session)) -> dict:
    run = session.get(BacktestRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="backtest run not found")
    dataset = session.get(BacktestDataset, run.dataset_id)
    trades = session.exec(
        select(BacktestTrade).where(BacktestTrade.run_id == run.id).order_by(BacktestTrade.id)
    ).all()
    equity = session.exec(
        select(BacktestEquityPoint)
        .where(BacktestEquityPoint.run_id == run.id)
        .order_by(BacktestEquityPoint.ordinal)
    ).all()
    payload = _run_payload(run)
    payload.update({
        "dataset": _dataset_payload(dataset) if dataset else None,
        "metrics": {
            "net_pnl": _decimal(run.net_pnl),
            "net_return": _decimal(run.net_return),
            "max_drawdown": _decimal(run.max_drawdown),
            "win_rate": _decimal(run.win_rate),
            "profit_factor": _decimal(run.profit_factor),
            "total_fees": _decimal(run.total_fees),
            "exposure_fraction": _decimal(run.exposure_fraction),
        },
        "trade_count": len(trades),
        "equity_point_count": len(equity),
        "trades": [
            {
                "id": trade.id,
                "side": trade.side,
                "signal_candle_time": trade.signal_candle_time.isoformat() if trade.signal_candle_time else None,
                "execution_candle_time": trade.execution_candle_time.isoformat(),
                "quantity": _decimal(trade.quantity),
                "market_price": _decimal(trade.market_price),
                "fill_price": _decimal(trade.fill_price),
                "fee": _decimal(trade.fee),
                "realized_pnl": _decimal(trade.realized_pnl),
                "exit_reason": trade.exit_reason,
            }
            for trade in trades
        ],
    })
    return payload
