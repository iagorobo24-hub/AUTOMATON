from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import Session, select

from app.models import (
    BacktestDataset,
    BacktestRun,
    BacktestRunEvidence,
    ResearchStudy,
    ResearchWindow,
    StrategyEnum,
)

ROLE_SEQUENCE = ("TRAIN", "VALIDATION", "OOS")


class StrategyResearchError(ValueError):
    pass


def _now():
    return datetime.now(timezone.utc)


class StrategyResearchService:
    def __init__(self, session: Session):
        self.session = session

    def get_study(self, study_id: int) -> ResearchStudy:
        study = self.session.get(ResearchStudy, study_id)
        if study is None:
            raise StrategyResearchError("research study not found")
        return study

    def create_study(self, *, name: str, strategy_id: str, notes: str | None = None) -> ResearchStudy:
        normalized_name = name.strip()
        if not normalized_name:
            raise StrategyResearchError("research study name is required")
        normalized_strategy = strategy_id.strip().upper()
        if normalized_strategy not in {item.value for item in StrategyEnum}:
            raise StrategyResearchError("unknown strategy id")
        study = ResearchStudy(
            name=normalized_name,
            strategy_id=normalized_strategy,
            notes=notes.strip()[:512] if notes and notes.strip() else None,
        )
        self.session.add(study)
        self.session.commit(); self.session.refresh(study)
        return study

    def windows(self, study_id: int) -> list[ResearchWindow]:
        self.get_study(study_id)
        return self.session.exec(
            select(ResearchWindow)
            .where(ResearchWindow.study_id == study_id)
            .order_by(ResearchWindow.ordinal)
        ).all()

    def _run_bundle(self, run_id: int):
        run = self.session.get(BacktestRun, run_id)
        if run is None:
            raise StrategyResearchError("backtest run not found")
        if run.status != "COMPLETED":
            raise StrategyResearchError("research window requires a COMPLETED Backtest run")
        dataset = self.session.get(BacktestDataset, run.dataset_id)
        if dataset is None or dataset.status != "READY":
            raise StrategyResearchError("research window requires a READY Backtest dataset")
        evidence = self.session.exec(
            select(BacktestRunEvidence).where(BacktestRunEvidence.run_id == run.id)
        ).first()
        if evidence is None or not evidence.strategy_code_sha256:
            raise StrategyResearchError("research window requires strategy source fingerprint evidence")
        return run, dataset, evidence

    def _assert_compatible(self, study: ResearchStudy, run: BacktestRun, source_sha: str) -> None:
        if run.strategy_id != study.strategy_id:
            raise StrategyResearchError("research window strategy does not match study")
        if study.strategy_source_sha256 is None:
            return
        checks = (
            (run.strategy_version, study.strategy_version, "strategy version"),
            (source_sha, study.strategy_source_sha256, "strategy source"),
            (run.execution_policy, study.execution_policy, "execution policy"),
            (Decimal(run.fee_bps), Decimal(study.fee_bps), "fee"),
            (Decimal(run.slippage_bps), Decimal(study.slippage_bps), "slippage"),
            (Decimal(run.position_fraction), Decimal(study.position_fraction), "position fraction"),
        )
        for actual, expected, label in checks:
            if actual != expected:
                raise StrategyResearchError(f"research window {label} does not match frozen study configuration")

    def add_window(self, study_id: int, role: str, backtest_run_id: int) -> ResearchWindow:
        study = self.get_study(study_id)
        normalized_role = role.strip().upper()
        existing = self.windows(study_id)
        expected_role = ROLE_SEQUENCE[len(existing) % len(ROLE_SEQUENCE)]
        if normalized_role != expected_role:
            raise StrategyResearchError(f"next research window role must be {expected_role}")
        run, dataset, evidence = self._run_bundle(backtest_run_id)
        self._assert_compatible(study, run, evidence.strategy_code_sha256)
        if existing:
            first_run, first_dataset, _ = self._run_bundle(existing[0].backtest_run_id)
            invariant_checks = (
                (dataset.symbol, first_dataset.symbol, "market symbol"),
                (dataset.interval, first_dataset.interval, "timeframe"),
                (Decimal(run.initial_capital), Decimal(first_run.initial_capital), "initial capital"),
                (run.risk_profile_version, first_run.risk_profile_version, "risk profile"),
            )
            for actual, expected, label in invariant_checks:
                if actual != expected:
                    raise StrategyResearchError(f"research window {label} does not match study evidence contract")
            _, previous_dataset, _ = self._run_bundle(existing[-1].backtest_run_id)
            if dataset.actual_start <= previous_dataset.actual_end:
                raise StrategyResearchError("research windows must be chronological and non-overlapping")
        duplicate = self.session.exec(
            select(ResearchWindow).where(
                ResearchWindow.study_id == study.id,
                ResearchWindow.backtest_run_id == run.id,
            )
        ).first()
        if duplicate is not None:
            raise StrategyResearchError("backtest run is already attached to this study")
        if study.strategy_source_sha256 is None:
            study.strategy_version = run.strategy_version
            study.strategy_source_sha256 = evidence.strategy_code_sha256
            study.execution_policy = run.execution_policy
            study.fee_bps = Decimal(run.fee_bps)
            study.slippage_bps = Decimal(run.slippage_bps)
            study.position_fraction = Decimal(run.position_fraction)
        study.status = "READY" if len(existing) + 1 >= 3 else "DRAFT"
        study.updated_at = _now()
        window = ResearchWindow(
            study_id=study.id,
            backtest_run_id=run.id,
            role=normalized_role,
            ordinal=len(existing),
        )
        self.session.add(study); self.session.add(window)
        self.session.commit(); self.session.refresh(window)
        return window
