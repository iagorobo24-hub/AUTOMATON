from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlmodel import Session, select, func

from app.models import Trade, Agent
from app.database import get_session

router = APIRouter()


@router.get("/")
def get_trades(
    agente_id: Optional[int] = None,
    limit: int = Query(default=100, le=1000),
    session: Session = Depends(get_session)
) -> List[dict]:
    """Get all trades with optional filter by agent_id"""
    query = select(Trade)
    if agente_id:
        query = query.where(Trade.agente_id == agente_id)
    query = query.limit(limit)
    
    trades = session.exec(query).all()
    return [
        {
            "id": t.id,
            "agente_id": t.agente_id,
            "precio_entrada": t.precio_entrada,
            "precio_salida": t.precio_salida,
            "cantidad": t.cantidad,
            "tipo": t.tipo.value,
            "resultado": t.resultado,
            "timestamp": t.timestamp.isoformat(),
        }
        for t in trades
    ]


@router.get("/stats")
def get_trades_stats(
    session: Session = Depends(get_session)
) -> dict:
    """Get trading statistics: total profit, win rate, number of trades"""
    trades = session.exec(select(Trade)).all()
    
    total_trades = len(trades)
    trades_cerrados = [t for t in trades if t.resultado is not None]
    
    # Profit total
    profit_total = sum(t.resultado for t in trades_cerrados if t.resultado)
    
    # Win rate (trades con resultado positivo / total cerrados)
    if trades_cerrados:
        winners = sum(1 for t in trades_cerrados if t.resultado and t.resultado > 0)
        win_rate = winners / len(trades_cerrados)
    else:
        win_rate = 0.0
    
    return {
        "total_trades": total_trades,
        "trades_cerrados": len(trades_cerrados),
        "profit_total": profit_total,
        "win_rate": win_rate,
        "win_rate_percent": round(win_rate * 100, 2),
    }
