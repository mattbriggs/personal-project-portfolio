"""Domain model for a work session."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal

from portfolio_manager.utils.date_utils import utcnow

SessionStatus = Literal["backlog", "planned", "doing", "done", "cancelled"]


@dataclass
class Session:
    """Represents a single time-boxed work session.

    :param id: Database primary key (0 for unsaved instances).
    :param project_id: Foreign key to the owning project.
    :param milestone_id: Optional foreign key to the associated milestone.
    :param scheduled_date: The date on which the session is planned.
    :param week_key: ISO week key in ``YYYY.W`` format, derived from *scheduled_date*.
    :param duration_minutes: Session length in minutes (15–480).
    :param status: Current state — ``backlog``, ``planned``, ``doing``, ``done``, or ``cancelled``.
    :param description: What this session is about / intended focus.
    :param notes: Free-text notes recorded after completion.
    :param created_at: Row creation timestamp.
    :param completed_at: Timestamp when status transitioned to ``done``.
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
        """Return ``True`` if the session has been completed.

        :rtype: bool
        """
        return self.status == "done"

    def is_planned(self) -> bool:
        """Return ``True`` if the session is in a planned state.

        :rtype: bool
        """
        return self.status == "planned"

    def __str__(self) -> str:
        return f"Session({self.id}, project={self.project_id}, {self.scheduled_date}, {self.status})"
