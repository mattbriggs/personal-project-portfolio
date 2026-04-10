"""Repository for Session entities."""

import sqlite3
from datetime import date, datetime

from portfolio_manager.db.connection import DatabaseConnection
from portfolio_manager.exceptions import NotFoundError
from portfolio_manager.models.session import Session, SessionStatus
from portfolio_manager.repositories.base import BaseRepository


def _row_to_session(row: sqlite3.Row) -> Session:
    """Convert a :class:`sqlite3.Row` to a :class:`Session` domain object.

    :param row: A row from the ``session`` table.
    :rtype: Session
    """
    return Session(
        id=row["id"],
        project_id=row["project_id"],
        milestone_id=row["milestone_id"] if row["milestone_id"] is not None else None,
        scheduled_date=date.fromisoformat(row["scheduled_date"]),
        week_key=row["week_key"],
        duration_minutes=row["duration_minutes"],
        status=row["status"],
        description=row["description"],
        notes=row["notes"],
        created_at=datetime.fromisoformat(row["created_at"]),
        completed_at=(
            datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        ),
    )


class SessionRepository(BaseRepository):
    """CRUD and query operations for :class:`~portfolio_manager.models.session.Session`.

    :param db: Shared database connection.
    :type db: DatabaseConnection
    """

    def __init__(self, db: DatabaseConnection) -> None:
        super().__init__(db)

    def create(self, session: Session) -> Session:
        """Insert a new session and return it with the assigned ``id``.

        :param session: Unsaved session object.
        :rtype: Session
        """
        with self.transaction():
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

        :raises NotFoundError: If no session with *session_id* exists.
        :rtype: Session
        """
        row = self._db.fetchone("SELECT * FROM session WHERE id = ?", (session_id,))
        if row is None:
            raise NotFoundError("Session", session_id)
        return _row_to_session(row)

    def list_for_project(
        self,
        project_id: int,
        week_key: str | None = None,
        status: SessionStatus | None = None,
    ) -> list[Session]:
        """Return sessions for a project, with optional week and status filters.

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

        sql += " ORDER BY scheduled_date"
        rows = self._db.fetchall(sql, params)
        return [_row_to_session(r) for r in rows]

    def list_for_week(self, week_key: str) -> list[Session]:
        """Return all sessions across all projects for a given week.

        :rtype: list[Session]
        """
        rows = self._db.fetchall(
            "SELECT * FROM session WHERE week_key = ? ORDER BY scheduled_date",
            (week_key,),
        )
        return [_row_to_session(r) for r in rows]

    def update(self, session: Session) -> Session:
        """Persist changes to an existing session.

        :raises NotFoundError: If the session does not exist.
        :rtype: Session
        """
        with self.transaction():
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
        with self.transaction():
            self._db.execute("DELETE FROM session WHERE id = ?", (session_id,))

    def count_by_status(self, project_id: int, week_key: str) -> dict[str, int]:
        """Return a dict of ``{status: count}`` for a project in a week.

        :rtype: dict[str, int]
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
