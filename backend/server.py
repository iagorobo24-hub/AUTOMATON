"""
Automaton Orchestrator - Main API Server
Self-replicating AI agent platform with real monetary actions
"""
from fastapi import FastAPI, APIRouter, HTTPException, Request, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx

# Load models and database service
from models import (
    Agent, AgentStatus, AgentType, AgentCreateRequest, AgentReplicateRequest,
    Strategy, Trade, TradeSide, TradeCreateRequest,
    RiskProfile, OrchestratorState
)
from database import DatabaseService
from notifications import NotificationService, NotificationType

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize services
db_service = DatabaseService(db)
notification_service = NotificationService(db)

# Create the main app
app = FastAPI(
    title="Automaton Orchestrator API",
    description="Self-replicating AI agent platform with crypto trading capabilities",
    version="2.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ==================== CRYPTO API (CoinGecko) ====================

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
crypto_cache = {}
cache_ttl = 60

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
            crypto_cache[cache_key] = (data, now)
            return data
        except Exception as e:
            logging.error(f"CoinGecko API error: {e}")
            raise HTTPException(status_code=503, detail="Crypto data service unavailable")

@api_router.get("/crypto/top-coins")
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

@api_router.get("/crypto/trending")
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

@api_router.get("/crypto/price/{coin_id}")
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

@api_router.get("/crypto/history/{coin_id}")
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

# ==================== AGENTS API ====================

@api_router.get("/agents")
async def get_agents(status: Optional[str] = None):
    """Get all agents with optional status filter"""
    status_enum = AgentStatus(status) if status else None
    agents = await db_service.get_agents(status=status_enum)
    return {"agents": agents}

@api_router.get("/agents/status-summary")
async def get_agents_status_summary():
    """Get summary of agent statuses"""
    agents = await db_service.get_agents()
    
    summary = {
        "total": len(agents),
        "active": len([a for a in agents if a.get('status') == 'active']),
        "paused": len([a for a in agents if a.get('status') == 'paused']),
        "replicating": len([a for a in agents if a.get('status') == 'replicating']),
        "dying": len([a for a in agents if a.get('status') == 'dying']),
        "dead": len([a for a in agents if a.get('status') == 'dead']),
        "hibernating": len([a for a in agents if a.get('status') == 'hibernating'])
    }
    
    return summary

@api_router.post("/agents")
async def create_agent(request: AgentCreateRequest):
    """Create a new agent with full schema"""
    agent = await db_service.create_agent(request)
    
    # Send notification
    await notification_service.notify_agent_created(
        agent.id, 
        agent.name, 
        request.initial_capital
    )
    
    return agent.model_dump()

@api_router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent by ID with full details"""
    agent = await db_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@api_router.post("/agents/{agent_id}/replicate")
async def replicate_agent(agent_id: str, request: AgentReplicateRequest = None):
    """Replicate an agent (create child with inherited traits)"""
    if request is None:
        request = AgentReplicateRequest()
    
    try:
        parent = await db_service.get_agent(agent_id)
        child = await db_service.replicate_agent(agent_id, request)
        if not child:
            raise HTTPException(status_code=404, detail="Parent agent not found")
        
        # Send notification
        await notification_service.notify_agent_replicated(
            parent['name'],
            child.name,
            child.id,
            child.finances.current_balance
        )
        
        return {
            "parent_id": agent_id,
            "child": child.model_dump(),
            "message": "Agent replicated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.delete("/agents/{agent_id}")
async def destroy_agent(agent_id: str):
    """Destroy/terminate an agent"""
    agent = await db_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    await db_service.update_agent_status(agent_id, AgentStatus.DEAD, reason="manual")
    
    return {
        "message": f"Agent {agent_id} destroyed",
        "final_balance": agent.get('finances', {}).get('current_balance', 0)
    }

@api_router.post("/agents/{agent_id}/simulate-trade")
async def simulate_trade(agent_id: str, profit: float = Query(default=0)):
    """Simulate a trade for an agent"""
    try:
        result = await db_service.simulate_trade(agent_id, profit)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@api_router.patch("/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: str, reason: str = None):
    """Update agent status"""
    try:
        status_enum = AgentStatus(status)
        await db_service.update_agent_status(agent_id, status_enum, reason)
        return {"message": f"Agent status updated to {status}"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")

@api_router.get("/agents/{agent_id}/trades")
async def get_agent_trades(agent_id: str, limit: int = 100):
    """Get trade history for an agent"""
    trades = await db_service.get_trades(agent_id, limit)
    return {"trades": trades}

@api_router.get("/agents/{agent_id}/wallet")
async def get_agent_wallet(agent_id: str):
    """Get wallet for an agent"""
    wallet = await db_service.get_wallet(agent_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

@api_router.get("/agents/{agent_id}/lineage")
async def get_agent_lineage(agent_id: str):
    """Get lineage tree for an agent family"""
    agent = await db_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    root_id = agent.get('lineage', {}).get('root_ancestor_id', agent_id)
    
    # Rebuild lineage tree
    await db_service.rebuild_lineage_tree(root_id)
    
    lineage = await db_service.get_agent_lineage(root_id)
    return lineage or {"message": "No lineage data available"}

# ==================== STRATEGIES API ====================

@api_router.get("/strategies")
async def get_strategies():
    """Get all trading strategies"""
    strategies = await db_service.get_strategies()
    return {"strategies": strategies}

@api_router.post("/strategies")
async def create_strategy(
    name: str,
    description: str = "",
    type: str = "momentum",
    timeframe: str = "4h"
):
    """Create a new trading strategy"""
    strategy = await db_service.create_strategy(
        name=name,
        description=description,
        type=type,
        timeframe=timeframe
    )
    return strategy.model_dump()

@api_router.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: str):
    """Get strategy by ID"""
    strategy = await db_service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

# ==================== RISK PROFILES API ====================

@api_router.get("/risk-profiles")
async def get_risk_profiles():
    """Get all risk profiles"""
    profiles = await db_service.get_risk_profiles()
    return {"profiles": profiles}

@api_router.post("/risk-profiles")
async def create_risk_profile(name: str, description: str = ""):
    """Create a new risk profile"""
    profile = await db_service.create_risk_profile(name=name, description=description)
    return profile.model_dump()

# ==================== TRADES API ====================

@api_router.get("/trades")
async def get_all_trades(limit: int = 100):
    """Get all trades across agents"""
    trades = await db_service.get_all_trades(limit)
    return {"trades": trades}

@api_router.post("/trades")
async def create_trade(request: TradeCreateRequest):
    """Create/open a new trade"""
    trade = await db_service.create_trade(request)
    return trade.model_dump()

# ==================== SIGNALS API ====================

@api_router.get("/signals")
async def get_signals(symbol: Optional[str] = None):
    """Get active trading signals"""
    signals = await db_service.get_active_signals(symbol)
    return {"signals": signals}

# ==================== AUDIT LOGS API ====================

@api_router.get("/audit-logs")
async def get_audit_logs(
    agent_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100
):
    """Get audit logs with optional filters"""
    logs = await db_service.get_audit_logs(agent_id, event_type, limit)
    return {"logs": logs}

# ==================== ORCHESTRATOR CHAT API ====================

@api_router.post("/chat")
async def chat_with_orchestrator(message: str, session_id: Optional[str] = None):
    """Chat with the orchestrator AI"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    session_id = session_id or str(uuid.uuid4())
    
    # Get context
    stats = await db_service.get_dashboard_stats()
    
    system_message = f"""Eres el Orquestador Principal de Automaton, un sistema de agentes autoreplicantes con capacidades de trading crypto.

Tu rol:
1. Gestionar el ecosistema de agentes (crear, replicar, destruir según rendimiento)
2. Analizar mercados crypto y detectar oportunidades
3. Investigar nuevos modelos de negocio para autoreplicación
4. Optimizar el uso de recursos y tokens de LLM
5. Proporcionar análisis estratégicos

Estado actual del sistema:
- Agentes activos: {stats['agents']['active']} de {stats['agents']['total']}
- Balance total: ${stats['finances']['total_balance']:.2f}
- ROI promedio: {stats['finances']['avg_roi']:.1f}%
- Trades totales: {stats['trading']['total_trades']}
- Tasa de éxito: {stats['trading']['win_rate']*100:.1f}%
- Generaciones: {stats['lineage']['total_generations']}
- Replicaciones: {stats['lineage']['total_replications']}

Base de datos estructurada para:
- Agentes con jerarquía y linaje completo
- Estrategias de trading heredables
- Perfiles de riesgo configurables
- Historial de trades con métricas detalladas
- Wallets individuales por agente
- Sistema de señales compartido
- Logs de auditoría inmutables

Responde de forma concisa, técnica y orientada a la acción. Usa datos cuando estén disponibles."""

    chat = LlmChat(
        api_key=api_key,
        session_id=session_id,
        system_message=system_message
    ).with_model("openai", "gpt-4o")
    
    user_message = UserMessage(text=message)
    response = await chat.send_message(user_message)
    
    # Save chat and track usage
    await db.chat_history.insert_one({
        "session_id": session_id,
        "message": message,
        "response": response,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    await db.llm_usage.insert_one({
        "id": str(uuid.uuid4()),
        "provider": "openai",
        "model": "gpt-4o",
        "tokens_used": len(message.split()) + len(response.split()),
        "cost_estimate": 0.001,
        "task_type": "orchestrator_chat",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"response": response, "session_id": session_id}

# ==================== PAYMENTS API (Stripe) ====================

@api_router.post("/payments/create-session")
async def create_payment_session(request: Request, amount: float, package_type: str = "custom"):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    api_key = os.environ.get('STRIPE_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    origin = request.headers.get("origin", str(request.base_url).rstrip("/"))
    
    success_url = f"{origin}/wallet?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin}/wallet"
    
    webhook_url = f"{str(request.base_url).rstrip('/')}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
    
    checkout_request = CheckoutSessionRequest(
        amount=float(amount),
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"package_type": package_type, "type": "agent_funding"},
        payment_methods=["card", "crypto"]
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    await db.payment_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "type": "stripe",
        "amount": amount,
        "currency": "USD",
        "status": "pending",
        "stripe_session_id": session.session_id,
        "metadata": {"package_type": package_type},
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    api_key = os.environ.get('STRIPE_API_KEY')
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url="")
    
    status = await stripe_checkout.get_checkout_status(session_id)
    
    await db.payment_transactions.update_one(
        {"stripe_session_id": session_id},
        {"$set": {"status": status.payment_status}}
    )
    
    return {
        "session_id": session_id,
        "status": status.status,
        "payment_status": status.payment_status,
        "amount": status.amount_total / 100,
        "currency": status.currency
    }

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    api_key = os.environ.get('STRIPE_API_KEY')
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url="")
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.payment_status == "paid":
            await db.payment_transactions.update_one(
                {"stripe_session_id": webhook_response.session_id},
                {"$set": {"status": "completed"}}
            )
        
        return {"received": True}
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return {"received": True}

@api_router.get("/payments/transactions")
async def get_transactions():
    transactions = await db.payment_transactions.find({}, {"_id": 0}).to_list(100)
    return {"transactions": transactions}

# ==================== LLM USAGE API ====================

@api_router.get("/llm/usage")
async def get_llm_usage():
    usage = await db.llm_usage.find({}, {"_id": 0}).to_list(100)
    
    by_provider = {}
    total_tokens = 0
    total_cost = 0
    
    for u in usage:
        provider = u.get("provider", "unknown")
        if provider not in by_provider:
            by_provider[provider] = {"tokens": 0, "cost": 0, "calls": 0}
        by_provider[provider]["tokens"] += u.get("tokens_used", 0)
        by_provider[provider]["cost"] += u.get("cost_estimate", 0)
        by_provider[provider]["calls"] += 1
        total_tokens += u.get("tokens_used", 0)
        total_cost += u.get("cost_estimate", 0)
    
    return {
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "by_provider": by_provider,
        "recent": usage[-10:] if usage else []
    }

# ==================== DASHBOARD STATS ====================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    stats = await db_service.get_dashboard_stats()
    
    # Update orchestrator metrics
    await db_service.update_orchestrator_metrics()
    
    # Get LLM usage stats
    llm_usage = await db.llm_usage.find({}, {"_id": 0}).to_list(1000)
    total_tokens = sum(u.get("tokens_used", 0) for u in llm_usage)
    
    # Calculate PnL periods
    trades = await db_service.get_all_trades(limit=1000)
    now = datetime.now(timezone.utc)
    
    pnl_24h = sum(
        t.get('result', {}).get('pnl_usd', 0) 
        for t in trades 
        if t.get('created_at') and (now - datetime.fromisoformat(t['created_at'].replace('Z', '+00:00'))).days < 1
    )
    
    pnl_7d = sum(
        t.get('result', {}).get('pnl_usd', 0) 
        for t in trades 
        if t.get('created_at') and (now - datetime.fromisoformat(t['created_at'].replace('Z', '+00:00'))).days < 7
    )
    
    # Add extended stats
    stats["trading"]["pnl_24h"] = pnl_24h
    stats["trading"]["pnl_7d"] = pnl_7d
    stats["llm"] = {
        "total_tokens": total_tokens,
        "total_calls": len(llm_usage),
        "cost_estimate": total_tokens * 0.00001  # Rough estimate
    }
    
    return stats

# ==================== BULK AGENT ACTIONS API ====================

@api_router.post("/agents/pause-all")
async def pause_all_agents():
    """Pausar todos los agentes activos"""
    agents = await db_service.get_agents(status=AgentStatus.ACTIVE)
    paused_count = 0
    
    for agent in agents:
        await db_service.update_agent_status(agent['id'], AgentStatus.PAUSED, reason="pausa_masiva")
        await notification_service.log_activity(
            type="agent_paused",
            title="Agente Pausado",
            description=f"{agent['name']} pausado por acción masiva",
            icon="pause",
            color="yellow",
            agent_id=agent['id'],
            agent_name=agent['name']
        )
        paused_count += 1
    
    if paused_count > 0:
        await notification_service.create_notification(
            type="system_info",
            title="Todos los Agentes Pausados",
            message=f"{paused_count} agentes han sido pausados",
            icon="pause",
            color="yellow",
            priority="high"
        )
    
    return {
        "success": True,
        "paused_count": paused_count,
        "message": f"{paused_count} agentes pausados"
    }

@api_router.post("/agents/resume-all")
async def resume_all_agents():
    """Resume all paused agents"""
    agents = await db_service.get_agents(status=AgentStatus.PAUSED)
    resumed_count = 0
    
    for agent in agents:
        await db_service.update_agent_status(agent['id'], AgentStatus.ACTIVE, reason="bulk_resume")
        resumed_count += 1
    
    if resumed_count > 0:
        await notification_service.create_notification(
            type="system_info",
            title="Agentes Reanudados",
            message=f"{resumed_count} agentes han sido reanudados",
            icon="play",
            color="green",
            priority="medium"
        )
    
    return {
        "success": True,
        "resumed_count": resumed_count,
        "message": f"{resumed_count} agentes reanudados"
    }

@api_router.post("/agents/emergency-stop")
async def emergency_stop_all_agents(confirm: bool = Query(default=False)):
    """Parada de emergencia - termina TODOS los agentes inmediatamente. Requiere confirmación."""
    if not confirm:
        return {
            "success": False,
            "error": "confirmation_required",
            "message": "Esta acción TERMINARÁ TODOS LOS AGENTES. Añade ?confirm=true para proceder."
        }
    
    # Get all non-dead agents
    all_agents = await db_service.get_agents()
    active_agents = [a for a in all_agents if a.get('status') != 'dead']
    
    terminated_count = 0
    total_balance_lost = 0
    
    for agent in active_agents:
        balance = agent.get('finances', {}).get('current_balance', 0) or agent.get('balance', 0)
        total_balance_lost += balance
        
        await db_service.update_agent_status(agent['id'], AgentStatus.DEAD, reason="parada_emergencia")
        await notification_service.notify_agent_dead(agent['id'], agent['name'], "parada_emergencia")
        terminated_count += 1
    
    # Create critical notification
    await notification_service.create_notification(
        type="system_info",
        title="¡PARADA DE EMERGENCIA EJECUTADA!",
        message=f"{terminated_count} agentes terminados. Balance total afectado: ${total_balance_lost:.2f}",
        icon="alert-triangle",
        color="red",
        priority="critical"
    )
    
    return {
        "success": True,
        "terminated_count": terminated_count,
        "total_balance_affected": total_balance_lost,
        "message": f"Parada de emergencia ejecutada. {terminated_count} agentes terminados."
    }

# ==================== PORTFOLIO HISTORY API ====================

@api_router.get("/portfolio/history")
async def get_portfolio_history(period: str = "7d"):
    """Get portfolio value history based on trades"""
    from datetime import timedelta
    
    # Determine time range
    now = datetime.now(timezone.utc)
    periods = {
        "1d": timedelta(days=1),
        "7d": timedelta(days=7),
        "1m": timedelta(days=30),
        "3m": timedelta(days=90),
        "all": timedelta(days=365)
    }
    delta = periods.get(period, timedelta(days=7))
    start_date = now - delta
    
    # Get all trades
    trades = await db.trades.find(
        {"created_at": {"$gte": start_date.isoformat()}},
        {"_id": 0}
    ).sort("created_at", 1).to_list(10000)
    
    # Get all agents for initial capital
    agents = await db_service.get_agents()
    initial_capital = sum(a.get('finances', {}).get('initial_capital', 0) or a.get('initial_balance', 100) for a in agents)
    
    # Build cumulative PnL over time
    history = []
    cumulative_pnl = 0
    
    # Group trades by hour/day depending on period
    if period == "1d":
        # Group by hour
        interval_seconds = 3600
    elif period in ["7d", "1m"]:
        # Group by 4 hours
        interval_seconds = 14400
    else:
        # Group by day
        interval_seconds = 86400
    
    # Create time buckets
    current_time = start_date
    trade_index = 0
    
    while current_time <= now:
        # Sum all trades in this bucket
        bucket_end = current_time + timedelta(seconds=interval_seconds)
        
        while trade_index < len(trades):
            trade_time = datetime.fromisoformat(trades[trade_index]['created_at'].replace('Z', '+00:00'))
            if trade_time < bucket_end:
                pnl = trades[trade_index].get('result', {}).get('pnl_usd', 0)
                cumulative_pnl += pnl
                trade_index += 1
            else:
                break
        
        history.append({
            "timestamp": current_time.isoformat(),
            "time": current_time.strftime("%H:%M" if period == "1d" else "%m/%d"),
            "value": initial_capital + cumulative_pnl,
            "pnl": cumulative_pnl
        })
        
        current_time = bucket_end
    
    # If no trades, create flat line at initial capital
    if not history or len(history) < 2:
        points = 24 if period == "1d" else 7 if period == "7d" else 30
        history = []
        for i in range(points):
            t = start_date + timedelta(seconds=interval_seconds * i)
            history.append({
                "timestamp": t.isoformat(),
                "time": t.strftime("%H:%M" if period == "1d" else "%m/%d"),
                "value": initial_capital,
                "pnl": 0
            })
    
    return {
        "period": period,
        "initial_capital": initial_capital,
        "current_value": initial_capital + cumulative_pnl,
        "total_pnl": cumulative_pnl,
        "pnl_percent": (cumulative_pnl / initial_capital * 100) if initial_capital > 0 else 0,
        "history": history
    }

# ==================== NOTIFICATIONS API ====================

@api_router.get("/notifications")
async def get_notifications(unread_only: bool = False, limit: int = 50):
    """Get notifications"""
    notifications = await notification_service.get_notifications(unread_only, limit)
    unread_count = await notification_service.get_unread_count()
    return {
        "notifications": notifications,
        "unread_count": unread_count
    }

@api_router.get("/notifications/count")
async def get_notification_count():
    """Get unread notification count"""
    count = await notification_service.get_unread_count()
    return {"unread_count": count}

@api_router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark a notification as read"""
    success = await notification_service.mark_as_read(notification_id)
    return {"success": success}

@api_router.post("/notifications/read-all")
async def mark_all_notifications_read():
    """Mark all notifications as read"""
    count = await notification_service.mark_all_as_read()
    return {"marked_count": count}

@api_router.delete("/notifications/{notification_id}")
async def dismiss_notification(notification_id: str):
    """Dismiss/delete a notification"""
    success = await notification_service.dismiss_notification(notification_id)
    return {"success": success}

@api_router.delete("/notifications")
async def dismiss_all_notifications():
    """Dismiss all notifications"""
    count = await notification_service.dismiss_all()
    return {"dismissed_count": count}

# ==================== ACTIVITY FEED API ====================

@api_router.get("/activity")
async def get_activity_feed(
    agent_id: Optional[str] = None,
    type_filter: Optional[str] = None,
    limit: int = 100
):
    """Get activity feed"""
    events = await notification_service.get_activity_feed(agent_id, type_filter, limit)
    return {"events": events}

# ==================== ORCHESTRATOR STATE ====================

@api_router.get("/orchestrator/state")
async def get_orchestrator_state():
    """Get orchestrator state"""
    return await db_service.get_orchestrator_state()

# ==================== ROOT & HEALTH ====================

@api_router.get("/")
async def root():
    return {
        "message": "Automaton Orchestrator API",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Self-replicating agents",
            "Crypto trading",
            "Agent lineage tracking",
            "Strategy inheritance",
            "Risk profiles",
            "Audit logging"
        ]
    }

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include the router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
