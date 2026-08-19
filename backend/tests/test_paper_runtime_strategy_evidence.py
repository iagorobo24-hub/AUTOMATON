from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.accounting.service import AccountingService
from app.models import Agent, AgentStatus, PaperRuntimeStrategyEvidence, StrategyEnum
from app.paper_runtime.service import PaperRuntimeError, PaperRuntimeService


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def test_first_start_persists_strategy_source_identity_and_resume_reuses_it(monkeypatch):
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent = Agent(nombre="source-bound", presupuesto_inicial=1000, presupuesto_actual=1000,
            estrategia=StrategyEnum.S1, estado=AgentStatus.ACTIVO)
        session.add(agent); session.commit(); session.refresh(agent)
        AccountingService(session).create_account(agent.id, 1000)
        runtime = PaperRuntimeService(session).create_session(
            name="source-bound", symbol="BTC/USDT", interval="1m", agent_ids=[agent.id]
        )
        monkeypatch.setattr("app.paper_runtime.service.strategy_source_sha256", lambda: "a" * 64)
        service = PaperRuntimeService(session)
        service.start(runtime.id)
        evidence = session.exec(select(PaperRuntimeStrategyEvidence)).one()
        assert evidence.session_id == runtime.id
        assert evidence.agent_id == agent.id
        assert evidence.strategy_id == "S1"
        assert evidence.strategy_version == "baseline-v1"
        assert evidence.strategy_source_sha256 == "a" * 64

        service.pause(runtime.id)
        service.resume(runtime.id)
        assert len(session.exec(select(PaperRuntimeStrategyEvidence)).all()) == 1


def test_resume_fails_closed_when_strategy_source_changed(monkeypatch):
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent = Agent(nombre="drift", presupuesto_inicial=1000, presupuesto_actual=1000,
            estrategia=StrategyEnum.S1, estado=AgentStatus.ACTIVO)
        session.add(agent); session.commit(); session.refresh(agent)
        AccountingService(session).create_account(agent.id, 1000)
        service = PaperRuntimeService(session)
        runtime = service.create_session(name="drift", symbol="BTC/USDT", interval="1m", agent_ids=[agent.id])
        monkeypatch.setattr("app.paper_runtime.service.strategy_source_sha256", lambda: "a" * 64)
        service.start(runtime.id); service.pause(runtime.id)
        monkeypatch.setattr("app.paper_runtime.service.strategy_source_sha256", lambda: "b" * 64)
        try:
            service.resume(runtime.id)
            assert False, "source drift must block resuming the same runtime session"
        except PaperRuntimeError as exc:
            assert "source changed" in str(exc)
