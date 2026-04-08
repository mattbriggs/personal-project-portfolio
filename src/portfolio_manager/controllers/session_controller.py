"""Controller for the session management view."""

import logging
from datetime import date

from portfolio_manager.models.session import Session
from portfolio_manager.services.session_service import SessionService
from portfolio_manager.services.week_service import WeekService

logger = logging.getLogger(__name__)


class SessionController:
    """Mediates between the session view and session service.

    :param session_service: Service for session lifecycle operations.
    :param week_service: Service for week-key computation.
    """

    def __init__(
        self,
        session_service: SessionService,
        week_service: WeekService,
    ) -> None:
        self._sessions = session_service
        self._weeks = week_service

    def get_week_sessions(self, week_key: str | None = None) -> list[Session]:
        """Return all sessions for a given week (defaults to current week).

        :param week_key: Week in ``YYYY.W`` format; uses current week if ``None``.
        :rtype: list[Session]
        """
        wk = week_key or self._weeks.current_week_key()
        return self._sessions.get_sessions_for_week(wk)

    def get_project_sessions(
        self, project_id: int, week_key: str | None = None
    ) -> list[Session]:
        """Return sessions for a project, optionally filtered by week.

        :param project_id: Target project.
        :param week_key: Optional week filter.
        :rtype: list[Session]
        """
        return self._sessions.get_sessions_for_project(project_id, week_key=week_key)

    def create_session(
        self,
        project_id: int,
        scheduled_date: date,
        duration_minutes: int = 90,
        focus: str = "",
    ) -> Session:
        """Create a planned session.

        :param project_id: Parent project.
        :param scheduled_date: Date for the session.
        :param duration_minutes: Session length (60–180).
        :param focus: Optional focus description.
        :rtype: Session
        """
        return self._sessions.create_session(
            project_id, scheduled_date, duration_minutes, focus
        )

    def complete_session(
        self, session_id: int, notes: str = "", focus: str = ""
    ) -> Session:
        """Mark a session as completed.

        :param session_id: Target session.
        :param notes: Optional completion notes.
        :param focus: Optional focus description.
        :rtype: Session
        """
        return self._sessions.complete_session(session_id, notes=notes, focus=focus)

    def reschedule_session(self, session_id: int, new_date: date) -> Session:
        """Reschedule a planned session.

        :param session_id: Target session.
        :param new_date: New scheduled date.
        :rtype: Session
        """
        return self._sessions.reschedule_session(session_id, new_date)

    def cancel_session(self, session_id: int) -> Session:
        """Cancel a planned session.

        :param session_id: Target session.
        :rtype: Session
        """
        return self._sessions.cancel_session(session_id)

    def delete_session(self, session_id: int) -> None:
        """Delete a session permanently.

        :param session_id: Target session.
        """
        self._sessions.delete_session(session_id)
