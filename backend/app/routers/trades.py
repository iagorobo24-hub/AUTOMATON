from fastapi import APIRouter, Depends
from typing import List, Optional
from ..models.requests import TradeCreateRequest
from ..services.database import DatabaseService
from ..api.deps import get_db_service

router = APIRouter()

@router.get("/")
async def get_all_trades(
    limit: int = 100,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all trades across agents"""
    trades = await db_service.get_all_trades(limit)
    return {"trades": trades}

@router.post("/")
async def create_trade(
    request: TradeCreateRequest,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create/open a new trade"""
    trade = await db_service.create_trade(request)
    return trade.model_dump()
