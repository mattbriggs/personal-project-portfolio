"""Controller for the weekly review view."""

import logging

from portfolio_manager.events.event_bus import REVIEW_SAVED, EventBus
from portfolio_manager.models.review import WeeklyReview
from portfolio_manager.repositories.review_repo import ReviewRepository
from portfolio_manager.services.week_service import WeekService

logger = logging.getLogger(__name__)


class ReviewController:
    """Mediates between the weekly review view and the review repository.

    :param review_repo: Repository for weekly review persistence.
    :param week_service: Service for week-key and date-range helpers.
    :param bus: Event bus.
    """

    def __init__(
        self,
        review_repo: ReviewRepository,
        week_service: WeekService,
        bus: EventBus | None = None,
    ) -> None:
        self._reviews = review_repo
        self._weeks = week_service
        self._bus = bus or EventBus.get()

    def get_or_create_review(self, week_key: str | None = None) -> WeeklyReview:
        """Return the review for a week, creating a blank one if absent.

        :param week_key: Week in ``YYYY.W`` format; uses current week if ``None``.
        :rtype: WeeklyReview
        """
        wk = week_key or self._weeks.current_week_key()
        review = self._reviews.get_for_week(wk)
        if review is None:
            monday, sunday = self._weeks.date_range(wk)
            review = WeeklyReview(
                week_key=wk,
                date_from=monday,
                date_to=sunday,
            )
        return review

    def save_review(self, review: WeeklyReview) -> WeeklyReview:
        """Persist a weekly review.

        :param review: Review to save.
        :rtype: WeeklyReview
        """
        saved = self._reviews.upsert(review)
        self._bus.emit(REVIEW_SAVED, week_key=saved.week_key)
        logger.info("Saved weekly review for %s", saved.week_key)
        return saved

    def list_reviews(self) -> list[WeeklyReview]:
        """Return all weekly reviews, most recent first.

        :rtype: list[WeeklyReview]
        """
        return self._reviews.list_all()
