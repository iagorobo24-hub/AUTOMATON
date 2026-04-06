"""
Simulation Mode Router
Manages paper trading simulation with real market data but fake money.
Uses PaperTradingEngine for realistic 24/7 operation with configured capital.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timezone
from typing import Optional
from ..services.database import DatabaseService
from ..services.notifications import NotificationService
from ..services.paper_engine import PaperTradingEngine
from ..services.mock_engine import MockEngine
from ..services import registry
from ..api.deps import get_db_service, get_notification_service
from ..models.requests import AgentCreateRequest
from ..models.enums import AgentType

router = APIRouter()

# Simulation state
_simulation_state = {
    "active": False,
    "started_at": None,
    "initial_capital": 0,
    "num_agents": 0,
    "initial_total_capital": 0,
}


@router.get("/status")
async def get_simulation_status(
    db_service: DatabaseService = Depends(get_db_service),
):
    """Get current simulation status and live metrics"""
    paper_engine = registry.get_trading_engine()
    mock_engine = registry.get_mock_engine()

    is_paper_running = paper_engine is not None and getattr(paper_engine, "is_running", False)
    is_mock_running = mock_engine is not None and getattr(mock_engine, "is_running", False)

    state = {
        "active": is_paper_running,
        "mode": "paper" if is_paper_running else ("mock" if is_mock_running else "stopped"),
        "started_at": _simulation_state.get("started_at"),
        "initial_capital": _simulation_state.get("initial_capital", 0),
        "num_agents": _simulation_state.get("num_agents", 0),
        "initial_total_capital": _simulation_state.get("initial_total_capital", 0),
    }

    if is_paper_running and paper_engine:
        # Calculate live metrics
        agents = await db_service.get_agents()
        total_balance = sum(
            a.get("finances", {}).get("current_balance", 0)
            for a in agents
        )
        total_trades = getattr(paper_engine, "total_trades", 0)
        total_pnl = getattr(paper_engine, "total_pnl", 0.0)
        winning = getattr(paper_engine, "winning_trades", 0)
        win_rate = (winning / total_trades * 100) if total_trades > 0 else 0

        active = [a for a in agents if a.get("status") == "active"]
        replicating = [a for a in agents if a.get("status") == "replicating"]
        dead = [a for a in agents if a.get("status") == "dead"]

        started = _simulation_state.get("started_at")
        uptime_seconds = 0
        if started:
            started_dt = datetime.fromisoformat(started)
            uptime_seconds = (datetime.now(timezone.utc) - started_dt).total_seconds()

        state.update({
            "total_balance": round(total_balance, 2),
            "total_pnl": round(total_pnl, 2),
            "pnl_percent": round((total_pnl / state["initial_total_capital"] * 100) if state["initial_total_capital"] > 0 else 0, 2),
            "total_trades": total_trades,
            "win_rate": round(win_rate, 1),
            "active_agents": len(active) + len(replicating),
            "dead_agents": len(dead),
            "replications": sum(1 for a in agents if a.get("lineage", {}).get("parent_id")),
            "uptime_seconds": int(uptime_seconds),
        })

    return state


@router.post("/start")
async def start_simulation(
    capital: float = Query(1000, ge=50, description="Initial capital per agent"),
    agents: int = Query(3, ge=1, le=10, description="Number of genesis agents"),
    db_service: DatabaseService = Depends(get_db_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """
    Start paper trading simulation:
    1. Stops any existing engines
    2. Kills all existing agents
    3. Creates fresh genesis agents with configured capital
    4. Starts PaperTradingEngine with real Binance data
    """
    global _simulation_state

    # Stop existing engines
    paper_engine = registry.get_trading_engine()
    mock_engine = registry.get_mock_engine()

    if paper_engine and getattr(paper_engine, "is_running", False):
        await paper_engine.stop()
    if mock_engine:
        mock_engine.is_running = False

    # Kill all existing agents
    existing = await db_service.get_agents()
    for agent in existing:
        await db_service.db.agents.update_one(
            {"id": agent["id"]},
            {"$set": {"status": "dead", "updated_at": datetime.now(timezone.utc).isoformat()}},
        )

    # Create genesis agents
    genesis_names = ["ADAN", "EVA", "LILITH", "CAIN", "ABEL", "SETH", "ENOS", "NOAH", "ABRAM", "ISAAC"]
    created = []

    for i in range(min(agents, len(genesis_names))):
        req = AgentCreateRequest(
            name=genesis_names[i],
            agent_type=AgentType.CRYPTO_TRADER,
            initial_capital=capital,
        )
        agent = await db_service.create_agent(req)
        # Mark as simulation agent
        await db_service.db.agents.update_one(
            {"id": agent.id},
            {"$set": {"metadata.simulation": True}},
        )
        # Log activity and notification for each simulation agent
        await notification_service.notify_agent_created(agent.id, agent.name, capital)
        created.append({"id": agent.id, "name": agent.name})

    total_capital = capital * len(created)

    # Clear any stale positions
    if paper_engine:
        paper_engine.active_positions.clear()
        paper_engine.total_trades = 0
        paper_engine.total_pnl = 0.0
        paper_engine.winning_trades = 0

    # Start PaperTradingEngine (real market data, simulated execution)
    new_engine = PaperTradingEngine(db_service, notification_service)
    await new_engine.start()
    registry.set_trading_engine(new_engine)

    # Update simulation state
    _simulation_state = {
        "active": True,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "initial_capital": capital,
        "num_agents": len(created),
        "initial_total_capital": total_capital,
    }

    # Log simulation start activity
    await notification_service.log_activity(
        type="simulation_started",
        title="Simulación Iniciada",
        description=f"{len(created)} agentes con €{capital} cada uno (Total: €{total_capital})",
        icon="play",
        color="green",
        amount=total_capital,
        link="/simulation",
    )
    await notification_service.create_notification(
        type="system_info",
        title="Simulación Activa",
        message=f"{len(created)} agentes operando con €{capital} cada uno",
        icon="bot",
        color="green",
        link="/simulation",
    )

    return {
        "success": True,
        "mode": "paper",
        "agents": created,
        "total_capital": total_capital,
        "message": f"Simulación iniciada: {len(created)} agentes con €{capital} cada uno",
    }


@router.post("/stop")
async def stop_simulation(
    db_service: DatabaseService = Depends(get_db_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Stop the paper trading simulation"""
    global _simulation_state

    paper_engine = registry.get_trading_engine()

    if paper_engine and getattr(paper_engine, "is_running", False):
        await paper_engine.stop()
        registry.set_trading_engine(None)

    # Log simulation stop activity
    await notification_service.log_activity(
        type="simulation_stopped",
        title="Simulación Detenida",
        description="La simulación de trading ha sido detenida",
        icon="pause",
        color="yellow",
        link="/simulation",
    )
    await notification_service.create_notification(
        type="system_info",
        title="Simulación Detenida",
        message="La simulación de trading ha sido detenida manualmente",
        icon="pause",
        color="yellow",
        link="/simulation",
    )

    _simulation_state = {
        "active": False,
        "started_at": None,
        "initial_capital": 0,
        "num_agents": 0,
        "initial_total_capital": 0,
    }

    return {
        "success": True,
        "message": "Simulación detenida",
    }


@router.post("/reset")
async def reset_simulation(
    capital: float = Query(1000, ge=50),
    agents: int = Query(3, ge=1, le=10),
    db_service: DatabaseService = Depends(get_db_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Stop, clean, and restart simulation (convenience endpoint)"""
    await stop_simulation(db_service)
    return await start_simulation(capital, agents, db_service, notification_service)
