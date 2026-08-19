from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models import (
    Account,
    Agent,
    AgentStatus,
    PaperExecution,
    PaperRequest,
    PaperRuntimeAgent,
    PaperRuntimeEvent,
    PaperRuntimeSession,
)


ACTIVE_STATES = {"RUNNING", "DEGRADED"}


class PaperRuntimeError(ValueError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def recover_interrupted_runtime_sessions(session: Session) -> int:
    interrupted = session.exec(
        select(PaperRuntimeSession).where(PaperRuntimeSession.status.in_(ACTIVE_STATES))
    ).all()
    if not interrupted:
        return 0
    now = _now()
    for runtime in interrupted:
        runtime.status = "RECOVERY_REQUIRED"
        runtime.last_error = "runtime_process_restart"
        runtime.updated_at = now
        session.add(runtime)
        session.add(
            PaperRuntimeEvent(
                session_id=runtime.id,
                event_type="RECOVERY_REQUIRED",
                reason="runtime_process_restart",
            )
        )
    session.commit()
    return len(interrupted)


class PaperRuntimeService:
    def __init__(self, session: Session):
        self.session = session

    def _session(self, session_id: int) -> PaperRuntimeSession:
        runtime = self.session.get(PaperRuntimeSession, session_id)
        if runtime is None:
            raise PaperRuntimeError("runtime session not found")
        return runtime

    def _event(self, session_id: int, event_type: str, reason: str) -> None:
        self.session.add(
            PaperRuntimeEvent(
                session_id=session_id,
                event_type=event_type,
                reason=reason[:256],
            )
        )

    def create_session(
        self,
        *,
        name: str,
        symbol: str,
        interval: str,
        agent_ids: list[int],
        poll_seconds: int = 15,
        max_consecutive_failures: int = 5,
    ) -> PaperRuntimeSession:
        normalized_name = name.strip()
        normalized_symbol = symbol.strip().upper()
        normalized_interval = interval.strip()
        if not normalized_name:
            raise PaperRuntimeError("runtime session name is required")
        if "/" not in normalized_symbol:
            raise PaperRuntimeError("runtime symbol must use BASE/QUOTE format")
        if not normalized_interval:
            raise PaperRuntimeError("runtime interval is required")
        unique_ids = list(dict.fromkeys(agent_ids))
        if not unique_ids:
            raise PaperRuntimeError("runtime session requires at least one agent")
        if poll_seconds <= 0:
            raise PaperRuntimeError("poll_seconds must be positive")
        if max_consecutive_failures <= 0:
            raise PaperRuntimeError("max_consecutive_failures must be positive")

        for agent_id in unique_ids:
            agent = self.session.get(Agent, agent_id)
            if agent is None:
                raise PaperRuntimeError(f"agent {agent_id} not found")
            if agent.estado != AgentStatus.ACTIVO:
                raise PaperRuntimeError(f"agent {agent_id} is not active")
            account = self.session.exec(
                select(Account).where(Account.agente_id == agent_id)
            ).first()
            if account is None:
                raise PaperRuntimeError(f"agent {agent_id} has no accounting account")

        runtime = PaperRuntimeSession(
            name=normalized_name,
            symbol=normalized_symbol,
            interval=normalized_interval,
            poll_seconds=poll_seconds,
            max_consecutive_failures=max_consecutive_failures,
        )
        self.session.add(runtime)
        self.session.flush()
        for agent_id in unique_ids:
            self.session.add(PaperRuntimeAgent(session_id=runtime.id, agent_id=agent_id))
        self._event(runtime.id, "CREATED", "operator_created_runtime_session")
        self.session.commit()
        self.session.refresh(runtime)
        return runtime

    def _assert_no_active_conflict(self, runtime: PaperRuntimeSession) -> None:
        agent_ids = {
            item.agent_id
            for item in self.session.exec(
                select(PaperRuntimeAgent).where(
                    PaperRuntimeAgent.session_id == runtime.id,
                    PaperRuntimeAgent.enabled == True,  # noqa: E712
                )
            ).all()
        }
        if not agent_ids:
            raise PaperRuntimeError("runtime session has no enabled agents")
        candidates = self.session.exec(
            select(PaperRuntimeSession).where(
                PaperRuntimeSession.id != runtime.id,
                PaperRuntimeSession.status.in_(ACTIVE_STATES),
                PaperRuntimeSession.symbol == runtime.symbol,
                PaperRuntimeSession.interval == runtime.interval,
            )
        ).all()
        for candidate in candidates:
            candidate_agents = {
                item.agent_id
                for item in self.session.exec(
                    select(PaperRuntimeAgent).where(
                        PaperRuntimeAgent.session_id == candidate.id,
                        PaperRuntimeAgent.enabled == True,  # noqa: E712
                    )
                ).all()
            }
            if agent_ids & candidate_agents:
                raise PaperRuntimeError("agent is already active in another runtime session")

    def start(self, session_id: int) -> PaperRuntimeSession:
        runtime = self._session(session_id)
        if runtime.status not in {"CREATED", "PAUSED"}:
            raise PaperRuntimeError(f"cannot start runtime from {runtime.status}")
        self._assert_no_active_conflict(runtime)
        now = _now()
        runtime.status = "RUNNING"
        runtime.started_at = runtime.started_at or now
        runtime.heartbeat_at = now
        runtime.last_error = None
        runtime.updated_at = now
        self.session.add(runtime)
        self._event(runtime.id, "STARTED", "operator_started_runtime_session")
        self.session.commit(); self.session.refresh(runtime)
        return runtime

    def pause(self, session_id: int) -> PaperRuntimeSession:
        runtime = self._session(session_id)
        if runtime.status not in {"RUNNING", "DEGRADED"}:
            raise PaperRuntimeError(f"cannot pause runtime from {runtime.status}")
        runtime.status = "PAUSED"
        runtime.updated_at = _now()
        self.session.add(runtime)
        self._event(runtime.id, "PAUSED", "operator_paused_runtime_session")
        self.session.commit(); self.session.refresh(runtime)
        return runtime

    def resume(self, session_id: int) -> PaperRuntimeSession:
        runtime = self._session(session_id)
        if runtime.status != "PAUSED":
            raise PaperRuntimeError(f"cannot resume runtime from {runtime.status}")
        return self.start(session_id)

    def recover(self, session_id: int) -> PaperRuntimeSession:
        runtime = self._session(session_id)
        if runtime.status != "RECOVERY_REQUIRED":
            raise PaperRuntimeError("runtime session is not awaiting recovery")
        attachments = self.session.exec(
            select(PaperRuntimeAgent).where(PaperRuntimeAgent.session_id == runtime.id)
        ).all()
        agent_ids = [item.agent_id for item in attachments]
        accounts = self.session.exec(select(Account).where(Account.agente_id.in_(agent_ids))).all()
        account_ids = [account.id for account in accounts]
        if account_ids:
            unresolved_request = self.session.exec(
                select(PaperRequest).where(
                    PaperRequest.account_id.in_(account_ids),
                    PaperRequest.status == "RECOVERY_REQUIRED",
                )
            ).first()
            unresolved_execution = self.session.exec(
                select(PaperExecution).where(
                    PaperExecution.account_id.in_(account_ids),
                    PaperExecution.status == "RECOVERY_REQUIRED",
                )
            ).first()
            if unresolved_request is not None or unresolved_execution is not None:
                raise PaperRuntimeError("Paper recovery state is unresolved")
        runtime.status = "PAUSED"
        runtime.consecutive_failures = 0
        runtime.last_error = None
        runtime.updated_at = _now()
        self.session.add(runtime)
        self._event(runtime.id, "RECOVERED", "operator_confirmed_runtime_recovery")
        self.session.commit(); self.session.refresh(runtime)
        return runtime

    def stop(self, session_id: int) -> PaperRuntimeSession:
        runtime = self._session(session_id)
        if runtime.status == "STOPPED":
            raise PaperRuntimeError("runtime session is already stopped")
        now = _now()
        runtime.status = "STOPPED"
        runtime.stopped_at = now
        runtime.updated_at = now
        self.session.add(runtime)
        self._event(runtime.id, "STOPPED", "operator_stopped_runtime_session")
        self.session.commit(); self.session.refresh(runtime)
        return runtime
