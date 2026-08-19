import asyncio
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Awaitable, Callable

import httpx

from app.market_data.contracts import Candle
from app.market_data.quality import (
    MarketDataQualityError,
    MarketDataUnavailable,
    interval_timedelta,
    normalize_symbol,
    provider_symbol,
)

Sleep = Callable[[float], Awaitable[None]]


class BinanceHistoricalDataProvider:
    """Read-only historical Binance kline provider for immutable backtest datasets."""

    name = "binance_public_history"
    default_base_url = "https://data-api.binance.vision"

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        base_url: str | None = None,
        sleep: Sleep = asyncio.sleep,
        max_attempts: int = 3,
        timeout_seconds: float = 10.0,
        max_retry_after_seconds: float = 10.0,
        page_limit: int = 1000,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if not 1 <= page_limit <= 1000:
            raise ValueError("page_limit must be between 1 and 1000")
        self._client = client
        self._base_url = (base_url or self.default_base_url).rstrip("/")
        self._sleep = sleep
        self._max_attempts = max_attempts
        self._timeout_seconds = timeout_seconds
        self._max_retry_after_seconds = max_retry_after_seconds
        self._page_limit = page_limit

    def _retry_delay(self, response: httpx.Response, attempt: int) -> float:
        if response.status_code == 429:
            raw = response.headers.get("Retry-After")
            if raw is not None:
                try:
                    delay = max(0.0, float(raw))
                except ValueError as exc:
                    raise MarketDataUnavailable("Binance returned invalid Retry-After") from exc
                if delay > self._max_retry_after_seconds:
                    raise MarketDataUnavailable("Binance rate-limit wait exceeds retry window")
                return delay
        return 0.25 * (2 ** (attempt - 1))

    async def _send(self, params: dict) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            retry_delay: float | None = None
            try:
                if self._client is not None:
                    response = await self._client.get(
                        "/api/v3/klines",
                        params=params,
                        timeout=self._timeout_seconds,
                    )
                else:
                    async with httpx.AsyncClient(base_url=self._base_url) as client:
                        response = await client.get(
                            "/api/v3/klines",
                            params=params,
                            timeout=self._timeout_seconds,
                        )
                if response.status_code == 418:
                    raise MarketDataUnavailable("Binance market-data IP access is temporarily banned")
                if response.status_code == 429 or response.status_code >= 500:
                    last_error = MarketDataUnavailable(
                        f"Binance public API returned HTTP {response.status_code}"
                    )
                    retry_delay = self._retry_delay(response, attempt)
                elif response.is_error:
                    raise MarketDataQualityError(
                        f"Binance public API rejected historical request with HTTP {response.status_code}"
                    )
                else:
                    return response
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc
                retry_delay = 0.25 * (2 ** (attempt - 1))

            if attempt < self._max_attempts and retry_delay is not None:
                await self._sleep(retry_delay)

        raise MarketDataUnavailable("Binance historical market data unavailable") from last_error

    async def _page(self, params: dict) -> list:
        response = await self._send(params)
        try:
            payload = response.json()
        except ValueError as exc:
            raise MarketDataQualityError("historical provider returned invalid JSON") from exc
        if not isinstance(payload, list):
            raise MarketDataQualityError("unexpected historical klines payload")
        return payload

    @staticmethod
    def _utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            raise MarketDataQualityError("historical window must be timezone-aware")
        return value.astimezone(timezone.utc)

    async def fetch_candles(
        self,
        symbol: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        start = self._utc(start)
        end = self._utc(end)
        if end <= start:
            raise MarketDataQualityError("historical end must be after start")

        step = interval_timedelta(interval)
        step_ms = int(step.total_seconds() * 1000)
        canonical = normalize_symbol(symbol)
        raw_symbol = provider_symbol(canonical)
        cursor_ms = int(start.timestamp() * 1000)
        end_ms = int(end.timestamp() * 1000)
        candles: list[Candle] = []

        while cursor_ms < end_ms:
            payload = await self._page(
                {
                    "symbol": raw_symbol,
                    "interval": interval,
                    "startTime": cursor_ms,
                    "endTime": end_ms - 1,
                    "limit": self._page_limit,
                }
            )
            if not payload:
                break

            page_candles: list[Candle] = []
            for row in payload:
                try:
                    if not isinstance(row, list) or len(row) < 7:
                        raise ValueError("short historical kline row")
                    candle = Candle(
                        symbol=canonical,
                        interval=interval,
                        open_time=datetime.fromtimestamp(int(row[0]) / 1000, tz=timezone.utc),
                        close_time=datetime.fromtimestamp(int(row[6]) / 1000, tz=timezone.utc),
                        open=Decimal(str(row[1])),
                        high=Decimal(str(row[2])),
                        low=Decimal(str(row[3])),
                        close=Decimal(str(row[4])),
                        volume=Decimal(str(row[5])),
                        provider=self.name,
                        provider_symbol=raw_symbol,
                    )
                except (TypeError, ValueError, InvalidOperation) as exc:
                    raise MarketDataQualityError("invalid historical kline fields") from exc
                if candle.open_time >= start and candle.close_time <= end:
                    page_candles.append(candle)

            if page_candles:
                candles.extend(page_candles)
                next_cursor_ms = int(page_candles[-1].open_time.timestamp() * 1000) + step_ms
            else:
                try:
                    last_open_ms = int(payload[-1][0])
                except (TypeError, ValueError, IndexError) as exc:
                    raise MarketDataQualityError("invalid historical pagination cursor") from exc
                next_cursor_ms = last_open_ms + step_ms

            if next_cursor_ms <= cursor_ms:
                raise MarketDataQualityError("historical provider pagination did not advance")
            cursor_ms = next_cursor_ms

            if len(payload) < self._page_limit:
                break

        if not candles:
            raise MarketDataQualityError("historical provider returned no closed candles")
        return candles
