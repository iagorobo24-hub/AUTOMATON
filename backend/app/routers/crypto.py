from fastapi import APIRouter, HTTPException, Query
import httpx
import logging
from datetime import datetime, timezone
from typing import Optional, Dict
from collections import OrderedDict

router = APIRouter()

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
crypto_cache: OrderedDict[str, tuple] = OrderedDict()
cache_ttl = 60
max_cache_size = 100  # Eviction limit to prevent memory leaks

async def fetch_crypto_data(endpoint: str, params: dict = None):
    cache_key = f"{endpoint}:{str(params)}"
    now = datetime.now(timezone.utc).timestamp()
    
    if cache_key in crypto_cache:
        cached_data, cached_time = crypto_cache[cache_key]
        if now - cached_time < cache_ttl:
            return cached_data
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{COINGECKO_BASE}{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Evict oldest entry if cache is full
            if len(crypto_cache) >= max_cache_size:
                crypto_cache.popitem(last=False)
            crypto_cache[cache_key] = (data, now)
            return data
        except Exception as e:
            logging.error(f"CoinGecko API error: {e}")
            raise HTTPException(status_code=503, detail="Crypto data service unavailable")

@router.get("/top-coins")
async def get_top_coins(limit: int = 10):
    data = await fetch_crypto_data("/coins/markets", {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d"
    })
    return {"coins": [
        {
            "id": coin["id"],
            "symbol": coin["symbol"].upper(),
            "name": coin["name"],
            "image": coin["image"],
            "current_price": coin["current_price"],
            "market_cap": coin["market_cap"],
            "market_cap_rank": coin["market_cap_rank"],
            "price_change_24h": coin.get("price_change_percentage_24h", 0),
            "price_change_7d": coin.get("price_change_percentage_7d_in_currency", 0),
            "volume_24h": coin["total_volume"]
        }
        for coin in data
    ]}

@router.get("/trending")
async def get_trending():
    data = await fetch_crypto_data("/search/trending")
    return {"trending": [
        {
            "id": coin["item"]["id"],
            "name": coin["item"]["name"],
            "symbol": coin["item"]["symbol"],
            "market_cap_rank": coin["item"]["market_cap_rank"],
            "thumb": coin["item"]["thumb"]
        }
        for coin in data.get("coins", [])[:7]
    ]}

@router.get("/price/{coin_id}")
async def get_coin_price(coin_id: str):
    data = await fetch_crypto_data(f"/simple/price", {
        "ids": coin_id,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true"
    })
    if coin_id not in data:
        raise HTTPException(status_code=404, detail="Coin not found")
    return {
        "coin_id": coin_id,
        "price_usd": data[coin_id]["usd"],
        "change_24h": data[coin_id].get("usd_24h_change", 0),
        "market_cap": data[coin_id].get("usd_market_cap", 0),
        "volume_24h": data[coin_id].get("usd_24h_vol", 0)
    }

@router.get("/history/{coin_id}")
async def get_coin_history(coin_id: str, days: int = 7):
    data = await fetch_crypto_data(f"/coins/{coin_id}/market_chart", {
        "vs_currency": "usd",
        "days": str(days)
    })
    return {
        "coin_id": coin_id,
        "prices": data.get("prices", []),
        "market_caps": data.get("market_caps", []),
        "volumes": data.get("total_volumes", [])
    }
