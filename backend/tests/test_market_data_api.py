from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.market_data.contracts import Candle, Quote
from app.market_data.quality import MarketDataQualityError, MarketDataUnavailable
from app.market_data.router import get_market_data_service
from app.market_data.service import MarketDataService


NOW = datetime(2026, 8, 19, 12, 5, 30, tzinfo=timezone.utc)


class FakeProvider:
    name = "fake_real_provider"

    async def get_quote(self, symbol: str) -> Quote:
        return Quote(
            symbol="BTC/USDT",
            price=Decimal("65000.25"),
            observed_at=NOW - timedelta(seconds=2),
            received_at=NOW,
            provider=self.name,
            provider_symbol="BTCUSDT",
            timestamp_source="provider",
        )

    async def get_candles(self, symbol: str, *, interval: str, limit: int):
        candles = []
        for index in range(limit):
            open_time = NOW - timedelta(minutes=limit - index)
            candles.append(
                Candle(
                    symbol="BTC/USDT",
                    interval=interval,
                    open_time=open_time,
                    close_time=open_time + timedelta(minutes=1) - timedelta(milliseconds=1),
                    open=Decimal("100"),
                    high=Decimal("102"),
                    low=Decimal("99"),
                    close=Decimal("101"),
                    volume=Decimal("10"),
                    provider=self.name,
                    provider_symbol="BTCUSDT",
                )
            )
        return candles


class UnavailableProvider(FakeProvider):
    async def get_quote(self, symbol: str) -> Quote:
        raise MarketDataUnavailable("provider down")


class InvalidProvider(FakeProvider):
    async def get_quote(self, symbol: str) -> Quote:
        raise MarketDataQualityError("bad payload")


def _override(provider):
    app.dependency_overrides[get_market_data_service] = lambda: MarketDataService(provider)


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.pop(get_market_data_service, None)


@pytest.mark.asyncio
async def test_market_data_status_is_explicitly_real_and_has_no_synthetic_fallback():
    _override(FakeProvider())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/market-data/status")

    assert response.status_code == 200
    assert response.json() == {
        "provider": "fake_real_provider",
        "evidence_mode": "real",
        "synthetic_fallback": False,
        "execution_capability": False,
    }


@pytest.mark.asyncio
async def test_market_data_quote_exposes_provenance_and_real_evidence_mode():
    _override(FakeProvider())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/market-data/quote/BTCUSDT")

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "BTC/USDT"
    assert payload["provider"] == "fake_real_provider"
    assert payload["evidence_mode"] == "real"
    assert payload["timestamp_source"] == "provider"


@pytest.mark.asyncio
async def test_market_data_candles_expose_closed_series():
    _override(FakeProvider())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/market-data/candles/BTCUSDT",
            params={"interval": "1m", "limit": 2},
        )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert all(item["evidence_mode"] == "real" for item in payload)
    assert all(item["provider"] == "fake_real_provider" for item in payload)


@pytest.mark.asyncio
async def test_market_data_provider_unavailable_returns_503_without_fallback():
    _override(UnavailableProvider())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/market-data/quote/BTCUSDT")

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_market_data_quality_error_returns_502_without_repairing_payload():
    _override(InvalidProvider())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/market-data/quote/BTCUSDT")

    assert response.status_code == 502
    assert "quality" in response.json()["detail"].lower()
