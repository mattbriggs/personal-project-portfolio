"""Controller for the project management view."""

import logging
from typing import Any

from portfolio_manager.models.project import Project, ProjectStatus
from portfolio_manager.services.plan_service import PlanService
from portfolio_manager.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class ProjectController:
    """Mediates between the project view and project/plan services.

    :param project_service: Service for project lifecycle operations.
    :param plan_service: Service for plan document rendering and persistence.
    """

    def __init__(
        self,
        project_service: ProjectService,
        plan_service: PlanService,
    ) -> None:
        self._projects = project_service
        self._plans = plan_service

    def list_projects(self, status: ProjectStatus | None = "active") -> list[Project]:
        """Return projects filtered by status.

        :param status: Lifecycle status filter; ``None`` returns all.
        :rtype: list[Project]
        """
        return self._projects.list_projects(status=status)

    def get_project(self, project_id: int) -> Project:
        """Fetch a single project.

        :param project_id: Target project's primary key.
        :rtype: Project
        """
        return self._projects.get_project(project_id)

    def create_project(self, name: str, **kwargs: Any) -> Project:
        """Create a new project.

        :param name: Project name (required).
        :param kwargs: Optional field overrides forwarded to the service.
        :returns: The created :class:`~portfolio_manager.models.project.Project`.
        :rtype: Project
        :raises ValidationError: If inputs are invalid.
        """
        return self._projects.create_project(name, **kwargs)

    def update_project(self, project: Project) -> Project:
        """Persist changes to a project.

        :param project: Modified project domain object.
        :rtype: Project
        """
        return self._projects.update_project(project)

    def archive_project(self, project_id: int) -> Project:
        """Archive a project.

        :param project_id: Target project.
        :rtype: Project
        """
        return self._projects.archive_project(project_id)

    def delete_project(self, project_id: int) -> None:
        """Delete a project and its associated data.

        :param project_id: Target project.
        """
        self._projects.delete_project(project_id)

    def save_plan(self, project_id: int, content: str) -> None:
        """Persist plan Markdown for a project.

        :param project_id: Target project.
        :param content: Markdown text.
        """
        self._plans.save_plan(project_id, content)

    def render_plan(self, markdown_text: str) -> str:
        """Render Markdown to a full HTML page for the preview pane.

        :param markdown_text: Raw Markdown.
        :returns: HTML document string.
        :rtype: str
        """
        return self._plans.render_html(markdown_text)
