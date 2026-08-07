"""ISO week-key calculations.

Ported verbatim from the original ``utils/date_utils.py`` so week keys, week
date ranges, and year-boundary behavior remain identical to existing data.

Week key format: ``YYYY.W`` (e.g. ``2026.15``). Week numbers use ISO 8601 via
:meth:`datetime.date.isocalendar`; week 1 contains the first Thursday of the
year.
"""

from datetime import date, timedelta


def to_week_key(d: date) -> str:
    """Convert a date to the canonical ``YYYY.W`` week key.

    :param d: The date to convert.
    :returns: Week key string, e.g. ``'2026.15'``.
    :rtype: str
    """
    iso = d.isocalendar()
    return f"{iso.year}.{iso.week}"


def current_week_key(today: date | None = None) -> str:
    """Return the week key for *today* (or the current date).

    :param today: Optional injected date for deterministic tests.
    :returns: Week key string.
    :rtype: str
    """
    return to_week_key(today or date.today())


def week_key_to_date_range(week_key: str) -> tuple[date, date]:
    """Return the Monday and Sunday bounding the given ISO week.

    :param week_key: Week key in ``YYYY.W`` format.
    :returns: ``(monday, sunday)`` tuple.
    :rtype: tuple[datetime.date, datetime.date]
    :raises ValueError: If *week_key* is not in ``YYYY.W`` format.
    """
    year, week = parse_week_key(week_key)
    # ISO week 1 always contains Jan 4.
    jan4 = date(year, 1, 4)
    week1_monday = jan4 - timedelta(days=jan4.weekday())
    monday = week1_monday + timedelta(weeks=week - 1)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def parse_week_key(week_key: str) -> tuple[int, int]:
    """Parse a week key into ``(year, week)`` integers.

    :param week_key: Week key in ``YYYY.W`` format.
    :returns: ``(year, week_number)``.
    :rtype: tuple[int, int]
    :raises ValueError: If the format is invalid.
    """
    try:
        year_str, week_str = week_key.split(".")
        return int(year_str), int(week_str)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"Invalid week key format: {week_key!r}. Expected 'YYYY.W'.") from exc


def is_valid_week_key(week_key: str) -> bool:
    """Return ``True`` if *week_key* is a syntactically valid ``YYYY.W`` key.

    :param week_key: Candidate week key.
    :rtype: bool
    """
    try:
        year, week = parse_week_key(week_key)
    except ValueError:
        return False
    return 1 <= week <= 53 and year >= 1


def display_range(week_key: str) -> str:
    """Return a human-readable date range string for a week.

    Example: ``'Apr 6 – Apr 12, 2026'``.

    :param week_key: Week key in ``YYYY.W`` format.
    :rtype: str
    """
    monday, sunday = week_key_to_date_range(week_key)
    if monday.year == sunday.year:
        return f"{monday.strftime('%b %-d')} – {sunday.strftime('%b %-d, %Y')}"
    return f"{monday.strftime('%b %-d, %Y')} – {sunday.strftime('%b %-d, %Y')}"
