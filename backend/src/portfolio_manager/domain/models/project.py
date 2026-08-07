"""Domain model for a portfolio project."""

from dataclasses import dataclass, field
from datetime import date, datetime

from portfolio_manager.domain.enums import ProjectStatus
from portfolio_manager.domain.models._time import utcnow


@dataclass
class Project:
    """A single project in the portfolio.

    :param id: Primary key (0 for unsaved instances).
    :param name: Human-readable project name.
    :param slug: URL-safe unique identifier.
    :param status: ``active``, ``backlog``, or ``archive``.
    :param priority: Priority 1 (highest) to 5 (lowest).
    :param started_date: Date work began, or ``None``.
    :param end_date: Optional end date.
    :param owner: Project owner name.
    :param review_cadence: How often the project is reviewed.
    :param plan_content: Markdown plan document text.
    :param description: Free-text description.
    :param created_at: Creation timestamp.
    :param updated_at: Last modification timestamp.
    """

    id: int = 0
    name: str = ""
    slug: str = ""
    status: ProjectStatus = "active"
    priority: int = 3
    started_date: date | None = None
    end_date: date | None = None
    owner: str = "Matt Briggs"
    review_cadence: str = "weekly"
    plan_content: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def is_archived(self) -> bool:
        """Return ``True`` if the project is archived (read-only).

        :rtype: bool
        """
        return self.status == "archive"
