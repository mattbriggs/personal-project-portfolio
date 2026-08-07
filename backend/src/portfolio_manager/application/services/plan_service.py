"""Plan document service.

Stores and retrieves per-project Markdown plan content. Unlike the original
Tkinter ``PlanService``, rendering (Markdown + Mermaid) happens in the React
renderer with bundled, offline libraries — the backend only persists raw text.
See ADR-011 for the frontend-only rendering decision.
"""

import logging

from portfolio_manager.application.ports.project_repository import ProjectRepository

logger = logging.getLogger(__name__)


class PlanService:
    """Read and write a project's Markdown plan document.

    :param projects: Project repository port.
    """

    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def get_plan(self, project_id: int) -> str:
        """Return the raw Markdown plan content for a project.

        :param project_id: Target project.
        :returns: Markdown text (may be empty).
        :rtype: str
        :raises NotFoundError: If the project does not exist.
        """
        return self._projects.get(project_id).plan_content

    def save_plan(self, project_id: int, content: str) -> None:
        """Persist updated plan Markdown.

        :param project_id: Target project.
        :param content: New Markdown text.
        :raises NotFoundError: If the project does not exist.
        """
        self._projects.get(project_id)  # validate existence
        self._projects.update_plan(project_id, content)
        logger.debug("Saved plan for project %d (%d chars)", project_id, len(content))
