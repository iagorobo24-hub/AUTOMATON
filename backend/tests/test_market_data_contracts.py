from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.market_data.contracts import Candle, Quote
from app.market_data.quality import (
    MarketDataQualityError,
    normalize_symbol,
    validate_candle_series,
    validate_quote_freshness,
)


def test_normalize_symbol_uses_canonical_base_quote_format():
    assert normalize_symbol("btcusdt") == "BTC/USDT"
    assert normalize_symbol("btc-usdt") == "BTC/USDT"
    assert normalize_symbol("BTC/USDT") == "BTC/USDT"


def test_normalize_symbol_rejects_ambiguous_symbols():
    with pytest.raises(MarketDataQualityError):
        normalize_symbol("BTC")


def test_quote_is_real_utc_and_positive():
    quote = Quote(
        symbol="BTC/USDT",
        price=Decimal("65000.50"),
        observed_at=datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc),
        received_at=datetime(2026, 8, 19, 12, 0, 1, tzinfo=timezone.utc),
        provider="binance_public",
        provider_symbol="BTCUSDT",
        timestamp_source="provider",
    )

    assert quote.evidence_mode == "real"
    assert quote.observed_at.tzinfo == timezone.utc
    assert quote.price == Decimal("65000.50")


def test_quote_rejects_non_positive_price():
    with pytest.raises(ValueError):
        Quote(
            symbol="BTC/USDT",
            price=Decimal("0"),
            observed_at=datetime.now(timezone.utc),
            received_at=datetime.now(timezone.utc),
            provider="binance_public",
            provider_symbol="BTCUSDT",
            timestamp_source="provider",
        )


def test_validate_quote_freshness_rejects_stale_and_future_observations():
    now = datetime(2026, 8, 19, 12, 0, 30, tzinfo=timezone.utc)
    stale = Quote(
        symbol="BTC/USDT",
        price=Decimal("65000"),
        observed_at=now - timedelta(seconds=31),
        received_at=now,
        provider="binance_public",
        provider_symbol="BTCUSDT",
        timestamp_source="provider",
    )
    future = stale.model_copy(update={"observed_at": now + timedelta(seconds=6)})

    with pytest.raises(MarketDataQualityError, match="stale"):
        validate_quote_freshness(stale, now=now, max_age=timedelta(seconds=30))

    with pytest.raises(MarketDataQualityError, match="future"):
        validate_quote_freshness(future, now=now, max_age=timedelta(seconds=30))


def _candle(open_minute: int, close: str = "101") -> Candle:
    start = datetime(2026, 8, 19, 12, open_minute, tzinfo=timezone.utc)
    return Candle(
        symbol="BTC/USDT",
        interval="1m",
        open_time=start,
        close_time=start + timedelta(minutes=1) - timedelta(milliseconds=1),
        open=Decimal("100"),
        high=Decimal("102"),
        low=Decimal("99"),
        close=Decimal(close),
        volume=Decimal("10"),
        provider="binance_public",
        provider_symbol="BTCUSDT",
    )


def test_validate_candle_series_accepts_contiguous_closed_candles():
    candles = [_candle(0), _candle(1), _candle(2)]
    now = datetime(2026, 8, 19, 12, 3, 30, tzinfo=timezone.utc)

    validated = validate_candle_series(candles, interval="1m", now=now)

    assert validated == candles


def test_validate_candle_series_rejects_gap_or_out_of_order_data():
    gap = [_candle(0), _candle(2)]
    out_of_order = [_candle(1), _candle(0)]
    now = datetime(2026, 8, 19, 12, 3, 30, tzinfo=timezone.utc)

    with pytest.raises(MarketDataQualityError, match="gap"):
        validate_candle_series(gap, interval="1m", now=now)

    with pytest.raises(MarketDataQualityError, match="order"):
        validate_candle_series(out_of_order, interval="1m", now=now)
