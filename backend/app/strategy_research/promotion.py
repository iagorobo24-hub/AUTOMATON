from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models import ResearchStudy, StrategyCandidate
from app.strategy_research.evaluator import ResearchEvaluator


class ResearchPromotionError(ValueError):
    pass


class StrategyPromotionService:
    def __init__(self, session: Session):
        self.session = session

    def promote(self, study_id: int, *, note: str | None = None) -> StrategyCandidate:
        study = self.session.get(ResearchStudy, study_id)
        if study is None:
            raise ResearchPromotionError("research study not found")

        evaluation = ResearchEvaluator(self.session).evaluate(
            study_id,
            require_current_source=True,
        )
        if evaluation.decision != "PASS":
            raise ResearchPromotionError(
                f"research promotion rejected: {evaluation.reason_code} - {evaluation.reason}"
            )

        existing = self.session.exec(
            select(StrategyCandidate).where(
                StrategyCandidate.strategy_id == evaluation.strategy_id,
                StrategyCandidate.strategy_version == evaluation.strategy_version,
                StrategyCandidate.strategy_source_sha256 == evaluation.strategy_source_sha256,
            )
        ).first()
        if existing is not None:
            study.status = "PROMOTED"
            study.updated_at = datetime.now(timezone.utc)
            self.session.add(study)
            self.session.commit()
            return existing

        candidate = StrategyCandidate(
            study_id=study.id,
            evaluation_id=evaluation.id,
            strategy_id=evaluation.strategy_id,
            strategy_version=evaluation.strategy_version,
            strategy_source_sha256=evaluation.strategy_source_sha256,
            status="PROMOTED",
            operator_note=note.strip()[:512] if note and note.strip() else None,
            promoted_at=datetime.now(timezone.utc),
        )
        study.status = "PROMOTED"
        study.updated_at = datetime.now(timezone.utc)
        self.session.add(candidate)
        self.session.add(study)
        self.session.commit(); self.session.refresh(candidate)
        return candidate
