"""Session lifecycle service.

Ported from the original ``services/session_service.py``. Adds SRS-required
validation that new/updated sessions reference a non-archived project and that a
supplied ``milestone_id`` belongs to the same project. ``week_key`` is always
derived from ``scheduled_date`` and can never be supplied by the client.
"""

import logging
from datetime import date

from portfolio_manager.application.ports.clock import Clock
from portfolio_manager.application.ports.milestone_repository import MilestoneRepository
from portfolio_manager.application.ports.project_repository import ProjectRepository
from portfolio_manager.application.ports.session_repository import SessionRepository
from portfolio_manager.domain.enums import SESSION_STATUSES, SessionStatus
from portfolio_manager.domain.errors import ArchivedProjectError, ValidationError
from portfolio_manager.domain.models import Session
from portfolio_manager.domain.week import to_week_key
from portfolio_manager.infrastructure.system.clock import SystemClock

logger = logging.getLogger(__name__)

_MIN_DURATION = 15
_MAX_DURATION = 480


class SessionService:
    """Coordinate session creation, transitions, rescheduling, and deletion.

    :param sessions: Session repository port.
    :param projects: Project repository port (used to reject archived projects).
    :param milestones: Milestone repository port (used to validate ``milestone_id``).
    :param clock: Clock for completion timestamps. Defaults to the system clock.
    """

    def __init__(
        self,
        sessions: SessionRepository,
        projects: ProjectRepository,
        milestones: MilestoneRepository,
        clock: Clock | None = None,
    ) -> None:
        self._sessions = sessions
        self._projects = projects
        self._milestones = milestones
        self._clock: Clock = clock or SystemClock()

    def _validate_duration(self, minutes: int) -> None:
        if not _MIN_DURATION <= minutes <= _MAX_DURATION:
            raise ValidationError(
                f"Session duration must be {_MIN_DURATION}–{_MAX_DURATION} minutes (got {minutes})."
            )

    def _require_active_project(self, project_id: int) -> None:
        project = self._projects.get(project_id)  # raises NotFoundError
        if project.is_archived():
            raise ArchivedProjectError(
                f"Project {project_id} is archived; sessions cannot be modified."
            )

    def _validate_milestone(self, project_id: int, milestone_id: int | None) -> None:
        if milestone_id is None:
            return
        milestone = self._milestones.get(milestone_id)  # raises NotFoundError
        if milestone.project_id != project_id:
            raise ValidationError(
                f"Milestone {milestone_id} does not belong to project {project_id}."
            )

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

        :param project_id: Owning project (must exist and not be archived).
        :param scheduled_date: Scheduled date (week key derived from it).
        :param duration_minutes: 15–480 minutes.
        :param description: What the session is about.
        :param notes: Free-text notes.
        :param milestone_id: Optional milestone (must belong to the project).
        :param status: Initial status.
        :returns: The persisted session.
        :rtype: Session
        :raises ValidationError: On invalid duration/status/milestone.
        :raises NotFoundError: If the project or milestone does not exist.
        :raises ArchivedProjectError: If the project is archived.
        """
        self._validate_duration(duration_minutes)
        if status not in SESSION_STATUSES:
            raise ValidationError(f"Invalid session status {status!r}.")
        self._require_active_project(project_id)
        self._validate_milestone(project_id, milestone_id)

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
        logger.info("Created session %d for project %d", session.id, project_id)
        return session

    def set_status(self, session_id: int, status: SessionStatus) -> Session:
        """Set a session's status, managing ``completed_at``.

        Entering ``done`` sets ``completed_at``; leaving ``done`` clears it.

        :param session_id: Target session.
        :param status: New status.
        :returns: The updated session.
        :rtype: Session
        :raises ValidationError: If *status* is not recognised.
        :raises NotFoundError: If the session does not exist.
        """
        if status not in SESSION_STATUSES:
            raise ValidationError(f"Invalid session status {status!r}.")
        session = self._sessions.get(session_id)
        session.status = status
        if status == "done" and session.completed_at is None:
            session.completed_at = self._clock.now()
        elif status != "done":
            session.completed_at = None
        updated = self._sessions.update(session)
        logger.info("Session %d -> %s", session_id, status)
        return updated

    def update_session(self, session: Session) -> Session:
        """Persist all editable fields, re-deriving ``week_key``.

        :param session: Session with updated fields (valid ``id`` required).
        :returns: The updated session.
        :rtype: Session
        :raises ValidationError: On invalid duration/milestone.
        :raises NotFoundError: If the referenced project/milestone is missing.
        :raises ArchivedProjectError: If the project is archived.
        """
        self._validate_duration(session.duration_minutes)
        self._require_active_project(session.project_id)
        self._validate_milestone(session.project_id, session.milestone_id)
        session.week_key = to_week_key(session.scheduled_date)
        if session.status == "done" and session.completed_at is None:
            session.completed_at = self._clock.now()
        elif session.status != "done":
            session.completed_at = None
        updated = self._sessions.update(session)
        logger.info("Updated session %d", session.id)
        return updated

    def reschedule_session(self, session_id: int, new_date: date) -> Session:
        """Move a session to a new date and recompute its week key.

        :param session_id: Target session.
        :param new_date: New scheduled date.
        :returns: The updated session.
        :rtype: Session
        :raises NotFoundError: If the session does not exist.
        """
        session = self._sessions.get(session_id)
        session.scheduled_date = new_date
        session.week_key = to_week_key(new_date)
        updated = self._sessions.update(session)
        logger.info("Rescheduled session %d to %s", session_id, new_date)
        return updated

    def delete_session(self, session_id: int) -> None:
        """Delete a session permanently.

        :param session_id: Target session.
        :raises NotFoundError: If the session does not exist.
        """
        self._sessions.get(session_id)
        self._sessions.delete(session_id)
        logger.info("Deleted session %d", session_id)

    def get_session(self, session_id: int) -> Session:
        """Fetch a session by primary key.

        :raises NotFoundError: If the session does not exist.
        :rtype: Session
        """
        return self._sessions.get(session_id)

    def get_sessions_for_week(self, week_key: str) -> list[Session]:
        """Return all sessions for a week across projects.

        :rtype: list[Session]
        """
        return self._sessions.list_for_week(week_key)

    def get_sessions_for_project(
        self, project_id: int, week_key: str | None = None
    ) -> list[Session]:
        """Return sessions for a project, optionally filtered by week.

        :rtype: list[Session]
        """
        return self._sessions.list_for_project(project_id, week_key=week_key)
