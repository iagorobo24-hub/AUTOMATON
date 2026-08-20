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
from app.live_execution.adapter import DisabledLiveAdapter
from app.live_execution.policy import bootstrap_live_policy, ensure_emergency_stop_baseline
from app.live_execution.reconciliation import reconcile_live_state
from app.live_execution.router import router as live_router
from app.market_data.router import router as market_data_router
from app.paper_execution.router import router as paper_execution_router
from app.paper_execution.service import PaperExecutionService
from app.paper_runtime.execution import reconcile_runtime_cycles
from app.paper_runtime.router import router as paper_runtime_router
from app.paper_runtime.scheduler import runtime_scheduler
from app.paper_runtime.service import recover_interrupted_runtime_sessions
from app.risk.bootstrap import ensure_active_risk_profile
from app.risk.router import router as risk_router
from app.strategy_research.policy import bootstrap_research_policy
from app.strategy_research.router import router as research_router
from app.routers import agents, trades, crypto

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RUNTIME_MODE = "transition"
MARKET_DATA_MODE = "real_contract_available"
ACCOUNTING_MODE = "authoritative_phase_2"
PAPER_TRADING_MODE = "autonomous_phase_7"
RISK_MODE = "authoritative_phase_4"
BACKTESTING_MODE = "evidence_phase_5"
AGENT_EVOLUTION_MODE = "evidence_phase_6"
PAPER_RUNTIME_MODE = "runtime_phase_7"
STRATEGY_RESEARCH_MODE = "evidence_phase_8"
LEGACY_PRUNING_MODE = "pruned_phase_9"
LIVE_EXECUTION_MODE = "readiness_phase_10"
REAL_CAPITAL_EXECUTION_MODE = "disabled"
AUTOMATED_TRADING_MODE = "paper_enabled_phase_7"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[MAIN] Starting up...")
    init_db()
    with SessionLocal() as session:
        bootstrapped_accounts = ensure_accounting_baseline(session)
        evolution_policy = bootstrap_evolution_policy(session)
        lifecycle_baselines = bootstrap_lifecycle_baselines(session)
        risk_profile = ensure_active_risk_profile(session)
        research_policy = bootstrap_research_policy(session)
        live_policy = bootstrap_live_policy(session)
        emergency_stop = ensure_emergency_stop_baseline(session)
        interrupted_backtests = recover_interrupted_runs(session)
        paper_service = PaperExecutionService(session)
        recovered_paper = paper_service.recover_pending()
        recovered_requests = paper_service.recover_requests()
        reconciled_runtime_cycles = reconcile_runtime_cycles(session)
        interrupted_runtime = recover_interrupted_runtime_sessions(session)
        live_reconciliation = reconcile_live_state(session, DisabledLiveAdapter())
    logger.info("[MAIN] Accounting baseline ready (%s accounts bootstrapped)", bootstrapped_accounts)
    logger.info("[MAIN] Evolution policy ready (%s)", evolution_policy.version)
    logger.info("[MAIN] Agent lifecycle baseline ready (%s agents classified)", lifecycle_baselines)
    logger.info("[MAIN] Risk profile ready (%s, paused=%s)", risk_profile.version, risk_profile.paused)
    logger.info("[MAIN] Research policy ready (%s)", research_policy.version)
    logger.info("[MAIN] Live Readiness policy ready (%s); emergency_stop=%s", live_policy.version, emergency_stop.active)
    logger.info("[MAIN] Backtest recovery invalidated %s interrupted runs", interrupted_backtests)
    logger.info("[MAIN] Paper recovery complete (filled=%s cancelled=%s)", recovered_paper["filled"], recovered_paper["cancelled"])
    logger.info("[MAIN] Paper request recovery complete (completed=%s recovery_required=%s)", recovered_requests["completed"], recovered_requests["recovery_required"])
    logger.info("[MAIN] Runtime cycle recovery reconciled %s interrupted intents without replay", reconciled_runtime_cycles)
    logger.info("[MAIN] Runtime recovery blocked %s interrupted sessions pending explicit operator recovery", interrupted_runtime)
    logger.info("[MAIN] Live read-only reconciliation status=%s", live_reconciliation.status)
    app.state.runtime_mode = RUNTIME_MODE
    app.state.market_data_mode = MARKET_DATA_MODE
    app.state.accounting_mode = ACCOUNTING_MODE
    app.state.paper_trading_mode = PAPER_TRADING_MODE
    app.state.risk_mode = RISK_MODE
    app.state.backtesting_mode = BACKTESTING_MODE
    app.state.agent_evolution_mode = AGENT_EVOLUTION_MODE
    app.state.paper_runtime_mode = PAPER_RUNTIME_MODE
    app.state.strategy_research_mode = STRATEGY_RESEARCH_MODE
    app.state.legacy_pruning_mode = LEGACY_PRUNING_MODE
    app.state.live_execution_mode = LIVE_EXECUTION_MODE
    app.state.real_capital_execution_mode = REAL_CAPITAL_EXECUTION_MODE
    logger.info("[MAIN] Phase 10 Live Readiness boundary is available; real-capital execution remains disabled")
    yield
    runtime_scheduler.cancel_all()
    logger.info("[MAIN] Shutdown complete")


app = FastAPI(
    title="AUTOMATON v2",
    version="2.13.0",
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
app.include_router(research_router, prefix="/api/research", tags=["research"])
app.include_router(live_router, prefix="/api/live", tags=["live-readiness"])


def _runtime_payload():
    return {
        "runtime_mode": RUNTIME_MODE,
        "market_data": MARKET_DATA_MODE,
        "accounting": ACCOUNTING_MODE,
        "risk": RISK_MODE,
        "paper_trading": PAPER_TRADING_MODE,
        "backtesting": BACKTESTING_MODE,
        "agent_evolution": AGENT_EVOLUTION_MODE,
        "paper_runtime": PAPER_RUNTIME_MODE,
        "strategy_research": STRATEGY_RESEARCH_MODE,
        "legacy_pruning": LEGACY_PRUNING_MODE,
        "live_execution": LIVE_EXECUTION_MODE,
        "real_capital_execution": REAL_CAPITAL_EXECUTION_MODE,
    }


@app.get("/")
def root():
    return {"message": "AUTOMATON v2 API", "version": "2.13.0", "status": "operational", **_runtime_payload()}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "synthetic_engine": "disabled",
        "automated_trading": AUTOMATED_TRADING_MODE,
        **_runtime_payload(),
    }


@app.get("/api/estado")
def get_estado():
    payload = _runtime_payload()
    return {
        **{f"{key}_mode" if key in {"market_data", "accounting", "risk"} else key: value for key, value in payload.items()},
        "synthetic_engine": "disabled",
        "automated_trading": AUTOMATED_TRADING_MODE,
        "financial_evidence": "paper_backtest_evolution_runtime_research_and_live_readiness_records_separated_by_explicit_provenance",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
