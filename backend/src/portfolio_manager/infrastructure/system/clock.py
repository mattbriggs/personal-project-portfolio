"""Clock adapter.

Provides a :class:`Clock` protocol and a system implementation. Services use an
injected clock when assigning or clearing completion timestamps so tests can
supply a deterministic clock.
"""

from datetime import date, datetime
from typing import Protocol

from portfolio_manager.domain.models._time import utcnow


class Clock(Protocol):
    """Abstraction over the current time. See :class:`SystemClock`."""

    def now(self) -> datetime:
        """Return the current naive-UTC datetime.

        :rtype: datetime
        """
        ...

    def today(self) -> date:
        """Return the current local date.

        :rtype: datetime.date
        """
        ...


class SystemClock:
    """Production clock backed by the system time."""

    def now(self) -> datetime:
        """Return the current naive-UTC datetime.

        :rtype: datetime
        """
        return utcnow()

    def today(self) -> date:
        """Return today's local date.

        :rtype: datetime.date
        """
        return date.today()
