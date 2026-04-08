"""Controller for the portfolio dashboard view."""

import logging
from typing import Any

from portfolio_manager.events.event_bus import (
    PROJECT_CREATED,
    PROJECT_DELETED,
    PROJECT_UPDATED,
    SESSION_COMPLETED,
    SESSION_CREATED,
    SESSION_DELETED,
    SESSION_UPDATED,
    EventBus,
)
from portfolio_manager.services.project_service import ProjectService
from portfolio_manager.services.scoring_service import ScoringService
from portfolio_manager.services.week_service import WeekService

logger = logging.getLogger(__name__)


class DashboardController:
    """Provides data and actions for the dashboard view.

    :param project_service: Service for project queries.
    :param scoring_service: Service for score computation.
    :param week_service: Service for week-key helpers.
    :param bus: Event bus for subscribing to state changes.
    """

    def __init__(
        self,
        project_service: ProjectService,
        scoring_service: ScoringService,
        week_service: WeekService,
        bus: EventBus | None = None,
    ) -> None:
        self._projects = project_service
        self._scoring = scoring_service
        self._weeks = week_service
        self._bus = bus or EventBus.get()
        self._view: Any = None  # set by main_window after view is created

        # Subscribe to events that require a dashboard refresh.
        for event in (
            PROJECT_CREATED, PROJECT_UPDATED, PROJECT_DELETED,
            SESSION_CREATED, SESSION_UPDATED, SESSION_COMPLETED, SESSION_DELETED,
        ):
            self._bus.subscribe(event, self._on_data_changed)

    def bind_view(self, view: Any) -> None:
        """Attach the dashboard view so the controller can trigger refreshes.

        :param view: A view object with a ``refresh()`` method.
        """
        self._view = view

    def _on_data_changed(self, **_kwargs: Any) -> None:
        """Refresh the dashboard whenever relevant data changes."""
        if self._view is not None:
            try:
                self._view.refresh()
            except Exception:
                logger.exception("Error refreshing dashboard view")

    def get_dashboard_data(self) -> dict[str, Any]:
        """Return all data needed to render the dashboard.

        :returns: Dict with keys ``week_key``, ``date_range``, ``rows``,
            ``portfolio_score``, ``portfolio_status``.
        :rtype: dict[str, Any]
        """
        week_key = self._weeks.current_week_key()
        date_range = self._weeks.display_range(week_key)
        projects = self._projects.list_projects(status="active")

        rows = []
        for project in projects:
            score = self._scoring.compute_and_save(project.id, week_key)
            from portfolio_manager.repositories.session_repo import SessionRepository
            from portfolio_manager.db.connection import DatabaseConnection
            sr = SessionRepository(DatabaseConnection.get())
            counts = sr.count_by_status(project.id, week_key)
            planned = counts.get("planned", 0) + counts.get("completed", 0)
            completed = counts.get("completed", 0)
            rows.append({
                "project": project,
                "score": score,
                "planned": planned,
                "completed": completed,
                "remaining": planned - completed,
            })

        portfolio_score = self._scoring.portfolio_score(week_key)
        from portfolio_manager.services.scoring_service import score_to_status
        portfolio_status = score_to_status(portfolio_score)

        return {
            "week_key": week_key,
            "date_range": date_range,
            "rows": rows,
            "portfolio_score": portfolio_score,
            "portfolio_status": portfolio_status,
        }
