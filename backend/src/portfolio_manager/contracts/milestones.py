"""Milestone HTTP contracts."""

from datetime import date, datetime

from pydantic import BaseModel, Field

from portfolio_manager.domain.enums import MilestoneStatus
from portfolio_manager.domain.models import Milestone


class MilestoneCreateRequest(BaseModel):
    """Request body for creating a milestone."""

    project_id: int = Field(gt=0)
    description: str = Field(min_length=1)
    status: MilestoneStatus = "backlog"
    target_date: date | None = None
    sort_order: int = 0
    notes: str = ""


class MilestoneUpdateRequest(BaseModel):
    """Request body for updating a milestone."""

    description: str = Field(min_length=1)
    status: MilestoneStatus
    target_date: date | None = None
    sort_order: int = 0
    notes: str = ""


class MilestoneStatusRequest(BaseModel):
    """Request body for a milestone status transition."""

    status: MilestoneStatus


class MilestoneResponse(BaseModel):
    """Milestone response body, including associated session minutes."""

    id: int
    project_id: int
    description: str
    status: MilestoneStatus
    completed_date: date | None
    target_date: date | None
    sort_order: int
    notes: str
    total_session_minutes: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, m: Milestone, total_minutes: int = 0) -> "MilestoneResponse":
        """Build a response from a domain :class:`Milestone`.

        :param m: The milestone.
        :param total_minutes: Associated session-minute total.
        :rtype: MilestoneResponse
        """
        return cls(
            id=m.id,
            project_id=m.project_id,
            description=m.description,
            status=m.status,
            completed_date=m.completed_date,
            target_date=m.target_date,
            sort_order=m.sort_order,
            notes=m.notes,
            total_session_minutes=total_minutes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class MilestoneListResponse(BaseModel):
    """List of milestones."""

    milestones: list[MilestoneResponse]
