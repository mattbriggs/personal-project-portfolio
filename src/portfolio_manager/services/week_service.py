"""Service for week-key computation and week boundary resolution."""

import logging
from datetime import date

from portfolio_manager.utils.date_utils import (
    current_week_key,
    to_week_key,
    week_key_to_date_range,
)

logger = logging.getLogger(__name__)


class WeekService:
    """Provides week-key helpers used by other services and controllers.

    This service has no repository dependency — it is purely computational.
    """

    def current_week_key(self) -> str:
        """Return the ISO week key for today's date.

        :returns: Week key string, e.g. ``'2026.15'``.
        :rtype: str
        """
        return current_week_key()

    def week_key_for_date(self, d: date) -> str:
        """Return the ISO week key for an arbitrary date.

        :param d: Any calendar date.
        :type d: datetime.date
        :returns: Week key string.
        :rtype: str
        """
        return to_week_key(d)

    def date_range(self, week_key: str) -> tuple[date, date]:
        """Return the Monday and Sunday for a given week key.

        :param week_key: Week in ``YYYY.W`` format.
        :type week_key: str
        :returns: ``(monday, sunday)`` tuple.
        :rtype: tuple[datetime.date, datetime.date]
        """
        return week_key_to_date_range(week_key)

    def display_range(self, week_key: str) -> str:
        """Return a human-readable date range string for a week.

        Example: ``'Apr 6 – Apr 12, 2026'``

        :param week_key: Week in ``YYYY.W`` format.
        :type week_key: str
        :rtype: str
        """
        monday, sunday = week_key_to_date_range(week_key)
        if monday.year == sunday.year:
            return f"{monday.strftime('%b %-d')} – {sunday.strftime('%b %-d, %Y')}"
        return f"{monday.strftime('%b %-d, %Y')} – {sunday.strftime('%b %-d, %Y')}"
