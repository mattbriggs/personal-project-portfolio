"""TOML settings adapter.

Reads and writes ``~/.portfolio_manager/config.toml``, creating it with defaults
on first launch. Preserves the exact TOML layout produced by the original
``config/settings.py`` so existing config files remain valid.

Implements :class:`portfolio_manager.application.ports.settings_repository.SettingsRepository`.
"""

import logging
import tomllib
from pathlib import Path

from portfolio_manager.domain.errors import ConfigError
from portfolio_manager.infrastructure.config.models import (
    AppConfig,
    DatabaseConfig,
    SessionConfig,
    Settings,
)
from portfolio_manager.infrastructure.system.paths import CONFIG_FILE

logger = logging.getLogger(__name__)

_DEFAULT_TOML = """\
[app]
log_level = "INFO"
theme = "light"

[session]
default_duration_minutes = 90
weekly_budget_hours = 12

[database]
path = "~/.portfolio_manager/portfolio.db"
"""


class TomlSettingsRepository:
    """Load and persist :class:`Settings` from a TOML file.

    :param config_path: Path to the config file. Defaults to
        ``~/.portfolio_manager/config.toml``.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        self._path = config_path or CONFIG_FILE

    @property
    def path(self) -> Path:
        """The resolved config file path.

        :rtype: pathlib.Path
        """
        return self._path

    def load(self) -> Settings:
        """Load settings, writing defaults if the file is absent.

        :returns: Validated settings.
        :rtype: Settings
        :raises ConfigError: If the file exists but cannot be parsed or validated.
        """
        if not self._path.exists():
            self._write_defaults()

        try:
            with self._path.open("rb") as fh:
                raw = tomllib.load(fh)
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(f"Could not parse config file {self._path}: {exc}") from exc

        try:
            return Settings(
                app=AppConfig(**raw.get("app", {})),
                session=SessionConfig(**raw.get("session", {})),
                database=DatabaseConfig(**raw.get("database", {})),
            )
        except ValueError as exc:
            raise ConfigError(f"Invalid configuration in {self._path}: {exc}") from exc

    def save(self, settings: Settings) -> None:
        """Persist *settings* back to the TOML file.

        :param settings: Settings to persist.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            "[app]\n"
            f'log_level = "{settings.app.log_level}"\n'
            f'theme = "{settings.app.theme}"\n'
            "\n"
            "[session]\n"
            f"default_duration_minutes = {settings.session.default_duration_minutes}\n"
            f"weekly_budget_hours = {settings.session.weekly_budget_hours}\n"
            "\n"
            "[database]\n"
            f'path = "{settings.database.path}"\n'
        )
        self._path.write_text(content, encoding="utf-8")
        logger.info("Saved settings to %s", self._path)

    def _write_defaults(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(_DEFAULT_TOML, encoding="utf-8")
        logger.info("Wrote default config to %s", self._path)
