"""Scoring service.

Ported from the original ``services/scoring_service.py``. Computation is
delegated to a :class:`ScoringStrategy`; a manual override is never replaced by
automatic recomputation. Portfolio score is the rounded average of a week's
project scores, or 0 when none exist (preserving current behavior).
"""

import logging

from portfolio_manager.application.ports.milestone_repository import MilestoneRepository
from portfolio_manager.application.ports.score_repository import ScoreRepository
from portfolio_manager.application.ports.session_repository import SessionRepository
from portfolio_manager.domain.enums import ScoreStatus
from portfolio_manager.domain.errors import ValidationError
from portfolio_manager.domain.models import ProjectScore
from portfolio_manager.domain.scoring import (
    DefaultScoringStrategy,
    ScoringStrategy,
    score_to_status,
)

logger = logging.getLogger(__name__)


class ScoringService:
    """Compute and persist project scores for a given week.

    :param sessions: Session repository port (session counts).
    :param milestones: Milestone repository port (milestone counts).
    :param scores: Score repository port (persistence).
    :param strategy: Scoring algorithm. Defaults to :class:`DefaultScoringStrategy`.
    """

    def __init__(
        self,
        sessions: SessionRepository,
        milestones: MilestoneRepository,
        scores: ScoreRepository,
        strategy: ScoringStrategy | None = None,
    ) -> None:
        self._sessions = sessions
        self._milestones = milestones
        self._scores = scores
        self._strategy: ScoringStrategy = strategy or DefaultScoringStrategy()

    def compute_and_save(self, project_id: int, week_key: str) -> ProjectScore:
        """Compute and persist a project's score for a week.

        Skips recomputation when a manual override is active.

        :param project_id: Target project.
        :param week_key: Target week (``YYYY.W``).
        :returns: The persisted score.
        :rtype: ProjectScore
        """
        existing = self._scores.get_for_week(project_id, week_key)
        if existing and existing.is_manual_override:
            logger.debug(
                "Skipping recompute for project %d week %s (manual override).",
                project_id,
                week_key,
            )
            return existing

        counts = self._sessions.count_by_status(project_id, week_key)
        planned = counts.get("planned", 0) + counts.get("doing", 0) + counts.get("done", 0)
        completed = counts.get("done", 0)
        total_ms, completed_ms = self._milestones.count(project_id)

        value = self._strategy.compute_score(planned, completed, total_ms, completed_ms)
        score = ProjectScore(
            project_id=project_id,
            week_key=week_key,
            score=value,
            status=score_to_status(value),
            is_manual_override=False,
        )
        return self._scores.upsert(score)

    def manual_override(
        self,
        project_id: int,
        week_key: str,
        score: int,
        status: ScoreStatus,
        reason: str,
        status_note: str = "",
    ) -> ProjectScore:
        """Persist a user-supplied manual score override.

        :param project_id: Target project.
        :param week_key: Target week.
        :param score: Override score (0–100).
        :param status: Override traffic-light status.
        :param reason: Required non-empty explanation.
        :param status_note: Optional display note.
        :returns: The saved score.
        :rtype: ProjectScore
        :raises ValidationError: If *reason* is empty or *score* is out of range.
        """
        if not reason.strip():
            raise ValidationError("A manual score override requires a reason.")
        if not 0 <= score <= 100:
            raise ValidationError("Score must be between 0 and 100.")
        ps = ProjectScore(
            project_id=project_id,
            week_key=week_key,
            score=score,
            status=status,
            status_note=status_note,
            is_manual_override=True,
            override_reason=reason,
        )
        return self._scores.upsert(ps)

    def portfolio_score(self, week_key: str) -> int:
        """Return the rounded average of a week's project scores (0 if none).

        :param week_key: Target week.
        :rtype: int
        """
        scores = self._scores.list_for_week(week_key)
        if not scores:
            return 0
        return round(sum(s.score for s in scores) / len(scores))
