from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.market_data.quality import MarketDataQualityError, MarketDataUnavailable
from app.market_data.router import get_market_data_service
from app.market_data.service import MarketDataService
from app.models.paper_execution import PaperExecution
from app.paper_execution.service import (
    PaperExecutionError,
    PaperExecutionPolicy,
    PaperExecutionService,
)


router = APIRouter()
POLICY = PaperExecutionPolicy()


def _serialize_execution(execution: PaperExecution) -> dict:
    return {
        "id": execution.id,
        "account_id": execution.account_id,
        "agent_id": execution.agent_id,
        "order_id": execution.order_id,
        "fill_id": execution.fill_id,
        "symbol": execution.symbol,
        "side": execution.side,
        "requested_quantity": str(execution.requested_quantity),
        "origin": execution.origin,
        "policy_version": execution.policy_version,
        "provider": execution.provider,
        "provider_symbol": execution.provider_symbol,
        "quote_observed_at": execution.quote_observed_at.isoformat(),
        "quote_received_at": execution.quote_received_at.isoformat(),
        "market_price": str(execution.market_price),
        "fill_price": str(execution.fill_price),
        "slippage_bps": str(execution.slippage_bps),
        "fee_bps": str(execution.fee_bps),
        "fee": str(execution.fee),
        "status": execution.status,
        "rejection_reason": execution.rejection_reason,
        "evidence_mode": execution.evidence_mode,
        "created_at": execution.created_at.isoformat(),
        "updated_at": execution.updated_at.isoformat(),
    }


@router.get("/status")
def paper_status() -> dict:
    return {
        "mode": "paper",
        "market_data": "real_only",
        "capital": "virtual_only",
        "order_type": "market_only",
        "origin": "operator_only_until_risk",
        "live_execution_capability": False,
        "synthetic_fallback": False,
        "policy_version": POLICY.version,
        "slippage_bps": str(POLICY.slippage_bps),
        "fee_bps": str(POLICY.fee_bps),
    }


@router.post("/orders/market")
async def execute_market_order(
    account_id: int,
    symbol: str = Query(min_length=3),
    side: str = Query(min_length=3, max_length=4),
    quantity: Decimal = Query(gt=0),
    session: Session = Depends(get_session),
    market_data: MarketDataService = Depends(get_market_data_service),
) -> dict:
    try:
        quote = await market_data.get_quote(symbol)
    except MarketDataUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail="Real market-data provider unavailable; Paper order was not created",
        ) from exc
    except MarketDataQualityError as exc:
        raise HTTPException(
            status_code=502,
            detail="Real market-data quality validation failed; Paper order was not created",
        ) from exc

    service = PaperExecutionService(session, policy=POLICY)
    try:
        result = service.execute_market_order(
            account_id=account_id,
            symbol=quote.symbol,
            side=side,
            quantity=quantity,
            quote=quote,
            origin="operator",
        )
    except PaperExecutionError as exc:
        status_code = 404 if str(exc) == "account not found" else 409
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    execution = session.get(PaperExecution, result.execution_id)
    payload = _serialize_execution(execution)
    payload.update(
        {
            "quantity": str(result.quantity),
            "observed_at": result.observed_at.isoformat(),
        }
    )
    return payload


@router.get("/executions")
def list_executions(
    account_id: int | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[dict]:
    statement = select(PaperExecution)
    if account_id is not None:
        statement = statement.where(PaperExecution.account_id == account_id)
    statement = statement.order_by(PaperExecution.id.desc()).limit(limit)
    return [_serialize_execution(item) for item in session.exec(statement).all()]
