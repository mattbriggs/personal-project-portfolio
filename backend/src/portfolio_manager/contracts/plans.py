"""Plan document HTTP contracts."""

from pydantic import BaseModel


class PlanResponse(BaseModel):
    """Raw Markdown plan content for a project.

    :param project_id: Owning project.
    :param content: Markdown text (may be empty).
    """

    project_id: int
    content: str


class PlanSaveRequest(BaseModel):
    """Request body for saving plan content.

    :param content: New Markdown text.
    """

    content: str
