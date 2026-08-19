from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.risk import RiskDecision, RiskProfile
from app.risk.bootstrap import ensure_active_risk_profile


router = APIRouter()


def _profile_payload(profile: RiskProfile) -> dict:
    return {
        "id": profile.id,
        "name": profile.name,
        "version": profile.version,
        "active": profile.active,
        "paused": profile.paused,
        "max_order_notional": str(profile.max_order_notional),
        "max_order_equity_pct": str(profile.max_order_equity_pct),
        "max_total_exposure_pct": str(profile.max_total_exposure_pct),
        "max_symbol_exposure_pct": str(profile.max_symbol_exposure_pct),
        "max_open_positions": profile.max_open_positions,
        "max_realized_loss_pct": str(profile.max_realized_loss_pct),
        "max_drawdown_pct": str(profile.max_drawdown_pct),
        "max_quote_age_seconds": profile.max_quote_age_seconds,
    }


def _decision_payload(item: RiskDecision) -> dict:
    return {
        "id": item.id,
        "account_id": item.account_id,
        "agent_id": item.agent_id,
        "profile_version": item.profile_version,
        "symbol": item.symbol,
        "side": item.side,
        "quantity": str(item.quantity),
        "provider": item.provider,
        "quote_observed_at": item.quote_observed_at.isoformat(),
        "market_price": str(item.market_price),
        "requested_notional": str(item.requested_notional),
        "equity": str(item.equity),
        "total_exposure_before": str(item.total_exposure_before),
        "projected_total_exposure": str(item.projected_total_exposure),
        "symbol_exposure_before": str(item.symbol_exposure_before),
        "projected_symbol_exposure": str(item.projected_symbol_exposure),
        "open_positions_before": item.open_positions_before,
        "projected_open_positions": item.projected_open_positions,
        "realized_pnl": str(item.realized_pnl),
        "drawdown_pct": str(item.drawdown_pct),
        "decision": item.decision,
        "reason_code": item.reason_code,
        "reason": item.reason,
        "consumed_at": item.consumed_at.isoformat() if item.consumed_at else None,
        "paper_execution_id": item.paper_execution_id,
        "created_at": item.created_at.isoformat(),
    }


@router.get("/status")
def status(session: Session = Depends(get_session)) -> dict:
    profile = ensure_active_risk_profile(session)
    return {
        "mode": "authoritative_phase_4",
        "profile_version": profile.version,
        "paused": profile.paused,
        "paper_gate_required": True,
        "automated_trading": False,
        "live_execution": False,
        "fail_closed": True,
    }


@router.get("/profiles/active")
def active_profile(session: Session = Depends(get_session)) -> dict:
    return _profile_payload(ensure_active_risk_profile(session))


@router.get("/decisions")
def decisions(
    account_id: int | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[dict]:
    statement = select(RiskDecision)
    if account_id is not None:
        statement = statement.where(RiskDecision.account_id == account_id)
    statement = statement.order_by(RiskDecision.id.desc()).limit(limit)
    return [_decision_payload(item) for item in session.exec(statement).all()]


def _set_pause(session: Session, paused: bool) -> dict:
    profile = ensure_active_risk_profile(session)
    profile.paused = paused
    profile.updated_at = datetime.now(timezone.utc)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return {
        "profile_version": profile.version,
        "paused": profile.paused,
    }


@router.post("/pause")
def pause(session: Session = Depends(get_session)) -> dict:
    return _set_pause(session, True)


@router.post("/resume")
def resume(session: Session = Depends(get_session)) -> dict:
    return _set_pause(session, False)
