from fastapi import APIRouter, Depends
from typing import List
from ..services.database import DatabaseService
from ..api.deps import get_db_service

router = APIRouter()

@router.get("/")
async def get_risk_profiles(
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all risk profiles"""
    profiles = await db_service.get_risk_profiles()
    return {"profiles": profiles}

@router.post("/")
async def create_risk_profile(
    name: str, 
    description: str = "",
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create a new risk profile"""
    profile = await db_service.create_risk_profile(name=name, description=description)
    return profile.model_dump()
