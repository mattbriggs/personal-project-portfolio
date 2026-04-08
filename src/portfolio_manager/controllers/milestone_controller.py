"""Controller for the milestone tracking view."""

import logging

from portfolio_manager.events.event_bus import MILESTONE_UPDATED, EventBus
from portfolio_manager.models.milestone import Milestone
from portfolio_manager.repositories.milestone_repo import MilestoneRepository

logger = logging.getLogger(__name__)


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

    def list_milestones(self, project_id: int) -> list[Milestone]:
        """Return milestones for a project in sort order.

        :param project_id: Target project.
        :rtype: list[Milestone]
        """
        return self._milestones.list_for_project(project_id)

    def add_milestone(self, project_id: int, description: str, sort_order: int = 0) -> Milestone:
        """Create a new milestone for a project.

        :param project_id: Parent project.
        :param description: Outcome description.
        :param sort_order: Display position.
        :rtype: Milestone
        """
        ms = Milestone(
            project_id=project_id,
            description=description,
            sort_order=sort_order,
        )
        ms = self._milestones.create(ms)
        self._bus.emit(MILESTONE_UPDATED, project_id=project_id)
        return ms

    def toggle_milestone(self, milestone_id: int) -> Milestone:
        """Toggle the completion state of a milestone.

        :param milestone_id: Target milestone.
        :rtype: Milestone
        """
        ms = self._milestones.get(milestone_id)
        ms.toggle()
        updated = self._milestones.update(ms)
        self._bus.emit(MILESTONE_UPDATED, project_id=ms.project_id)
        logger.info("Toggled milestone %d → %s", milestone_id, updated.is_complete)
        return updated

    def delete_milestone(self, milestone_id: int) -> None:
        """Delete a milestone.

        :param milestone_id: Target milestone.
        """
        ms = self._milestones.get(milestone_id)
        self._milestones.delete(milestone_id)
        self._bus.emit(MILESTONE_UPDATED, project_id=ms.project_id)
        logger.info("Deleted milestone %d", milestone_id)
