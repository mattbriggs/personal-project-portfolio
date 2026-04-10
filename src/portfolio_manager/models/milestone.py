"""Domain model for a project milestone."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal

from portfolio_manager.utils.date_utils import utcnow

MilestoneStatus = Literal["backlog", "planned", "doing", "done", "cancelled"]


@dataclass
class Milestone:
    """Represents an outcome-based milestone within a project.

    :param id: Database primary key (0 for unsaved instances).
    :param project_id: Foreign key to the owning project.
    :param description: Outcome-based milestone description.
    :param status: Lifecycle state — ``backlog``, ``planned``, ``doing``, ``done``,
        or ``cancelled``.
    :param completed_date: Date the milestone was marked ``done``.
    :param target_date: Optional target/due date for the milestone.
    :param sort_order: Display order within the project's milestone list.
    :param notes: Free-text notes about this milestone.
    :param created_at: Row creation timestamp.
    :param updated_at: Last modification timestamp.
    """

    id: int = 0
    project_id: int = 0
    description: str = ""
    status: MilestoneStatus = "backlog"
    completed_date: date | None = None
    target_date: date | None = None
    sort_order: int = 0
    notes: str = ""
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def is_done(self) -> bool:
        """Return ``True`` if the milestone has been completed.

        :rtype: bool
        """
        return self.status == "done"

    def __str__(self) -> str:
        return f"Milestone({self.id}, {self.status}, {self.description[:40]!r})"
