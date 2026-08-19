from datetime import datetime, timezone
from decimal import Decimal

import httpx
import pytest

from app.market_data.providers.binance_public import BinancePublicMarketDataProvider
from app.market_data.quality import MarketDataQualityError, MarketDataUnavailable


NOW = datetime(2026, 8, 19, 12, 5, 30, tzinfo=timezone.utc)


async def _no_sleep(_seconds: float):
    return None


def _client(handler):
    return httpx.AsyncClient(
        base_url="https://api.binance.test",
        transport=httpx.MockTransport(handler),
    )


def test_default_base_url_is_binance_market_data_only_host():
    provider = BinancePublicMarketDataProvider()
    assert provider.default_base_url == "https://data-api.binance.vision"


@pytest.mark.asyncio
async def test_quote_uses_real_provider_timestamp_and_never_mock_data():
    def handler(request: httpx.Request):
        assert request.url.path == "/api/v3/aggTrades"
        assert request.url.params["symbol"] == "BTCUSDT"
        assert request.url.params["limit"] == "1"
        return httpx.Response(
            200,
            json=[{"a": 1, "p": "65000.25", "q": "0.01", "T": 1787141110000}],
        )

    async with _client(handler) as client:
        provider = BinancePublicMarketDataProvider(
            client=client,
            clock=lambda: NOW,
            sleep=_no_sleep,
        )
        quote = await provider.get_quote("btc-usdt")

    assert quote.symbol == "BTC/USDT"
    assert quote.provider_symbol == "BTCUSDT"
    assert quote.provider == "binance_public"
    assert quote.evidence_mode == "real"
    assert quote.timestamp_source == "provider"
    assert quote.price == Decimal("65000.25")
    assert quote.observed_at == datetime.fromtimestamp(1787141110, tz=timezone.utc)


@pytest.mark.asyncio
async def test_candles_return_only_closed_real_candles_in_utc():
    def kline(open_ms, close_ms, open_, high, low, close, volume):
        return [open_ms, open_, high, low, close, volume, close_ms, "0", 1, "0", "0", "0"]

    rows = [
        kline(1787140980000, 1787141039999, "100", "102", "99", "101", "10"),
        kline(1787141040000, 1787141099999, "101", "103", "100", "102", "12"),
        # Current/open candle: close time is after NOW and must never be returned.
        kline(1787141100000, 1787141159999, "102", "104", "101", "103", "8"),
    ]

    def handler(request: httpx.Request):
        assert request.url.path == "/api/v3/klines"
        assert request.url.params["symbol"] == "BTCUSDT"
        assert request.url.params["interval"] == "1m"
        return httpx.Response(200, json=rows)

    async with _client(handler) as client:
        provider = BinancePublicMarketDataProvider(
            client=client,
            clock=lambda: NOW,
            sleep=_no_sleep,
        )
        candles = await provider.get_candles("BTC/USDT", interval="1m", limit=2)

    assert len(candles) == 2
    assert [c.close for c in candles] == [Decimal("101"), Decimal("102")]
    assert all(c.close_time <= NOW for c in candles)
    assert all(c.open_time.tzinfo == timezone.utc for c in candles)


@pytest.mark.asyncio
async def test_provider_failure_fails_closed_without_generated_fallback():
    attempts = 0

    def handler(_request: httpx.Request):
        nonlocal attempts
        attempts += 1
        return httpx.Response(503, json={"msg": "unavailable"})

    async with _client(handler) as client:
        provider = BinancePublicMarketDataProvider(
            client=client,
            clock=lambda: NOW,
            sleep=_no_sleep,
            max_attempts=3,
        )
        with pytest.raises(MarketDataUnavailable):
            await provider.get_quote("BTC/USDT")

    assert attempts == 3


@pytest.mark.asyncio
async def test_rate_limit_honors_retry_after_before_retrying():
    attempts = 0
    sleeps = []

    async def record_sleep(seconds: float):
        sleeps.append(seconds)

    def handler(_request: httpx.Request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, headers={"Retry-After": "2"}, json={"msg": "rate limited"})
        return httpx.Response(
            200,
            json=[{"a": 1, "p": "65000.25", "q": "0.01", "T": 1787141110000}],
        )

    async with _client(handler) as client:
        provider = BinancePublicMarketDataProvider(
            client=client,
            clock=lambda: NOW,
            sleep=record_sleep,
            max_attempts=2,
        )
        quote = await provider.get_quote("BTC/USDT")

    assert quote.price == Decimal("65000.25")
    assert attempts == 2
    assert sleeps == [2.0]


@pytest.mark.asyncio
async def test_malformed_provider_payload_is_rejected_not_repaired():
    def handler(_request: httpx.Request):
        return httpx.Response(200, json=[{"p": "not-a-price", "T": 1787141110000}])

    async with _client(handler) as client:
        provider = BinancePublicMarketDataProvider(
            client=client,
            clock=lambda: NOW,
            sleep=_no_sleep,
        )
        with pytest.raises(MarketDataQualityError):
            await provider.get_quote("BTC/USDT")
