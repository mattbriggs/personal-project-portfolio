"""Score HTTP contracts."""

from datetime import datetime

from pydantic import BaseModel, Field

from portfolio_manager.domain.enums import ScoreStatus
from portfolio_manager.domain.models import ProjectScore


class ScoreOverrideRequest(BaseModel):
    """Request body for a manual score override.

    ``reason`` is required and non-empty (SRS §3.10 Score).
    """

    project_id: int = Field(gt=0)
    week_key: str
    score: int = Field(ge=0, le=100)
    status: ScoreStatus
    reason: str = Field(min_length=1)
    status_note: str = ""


class ScoreResponse(BaseModel):
    """Project score response body."""

    id: int
    project_id: int
    week_key: str
    score: int
    status: ScoreStatus
    status_note: str
    is_manual_override: bool
    override_reason: str
    created_at: datetime | None

    @classmethod
    def from_domain(cls, s: ProjectScore) -> "ScoreResponse":
        """Build a response from a domain :class:`ProjectScore`.

        :rtype: ScoreResponse
        """
        return cls(
            id=s.id,
            project_id=s.project_id,
            week_key=s.week_key,
            score=s.score,
            status=s.status,
            status_note=s.status_note,
            is_manual_override=s.is_manual_override,
            override_reason=s.override_reason,
            created_at=s.created_at,
        )
