from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.accounting.service import AccountingService
from app.agent_evolution.fitness import FitnessService
from app.agent_evolution.policy import bootstrap_evolution_policy
from app.backtesting.runner import strategy_source_sha256
from app.models import (
    Agent, AgentStatus, BacktestDataset, BacktestRun, BacktestRunEvidence,
    Order, Fill, PaperExecution, PaperRequest, StrategyEnum,
)

UTC = timezone.utc


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _ready_candidate(session: Session, *, status=AgentStatus.ACTIVO, source_sha=None):
    bootstrap_evolution_policy(session)
    agent = Agent(nombre="candidate", presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=StrategyEnum.S1, estado=status)
    session.add(agent); session.commit(); session.refresh(agent)
    account = AccountingService(session).create_account(agent.id, Decimal("1000"))
    dataset = BacktestDataset(
        symbol="BTC/USDT", interval="1h", provider="fixture_real_history",
        requested_start=datetime(2026,1,1,tzinfo=UTC), requested_end=datetime(2026,2,1,tzinfo=UTC),
        actual_start=datetime(2026,1,1,tzinfo=UTC), actual_end=datetime(2026,1,31,23,tzinfo=UTC),
        candle_count=744, content_sha256="1"*64, status="READY",
    )
    session.add(dataset); session.commit(); session.refresh(dataset)
    run = BacktestRun(
        dataset_id=dataset.id, dataset_sha256=dataset.content_sha256, strategy_id="S1",
        strategy_version="baseline-v1", execution_policy="backtest-v1", initial_capital=Decimal("1000"),
        fee_bps=Decimal("10"), slippage_bps=Decimal("10"), position_fraction=Decimal("0.25"),
        risk_profile_version="backtest-risk-v1", status="COMPLETED", initial_equity=Decimal("1000"),
        final_equity=Decimal("1050"), net_pnl=Decimal("50"), net_return=Decimal("0.05"),
        trade_count=12, round_trip_count=6, expectancy=Decimal("2"), max_drawdown=Decimal("0.08"),
    )
    session.add(run); session.commit(); session.refresh(run)
    session.add(BacktestRunEvidence(run_id=run.id, strategy_code_sha256=source_sha or strategy_source_sha256())); session.commit()
    account.realized_pnl = Decimal("12"); session.add(account); session.commit()
    for i in range(3):
        observed = datetime(2026,3,1,12,i,tzinfo=UTC)
        order = Order(account_id=account.id, symbol="BTC/USDT", side="SELL", status="FILLED", requested_quantity=Decimal("0.01"), filled_quantity=Decimal("0.01"))
        session.add(order); session.flush()
        fill = Fill(order_id=order.id, account_id=account.id, symbol="BTC/USDT", side="SELL", quantity=Decimal("0.01"), price=Decimal("110"), fee=Decimal("0.01"), observed_at=observed, evidence_mode="paper")
        session.add(fill); session.flush()
        session.add(PaperExecution(account_id=account.id, agent_id=agent.id, order_id=order.id, fill_id=fill.id, symbol="BTC/USDT", side="SELL", requested_quantity=Decimal("0.01"), origin="operator", policy_version="paper-v1", provider="fixture_real", provider_symbol="BTCUSDT", quote_observed_at=observed, quote_received_at=observed, market_price=Decimal("110"), fill_price=Decimal("110"), slippage_bps=Decimal("10"), fee_bps=Decimal("10"), fee=Decimal("0.01"), status="FILLED", evidence_mode="paper"))
    session.commit()
    return agent, account


def test_inactive_agent_cannot_receive_fitness_pass():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent, _ = _ready_candidate(session, status=AgentStatus.MUERTO)
        evaluation = FitnessService(session).evaluate(agent.id)
        assert evaluation.decision == "REJECT"
        assert "AGENT_NOT_ACTIVE" in evaluation.reason_codes


def test_backtest_from_stale_strategy_source_cannot_receive_fitness_pass():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent, _ = _ready_candidate(session, source_sha="0"*64)
        evaluation = FitnessService(session).evaluate(agent.id)
        assert evaluation.decision == "REJECT"
        assert "STRATEGY_SOURCE_CHANGED" in evaluation.reason_codes


def test_unresolved_paper_recovery_blocks_fitness_pass():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        agent, account = _ready_candidate(session)
        session.add(PaperRequest(request_id="recovery-1", request_fingerprint="a"*64, account_id=account.id, status="RECOVERY_REQUIRED", http_status=409, error_detail="ambiguous restart")); session.commit()
        evaluation = FitnessService(session).evaluate(agent.id)
        assert evaluation.decision == "REJECT"
        assert "PAPER_RECOVERY_REQUIRED" in evaluation.reason_codes
