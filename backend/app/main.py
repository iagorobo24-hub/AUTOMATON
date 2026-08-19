import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.accounting.bootstrap import ensure_accounting_baseline
from app.accounting.router import router as accounting_router
from app.agent_evolution.policy import bootstrap_evolution_policy, bootstrap_lifecycle_baselines
from app.agent_evolution.router import router as evolution_router
from app.backtesting.router import router as backtesting_router
from app.backtesting.runner import recover_interrupted_runs
from app.database import SessionLocal, init_db
from app.market_data.router import router as market_data_router
from app.paper_execution.router import router as paper_execution_router
from app.paper_execution.service import PaperExecutionService
from app.paper_runtime.router import router as paper_runtime_router
from app.paper_runtime.scheduler import runtime_scheduler
from app.paper_runtime.service import recover_interrupted_runtime_sessions
from app.risk.bootstrap import ensure_active_risk_profile
from app.risk.router import router as risk_router
from app.routers import agents, trades, crypto

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

RUNTIME_MODE = "transition"
MARKET_DATA_MODE = "real_contract_available"
ACCOUNTING_MODE = "authoritative_phase_2"
PAPER_TRADING_MODE = "autonomous_phase_7"
RISK_MODE = "authoritative_phase_4"
BACKTESTING_MODE = "evidence_phase_5"
AGENT_EVOLUTION_MODE = "evidence_phase_6"
PAPER_RUNTIME_MODE = "runtime_phase_7"
AUTOMATED_TRADING_MODE = "paper_enabled_phase_7"
LIVE_EXECUTION_MODE = "disabled"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[MAIN] Starting up...")
    init_db()
    logger.info("[MAIN] Database initialized")
    with SessionLocal() as session:
        bootstrapped_accounts = ensure_accounting_baseline(session)
        evolution_policy = bootstrap_evolution_policy(session)
        lifecycle_baselines = bootstrap_lifecycle_baselines(session)
        risk_profile = ensure_active_risk_profile(session)
        interrupted_backtests = recover_interrupted_runs(session)
        paper_service = PaperExecutionService(session)
        recovered_paper = paper_service.recover_pending()
        recovered_requests = paper_service.recover_requests()
        interrupted_runtime = recover_interrupted_runtime_sessions(session)
    logger.info("[MAIN] Accounting baseline ready (%s accounts bootstrapped)", bootstrapped_accounts)
    logger.info("[MAIN] Evolution policy ready (%s)", evolution_policy.version)
    logger.info("[MAIN] Agent lifecycle baseline ready (%s agents classified)", lifecycle_baselines)
    logger.info("[MAIN] Risk profile ready (%s, paused=%s)", risk_profile.version, risk_profile.paused)
    logger.info("[MAIN] Backtest recovery invalidated %s interrupted runs", interrupted_backtests)
    logger.info(
        "[MAIN] Paper recovery complete (filled=%s cancelled=%s)",
        recovered_paper["filled"],
        recovered_paper["cancelled"],
    )
    logger.info(
        "[MAIN] Paper request recovery complete (completed=%s recovery_required=%s)",
        recovered_requests["completed"],
        recovered_requests["recovery_required"],
    )
    logger.info("[MAIN] Runtime recovery blocked %s interrupted sessions pending explicit operator recovery", interrupted_runtime)
    app.state.runtime_mode = RUNTIME_MODE
    app.state.market_data_mode = MARKET_DATA_MODE
    app.state.accounting_mode = ACCOUNTING_MODE
    app.state.paper_trading_mode = PAPER_TRADING_MODE
    app.state.risk_mode = RISK_MODE
    app.state.backtesting_mode = BACKTESTING_MODE
    app.state.agent_evolution_mode = AGENT_EVOLUTION_MODE
    app.state.paper_runtime_mode = PAPER_RUNTIME_MODE
    logger.info("[MAIN] Synthetic AgentEngine is disabled in the normal runtime")
    logger.info("[MAIN] Real read-only market-data contract is available")
    logger.info("[MAIN] Authoritative portfolio accounting is available")
    logger.info("[MAIN] Phase 4 Risk remains mandatory for every active Paper order")
    logger.info("[MAIN] Phase 5 deterministic historical evidence boundary is available")
    logger.info("[MAIN] Phase 6 evidence-gated manual replication is available")
    logger.info("[MAIN] Phase 7 autonomous Paper sessions are available but never auto-resume after restart")
    yield
    runtime_scheduler.cancel_all()
    logger.info("[MAIN] Shutdown complete")


app = FastAPI(
    title="AUTOMATON v2",
    version="2.10.0",
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
app.include_router(market_data_router, prefix="/api/market-data", tags=["market-data"])
app.include_router(accounting_router, prefix="/api/accounting", tags=["accounting"])
app.include_router(risk_router, prefix="/api/risk", tags=["risk"])
app.include_router(paper_execution_router, prefix="/api/paper", tags=["paper"])
app.include_router(backtesting_router, prefix="/api/backtests", tags=["backtests"])
app.include_router(evolution_router, prefix="/api/evolution", tags=["evolution"])
app.include_router(paper_runtime_router, prefix="/api/runtime", tags=["runtime"])


@app.get("/")
def root():
    return {
        "message": "AUTOMATON v2 API",
        "version": "2.10.0",
        "status": "operational",
        "runtime_mode": RUNTIME_MODE,
        "market_data": MARKET_DATA_MODE,
        "accounting": ACCOUNTING_MODE,
        "risk": RISK_MODE,
        "paper_trading": PAPER_TRADING_MODE,
        "backtesting": BACKTESTING_MODE,
        "agent_evolution": AGENT_EVOLUTION_MODE,
        "paper_runtime": PAPER_RUNTIME_MODE,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "runtime_mode": RUNTIME_MODE,
        "synthetic_engine": "disabled",
        "market_data": MARKET_DATA_MODE,
        "accounting": ACCOUNTING_MODE,
        "risk": RISK_MODE,
        "paper_trading": PAPER_TRADING_MODE,
        "backtesting": BACKTESTING_MODE,
        "agent_evolution": AGENT_EVOLUTION_MODE,
        "paper_runtime": PAPER_RUNTIME_MODE,
        "automated_trading": AUTOMATED_TRADING_MODE,
        "live_execution": LIVE_EXECUTION_MODE,
    }


@app.get("/api/estado")
def get_estado():
    return {
        "runtime_mode": RUNTIME_MODE,
        "synthetic_engine": "disabled",
        "market_data_mode": MARKET_DATA_MODE,
        "accounting_mode": ACCOUNTING_MODE,
        "risk_mode": RISK_MODE,
        "paper_trading": PAPER_TRADING_MODE,
        "backtesting": BACKTESTING_MODE,
        "agent_evolution": AGENT_EVOLUTION_MODE,
        "paper_runtime": PAPER_RUNTIME_MODE,
        "automated_trading": AUTOMATED_TRADING_MODE,
        "live_execution": LIVE_EXECUTION_MODE,
        "financial_evidence": "paper_backtest_evolution_and_runtime_records_separated_by_explicit_provenance",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
