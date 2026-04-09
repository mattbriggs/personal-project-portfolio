"""Controller for the milestone tracking view."""

import logging
from datetime import date

from portfolio_manager.events.event_bus import MILESTONE_UPDATED, EventBus
from portfolio_manager.models.milestone import Milestone, MilestoneStatus
from portfolio_manager.repositories.milestone_repo import MilestoneRepository

logger = logging.getLogger(__name__)

_VALID_STATUSES: set[str] = {"backlog", "planned", "doing", "done", "cancelled"}


class MilestoneController:
    """Mediates between the milestone view and the milestone repository.

    :param milestone_repo: Repository for milestone persistence.
    :param bus: Event bus.
    """

    def __init__(
        self,
        milestone_repo: MilestoneRepository,
        bus: EventBus | None = None,
    ) -> None:
        self._milestones = milestone_repo
        self._bus = bus or EventBus.get()

    def count_milestones(self, project_id: int) -> tuple[int, int]:
        """Return ``(total, done)`` milestone counts for a project.

        :rtype: tuple[int, int]
        """
        return self._milestones.count(project_id)

    def list_milestones(self, project_id: int) -> list[Milestone]:
        """Return milestones for a project in sort order.

        :rtype: list[Milestone]
        """
        return self._milestones.list_for_project(project_id)

    def list_milestones_with_totals(
        self, project_id: int
    ) -> list[tuple[Milestone, int]]:
        """Return milestones paired with their total session minutes.

        :rtype: list[tuple[Milestone, int]]
        """
        return self._milestones.list_for_project_with_totals(project_id)

    def add_milestone(
        self,
        project_id: int,
        description: str,
        target_date: date | None = None,
        sort_order: int = 0,
        notes: str = "",
        status: MilestoneStatus = "backlog",
    ) -> Milestone:
        """Create a new milestone for a project.

        :param project_id: Parent project.
        :param description: Outcome description.
        :param target_date: Optional target completion date.
        :param sort_order: Display position.
        :param notes: Free-text notes.
        :param status: Initial status (default ``backlog``).
        :rtype: Milestone
        """
        ms = Milestone(
            project_id=project_id,
            description=description,
            target_date=target_date,
            sort_order=sort_order,
            notes=notes,
            status=status,
        )
        ms = self._milestones.create(ms)
        self._bus.emit(MILESTONE_UPDATED, project_id=project_id)
        return ms

    def update_milestone(
        self,
        milestone_id: int,
        description: str,
        target_date: date | None = None,
        notes: str = "",
    ) -> Milestone:
        """Update the description, target date, and notes of an existing milestone.

        :param milestone_id: Target milestone.
        :param description: New description text.
        :param target_date: New target date (``None`` clears it).
        :param notes: Free-text notes.
        :rtype: Milestone
        """
        ms = self._milestones.get(milestone_id)
        ms.description = description
        ms.target_date = target_date
        ms.notes = notes
        updated = self._milestones.update(ms)
        self._bus.emit(MILESTONE_UPDATED, project_id=ms.project_id)
        logger.info("Updated milestone %d", milestone_id)
        return updated

    def update_milestone_fields(
        self,
        milestone_id: int,
        description: str,
        target_date: date | None = None,
        notes: str = "",
        status: MilestoneStatus = "backlog",
    ) -> Milestone:
        """Update all editable fields of a milestone in a single operation.

        Manages ``completed_date`` automatically based on *status*.

        :param milestone_id: Target milestone.
        :param description: New description text.
        :param target_date: New target date (``None`` clears it).
        :param notes: Free-text notes.
        :param status: New status value.
        :rtype: Milestone
        """
        ms = self._milestones.get(milestone_id)
        ms.description = description
        ms.target_date = target_date
        ms.notes = notes
        ms.status = status
        if status == "done" and ms.completed_date is None:
            ms.completed_date = date.today()
        elif status != "done":
            ms.completed_date = None
        updated = self._milestones.update(ms)
        self._bus.emit(MILESTONE_UPDATED, project_id=ms.project_id)
        logger.info("Updated milestone %d → %s", milestone_id, status)
        return updated

    def set_milestone_status(
        self, milestone_id: int, status: MilestoneStatus
    ) -> Milestone:
        """Set the status of a milestone.

        Automatically sets ``completed_date`` when transitioning to ``done``
        and clears it when leaving ``done``.

        :param milestone_id: Target milestone.
        :param status: New status value.
        :rtype: Milestone
        """
        ms = self._milestones.get(milestone_id)
        ms.status = status
        if status == "done" and ms.completed_date is None:
            ms.completed_date = date.today()
        elif status != "done":
            ms.completed_date = None
        updated = self._milestones.update(ms)
        self._bus.emit(MILESTONE_UPDATED, project_id=ms.project_id)
        logger.info("Milestone %d → %s", milestone_id, status)
        return updated

    def delete_milestone(self, milestone_id: int) -> None:
        """Delete a milestone.

        :param milestone_id: Target milestone.
        """
        ms = self._milestones.get(milestone_id)
        self._milestones.delete(milestone_id)
        self._bus.emit(MILESTONE_UPDATED, project_id=ms.project_id)
        logger.info("Deleted milestone %d", milestone_id)
