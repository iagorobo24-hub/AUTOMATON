from fastapi import APIRouter
from ..routers import (
    agents,
    crypto,
    dashboard,
    chat,
    notifications,
    trades,
    strategies,
    risk,
    audit,
    payments,
    signals,
    trading,
    system,
    simulation,
)

api_router = APIRouter()

api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(crypto.router, prefix="/crypto", tags=["crypto"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["notifications"]
)
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(signals.router, prefix="/signals", tags=["signals"])
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["simulation"])
