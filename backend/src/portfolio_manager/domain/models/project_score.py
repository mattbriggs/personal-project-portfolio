"""Domain model for a project's weekly score record."""

from dataclasses import dataclass, field
from datetime import datetime

from portfolio_manager.domain.enums import ScoreStatus
from portfolio_manager.domain.models._time import utcnow


@dataclass
class ProjectScore:
    """A computed (or manually overridden) project score for one week.

    :param id: Primary key (0 for unsaved instances).
    :param project_id: Scored project's primary key.
    :param week_key: ISO ``YYYY.W`` key.
    :param score: Integer score 0–100.
    :param status: ``green``, ``yellow``, or ``red``.
    :param status_note: Human-readable status note.
    :param is_manual_override: Whether score/status were set by the user.
    :param override_reason: Required explanation when *is_manual_override*.
    :param created_at: Creation timestamp.
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
