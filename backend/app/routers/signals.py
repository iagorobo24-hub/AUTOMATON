from fastapi import APIRouter, Depends
from typing import Optional
from ..services.database import DatabaseService
from ..api.deps import get_db_service

router = APIRouter()


@router.get("/")
async def get_signals(
    symbol: Optional[str] = None, db_service: DatabaseService = Depends(get_db_service)
):
    """Get active trading signals"""
    signals = await db_service.get_active_signals(symbol)
    return {"signals": signals}
