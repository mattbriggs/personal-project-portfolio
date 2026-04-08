"""Domain model for a work session."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal

SessionStatus = Literal["planned", "completed", "cancelled"]


@dataclass
class Session:
    """Represents a single time-boxed work session.

    :param id: Database primary key (0 for unsaved instances).
    :param project_id: Foreign key to the owning :class:`~portfolio_manager.models.project.Project`.
    :param scheduled_date: The date on which the session is planned.
    :param week_key: ISO week key in ``YYYY.W`` format, computed from *scheduled_date*.
    :param duration_minutes: Session length in minutes (60–180).
    :param status: Current state — ``planned``, ``completed``, or ``cancelled``.
    :param focus: Brief description of the session's intended focus.
    :param notes: Free-text notes recorded after completion.
    :param created_at: Row creation timestamp.
    :param completed_at: Timestamp when status transitioned to ``completed``.
    """

    id: int = 0
    project_id: int = 0
    scheduled_date: date = field(default_factory=date.today)
    week_key: str = ""
    duration_minutes: int = 90
    status: SessionStatus = "planned"
    focus: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    def is_completed(self) -> bool:
        """Return ``True`` if the session has been marked complete.

        :rtype: bool
        """
        return self.status == "completed"

    def is_planned(self) -> bool:
        """Return ``True`` if the session is still planned.

        :rtype: bool
        """
        return self.status == "planned"

    def __str__(self) -> str:
        return f"Session({self.id}, project={self.project_id}, {self.scheduled_date}, {self.status})"
