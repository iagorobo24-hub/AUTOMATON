from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.accounting.service import AccountingService
from app.models import (
    Agent, AgentStatus, BacktestDataset, BacktestRun, BacktestRunEvidence,
    Fill, Order, PaperExecution, PaperRequest, PaperRuntimeAgent, PaperRuntimeCycle,
    PaperRuntimeSession, StrategyEnum,
)
from app.strategy_research.evaluator import ResearchEvaluator
from app.strategy_research.service import StrategyResearchService


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _historical_study(session):
    service = StrategyResearchService(session)
    study = service.create_study(name="forward", strategy_id="S1")
    for idx, role in enumerate(("TRAIN", "VALIDATION", "OOS")):
        start = datetime(2026, 3, 1 + idx * 4, tzinfo=timezone.utc); end = start + timedelta(days=2)
        ds = BacktestDataset(symbol="BTC/USDT", interval="1h", provider="fixture_real", requested_start=start,
            requested_end=end, actual_start=start, actual_end=end, candle_count=48,
            content_sha256=f"{500 + idx:064x}"[-64:], status="READY")
        session.add(ds); session.commit(); session.refresh(ds)
        run = BacktestRun(dataset_id=ds.id, dataset_sha256=ds.content_sha256, strategy_id="S1",
            strategy_version="baseline-v1", execution_policy="backtest-v1", initial_capital=Decimal("1000"),
            fee_bps=Decimal("10"), slippage_bps=Decimal("10"), position_fraction=Decimal("0.25"),
            risk_profile_version="backtest-risk-v1", status="COMPLETED", round_trip_count=6,
            net_return=Decimal("0.10"), expectancy=Decimal("5"), max_drawdown=Decimal("0.10"),
            profit_factor=Decimal("1.20"))
        session.add(run); session.commit(); session.refresh(run)
        session.add(BacktestRunEvidence(run_id=run.id, strategy_code_sha256="a" * 64)); session.commit()
        service.add_window(study.id, role, run.id)
    return study


def _forward_session(session, *, status="STOPPED", origin="strategy_runtime", sells=3, pnl="25", interval="1h"):
    agent = Agent(nombre="forward-agent", presupuesto_inicial=1000, presupuesto_actual=1000,
        estrategia=StrategyEnum.S1, estado=AgentStatus.ACTIVO)
    session.add(agent); session.commit(); session.refresh(agent)
    account = AccountingService(session).create_account(agent.id, Decimal("1000"))
    account.realized_pnl = Decimal(pnl); session.add(account); session.commit()
    runtime = PaperRuntimeSession(name="forward-paper", symbol="BTC/USDT", interval=interval, status=status,
        started_at=datetime(2026, 4, 1, tzinfo=timezone.utc), stopped_at=datetime(2026, 4, 2, tzinfo=timezone.utc) if status == "STOPPED" else None)
    session.add(runtime); session.commit(); session.refresh(runtime)
    session.add(PaperRuntimeAgent(session_id=runtime.id, agent_id=agent.id)); session.commit()
    for index in range(sells):
        order = Order(account_id=account.id, symbol="BTC/USDT", side="SELL", status="FILLED",
            requested_quantity=Decimal("0.1"), filled_quantity=Decimal("0.1"))
        session.add(order); session.commit(); session.refresh(order)
        observed = datetime(2026, 4, 1, 1 + index, tzinfo=timezone.utc)
        fill = Fill(order_id=order.id, account_id=account.id, symbol="BTC/USDT", side="SELL",
            quantity=Decimal("0.1"), price=Decimal("100"), fee=Decimal("0.01"), observed_at=observed,
            evidence_mode="paper")
        session.add(fill); session.commit(); session.refresh(fill)
        execution = PaperExecution(account_id=account.id, agent_id=agent.id, order_id=order.id, fill_id=fill.id,
            symbol="BTC/USDT", side="SELL", requested_quantity=Decimal("0.1"), origin=origin,
            provider="fixture_real", provider_symbol="BTCUSDT", quote_observed_at=observed,
            quote_received_at=observed, market_price=Decimal("100"), fill_price=Decimal("99.9"),
            slippage_bps=Decimal("10"), fee_bps=Decimal("10"), fee=Decimal("0.01"), status="FILLED")
        session.add(execution); session.commit(); session.refresh(execution)
        cycle = PaperRuntimeCycle(session_id=runtime.id, agent_id=agent.id, account_id=account.id,
            symbol="BTC/USDT", interval=interval, candle_close=observed, signal="SELL", outcome="FILLED",
            paper_execution_id=execution.id)
        session.add(cycle); session.commit()
    return runtime, agent, account


def test_forward_gate_requires_stopped_runtime_and_three_provenanced_closing_sells():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        study = _historical_study(session)
        runtime, agent, account = _forward_session(session)
        result = ResearchEvaluator(session).forward_gate(study.id)
        assert result.passed is True
        assert result.reason_code == "FORWARD_PASS"
        assert result.metrics["forward_closing_sells"] == 3
        assert result.metrics["forward_realized_pnl"] == Decimal("25")
        assert result.metrics["forward_session_ids"] == [runtime.id]


def test_forward_gate_rejects_incomplete_or_unprovenanced_evidence():
    cases = [
        {"status": "RUNNING", "origin": "strategy_runtime", "sells": 3, "pnl": "25", "code": "FORWARD_SESSION_REQUIRED"},
        {"status": "STOPPED", "origin": "operator", "sells": 3, "pnl": "25", "code": "FORWARD_ATTRIBUTION_AMBIGUOUS"},
        {"status": "STOPPED", "origin": "strategy_runtime", "sells": 2, "pnl": "25", "code": "FORWARD_CLOSE_SAMPLE_TOO_SMALL"},
        {"status": "STOPPED", "origin": "strategy_runtime", "sells": 3, "pnl": "0", "code": "FORWARD_PNL_NON_POSITIVE"},
    ]
    for case in cases:
        engine = _engine(); SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            study = _historical_study(session)
            _forward_session(session, status=case["status"], origin=case["origin"], sells=case["sells"], pnl=case["pnl"])
            result = ResearchEvaluator(session).forward_gate(study.id)
            assert result.passed is False
            assert result.reason_code == case["code"]


def test_forward_gate_rejects_different_timeframe_and_unresolved_paper_recovery():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        study = _historical_study(session)
        _forward_session(session, interval="1m")
        result = ResearchEvaluator(session).forward_gate(study.id)
        assert result.passed is False
        assert result.reason_code == "FORWARD_SESSION_REQUIRED"

    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        study = _historical_study(session)
        runtime, agent, account = _forward_session(session)
        session.add(PaperRequest(request_id="ambiguous-forward", request_fingerprint="f" * 64,
            account_id=account.id, status="RECOVERY_REQUIRED", http_status=409, error_detail="ambiguous"))
        session.commit()
        result = ResearchEvaluator(session).forward_gate(study.id)
        assert result.passed is False
        assert result.reason_code == "FORWARD_RECOVERY_UNRESOLVED"
