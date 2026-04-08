"""Domain model for a project milestone."""

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Milestone:
    """Represents an outcome-based milestone within a project.

    :param id: Database primary key (0 for unsaved instances).
    :param project_id: Foreign key to the owning project.
    :param description: Outcome-based milestone description.
    :param is_complete: Whether the milestone has been achieved.
    :param completed_date: Date the milestone was marked complete.
    :param sort_order: Display order within the project's milestone list.
    :param created_at: Row creation timestamp.
    :param updated_at: Last modification timestamp.
    """

    id: int = 0
    project_id: int = 0
    description: str = ""
    is_complete: bool = False
    completed_date: date | None = None
    sort_order: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def toggle(self) -> None:
        """Toggle the completion state and set or clear *completed_date*.

        Sets ``completed_date`` to today when marking complete; clears it when
        marking incomplete.
        """
        self.is_complete = not self.is_complete
        self.completed_date = date.today() if self.is_complete else None

    def __str__(self) -> str:
        status = "done" if self.is_complete else "open"
        return f"Milestone({self.id}, {status}, {self.description[:40]!r})"
