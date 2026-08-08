"""Domain model for a work session."""

from dataclasses import dataclass, field
from datetime import date, datetime

from portfolio_manager.domain.enums import SessionStatus
from portfolio_manager.domain.models._time import utcnow


@dataclass
class Session:
    """A single time-boxed work session.

    :param id: Primary key (0 for unsaved instances).
    :param project_id: Owning project's primary key.
    :param milestone_id: Optional associated milestone primary key.
    :param scheduled_date: Date the session is planned for.
    :param week_key: ISO ``YYYY.W`` key derived from *scheduled_date*.
    :param duration_minutes: Session length in minutes (15–480).
    :param status: ``backlog``, ``planned``, ``doing``, ``done``, or ``cancelled``.
    :param description: What the session is about.
    :param notes: Free-text notes.
    :param created_at: Creation timestamp.
    :param completed_at: Timestamp when status became ``done``.
    """

    id: int = 0
    project_id: int = 0
    milestone_id: int | None = None
    scheduled_date: date = field(default_factory=date.today)
    week_key: str = ""
    duration_minutes: int = 90
    status: SessionStatus = "backlog"
    description: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=utcnow)
    completed_at: datetime | None = None

    def is_done(self) -> bool:
        """Return ``True`` if the session is completed.

        :rtype: bool
        """
        return self.status == "done"
