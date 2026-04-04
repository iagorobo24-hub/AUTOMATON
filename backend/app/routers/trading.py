from fastapi import APIRouter, Depends
from fastapi import Request
from ..services.database import DatabaseService
from ..api.deps import get_db_service

router = APIRouter()


@router.get("/engine/status")
async def get_trading_engine_status(request: Request):
    """Get trading engine status"""
    engine = getattr(request.app.state, "trading_engine", None)
    if engine is None:
        return {"status": "not_initialized", "message": "Trading engine not started"}
    return engine.get_status()


@router.post("/engine/start")
async def start_trading_engine(
    request: Request, db_service: DatabaseService = Depends(get_db_service)
):
    """Start the trading engine"""
    engine = getattr(request.app.state, "trading_engine", None)
    if engine is None:
        from ..services.trading_engine import TradingEngine
        from ..services.notifications import NotificationService
        from ..api.deps import db

        notification_service = NotificationService(db)
        engine = TradingEngine(db_service, notification_service)
        await engine.start()
        request.app.state.trading_engine = engine
        return {"status": "started", "mode": "paper_trading"}
    return {"status": "already_running"}


@router.post("/engine/stop")
async def stop_trading_engine(request: Request):
    """Stop the trading engine"""
    engine = getattr(request.app.state, "trading_engine", None)
    if engine:
        await engine.stop()
        return {"status": "stopped"}
    return {"status": "not_running"}


@router.get("/regime")
async def get_market_regime(request: Request):
    """Get current market regime"""
    engine = getattr(request.app.state, "trading_engine", None)
    if engine:
        return engine.regime_detector.get_status()
    return {"status": "engine_not_running"}


@router.get("/risk")
async def get_risk_status(
    request: Request, db_service: DatabaseService = Depends(get_db_service)
):
    """Get risk manager status"""
    engine = getattr(request.app.state, "trading_engine", None)
    if engine:
        agents = await db_service.get_agents()
        total_capital = sum(
            a.get("finances", {}).get("current_balance", 0) for a in agents
        )
        return engine.risk_manager.get_status(total_capital)
    return {"status": "engine_not_running"}


@router.get("/positions")
async def get_active_positions(request: Request):
    """Get all active positions"""
    engine = getattr(request.app.state, "trading_engine", None)
    if engine:
        return {
            "count": len(engine.active_positions),
            "positions": list(engine.active_positions.values()),
        }
    return {"count": 0, "positions": []}
