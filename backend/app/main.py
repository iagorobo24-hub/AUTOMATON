import logging
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

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

# Add rate limiting middleware
app.add_middleware(SlowAPIMiddleware)

# Attach limiter to app state for use in routers
app.state.limiter = limiter

# Add exception handler for rate limiting
@app.exception_handler(429)
async def rate_limit_exception_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    db_service = await get_db_service()
    notification_service = await get_notification_service()

    # Startup with error handling
    try:
        mock_engine = MockEngine(db_service)
        await mock_engine.start()
        app.state.mock_engine = mock_engine
        registry.set_mock_engine(mock_engine)
        logger.info("Mock Engine: OK")
    except Exception as e:
        logger.error(f"Mock Engine failed: {e}")
        raise

    try:
        replication_service = ReplicationService(db_service, notification_service)
        await replication_service.start()
        app.state.replication_service = replication_service
        registry.set_replication_service(replication_service)
        logger.info("Replication Service: OK")
    except Exception as e:
        logger.error(f"Replication Service failed: {e}")
        raise

    try:
        trading_engine = TradingEngine(db_service, notification_service)
        await trading_engine.start()
        app.state.trading_engine = trading_engine
        registry.set_trading_engine(trading_engine)
        logger.info("Trading Engine: OK")
    except Exception as e:
        logger.error(f"Trading Engine failed: {e}")
        raise

    try:
        snapshot_service = PortfolioSnapshotService(db_service)
        await snapshot_service.start()
        app.state.snapshot_service = snapshot_service
        registry.set_snapshot_service(snapshot_service)
        logger.info("Portfolio Snapshot Service: OK")
    except Exception as e:
        logger.error(f"Portfolio Snapshot Service failed: {e}")
        raise

    logger.info("All services started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down services...")

    if hasattr(app.state, "trading_engine") and app.state.trading_engine:
        await app.state.trading_engine.stop()

    if hasattr(app.state, "snapshot_service") and app.state.snapshot_service:
        await app.state.snapshot_service.stop()

    if hasattr(app.state, "replication_service") and app.state.replication_service:
        await app.state.replication_service.stop()

    if hasattr(app.state, "mock_engine") and app.state.mock_engine:
        await app.state.mock_engine.stop()

    client.close()
    logger.info("Shutdown complete")


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
