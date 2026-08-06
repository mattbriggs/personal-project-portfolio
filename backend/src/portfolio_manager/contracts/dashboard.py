"""Dashboard aggregate HTTP contract."""

from datetime import date

from pydantic import BaseModel

from portfolio_manager.application.dto.dashboard import Dashboard
from portfolio_manager.contracts.projects import ProjectResponse
from portfolio_manager.contracts.scores import ScoreResponse
from portfolio_manager.domain.enums import ScoreStatus


class DashboardRowResponse(BaseModel):
    """Per-project dashboard row."""

    project: ProjectResponse
    score: ScoreResponse
    planned: int
    completed: int
    remaining: int


class UpcomingMilestoneResponse(BaseModel):
    """An upcoming milestone with its target date."""

    project_name: str
    description: str
    target_date: date


class DashboardResponse(BaseModel):
    """Aggregate dashboard response for a single week."""

    week_key: str
    date_range: str
    rows: list[DashboardRowResponse]
    portfolio_score: int
    portfolio_status: ScoreStatus
    week_total_minutes: int
    week_done_minutes: int
    week_remaining_minutes: int
    budget_minutes: int
    upcoming_milestones: list[UpcomingMilestoneResponse]

    @classmethod
    def from_domain(cls, d: Dashboard) -> "DashboardResponse":
        """Build a response from a :class:`Dashboard` read model.

        :rtype: DashboardResponse
        """
        return cls(
            week_key=d.week_key,
            date_range=d.date_range,
            rows=[
                DashboardRowResponse(
                    project=ProjectResponse.from_domain(r.project),
                    score=ScoreResponse.from_domain(r.score),
                    planned=r.planned,
                    completed=r.completed,
                    remaining=r.remaining,
                )
                for r in d.rows
            ],
            portfolio_score=d.portfolio_score,
            portfolio_status=d.portfolio_status,
            week_total_minutes=d.week_total_minutes,
            week_done_minutes=d.week_done_minutes,
            week_remaining_minutes=d.week_remaining_minutes,
            budget_minutes=d.budget_minutes,
            upcoming_milestones=[
                UpcomingMilestoneResponse(
                    project_name=m.project_name,
                    description=m.description,
                    target_date=m.target_date,
                )
                for m in d.upcoming_milestones
            ],
        )
