from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.models import ResearchEvaluation, ResearchStudy, StrategyCandidate
from app.strategy_research.evaluator import ResearchEvaluator
from app.strategy_research.promotion import ResearchPromotionError, StrategyPromotionService


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _study(session):
    study = ResearchStudy(name="candidate", strategy_id="S1", policy_version="research-v1",
        status="READY", strategy_version="baseline-v1", strategy_source_sha256="a" * 64,
        execution_policy="backtest-v1")
    session.add(study); session.commit(); session.refresh(study)
    return study


def _evaluation(session, study, decision="PASS"):
    row = ResearchEvaluation(study_id=study.id, policy_version="research-v1", decision=decision,
        reason_code="RESEARCH_PASS" if decision == "PASS" else "TEST_REJECT", reason="fixture",
        strategy_id="S1", strategy_version="baseline-v1", strategy_source_sha256="a" * 64,
        historical_run_ids="1,2,3", forward_session_ids="1", forward_closing_sells=3)
    session.add(row); session.commit(); session.refresh(row)
    return row


def test_promotion_creates_fresh_evaluation_each_attempt_and_only_one_candidate(monkeypatch):
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        study = _study(session)
        calls = []
        def fake_evaluate(self, study_id, *, require_current_source=False):
            calls.append((study_id, require_current_source))
            return _evaluation(self.session, study, "PASS")
        monkeypatch.setattr(ResearchEvaluator, "evaluate", fake_evaluate)
        service = StrategyPromotionService(session)
        first = service.promote(study.id, note="manual review")
        second = service.promote(study.id, note="again")
        assert first.id == second.id
        assert calls == [(study.id, True), (study.id, True)]
        assert len(session.exec(select(ResearchEvaluation)).all()) == 2
        assert len(session.exec(select(StrategyCandidate)).all()) == 1
        assert first.status == "PROMOTED"
        assert session.get(ResearchStudy, study.id).status == "PROMOTED"


def test_rejected_fresh_evaluation_creates_no_candidate(monkeypatch):
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        study = _study(session)
        monkeypatch.setattr(ResearchEvaluator, "evaluate", lambda self, study_id, require_current_source=False: _evaluation(self.session, study, "REJECT"))
        try:
            StrategyPromotionService(session).promote(study.id)
            assert False, "REJECT must not create a candidate"
        except ResearchPromotionError as exc:
            assert "rejected" in str(exc).lower()
        assert session.exec(select(StrategyCandidate)).all() == []
