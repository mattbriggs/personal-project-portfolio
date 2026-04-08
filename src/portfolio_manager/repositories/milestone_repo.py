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
        is_complete=bool(row["is_complete"]),
        completed_date=(
            date.fromisoformat(row["completed_date"]) if row["completed_date"] else None
        ),
        sort_order=row["sort_order"],
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

        :param milestone: Unsaved milestone object.
        :type milestone: Milestone
        :returns: The milestone with ``id`` populated.
        :rtype: Milestone
        """
        with self.transaction():
            cur = self._db.execute(
                """
                INSERT INTO milestone
                    (project_id, description, is_complete, completed_date, sort_order)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    milestone.project_id,
                    milestone.description,
                    int(milestone.is_complete),
                    milestone.completed_date.isoformat() if milestone.completed_date else None,
                    milestone.sort_order,
                ),
            )
            milestone.id = cur.lastrowid or 0
        return milestone

    def get(self, milestone_id: int) -> Milestone:
        """Fetch a milestone by primary key.

        :param milestone_id: The milestone's primary key.
        :type milestone_id: int
        :raises NotFoundError: If no milestone with *milestone_id* exists.
        :rtype: Milestone
        """
        row = self._db.fetchone(
            "SELECT * FROM milestone WHERE id = ?", (milestone_id,)
        )
        if row is None:
            raise NotFoundError("Milestone", milestone_id)
        return _row_to_milestone(row)

    def list_for_project(self, project_id: int) -> list[Milestone]:
        """Return all milestones for a project ordered by ``sort_order``.

        :param project_id: Target project's primary key.
        :type project_id: int
        :rtype: list[Milestone]
        """
        rows = self._db.fetchall(
            "SELECT * FROM milestone WHERE project_id = ? ORDER BY sort_order, id",
            (project_id,),
        )
        return [_row_to_milestone(r) for r in rows]

    def update(self, milestone: Milestone) -> Milestone:
        """Persist changes to an existing milestone.

        :param milestone: Milestone with updated fields.
        :type milestone: Milestone
        :raises NotFoundError: If the milestone does not exist.
        :rtype: Milestone
        """
        with self.transaction():
            self._db.execute(
                """
                UPDATE milestone SET
                    description = ?, is_complete = ?, completed_date = ?, sort_order = ?
                WHERE id = ?
                """,
                (
                    milestone.description,
                    int(milestone.is_complete),
                    milestone.completed_date.isoformat() if milestone.completed_date else None,
                    milestone.sort_order,
                    milestone.id,
                ),
            )
        return self.get(milestone.id)

    def delete(self, milestone_id: int) -> None:
        """Delete a milestone by primary key.

        :param milestone_id: Primary key of the milestone to delete.
        :type milestone_id: int
        :raises NotFoundError: If the milestone does not exist.
        """
        self.get(milestone_id)
        with self.transaction():
            self._db.execute(
                "DELETE FROM milestone WHERE id = ?", (milestone_id,)
            )

    def count(self, project_id: int) -> tuple[int, int]:
        """Return ``(total, completed)`` milestone counts for a project.

        :param project_id: Target project's primary key.
        :type project_id: int
        :returns: Tuple of ``(total_count, completed_count)``.
        :rtype: tuple[int, int]
        """
        row = self._db.fetchone(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN is_complete = 1 THEN 1 ELSE 0 END) AS completed
            FROM milestone
            WHERE project_id = ?
            """,
            (project_id,),
        )
        if row is None:
            return 0, 0
        return (row["total"] or 0), (row["completed"] or 0)
