"""Dashboard read-model DTOs assembled by :class:`DashboardService`."""

from dataclasses import dataclass, field
from datetime import date

from portfolio_manager.domain.enums import ScoreStatus
from portfolio_manager.domain.models import Project, ProjectScore


@dataclass
class DashboardProjectRow:
    """Per-project dashboard row.

    :param project: The active project.
    :param score: The project's score for the week.
    :param planned: Committed session count (planned+doing+done).
    :param completed: Completed (``done``) session count.
    :param remaining: ``planned - completed``.
    """

    project: Project
    score: ProjectScore
    planned: int
    completed: int
    remaining: int


@dataclass
class UpcomingMilestone:
    """An upcoming (non-done, non-cancelled) milestone with a target date.

    :param project_name: Owning project name.
    :param description: Milestone description.
    :param target_date: The milestone's target date.
    """

    project_name: str
    description: str
    target_date: date


@dataclass
class Dashboard:
    """Aggregate dashboard read model for one week.

    :param week_key: The reported ISO week key.
    :param date_range: Human-readable date range.
    :param rows: Per-project rows for active projects.
    :param portfolio_score: Rounded average of active-project scores.
    :param portfolio_status: Traffic-light status for the portfolio score.
    :param week_total_minutes: Non-cancelled session minutes across projects.
    :param week_done_minutes: Completed session minutes across projects.
    :param budget_minutes: Configured weekly budget in minutes.
    :param upcoming_milestones: Upcoming milestones ordered by target date.
    """

    week_key: str
    date_range: str
    rows: list[DashboardProjectRow] = field(default_factory=list)
    portfolio_score: int = 0
    portfolio_status: ScoreStatus = "red"
    week_total_minutes: int = 0
    week_done_minutes: int = 0
    budget_minutes: int = 0
    upcoming_milestones: list[UpcomingMilestone] = field(default_factory=list)

    @property
    def week_remaining_minutes(self) -> int:
        """Planned-but-not-done session minutes for the week.

        :rtype: int
        """
        return self.week_total_minutes - self.week_done_minutes
