"""Project lifecycle service.

Ported from the original ``services/project_service.py``. The event bus is
removed — the React query layer handles refresh via cache invalidation. Slug
uniqueness is enforced by *rejection* on collision (the original behavior),
surfaced as :class:`ConflictError`.
"""

import logging
import sqlite3
from datetime import date

from portfolio_manager.application.ports.project_repository import ProjectRepository
from portfolio_manager.domain.enums import ProjectStatus
from portfolio_manager.domain.errors import (
    ArchivedProjectError,
    ConflictError,
    ValidationError,
)
from portfolio_manager.domain.models import Project
from portfolio_manager.domain.slug import slugify

logger = logging.getLogger(__name__)


class ProjectService:
    """Coordinate project creation, updates, archival, and deletion.

    :param projects: Project repository port.
    """

    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def create_project(
        self,
        name: str,
        status: ProjectStatus = "active",
        priority: int = 3,
        description: str = "",
        started_date: date | None = None,
        end_date: date | None = None,
        owner: str = "Matt Briggs",
        review_cadence: str = "weekly",
    ) -> Project:
        """Create and persist a new project.

        :param name: Display name (required after trimming).
        :param status: Initial lifecycle status.
        :param priority: Priority 1–5.
        :param description: Optional description.
        :param started_date: Optional start date.
        :param end_date: Optional end date.
        :param owner: Project owner.
        :param review_cadence: Review cadence label.
        :returns: The persisted project.
        :rtype: Project
        :raises ValidationError: If *name* is empty or *priority* out of range.
        :raises ConflictError: If the derived slug already exists.
        """
        name = name.strip()
        if not name:
            raise ValidationError("Project name must not be empty.")
        if not 1 <= priority <= 5:
            raise ValidationError("Priority must be between 1 and 5.")

        project = Project(
            name=name,
            slug=slugify(name),
            status=status,
            priority=priority,
            description=description,
            started_date=started_date,
            end_date=end_date,
            owner=owner,
            review_cadence=review_cadence,
        )
        try:
            project = self._projects.create(project)
        except sqlite3.IntegrityError as exc:
            raise ConflictError(
                f"A project named {name!r} already exists. Choose a different name."
            ) from exc
        logger.info("Created project %d: %r", project.id, project.name)
        return project

    def update_project(self, project: Project) -> Project:
        """Persist updated project fields.

        :param project: Project with modified fields.
        :returns: The refreshed project.
        :rtype: Project
        :raises ArchivedProjectError: If the project is archived (read-only).
        :raises ConflictError: If a renamed slug collides with another project.
        """
        existing = self._projects.get(project.id)
        if existing.is_archived():
            raise ArchivedProjectError(
                f"Project {project.id!r} is archived and cannot be modified."
            )
        project.slug = slugify(project.name)
        try:
            updated = self._projects.update(project)
        except sqlite3.IntegrityError as exc:
            raise ConflictError(f"A project named {project.name!r} already exists.") from exc
        logger.info("Updated project %d: %r", updated.id, updated.name)
        return updated

    def archive_project(self, project_id: int) -> Project:
        """Move a project to ``archive`` status (read-only).

        :param project_id: Target project.
        :returns: The archived project.
        :rtype: Project
        :raises NotFoundError: If the project does not exist.
        """
        project = self._projects.get(project_id)
        project.status = "archive"
        updated = self._projects.update(project)
        logger.info("Archived project %d", project_id)
        return updated

    def delete_project(self, project_id: int) -> None:
        """Permanently delete a project and its cascaded records.

        Service authorization does not depend on renderer confirmation.

        :param project_id: Target project.
        :raises NotFoundError: If the project does not exist.
        """
        self._projects.delete(project_id)
        logger.info("Deleted project %d", project_id)

    def get_project(self, project_id: int) -> Project:
        """Fetch a project by primary key.

        :raises NotFoundError: If the project does not exist.
        :rtype: Project
        """
        return self._projects.get(project_id)

    def list_projects(self, status: ProjectStatus | None = "active") -> list[Project]:
        """Return projects filtered by lifecycle status (``None`` = all).

        :rtype: list[Project]
        """
        return self._projects.list(status=status)
