"""Repository for Project entities."""

import sqlite3
from datetime import date, datetime

from portfolio_manager.db.connection import DatabaseConnection
from portfolio_manager.exceptions import NotFoundError
from portfolio_manager.models.project import Project, ProjectStatus
from portfolio_manager.repositories.base import BaseRepository


def _row_to_project(row: sqlite3.Row) -> Project:
    """Convert a :class:`sqlite3.Row` to a :class:`Project` domain object.

    :param row: A row from the ``project`` table.
    :rtype: Project
    """
    return Project(
        id=row["id"],
        name=row["name"],
        slug=row["slug"],
        status=row["status"],
        priority=row["priority"],
        started_date=(
            date.fromisoformat(row["started_date"]) if row["started_date"] else None
        ),
        owner=row["owner"],
        review_cadence=row["review_cadence"],
        plan_content=row["plan_content"],
        description=row["description"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class ProjectRepository(BaseRepository):
    """CRUD and query operations for :class:`~portfolio_manager.models.project.Project`.

    :param db: Shared database connection.
    :type db: DatabaseConnection
    """

    def __init__(self, db: DatabaseConnection) -> None:
        super().__init__(db)

    def create(self, project: Project) -> Project:
        """Insert a new project and return it with the assigned ``id``.

        :param project: Unsaved project (``id`` will be 0 or ignored).
        :type project: Project
        :returns: The same project with ``id`` populated.
        :rtype: Project
        """
        with self.transaction():
            cur = self._db.execute(
                """
                INSERT INTO project
                    (name, slug, status, priority, started_date, owner,
                     review_cadence, plan_content, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.name,
                    project.slug,
                    project.status,
                    project.priority,
                    project.started_date.isoformat() if project.started_date else None,
                    project.owner,
                    project.review_cadence,
                    project.plan_content,
                    project.description,
                ),
            )
            project.id = cur.lastrowid or 0
        return project

    def get(self, project_id: int) -> Project:
        """Fetch a project by primary key.

        :param project_id: The project's primary key.
        :type project_id: int
        :returns: The matching :class:`Project`.
        :rtype: Project
        :raises NotFoundError: If no project with *project_id* exists.
        """
        row = self._db.fetchone("SELECT * FROM project WHERE id = ?", (project_id,))
        if row is None:
            raise NotFoundError("Project", project_id)
        return _row_to_project(row)

    def list(
        self,
        status: ProjectStatus | None = None,
    ) -> list[Project]:
        """Return projects, optionally filtered by lifecycle status.

        Results are ordered by priority ascending, then name ascending.

        :param status: Filter by ``active``, ``backlog``, or ``archive``.
            Pass ``None`` to return all projects.
        :type status: str | None
        :returns: List of :class:`Project` objects.
        :rtype: list[Project]
        """
        if status:
            rows = self._db.fetchall(
                "SELECT * FROM project WHERE status = ? ORDER BY priority, name",
                (status,),
            )
        else:
            rows = self._db.fetchall("SELECT * FROM project ORDER BY priority, name")
        return [_row_to_project(r) for r in rows]

    def update(self, project: Project) -> Project:
        """Persist changes to an existing project.

        The ``updated_at`` column is refreshed by a database trigger.

        :param project: Project with updated fields.
        :type project: Project
        :returns: The updated :class:`Project`.
        :rtype: Project
        :raises NotFoundError: If the project does not exist.
        """
        with self.transaction():
            self._db.execute(
                """
                UPDATE project SET
                    name = ?, slug = ?, status = ?, priority = ?,
                    started_date = ?, owner = ?, review_cadence = ?,
                    plan_content = ?, description = ?
                WHERE id = ?
                """,
                (
                    project.name,
                    project.slug,
                    project.status,
                    project.priority,
                    project.started_date.isoformat() if project.started_date else None,
                    project.owner,
                    project.review_cadence,
                    project.plan_content,
                    project.description,
                    project.id,
                ),
            )
        return self.get(project.id)

    def update_plan(self, project_id: int, plan_content: str) -> None:
        """Update only the ``plan_content`` field for a project.

        This triggers the ``project_updated_at`` database trigger, which
        updates ``updated_at`` automatically.

        :param project_id: Target project's primary key.
        :type project_id: int
        :param plan_content: New Markdown plan content.
        :type plan_content: str
        """
        with self.transaction():
            self._db.execute(
                "UPDATE project SET plan_content = ? WHERE id = ?",
                (plan_content, project_id),
            )

    def delete(self, project_id: int) -> None:
        """Delete a project and cascade-delete its sessions and milestones.

        :param project_id: Primary key of the project to delete.
        :type project_id: int
        :raises NotFoundError: If the project does not exist.
        """
        self.get(project_id)  # validates existence
        with self.transaction():
            self._db.execute("DELETE FROM project WHERE id = ?", (project_id,))
