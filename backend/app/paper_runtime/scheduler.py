import asyncio
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.database import SessionLocal
from app.market_data.quality import MarketDataQualityError, MarketDataUnavailable
from app.market_data.router import get_market_data_service
from app.market_data.service import MarketDataService
from app.models import PaperRuntimeAgent, PaperRuntimeEvent, PaperRuntimeSession
from app.paper_runtime.cycle import PaperRuntimeCycleError, evaluate_agent_cycle
from app.paper_runtime.execution import execute_runtime_cycle
from app.paper_runtime.service import PaperRuntimeError


async def run_runtime_once(
    session: Session,
    session_id: int,
    market_data: MarketDataService,
) -> PaperRuntimeSession:
    runtime = session.get(PaperRuntimeSession, session_id)
    if runtime is None:
        raise PaperRuntimeError("runtime session not found")
    if runtime.status != "RUNNING":
        return runtime

    attachments = session.exec(
        select(PaperRuntimeAgent).where(
            PaperRuntimeAgent.session_id == runtime.id,
            PaperRuntimeAgent.enabled == True,  # noqa: E712
        )
    ).all()
    any_failure = False
    last_error = None

    for attachment in attachments:
        try:
            cycle = await evaluate_agent_cycle(session, runtime.id, attachment.agent_id, market_data)
            if cycle is not None and cycle.outcome in {"INTENT_BUY", "INTENT_SELL"}:
                cycle = await execute_runtime_cycle(session, cycle.id, market_data)
            if cycle is not None and cycle.outcome == "RECOVERY_REQUIRED":
                return session.get(PaperRuntimeSession, runtime.id)
            if cycle is not None and cycle.outcome in {"SKIPPED_PROVIDER_UNAVAILABLE", "SKIPPED_MARKET_DATA_INVALID"}:
                any_failure = True
                last_error = cycle.error_detail
        except MarketDataUnavailable as exc:
            any_failure = True
            last_error = f"provider unavailable: {exc}"
        except MarketDataQualityError as exc:
            any_failure = True
            last_error = f"market data invalid: {exc}"
        except PaperRuntimeCycleError as exc:
            any_failure = True
            last_error = str(exc)
        except Exception as exc:
            any_failure = True
            last_error = f"runtime cycle failed: {exc}"

    runtime = session.get(PaperRuntimeSession, session_id)
    now = datetime.now(timezone.utc)
    runtime.heartbeat_at = now
    runtime.updated_at = now
    if any_failure:
        runtime.consecutive_failures += 1
        runtime.last_error = (last_error or "runtime operational failure")[:256]
        session.add(PaperRuntimeEvent(session_id=runtime.id, event_type="OPERATIONAL_FAILURE", reason=runtime.last_error))
        if runtime.consecutive_failures >= runtime.max_consecutive_failures:
            runtime.status = "DEGRADED"
            session.add(PaperRuntimeEvent(session_id=runtime.id, event_type="DEGRADED", reason="maximum consecutive runtime failures reached"))
    else:
        runtime.consecutive_failures = 0
        runtime.last_error = None
    session.add(runtime)
    session.commit(); session.refresh(runtime)
    return runtime


class PaperRuntimeScheduler:
    """Own in-process asyncio tasks while SQLite remains runtime authority."""

    def __init__(self):
        self._tasks: dict[int, asyncio.Task] = {}

    def is_running(self, session_id: int) -> bool:
        task = self._tasks.get(session_id)
        return task is not None and not task.done()

    async def _loop(self, session_id: int) -> None:
        try:
            while True:
                with SessionLocal() as session:
                    runtime = session.get(PaperRuntimeSession, session_id)
                    if runtime is None or runtime.status != "RUNNING":
                        return
                    poll_seconds = runtime.poll_seconds
                    await run_runtime_once(session, session_id, get_market_data_service())
                    runtime = session.get(PaperRuntimeSession, session_id)
                    if runtime is None or runtime.status != "RUNNING":
                        return
                await asyncio.sleep(poll_seconds)
        finally:
            self._tasks.pop(session_id, None)

    def spawn(self, session_id: int) -> None:
        if self.is_running(session_id):
            return
        self._tasks[session_id] = asyncio.create_task(self._loop(session_id))

    def cancel(self, session_id: int) -> None:
        task = self._tasks.pop(session_id, None)
        if task is not None:
            task.cancel()

    def cancel_all(self) -> None:
        for task in self._tasks.values():
            task.cancel()
        self._tasks.clear()


runtime_scheduler = PaperRuntimeScheduler()


def get_runtime_scheduler() -> PaperRuntimeScheduler:
    return runtime_scheduler
