from datetime import datetime, timedelta, timezone
from decimal import Decimal

import httpx
import pytest

from app.backtesting.providers.binance_history import BinanceHistoricalDataProvider
from app.market_data.quality import MarketDataUnavailable

UTC = timezone.utc
START = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
END = START + timedelta(minutes=3)


async def _no_sleep(_seconds: float):
    return None


def _client(handler):
    return httpx.AsyncClient(
        base_url="https://api.binance.test",
        transport=httpx.MockTransport(handler),
    )


def _row(open_time: datetime, close: str):
    open_ms = int(open_time.timestamp() * 1000)
    close_ms = int((open_time + timedelta(minutes=1) - timedelta(milliseconds=1)).timestamp() * 1000)
    return [
        open_ms,
        "100",
        "102",
        "99",
        close,
        "10",
        close_ms,
        "0",
        1,
        "0",
        "0",
        "0",
    ]


@pytest.mark.asyncio
async def test_historical_provider_paginates_forward_with_explicit_window():
    requests = []

    def handler(request: httpx.Request):
        requests.append(dict(request.url.params))
        start_ms = int(request.url.params["startTime"])
        if start_ms == int(START.timestamp() * 1000):
            return httpx.Response(200, json=[_row(START, "100.5"), _row(START + timedelta(minutes=1), "101.5")])
        return httpx.Response(200, json=[_row(START + timedelta(minutes=2), "102.5")])

    async with _client(handler) as client:
        provider = BinanceHistoricalDataProvider(client=client, sleep=_no_sleep, page_limit=2)
        candles = await provider.fetch_candles("btc-usdt", "1m", START, END)

    assert len(candles) == 3
    assert [c.open_time for c in candles] == [START, START + timedelta(minutes=1), START + timedelta(minutes=2)]
    assert [c.close for c in candles] == [Decimal("100.5"), Decimal("101.5"), Decimal("102.5")]
    assert all(c.provider == "binance_public_history" for c in candles)
    assert all(c.evidence_mode == "real" for c in candles)
    assert len(requests) == 2
    assert requests[0]["symbol"] == "BTCUSDT"
    assert requests[0]["interval"] == "1m"
    assert requests[0]["limit"] == "2"
    assert int(requests[1]["startTime"]) > int(requests[0]["startTime"])


@pytest.mark.asyncio
async def test_historical_provider_never_returns_candles_beyond_requested_end():
    def handler(_request: httpx.Request):
        return httpx.Response(
            200,
            json=[
                _row(START, "100.5"),
                _row(START + timedelta(minutes=1), "101.5"),
                _row(START + timedelta(minutes=2), "102.5"),
                _row(START + timedelta(minutes=3), "103.5"),
            ],
        )

    async with _client(handler) as client:
        provider = BinanceHistoricalDataProvider(client=client, sleep=_no_sleep, page_limit=1000)
        candles = await provider.fetch_candles("BTC/USDT", "1m", START, END)

    assert [c.open_time for c in candles] == [START, START + timedelta(minutes=1), START + timedelta(minutes=2)]
    assert all(c.close_time <= END for c in candles)


@pytest.mark.asyncio
async def test_historical_provider_fails_closed_after_bounded_retries():
    attempts = 0

    def handler(_request: httpx.Request):
        nonlocal attempts
        attempts += 1
        return httpx.Response(503, json={"msg": "unavailable"})

    async with _client(handler) as client:
        provider = BinanceHistoricalDataProvider(
            client=client,
            sleep=_no_sleep,
            max_attempts=3,
        )
        with pytest.raises(MarketDataUnavailable):
            await provider.fetch_candles("BTC/USDT", "1m", START, END)

    assert attempts == 3
