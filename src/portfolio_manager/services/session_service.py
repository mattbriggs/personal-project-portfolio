"""Business logic for session lifecycle management."""

import logging
from datetime import date, datetime

from portfolio_manager.events.event_bus import (
    SESSION_COMPLETED,
    SESSION_CREATED,
    SESSION_DELETED,
    SESSION_UPDATED,
    EventBus,
)
from portfolio_manager.exceptions import ValidationError
from portfolio_manager.models.session import Session, SessionStatus
from portfolio_manager.repositories.session_repo import SessionRepository
from portfolio_manager.utils.date_utils import to_week_key

logger = logging.getLogger(__name__)

_VALID_STATUSES: set[str] = {"backlog", "planned", "doing", "done", "cancelled"}
_MIN_DURATION = 15
_MAX_DURATION = 480


class SessionService:
    """Manages session creation, status transitions, and deletion.

    :param session_repo: Repository for session persistence.
    :param bus: Event bus for notifying subscribers of state changes.
    """

    def __init__(
        self,
        session_repo: SessionRepository,
        bus: EventBus | None = None,
    ) -> None:
        self._sessions = session_repo
        self._bus = bus or EventBus.get()

    def create_session(
        self,
        project_id: int,
        scheduled_date: date,
        duration_minutes: int = 90,
        description: str = "",
        notes: str = "",
        milestone_id: int | None = None,
        status: SessionStatus = "backlog",
    ) -> Session:
        """Create and persist a new session.

        :param project_id: Parent project's primary key.
        :param scheduled_date: The date to schedule the session.
        :param duration_minutes: Session length in minutes (15–480).
        :param description: What this session is about.
        :param notes: Free-text notes for the session.
        :param milestone_id: Optional associated milestone primary key.
        :param status: Initial status (default ``backlog``).
        :raises ValidationError: If *duration_minutes* is out of range.
        :rtype: Session
        """
        if not _MIN_DURATION <= duration_minutes <= _MAX_DURATION:
            raise ValidationError(
                f"Session duration must be {_MIN_DURATION}–{_MAX_DURATION} minutes "
                f"(got {duration_minutes})."
            )
        session = Session(
            project_id=project_id,
            milestone_id=milestone_id,
            scheduled_date=scheduled_date,
            week_key=to_week_key(scheduled_date),
            duration_minutes=duration_minutes,
            status=status,
            description=description,
            notes=notes,
        )
        session = self._sessions.create(session)
        self._bus.emit(SESSION_CREATED, session_id=session.id, project_id=project_id)
        logger.info(
            "Created session %d for project %d on %s",
            session.id,
            project_id,
            scheduled_date,
        )
        return session

    def set_status(self, session_id: int, status: SessionStatus) -> Session:
        """Set the status of a session to any valid value.

        Automatically sets ``completed_at`` when transitioning to ``done``
        and clears it when leaving ``done``.

        :param session_id: Target session primary key.
        :param status: New status value.
        :raises ValidationError: If *status* is not a recognised value.
        :rtype: Session
        """
        if status not in _VALID_STATUSES:
            raise ValidationError(
                f"Invalid session status {status!r}. "
                f"Valid values: {sorted(_VALID_STATUSES)}"
            )
        session = self._sessions.get(session_id)
        session.status = status
        if status == "done" and session.completed_at is None:
            session.completed_at = datetime.utcnow()
        elif status != "done":
            session.completed_at = None
        updated = self._sessions.update(session)
        event = SESSION_COMPLETED if status == "done" else SESSION_UPDATED
        self._bus.emit(event, session_id=session_id, project_id=session.project_id)
        logger.info("Session %d → %s", session_id, status)
        return updated

    # ------------------------------------------------------------------
    # Convenience wrappers kept for compatibility
    # ------------------------------------------------------------------

    def update_session(self, session: Session) -> Session:
        """Persist all editable fields of a session.

        Recomputes ``week_key`` from ``scheduled_date`` and manages
        ``completed_at`` based on status.

        :param session: Session with updated fields (must have a valid ``id``).
        :raises ValidationError: If *duration_minutes* is out of range.
        :rtype: Session
        """
        if not _MIN_DURATION <= session.duration_minutes <= _MAX_DURATION:
            raise ValidationError(
                f"Session duration must be {_MIN_DURATION}–{_MAX_DURATION} minutes "
                f"(got {session.duration_minutes})."
            )
        session.week_key = to_week_key(session.scheduled_date)
        if session.status == "done" and session.completed_at is None:
            session.completed_at = datetime.utcnow()
        elif session.status != "done":
            session.completed_at = None
        updated = self._sessions.update(session)
        self._bus.emit(SESSION_UPDATED, session_id=session.id, project_id=session.project_id)
        logger.info("Updated session %d", session.id)
        return updated

    def complete_session(self, session_id: int, notes: str = "", description: str = "") -> Session:
        """Mark a session as ``done``."""
        if notes or description:
            session = self._sessions.get(session_id)
            if notes:
                session.notes = notes
            if description:
                session.description = description
            self._sessions.update(session)
        return self.set_status(session_id, "done")

    def cancel_session(self, session_id: int) -> Session:
        """Mark a session as ``cancelled``."""
        return self.set_status(session_id, "cancelled")

    def reschedule_session(self, session_id: int, new_date: date) -> Session:
        """Move a session to a different date and recalculate its week key.

        :param session_id: Target session's primary key.
        :param new_date: New scheduled date.
        :rtype: Session
        """
        session = self._sessions.get(session_id)
        session.scheduled_date = new_date
        session.week_key = to_week_key(new_date)
        updated = self._sessions.update(session)
        self._bus.emit(SESSION_UPDATED, session_id=session_id, project_id=session.project_id)
        logger.info("Rescheduled session %d to %s", session_id, new_date)
        return updated

    def delete_session(self, session_id: int) -> None:
        """Delete a session permanently.

        :param session_id: Primary key of the session to delete.
        """
        session = self._sessions.get(session_id)
        self._sessions.delete(session_id)
        self._bus.emit(SESSION_DELETED, session_id=session_id, project_id=session.project_id)
        logger.info("Deleted session %d", session_id)

    def get_sessions_for_week(self, week_key: str) -> list[Session]:
        """Return all sessions across all projects for a given week.

        :rtype: list[Session]
        """
        return self._sessions.list_for_week(week_key)

    def get_sessions_for_project(
        self,
        project_id: int,
        week_key: str | None = None,
    ) -> list[Session]:
        """Return sessions for a specific project, optionally filtered by week.

        :rtype: list[Session]
        """
        return self._sessions.list_for_project(project_id, week_key=week_key)
