import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.services.agent_engine import AgentEngine
from app.routers import agents, trades, crypto

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

agent_engine: AgentEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_engine
    logger.info("[MAIN] Starting up...")
    init_db()
    logger.info("[MAIN] Database initialized")
    agent_engine = AgentEngine()
    await agent_engine.start()
    app.state.agent_engine = agent_engine
    logger.info("[MAIN] AgentEngine started")
    yield
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    engine_status = "running" if agent_engine and agent_engine.running else "stopped"
    return {"status": "ok", "agent_engine": engine_status}


@app.get("/api/estado")
def get_estado():
    if not agent_engine:
        return {"error": "AgentEngine not running"}, 503
    return agent_engine.get_estado()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
