"""Controller for the portfolio dashboard view."""

import logging
from typing import Any

from portfolio_manager.events.event_bus import (
    MILESTONE_UPDATED,
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
            PROJECT_CREATED,
            PROJECT_UPDATED,
            PROJECT_DELETED,
            SESSION_CREATED,
            SESSION_UPDATED,
            SESSION_COMPLETED,
            SESSION_DELETED,
            MILESTONE_UPDATED,
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
            ``portfolio_score``, ``portfolio_status``,
            ``week_total_min``, ``week_done_min``, ``next_milestones``.
        :rtype: dict[str, Any]
        """
        from portfolio_manager.db.connection import DatabaseConnection
        from portfolio_manager.repositories.milestone_repo import MilestoneRepository
        from portfolio_manager.repositories.session_repo import SessionRepository
        from portfolio_manager.services.scoring_service import score_to_status

        week_key = self._weeks.current_week_key()
        date_range = self._weeks.display_range(week_key)
        projects = self._projects.list_projects(status="active")

        sr = SessionRepository(DatabaseConnection.get())
        mr = MilestoneRepository(DatabaseConnection.get())

        rows = []
        week_total_min = 0
        week_done_min = 0
        next_milestones: list[dict[str, Any]] = []

        for project in projects:
            score = self._scoring.compute_and_save(project.id, week_key)
            counts = sr.count_by_status(project.id, week_key)
            planned = (
                counts.get("planned", 0)
                + counts.get("doing", 0)
                + counts.get("done", 0)
            )
            completed = counts.get("done", 0)
            rows.append(
                {
                    "project": project,
                    "score": score,
                    "planned": planned,
                    "completed": completed,
                    "remaining": planned - completed,
                }
            )

            # Accumulate this-week minute totals across all projects
            week_sessions = sr.list_for_project(project.id, week_key=week_key)
            for s in week_sessions:
                if s.status != "cancelled":
                    week_total_min += s.duration_minutes
                if s.status == "done":
                    week_done_min += s.duration_minutes

            # Find the earliest non-done milestone for this project
            milestones = mr.list_for_project(project.id)
            active_ms = [
                m for m in milestones
                if m.status not in ("done", "cancelled") and m.target_date is not None
            ]
            active_ms.sort(key=lambda m: m.target_date)  # type: ignore[arg-type]
            if active_ms:
                next_milestones.append(
                    {
                        "project": project.name,
                        "milestone": active_ms[0].description,
                        "target": active_ms[0].target_date,
                    }
                )

        next_milestones.sort(key=lambda m: m["target"])

        portfolio_score = self._scoring.portfolio_score(week_key)
        portfolio_status = score_to_status(portfolio_score)

        return {
            "week_key": week_key,
            "date_range": date_range,
            "rows": rows,
            "portfolio_score": portfolio_score,
            "portfolio_status": portfolio_status,
            "week_total_min": week_total_min,
            "week_done_min": week_done_min,
            "next_milestones": next_milestones,
        }
