"""Domain model for a project's weekly score record."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from portfolio_manager.utils.date_utils import utcnow

ScoreStatus = Literal["green", "yellow", "red"]


@dataclass
class ProjectScore:
    """Represents a computed (or manually overridden) project score for one week.

    :param id: Database primary key (0 for unsaved instances).
    :param project_id: Foreign key to the scored project.
    :param week_key: ISO week key in ``YYYY.W`` format.
    :param score: Integer score in range 0–100.
    :param status: Traffic-light status — ``green``, ``yellow``, or ``red``.
    :param status_note: Human-readable note explaining the status.
    :param is_manual_override: Whether the score/status was set by the user.
    :param override_reason: Required explanation when *is_manual_override* is ``True``.
    :param created_at: Row creation timestamp.
    """

    id: int = 0
    project_id: int = 0
    week_key: str = ""
    score: int = 0
    status: ScoreStatus = "red"
    status_note: str = ""
    is_manual_override: bool = False
    override_reason: str = ""
    created_at: datetime = field(default_factory=utcnow)

    def __str__(self) -> str:
        flag = " [manual]" if self.is_manual_override else ""
        return f"ProjectScore({self.project_id}, {self.week_key}, {self.score}, {self.status}{flag})"
