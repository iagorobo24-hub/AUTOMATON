import logging
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from .core.config import settings
from .api.api import api_router
from .api.deps import client, db, get_db_service, get_notification_service
from .services.mock_engine import MockEngine
from .services.replication import ReplicationService
from .services.trading_engine import TradingEngine
from .services.portfolio_snapshot import PortfolioSnapshotService
from app.services import registry

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Self-replicating AI agent platform with crypto trading capabilities",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    db_service = await get_db_service()
    notification_service = await get_notification_service()

    mock_engine = MockEngine(db_service)
    await mock_engine.start()
    app.state.mock_engine = mock_engine
    registry.set_mock_engine(mock_engine)

    replication_service = ReplicationService(db_service, notification_service)
    await replication_service.start()
    app.state.replication_service = replication_service
    registry.set_replication_service(replication_service)

    trading_engine = TradingEngine(db_service, notification_service)
    await trading_engine.start()
    app.state.trading_engine = trading_engine
    registry.set_trading_engine(trading_engine)

    snapshot_service = PortfolioSnapshotService(db_service)
    await snapshot_service.start()
    app.state.snapshot_service = snapshot_service
    registry.set_snapshot_service(snapshot_service)

    logger.info(
        "All services started: Mock Engine, Replication, Trading Engine, Portfolio Snapshots"
    )


@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, "mock_engine"):
        await app.state.mock_engine.stop()
    if hasattr(app.state, "replication_service"):
        await app.state.replication_service.stop()
    if hasattr(app.state, "trading_engine"):
        await app.state.trading_engine.stop()
    if hasattr(app.state, "snapshot_service"):
        await app.state.snapshot_service.stop()
    client.close()


@app.get("/")
async def root():
    return {
        "message": "Automaton Orchestrator API",
        "version": settings.VERSION,
        "status": "operational",
    }


@app.get("/health")
async def health():
    engine_status = "running" if hasattr(app.state, "trading_engine") else "stopped"
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": settings.PROJECT_NAME,
        "trading_engine": engine_status,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
