from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.live_execution.adapter import DisabledLiveAdapter
from app.live_execution.policy import ensure_emergency_stop_baseline, get_active_live_policy
from app.live_execution.readiness import LiveReadinessEvaluator
from app.live_execution.service import LiveReadinessService
from app.models.live_execution import LiveReadinessEvaluation, LiveReconciliation

router = APIRouter()


def _adapter() -> DisabledLiveAdapter:
    return DisabledLiveAdapter()


@router.get("/status")
def status(session: Session = Depends(get_session)):
    policy = get_active_live_policy(session)
    stop = ensure_emergency_stop_baseline(session)
    latest = session.exec(select(LiveReadinessEvaluation).order_by(LiveReadinessEvaluation.id.desc())).first()
    return {
        "mode": "readiness_phase_10",
        "policy_version": policy.version,
        "architecture_ready": bool(latest.architecture_ready) if latest else False,
        "real_capital_execution": "disabled",
        "adapter": "disabled_read_only",
        "emergency_stop": stop.active,
        "order_submission_available": False,
        "credential_write_available": False,
    }


@router.get("/policy")
def policy(session: Session = Depends(get_session)):
    return get_active_live_policy(session)


@router.get("/readiness")
def readiness_history(session: Session = Depends(get_session), limit: int = Query(default=20, ge=1, le=100)):
    return list(session.exec(select(LiveReadinessEvaluation).order_by(LiveReadinessEvaluation.id.desc()).limit(limit)))


@router.post("/readiness/evaluate")
def evaluate(candidate_id: int, session: Session = Depends(get_session)):
    return LiveReadinessEvaluator(session, _adapter()).evaluate(candidate_id)


@router.post("/emergency-stop")
def activate_emergency_stop(reason: str, session: Session = Depends(get_session)):
    try:
        return LiveReadinessService(session, _adapter()).activate_emergency_stop(reason)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/emergency-stop/clear")
def clear_emergency_stop(reason: str, session: Session = Depends(get_session)):
    try:
        return LiveReadinessService(session, _adapter()).clear_emergency_stop(reason)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/reconciliations")
def reconciliations(session: Session = Depends(get_session), limit: int = Query(default=20, ge=1, le=100)):
    return list(session.exec(select(LiveReconciliation).order_by(LiveReconciliation.id.desc()).limit(limit)))


@router.post("/reconciliations/{reconciliation_id}/resolve")
def resolve_reconciliation(reconciliation_id: int, reason: str, session: Session = Depends(get_session)):
    try:
        return LiveReadinessService(session, _adapter()).resolve_reconciliation(reconciliation_id, reason)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
