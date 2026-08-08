"""SQLite repository for :class:`Milestone`.

Implements :class:`portfolio_manager.application.ports.milestone_repository.MilestoneRepository`.
Ported from the original ``repositories/milestone_repo.py``.
"""

from portfolio_manager.domain.errors import NotFoundError
from portfolio_manager.domain.models import Milestone
from portfolio_manager.infrastructure.db.connection import DatabaseConnection
from portfolio_manager.infrastructure.db.row_mapping import row_to_milestone


class SqliteMilestoneRepository:
    """CRUD and query operations for milestones.

    :param db: Shared database connection.
    """

    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def create(self, milestone: Milestone) -> Milestone:
        """Insert a milestone and return it with its assigned ``id``.

        :rtype: Milestone
        """
        with self._db.transaction():
            cur = self._db.execute(
                """
                INSERT INTO milestone
                    (project_id, description, status, completed_date, target_date,
                     sort_order, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    milestone.project_id,
                    milestone.description,
                    milestone.status,
                    milestone.completed_date.isoformat() if milestone.completed_date else None,
                    milestone.target_date.isoformat() if milestone.target_date else None,
                    milestone.sort_order,
                    milestone.notes,
                ),
            )
            milestone.id = cur.lastrowid or 0
        return milestone

    def get(self, milestone_id: int) -> Milestone:
        """Fetch a milestone by primary key.

        :raises NotFoundError: If the milestone does not exist.
        :rtype: Milestone
        """
        row = self._db.fetchone("SELECT * FROM milestone WHERE id = ?", (milestone_id,))
        if row is None:
            raise NotFoundError("Milestone", milestone_id)
        return row_to_milestone(row)

    def list_for_project(self, project_id: int) -> list[Milestone]:
        """Return milestones for a project, ordered by ``sort_order`` then ``id``.

        :rtype: list[Milestone]
        """
        rows = self._db.fetchall(
            "SELECT * FROM milestone WHERE project_id = ? ORDER BY sort_order, id",
            (project_id,),
        )
        return [row_to_milestone(r) for r in rows]

    def list_for_project_with_totals(self, project_id: int) -> list[tuple[Milestone, int]]:
        """Return ``(milestone, total_session_minutes)`` pairs for a project.

        :rtype: list[tuple[Milestone, int]]
        """
        rows = self._db.fetchall(
            """
            SELECT m.*, COALESCE(SUM(s.duration_minutes), 0) AS total_minutes
            FROM milestone m
            LEFT JOIN session s ON s.milestone_id = m.id
            WHERE m.project_id = ?
            GROUP BY m.id
            ORDER BY m.sort_order, m.id
            """,
            (project_id,),
        )
        return [(row_to_milestone(r), r["total_minutes"]) for r in rows]

    def update(self, milestone: Milestone) -> Milestone:
        """Persist changes to an existing milestone.

        :raises NotFoundError: If the milestone does not exist.
        :rtype: Milestone
        """
        with self._db.transaction():
            self._db.execute(
                """
                UPDATE milestone SET
                    description = ?, status = ?, completed_date = ?,
                    target_date = ?, sort_order = ?, notes = ?
                WHERE id = ?
                """,
                (
                    milestone.description,
                    milestone.status,
                    milestone.completed_date.isoformat() if milestone.completed_date else None,
                    milestone.target_date.isoformat() if milestone.target_date else None,
                    milestone.sort_order,
                    milestone.notes,
                    milestone.id,
                ),
            )
        return self.get(milestone.id)

    def delete(self, milestone_id: int) -> None:
        """Delete a milestone by primary key.

        :raises NotFoundError: If the milestone does not exist.
        """
        self.get(milestone_id)
        with self._db.transaction():
            self._db.execute("DELETE FROM milestone WHERE id = ?", (milestone_id,))

    def count(self, project_id: int) -> tuple[int, int]:
        """Return ``(total, done)`` counts, excluding cancelled milestones.

        Cancelled milestones are excluded from scoring per the SRS.

        :rtype: tuple[int, int]
        """
        row = self._db.fetchone(
            """
            SELECT
                SUM(CASE WHEN status != 'cancelled' THEN 1 ELSE 0 END) AS total,
                SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) AS done_count
            FROM milestone
            WHERE project_id = ?
            """,
            (project_id,),
        )
        if row is None:
            return 0, 0
        return (row["total"] or 0), (row["done_count"] or 0)
