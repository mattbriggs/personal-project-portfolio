"""Project scoring policy (Strategy pattern).

Ported verbatim from the original ``services/scoring_service.py`` scoring math.
The default algorithm (SRS Appendix A):

    session_score   = (completed / planned) * 60      (0 if planned == 0)
    milestone_score = (completed_ms / total_ms) * 40  (0 if total_ms == 0)
    score           = min(100, round(session_score + milestone_score))

Status mapping:

    80–100 -> green
    60–79  -> yellow
    0–59   -> red
"""

from abc import ABC, abstractmethod

from portfolio_manager.domain.enums import ScoreStatus


class ScoringStrategy(ABC):
    """Abstract base class for pluggable scoring algorithms.

    Implement this interface to replace the default algorithm without changing
    :class:`~portfolio_manager.application.services.scoring_service.ScoringService`.
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

        :param planned: Committed sessions for the week (planned+doing+done).
        :param completed: Sessions completed this week (``done``).
        :param total_milestones: Total non-cancelled milestones for the project.
        :param completed_milestones: Milestones already completed.
        :returns: Score in range 0–100.
        :rtype: int
        """


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

        :param planned: Committed sessions (denominator).
        :param completed: Completed sessions (numerator).
        :param total_milestones: Total milestones.
        :param completed_milestones: Completed milestones.
        :returns: Integer score 0–100.
        :rtype: int
        """
        session_score = (completed / planned * 60) if planned > 0 else 0
        milestone_score = (
            (completed_milestones / total_milestones * 40) if total_milestones > 0 else 0
        )
        return min(100, round(session_score + milestone_score))


def score_to_status(score: int) -> ScoreStatus:
    """Map an integer score to a traffic-light status.

    Boundaries: ``>= 80`` green, ``>= 60`` yellow, otherwise red.

    :param score: Integer score 0–100.
    :returns: ``'green'``, ``'yellow'``, or ``'red'``.
    :rtype: ScoreStatus
    """
    if score >= 80:
        return "green"
    if score >= 60:
        return "yellow"
    return "red"
