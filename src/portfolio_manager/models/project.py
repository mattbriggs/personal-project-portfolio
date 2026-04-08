"""Domain model for a Portfolio Manager project."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal

ProjectStatus = Literal["active", "backlog", "archive"]


@dataclass
class Project:
    """Represents a single project in the portfolio.

    :param id: Database primary key (0 for unsaved instances).
    :param name: Human-readable project name.
    :param slug: URL-safe unique identifier (e.g. ``my-novel``).
    :param status: Lifecycle state — ``active``, ``backlog``, or ``archive``.
    :param priority: Priority 1 (highest) to 5 (lowest).
    :param started_date: Date work began, or ``None`` if not started.
    :param owner: Project owner name.
    :param review_cadence: How often the project is reviewed (e.g. ``weekly``).
    :param plan_content: Markdown text for the plan document.
    :param description: Free-text project description.
    :param created_at: Creation timestamp.
    :param updated_at: Last modification timestamp.
    """

    id: int = 0
    name: str = ""
    slug: str = ""
    status: ProjectStatus = "active"
    priority: int = 3
    started_date: date | None = None
    owner: str = "Matt Briggs"
    review_cadence: str = "weekly"
    plan_content: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def is_archived(self) -> bool:
        """Return ``True`` if the project is archived (read-only).

        :rtype: bool
        """
        return self.status == "archive"

    def __str__(self) -> str:
        return f"Project({self.id}, {self.name!r}, {self.status})"
