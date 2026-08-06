"""SQLite repository for :class:`WeeklyReview`.

Implements :class:`portfolio_manager.application.ports.review_repository.ReviewRepository`.
Ported from the original ``repositories/review_repo.py``.
"""

from portfolio_manager.domain.models import WeeklyReview
from portfolio_manager.infrastructure.db.connection import DatabaseConnection
from portfolio_manager.infrastructure.db.row_mapping import row_to_review


class SqliteReviewRepository:
    """Upsert and query operations for weekly reviews.

    :param db: Shared database connection.
    """

    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def upsert(self, review: WeeklyReview) -> WeeklyReview:
        """Insert or update a weekly review (keyed by ``week_key``).

        :param review: Review to persist.
        :returns: The persisted review with ``id`` set.
        :rtype: WeeklyReview
        """
        with self._db.transaction():
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
        """Return the review for a week, or ``None``.

        :rtype: WeeklyReview | None
        """
        row = self._db.fetchone("SELECT * FROM weekly_review WHERE week_key = ?", (week_key,))
        return row_to_review(row) if row else None

    def list_all(self) -> list[WeeklyReview]:
        """Return all reviews ordered most recent first.

        :rtype: list[WeeklyReview]
        """
        rows = self._db.fetchall(
            "SELECT * FROM weekly_review"
            " ORDER BY substr(week_key, 1, 4) DESC,"
            " CAST(substr(week_key, 6) AS INTEGER) DESC"
        )
        return [row_to_review(r) for r in rows]
