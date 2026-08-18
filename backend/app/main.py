import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.models import Agent, Trade, AgentStatus, StrategyEnum, TradeType
from app.services.agent_engine import AgentEngine
from app.routers import agents, trades, crypto

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global agent engine instance
agent_engine: AgentEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global agent_engine

    # Startup
    logger.info("[MAIN] Starting up...")

    # Initialize database
    init_db()
    logger.info("[MAIN] Database initialized")

    # Start agent engine
    agent_engine = AgentEngine()
    await agent_engine.start()
    app.state.agent_engine = agent_engine
    logger.info("[MAIN] AgentEngine started")

    yield

    # Shutdown
    logger.info("[MAIN] Shutting down...")
    if agent_engine:
        await agent_engine.stop()
    logger.info("[MAIN] Shutdown complete")


app = FastAPI(
    title="AUTOMATON v2",
    version="2.2.0",
    description="Agentes de trading crypto autónomos",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers backed by the active SQLModel stack.
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(crypto.router, prefix="/api/crypto", tags=["crypto"])


@app.get("/")
def root():
    return {
        "message": "AUTOMATON v2 API",
        "version": "2.2.0",
        "status": "operational",
    }


@app.get("/health")
def health():
    """Health check endpoint for wait-on"""
    engine_status = "running" if agent_engine and agent_engine.running else "stopped"
    return {
        "status": "ok",
        "agent_engine": engine_status,
    }


@app.post("/api/agents/crear")
def crear_agente_api(
    nombre: str,
    estrategia: StrategyEnum,
    presupuesto: float,
    umbral: float = 0.15,
):
    """Convenience endpoint to create agent via engine"""
    if not agent_engine:
        return {"error": "AgentEngine not running"}, 503

    agente = agent_engine.crear_agente(nombre, estrategia, presupuesto, umbral)
    return {
        "id": agente.id,
        "nombre": agente.nombre,
        "estrategia": agente.estrategia.value,
    }


@app.get("/api/estado")
def get_estado():
    """Get global system state"""
    if not agent_engine:
        return {"error": "AgentEngine not running"}, 503

    return agent_engine.get_estado()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
