"""SQLite repository for :class:`Project`.

Implements :class:`portfolio_manager.application.ports.project_repository.ProjectRepository`.
Ported from the original ``repositories/project_repo.py``; the SQL is unchanged
so behavior against existing databases is preserved.
"""

from portfolio_manager.domain.enums import ProjectStatus
from portfolio_manager.domain.errors import NotFoundError
from portfolio_manager.domain.models import Project
from portfolio_manager.infrastructure.db.connection import DatabaseConnection
from portfolio_manager.infrastructure.db.row_mapping import row_to_project


class SqliteProjectRepository:
    """CRUD and query operations for projects.

    :param db: Shared database connection.
    """

    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def create(self, project: Project) -> Project:
        """Insert a project and return it with its assigned ``id``.

        :param project: Unsaved project.
        :returns: The project with ``id`` populated.
        :rtype: Project
        :raises sqlite3.IntegrityError: On duplicate slug (translated by the
            service layer to a conflict).
        """
        with self._db.transaction():
            cur = self._db.execute(
                """
                INSERT INTO project
                    (name, slug, status, priority, started_date, end_date, owner,
                     review_cadence, plan_content, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project.name,
                    project.slug,
                    project.status,
                    project.priority,
                    project.started_date.isoformat() if project.started_date else None,
                    project.end_date.isoformat() if project.end_date else None,
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

        :raises NotFoundError: If the project does not exist.
        :rtype: Project
        """
        row = self._db.fetchone("SELECT * FROM project WHERE id = ?", (project_id,))
        if row is None:
            raise NotFoundError("Project", project_id)
        return row_to_project(row)

    def get_by_slug(self, slug: str) -> Project | None:
        """Return the project with *slug*, or ``None``.

        :rtype: Project | None
        """
        row = self._db.fetchone("SELECT * FROM project WHERE slug = ?", (slug,))
        return row_to_project(row) if row else None

    def list(self, status: ProjectStatus | None = None) -> list[Project]:
        """Return projects ordered by priority, then name.

        :param status: Optional lifecycle-status filter; ``None`` returns all.
        :rtype: list[Project]
        """
        if status:
            rows = self._db.fetchall(
                "SELECT * FROM project WHERE status = ? ORDER BY priority, name",
                (status,),
            )
        else:
            rows = self._db.fetchall("SELECT * FROM project ORDER BY priority, name")
        return [row_to_project(r) for r in rows]

    def update(self, project: Project) -> Project:
        """Persist changes to an existing project.

        :raises NotFoundError: If the project does not exist.
        :rtype: Project
        """
        with self._db.transaction():
            self._db.execute(
                """
                UPDATE project SET
                    name = ?, slug = ?, status = ?, priority = ?,
                    started_date = ?, end_date = ?, owner = ?, review_cadence = ?,
                    plan_content = ?, description = ?
                WHERE id = ?
                """,
                (
                    project.name,
                    project.slug,
                    project.status,
                    project.priority,
                    project.started_date.isoformat() if project.started_date else None,
                    project.end_date.isoformat() if project.end_date else None,
                    project.owner,
                    project.review_cadence,
                    project.plan_content,
                    project.description,
                    project.id,
                ),
            )
        return self.get(project.id)

    def update_plan(self, project_id: int, plan_content: str) -> None:
        """Update only the ``plan_content`` field.

        :param project_id: Target project.
        :param plan_content: New Markdown plan content.
        """
        with self._db.transaction():
            self._db.execute(
                "UPDATE project SET plan_content = ? WHERE id = ?",
                (plan_content, project_id),
            )

    def delete(self, project_id: int) -> None:
        """Delete a project (cascades to sessions, milestones, scores).

        :raises NotFoundError: If the project does not exist.
        """
        self.get(project_id)
        with self._db.transaction():
            self._db.execute("DELETE FROM project WHERE id = ?", (project_id,))
