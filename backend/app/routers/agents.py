from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timezone
from ..models.enums import AgentStatus
from ..models.requests import AgentCreateRequest, AgentReplicateRequest
from ..services.database import DatabaseService
from ..services.notifications import NotificationService
from ..api.deps import get_db_service, get_notification_service
from ..core.mode import get_mode

router = APIRouter()


@router.get("/")
async def get_agents(
    status: Optional[str] = None,
    mode: Optional[str] = Query(None, description="Filter by mode: 'real' or 'test'. Defaults to current global mode."),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all agents filtered by current mode (or override with ?mode=real/test)"""
    filter_mode = mode if mode is not None else get_mode()
    status_enum = AgentStatus(status) if status else None
    agents = await db_service.get_agents(status=status_enum, mode=filter_mode)
    return {"agents": agents}


@router.get("/status-summary")
async def get_agents_status_summary(
    mode: Optional[str] = Query(None),
    db_service: DatabaseService = Depends(get_db_service),
):
    """Get summary of agent statuses for current mode"""
    filter_mode = mode if mode is not None else get_mode()
    agents = await db_service.get_agents(mode=filter_mode)

    summary = {
        "total": len(agents),
        "active": len([a for a in agents if a.get("status") == "active"]),
        "paused": len([a for a in agents if a.get("status") == "paused"]),
        "replicating": len([a for a in agents if a.get("status") == "replicating"]),
        "dying": len([a for a in agents if a.get("status") == "dying"]),
        "dead": len([a for a in agents if a.get("status") == "dead"]),
        "hibernating": len([a for a in agents if a.get("status") == "hibernating"]),
    }

    return summary


@router.post("/")
async def create_agent(
    request: AgentCreateRequest,
    db_service: DatabaseService = Depends(get_db_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Create a new agent in current mode"""
    agent = await db_service.create_agent(request)

    # Mark agent with current mode
    current_mode = get_mode()
    await db_service.db.agents.update_one(
        {"id": agent.id},
        {"$set": {"metadata.mode": current_mode}},
    )

    await notification_service.notify_agent_created(
        agent.id, agent.name, request.initial_capital
    )

    return agent.model_dump()


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str, db_service: DatabaseService = Depends(get_db_service)
):
    """Get agent by ID with full details"""
    agent = await db_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/{agent_id}/replicate")
async def replicate_agent(
    agent_id: str,
    request: AgentReplicateRequest = None,
    db_service: DatabaseService = Depends(get_db_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Replicate an agent (create child with inherited traits)"""
    if request is None:
        request = AgentReplicateRequest()

    try:
        parent = await db_service.get_agent(agent_id)
        child = await db_service.replicate_agent(agent_id, request)
        if not child:
            raise HTTPException(status_code=404, detail="Parent agent not found")

        await notification_service.notify_agent_replicated(
            parent["name"], child.name, child.id, child.finances.current_balance
        )

        return {
            "parent_id": agent_id,
            "child": child.model_dump(),
            "message": "Agent replicated successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{agent_id}")
async def destroy_agent(
    agent_id: str, db_service: DatabaseService = Depends(get_db_service)
):
    """Destroy/terminate an agent - removes from database with cascade"""
    agent = await db_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Cascade delete related data
    await db_service.db.trades.delete_many({"agent_id": agent_id})
    await db_service.db.wallets.delete_one({"agent_id": agent_id})
    await db_service.db.activity_feed.delete_many({"agent_id": agent_id})
    await db_service.db.agents.delete_one({"id": agent_id})

    return {
        "message": f"Agent {agent_id} destroyed",
        "final_balance": agent.get("finances", {}).get("current_balance", 0),
    }


@router.post("/{agent_id}/simulate-trade")
async def simulate_trade(
    agent_id: str,
    profit: float = Query(default=0),
    db_service: DatabaseService = Depends(get_db_service),
):
    """Simulate a trade for an agent"""
    try:
        result = await db_service.simulate_trade(agent_id, profit)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{agent_id}/deposit")
async def deposit_to_agent(
    agent_id: str,
    amount: float = Query(default=0),
    db_service: DatabaseService = Depends(get_db_service),
):
    """Deposit funds into an agent's wallet"""
    agent = await db_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    current = agent.get("finances", {}).get("current_balance", 0)
    await db_service.db.agents.update_one(
        {"id": agent_id},
        {
            "$set": {
                "finances.current_balance": current + amount,
                "finances.available_balance": current + amount,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        },
    )
    return {"success": True, "new_balance": current + amount, "deposited": amount}


@router.patch("/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status: str,
    reason: str = None,
    db_service: DatabaseService = Depends(get_db_service),
):
    """Update agent status"""
    try:
        status_enum = AgentStatus(status)
        await db_service.update_agent_status(agent_id, status_enum, reason)
        return {"message": f"Agent status updated to {status}"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")


@router.get("/{agent_id}/trades")
async def get_agent_trades(
    agent_id: str,
    limit: int = 100,
    db_service: DatabaseService = Depends(get_db_service),
):
    """Get trade history for an agent"""
    trades = await db_service.get_trades(agent_id, limit)
    return {"trades": trades}


@router.get("/{agent_id}/wallet")
async def get_agent_wallet(
    agent_id: str, db_service: DatabaseService = Depends(get_db_service)
):
    """Get wallet for an agent"""
    wallet = await db_service.get_wallet(agent_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@router.get("/{agent_id}/lineage")
async def get_agent_lineage(
    agent_id: str, db_service: DatabaseService = Depends(get_db_service)
):
    """Get lineage tree for an agent family"""
    agent = await db_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    root_id = agent.get("lineage", {}).get("root_ancestor_id", agent_id)
    await db_service.rebuild_lineage_tree(root_id)
    lineage = await db_service.get_agent_lineage(root_id)
    return lineage or {"message": "No lineage data available"}


@router.post("/pause-all")
async def pause_all_agents(
    db_service: DatabaseService = Depends(get_db_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Pausar todos los agentes activos"""
    agents = await db_service.get_agents(status=AgentStatus.ACTIVE)
    paused_count = 0

    for agent in agents:
        await db_service.update_agent_status(
            agent["id"], AgentStatus.PAUSED, reason="pausa_masiva"
        )
        await notification_service.log_activity(
            type="agent_paused",
            title="Agente Pausado",
            description=f"{agent['name']} pausado por acción masiva",
            icon="pause",
            color="yellow",
            agent_id=agent["id"],
            agent_name=agent["name"],
        )
        paused_count += 1

    if paused_count > 0:
        await notification_service.create_notification(
            type="system_info",
            title="Todos los Agentes Pausados",
            message=f"{paused_count} agentes han sido pausados",
            icon="pause",
            color="yellow",
            priority="high",
        )

    return {"success": True, "paused_count": paused_count}


@router.post("/resume-all")
async def resume_all_agents(
    db_service: DatabaseService = Depends(get_db_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Resume all paused agents"""
    agents = await db_service.get_agents(status=AgentStatus.PAUSED)
    resumed_count = 0

    for agent in agents:
        await db_service.update_agent_status(
            agent["id"], AgentStatus.ACTIVE, reason="bulk_resume"
        )
        resumed_count += 1

    if resumed_count > 0:
        await notification_service.create_notification(
            type="system_info",
            title="Agentes Reanudados",
            message=f"{resumed_count} agentes han sido reanudados",
            icon="play",
            color="green",
            priority="medium",
        )

    return {"success": True, "resumed_count": resumed_count}


@router.post("/emergency-stop")
async def emergency_stop_all_agents(
    confirm: bool = Query(default=False),
    db_service: DatabaseService = Depends(get_db_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Parada de emergencia - termina TODOS los agentes inmediatamente."""
    if not confirm:
        return {"success": False, "error": "confirmation_required"}

    all_agents = await db_service.get_agents()
    active_agents = [a for a in all_agents if a.get("status") != "dead"]

    terminated_count = 0
    total_balance_lost = 0

    for agent in active_agents:
        balance = agent.get("finances", {}).get("current_balance", 0) or agent.get(
            "balance", 0
        )
        total_balance_lost += balance
        await db_service.update_agent_status(
            agent["id"], AgentStatus.DEAD, reason="parada_emergencia"
        )
        await notification_service.notify_agent_dead(
            agent["id"], agent["name"], "parada_emergencia"
        )
        terminated_count += 1

    await notification_service.create_notification(
        type="system_info",
        title="¡PARADA DE EMERGENCIA EJECUTADA!",
        message=f"{terminated_count} agentes terminados. Balance afectado: €{total_balance_lost:.2f}",
        icon="alert-triangle",
        color="red",
        priority="critical",
    )

    return {"success": True, "terminated_count": terminated_count}
