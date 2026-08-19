import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.market_data.contracts import Candle
from app.market_data.quality import interval_timedelta, normalize_symbol
from app.models.backtesting import BacktestCandle, BacktestDataset


class DatasetValidationError(ValueError):
    pass


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise DatasetValidationError("dataset timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def _decimal_text(value: Decimal) -> str:
    return format(Decimal(value), "f")


def _canonical_rows(candles: list[Candle]) -> list[dict[str, str]]:
    return [
        {
            "symbol": candle.symbol,
            "interval": candle.interval,
            "open_time": candle.open_time.astimezone(timezone.utc).isoformat(),
            "close_time": candle.close_time.astimezone(timezone.utc).isoformat(),
            "open": _decimal_text(candle.open),
            "high": _decimal_text(candle.high),
            "low": _decimal_text(candle.low),
            "close": _decimal_text(candle.close),
            "volume": _decimal_text(candle.volume),
            "provider": candle.provider,
            "provider_symbol": candle.provider_symbol,
        }
        for candle in candles
    ]


def canonical_dataset_sha256(candles: list[Candle]) -> str:
    payload = json.dumps(
        _canonical_rows(candles),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_dataset_candles(
    candles: list[Candle],
    *,
    symbol: str,
    interval: str,
    requested_start: datetime,
    requested_end: datetime,
) -> None:
    if not candles:
        raise DatasetValidationError("historical dataset cannot be empty")

    canonical_symbol = normalize_symbol(symbol)
    start = _utc(requested_start)
    end = _utc(requested_end)
    if end <= start:
        raise DatasetValidationError("requested_end must be after requested_start")

    step = interval_timedelta(interval)
    seen: set[datetime] = set()
    previous: Candle | None = None
    for candle in candles:
        if candle.evidence_mode != "real":
            raise DatasetValidationError("historical dataset requires real market evidence")
        if candle.symbol != canonical_symbol or candle.interval != interval:
            raise DatasetValidationError("dataset candle symbol/interval mismatch")
        if not candle.provider.strip() or not candle.provider_symbol.strip():
            raise DatasetValidationError("dataset candle provider provenance is required")
        if candle.open_time < start or candle.close_time > end:
            raise DatasetValidationError("dataset candle is outside requested window")
        if candle.open_time in seen:
            raise DatasetValidationError("duplicate candle open_time")
        seen.add(candle.open_time)
        if previous is not None:
            if candle.open_time <= previous.open_time:
                raise DatasetValidationError("candle order is not strictly increasing")
            if candle.open_time - previous.open_time != step:
                raise DatasetValidationError("historical dataset contains a candle gap")
        previous = candle


def persist_dataset(
    session: Session,
    *,
    symbol: str,
    interval: str,
    requested_start: datetime,
    requested_end: datetime,
    candles: list[Candle],
) -> BacktestDataset:
    validate_dataset_candles(
        candles,
        symbol=symbol,
        interval=interval,
        requested_start=requested_start,
        requested_end=requested_end,
    )
    digest = canonical_dataset_sha256(candles)
    existing = session.exec(
        select(BacktestDataset).where(BacktestDataset.content_sha256 == digest)
    ).first()
    if existing is not None:
        raise DatasetValidationError("historical dataset already exists")

    dataset = BacktestDataset(
        symbol=normalize_symbol(symbol),
        interval=interval,
        provider=candles[0].provider,
        requested_start=_utc(requested_start),
        requested_end=_utc(requested_end),
        actual_start=candles[0].open_time,
        actual_end=candles[-1].close_time,
        candle_count=len(candles),
        content_sha256=digest,
        status="READY",
    )
    session.add(dataset)
    session.flush()

    for ordinal, candle in enumerate(candles):
        session.add(
            BacktestCandle(
                dataset_id=dataset.id,
                ordinal=ordinal,
                symbol=candle.symbol,
                interval=candle.interval,
                open_time=candle.open_time,
                close_time=candle.close_time,
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
                provider=candle.provider,
                provider_symbol=candle.provider_symbol,
            )
        )

    session.commit()
    session.refresh(dataset)
    return dataset
