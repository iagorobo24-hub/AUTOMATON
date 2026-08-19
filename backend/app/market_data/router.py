from fastapi import APIRouter, Depends, HTTPException, Query

from .contracts import Candle, Quote
from .providers.binance_public import BinancePublicMarketDataProvider
from .quality import MarketDataQualityError, MarketDataUnavailable
from .service import MarketDataService


router = APIRouter()
_default_service = MarketDataService(BinancePublicMarketDataProvider())


def get_market_data_service() -> MarketDataService:
    return _default_service


def _provider_error(exc: Exception) -> HTTPException:
    if isinstance(exc, MarketDataUnavailable):
        return HTTPException(
            status_code=503,
            detail="Real market-data provider unavailable; no synthetic fallback was used",
        )
    return HTTPException(
        status_code=502,
        detail="Real market-data quality validation failed; payload was rejected",
    )


@router.get("/status")
def get_status(service: MarketDataService = Depends(get_market_data_service)) -> dict:
    return service.status()


@router.get("/quote/{symbol}", response_model=Quote)
async def get_quote(
    symbol: str,
    service: MarketDataService = Depends(get_market_data_service),
) -> Quote:
    try:
        return await service.get_quote(symbol)
    except (MarketDataUnavailable, MarketDataQualityError) as exc:
        raise _provider_error(exc) from exc


@router.get("/candles/{symbol}", response_model=list[Candle])
async def get_candles(
    symbol: str,
    interval: str = Query(default="1m"),
    limit: int = Query(default=100, ge=1, le=1000),
    service: MarketDataService = Depends(get_market_data_service),
) -> list[Candle]:
    try:
        return await service.get_candles(symbol, interval=interval, limit=limit)
    except (MarketDataUnavailable, MarketDataQualityError) as exc:
        raise _provider_error(exc) from exc
