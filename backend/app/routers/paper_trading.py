from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timezone
from ..services.database import DatabaseService
from ..services.notifications import NotificationService
from ..services.paper_engine import PaperTradingEngine
from ..services.registry import get_trading_engine
from ..api.deps import get_db_service, get_notification_service

router = APIRouter()


@router.post("/setup")
async def setup_paper_trading(
    initial_capital: float = Query(default=1000),
    agent_count: int = Query(default=3),
    db_service: DatabaseService = Depends(get_db_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """
    Setup paper trading environment:
    - Clean existing agents
    - Create genesis agents with specified capital
    - Start paper trading engine with real market data
    """
    existing = await db_service.get_agents()
    if existing:
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

    agent_names = ["ADAN", "EVA", "LILITH"]
    agent_types = ["crypto_analyzer", "trader", "business_scout"]
    created = []

    for i in range(min(agent_count, 3)):
        from ..models.requests import AgentCreateRequest

        request = AgentCreateRequest(
            name=agent_names[i], type=agent_types[i], initial_capital=initial_capital
        )
        agent = await db_service.create_agent(request)
        created.append({"id": agent.id, "name": agent.name, "capital": initial_capital})

    total_capital = initial_capital * len(created)

    engine = get_trading_engine()
    if engine is None:
        engine = PaperTradingEngine(db_service, notification_service)
        await engine.start()
        from ..services import registry

        registry.set_trading_engine(engine)

    return {
        "success": True,
        "agents": created,
        "total_capital": total_capital,
        "mode": "paper_trading",
        "data_source": "binance_public",
        "message": f"Paper trading started with {len(created)} agents, ${total_capital:.0f} total capital",
    }


@router.get("/status")
async def get_paper_trading_status():
    """Get paper trading engine status"""
    engine = get_trading_engine()
    if engine is None:
        return {"status": "not_running", "message": "Paper trading engine not started"}
    return engine.get_status()


@router.get("/positions")
async def get_paper_positions():
    """Get active paper trading positions"""
    engine = get_trading_engine()
    if engine is None:
        return {"count": 0, "positions": []}
    return {
        "count": len(engine.active_positions),
        "positions": list(engine.active_positions.values()),
    }


@router.post("/reset")
async def reset_paper_trading(
    initial_capital: float = Query(default=1000),
    db_service: DatabaseService = Depends(get_db_service),
):
    """Reset paper trading - kill all agents and start fresh"""
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

    engine = get_trading_engine()
    if engine:
        engine.active_positions.clear()
        engine.total_trades = 0
        engine.total_pnl = 0.0
        engine.winning_trades = 0

    return {
        "success": True,
        "message": "Paper trading reset. Use /setup to start fresh.",
    }
