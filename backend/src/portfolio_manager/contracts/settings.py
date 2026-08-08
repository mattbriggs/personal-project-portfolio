"""Settings HTTP contracts."""

from pydantic import BaseModel, Field

from portfolio_manager.infrastructure.config.models import Settings


class SettingsResponse(BaseModel):
    """Settings response, exposing a resolved (display) database path.

    The active path (currently opened by the sidecar) is reported separately so
    the UI can show a pending restart-required change (SRS §5.13).
    """

    log_level: str
    theme: str
    default_duration_minutes: int
    weekly_budget_hours: int
    database_path: str
    resolved_database_path: str
    active_database_path: str

    @classmethod
    def from_settings(cls, settings: Settings, active_database_path: str) -> "SettingsResponse":
        """Build a response from :class:`Settings`.

        :param settings: Loaded settings.
        :param active_database_path: The path the sidecar currently has open.
        :rtype: SettingsResponse
        """
        return cls(
            log_level=settings.app.log_level,
            theme=settings.app.theme,
            default_duration_minutes=settings.session.default_duration_minutes,
            weekly_budget_hours=settings.session.weekly_budget_hours,
            database_path=settings.database.path,
            resolved_database_path=str(settings.database.resolved_path),
            active_database_path=active_database_path,
        )


class SettingsUpdateRequest(BaseModel):
    """Request body for updating settings.

    Validation bounds mirror :mod:`portfolio_manager.infrastructure.config.models`.
    """

    log_level: str
    theme: str
    default_duration_minutes: int = Field(ge=15, le=480)
    weekly_budget_hours: int = Field(ge=1, le=100)
    database_path: str = Field(min_length=1)
