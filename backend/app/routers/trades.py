from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlmodel import Session, select

from app.models import Trade
from app.database import get_session

router = APIRouter()

LEGACY_EVIDENCE_MODE = "legacy_unclassified"


@router.get("/")
def get_trades(
    agente_id: Optional[int] = None,
    limit: int = Query(default=100, le=1000),
    session: Session = Depends(get_session),
) -> List[dict]:
    """Return preserved legacy trade records without presenting them as valid evidence."""
    query = select(Trade)
    if agente_id:
        query = query.where(Trade.agente_id == agente_id)
    trades = session.exec(query.limit(limit)).all()
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
            "evidence_mode": LEGACY_EVIDENCE_MODE,
            "evidence_valid": False,
        }
        for t in trades
    ]


@router.get("/stats")
def get_trades_stats(session: Session = Depends(get_session)) -> dict:
    """Do not derive financial metrics from pre-provenance trade records."""
    records = session.exec(select(Trade)).all()
    closed_records = [record for record in records if record.resultado is not None]
    return {
        "evidence_mode": LEGACY_EVIDENCE_MODE,
        "evidence_valid": False,
        "legacy_records": len(records),
        "legacy_closed_records": len(closed_records),
        "total_trades": None,
        "trades_cerrados": None,
        "profit_total": None,
        "win_rate": None,
        "win_rate_percent": None,
    }
