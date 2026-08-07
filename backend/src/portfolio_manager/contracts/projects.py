"""Project HTTP contracts."""

from datetime import date, datetime

from pydantic import BaseModel, Field

from portfolio_manager.domain.enums import ProjectStatus
from portfolio_manager.domain.models import Project


class ProjectCreateRequest(BaseModel):
    """Request body for creating a project."""

    name: str = Field(min_length=1)
    status: ProjectStatus = "active"
    priority: int = Field(default=3, ge=1, le=5)
    description: str = ""
    started_date: date | None = None
    end_date: date | None = None
    owner: str = "Matt Briggs"
    review_cadence: str = "weekly"


class ProjectUpdateRequest(BaseModel):
    """Request body for updating a project (full replacement of editable fields)."""

    name: str = Field(min_length=1)
    status: ProjectStatus
    priority: int = Field(ge=1, le=5)
    description: str = ""
    started_date: date | None = None
    end_date: date | None = None
    owner: str = "Matt Briggs"
    review_cadence: str = "weekly"


class ProjectResponse(BaseModel):
    """Project response body."""

    id: int
    name: str
    slug: str
    status: ProjectStatus
    priority: int
    started_date: date | None
    end_date: date | None
    owner: str
    review_cadence: str
    description: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, p: Project) -> "ProjectResponse":
        """Build a response from a domain :class:`Project`.

        :rtype: ProjectResponse
        """
        return cls(
            id=p.id,
            name=p.name,
            slug=p.slug,
            status=p.status,
            priority=p.priority,
            started_date=p.started_date,
            end_date=p.end_date,
            owner=p.owner,
            review_cadence=p.review_cadence,
            description=p.description,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )


class ProjectListResponse(BaseModel):
    """List of projects."""

    projects: list[ProjectResponse]
