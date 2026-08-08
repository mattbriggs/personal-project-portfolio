"""Settings service.

Loads and persists application settings via the TOML repository. Detects when the
database path changes and reports ``restart_required`` so the shell does not
hot-switch the active database (SRS §5.13).
"""

import logging
from pathlib import Path

from portfolio_manager.application.ports.settings_repository import SettingsRepository
from portfolio_manager.infrastructure.config.models import Settings

logger = logging.getLogger(__name__)


class SettingsService:
    """Coordinate settings retrieval, validation, and persistence.

    :param repository: Settings repository port (TOML-backed).
    :param active_db_path: The database path the running sidecar actually opened,
        used to detect a pending restart-required change.
    """

    def __init__(
        self,
        repository: SettingsRepository,
        active_db_path: Path | None = None,
    ) -> None:
        self._repo = repository
        self._active_db_path = active_db_path

    def get_settings(self) -> Settings:
        """Return the current settings.

        :rtype: Settings
        """
        return self._repo.load()

    def config_path(self) -> Path:
        """Return the resolved config file path.

        :rtype: pathlib.Path
        """
        return self._repo.path

    def active_database_path(self) -> Path:
        """Return the database path the sidecar is currently using.

        :rtype: pathlib.Path
        """
        if self._active_db_path is not None:
            return self._active_db_path
        return self._repo.load().database.resolved_path

    def update_settings(self, settings: Settings) -> tuple[Settings, bool]:
        """Persist *settings* and report whether a restart is required.

        A restart is required when the configured database path differs from the
        path the sidecar currently has open.

        :param settings: Validated settings to persist.
        :returns: ``(saved_settings, restart_required)``.
        :rtype: tuple[Settings, bool]
        """
        new_db = settings.database.resolved_path
        restart_required = (
            self._active_db_path is not None
            and new_db.resolve() != Path(self._active_db_path).resolve()
        )
        self._repo.save(settings)
        logger.info("Settings saved (restart_required=%s)", restart_required)
        return settings, restart_required
