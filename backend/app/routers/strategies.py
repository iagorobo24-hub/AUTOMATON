from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..services.database import DatabaseService
from ..api.deps import get_db_service

router = APIRouter()

@router.get("/")
async def get_strategies(
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all trading strategies"""
    strategies = await db_service.get_strategies()
    return {"strategies": strategies}

@router.post("/")
async def create_strategy(
    name: str,
    description: str = "",
    type: str = "momentum",
    timeframe: str = "4h",
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create a new trading strategy"""
    strategy = await db_service.create_strategy(
        name=name,
        description=description,
        type=type,
        timeframe=timeframe
    )
    return strategy.model_dump()

@router.get("/{strategy_id}")
async def get_strategy(
    strategy_id: str,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get strategy by ID"""
    strategy = await db_service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy
