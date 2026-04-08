"""Repository for ProjectScore entities."""

import sqlite3
from datetime import datetime

from portfolio_manager.db.connection import DatabaseConnection
from portfolio_manager.exceptions import NotFoundError
from portfolio_manager.models.score import ProjectScore, ScoreStatus
from portfolio_manager.repositories.base import BaseRepository


def _row_to_score(row: sqlite3.Row) -> ProjectScore:
    """Convert a :class:`sqlite3.Row` to a :class:`ProjectScore` domain object.

    :param row: A row from the ``project_score`` table.
    :rtype: ProjectScore
    """
    return ProjectScore(
        id=row["id"],
        project_id=row["project_id"],
        week_key=row["week_key"],
        score=row["score"] if row["score"] is not None else 0,
        status=row["status"] if row["status"] else "red",
        status_note=row["status_note"],
        is_manual_override=bool(row["is_manual_override"]),
        override_reason=row["override_reason"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


class ScoreRepository(BaseRepository):
    """CRUD and query operations for :class:`~portfolio_manager.models.score.ProjectScore`.

    :param db: Shared database connection.
    :type db: DatabaseConnection
    """

    def __init__(self, db: DatabaseConnection) -> None:
        super().__init__(db)

    def upsert(self, score: ProjectScore) -> ProjectScore:
        """Insert or replace the score record for a ``(project_id, week_key)`` pair.

        If a record already exists for this project+week it is replaced.

        :param score: Score to persist.
        :type score: ProjectScore
        :returns: The persisted score with ``id`` set.
        :rtype: ProjectScore
        """
        with self.transaction():
            cur = self._db.execute(
                """
                INSERT INTO project_score
                    (project_id, week_key, score, status, status_note,
                     is_manual_override, override_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id, week_key) DO UPDATE SET
                    score              = excluded.score,
                    status             = excluded.status,
                    status_note        = excluded.status_note,
                    is_manual_override = excluded.is_manual_override,
                    override_reason    = excluded.override_reason
                """,
                (
                    score.project_id,
                    score.week_key,
                    score.score,
                    score.status,
                    score.status_note,
                    int(score.is_manual_override),
                    score.override_reason,
                ),
            )
            if score.id == 0 and cur.lastrowid:
                score.id = cur.lastrowid
        return score

    def get_for_week(self, project_id: int, week_key: str) -> ProjectScore | None:
        """Return the score for a project in a given week, or ``None``.

        :param project_id: Target project.
        :param week_key: Target week in ``YYYY.W`` format.
        :rtype: ProjectScore | None
        """
        row = self._db.fetchone(
            "SELECT * FROM project_score WHERE project_id = ? AND week_key = ?",
            (project_id, week_key),
        )
        return _row_to_score(row) if row else None

    def list_for_project(self, project_id: int) -> list[ProjectScore]:
        """Return all score records for a project, most recent first.

        :param project_id: Target project.
        :rtype: list[ProjectScore]
        """
        rows = self._db.fetchall(
            "SELECT * FROM project_score WHERE project_id = ? ORDER BY week_key DESC",
            (project_id,),
        )
        return [_row_to_score(r) for r in rows]

    def list_for_week(self, week_key: str) -> list[ProjectScore]:
        """Return scores for all projects in a given week.

        :param week_key: Target week in ``YYYY.W`` format.
        :rtype: list[ProjectScore]
        """
        rows = self._db.fetchall(
            "SELECT * FROM project_score WHERE week_key = ?",
            (week_key,),
        )
        return [_row_to_score(r) for r in rows]
