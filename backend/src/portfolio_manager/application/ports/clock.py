"""Clock port used by services for completion timestamps."""

from datetime import date, datetime
from typing import Protocol


class Clock(Protocol):
    """Abstraction over the current time. Tests inject a deterministic clock."""

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
