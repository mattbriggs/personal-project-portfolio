"""Controller for the session management view."""

import logging
from datetime import date

from portfolio_manager.models.milestone import Milestone
from portfolio_manager.models.session import Session, SessionStatus
from portfolio_manager.repositories.milestone_repo import MilestoneRepository
from portfolio_manager.services.session_service import SessionService
from portfolio_manager.services.week_service import WeekService

logger = logging.getLogger(__name__)


class SessionController:
    """Mediates between the session view and session service.

    :param session_service: Service for session lifecycle operations.
    :param week_service: Service for week-key computation.
    :param milestone_repo: Repository used to populate the milestone dropdown.
    :param default_duration_minutes: Default session length pulled from settings.
    """

    def __init__(
        self,
        session_service: SessionService,
        week_service: WeekService,
        milestone_repo: MilestoneRepository | None = None,
        default_duration_minutes: int = 90,
    ) -> None:
        self._sessions = session_service
        self._weeks = week_service
        self._milestones = milestone_repo
        self.default_duration_minutes = default_duration_minutes

    def get_week_sessions(self, week_key: str | None = None) -> list[Session]:
        """Return all sessions for a given week (defaults to current week).

        :rtype: list[Session]
        """
        wk = week_key or self._weeks.current_week_key()
        return self._sessions.get_sessions_for_week(wk)

    def get_project_sessions(
        self, project_id: int, week_key: str | None = None
    ) -> list[Session]:
        """Return sessions for a project, optionally filtered by week.

        :rtype: list[Session]
        """
        return self._sessions.get_sessions_for_project(project_id, week_key=week_key)

    def get_milestones_for_project(self, project_id: int) -> list[Milestone]:
        """Return active milestones for a project for the milestone dropdown.

        Returns an empty list if no milestone repository was provided.

        :rtype: list[Milestone]
        """
        if self._milestones is None:
            return []
        return self._milestones.list_for_project(project_id)

    def create_session(
        self,
        project_id: int,
        scheduled_date: date,
        duration_minutes: int | None = None,
        description: str = "",
        notes: str = "",
        milestone_id: int | None = None,
        status: SessionStatus = "backlog",
    ) -> Session:
        """Create a planned session.

        :param project_id: Parent project.
        :param scheduled_date: Date for the session.
        :param duration_minutes: Session length; defaults to ``default_duration_minutes``.
        :param description: What this session is about.
        :param notes: Free-text notes for the session.
        :param milestone_id: Optional associated milestone.
        :param status: Initial status (default ``backlog``).
        :rtype: Session
        """
        if duration_minutes is None:
            duration_minutes = self.default_duration_minutes
        return self._sessions.create_session(
            project_id,
            scheduled_date,
            duration_minutes=duration_minutes,
            description=description,
            notes=notes,
            milestone_id=milestone_id,
            status=status,
        )

    def set_session_status(self, session_id: int, status: SessionStatus) -> Session:
        """Set the status of a session.

        :param session_id: Target session.
        :param status: New status value.
        :rtype: Session
        """
        return self._sessions.set_status(session_id, status)

    def update_session(self, session: Session) -> Session:
        """Persist all editable fields of an existing session.

        :param session: Modified session domain object.
        :rtype: Session
        """
        return self._sessions.update_session(session)

    def complete_session(self, session_id: int) -> Session:
        """Shortcut: mark a session as ``done``."""
        return self._sessions.set_status(session_id, "done")

    def cancel_session(self, session_id: int) -> Session:
        """Shortcut: mark a session as ``cancelled``."""
        return self._sessions.set_status(session_id, "cancelled")

    def reschedule_session(self, session_id: int, new_date: date) -> Session:
        """Reschedule a session to a new date.

        :rtype: Session
        """
        return self._sessions.reschedule_session(session_id, new_date)

    def delete_session(self, session_id: int) -> None:
        """Delete a session permanently."""
        self._sessions.delete_session(session_id)
