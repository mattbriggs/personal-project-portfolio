"""Repository for WeeklyReview entities."""

import sqlite3
from datetime import date, datetime

from portfolio_manager.db.connection import DatabaseConnection
from portfolio_manager.models.review import WeeklyReview
from portfolio_manager.repositories.base import BaseRepository


def _row_to_review(row: sqlite3.Row) -> WeeklyReview:
    """Convert a :class:`sqlite3.Row` to a :class:`WeeklyReview` domain object.

    :param row: A row from the ``weekly_review`` table.
    :rtype: WeeklyReview
    """
    return WeeklyReview(
        id=row["id"],
        week_key=row["week_key"],
        date_from=date.fromisoformat(row["date_from"]) if row["date_from"] else None,
        date_to=date.fromisoformat(row["date_to"]) if row["date_to"] else None,
        hours_invested=row["hours_invested"] or 0.0,
        sessions_completed=row["sessions_completed"] or 0,
        what_moved=row["what_moved"],
        what_stalled=row["what_stalled"],
        signals=row["signals"],
        decision_next_week=row["decision_next_week"],
        primary_focus=row["primary_focus"],
        project_to_deprioritize=row["project_to_deprioritize"],
        risk_to_watch=row["risk_to_watch"],
        first_session_target=row["first_session_target"],
        written_to_repo=bool(row["written_to_repo"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class ReviewRepository(BaseRepository):
    """CRUD and query operations for :class:`~portfolio_manager.models.review.WeeklyReview`.

    :param db: Shared database connection.
    :type db: DatabaseConnection
    """

    def __init__(self, db: DatabaseConnection) -> None:
        super().__init__(db)

    def upsert(self, review: WeeklyReview) -> WeeklyReview:
        """Insert or update a weekly review (keyed by ``week_key``).

        :param review: Review to persist.
        :type review: WeeklyReview
        :returns: The persisted review with ``id`` set.
        :rtype: WeeklyReview
        """
        with self.transaction():
            cur = self._db.execute(
                """
                INSERT INTO weekly_review
                    (week_key, date_from, date_to, hours_invested, sessions_completed,
                     what_moved, what_stalled, signals, decision_next_week,
                     primary_focus, project_to_deprioritize, risk_to_watch,
                     first_session_target, written_to_repo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(week_key) DO UPDATE SET
                    date_from              = excluded.date_from,
                    date_to                = excluded.date_to,
                    hours_invested         = excluded.hours_invested,
                    sessions_completed     = excluded.sessions_completed,
                    what_moved             = excluded.what_moved,
                    what_stalled           = excluded.what_stalled,
                    signals                = excluded.signals,
                    decision_next_week     = excluded.decision_next_week,
                    primary_focus          = excluded.primary_focus,
                    project_to_deprioritize = excluded.project_to_deprioritize,
                    risk_to_watch          = excluded.risk_to_watch,
                    first_session_target   = excluded.first_session_target,
                    written_to_repo        = excluded.written_to_repo
                """,
                (
                    review.week_key,
                    review.date_from.isoformat() if review.date_from else None,
                    review.date_to.isoformat() if review.date_to else None,
                    review.hours_invested,
                    review.sessions_completed,
                    review.what_moved,
                    review.what_stalled,
                    review.signals,
                    review.decision_next_week,
                    review.primary_focus,
                    review.project_to_deprioritize,
                    review.risk_to_watch,
                    review.first_session_target,
                    int(review.written_to_repo),
                ),
            )
            if review.id == 0 and cur.lastrowid:
                review.id = cur.lastrowid
        return review

    def get_for_week(self, week_key: str) -> WeeklyReview | None:
        """Return the review for a given week, or ``None`` if absent.

        :param week_key: Target week in ``YYYY.W`` format.
        :rtype: WeeklyReview | None
        """
        row = self._db.fetchone(
            "SELECT * FROM weekly_review WHERE week_key = ?", (week_key,)
        )
        return _row_to_review(row) if row else None

    def list_all(self) -> list[WeeklyReview]:
        """Return all weekly reviews ordered by week key descending (most recent first).

        :rtype: list[WeeklyReview]
        """
        rows = self._db.fetchall(
            "SELECT * FROM weekly_review"
            " ORDER BY substr(week_key, 1, 4) DESC,"
            " CAST(substr(week_key, 6) AS INTEGER) DESC"
        )
        return [_row_to_review(r) for r in rows]
