from decimal import Decimal

from sqlmodel import Session, select

from app.accounting.integrity import AccountingIntegrityService
from app.agent_evolution.policy import active_evolution_policy
from app.models import (
    Account,
    Agent,
    AgentFitnessEvaluation,
    BacktestRun,
    BacktestRunEvidence,
    Fill,
)

ZERO = Decimal("0")


class FitnessError(ValueError):
    pass


class FitnessService:
    def __init__(self, session: Session):
        self.session = session

    def _matching_backtest(self, strategy_id: str):
        runs = self.session.exec(
            select(BacktestRun)
            .where(BacktestRun.status == "COMPLETED", BacktestRun.strategy_id == strategy_id)
            .order_by(BacktestRun.id.desc())
        ).all()
        for run in runs:
            evidence = self.session.exec(
                select(BacktestRunEvidence).where(BacktestRunEvidence.run_id == run.id)
            ).first()
            if evidence is not None:
                return run, evidence
        return None, None

    def evaluate(self, agent_id: int) -> AgentFitnessEvaluation:
        agent = self.session.get(Agent, agent_id)
        if agent is None:
            raise FitnessError("agent not found")
        policy = active_evolution_policy(self.session)
        account = self.session.exec(select(Account).where(Account.agente_id == agent.id)).first()
        strategy_id = agent.estrategia.value
        run, run_evidence = self._matching_backtest(strategy_id)

        paper_closed = 0
        paper_realized = ZERO
        integrity_issues: tuple[str, ...] = ("account_not_found",)
        if account is not None:
            paper_closed = len(
                self.session.exec(
                    select(Fill).where(
                        Fill.account_id == account.id,
                        Fill.evidence_mode == "paper",
                        Fill.side == "SELL",
                    )
                ).all()
            )
            paper_realized = Decimal(account.realized_pnl)
            integrity_issues = AccountingIntegrityService(self.session).issues(account.id)

        reasons: list[str] = []
        if run is None or run_evidence is None:
            reasons.append("BACKTEST_EVIDENCE_MISSING")
        else:
            if run.round_trip_count is None or run.round_trip_count < policy.min_backtest_round_trips:
                reasons.append("BACKTEST_ROUND_TRIPS_INSUFFICIENT")
            if run.net_return is None or Decimal(run.net_return) <= Decimal(policy.min_backtest_net_return):
                reasons.append("BACKTEST_RETURN_NOT_POSITIVE")
            if run.expectancy is None or Decimal(run.expectancy) <= Decimal(policy.min_backtest_expectancy):
                reasons.append("BACKTEST_EXPECTANCY_NOT_POSITIVE")
            if run.max_drawdown is None or Decimal(run.max_drawdown) > Decimal(policy.max_backtest_drawdown):
                reasons.append("BACKTEST_DRAWDOWN_EXCEEDED")

        if integrity_issues:
            reasons.append("ACCOUNTING_INTEGRITY_FAILED")
        if paper_closed < policy.min_paper_closed_trades:
            reasons.append("PAPER_TRADES_INSUFFICIENT")
        if paper_realized <= Decimal(policy.min_paper_realized_pnl):
            reasons.append("PAPER_REALIZED_PNL_NOT_POSITIVE")

        evaluation = AgentFitnessEvaluation(
            agent_id=agent.id,
            policy_id=policy.id,
            policy_version=policy.version,
            backtest_run_id=run.id if run is not None and run_evidence is not None else None,
            strategy_id=strategy_id,
            strategy_version=run.strategy_version if run is not None and run_evidence is not None else None,
            strategy_code_sha256=run_evidence.strategy_code_sha256 if run_evidence is not None else None,
            backtest_round_trips=run.round_trip_count if run is not None and run_evidence is not None else None,
            backtest_net_return=run.net_return if run is not None and run_evidence is not None else None,
            backtest_expectancy=run.expectancy if run is not None and run_evidence is not None else None,
            backtest_max_drawdown=run.max_drawdown if run is not None and run_evidence is not None else None,
            paper_closed_trades=paper_closed,
            paper_realized_pnl=paper_realized,
            decision="PASS" if not reasons else "REJECT",
            reason_codes="PASS" if not reasons else "|".join(reasons),
        )
        self.session.add(evaluation)
        self.session.commit()
        self.session.refresh(evaluation)
        return evaluation
