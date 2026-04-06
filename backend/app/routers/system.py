from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from ..services.database import DatabaseService
from ..services.notifications import NotificationService
from ..services.mock_engine import MockEngine
from ..services.paper_engine import PaperTradingEngine
from ..services import registry
from ..api.deps import get_db_service, get_notification_service
from ..models.requests import AgentCreateRequest
from ..models.enums import AgentType

router = APIRouter()

# In-memory store, reset on server restart (intentional for dev mode)
_system_mode = "test"


class ModeRequest(BaseModel):
    mode: str


@router.get("/mode")
async def get_mode():
    """Get current system mode: 'test' or 'live'"""
    global _system_mode
    return {
        "mode": _system_mode,
        "label": "Prueba" if _system_mode == "test" else "En vivo",
        "description": "Datos simulados"
        if _system_mode == "test"
        else "Datos reales de Binance",
    }


@router.post("/mode")
async def set_mode(
    request: ModeRequest,
    db_service: DatabaseService = Depends(get_db_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """
    Switch system mode:
    - 'test': MockEngine only (simulated data, fast)
    - 'live': PaperTradingEngine only (real Binance data)
    """
    global _system_mode
    mode = request.mode.lower()
    if mode not in ("test", "live"):
        raise HTTPException(status_code=400, detail="Mode must be 'test' or 'live'")

    if mode == _system_mode:
        return {"mode": _system_mode, "message": "Already in this mode"}

    old_mode = _system_mode
    _system_mode = mode

    mock_engine = registry.get_mock_engine()
    paper_engine = registry.get_trading_engine()

    if mode == "test":
        if paper_engine:
            await paper_engine.stop()
            registry.set_trading_engine(None)
        if mock_engine:
            if not mock_engine.is_running:
                mock_engine.is_running = True
                import asyncio

                asyncio.create_task(mock_engine._price_loop())
                asyncio.create_task(mock_engine._agent_loop())
    else:
        if mock_engine:
            mock_engine.is_running = False
        if paper_engine is None or not paper_engine.is_running:
            paper_engine = PaperTradingEngine(db_service, notification_service)
            await paper_engine.start()
            registry.set_trading_engine(paper_engine)

    return {
        "mode": _system_mode,
        "switched_from": old_mode,
        "message": f"Changed to {'test' if _system_mode == 'test' else 'live'} mode",
    }


@router.post("/reset-agents")
async def reset_agents(
    initial_capital: float = 1000,
    db_service: DatabaseService = Depends(get_db_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Kill all agents and create 3 fresh genesis agents"""
    existing = await db_service.get_agents()
    for agent in existing:
        await db_service.db.agents.update_one(
            {"id": agent["id"]},
            {
                "$set": {
                    "status": "dead",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            },
        )

    from ..models.requests import AgentCreateRequest
    from ..models.enums import AgentType

    names = ["ADAN", "EVA", "LILITH"]
    agent_types = [AgentType.CRYPTO_TRADER, AgentType.CRYPTO_TRADER, AgentType.BUSINESS_SCOUT]
    created = []

    for i in range(3):
        req = AgentCreateRequest(
            name=names[i],
            agent_type=agent_types[i],
            initial_capital=initial_capital
        )
        agent = await db_service.create_agent(req)
        created.append({"id": agent.id, "name": agent.name, "capital": initial_capital})

    engine = registry.get_trading_engine()
    if engine and hasattr(engine, "active_positions"):
        engine.active_positions.clear()
        engine.total_trades = 0
        engine.total_pnl = 0.0
        engine.winning_trades = 0

    return {
        "success": True,
        "agents": created,
        "total_capital": initial_capital * 3,
        "message": f"3 agentes creados con €{initial_capital} cada uno",
    }
