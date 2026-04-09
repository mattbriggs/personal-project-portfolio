"""Repository for Milestone entities."""

import sqlite3
from datetime import date, datetime

from portfolio_manager.db.connection import DatabaseConnection
from portfolio_manager.exceptions import NotFoundError
from portfolio_manager.models.milestone import Milestone
from portfolio_manager.repositories.base import BaseRepository


def _row_to_milestone(row: sqlite3.Row) -> Milestone:
    """Convert a :class:`sqlite3.Row` to a :class:`Milestone` domain object.

    :param row: A row from the ``milestone`` table.
    :rtype: Milestone
    """
    return Milestone(
        id=row["id"],
        project_id=row["project_id"],
        description=row["description"],
        status=row["status"],
        completed_date=(
            date.fromisoformat(row["completed_date"]) if row["completed_date"] else None
        ),
        target_date=(
            date.fromisoformat(row["target_date"]) if row["target_date"] else None
        ),
        sort_order=row["sort_order"],
        notes=row["notes"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class MilestoneRepository(BaseRepository):
    """CRUD and query operations for :class:`~portfolio_manager.models.milestone.Milestone`.

    :param db: Shared database connection.
    :type db: DatabaseConnection
    """

    def __init__(self, db: DatabaseConnection) -> None:
        super().__init__(db)

    def create(self, milestone: Milestone) -> Milestone:
        """Insert a new milestone and return it with the assigned ``id``.

        :rtype: Milestone
        """
        with self.transaction():
            cur = self._db.execute(
                """
                INSERT INTO milestone
                    (project_id, description, status, completed_date, target_date, sort_order, notes)
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

        :raises NotFoundError: If no milestone with *milestone_id* exists.
        :rtype: Milestone
        """
        row = self._db.fetchone("SELECT * FROM milestone WHERE id = ?", (milestone_id,))
        if row is None:
            raise NotFoundError("Milestone", milestone_id)
        return _row_to_milestone(row)

    def list_for_project(self, project_id: int) -> list[Milestone]:
        """Return all milestones for a project ordered by ``sort_order``.

        :rtype: list[Milestone]
        """
        rows = self._db.fetchall(
            "SELECT * FROM milestone WHERE project_id = ? ORDER BY sort_order, id",
            (project_id,),
        )
        return [_row_to_milestone(r) for r in rows]

    def list_for_project_with_totals(
        self, project_id: int
    ) -> list[tuple[Milestone, int]]:
        """Return milestones with their total session minutes.

        Performs a single LEFT JOIN so each milestone carries its aggregate
        session time without extra round-trips.

        :param project_id: Target project's primary key.
        :rtype: list[tuple[Milestone, int]]
        """
        rows = self._db.fetchall(
            """
            SELECT m.*,
                   COALESCE(SUM(s.duration_minutes), 0) AS total_minutes
            FROM milestone m
            LEFT JOIN session s ON s.milestone_id = m.id
            WHERE m.project_id = ?
            GROUP BY m.id
            ORDER BY m.sort_order, m.id
            """,
            (project_id,),
        )
        return [(_row_to_milestone(r), r["total_minutes"]) for r in rows]

    def update(self, milestone: Milestone) -> Milestone:
        """Persist changes to an existing milestone.

        :raises NotFoundError: If the milestone does not exist.
        :rtype: Milestone
        """
        with self.transaction():
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
        with self.transaction():
            self._db.execute("DELETE FROM milestone WHERE id = ?", (milestone_id,))

    def count(self, project_id: int) -> tuple[int, int]:
        """Return ``(total, done)`` milestone counts for a project.

        :rtype: tuple[int, int]
        """
        row = self._db.fetchone(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) AS done_count
            FROM milestone
            WHERE project_id = ?
            """,
            (project_id,),
        )
        if row is None:
            return 0, 0
        return (row["total"] or 0), (row["done_count"] or 0)
