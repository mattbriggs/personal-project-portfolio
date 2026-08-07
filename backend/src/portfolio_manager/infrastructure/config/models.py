"""Pydantic configuration models.

Replaces the original dataclass-based settings with validated Pydantic models
while preserving the same TOML layout, defaults, and the
``~/.portfolio_manager`` location. Validation bounds follow the SRS:

- default session duration 15–480 minutes
- weekly budget 1–100 hours
"""

from pathlib import Path

from pydantic import BaseModel, Field, field_validator

SUPPORTED_LOG_LEVELS: frozenset[str] = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
SUPPORTED_THEMES: frozenset[str] = frozenset({"light", "dark"})


class AppConfig(BaseModel):
    """Application-level configuration.

    :param log_level: Python logging level name.
    :param theme: UI theme (``light`` or ``dark``).
    """

    log_level: str = "INFO"
    theme: str = "light"

    @field_validator("log_level")
    @classmethod
    def _valid_level(cls, v: str) -> str:
        up = v.upper()
        if up not in SUPPORTED_LOG_LEVELS:
            raise ValueError(f"Unsupported log level {v!r}.")
        return up

    @field_validator("theme")
    @classmethod
    def _valid_theme(cls, v: str) -> str:
        low = v.lower()
        if low not in SUPPORTED_THEMES:
            raise ValueError(f"Unsupported theme {v!r}.")
        return low


class SessionConfig(BaseModel):
    """Session-related defaults.

    :param default_duration_minutes: Default session length (15–480).
    :param weekly_budget_hours: Hours available per week (1–100).
    """

    default_duration_minutes: int = Field(default=90, ge=15, le=480)
    weekly_budget_hours: int = Field(default=12, ge=1, le=100)


class DatabaseConfig(BaseModel):
    """Database configuration.

    :param path: Path to the SQLite database file (tilde-expanded on resolve).
    """

    path: str = "~/.portfolio_manager/portfolio.db"

    @property
    def resolved_path(self) -> Path:
        """Tilde-expanded absolute path to the database file.

        :rtype: pathlib.Path
        """
        return Path(self.path).expanduser()


class Settings(BaseModel):
    """Top-level application settings container.

    :param app: Application-level settings.
    :param session: Session defaults.
    :param database: Database path settings.
    """

    app: AppConfig = Field(default_factory=AppConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
