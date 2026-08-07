"""Weekly review service.

Consolidates behavior from the Tkinter review controller. Get-or-create returns
a *transient* blank review (with derived date range) when none exists — it is not
persisted until explicitly saved, preserving the original behavior.
"""

import logging

from portfolio_manager.application.ports.review_repository import ReviewRepository
from portfolio_manager.domain.errors import ValidationError
from portfolio_manager.domain.models import WeeklyReview
from portfolio_manager.domain.week import (
    current_week_key,
    is_valid_week_key,
    week_key_to_date_range,
)

logger = logging.getLogger(__name__)


class ReviewService:
    """Coordinate weekly review get-or-create, save, and history.

    :param reviews: Review repository port.
    """

    def __init__(self, reviews: ReviewRepository) -> None:
        self._reviews = reviews

    def get_or_create(self, week_key: str | None = None) -> WeeklyReview:
        """Return the review for a week, or a transient blank one if absent.

        The blank review is not persisted until :meth:`save` is called.

        :param week_key: Week (``YYYY.W``); uses the current week if ``None``.
        :returns: The persisted or transient review.
        :rtype: WeeklyReview
        :raises ValidationError: If *week_key* is malformed.
        """
        wk = week_key or current_week_key()
        if not is_valid_week_key(wk):
            raise ValidationError(f"Invalid week key {wk!r}. Expected 'YYYY.W'.")
        review = self._reviews.get_for_week(wk)
        if review is None:
            monday, sunday = week_key_to_date_range(wk)
            review = WeeklyReview(week_key=wk, date_from=monday, date_to=sunday)
        return review

    def save(self, review: WeeklyReview) -> WeeklyReview:
        """Persist a weekly review, deriving the date range from the week key.

        :param review: Review to save.
        :returns: The saved review.
        :rtype: WeeklyReview
        :raises ValidationError: If the week key is malformed.
        """
        if not is_valid_week_key(review.week_key):
            raise ValidationError(f"Invalid week key {review.week_key!r}. Expected 'YYYY.W'.")
        monday, sunday = week_key_to_date_range(review.week_key)
        review.date_from = monday
        review.date_to = sunday
        saved = self._reviews.upsert(review)
        logger.info("Saved weekly review for %s", saved.week_key)
        return saved

    def list_reviews(self) -> list[WeeklyReview]:
        """Return all reviews, most recent first.

        :rtype: list[WeeklyReview]
        """
        return self._reviews.list_all()
