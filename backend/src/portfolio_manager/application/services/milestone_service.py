"""Milestone lifecycle service.

Consolidates milestone behavior that lived in the Tkinter milestone controller.
Enforces SRS rules: mutation requires a non-archived project, description is
required, entering ``done`` sets ``completed_date`` (cleared on leaving), and
listing is deterministic by ``sort_order`` then id.
"""

import logging

from portfolio_manager.application.ports.clock import Clock
from portfolio_manager.application.ports.milestone_repository import MilestoneRepository
from portfolio_manager.application.ports.project_repository import ProjectRepository
from portfolio_manager.domain.enums import MILESTONE_STATUSES, MilestoneStatus
from portfolio_manager.domain.errors import ArchivedProjectError, ValidationError
from portfolio_manager.domain.models import Milestone
from portfolio_manager.infrastructure.system.clock import SystemClock

logger = logging.getLogger(__name__)


class MilestoneService:
    """Coordinate milestone creation, transitions, sorting, and deletion.

    :param milestones: Milestone repository port.
    :param projects: Project repository port (used to reject archived projects).
    :param clock: Clock for completion dates. Defaults to the system clock.
    """

    def __init__(
        self,
        milestones: MilestoneRepository,
        projects: ProjectRepository,
        clock: Clock | None = None,
    ) -> None:
        self._milestones = milestones
        self._projects = projects
        self._clock: Clock = clock or SystemClock()

    def _require_active_project(self, project_id: int) -> None:
        project = self._projects.get(project_id)  # raises NotFoundError
        if project.is_archived():
            raise ArchivedProjectError(
                f"Project {project_id} is archived; milestones cannot be modified."
            )

    def create_milestone(
        self,
        project_id: int,
        description: str,
        status: MilestoneStatus = "backlog",
        target_date=None,
        sort_order: int = 0,
        notes: str = "",
    ) -> Milestone:
        """Create and persist a milestone.

        :param project_id: Owning project (must exist and not be archived).
        :param description: Required outcome description.
        :param status: Initial status.
        :param target_date: Optional target date.
        :param sort_order: Display order.
        :param notes: Free-text notes.
        :returns: The persisted milestone.
        :rtype: Milestone
        :raises ValidationError: If *description* is empty or *status* invalid.
        :raises NotFoundError: If the project does not exist.
        :raises ArchivedProjectError: If the project is archived.
        """
        description = description.strip()
        if not description:
            raise ValidationError("Milestone description must not be empty.")
        if status not in MILESTONE_STATUSES:
            raise ValidationError(f"Invalid milestone status {status!r}.")
        self._require_active_project(project_id)

        milestone = Milestone(
            project_id=project_id,
            description=description,
            status=status,
            target_date=target_date,
            sort_order=sort_order,
            notes=notes,
        )
        if status == "done":
            milestone.completed_date = self._clock.today()
        milestone = self._milestones.create(milestone)
        logger.info("Created milestone %d for project %d", milestone.id, project_id)
        return milestone

    def update_milestone(self, milestone: Milestone) -> Milestone:
        """Persist edits to a milestone, managing ``completed_date``.

        :param milestone: Milestone with updated fields (valid ``id`` required).
        :returns: The updated milestone.
        :rtype: Milestone
        :raises ValidationError: If description empty or status invalid.
        :raises ArchivedProjectError: If the project is archived.
        """
        if not milestone.description.strip():
            raise ValidationError("Milestone description must not be empty.")
        if milestone.status not in MILESTONE_STATUSES:
            raise ValidationError(f"Invalid milestone status {milestone.status!r}.")
        self._require_active_project(milestone.project_id)
        if milestone.status == "done" and milestone.completed_date is None:
            milestone.completed_date = self._clock.today()
        elif milestone.status != "done":
            milestone.completed_date = None
        updated = self._milestones.update(milestone)
        logger.info("Updated milestone %d", milestone.id)
        return updated

    def set_status(self, milestone_id: int, status: MilestoneStatus) -> Milestone:
        """Set a milestone's status, managing ``completed_date``.

        :param milestone_id: Target milestone.
        :param status: New status.
        :returns: The updated milestone.
        :rtype: Milestone
        :raises ValidationError: If *status* is not recognised.
        :raises NotFoundError: If the milestone does not exist.
        """
        if status not in MILESTONE_STATUSES:
            raise ValidationError(f"Invalid milestone status {status!r}.")
        milestone = self._milestones.get(milestone_id)
        milestone.status = status
        if status == "done" and milestone.completed_date is None:
            milestone.completed_date = self._clock.today()
        elif status != "done":
            milestone.completed_date = None
        updated = self._milestones.update(milestone)
        logger.info("Milestone %d -> %s", milestone_id, status)
        return updated

    def delete_milestone(self, milestone_id: int) -> None:
        """Delete a milestone permanently.

        :raises NotFoundError: If the milestone does not exist.
        """
        self._milestones.get(milestone_id)
        self._milestones.delete(milestone_id)
        logger.info("Deleted milestone %d", milestone_id)

    def get_milestone(self, milestone_id: int) -> Milestone:
        """Fetch a milestone by primary key.

        :raises NotFoundError: If the milestone does not exist.
        :rtype: Milestone
        """
        return self._milestones.get(milestone_id)

    def list_for_project(self, project_id: int) -> list[tuple[Milestone, int]]:
        """Return ``(milestone, total_session_minutes)`` pairs, ordered.

        :rtype: list[tuple[Milestone, int]]
        """
        return self._milestones.list_for_project_with_totals(project_id)
