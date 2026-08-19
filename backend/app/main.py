import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.accounting.bootstrap import ensure_accounting_baseline
from app.accounting.router import router as accounting_router
from app.database import SessionLocal, init_db
from app.market_data.router import router as market_data_router
from app.routers import agents, trades, crypto

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

RUNTIME_MODE = "transition"
MARKET_DATA_MODE = "real_contract_available"
ACCOUNTING_MODE = "authoritative_phase_2"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[MAIN] Starting up...")
    init_db()
    logger.info("[MAIN] Database initialized")
    with SessionLocal() as session:
        bootstrapped_accounts = ensure_accounting_baseline(session)
    logger.info("[MAIN] Accounting baseline ready (%s accounts bootstrapped)", bootstrapped_accounts)
    app.state.runtime_mode = RUNTIME_MODE
    app.state.market_data_mode = MARKET_DATA_MODE
    app.state.accounting_mode = ACCOUNTING_MODE
    logger.info("[MAIN] Synthetic AgentEngine is disabled in the normal runtime")
    logger.info("[MAIN] Real read-only market-data contract is available")
    logger.info("[MAIN] Authoritative portfolio accounting is available")
    yield
    logger.info("[MAIN] Shutdown complete")


app = FastAPI(
    title="AUTOMATON v2",
    version="2.5.0",
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
app.include_router(
    market_data_router,
    prefix="/api/market-data",
    tags=["market-data"],
)
app.include_router(
    accounting_router,
    prefix="/api/accounting",
    tags=["accounting"],
)


@app.get("/")
def root():
    return {
        "message": "AUTOMATON v2 API",
        "version": "2.5.0",
        "status": "operational",
        "runtime_mode": RUNTIME_MODE,
        "market_data": MARKET_DATA_MODE,
        "accounting": ACCOUNTING_MODE,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "runtime_mode": RUNTIME_MODE,
        "synthetic_engine": "disabled",
        "market_data": MARKET_DATA_MODE,
        "accounting": ACCOUNTING_MODE,
        "paper_trading": "not_implemented",
    }


@app.get("/api/estado")
def get_estado():
    return {
        "runtime_mode": RUNTIME_MODE,
        "synthetic_engine": "disabled",
        "paper_trading": "not_implemented",
        "market_data_mode": MARKET_DATA_MODE,
        "accounting_mode": ACCOUNTING_MODE,
        "financial_evidence": "unavailable",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
