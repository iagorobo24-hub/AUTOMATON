from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models import ResearchEvaluation, ResearchPolicy, ResearchStudy, ResearchWindow, StrategyCandidate
from app.strategy_research.evaluator import ResearchEvaluator
from app.strategy_research.policy import bootstrap_research_policy
from app.strategy_research.promotion import ResearchPromotionError, StrategyPromotionService
from app.strategy_research.service import StrategyResearchError, StrategyResearchService

router = APIRouter()


def _study_payload(study: ResearchStudy) -> dict:
    return {
        "id": study.id,
        "name": study.name,
        "strategy_id": study.strategy_id,
        "policy_version": study.policy_version,
        "status": study.status,
        "notes": study.notes,
        "strategy_version": study.strategy_version,
        "strategy_source_sha256": study.strategy_source_sha256,
        "execution_policy": study.execution_policy,
        "fee_bps": str(study.fee_bps) if study.fee_bps is not None else None,
        "slippage_bps": str(study.slippage_bps) if study.slippage_bps is not None else None,
        "position_fraction": str(study.position_fraction) if study.position_fraction is not None else None,
        "created_at": study.created_at.isoformat(),
        "updated_at": study.updated_at.isoformat(),
    }


def _window_payload(window: ResearchWindow) -> dict:
    return {"id": window.id, "study_id": window.study_id, "backtest_run_id": window.backtest_run_id,
        "role": window.role, "ordinal": window.ordinal, "created_at": window.created_at.isoformat()}


def _evaluation_payload(row: ResearchEvaluation) -> dict:
    return {
        "id": row.id, "study_id": row.study_id, "policy_version": row.policy_version,
        "decision": row.decision, "reason_code": row.reason_code, "reason": row.reason,
        "strategy_id": row.strategy_id, "strategy_version": row.strategy_version,
        "strategy_source_sha256": row.strategy_source_sha256,
        "historical_run_ids": [int(value) for value in row.historical_run_ids.split(",") if value],
        "forward_session_ids": [int(value) for value in row.forward_session_ids.split(",") if value] if row.forward_session_ids else [],
        "validation_net_return": str(row.validation_net_return) if row.validation_net_return is not None else None,
        "validation_expectancy": str(row.validation_expectancy) if row.validation_expectancy is not None else None,
        "oos_net_return": str(row.oos_net_return) if row.oos_net_return is not None else None,
        "oos_expectancy": str(row.oos_expectancy) if row.oos_expectancy is not None else None,
        "oos_max_drawdown": str(row.oos_max_drawdown) if row.oos_max_drawdown is not None else None,
        "oos_profit_factor": str(row.oos_profit_factor) if row.oos_profit_factor is not None else None,
        "forward_closing_sells": row.forward_closing_sells,
        "forward_realized_pnl": str(row.forward_realized_pnl) if row.forward_realized_pnl is not None else None,
        "created_at": row.created_at.isoformat(),
    }


def _candidate_payload(row: StrategyCandidate) -> dict:
    return {"id": row.id, "study_id": row.study_id, "evaluation_id": row.evaluation_id,
        "strategy_id": row.strategy_id, "strategy_version": row.strategy_version,
        "strategy_source_sha256": row.strategy_source_sha256, "status": row.status,
        "operator_note": row.operator_note, "promoted_at": row.promoted_at.isoformat()}


def _http_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=404 if "not found" in str(exc).lower() else 409, detail=str(exc))


@router.get("/status")
def research_status() -> dict:
    return {
        "mode": "strategy_research",
        "policy_version": "research-v1",
        "historical_methodology": "chronological_train_validation_oos_walk_forward",
        "forward_evidence": "phase_7_paper_required",
        "promotion": "manual_evidence_gated",
        "optimizer": False,
        "strategy_mutation": False,
        "live_execution_capability": False,
    }


@router.get("/policies/active")
def active_policy(session: Session = Depends(get_session)) -> dict:
    policy = bootstrap_research_policy(session)
    return {"version": policy.version, "active": policy.active,
        "min_historical_windows": policy.min_historical_windows,
        "min_validation_round_trips": policy.min_validation_round_trips,
        "min_oos_round_trips": policy.min_oos_round_trips,
        "max_oos_drawdown": str(policy.max_oos_drawdown),
        "min_oos_profit_factor": str(policy.min_oos_profit_factor),
        "max_relative_return_degradation": str(policy.max_relative_return_degradation),
        "min_forward_closing_sells": policy.min_forward_closing_sells}


@router.post("/studies")
def create_study(name: str = Query(min_length=1, max_length=128), strategy_id: str = Query(min_length=2, max_length=8),
    notes: str | None = Query(default=None, max_length=512), session: Session = Depends(get_session)) -> dict:
    try:
        return _study_payload(StrategyResearchService(session).create_study(name=name, strategy_id=strategy_id, notes=notes))
    except StrategyResearchError as exc:
        raise _http_error(exc) from exc


@router.get("/studies")
def list_studies(limit: int = Query(default=100, ge=1, le=500), session: Session = Depends(get_session)) -> list[dict]:
    rows = session.exec(select(ResearchStudy).order_by(ResearchStudy.id.desc()).limit(limit)).all()
    return [_study_payload(row) for row in rows]


@router.get("/studies/{study_id}")
def get_study(study_id: int, session: Session = Depends(get_session)) -> dict:
    try:
        return _study_payload(StrategyResearchService(session).get_study(study_id))
    except StrategyResearchError as exc:
        raise _http_error(exc) from exc


@router.post("/studies/{study_id}/windows")
def add_window(study_id: int, role: str = Query(min_length=3, max_length=16), backtest_run_id: int = Query(gt=0),
    session: Session = Depends(get_session)) -> dict:
    try:
        return _window_payload(StrategyResearchService(session).add_window(study_id, role, backtest_run_id))
    except StrategyResearchError as exc:
        raise _http_error(exc) from exc


@router.get("/studies/{study_id}/windows")
def list_windows(study_id: int, session: Session = Depends(get_session)) -> list[dict]:
    try:
        return [_window_payload(row) for row in StrategyResearchService(session).windows(study_id)]
    except StrategyResearchError as exc:
        raise _http_error(exc) from exc


@router.post("/studies/{study_id}/evaluate")
def evaluate(study_id: int, session: Session = Depends(get_session)) -> dict:
    try:
        return _evaluation_payload(ResearchEvaluator(session).evaluate(study_id))
    except StrategyResearchError as exc:
        raise _http_error(exc) from exc


@router.get("/studies/{study_id}/evaluations")
def evaluations(study_id: int, session: Session = Depends(get_session)) -> list[dict]:
    if session.get(ResearchStudy, study_id) is None:
        raise HTTPException(status_code=404, detail="research study not found")
    rows = session.exec(select(ResearchEvaluation).where(ResearchEvaluation.study_id == study_id).order_by(ResearchEvaluation.id.desc())).all()
    return [_evaluation_payload(row) for row in rows]


@router.post("/studies/{study_id}/promote")
def promote(study_id: int, note: str | None = Query(default=None, max_length=512), session: Session = Depends(get_session)) -> dict:
    try:
        return _candidate_payload(StrategyPromotionService(session).promote(study_id, note=note))
    except (ResearchPromotionError, StrategyResearchError) as exc:
        raise _http_error(exc) from exc


@router.get("/candidates")
def candidates(limit: int = Query(default=100, ge=1, le=500), session: Session = Depends(get_session)) -> list[dict]:
    rows = session.exec(select(StrategyCandidate).order_by(StrategyCandidate.id.desc()).limit(limit)).all()
    return [_candidate_payload(row) for row in rows]
