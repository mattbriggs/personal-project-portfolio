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
from portfolio_manager.exceptions import SessionStateError, ValidationError
from portfolio_manager.models.session import Session
from portfolio_manager.repositories.session_repo import SessionRepository
from portfolio_manager.utils.date_utils import to_week_key

logger = logging.getLogger(__name__)


class SessionService:
    """Manages session creation, completion, rescheduling, and deletion.

    :param session_repo: Repository for session persistence.
    :type session_repo: SessionRepository
    :param bus: Event bus for notifying subscribers of state changes.
    :type bus: EventBus
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
        focus: str = "",
    ) -> Session:
        """Create and persist a new planned session.

        :param project_id: Parent project's primary key.
        :type project_id: int
        :param scheduled_date: The date to schedule the session.
        :type scheduled_date: datetime.date
        :param duration_minutes: Session length — must be 60–180.
        :type duration_minutes: int
        :param focus: Brief focus description.
        :type focus: str
        :returns: The persisted :class:`~portfolio_manager.models.session.Session`.
        :rtype: Session
        :raises ValidationError: If *duration_minutes* is out of range.
        """
        if not 60 <= duration_minutes <= 180:
            raise ValidationError(
                f"Session duration must be 60–180 minutes (got {duration_minutes})."
            )
        session = Session(
            project_id=project_id,
            scheduled_date=scheduled_date,
            week_key=to_week_key(scheduled_date),
            duration_minutes=duration_minutes,
            status="planned",
            focus=focus,
        )
        session = self._sessions.create(session)
        self._bus.emit(SESSION_CREATED, session_id=session.id, project_id=project_id)
        logger.info(
            "Created session %d for project %d on %s",
            session.id, project_id, scheduled_date,
        )
        return session

    def complete_session(
        self,
        session_id: int,
        notes: str = "",
        focus: str = "",
    ) -> Session:
        """Mark a session as completed and record the completion timestamp.

        :param session_id: The primary key of the session to complete.
        :type session_id: int
        :param notes: Optional session notes to record.
        :type notes: str
        :param focus: Optional focus description for the session.
        :type focus: str
        :returns: The updated :class:`~portfolio_manager.models.session.Session`.
        :rtype: Session
        :raises SessionStateError: If the session is already completed or cancelled.
        """
        session = self._sessions.get(session_id)
        if session.status == "completed":
            raise SessionStateError(f"Session {session_id} is already completed.")
        if session.status == "cancelled":
            raise SessionStateError(
                f"Session {session_id} is cancelled — restore it before completing."
            )
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        if notes:
            session.notes = notes
        if focus:
            session.focus = focus
        updated = self._sessions.update(session)
        self._bus.emit(
            SESSION_COMPLETED, session_id=session_id, project_id=session.project_id
        )
        logger.info("Completed session %d", session_id)
        return updated

    def reschedule_session(self, session_id: int, new_date: date) -> Session:
        """Move a planned session to a different date.

        Updates the ``week_key`` to match the new date.

        :param session_id: Target session's primary key.
        :type session_id: int
        :param new_date: New scheduled date.
        :type new_date: datetime.date
        :returns: The rescheduled :class:`~portfolio_manager.models.session.Session`.
        :rtype: Session
        :raises SessionStateError: If the session is not in ``planned`` state.
        """
        session = self._sessions.get(session_id)
        if session.status != "planned":
            raise SessionStateError(
                f"Only planned sessions can be rescheduled (current: {session.status})."
            )
        session.scheduled_date = new_date
        session.week_key = to_week_key(new_date)
        updated = self._sessions.update(session)
        self._bus.emit(SESSION_UPDATED, session_id=session_id, project_id=session.project_id)
        logger.info("Rescheduled session %d to %s", session_id, new_date)
        return updated

    def cancel_session(self, session_id: int) -> Session:
        """Mark a planned session as cancelled.

        :param session_id: Target session's primary key.
        :type session_id: int
        :returns: The updated :class:`~portfolio_manager.models.session.Session`.
        :rtype: Session
        :raises SessionStateError: If the session is not in ``planned`` state.
        """
        session = self._sessions.get(session_id)
        if session.status != "planned":
            raise SessionStateError(
                f"Only planned sessions can be cancelled (current: {session.status})."
            )
        session.status = "cancelled"
        updated = self._sessions.update(session)
        self._bus.emit(SESSION_UPDATED, session_id=session_id, project_id=session.project_id)
        logger.info("Cancelled session %d", session_id)
        return updated

    def reopen_session(self, session_id: int) -> Session:
        """Restore a completed or cancelled session to ``planned`` state.

        :param session_id: Target session's primary key.
        :type session_id: int
        :returns: The restored :class:`~portfolio_manager.models.session.Session`.
        :rtype: Session
        """
        session = self._sessions.get(session_id)
        session.status = "planned"
        session.completed_at = None
        updated = self._sessions.update(session)
        self._bus.emit(SESSION_UPDATED, session_id=session_id, project_id=session.project_id)
        logger.info("Reopened session %d", session_id)
        return updated

    def delete_session(self, session_id: int) -> None:
        """Delete a session permanently.

        :param session_id: Primary key of the session to delete.
        :type session_id: int
        """
        session = self._sessions.get(session_id)
        self._sessions.delete(session_id)
        self._bus.emit(SESSION_DELETED, session_id=session_id, project_id=session.project_id)
        logger.info("Deleted session %d", session_id)

    def get_sessions_for_week(self, week_key: str) -> list[Session]:
        """Return all sessions across all projects for a given week.

        :param week_key: Target week in ``YYYY.W`` format.
        :type week_key: str
        :rtype: list[Session]
        """
        return self._sessions.list_for_week(week_key)

    def get_sessions_for_project(
        self,
        project_id: int,
        week_key: str | None = None,
    ) -> list[Session]:
        """Return sessions for a specific project, optionally filtered by week.

        :param project_id: Target project.
        :param week_key: Optional week filter.
        :rtype: list[Session]
        """
        return self._sessions.list_for_project(project_id, week_key=week_key)
