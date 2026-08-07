"""Domain model for a project milestone."""

from dataclasses import dataclass, field
from datetime import date, datetime

from portfolio_manager.domain.enums import MilestoneStatus
from portfolio_manager.domain.models._time import utcnow


@dataclass
class Milestone:
    """An outcome-based milestone within a project.

    :param id: Primary key (0 for unsaved instances).
    :param project_id: Owning project's primary key.
    :param description: Outcome-based milestone description.
    :param status: ``backlog``, ``planned``, ``doing``, ``done``, or ``cancelled``.
    :param completed_date: Date the milestone was marked ``done``.
    :param target_date: Optional target/due date.
    :param sort_order: Display order within the project's milestone list.
    :param notes: Free-text notes.
    :param created_at: Creation timestamp.
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
        """Return ``True`` if the milestone is completed.

        :rtype: bool
        """
        return self.status == "done"
