from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.models import BacktestDataset, BacktestRun, BacktestRunEvidence, ResearchWindow
from app.strategy_research.service import StrategyResearchError, StrategyResearchService


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _run(session: Session, *, strategy="S1", start_day=1, source="a" * 64, fee="10", slippage="10", fraction="0.25"):
    start = datetime(2026, 1, start_day, tzinfo=timezone.utc)
    end = start + timedelta(days=5)
    dataset = BacktestDataset(
        symbol="BTC/USDT", interval="1h", provider="fixture_real",
        requested_start=start, requested_end=end, actual_start=start, actual_end=end,
        candle_count=120, content_sha256=f"{start_day:064x}"[-64:], status="READY",
    )
    session.add(dataset); session.commit(); session.refresh(dataset)
    run = BacktestRun(
        dataset_id=dataset.id, dataset_sha256=dataset.content_sha256,
        strategy_id=strategy, strategy_version="baseline-v1", execution_policy="backtest-v1",
        initial_capital=Decimal("1000"), fee_bps=Decimal(fee), slippage_bps=Decimal(slippage),
        position_fraction=Decimal(fraction), risk_profile_version="backtest-risk-v1",
        status="COMPLETED", round_trip_count=6, net_return=Decimal("0.10"),
        expectancy=Decimal("5"), max_drawdown=Decimal("0.10"), profit_factor=Decimal("1.2"),
    )
    session.add(run); session.commit(); session.refresh(run)
    session.add(BacktestRunEvidence(run_id=run.id, strategy_code_sha256=source)); session.commit()
    return run


def test_first_window_freezes_identity_and_repeating_train_validation_oos_order():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        runs = [_run(session, start_day=1), _run(session, start_day=7), _run(session, start_day=13), _run(session, start_day=19)]
        service = StrategyResearchService(session)
        study = service.create_study(name="S1 baseline", strategy_id="S1")
        service.add_window(study.id, "TRAIN", runs[0].id)
        service.add_window(study.id, "VALIDATION", runs[1].id)
        service.add_window(study.id, "OOS", runs[2].id)
        service.add_window(study.id, "TRAIN", runs[3].id)
        study = service.get_study(study.id)
        assert study.strategy_source_sha256 == "a" * 64
        assert study.fee_bps == Decimal("10")
        assert [w.role for w in session.exec(select(ResearchWindow).order_by(ResearchWindow.ordinal)).all()] == ["TRAIN", "VALIDATION", "OOS", "TRAIN"]


def test_window_rejects_incompatible_or_overlapping_evidence():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        base = _run(session, start_day=1)
        wrong_source = _run(session, start_day=7, source="b" * 64)
        wrong_cost = _run(session, start_day=13, fee="20")
        service = StrategyResearchService(session)
        study = service.create_study(name="strict", strategy_id="S1")
        service.add_window(study.id, "TRAIN", base.id)
        for run in (wrong_source, wrong_cost):
            try:
                service.add_window(study.id, "VALIDATION", run.id)
                assert False, "incompatible evidence must fail"
            except StrategyResearchError:
                pass


def test_window_rejects_role_sequence_and_non_completed_run():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        first = _run(session, start_day=1)
        second = _run(session, start_day=7)
        second.status = "INVALID"; session.add(second); session.commit()
        service = StrategyResearchService(session)
        study = service.create_study(name="order", strategy_id="S1")
        try:
            service.add_window(study.id, "VALIDATION", first.id)
            assert False
        except StrategyResearchError:
            pass
        service.add_window(study.id, "TRAIN", first.id)
        try:
            service.add_window(study.id, "VALIDATION", second.id)
            assert False
        except StrategyResearchError:
            pass
