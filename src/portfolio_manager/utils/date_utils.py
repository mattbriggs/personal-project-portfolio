"""Date and week-key utilities for Portfolio Manager.

All week numbers use **ISO 8601** via :meth:`datetime.date.isocalendar`.
Week 1 is the week containing the first Thursday of the year.

Week key format: ``YYYY.W`` — e.g. ``2026.15``.
"""

from datetime import date, datetime, timedelta, timezone


def utcnow() -> datetime:
    """Return the current UTC datetime as a naive :class:`datetime`.

    Replaces the deprecated :func:`datetime.utcnow` while keeping stored
    timestamps as naive UTC strings for backward compatibility with existing
    database rows.

    :rtype: datetime
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_week_key(d: date) -> str:
    """Convert a date to the canonical ``YYYY.W`` week key format.

    :param d: The date to convert.
    :type d: datetime.date
    :returns: Week key string, e.g. ``'2026.15'``.
    :rtype: str

    Example::

        >>> from datetime import date
        >>> to_week_key(date(2026, 4, 7))
        '2026.15'
    """
    iso = d.isocalendar()
    return f"{iso.year}.{iso.week}"


def current_week_key() -> str:
    """Return the week key for today's date.

    :returns: Week key string for today, e.g. ``'2026.15'``.
    :rtype: str
    """
    return to_week_key(date.today())


def week_key_to_date_range(week_key: str) -> tuple[date, date]:
    """Return the Monday and Sunday bounding the given ISO week.

    :param week_key: Week key in ``YYYY.W`` format.
    :type week_key: str
    :returns: Tuple of ``(monday, sunday)`` as :class:`datetime.date` objects.
    :rtype: tuple[datetime.date, datetime.date]
    :raises ValueError: If *week_key* is not in ``YYYY.W`` format.

    Example::

        >>> week_key_to_date_range('2026.15')
        (datetime.date(2026, 4, 6), datetime.date(2026, 4, 12))
    """
    try:
        year_str, week_str = week_key.split(".")
        year = int(year_str)
        week = int(week_str)
    except (ValueError, AttributeError) as exc:
        raise ValueError(
            f"Invalid week key format: {week_key!r}. Expected 'YYYY.W'."
        ) from exc

    # ISO week 1 Monday: use Jan 4 which is always in week 1.
    jan4 = date(year, 1, 4)
    week1_monday = jan4 - timedelta(days=jan4.weekday())
    monday = week1_monday + timedelta(weeks=week - 1)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def parse_week_key(week_key: str) -> tuple[int, int]:
    """Parse a week key into ``(year, week)`` integers.

    :param week_key: Week key in ``YYYY.W`` format.
    :type week_key: str
    :returns: Tuple of ``(year, week_number)``.
    :rtype: tuple[int, int]
    :raises ValueError: If the format is invalid.
    """
    try:
        year_str, week_str = week_key.split(".")
        return int(year_str), int(week_str)
    except (ValueError, AttributeError) as exc:
        raise ValueError(
            f"Invalid week key format: {week_key!r}. Expected 'YYYY.W'."
        ) from exc
