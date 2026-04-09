"""Scoring service implementing the Strategy design pattern.

The :class:`ScoringService` delegates computation to a :class:`ScoringStrategy`
implementation.  Swap the strategy by passing a different implementation at
construction time — no callers need to change.

Default algorithm (see Appendix A of the SRS):

    session_score    = (completed / planned) * 60      (0 if planned == 0)
    milestone_score  = (completed_ms / total_ms) * 40  (0 if total == 0)
    score            = min(100, round(session_score + milestone_score))

Status mapping:

    80–100 → green
    60–79  → yellow
    0–59   → red
"""

import logging
from abc import ABC, abstractmethod

from portfolio_manager.models.score import ProjectScore, ScoreStatus
from portfolio_manager.repositories.milestone_repo import MilestoneRepository
from portfolio_manager.repositories.score_repo import ScoreRepository
from portfolio_manager.repositories.session_repo import SessionRepository

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Strategy ABC
# ---------------------------------------------------------------------------


class ScoringStrategy(ABC):
    """Abstract base class for pluggable scoring algorithms.

    Implement this interface to replace the default scoring algorithm.
    """

    @abstractmethod
    def compute_score(
        self,
        planned: int,
        completed: int,
        total_milestones: int,
        completed_milestones: int,
    ) -> int:
        """Compute an integer project score in the range 0–100.

        :param planned: Sessions planned for the week.
        :param completed: Sessions completed this week.
        :param total_milestones: Total milestones for the project.
        :param completed_milestones: Milestones already completed.
        :returns: Score in range 0–100.
        :rtype: int
        """


# ---------------------------------------------------------------------------
# Default strategy
# ---------------------------------------------------------------------------


class DefaultScoringStrategy(ScoringStrategy):
    """Default weighted scoring: 60% session completion + 40% milestone ratio."""

    def compute_score(
        self,
        planned: int,
        completed: int,
        total_milestones: int,
        completed_milestones: int,
    ) -> int:
        """Compute score using the default weighted algorithm.

        :param planned: Sessions planned this week (denominator).
        :param completed: Sessions completed this week (numerator).
        :param total_milestones: Total project milestones.
        :param completed_milestones: Completed milestones.
        :returns: Integer score 0–100.
        :rtype: int
        """
        session_score = (completed / planned * 60) if planned > 0 else 0
        milestone_score = (
            (completed_milestones / total_milestones * 40)
            if total_milestones > 0
            else 0
        )
        return min(100, round(session_score + milestone_score))


# ---------------------------------------------------------------------------
# Score → status mapping
# ---------------------------------------------------------------------------


def score_to_status(score: int) -> ScoreStatus:
    """Map an integer score to a traffic-light status string.

    :param score: Integer score 0–100.
    :type score: int
    :returns: ``'green'``, ``'yellow'``, or ``'red'``.
    :rtype: ScoreStatus
    """
    if score >= 80:
        return "green"
    if score >= 60:
        return "yellow"
    return "red"


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class ScoringService:
    """Computes and persists project scores for a given week.

    :param session_repo: Repository used to retrieve session counts.
    :param milestone_repo: Repository used to retrieve milestone counts.
    :param score_repo: Repository used to persist computed scores.
    :param strategy: Scoring algorithm implementation.  Defaults to
        :class:`DefaultScoringStrategy`.
    """

    def __init__(
        self,
        session_repo: SessionRepository,
        milestone_repo: MilestoneRepository,
        score_repo: ScoreRepository,
        strategy: ScoringStrategy | None = None,
    ) -> None:
        self._sessions = session_repo
        self._milestones = milestone_repo
        self._scores = score_repo
        self._strategy: ScoringStrategy = strategy or DefaultScoringStrategy()

    def compute_and_save(
        self,
        project_id: int,
        week_key: str,
    ) -> ProjectScore:
        """Compute the score for a project in a given week and persist it.

        Skips computation if a manual override exists for this
        ``(project_id, week_key)`` pair.

        :param project_id: Target project.
        :type project_id: int
        :param week_key: Target week in ``YYYY.W`` format.
        :type week_key: str
        :returns: The persisted :class:`~portfolio_manager.models.score.ProjectScore`.
        :rtype: ProjectScore
        """
        existing = self._scores.get_for_week(project_id, week_key)
        if existing and existing.is_manual_override:
            logger.debug(
                "Skipping recompute for project %d week %s — manual override active.",
                project_id,
                week_key,
            )
            return existing

        counts = self._sessions.count_by_status(project_id, week_key)
        # planned = all committed (non-backlog, non-cancelled) sessions
        planned = (
            counts.get("planned", 0)
            + counts.get("doing", 0)
            + counts.get("done", 0)
        )
        completed = counts.get("done", 0)
        total_ms, completed_ms = self._milestones.count(project_id)

        score_value = self._strategy.compute_score(
            planned, completed, total_ms, completed_ms
        )
        status = score_to_status(score_value)

        ps = ProjectScore(
            project_id=project_id,
            week_key=week_key,
            score=score_value,
            status=status,
            status_note="",
            is_manual_override=False,
            override_reason="",
        )
        return self._scores.upsert(ps)

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
        :param status: Override status.
        :param reason: Required explanation for the override.
        :param status_note: Optional display note.
        :returns: The saved :class:`~portfolio_manager.models.score.ProjectScore`.
        :rtype: ProjectScore
        """
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
        """Return the average score across all project scores for a given week.

        Returns 0 if no scores exist for the week.

        :param week_key: Target week.
        :type week_key: str
        :returns: Average score rounded to the nearest integer.
        :rtype: int
        """
        scores = self._scores.list_for_week(week_key)
        if not scores:
            return 0
        return round(sum(s.score for s in scores) / len(scores))
