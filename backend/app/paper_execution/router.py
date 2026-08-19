import hashlib
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.database import get_session
from app.market_data.quality import (
    MarketDataQualityError,
    MarketDataUnavailable,
    normalize_symbol,
)
from app.market_data.router import get_market_data_service
from app.market_data.service import MarketDataService
from app.models.paper_execution import PaperExecution, PaperRequest
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


def _request_fingerprint(
    account_id: int,
    symbol: str,
    side: str,
    quantity: Decimal,
) -> str:
    normalized_quantity = format(Decimal(quantity).normalize(), "f")
    raw = f"{account_id}|{symbol}|{side}|{normalized_quantity}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _mark_request(
    session: Session,
    request: PaperRequest,
    *,
    status: str,
    http_status: int,
    error_detail: str | None,
    execution_id: int | None = None,
) -> None:
    request.status = status
    request.http_status = http_status
    request.error_detail = error_detail[:256] if error_detail else None
    if execution_id is not None:
        request.execution_id = execution_id
    request.updated_at = datetime.now(timezone.utc)
    session.add(request)
    session.commit()


def _handle_existing_request(
    session: Session,
    request: PaperRequest,
    fingerprint: str,
) -> dict | None:
    if request.request_fingerprint != fingerprint:
        raise HTTPException(
            status_code=409,
            detail="request_id is already bound to a different Paper order payload",
        )

    if request.status == "COMPLETED":
        if request.http_status == 200 and request.execution_id is not None:
            execution = session.get(PaperExecution, request.execution_id)
            if execution is None:
                raise HTTPException(
                    status_code=409,
                    detail="idempotent Paper request points to missing execution",
                )
            payload = _serialize_execution(execution)
            payload["request_id"] = request.request_id
            payload["idempotent_replay"] = True
            return payload
        raise HTTPException(
            status_code=request.http_status,
            detail=request.error_detail or "Paper request previously failed",
        )

    if request.status == "PROCESSING":
        raise HTTPException(
            status_code=409,
            detail="request_id is already processing",
        )

    if request.status == "RETRYABLE":
        _mark_request(
            session,
            request,
            status="PROCESSING",
            http_status=200,
            error_detail=None,
        )
        return None

    raise HTTPException(
        status_code=request.http_status or 409,
        detail=request.error_detail or "Paper request is not executable",
    )


def _reserve_request(
    session: Session,
    *,
    request_id: str,
    fingerprint: str,
    account_id: int,
) -> tuple[PaperRequest | None, dict | None]:
    existing = session.exec(
        select(PaperRequest).where(PaperRequest.request_id == request_id)
    ).first()
    if existing is not None:
        replay = _handle_existing_request(session, existing, fingerprint)
        return existing if replay is None else None, replay

    request = PaperRequest(
        request_id=request_id,
        request_fingerprint=fingerprint,
        account_id=account_id,
        status="PROCESSING",
    )
    session.add(request)
    try:
        session.commit()
        session.refresh(request)
        return request, None
    except IntegrityError:
        session.rollback()
        existing = session.exec(
            select(PaperRequest).where(PaperRequest.request_id == request_id)
        ).first()
        if existing is None:
            raise HTTPException(
                status_code=409,
                detail="Paper request reservation conflict",
            )
        replay = _handle_existing_request(session, existing, fingerprint)
        return existing if replay is None else None, replay


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
        "idempotency": "request_id_required",
    }


@router.post("/orders/market")
async def execute_market_order(
    request_id: str = Query(min_length=1, max_length=128),
    account_id: int = Query(gt=0),
    symbol: str = Query(min_length=3),
    side: str = Query(min_length=3, max_length=4),
    quantity: Decimal = Query(gt=0),
    session: Session = Depends(get_session),
    market_data: MarketDataService = Depends(get_market_data_service),
) -> dict:
    try:
        canonical_symbol = normalize_symbol(symbol)
    except MarketDataQualityError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    normalized_side = side.strip().upper()
    if normalized_side not in {"BUY", "SELL"}:
        raise HTTPException(status_code=422, detail="side must be BUY or SELL")

    fingerprint = _request_fingerprint(
        account_id, canonical_symbol, normalized_side, quantity
    )
    request, replay = _reserve_request(
        session,
        request_id=request_id.strip(),
        fingerprint=fingerprint,
        account_id=account_id,
    )
    if replay is not None:
        return replay
    assert request is not None

    try:
        quote = await market_data.get_quote(canonical_symbol)
    except MarketDataUnavailable as exc:
        detail = "Real market-data provider unavailable; Paper order was not created"
        _mark_request(
            session,
            request,
            status="RETRYABLE",
            http_status=503,
            error_detail=detail,
        )
        raise HTTPException(status_code=503, detail=detail) from exc
    except MarketDataQualityError as exc:
        detail = "Real market-data quality validation failed; Paper order was not created"
        _mark_request(
            session,
            request,
            status="RETRYABLE",
            http_status=502,
            error_detail=detail,
        )
        raise HTTPException(status_code=502, detail=detail) from exc

    service = PaperExecutionService(session, policy=POLICY)
    try:
        result = service.execute_market_order(
            account_id=account_id,
            symbol=quote.symbol,
            side=normalized_side,
            quantity=quantity,
            quote=quote,
            origin="operator",
            request=request,
        )
    except PaperExecutionError as exc:
        status_code = 404 if str(exc) == "account not found" else 409
        _mark_request(
            session,
            request,
            status="COMPLETED",
            http_status=status_code,
            error_detail=str(exc),
            execution_id=exc.execution_id,
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    _mark_request(
        session,
        request,
        status="COMPLETED",
        http_status=200,
        error_detail=None,
        execution_id=result.execution_id,
    )
    execution = session.get(PaperExecution, result.execution_id)
    payload = _serialize_execution(execution)
    payload.update(
        {
            "request_id": request.request_id,
            "quantity": str(result.quantity),
            "observed_at": result.observed_at.isoformat(),
            "idempotent_replay": False,
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
