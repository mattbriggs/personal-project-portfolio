"""Weekly review HTTP contracts."""

from datetime import date, datetime

from pydantic import BaseModel, Field

from portfolio_manager.domain.models import WeeklyReview


class ReviewSaveRequest(BaseModel):
    """Request body for saving a weekly review.

    ``week_key`` comes from the path; the date range is derived server-side.
    """

    hours_invested: float = Field(default=0.0, ge=0)
    sessions_completed: int = Field(default=0, ge=0)
    what_moved: str = ""
    what_stalled: str = ""
    signals: str = ""
    decision_next_week: str = ""
    primary_focus: str = ""
    project_to_deprioritize: str = ""
    risk_to_watch: str = ""
    first_session_target: str = ""
    written_to_repo: bool = False


class ReviewResponse(BaseModel):
    """Weekly review response body."""

    id: int
    week_key: str
    date_from: date | None
    date_to: date | None
    hours_invested: float
    sessions_completed: int
    what_moved: str
    what_stalled: str
    signals: str
    decision_next_week: str
    primary_focus: str
    project_to_deprioritize: str
    risk_to_watch: str
    first_session_target: str
    written_to_repo: bool
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_domain(cls, r: WeeklyReview) -> "ReviewResponse":
        """Build a response from a domain :class:`WeeklyReview`.

        :rtype: ReviewResponse
        """
        return cls(
            id=r.id,
            week_key=r.week_key,
            date_from=r.date_from,
            date_to=r.date_to,
            hours_invested=r.hours_invested,
            sessions_completed=r.sessions_completed,
            what_moved=r.what_moved,
            what_stalled=r.what_stalled,
            signals=r.signals,
            decision_next_week=r.decision_next_week,
            primary_focus=r.primary_focus,
            project_to_deprioritize=r.project_to_deprioritize,
            risk_to_watch=r.risk_to_watch,
            first_session_target=r.first_session_target,
            written_to_repo=r.written_to_repo,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )


class ReviewListResponse(BaseModel):
    """List of weekly reviews, most recent first."""

    reviews: list[ReviewResponse]
