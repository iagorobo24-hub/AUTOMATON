from dataclasses import dataclass, field
from decimal import Decimal

from sqlmodel import Session, select

from app.models import (
    Account,
    Agent,
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
        study = self._study(study_id)
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
        raise NotImplementedError

    def evaluate(self, study_id: int) -> ResearchEvaluation:
        raise NotImplementedError
