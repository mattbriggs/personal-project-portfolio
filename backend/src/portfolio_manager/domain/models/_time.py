"""Naive-UTC timestamp helper shared by domain models.

Kept identical to the original ``utils/date_utils.utcnow`` so stored timestamps
remain naive UTC ISO strings, preserving backward compatibility with existing
database rows.
"""

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Return the current UTC time as a naive :class:`datetime`.

    :rtype: datetime
    """
    return datetime.now(UTC).replace(tzinfo=None)
