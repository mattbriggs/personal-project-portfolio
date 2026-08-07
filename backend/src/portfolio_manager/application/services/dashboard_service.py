"""Dashboard read-model facade.

Ported from the original ``controllers/dashboard_controller.get_dashboard_data``.
Aggregates active projects, per-project scores and session counts, weekly minute
totals, portfolio score, and upcoming milestones. Requesting the dashboard
triggers score recomputation for each active project (skipping manual overrides).
"""

import logging

from portfolio_manager.application.dto.dashboard import (
    Dashboard,
    DashboardProjectRow,
    UpcomingMilestone,
)
from portfolio_manager.application.ports.milestone_repository import MilestoneRepository
from portfolio_manager.application.ports.project_repository import ProjectRepository
from portfolio_manager.application.ports.session_repository import SessionRepository
from portfolio_manager.application.services.scoring_service import ScoringService
from portfolio_manager.application.services.settings_service import SettingsService
from portfolio_manager.domain.scoring import score_to_status
from portfolio_manager.domain.week import current_week_key, display_range

logger = logging.getLogger(__name__)


class DashboardService:
    """Assemble the aggregate dashboard read model for a week.

    :param projects: Project repository port.
    :param sessions: Session repository port.
    :param milestones: Milestone repository port.
    :param scoring: Scoring service (recompute + portfolio score).
    :param settings: Settings service (weekly budget).
    """

    def __init__(
        self,
        projects: ProjectRepository,
        sessions: SessionRepository,
        milestones: MilestoneRepository,
        scoring: ScoringService,
        settings: SettingsService,
    ) -> None:
        self._projects = projects
        self._sessions = sessions
        self._milestones = milestones
        self._scoring = scoring
        self._settings = settings

    def get_dashboard(self, week_key: str | None = None) -> Dashboard:
        """Return the dashboard for *week_key* (defaults to the current week).

        :param week_key: Target week (``YYYY.W``).
        :returns: The aggregate dashboard read model.
        :rtype: Dashboard
        """
        wk = week_key or current_week_key()
        active = self._projects.list(status="active")
        budget_minutes = self._settings.get_settings().session.weekly_budget_hours * 60

        rows: list[DashboardProjectRow] = []
        week_total = 0
        week_done = 0
        upcoming: list[UpcomingMilestone] = []

        for project in active:
            score = self._scoring.compute_and_save(project.id, wk)
            counts = self._sessions.count_by_status(project.id, wk)
            planned = counts.get("planned", 0) + counts.get("doing", 0) + counts.get("done", 0)
            completed = counts.get("done", 0)
            rows.append(
                DashboardProjectRow(
                    project=project,
                    score=score,
                    planned=planned,
                    completed=completed,
                    remaining=planned - completed,
                )
            )

            for s in self._sessions.list_for_project(project.id, week_key=wk):
                if s.status != "cancelled":
                    week_total += s.duration_minutes
                if s.status == "done":
                    week_done += s.duration_minutes

            active_ms = [
                m
                for m in self._milestones.list_for_project(project.id)
                if m.status not in ("done", "cancelled") and m.target_date is not None
            ]
            active_ms.sort(key=lambda m: m.target_date)  # type: ignore[arg-type,return-value]
            if active_ms:
                first = active_ms[0]
                upcoming.append(
                    UpcomingMilestone(
                        project_name=project.name,
                        description=first.description,
                        target_date=first.target_date,  # type: ignore[arg-type]
                    )
                )

        upcoming.sort(key=lambda m: m.target_date)
        portfolio = self._scoring.portfolio_score(wk)

        return Dashboard(
            week_key=wk,
            date_range=display_range(wk),
            rows=rows,
            portfolio_score=portfolio,
            portfolio_status=score_to_status(portfolio),
            week_total_minutes=week_total,
            week_done_minutes=week_done,
            budget_minutes=budget_minutes,
            upcoming_milestones=upcoming,
        )
