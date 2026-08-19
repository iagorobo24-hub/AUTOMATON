import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import agents, trades, crypto

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

RUNTIME_MODE = "transition"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[MAIN] Starting up...")
    init_db()
    logger.info("[MAIN] Database initialized")
    app.state.runtime_mode = RUNTIME_MODE
    logger.info("[MAIN] Synthetic AgentEngine is disabled in the normal runtime")
    yield
    logger.info("[MAIN] Shutdown complete")


app = FastAPI(
    title="AUTOMATON v2",
    version="2.3.0",
    description="Autonomous crypto-trading research platform",
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
        "version": "2.3.0",
        "status": "operational",
        "runtime_mode": RUNTIME_MODE,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "runtime_mode": RUNTIME_MODE,
        "synthetic_engine": "disabled",
        "paper_trading": "not_implemented",
    }


@app.get("/api/estado")
def get_estado():
    return {
        "runtime_mode": RUNTIME_MODE,
        "synthetic_engine": "disabled",
        "paper_trading": "not_implemented",
        "market_data_mode": "ui_only_real_data",
        "financial_evidence": "unavailable",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
