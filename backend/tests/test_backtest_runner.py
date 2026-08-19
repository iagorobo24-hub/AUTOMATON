from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.backtesting.datasets import persist_dataset
from app.backtesting.runner import BacktestRunConfig, BacktestRunner
from app.market_data.contracts import Candle
from app.models.backtesting import BacktestEquityPoint, BacktestTrade

UTC = timezone.utc
START = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _candles(closes: list[str]) -> list[Candle]:
    result = []
    for i, close in enumerate(closes):
        open_time = START + timedelta(minutes=i)
        close_value = Decimal(close)
        result.append(
            Candle(
                symbol="BTC/USDT",
                interval="1m",
                open_time=open_time,
                close_time=open_time + timedelta(minutes=1) - timedelta(milliseconds=1),
                open=close_value - Decimal("0.2"),
                high=close_value + Decimal("0.5"),
                low=close_value - Decimal("0.5"),
                close=close_value,
                volume=Decimal("10"),
                provider="fixture_real_history",
                provider_symbol="BTCUSDT",
            )
        )
    return result


def _dataset(session: Session, closes: list[str]):
    candles = _candles(closes)
    return persist_dataset(
        session,
        symbol="BTC/USDT",
        interval="1m",
        requested_start=START,
        requested_end=START + timedelta(minutes=len(candles)),
        candles=candles,
    )


def test_s1_signal_on_candle_t_executes_only_at_next_candle_open():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        dataset = _dataset(session, ["100", "101", "102", "103", "104"])
        run = BacktestRunner(session).run(
            dataset.id,
            "S1",
            BacktestRunConfig(initial_capital=Decimal("1000")),
        )
        trades = session.exec(
            select(BacktestTrade).where(BacktestTrade.run_id == run.id).order_by(BacktestTrade.id)
        ).all()

        buy = trades[0]
        signal_candle = _candles(["100", "101", "102"])[2]
        execution_candle = _candles(["100", "101", "102", "103"])[3]
        assert buy.side == "BUY"
        assert buy.signal_candle_time == signal_candle.close_time
        assert buy.execution_candle_time == execution_candle.open_time
        assert buy.market_price == execution_candle.open
        assert buy.execution_candle_time > buy.signal_candle_time
        assert trades[-1].exit_reason == "DATASET_END_EXIT"
        assert run.status == "COMPLETED"


def test_identical_dataset_and_config_produce_identical_trade_and_equity_evidence():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        dataset = _dataset(session, ["100", "101", "102", "99", "98", "103", "104"])
        config = BacktestRunConfig(
            initial_capital=Decimal("1000"),
            fee_bps=Decimal("10"),
            slippage_bps=Decimal("10"),
            position_fraction=Decimal("0.25"),
        )
        first = BacktestRunner(session).run(dataset.id, "S1", config)
        second = BacktestRunner(session).run(dataset.id, "S1", config)

        first_trades = session.exec(select(BacktestTrade).where(BacktestTrade.run_id == first.id).order_by(BacktestTrade.id)).all()
        second_trades = session.exec(select(BacktestTrade).where(BacktestTrade.run_id == second.id).order_by(BacktestTrade.id)).all()
        assert [
            (t.side, t.signal_candle_time, t.execution_candle_time, t.quantity, t.market_price, t.fill_price, t.fee, t.realized_pnl, t.exit_reason)
            for t in first_trades
        ] == [
            (t.side, t.signal_candle_time, t.execution_candle_time, t.quantity, t.market_price, t.fill_price, t.fee, t.realized_pnl, t.exit_reason)
            for t in second_trades
        ]

        first_equity = session.exec(select(BacktestEquityPoint).where(BacktestEquityPoint.run_id == first.id).order_by(BacktestEquityPoint.ordinal)).all()
        second_equity = session.exec(select(BacktestEquityPoint).where(BacktestEquityPoint.run_id == second.id).order_by(BacktestEquityPoint.ordinal)).all()
        assert [(p.cash, p.market_value, p.equity, p.exposure, p.drawdown) for p in first_equity] == [
            (p.cash, p.market_value, p.equity, p.exposure, p.drawdown) for p in second_equity
        ]
        assert first.final_equity == second.final_equity
        assert first.net_pnl == second.net_pnl
