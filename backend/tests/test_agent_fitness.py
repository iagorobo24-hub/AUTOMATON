from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.accounting.service import AccountingService
from app.agent_evolution.fitness import FitnessService
from app.agent_evolution.policy import bootstrap_evolution_policy
from app.models import (
    Agent,
    AgentFitnessEvaluation,
    AgentStatus,
    BacktestDataset,
    BacktestRun,
    BacktestRunEvidence,
    Fill,
    StrategyEnum,
    Trade,
    TradeType,
)

UTC = timezone.utc


def _engine():
    return create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


def _agent(session: Session, strategy=StrategyEnum.S1):
    agent = Agent(nombre="fitness", presupuesto_inicial=1000, presupuesto_actual=1000, estrategia=strategy, estado=AgentStatus.ACTIVO)
    session.add(agent); session.commit(); session.refresh(agent)
    account = AccountingService(session).create_account(agent.id, Decimal("1000"))
    return agent, account


def _backtest(session: Session, strategy_id="S1", *, round_trips=5, net_return="0.05", expectancy="2", drawdown="0.10", with_fingerprint=True):
    dataset = BacktestDataset(
        symbol="BTC/USDT", interval="1h", provider="fixture_real_history",
        requested_start=datetime(2026, 1, 1, tzinfo=UTC), requested_end=datetime(2026, 2, 1, tzinfo=UTC),
        actual_start=datetime(2026, 1, 1, tzinfo=UTC), actual_end=datetime(2026, 1, 31, 23, tzinfo=UTC),
        candle_count=744, content_sha256=(strategy_id.lower()[0] * 64), status="READY",
    )
    session.add(dataset); session.commit(); session.refresh(dataset)
    run = BacktestRun(
        dataset_id=dataset.id, dataset_sha256=dataset.content_sha256,
        strategy_id=strategy_id, strategy_version="baseline-v1", execution_policy="backtest-v1",
        initial_capital=Decimal("1000"), fee_bps=Decimal("10"), slippage_bps=Decimal("10"),
        position_fraction=Decimal("0.25"), risk_profile_version="backtest-risk-v1",
        status="COMPLETED", initial_equity=Decimal("1000"), final_equity=Decimal("1050"),
        net_pnl=Decimal("50"), net_return=Decimal(net_return), round_trip_count=round_trips,
        expectancy=Decimal(expectancy), max_drawdown=Decimal(drawdown), trade_count=round_trips * 2,
    )
    session.add(run); session.commit(); session.refresh(run)
    if with_fingerprint:
        session.add(BacktestRunEvidence(run_id=run.id, strategy_code_sha256="f" * 64)); session.commit()
    return run


def _paper_closes(session: Session, account_id: int, count: int):
    for i in range(count):
        session.add(Fill(
            order_id=1000 + i, account_id=account_id, symbol="BTC/USDT", side="SELL",
            quantity=Decimal("0.01"), price=Decimal("110"), fee=Decimal("0.01"),
            observed_at=datetime(2026, 3, 1, 12, i, tzinfo=UTC), evidence_mode="paper",
        ))
    session.commit()


def test_fitness_rejects_when_reproducible_backtest_or_agent_paper_evidence_is_missing():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_evolution_policy(session)
        agent, account = _agent(session)
        evaluation = FitnessService(session).evaluate(agent.id)
        assert evaluation.decision == "REJECT"
        assert "BACKTEST_EVIDENCE_MISSING" in evaluation.reason_codes
        assert "PAPER_TRADES_INSUFFICIENT" in evaluation.reason_codes
        assert "PAPER_REALIZED_PNL_NOT_POSITIVE" in evaluation.reason_codes


def test_fitness_rejects_strategy_mismatch_or_missing_source_fingerprint():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_evolution_policy(session)
        agent, account = _agent(session, StrategyEnum.S1)
        _backtest(session, "S2")
        _backtest(session, "S1", with_fingerprint=False)
        account.realized_pnl = Decimal("10"); session.add(account); session.commit(); _paper_closes(session, account.id, 3)

        evaluation = FitnessService(session).evaluate(agent.id)
        assert evaluation.decision == "REJECT"
        assert evaluation.backtest_run_id is None
        assert "BACKTEST_EVIDENCE_MISSING" in evaluation.reason_codes


def test_fitness_passes_only_with_matching_backtest_and_agent_specific_paper_evidence():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_evolution_policy(session)
        agent, account = _agent(session)
        run = _backtest(session, "S1", round_trips=6, net_return="0.04", expectancy="1.5", drawdown="0.08")
        account.realized_pnl = Decimal("12"); session.add(account); session.commit(); _paper_closes(session, account.id, 4)

        evaluation = FitnessService(session).evaluate(agent.id)
        assert evaluation.decision == "PASS"
        assert evaluation.backtest_run_id == run.id
        assert evaluation.strategy_code_sha256 == "f" * 64
        assert evaluation.paper_closed_trades == 4
        assert evaluation.paper_realized_pnl == Decimal("12")
        assert evaluation.reason_codes == "PASS"


def test_legacy_trade_rows_never_satisfy_paper_fitness():
    engine = _engine(); SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        bootstrap_evolution_policy(session)
        agent, account = _agent(session)
        _backtest(session, "S1")
        for _ in range(10):
            session.add(Trade(agente_id=agent.id, precio_entrada=100, precio_salida=110, cantidad=1, tipo=TradeType.LONG, resultado=10))
        session.commit()

        evaluation = FitnessService(session).evaluate(agent.id)
        assert evaluation.decision == "REJECT"
        assert evaluation.paper_closed_trades == 0
        assert "PAPER_TRADES_INSUFFICIENT" in evaluation.reason_codes
        assert len(session.exec(select(AgentFitnessEvaluation)).all()) == 1
