"""Row-to-domain mapping helpers.

Centralizes conversion from :class:`sqlite3.Row` to domain dataclasses so SQL,
cursors, and rows never escape the infrastructure layer.
"""

import sqlite3
from datetime import date, datetime

from portfolio_manager.domain.models import (
    Milestone,
    Project,
    ProjectScore,
    Session,
    WeeklyReview,
)


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def row_to_project(row: sqlite3.Row) -> Project:
    """Map a ``project`` row to a :class:`Project`.

    :rtype: Project
    """
    keys = row.keys()
    return Project(
        id=row["id"],
        name=row["name"],
        slug=row["slug"],
        status=row["status"],
        priority=row["priority"],
        started_date=_date(row["started_date"]),
        end_date=_date(row["end_date"]) if "end_date" in keys else None,
        owner=row["owner"],
        review_cadence=row["review_cadence"],
        plan_content=row["plan_content"],
        description=row["description"],
        created_at=_dt(row["created_at"]),
        updated_at=_dt(row["updated_at"]),
    )


def row_to_session(row: sqlite3.Row) -> Session:
    """Map a ``session`` row to a :class:`Session`.

    :rtype: Session
    """
    return Session(
        id=row["id"],
        project_id=row["project_id"],
        milestone_id=row["milestone_id"],
        scheduled_date=date.fromisoformat(row["scheduled_date"]),
        week_key=row["week_key"],
        duration_minutes=row["duration_minutes"],
        status=row["status"],
        description=row["description"],
        notes=row["notes"],
        created_at=_dt(row["created_at"]),
        completed_at=_dt(row["completed_at"]),
    )


def row_to_milestone(row: sqlite3.Row) -> Milestone:
    """Map a ``milestone`` row to a :class:`Milestone`.

    :rtype: Milestone
    """
    return Milestone(
        id=row["id"],
        project_id=row["project_id"],
        description=row["description"],
        status=row["status"],
        completed_date=_date(row["completed_date"]),
        target_date=_date(row["target_date"]),
        sort_order=row["sort_order"],
        notes=row["notes"],
        created_at=_dt(row["created_at"]),
        updated_at=_dt(row["updated_at"]),
    )


def row_to_score(row: sqlite3.Row) -> ProjectScore:
    """Map a ``project_score`` row to a :class:`ProjectScore`.

    :rtype: ProjectScore
    """
    return ProjectScore(
        id=row["id"],
        project_id=row["project_id"],
        week_key=row["week_key"],
        score=row["score"] if row["score"] is not None else 0,
        status=row["status"] if row["status"] else "red",
        status_note=row["status_note"],
        is_manual_override=bool(row["is_manual_override"]),
        override_reason=row["override_reason"],
        created_at=_dt(row["created_at"]),
    )


def row_to_review(row: sqlite3.Row) -> WeeklyReview:
    """Map a ``weekly_review`` row to a :class:`WeeklyReview`.

    :rtype: WeeklyReview
    """
    return WeeklyReview(
        id=row["id"],
        week_key=row["week_key"],
        date_from=_date(row["date_from"]),
        date_to=_date(row["date_to"]),
        hours_invested=row["hours_invested"] or 0.0,
        sessions_completed=row["sessions_completed"] or 0,
        what_moved=row["what_moved"],
        what_stalled=row["what_stalled"],
        signals=row["signals"],
        decision_next_week=row["decision_next_week"],
        primary_focus=row["primary_focus"],
        project_to_deprioritize=row["project_to_deprioritize"],
        risk_to_watch=row["risk_to_watch"],
        first_session_target=row["first_session_target"],
        written_to_repo=bool(row["written_to_repo"]),
        created_at=_dt(row["created_at"]),
        updated_at=_dt(row["updated_at"]),
    )
