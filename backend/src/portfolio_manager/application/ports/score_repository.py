"""Score repository port."""

from typing import Protocol

from portfolio_manager.domain.models import ProjectScore


class ScoreRepository(Protocol):
    """Persistence contract for :class:`ProjectScore`.

    ``upsert`` enforces one score per ``(project_id, week_key)``. ``list_*``
    methods order most recent week first.
    """

    def upsert(self, score: ProjectScore) -> ProjectScore: ...
    def get_for_week(self, project_id: int, week_key: str) -> ProjectScore | None: ...
    def list_for_project(self, project_id: int) -> list[ProjectScore]: ...
    def list_for_week(self, week_key: str) -> list[ProjectScore]: ...
