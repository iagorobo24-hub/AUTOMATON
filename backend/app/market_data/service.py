from typing import Protocol

from .contracts import Candle, Quote


class MarketDataProvider(Protocol):
    name: str

    async def get_quote(self, symbol: str) -> Quote:
        ...

    async def get_candles(
        self,
        symbol: str,
        *,
        interval: str = "1m",
        limit: int = 100,
    ) -> list[Candle]:
        ...


class MarketDataService:
    """Provider-neutral boundary consumed by API and future trading domains."""

    def __init__(self, provider: MarketDataProvider):
        self.provider = provider

    def status(self) -> dict:
        return {
            "provider": self.provider.name,
            "evidence_mode": "real",
            "synthetic_fallback": False,
            "execution_capability": False,
        }

    async def get_quote(self, symbol: str) -> Quote:
        return await self.provider.get_quote(symbol)

    async def get_candles(
        self,
        symbol: str,
        *,
        interval: str = "1m",
        limit: int = 100,
    ) -> list[Candle]:
        return await self.provider.get_candles(symbol, interval=interval, limit=limit)
