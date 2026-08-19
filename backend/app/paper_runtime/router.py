from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models import PaperRuntimeAgent, PaperRuntimeCycle, PaperRuntimeEvent, PaperRuntimeSession
from app.paper_runtime.scheduler import PaperRuntimeScheduler, get_runtime_scheduler
from app.paper_runtime.service import PaperRuntimeError, PaperRuntimeService

router = APIRouter()


def _session_payload(runtime: PaperRuntimeSession) -> dict:
    return {
        "id": runtime.id,
        "name": runtime.name,
        "symbol": runtime.symbol,
        "interval": runtime.interval,
        "policy_version": runtime.policy_version,
        "status": runtime.status,
        "poll_seconds": runtime.poll_seconds,
        "max_consecutive_failures": runtime.max_consecutive_failures,
        "consecutive_failures": runtime.consecutive_failures,
        "heartbeat_at": runtime.heartbeat_at.isoformat() if runtime.heartbeat_at else None,
        "last_cycle_at": runtime.last_cycle_at.isoformat() if runtime.last_cycle_at else None,
        "last_error": runtime.last_error,
        "created_at": runtime.created_at.isoformat(),
        "started_at": runtime.started_at.isoformat() if runtime.started_at else None,
        "stopped_at": runtime.stopped_at.isoformat() if runtime.stopped_at else None,
    }


def _cycle_payload(cycle: PaperRuntimeCycle) -> dict:
    return {
        "id": cycle.id,
        "session_id": cycle.session_id,
        "agent_id": cycle.agent_id,
        "account_id": cycle.account_id,
        "symbol": cycle.symbol,
        "interval": cycle.interval,
        "candle_close": cycle.candle_close.isoformat(),
        "signal": cycle.signal,
        "outcome": cycle.outcome,
        "request_id": cycle.request_id,
        "risk_decision_id": cycle.risk_decision_id,
        "paper_execution_id": cycle.paper_execution_id,
        "error_detail": cycle.error_detail,
        "created_at": cycle.created_at.isoformat(),
    }


def _handle(exc: PaperRuntimeError) -> HTTPException:
    status = 404 if "not found" in str(exc) else 409
    return HTTPException(status_code=status, detail=str(exc))


@router.get("/status")
def runtime_status() -> dict:
    return {
        "mode": "paper_runtime",
        "policy_version": "runtime-v1",
        "market_data": "real_only",
        "capital": "virtual_only",
        "scheduler": "persistent_sqlite_plus_in_process_asyncio",
        "risk_gate": "required",
        "paper_execution": "required",
        "accounting": "authoritative",
        "auto_replication": False,
        "live_execution_capability": False,
        "synthetic_fallback": False,
    }


@router.post("/sessions")
def create_session(
    name: str = Query(min_length=1, max_length=128),
    symbol: str = Query(default="BTC/USDT", min_length=3, max_length=32),
    interval: str = Query(default="1m", min_length=2, max_length=16),
    agent_ids: list[int] = Query(),
    poll_seconds: int = Query(default=15, ge=1, le=3600),
    max_consecutive_failures: int = Query(default=5, ge=1, le=100),
    session: Session = Depends(get_session),
) -> dict:
    try:
        runtime = PaperRuntimeService(session).create_session(
            name=name,
            symbol=symbol,
            interval=interval,
            agent_ids=agent_ids,
            poll_seconds=poll_seconds,
            max_consecutive_failures=max_consecutive_failures,
        )
    except PaperRuntimeError as exc:
        raise _handle(exc) from exc
    return _session_payload(runtime)


@router.get("/sessions")
def list_sessions(
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> list[dict]:
    items = session.exec(select(PaperRuntimeSession).order_by(PaperRuntimeSession.id.desc()).limit(limit)).all()
    return [_session_payload(item) for item in items]


@router.get("/sessions/{session_id}")
def get_session_detail(session_id: int, session: Session = Depends(get_session)) -> dict:
    runtime = session.get(PaperRuntimeSession, session_id)
    if runtime is None:
        raise HTTPException(status_code=404, detail="runtime session not found")
    agents = session.exec(select(PaperRuntimeAgent).where(PaperRuntimeAgent.session_id == session_id)).all()
    events = session.exec(
        select(PaperRuntimeEvent).where(PaperRuntimeEvent.session_id == session_id).order_by(PaperRuntimeEvent.id.desc()).limit(100)
    ).all()
    payload = _session_payload(runtime)
    payload["agents"] = [
        {
            "agent_id": item.agent_id,
            "enabled": item.enabled,
            "last_candle_close": item.last_candle_close.isoformat() if item.last_candle_close else None,
            "last_signal": item.last_signal,
            "last_outcome": item.last_outcome,
            "last_cycle_id": item.last_cycle_id,
        }
        for item in agents
    ]
    payload["events"] = [
        {"id": item.id, "event_type": item.event_type, "reason": item.reason, "created_at": item.created_at.isoformat()}
        for item in events
    ]
    return payload


@router.get("/sessions/{session_id}/cycles")
def get_cycles(
    session_id: int,
    limit: int = Query(default=200, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> list[dict]:
    if session.get(PaperRuntimeSession, session_id) is None:
        raise HTTPException(status_code=404, detail="runtime session not found")
    cycles = session.exec(
        select(PaperRuntimeCycle).where(PaperRuntimeCycle.session_id == session_id).order_by(PaperRuntimeCycle.id.desc()).limit(limit)
    ).all()
    return [_cycle_payload(item) for item in cycles]


@router.post("/sessions/{session_id}/start")
async def start_session(
    session_id: int,
    session: Session = Depends(get_session),
    scheduler: PaperRuntimeScheduler = Depends(get_runtime_scheduler),
) -> dict:
    try:
        runtime = PaperRuntimeService(session).start(session_id)
    except PaperRuntimeError as exc:
        raise _handle(exc) from exc
    scheduler.spawn(session_id)
    return _session_payload(runtime)


@router.post("/sessions/{session_id}/pause")
async def pause_session(
    session_id: int,
    session: Session = Depends(get_session),
    scheduler: PaperRuntimeScheduler = Depends(get_runtime_scheduler),
) -> dict:
    try:
        runtime = PaperRuntimeService(session).pause(session_id)
    except PaperRuntimeError as exc:
        raise _handle(exc) from exc
    scheduler.cancel(session_id)
    return _session_payload(runtime)


@router.post("/sessions/{session_id}/resume")
async def resume_session(
    session_id: int,
    session: Session = Depends(get_session),
    scheduler: PaperRuntimeScheduler = Depends(get_runtime_scheduler),
) -> dict:
    try:
        runtime = PaperRuntimeService(session).resume(session_id)
    except PaperRuntimeError as exc:
        raise _handle(exc) from exc
    scheduler.spawn(session_id)
    return _session_payload(runtime)


@router.post("/sessions/{session_id}/recover")
def recover_session(
    session_id: int,
    session: Session = Depends(get_session),
) -> dict:
    try:
        runtime = PaperRuntimeService(session).recover(session_id)
    except PaperRuntimeError as exc:
        raise _handle(exc) from exc
    return _session_payload(runtime)


@router.post("/sessions/{session_id}/stop")
async def stop_session(
    session_id: int,
    session: Session = Depends(get_session),
    scheduler: PaperRuntimeScheduler = Depends(get_runtime_scheduler),
) -> dict:
    try:
        runtime = PaperRuntimeService(session).stop(session_id)
    except PaperRuntimeError as exc:
        raise _handle(exc) from exc
    scheduler.cancel(session_id)
    return _session_payload(runtime)
