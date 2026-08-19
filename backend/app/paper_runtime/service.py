from datetime import datetime, timezone

from sqlmodel import Session, select

from app.backtesting.runner import BacktestRunError, strategy_source_sha256
from app.market_data.quality import MarketDataQualityError, interval_timedelta, normalize_symbol
from app.models import (
    Account,
    Agent,
    AgentStatus,
    PaperExecution,
    PaperRequest,
    PaperRuntimeAgent,
    PaperRuntimeEvent,
    PaperRuntimeSession,
    PaperRuntimeStrategyEvidence,
)


INTERRUPTED_STATES = {"RUNNING", "DEGRADED"}
OWNERSHIP_BLOCKING_STATES = {"RUNNING", "DEGRADED", "RECOVERY_REQUIRED"}


class PaperRuntimeError(ValueError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def recover_interrupted_runtime_sessions(session: Session) -> int:
    interrupted = session.exec(
        select(PaperRuntimeSession).where(PaperRuntimeSession.status.in_(INTERRUPTED_STATES))
    ).all()
    if not interrupted:
        return 0
    now = _now()
    for runtime in interrupted:
        runtime.status = "RECOVERY_REQUIRED"
        runtime.last_error = "runtime_process_restart"
        runtime.updated_at = now
        session.add(runtime)
        session.add(PaperRuntimeEvent(session_id=runtime.id, event_type="RECOVERY_REQUIRED", reason="runtime_process_restart"))
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

    def _attachments(self, runtime: PaperRuntimeSession) -> list[PaperRuntimeAgent]:
        return self.session.exec(
            select(PaperRuntimeAgent).where(
                PaperRuntimeAgent.session_id == runtime.id,
                PaperRuntimeAgent.enabled == True,  # noqa: E712
            )
        ).all()

    def _event(self, session_id: int, event_type: str, reason: str) -> None:
        self.session.add(PaperRuntimeEvent(session_id=session_id, event_type=event_type, reason=reason[:256]))

    def _account_ids(self, runtime: PaperRuntimeSession) -> list[int]:
        agent_ids = [item.agent_id for item in self._attachments(runtime)]
        if not agent_ids:
            return []
        return [
            account.id
            for account in self.session.exec(select(Account).where(Account.agente_id.in_(agent_ids))).all()
        ]

    def _assert_agents_startable(self, runtime: PaperRuntimeSession) -> None:
        attachments = self._attachments(runtime)
        if not attachments:
            raise PaperRuntimeError("runtime session has no enabled agents")
        for item in attachments:
            agent = self.session.get(Agent, item.agent_id)
            if agent is None or agent.estado != AgentStatus.ACTIVO:
                raise PaperRuntimeError(f"agent {item.agent_id} is not active")
            account = self.session.exec(select(Account).where(Account.agente_id == item.agent_id)).first()
            if account is None:
                raise PaperRuntimeError(f"agent {item.agent_id} has no accounting account")

    def _assert_paper_recovery_clear(self, runtime: PaperRuntimeSession) -> None:
        account_ids = self._account_ids(runtime)
        if not account_ids:
            raise PaperRuntimeError("runtime session has no accounting accounts")
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

    def _bind_strategy_evidence(self, runtime: PaperRuntimeSession) -> None:
        try:
            current_sha = strategy_source_sha256()
        except BacktestRunError as exc:
            raise PaperRuntimeError(f"runtime strategy source fingerprint unavailable: {exc}") from exc

        for attachment in self._attachments(runtime):
            agent = self.session.get(Agent, attachment.agent_id)
            if agent is None:
                raise PaperRuntimeError(f"agent {attachment.agent_id} not found")
            existing = self.session.exec(
                select(PaperRuntimeStrategyEvidence).where(
                    PaperRuntimeStrategyEvidence.session_id == runtime.id,
                    PaperRuntimeStrategyEvidence.agent_id == agent.id,
                )
            ).first()
            strategy_id = agent.estrategia.value
            if existing is None:
                self.session.add(
                    PaperRuntimeStrategyEvidence(
                        session_id=runtime.id,
                        agent_id=agent.id,
                        strategy_id=strategy_id,
                        strategy_version="baseline-v1",
                        strategy_source_sha256=current_sha,
                    )
                )
                continue
            if existing.strategy_id != strategy_id:
                raise PaperRuntimeError("runtime agent strategy changed after session start")
            if existing.strategy_source_sha256 != current_sha:
                raise PaperRuntimeError("runtime strategy source changed after session start")

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
        if not normalized_name:
            raise PaperRuntimeError("runtime session name is required")
        try:
            normalized_symbol = normalize_symbol(symbol)
            normalized_interval = interval.strip()
            interval_timedelta(normalized_interval)
        except MarketDataQualityError as exc:
            raise PaperRuntimeError(f"invalid runtime market configuration: {exc}") from exc

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
            account = self.session.exec(select(Account).where(Account.agente_id == agent_id)).first()
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
        self.session.commit(); self.session.refresh(runtime)
        return runtime

    def _assert_no_active_conflict(self, runtime: PaperRuntimeSession) -> None:
        agent_ids = {item.agent_id for item in self._attachments(runtime)}
        if not agent_ids:
            raise PaperRuntimeError("runtime session has no enabled agents")
        candidates = self.session.exec(
            select(PaperRuntimeSession).where(
                PaperRuntimeSession.id != runtime.id,
                PaperRuntimeSession.status.in_(OWNERSHIP_BLOCKING_STATES),
                PaperRuntimeSession.symbol == runtime.symbol,
                PaperRuntimeSession.interval == runtime.interval,
            )
        ).all()
        for candidate in candidates:
            candidate_agents = {item.agent_id for item in self._attachments(candidate)}
            if agent_ids & candidate_agents:
                raise PaperRuntimeError("agent is already active or awaiting recovery in another runtime session")

    def start(self, session_id: int) -> PaperRuntimeSession:
        runtime = self._session(session_id)
        if runtime.status not in {"CREATED", "PAUSED"}:
            raise PaperRuntimeError(f"cannot start runtime from {runtime.status}")
        self._assert_agents_startable(runtime)
        self._assert_paper_recovery_clear(runtime)
        self._assert_no_active_conflict(runtime)
        self._bind_strategy_evidence(runtime)
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
        self._assert_agents_startable(runtime)
        self._assert_paper_recovery_clear(runtime)
        self._bind_strategy_evidence(runtime)
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
