from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.models import BacktestDataset, BacktestRun, BacktestRunEvidence
from app.strategy_research.evaluator import ResearchEvaluator
from app.strategy_research.service import StrategyResearchService


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _run(session, *, day, net="0.10", expectancy="5", dd="0.10", pf="1.20", trips=6):
    start = datetime(2026, 2, day, tzinfo=timezone.utc); end = start + timedelta(days=2)
    dataset = BacktestDataset(
        symbol="BTC/USDT", interval="1h", provider="fixture_real",
        requested_start=start, requested_end=end, actual_start=start, actual_end=end,
        candle_count=48, content_sha256=f"{day + 100:064x}"[-64:], status="READY",
    )
    session.add(dataset); session.commit(); session.refresh(dataset)
    run = BacktestRun(
        dataset_id=dataset.id, dataset_sha256=dataset.content_sha256, strategy_id="S1",
        strategy_version="baseline-v1", execution_policy="backtest-v1", initial_capital=Decimal("1000"),
        fee_bps=Decimal("10"), slippage_bps=Decimal("10"), position_fraction=Decimal("0.25"),
        risk_profile_version="backtest-risk-v1", status="COMPLETED", round_trip_count=trips,
        net_return=Decimal(net), expectancy=Decimal(expectancy), max_drawdown=Decimal(dd),
        profit_factor=Decimal(pf) if pf is not None else None,
    )
    session.add(run); session.commit(); session.refresh(run)
    session.add(BacktestRunEvidence(run_id=run.id, strategy_code_sha256="a" * 64)); session.commit()
    return run


def _study(session, runs):
    service = StrategyResearchService(session)
    study = service.create_study(name="historical", strategy_id="S1")
    for role, run in zip(("TRAIN", "VALIDATION", "OOS"), runs):
        service.add_window(study.id, role, run.id)
    return study


def test_historical_gate_passes_positive_validation_and_oos_with_fixed_contract():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        study = _study(session, [_run(session, day=1), _run(session, day=4, net="0.12"), _run(session, day=7, net="0.08")])
        result = ResearchEvaluator(session).historical_gate(study.id)
        assert result.passed is True
        assert result.reason_code == "HISTORICAL_PASS"
        assert result.metrics["validation_net_return"] == Decimal("0.12")
        assert result.metrics["oos_net_return"] == Decimal("0.08")


def test_historical_gate_rejects_small_sample_and_oos_degradation_or_risk_metrics():
    cases = [
        {"trips": 4, "net": "0.08", "dd": "0.10", "pf": "1.20", "code": "OOS_SAMPLE_TOO_SMALL"},
        {"trips": 6, "net": "0.04", "dd": "0.10", "pf": "1.20", "code": "OOS_RETURN_DEGRADATION"},
        {"trips": 6, "net": "0.08", "dd": "0.20", "pf": "1.20", "code": "OOS_DRAWDOWN_LIMIT"},
        {"trips": 6, "net": "0.08", "dd": "0.10", "pf": "1.01", "code": "OOS_PROFIT_FACTOR"},
    ]
    for index, case in enumerate(cases):
        engine = _engine(); SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            train = _run(session, day=1)
            validation = _run(session, day=4, net="0.10")
            oos = _run(session, day=7, trips=case["trips"], net=case["net"], dd=case["dd"], pf=case["pf"])
            study = _study(session, [train, validation, oos])
            result = ResearchEvaluator(session).historical_gate(study.id)
            assert result.passed is False, index
            assert result.reason_code == case["code"], index


def test_promotion_evaluation_fails_closed_when_active_strategy_source_drifted(monkeypatch):
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        study = _study(session, [_run(session, day=1), _run(session, day=4), _run(session, day=7)])
        monkeypatch.setattr("app.strategy_research.evaluator.strategy_source_sha256", lambda: "b" * 64)
        evaluation = ResearchEvaluator(session).evaluate(study.id, require_current_source=True)
        assert evaluation.decision == "REJECT"
        assert evaluation.reason_code == "CURRENT_SOURCE_DRIFT"
