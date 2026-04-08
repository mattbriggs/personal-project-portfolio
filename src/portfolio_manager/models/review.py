"""Domain model for a weekly review record."""

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class WeeklyReview:
    """Represents a structured weekly review for a single week.

    :param id: Database primary key (0 for unsaved instances).
    :param week_key: ISO week key in ``YYYY.W`` format.
    :param date_from: Monday of the week.
    :param date_to: Sunday of the week.
    :param hours_invested: Actual hours spent on portfolio work.
    :param sessions_completed: Count of sessions completed in the week.
    :param what_moved: What made meaningful progress.
    :param what_stalled: What did not advance as expected.
    :param signals: Signals or patterns noticed this week.
    :param decision_next_week: Key decision to apply next week.
    :param primary_focus: The single project to prioritise next week.
    :param project_to_deprioritize: Project to intentionally slow down.
    :param risk_to_watch: Risk or blocker to monitor.
    :param first_session_target: The very first session planned for next week.
    :param written_to_repo: Whether the review was exported to the repo.
    :param created_at: Row creation timestamp.
    :param updated_at: Last modification timestamp.
    """

    id: int = 0
    week_key: str = ""
    date_from: date | None = None
    date_to: date | None = None
    hours_invested: float = 0.0
    sessions_completed: int = 0
    what_moved: str = ""
    what_stalled: str = ""
    signals: str = ""
    decision_next_week: str = ""
    primary_focus: str = ""
    project_to_deprioritize: str = ""
    risk_to_watch: str = ""
    first_session_target: str = ""
    written_to_repo: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        return f"WeeklyReview({self.week_key})"
