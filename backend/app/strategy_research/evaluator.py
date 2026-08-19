from dataclasses import dataclass, field
from decimal import Decimal

from sqlmodel import Session, select

from app.backtesting.runner import BacktestRunError, strategy_source_sha256
from app.models import (
    Account,
    Agent,
    BacktestDataset,
    BacktestRun,
    PaperExecution,
    PaperRequest,
    PaperRuntimeAgent,
    PaperRuntimeCycle,
    PaperRuntimeSession,
    ResearchEvaluation,
    ResearchStudy,
    ResearchWindow,
)
from app.strategy_research.policy import bootstrap_research_policy
from app.strategy_research.service import StrategyResearchError, StrategyResearchService


@dataclass(frozen=True)
class ResearchGateResult:
    passed: bool
    reason_code: str
    reason: str
    metrics: dict[str, Decimal | int | str | list[int] | None] = field(default_factory=dict)


class ResearchEvaluator:
    def __init__(self, session: Session):
        self.session = session

    def _study(self, study_id: int) -> ResearchStudy:
        return StrategyResearchService(self.session).get_study(study_id)

    def _windows_with_runs(self, study_id: int):
        windows = self.session.exec(
            select(ResearchWindow)
            .where(ResearchWindow.study_id == study_id)
            .order_by(ResearchWindow.ordinal)
        ).all()
        result = []
        for window in windows:
            run = self.session.get(BacktestRun, window.backtest_run_id)
            if run is None:
                raise StrategyResearchError("research window points to missing Backtest run")
            result.append((window, run))
        return result

    def historical_gate(self, study_id: int) -> ResearchGateResult:
        policy = bootstrap_research_policy(self.session)
        self._study(study_id)
        items = self._windows_with_runs(study_id)
        if len(items) < policy.min_historical_windows or len(items) % 3 != 0:
            return ResearchGateResult(False, "HISTORICAL_WINDOWS_INCOMPLETE", "complete TRAIN/VALIDATION/OOS folds are required")

        validations = []
        oos_runs = []
        run_ids = []
        for index in range(0, len(items), 3):
            fold = items[index:index + 3]
            if [item[0].role for item in fold] != ["TRAIN", "VALIDATION", "OOS"]:
                return ResearchGateResult(False, "HISTORICAL_ROLE_SEQUENCE", "research folds must be TRAIN/VALIDATION/OOS")
            _, validation = fold[1]
            _, oos = fold[2]
            run_ids.extend([entry[1].id for entry in fold])
            for label, run, minimum in (
                ("VALIDATION", validation, policy.min_validation_round_trips),
                ("OOS", oos, policy.min_oos_round_trips),
            ):
                if run.status != "COMPLETED":
                    return ResearchGateResult(False, f"{label}_NOT_COMPLETED", f"{label} run is not completed")
                if run.round_trip_count is None or run.round_trip_count < minimum:
                    return ResearchGateResult(False, f"{label}_SAMPLE_TOO_SMALL", f"{label} round-trip sample is below research-v1")
                if run.net_return is None or Decimal(run.net_return) <= 0:
                    return ResearchGateResult(False, f"{label}_RETURN_NON_POSITIVE", f"{label} net return must be positive")
                if run.expectancy is None or Decimal(run.expectancy) <= 0:
                    return ResearchGateResult(False, f"{label}_EXPECTANCY_NON_POSITIVE", f"{label} expectancy must be positive")
            if oos.max_drawdown is None or Decimal(oos.max_drawdown) > Decimal(policy.max_oos_drawdown):
                return ResearchGateResult(False, "OOS_DRAWDOWN_LIMIT", "OOS drawdown exceeds research-v1")
            if oos.profit_factor is not None and Decimal(oos.profit_factor) < Decimal(policy.min_oos_profit_factor):
                return ResearchGateResult(False, "OOS_PROFIT_FACTOR", "OOS profit factor is below research-v1")
            validation_return = Decimal(validation.net_return)
            oos_return = Decimal(oos.net_return)
            degradation = (validation_return - oos_return) / validation_return
            if degradation > Decimal(policy.max_relative_return_degradation):
                return ResearchGateResult(False, "OOS_RETURN_DEGRADATION", "OOS return degraded beyond research-v1 limit")
            validations.append(validation)
            oos_runs.append(oos)

        metrics = {
            "historical_run_ids": run_ids,
            "validation_net_return": min(Decimal(item.net_return) for item in validations),
            "validation_expectancy": min(Decimal(item.expectancy) for item in validations),
            "oos_net_return": min(Decimal(item.net_return) for item in oos_runs),
            "oos_expectancy": min(Decimal(item.expectancy) for item in oos_runs),
            "oos_max_drawdown": max(Decimal(item.max_drawdown) for item in oos_runs),
            "oos_profit_factor": min(
                (Decimal(item.profit_factor) for item in oos_runs if item.profit_factor is not None),
                default=None,
            ),
        }
        return ResearchGateResult(True, "HISTORICAL_PASS", "historical validation and OOS evidence satisfy research-v1", metrics)

    def forward_gate(self, study_id: int) -> ResearchGateResult:
        policy = bootstrap_research_policy(self.session)
        study = self._study(study_id)
        items = self._windows_with_runs(study_id)
        if not items:
            return ResearchGateResult(False, "FORWARD_SESSION_REQUIRED", "historical study identity is required before forward evidence")
        reference_run = items[0][1]
        reference_dataset = self.session.get(BacktestDataset, reference_run.dataset_id)
        if reference_dataset is None:
            return ResearchGateResult(False, "FORWARD_MARKET_IDENTITY_MISSING", "reference historical market identity is missing")

        stopped = self.session.exec(
            select(PaperRuntimeSession).where(
                PaperRuntimeSession.status == "STOPPED",
                PaperRuntimeSession.symbol == reference_dataset.symbol,
                PaperRuntimeSession.interval == reference_dataset.interval,
            )
        ).all()
        qualifying_session_ids: list[int] = []
        qualifying_account_ids: set[int] = set()
        qualifying_execution_ids_by_account: dict[int, set[int]] = {}
        closing_execution_ids: set[int] = set()

        for runtime in stopped:
            if runtime.stopped_at is None:
                continue
            attachments = self.session.exec(
                select(PaperRuntimeAgent).where(
                    PaperRuntimeAgent.session_id == runtime.id,
                    PaperRuntimeAgent.enabled == True,  # noqa: E712
                )
            ).all()
            session_qualified = False
            for attachment in attachments:
                agent = self.session.get(Agent, attachment.agent_id)
                if agent is None or agent.estrategia.value != study.strategy_id:
                    continue
                account = self.session.exec(select(Account).where(Account.agente_id == agent.id)).first()
                if account is None:
                    continue
                cycles = self.session.exec(
                    select(PaperRuntimeCycle).where(
                        PaperRuntimeCycle.session_id == runtime.id,
                        PaperRuntimeCycle.agent_id == agent.id,
                    )
                ).all()
                if not cycles:
                    continue
                session_qualified = True
                qualifying_account_ids.add(account.id)
                execution_ids = qualifying_execution_ids_by_account.setdefault(account.id, set())
                for cycle in cycles:
                    if cycle.paper_execution_id is None:
                        continue
                    execution = self.session.get(PaperExecution, cycle.paper_execution_id)
                    if execution is None:
                        continue
                    if (
                        execution.agent_id == agent.id
                        and execution.account_id == account.id
                        and execution.status == "FILLED"
                        and execution.origin == "strategy_runtime"
                        and execution.fill_id is not None
                    ):
                        execution_ids.add(execution.id)
                        if execution.side == "SELL":
                            closing_execution_ids.add(execution.id)
            if session_qualified:
                qualifying_session_ids.append(runtime.id)

        if not qualifying_session_ids:
            return ResearchGateResult(False, "FORWARD_SESSION_REQUIRED", "a completed STOPPED Phase 7 session on the same market/timeframe is required")

        for account_id in qualifying_account_ids:
            unresolved_request = self.session.exec(
                select(PaperRequest).where(
                    PaperRequest.account_id == account_id,
                    PaperRequest.status == "RECOVERY_REQUIRED",
                )
            ).first()
            unresolved_execution = self.session.exec(
                select(PaperExecution).where(
                    PaperExecution.account_id == account_id,
                    PaperExecution.status == "RECOVERY_REQUIRED",
                )
            ).first()
            if unresolved_request is not None or unresolved_execution is not None:
                return ResearchGateResult(False, "FORWARD_RECOVERY_UNRESOLVED", "forward Paper recovery evidence is unresolved")

            allowed_ids = qualifying_execution_ids_by_account.get(account_id, set())
            filled_executions = self.session.exec(
                select(PaperExecution).where(
                    PaperExecution.account_id == account_id,
                    PaperExecution.status == "FILLED",
                )
            ).all()
            if any(execution.id not in allowed_ids for execution in filled_executions):
                return ResearchGateResult(
                    False,
                    "FORWARD_ATTRIBUTION_AMBIGUOUS",
                    "forward account PnL includes FILLED execution outside the qualifying Research sessions",
                )

        closing_sells = len(closing_execution_ids)
        if closing_sells < policy.min_forward_closing_sells:
            return ResearchGateResult(False, "FORWARD_CLOSE_SAMPLE_TOO_SMALL", "forward closing SELL sample is below research-v1")

        realized_pnl = sum(
            (Decimal(self.session.get(Account, account_id).realized_pnl) for account_id in qualifying_account_ids),
            Decimal("0"),
        )
        if realized_pnl <= 0:
            return ResearchGateResult(False, "FORWARD_PNL_NON_POSITIVE", "forward account-level realized PnL context must be positive")

        return ResearchGateResult(
            True,
            "FORWARD_PASS",
            "forward Phase 7 Paper evidence satisfies research-v1",
            {
                "forward_session_ids": qualifying_session_ids,
                "forward_closing_sells": closing_sells,
                "forward_realized_pnl": realized_pnl,
            },
        )

    def _persist_evaluation(
        self,
        study: ResearchStudy,
        decision: str,
        reason_code: str,
        reason: str,
        historical: ResearchGateResult,
        forward: ResearchGateResult | None,
    ) -> ResearchEvaluation:
        historical_ids = historical.metrics.get("historical_run_ids") or [
            run.id for _, run in self._windows_with_runs(study.id)
        ]
        forward_ids = forward.metrics.get("forward_session_ids") if forward else None
        evaluation = ResearchEvaluation(
            study_id=study.id,
            policy_version=study.policy_version,
            decision=decision,
            reason_code=reason_code,
            reason=reason[:512],
            strategy_id=study.strategy_id,
            strategy_version=study.strategy_version or "unfrozen",
            strategy_source_sha256=study.strategy_source_sha256 or "missing",
            historical_run_ids=",".join(str(item) for item in historical_ids),
            forward_session_ids=",".join(str(item) for item in forward_ids) if forward_ids else None,
            validation_net_return=historical.metrics.get("validation_net_return"),
            validation_expectancy=historical.metrics.get("validation_expectancy"),
            oos_net_return=historical.metrics.get("oos_net_return"),
            oos_expectancy=historical.metrics.get("oos_expectancy"),
            oos_max_drawdown=historical.metrics.get("oos_max_drawdown"),
            oos_profit_factor=historical.metrics.get("oos_profit_factor"),
            forward_closing_sells=int(forward.metrics.get("forward_closing_sells", 0)) if forward else 0,
            forward_realized_pnl=forward.metrics.get("forward_realized_pnl") if forward else None,
        )
        self.session.add(evaluation)
        study.status = "EVALUATED" if decision == "PASS" else "REJECTED"
        self.session.add(study)
        self.session.commit(); self.session.refresh(evaluation)
        return evaluation

    def evaluate(self, study_id: int, *, require_current_source: bool = False) -> ResearchEvaluation:
        study = self._study(study_id)
        historical = self.historical_gate(study_id)
        if not historical.passed:
            return self._persist_evaluation(
                study, "REJECT", historical.reason_code, historical.reason, historical, None
            )
        if require_current_source:
            try:
                current_sha = strategy_source_sha256()
            except BacktestRunError as exc:
                return self._persist_evaluation(
                    study,
                    "REJECT",
                    "CURRENT_SOURCE_UNAVAILABLE",
                    str(exc),
                    historical,
                    None,
                )
            if not study.strategy_source_sha256 or current_sha != study.strategy_source_sha256:
                return self._persist_evaluation(
                    study,
                    "REJECT",
                    "CURRENT_SOURCE_DRIFT",
                    "active strategy source no longer matches frozen research evidence",
                    historical,
                    None,
                )
        forward = self.forward_gate(study_id)
        if not forward.passed:
            return self._persist_evaluation(
                study, "REJECT", forward.reason_code, forward.reason, historical, forward
            )
        return self._persist_evaluation(
            study,
            "PASS",
            "RESEARCH_PASS",
            "historical and forward evidence satisfy research-v1",
            historical,
            forward,
        )
