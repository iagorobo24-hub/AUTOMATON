from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool

from app.accounting.service import AccountingService
from app.models import Agent, AgentStatus, StrategyEnum
from app.paper_runtime.service import PaperRuntimeError, PaperRuntimeService, recover_interrupted_runtime_sessions


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _agent(session: Session):
    agent = Agent(nombre="runtime", presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=StrategyEnum.S1, estado=AgentStatus.ACTIVO)
    session.add(agent); session.commit(); session.refresh(agent)
    AccountingService(session).create_account(agent.id, 1000)
    return agent


def test_session_lifecycle_and_single_active_assignment():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent = _agent(session)
        service = PaperRuntimeService(session)
        runtime = service.create_session(name="paper-1", symbol="BTC/USDT", interval="1m", agent_ids=[agent.id])
        assert runtime.status == "CREATED"
        service.start(runtime.id)
        assert session.get(type(runtime), runtime.id).status == "RUNNING"

        other = service.create_session(name="paper-2", symbol="BTC/USDT", interval="1m", agent_ids=[agent.id])
        try:
            service.start(other.id)
            assert False, "conflicting session must fail"
        except PaperRuntimeError as exc:
            assert "already active" in str(exc)

        service.pause(runtime.id)
        assert session.get(type(runtime), runtime.id).status == "PAUSED"
        service.resume(runtime.id)
        assert session.get(type(runtime), runtime.id).status == "RUNNING"
        service.stop(runtime.id)
        assert session.get(type(runtime), runtime.id).status == "STOPPED"


def test_restart_marks_running_or_degraded_sessions_recovery_required():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent = _agent(session)
        service = PaperRuntimeService(session)
        first = service.create_session(name="a", symbol="BTC/USDT", interval="1m", agent_ids=[agent.id])
        service.start(first.id)
        first = session.get(type(first), first.id)
        first.status = "DEGRADED"; session.add(first); session.commit()

        changed = recover_interrupted_runtime_sessions(session)
        assert changed == 1
        recovered = session.get(type(first), first.id)
        assert recovered.status == "RECOVERY_REQUIRED"
        assert recovered.last_error == "runtime_process_restart"
