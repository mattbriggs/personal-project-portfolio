"""Settings repository port."""

from pathlib import Path
from typing import Protocol

from portfolio_manager.infrastructure.config.models import Settings


class SettingsRepository(Protocol):
    """Read/write contract for application settings.

    ``load`` creates a default config on first use; ``save`` persists changes.
    """

    @property
    def path(self) -> Path: ...
    def load(self) -> Settings: ...
    def save(self, settings: Settings) -> None: ...
