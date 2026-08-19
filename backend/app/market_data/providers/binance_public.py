import asyncio
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Awaitable, Callable

import httpx

from app.market_data.contracts import Candle, Quote
from app.market_data.quality import (
    MarketDataQualityError,
    MarketDataUnavailable,
    interval_timedelta,
    normalize_symbol,
    provider_symbol,
    validate_candle_series,
    validate_quote_freshness,
)


Clock = Callable[[], datetime]
Sleep = Callable[[float], Awaitable[None]]


class BinancePublicMarketDataProvider:
    """Read-only Binance public REST market-data adapter.

    This adapter never authenticates and never places orders. Provider failures
    are surfaced as explicit exceptions; generated/mock fallbacks are forbidden.
    """

    name = "binance_public"
    default_base_url = "https://api.binance.com"

    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = None,
        base_url: str | None = None,
        clock: Clock | None = None,
        sleep: Sleep = asyncio.sleep,
        max_attempts: int = 3,
        timeout_seconds: float = 10.0,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self._client = client
        self._base_url = (base_url or self.default_base_url).rstrip("/")
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._sleep = sleep
        self._max_attempts = max_attempts
        self._timeout_seconds = timeout_seconds

    def _now_utc(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None:
            raise MarketDataQualityError("provider clock must be timezone-aware")
        return value.astimezone(timezone.utc)

    async def _send(self, path: str, params: dict) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                if self._client is not None:
                    response = await self._client.get(
                        path,
                        params=params,
                        timeout=self._timeout_seconds,
                    )
                else:
                    async with httpx.AsyncClient(base_url=self._base_url) as client:
                        response = await client.get(
                            path,
                            params=params,
                            timeout=self._timeout_seconds,
                        )

                if response.status_code == 429 or response.status_code >= 500:
                    last_error = MarketDataUnavailable(
                        f"Binance public API returned HTTP {response.status_code}"
                    )
                elif response.is_error:
                    raise MarketDataQualityError(
                        f"Binance public API rejected request with HTTP {response.status_code}"
                    )
                else:
                    return response
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc

            if attempt < self._max_attempts:
                await self._sleep(0.25 * (2 ** (attempt - 1)))

        raise MarketDataUnavailable("Binance public market data unavailable") from last_error

    async def _json(self, path: str, params: dict):
        response = await self._send(path, params)
        try:
            return response.json()
        except ValueError as exc:
            raise MarketDataQualityError("provider returned invalid JSON") from exc

    async def get_quote(self, symbol: str) -> Quote:
        canonical = normalize_symbol(symbol)
        raw_symbol = provider_symbol(canonical)
        payload = await self._json(
            "/api/v3/aggTrades",
            {"symbol": raw_symbol, "limit": 1},
        )

        if not isinstance(payload, list) or len(payload) != 1:
            raise MarketDataQualityError("unexpected aggTrades payload")

        item = payload[0]
        try:
            price = Decimal(str(item["p"]))
            observed_at = datetime.fromtimestamp(
                int(item["T"]) / 1000,
                tz=timezone.utc,
            )
        except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
            raise MarketDataQualityError("invalid aggTrade fields") from exc

        received_at = self._now_utc()
        try:
            quote = Quote(
                symbol=canonical,
                price=price,
                observed_at=observed_at,
                received_at=received_at,
                provider=self.name,
                provider_symbol=raw_symbol,
                timestamp_source="provider",
            )
        except ValueError as exc:
            raise MarketDataQualityError("invalid quote contract") from exc

        return validate_quote_freshness(quote, now=received_at)

    async def get_candles(
        self,
        symbol: str,
        *,
        interval: str = "1m",
        limit: int = 100,
    ) -> list[Candle]:
        if not 1 <= limit <= 1000:
            raise MarketDataQualityError("candle limit must be between 1 and 1000")
        interval_timedelta(interval)

        canonical = normalize_symbol(symbol)
        raw_symbol = provider_symbol(canonical)
        request_limit = min(limit + 1, 1000)
        payload = await self._json(
            "/api/v3/klines",
            {
                "symbol": raw_symbol,
                "interval": interval,
                "limit": request_limit,
            },
        )

        if not isinstance(payload, list):
            raise MarketDataQualityError("unexpected klines payload")

        now = self._now_utc()
        parsed: list[Candle] = []
        for row in payload:
            try:
                if not isinstance(row, list) or len(row) < 7:
                    raise ValueError("short kline row")
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
                raise MarketDataQualityError("invalid kline fields") from exc

            if candle.close_time <= now:
                parsed.append(candle)

        if len(parsed) < limit:
            raise MarketDataQualityError(
                f"provider returned only {len(parsed)} closed candles, expected {limit}"
            )

        selected = parsed[-limit:]
        return validate_candle_series(selected, interval=interval, now=now)
