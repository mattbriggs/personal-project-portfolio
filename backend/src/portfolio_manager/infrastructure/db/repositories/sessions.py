"""SQLite repository for :class:`Session`.

Implements :class:`portfolio_manager.application.ports.session_repository.SessionRepository`.
Ported from the original ``repositories/session_repo.py``.
"""

from collections.abc import Mapping

from portfolio_manager.domain.enums import SessionStatus
from portfolio_manager.domain.errors import NotFoundError
from portfolio_manager.domain.models import Session
from portfolio_manager.infrastructure.db.connection import DatabaseConnection
from portfolio_manager.infrastructure.db.row_mapping import row_to_session


class SqliteSessionRepository:
    """CRUD and query operations for sessions.

    :param db: Shared database connection.
    """

    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def create(self, session: Session) -> Session:
        """Insert a session and return it with its assigned ``id``.

        :rtype: Session
        """
        with self._db.transaction():
            cur = self._db.execute(
                """
                INSERT INTO session
                    (project_id, milestone_id, scheduled_date, week_key,
                     duration_minutes, status, description, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.project_id,
                    session.milestone_id,
                    session.scheduled_date.isoformat(),
                    session.week_key,
                    session.duration_minutes,
                    session.status,
                    session.description,
                    session.notes,
                ),
            )
            session.id = cur.lastrowid or 0
        return session

    def get(self, session_id: int) -> Session:
        """Fetch a session by primary key.

        :raises NotFoundError: If the session does not exist.
        :rtype: Session
        """
        row = self._db.fetchone("SELECT * FROM session WHERE id = ?", (session_id,))
        if row is None:
            raise NotFoundError("Session", session_id)
        return row_to_session(row)

    def list_for_project(
        self,
        project_id: int,
        week_key: str | None = None,
        status: SessionStatus | None = None,
    ) -> list[Session]:
        """Return sessions for a project, optionally filtered by week/status.

        Ordered by scheduled date.

        :rtype: list[Session]
        """
        sql = "SELECT * FROM session WHERE project_id = ?"
        params: list = [project_id]
        if week_key:
            sql += " AND week_key = ?"
            params.append(week_key)
        if status:
            sql += " AND status = ?"
            params.append(status)
        sql += " ORDER BY scheduled_date, id"
        return [row_to_session(r) for r in self._db.fetchall(sql, params)]

    def list_for_week(self, week_key: str) -> list[Session]:
        """Return all sessions across projects for a week, ordered by date.

        :rtype: list[Session]
        """
        rows = self._db.fetchall(
            "SELECT * FROM session WHERE week_key = ? ORDER BY scheduled_date, id",
            (week_key,),
        )
        return [row_to_session(r) for r in rows]

    def update(self, session: Session) -> Session:
        """Persist changes to an existing session.

        :raises NotFoundError: If the session does not exist.
        :rtype: Session
        """
        with self._db.transaction():
            self._db.execute(
                """
                UPDATE session SET
                    project_id = ?, milestone_id = ?, scheduled_date = ?, week_key = ?,
                    duration_minutes = ?, status = ?, description = ?,
                    notes = ?, completed_at = ?
                WHERE id = ?
                """,
                (
                    session.project_id,
                    session.milestone_id,
                    session.scheduled_date.isoformat(),
                    session.week_key,
                    session.duration_minutes,
                    session.status,
                    session.description,
                    session.notes,
                    session.completed_at.isoformat() if session.completed_at else None,
                    session.id,
                ),
            )
        return self.get(session.id)

    def delete(self, session_id: int) -> None:
        """Delete a session by primary key.

        :raises NotFoundError: If the session does not exist.
        """
        self.get(session_id)
        with self._db.transaction():
            self._db.execute("DELETE FROM session WHERE id = ?", (session_id,))

    def count_by_status(self, project_id: int, week_key: str) -> Mapping[str, int]:
        """Return ``{status: count}`` for a project in a week.

        :rtype: collections.abc.Mapping[str, int]
        """
        rows = self._db.fetchall(
            """
            SELECT status, COUNT(*) AS cnt
            FROM session
            WHERE project_id = ? AND week_key = ?
            GROUP BY status
            """,
            (project_id, week_key),
        )
        return {r["status"]: r["cnt"] for r in rows}
