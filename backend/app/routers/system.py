"""
System router - app mode management
"""
from fastapi import APIRouter, Body
from ..core.mode import get_mode, set_mode, is_real, is_test

router = APIRouter()


@router.get("/mode")
async def get_system_mode():
    """Get current system mode"""
    mode = get_mode()
    return {
        "mode": mode,
        "is_real": is_real(),
        "is_test": is_test()
    }


@router.post("/mode")
async def set_system_mode(body: dict = Body(...)):
    """Switch between real and test mode. Body: {"mode": "real" | "test"}"""
    new_mode = body.get("mode", "")
    if new_mode not in ("real", "test"):
        return {"success": False, "error": "Mode must be 'real' or 'test'"}
    set_mode(new_mode)
    return {
        "success": True,
        "mode": new_mode,
        "message": f"Switched to {'Real' if new_mode == 'real' else 'Test'} mode"
    }
