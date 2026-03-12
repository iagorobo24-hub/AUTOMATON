from fastapi import FastAPI, APIRouter, HTTPException, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Automaton Orchestrator API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ==================== MODELS ====================

class AgentCreate(BaseModel):
    name: str
    type: str  # crypto_analyzer, business_scout, trader
    initial_balance: float = 100.0
    config: Optional[Dict[str, Any]] = {}

class Agent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str
    balance: float
    initial_balance: float
    roi: float = 0.0
    status: str = "active"  # active, replicating, dying, dead
    trades_count: int = 0
    successful_trades: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    parent_id: Optional[str] = None
    children_ids: List[str] = []
    config: Dict[str, Any] = {}

class Opportunity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str  # crypto, business, trading
    potential_roi: float
    risk_level: str  # low, medium, high
    detected_by: str  # agent_id
    status: str = "pending"  # pending, approved, rejected, executing
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    analysis: Dict[str, Any] = {}

class ChatMessage(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class Transaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # deposit, withdrawal, agent_allocation, stripe, crypto
    amount: float
    currency: str = "USD"
    status: str = "pending"
    agent_id: Optional[str] = None
    stripe_session_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LLMUsage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider: str  # openai, anthropic, gemini
    model: str
    tokens_used: int
    cost_estimate: float
    task_type: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== CRYPTO API (CoinGecko) ====================

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
crypto_cache = {}
cache_ttl = 60  # seconds

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
async def get_agents():
    agents = await db.agents.find({}, {"_id": 0}).to_list(100)
    for agent in agents:
        if isinstance(agent.get('created_at'), str):
            agent['created_at'] = datetime.fromisoformat(agent['created_at'])
    return {"agents": agents}

@api_router.post("/agents")
async def create_agent(agent_data: AgentCreate):
    agent = Agent(
        name=agent_data.name,
        type=agent_data.type,
        balance=agent_data.initial_balance,
        initial_balance=agent_data.initial_balance,
        config=agent_data.config or {}
    )
    doc = agent.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.agents.insert_one(doc)
    return agent.model_dump()

@api_router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@api_router.post("/agents/{agent_id}/replicate")
async def replicate_agent(agent_id: str):
    parent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not parent:
        raise HTTPException(status_code=404, detail="Parent agent not found")
    
    if parent["balance"] < 50:
        raise HTTPException(status_code=400, detail="Insufficient balance for replication")
    
    # Create child agent with half the parent's balance
    split_balance = parent["balance"] / 2
    
    child = Agent(
        name=f"{parent['name']}_child_{len(parent.get('children_ids', [])) + 1}",
        type=parent["type"],
        balance=split_balance,
        initial_balance=split_balance,
        parent_id=agent_id,
        config=parent.get("config", {})
    )
    
    child_doc = child.model_dump()
    child_doc['created_at'] = child_doc['created_at'].isoformat()
    await db.agents.insert_one(child_doc)
    
    # Update parent
    await db.agents.update_one(
        {"id": agent_id},
        {
            "$set": {"balance": split_balance, "status": "active"},
            "$push": {"children_ids": child.id}
        }
    )
    
    return {"parent_id": agent_id, "child": child.model_dump(), "message": "Agent replicated successfully"}

@api_router.delete("/agents/{agent_id}")
async def destroy_agent(agent_id: str):
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Mark as dead instead of deleting
    await db.agents.update_one(
        {"id": agent_id},
        {"$set": {"status": "dead", "balance": 0}}
    )
    
    return {"message": f"Agent {agent_id} destroyed", "final_balance": agent["balance"]}

@api_router.post("/agents/{agent_id}/simulate-trade")
async def simulate_trade(agent_id: str, profit: float = 0):
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    new_balance = agent["balance"] + profit
    new_trades = agent.get("trades_count", 0) + 1
    new_successful = agent.get("successful_trades", 0) + (1 if profit > 0 else 0)
    roi = ((new_balance - agent["initial_balance"]) / agent["initial_balance"]) * 100
    
    status = "active"
    if new_balance <= 0:
        status = "dead"
        new_balance = 0
    elif roi > 50:
        status = "replicating"
    elif new_balance < agent["initial_balance"] * 0.2:
        status = "dying"
    
    await db.agents.update_one(
        {"id": agent_id},
        {"$set": {
            "balance": new_balance,
            "trades_count": new_trades,
            "successful_trades": new_successful,
            "roi": roi,
            "status": status
        }}
    )
    
    return {
        "agent_id": agent_id,
        "new_balance": new_balance,
        "roi": roi,
        "status": status,
        "trades_count": new_trades
    }

# ==================== OPPORTUNITIES API ====================

@api_router.get("/opportunities")
async def get_opportunities():
    opportunities = await db.opportunities.find({}, {"_id": 0}).to_list(100)
    return {"opportunities": opportunities}

@api_router.post("/opportunities")
async def create_opportunity(
    title: str,
    description: str,
    category: str,
    potential_roi: float,
    risk_level: str,
    detected_by: str
):
    opp = Opportunity(
        title=title,
        description=description,
        category=category,
        potential_roi=potential_roi,
        risk_level=risk_level,
        detected_by=detected_by
    )
    doc = opp.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.opportunities.insert_one(doc)
    return opp.model_dump()

# ==================== ORCHESTRATOR CHAT API ====================

@api_router.post("/chat")
async def chat_with_orchestrator(req: ChatRequest):
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    session_id = req.session_id or str(uuid.uuid4())
    
    # Get context: agents, crypto data, opportunities
    agents = await db.agents.find({}, {"_id": 0}).to_list(10)
    opportunities = await db.opportunities.find({}, {"_id": 0}).to_list(5)
    
    system_message = f"""Eres el Orquestador Principal de Automaton, un sistema de agentes autoreplicantes con capacidades monetarias reales.

Tu rol:
1. Gestionar el ecosistema de agentes (crear, replicar, destruir según rendimiento)
2. Analizar mercados crypto y detectar oportunidades
3. Investigar nuevos modelos de negocio
4. Optimizar el uso de recursos y tokens de LLM
5. Proporcionar análisis estratégicos

Estado actual del sistema:
- Agentes activos: {len([a for a in agents if a.get('status') == 'active'])}
- Agentes totales: {len(agents)}
- Oportunidades pendientes: {len([o for o in opportunities if o.get('status') == 'pending'])}

Responde de forma concisa, técnica y orientada a la acción. Usa datos cuando estén disponibles."""

    chat = LlmChat(
        api_key=api_key,
        session_id=session_id,
        system_message=system_message
    ).with_model("openai", "gpt-4o")
    
    user_message = UserMessage(text=req.message)
    response = await chat.send_message(user_message)
    
    # Save to chat history
    chat_doc = {
        "session_id": session_id,
        "messages": [
            {"role": "user", "content": req.message, "timestamp": datetime.now(timezone.utc).isoformat()},
            {"role": "assistant", "content": response, "timestamp": datetime.now(timezone.utc).isoformat()}
        ]
    }
    await db.chat_history.insert_one(chat_doc)
    
    # Track LLM usage
    usage_doc = {
        "id": str(uuid.uuid4()),
        "provider": "openai",
        "model": "gpt-4o",
        "tokens_used": len(req.message.split()) + len(response.split()),  # Estimate
        "cost_estimate": 0.001,
        "task_type": "orchestrator_chat",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.llm_usage.insert_one(usage_doc)
    
    return {"response": response, "session_id": session_id}

# ==================== PAYMENTS API (Stripe) ====================

@api_router.post("/payments/create-session")
async def create_payment_session(request: Request, amount: float, package_type: str = "custom"):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
    
    api_key = os.environ.get('STRIPE_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    # Get origin from request
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
    
    # Create transaction record
    tx_doc = {
        "id": str(uuid.uuid4()),
        "type": "stripe",
        "amount": amount,
        "currency": "USD",
        "status": "pending",
        "stripe_session_id": session.session_id,
        "metadata": {"package_type": package_type},
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.payment_transactions.insert_one(tx_doc)
    
    return {"checkout_url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    api_key = os.environ.get('STRIPE_API_KEY')
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url="")
    
    status = await stripe_checkout.get_checkout_status(session_id)
    
    # Update transaction in DB
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
    
    # Aggregate by provider
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
    agents = await db.agents.find({}, {"_id": 0}).to_list(100)
    transactions = await db.payment_transactions.find({}, {"_id": 0}).to_list(100)
    opportunities = await db.opportunities.find({}, {"_id": 0}).to_list(100)
    
    active_agents = [a for a in agents if a.get("status") == "active"]
    total_balance = sum(a.get("balance", 0) for a in agents)
    avg_roi = sum(a.get("roi", 0) for a in agents) / len(agents) if agents else 0
    
    completed_txs = [t for t in transactions if t.get("status") == "completed"]
    total_funded = sum(t.get("amount", 0) for t in completed_txs)
    
    return {
        "agents": {
            "total": len(agents),
            "active": len(active_agents),
            "dying": len([a for a in agents if a.get("status") == "dying"]),
            "dead": len([a for a in agents if a.get("status") == "dead"]),
            "replicating": len([a for a in agents if a.get("status") == "replicating"])
        },
        "finances": {
            "total_balance": total_balance,
            "total_funded": total_funded,
            "avg_roi": avg_roi
        },
        "opportunities": {
            "total": len(opportunities),
            "pending": len([o for o in opportunities if o.get("status") == "pending"]),
            "approved": len([o for o in opportunities if o.get("status") == "approved"])
        }
    }

# ==================== ROOT & HEALTH ====================

@api_router.get("/")
async def root():
    return {"message": "Automaton Orchestrator API", "status": "operational"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
