from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.backtesting.datasets import (
    DatasetValidationError,
    canonical_dataset_sha256,
    persist_dataset,
)
from app.market_data.contracts import Candle
from app.models.backtesting import BacktestCandle, BacktestDataset

UTC = timezone.utc
START = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)


def _candle(i: int, *, open_time: datetime | None = None) -> Candle:
    start = open_time or START + timedelta(minutes=i)
    return Candle(
        symbol="BTC/USDT",
        interval="1m",
        open_time=start,
        close_time=start + timedelta(minutes=1) - timedelta(milliseconds=1),
        open=Decimal("100") + i,
        high=Decimal("101") + i,
        low=Decimal("99") + i,
        close=Decimal("100.5") + i,
        volume=Decimal("10") + i,
        provider="binance_public",
        provider_symbol="BTCUSDT",
    )


def _engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_dataset_hash_is_stable_for_identical_normalized_content():
    candles_a = [_candle(0), _candle(1), _candle(2)]
    candles_b = [_candle(0), _candle(1), _candle(2)]

    assert canonical_dataset_sha256(candles_a) == canonical_dataset_sha256(candles_b)
    assert len(canonical_dataset_sha256(candles_a)) == 64


def test_dataset_hash_normalizes_decimal_scale_not_only_string_representation():
    base = [_candle(0), _candle(1)]
    equivalent = list(base)
    equivalent[1] = equivalent[1].model_copy(update={
        "open": Decimal("101.0000"),
        "high": Decimal("102.000"),
        "low": Decimal("100.00"),
        "close": Decimal("101.5000"),
        "volume": Decimal("11.000"),
    })

    assert canonical_dataset_sha256(base) == canonical_dataset_sha256(equivalent)


def test_dataset_hash_changes_when_market_content_changes():
    candles = [_candle(0), _candle(1)]
    changed = list(candles)
    changed[1] = changed[1].model_copy(update={"close": Decimal("999")})

    assert canonical_dataset_sha256(candles) != canonical_dataset_sha256(changed)


def test_persist_dataset_rejects_gap_duplicate_out_of_order_and_mixed_provider_series():
    engine = _engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        with pytest.raises(DatasetValidationError, match="gap"):
            persist_dataset(
                session,
                symbol="BTC/USDT",
                interval="1m",
                requested_start=START,
                requested_end=START + timedelta(minutes=4),
                candles=[_candle(0), _candle(2), _candle(3)],
            )

        duplicate = [_candle(0), _candle(1), _candle(1)]
        with pytest.raises(DatasetValidationError, match="duplicate"):
            persist_dataset(
                session,
                symbol="BTC/USDT",
                interval="1m",
                requested_start=START,
                requested_end=START + timedelta(minutes=3),
                candles=duplicate,
            )

        out_of_order = [_candle(0), _candle(2), _candle(1)]
        with pytest.raises(DatasetValidationError, match="order"):
            persist_dataset(
                session,
                symbol="BTC/USDT",
                interval="1m",
                requested_start=START,
                requested_end=START + timedelta(minutes=3),
                candles=out_of_order,
            )

        mixed_provider = [_candle(0), _candle(1)]
        mixed_provider[1] = mixed_provider[1].model_copy(update={
            "provider": "other_real_provider",
            "provider_symbol": "BTCUSDT",
        })
        with pytest.raises(DatasetValidationError, match="provider"):
            persist_dataset(
                session,
                symbol="BTC/USDT",
                interval="1m",
                requested_start=START,
                requested_end=START + timedelta(minutes=2),
                candles=mixed_provider,
            )


def test_ready_dataset_persists_immutable_snapshot_metadata_and_candles():
    engine = _engine()
    SQLModel.metadata.create_all(engine)
    candles = [_candle(0), _candle(1), _candle(2)]

    with Session(engine) as session:
        dataset = persist_dataset(
            session,
            symbol="BTC/USDT",
            interval="1m",
            requested_start=START,
            requested_end=START + timedelta(minutes=3),
            candles=candles,
        )

        assert dataset.status == "READY"
        assert dataset.candle_count == 3
        assert dataset.content_sha256 == canonical_dataset_sha256(candles)
        assert dataset.actual_start == candles[0].open_time
        assert dataset.actual_end == candles[-1].close_time
        persisted = session.exec(
            select(BacktestCandle)
            .where(BacktestCandle.dataset_id == dataset.id)
            .order_by(BacktestCandle.ordinal)
        ).all()
        assert [item.ordinal for item in persisted] == [0, 1, 2]
        assert [item.close for item in persisted] == [c.close for c in candles]

        with pytest.raises(DatasetValidationError, match="already exists"):
            persist_dataset(
                session,
                symbol="BTC/USDT",
                interval="1m",
                requested_start=START,
                requested_end=START + timedelta(minutes=3),
                candles=candles,
            )

        assert len(session.exec(select(BacktestDataset)).all()) == 1
