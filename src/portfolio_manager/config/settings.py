"""Application configuration loader for Portfolio Manager.

Settings are read from ``~/.portfolio_manager/config.toml`` (created with
defaults on first launch).  The :class:`Settings` dataclass is the sole
source of truth for runtime configuration.
"""

import logging
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from portfolio_manager.exceptions import ConfigError

logger = logging.getLogger(__name__)

_CONFIG_DIR = Path.home() / ".portfolio_manager"
_CONFIG_FILE = _CONFIG_DIR / "config.toml"

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


@dataclass
class AppConfig:
    """Application-level configuration.

    :param log_level: Python logging level name (default ``INFO``).
    :param theme: UI theme — ``light`` or ``dark`` (default ``light``).
    """

    log_level: str = "INFO"
    theme: str = "light"


@dataclass
class SessionConfig:
    """Session-related defaults.

    :param default_duration_minutes: Default session length in minutes
        (default 90).
    :param weekly_budget_hours: Total hours available per week (default 12).
    """

    default_duration_minutes: int = 90
    weekly_budget_hours: int = 12


@dataclass
class DatabaseConfig:
    """Database configuration.

    :param path: Path to the SQLite database file.  Tilde-expanded.
    """

    path: str = "~/.portfolio_manager/portfolio.db"

    @property
    def resolved_path(self) -> Path:
        """Tilde-expanded :class:`pathlib.Path` to the database file.

        :rtype: pathlib.Path
        """
        return Path(self.path).expanduser()


@dataclass
class Settings:
    """Top-level application settings container.

    Holds sub-configs for the app, sessions, and database.  Access via
    :func:`load_settings` to get a properly initialised instance.

    :param app: Application-level settings.
    :param session: Session defaults.
    :param database: Database path settings.
    """

    app: AppConfig = field(default_factory=AppConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)


def _write_defaults(path: Path | None = None) -> None:
    """Write the default ``config.toml`` to *path* (or the standard location).

    :param path: Destination path for the default config file.
    :type path: pathlib.Path | None
    """
    target = path or _CONFIG_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_DEFAULT_TOML, encoding="utf-8")
    logger.info("Wrote default config to %s", target)


def load_settings(config_path: Path | None = None) -> Settings:
    """Load application settings from the TOML config file.

    If the config file does not exist it is created with default values.
    Unknown keys in the file are silently ignored.

    :param config_path: Path to the config file.  Defaults to
        ``~/.portfolio_manager/config.toml``.
    :type config_path: pathlib.Path | None
    :returns: Populated :class:`Settings` instance.
    :rtype: Settings
    :raises ConfigError: If the file exists but cannot be parsed.
    """
    path = config_path or _CONFIG_FILE

    if not path.exists():
        _write_defaults(path)

    try:
        with path.open("rb") as fh:
            raw = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Could not parse config file {path}: {exc}") from exc

    app_raw = raw.get("app", {})
    ses_raw = raw.get("session", {})
    db_raw = raw.get("database", {})

    settings = Settings(
        app=AppConfig(
            log_level=str(app_raw.get("log_level", "INFO")),
            theme=str(app_raw.get("theme", "light")),
        ),
        session=SessionConfig(
            default_duration_minutes=int(ses_raw.get("default_duration_minutes", 90)),
            weekly_budget_hours=int(ses_raw.get("weekly_budget_hours", 12)),
        ),
        database=DatabaseConfig(
            path=str(db_raw.get("path", "~/.portfolio_manager/portfolio.db")),
        ),
    )

    logger.debug("Loaded settings from %s", path)
    return settings


def save_settings(settings: Settings, config_path: Path | None = None) -> None:
    """Persist updated settings back to the TOML config file.

    :param settings: The :class:`Settings` object to persist.
    :type settings: Settings
    :param config_path: Destination path.  Defaults to the standard location.
    :type config_path: pathlib.Path | None
    """
    path = config_path or _CONFIG_FILE
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    content = f"""\
[app]
log_level = "{settings.app.log_level}"
theme = "{settings.app.theme}"

[session]
default_duration_minutes = {settings.session.default_duration_minutes}
weekly_budget_hours = {settings.session.weekly_budget_hours}

[database]
path = "{settings.database.path}"
"""
    path.write_text(content, encoding="utf-8")
    logger.info("Saved settings to %s", path)
