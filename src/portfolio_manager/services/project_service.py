"""Business logic for project lifecycle management."""

import logging
import re

from portfolio_manager.events.event_bus import (
    PROJECT_CREATED,
    PROJECT_DELETED,
    PROJECT_UPDATED,
    EventBus,
)
from portfolio_manager.exceptions import ProjectStateError, ValidationError
from portfolio_manager.models.project import Project, ProjectStatus
from portfolio_manager.repositories.project_repo import ProjectRepository

logger = logging.getLogger(__name__)


def _slugify(name: str) -> str:
    """Convert a project name to a URL-safe slug.

    :param name: Human-readable project name.
    :type name: str
    :returns: Lowercase slug with hyphens instead of whitespace/punctuation.
    :rtype: str
    """
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    return slug


class ProjectService:
    """Manages the project lifecycle: create, update, archive, delete.

    :param project_repo: Repository for project persistence.
    :type project_repo: ProjectRepository
    :param bus: Event bus for notifying subscribers of state changes.
    :type bus: EventBus
    """

    def __init__(
        self,
        project_repo: ProjectRepository,
        bus: EventBus | None = None,
    ) -> None:
        self._projects = project_repo
        self._bus = bus or EventBus.get()

    def create_project(
        self,
        name: str,
        status: ProjectStatus = "active",
        priority: int = 3,
        description: str = "",
        **kwargs: object,
    ) -> Project:
        """Create and persist a new project.

        :param name: Project display name (must be non-empty).
        :type name: str
        :param status: Initial lifecycle status.
        :type status: ProjectStatus
        :param priority: Priority 1–5 (default 3).
        :type priority: int
        :param description: Optional free-text description.
        :type description: str
        :param kwargs: Additional :class:`~portfolio_manager.models.project.Project`
            field overrides (``started_date``, ``owner``, etc.).
        :returns: The persisted :class:`~portfolio_manager.models.project.Project`.
        :rtype: Project
        :raises ValidationError: If *name* is empty or *priority* is out of range.
        """
        name = name.strip()
        if not name:
            raise ValidationError("Project name must not be empty.")
        if not 1 <= priority <= 5:
            raise ValidationError("Priority must be between 1 and 5.")

        project = Project(
            name=name,
            slug=_slugify(name),
            status=status,
            priority=priority,
            description=description,
            **kwargs,  # type: ignore[arg-type]
        )
        project = self._projects.create(project)
        self._bus.emit(PROJECT_CREATED, project_id=project.id)
        logger.info("Created project %d: %r", project.id, project.name)
        return project

    def update_project(self, project: Project) -> Project:
        """Persist updated project fields.

        :param project: Project domain object with modified fields.
        :type project: Project
        :returns: The refreshed :class:`~portfolio_manager.models.project.Project`.
        :rtype: Project
        :raises ProjectStateError: If the project is archived (read-only).
        """
        existing = self._projects.get(project.id)
        if existing.is_archived():
            raise ProjectStateError(
                f"Project {project.id!r} is archived and cannot be modified."
            )
        updated = self._projects.update(project)
        self._bus.emit(PROJECT_UPDATED, project_id=updated.id)
        logger.info("Updated project %d: %r", updated.id, updated.name)
        return updated

    def archive_project(self, project_id: int) -> Project:
        """Move a project to ``archive`` status (makes it read-only).

        :param project_id: Target project.
        :type project_id: int
        :returns: The archived project.
        :rtype: Project
        """
        project = self._projects.get(project_id)
        project.status = "archive"
        updated = self._projects.update(project)
        self._bus.emit(PROJECT_UPDATED, project_id=project_id)
        logger.info("Archived project %d", project_id)
        return updated

    def delete_project(self, project_id: int) -> None:
        """Delete a project and all its associated data.

        :param project_id: Primary key of the project to delete.
        :type project_id: int
        """
        self._projects.delete(project_id)
        self._bus.emit(PROJECT_DELETED, project_id=project_id)
        logger.info("Deleted project %d", project_id)

    def get_project(self, project_id: int) -> Project:
        """Fetch a project by primary key.

        :param project_id: Target project.
        :type project_id: int
        :rtype: Project
        """
        return self._projects.get(project_id)

    def list_projects(self, status: ProjectStatus | None = "active") -> list[Project]:
        """Return projects filtered by lifecycle status.

        :param status: Filter value — pass ``None`` for all projects.
        :type status: str | None
        :rtype: list[Project]
        """
        return self._projects.list(status=status)
