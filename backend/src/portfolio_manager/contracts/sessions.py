"""Session HTTP contracts.

``week_key`` is derived on the server and only appears in responses — clients
cannot supply it authoritatively (SRS §3.10).
"""

from datetime import date, datetime

from pydantic import BaseModel, Field

from portfolio_manager.domain.enums import SessionStatus
from portfolio_manager.domain.models import Session


class SessionCreateRequest(BaseModel):
    """Request body for creating a session."""

    project_id: int = Field(gt=0)
    milestone_id: int | None = Field(default=None, gt=0)
    scheduled_date: date
    duration_minutes: int | None = Field(default=None, ge=15, le=480)
    status: SessionStatus = "backlog"
    description: str = ""
    notes: str = ""


class SessionUpdateRequest(BaseModel):
    """Request body for updating an existing session."""

    project_id: int = Field(gt=0)
    milestone_id: int | None = Field(default=None, gt=0)
    scheduled_date: date
    duration_minutes: int = Field(ge=15, le=480)
    status: SessionStatus
    description: str = ""
    notes: str = ""


class SessionStatusRequest(BaseModel):
    """Request body for a session status transition."""

    status: SessionStatus


class SessionRescheduleRequest(BaseModel):
    """Request body for rescheduling a session."""

    scheduled_date: date


class SessionResponse(BaseModel):
    """Session response body."""

    id: int
    project_id: int
    milestone_id: int | None
    scheduled_date: date
    week_key: str
    duration_minutes: int
    status: SessionStatus
    description: str
    notes: str
    created_at: datetime
    completed_at: datetime | None

    @classmethod
    def from_domain(cls, s: Session) -> "SessionResponse":
        """Build a response from a domain :class:`Session`.

        :rtype: SessionResponse
        """
        return cls(
            id=s.id,
            project_id=s.project_id,
            milestone_id=s.milestone_id,
            scheduled_date=s.scheduled_date,
            week_key=s.week_key,
            duration_minutes=s.duration_minutes,
            status=s.status,
            description=s.description,
            notes=s.notes,
            created_at=s.created_at,
            completed_at=s.completed_at,
        )


class SessionListResponse(BaseModel):
    """List of sessions."""

    sessions: list[SessionResponse]
