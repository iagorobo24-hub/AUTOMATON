import re
from datetime import datetime, timedelta, timezone
from typing import Iterable

from .contracts import Candle, Quote


class MarketDataError(RuntimeError):
    """Base exception for the real market-data boundary."""


class MarketDataUnavailable(MarketDataError):
    """The provider could not return trustworthy real market data."""


class MarketDataQualityError(MarketDataError):
    """Provider data was received but violated the market-data contract."""


_INTERVAL_SECONDS = {
    "1m": 60,
    "3m": 180,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "2h": 7200,
    "4h": 14400,
    "6h": 21600,
    "8h": 28800,
    "12h": 43200,
    "1d": 86400,
}


def interval_timedelta(interval: str) -> timedelta:
    seconds = _INTERVAL_SECONDS.get(interval)
    if seconds is None:
        raise MarketDataQualityError(f"unsupported interval: {interval}")
    return timedelta(seconds=seconds)


def normalize_symbol(symbol: str) -> str:
    compact = re.sub(r"[/_\-\s]", "", symbol.strip().upper())
    if not compact.endswith("USDT") or len(compact) <= 4:
        raise MarketDataQualityError(
            "symbol must identify a BASE/USDT market, for example BTC/USDT"
        )
    base = compact[:-4]
    if not re.fullmatch(r"[A-Z0-9]{2,15}", base):
        raise MarketDataQualityError("invalid base asset in market symbol")
    return f"{base}/USDT"


def provider_symbol(symbol: str) -> str:
    return normalize_symbol(symbol).replace("/", "")


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise MarketDataQualityError("comparison timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def validate_quote_freshness(
    quote: Quote,
    *,
    now: datetime | None = None,
    max_age: timedelta = timedelta(seconds=30),
    future_tolerance: timedelta = timedelta(seconds=5),
) -> Quote:
    current = _ensure_utc(now or datetime.now(timezone.utc))
    age = current - quote.observed_at
    if age > max_age:
        raise MarketDataQualityError(
            f"quote is stale by {age.total_seconds():.3f}s"
        )
    if quote.observed_at - current > future_tolerance:
        raise MarketDataQualityError("quote timestamp is in the future")
    return quote


def validate_candle_series(
    candles: Iterable[Candle],
    *,
    interval: str,
    now: datetime | None = None,
    max_staleness_intervals: float = 2.0,
) -> list[Candle]:
    items = list(candles)
    if not items:
        raise MarketDataQualityError("empty candle series")

    current = _ensure_utc(now or datetime.now(timezone.utc))
    step = interval_timedelta(interval)
    first_symbol = items[0].symbol

    for candle in items:
        if candle.interval != interval:
            raise MarketDataQualityError("candle interval mismatch")
        if candle.symbol != first_symbol:
            raise MarketDataQualityError("mixed symbols in candle series")
        if candle.close_time > current:
            raise MarketDataQualityError("candle is not closed yet")

    for previous, current_candle in zip(items, items[1:]):
        if current_candle.open_time <= previous.open_time:
            raise MarketDataQualityError("candle order is not strictly increasing")
        expected = previous.open_time + step
        if current_candle.open_time != expected:
            raise MarketDataQualityError(
                f"candle gap detected: expected {expected.isoformat()}, "
                f"got {current_candle.open_time.isoformat()}"
            )

    max_staleness = step * max_staleness_intervals
    if current - items[-1].close_time > max_staleness:
        raise MarketDataQualityError("latest candle is stale")

    return items
