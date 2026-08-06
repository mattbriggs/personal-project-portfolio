"""SQLite repository for :class:`ProjectScore`.

Implements :class:`portfolio_manager.application.ports.score_repository.ScoreRepository`.
Ported from the original ``repositories/score_repo.py``.
"""

from portfolio_manager.domain.models import ProjectScore
from portfolio_manager.infrastructure.db.connection import DatabaseConnection
from portfolio_manager.infrastructure.db.row_mapping import row_to_score


class SqliteScoreRepository:
    """Upsert and query operations for project scores.

    :param db: Shared database connection.
    """

    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def upsert(self, score: ProjectScore) -> ProjectScore:
        """Insert or update the score for a ``(project_id, week_key)`` pair.

        :param score: Score to persist.
        :returns: The persisted score with ``id`` set.
        :rtype: ProjectScore
        """
        with self._db.transaction():
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
        """Return the score for a project in a week, or ``None``.

        :rtype: ProjectScore | None
        """
        row = self._db.fetchone(
            "SELECT * FROM project_score WHERE project_id = ? AND week_key = ?",
            (project_id, week_key),
        )
        return row_to_score(row) if row else None

    def list_for_project(self, project_id: int) -> list[ProjectScore]:
        """Return all scores for a project, most recent week first.

        :rtype: list[ProjectScore]
        """
        rows = self._db.fetchall(
            "SELECT * FROM project_score WHERE project_id = ?"
            " ORDER BY substr(week_key, 1, 4) DESC,"
            " CAST(substr(week_key, 6) AS INTEGER) DESC",
            (project_id,),
        )
        return [row_to_score(r) for r in rows]

    def list_for_week(self, week_key: str) -> list[ProjectScore]:
        """Return scores for all projects in a week.

        :rtype: list[ProjectScore]
        """
        rows = self._db.fetchall("SELECT * FROM project_score WHERE week_key = ?", (week_key,))
        return [row_to_score(r) for r in rows]
