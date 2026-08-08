"""Weekly review repository port."""

from typing import Protocol

from portfolio_manager.domain.models import WeeklyReview


class ReviewRepository(Protocol):
    """Persistence contract for :class:`WeeklyReview`.

    ``upsert`` enforces one review per week key. ``list_all`` orders most recent
    first.
    """

    def upsert(self, review: WeeklyReview) -> WeeklyReview: ...
    def get_for_week(self, week_key: str) -> WeeklyReview | None: ...
    def list_all(self) -> list[WeeklyReview]: ...
