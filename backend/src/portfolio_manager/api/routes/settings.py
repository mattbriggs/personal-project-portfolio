"""Settings routes under ``/api/v1``."""

from fastapi import APIRouter, Depends

from portfolio_manager.api.dependencies import get_settings_service
from portfolio_manager.application.services.settings_service import SettingsService
from portfolio_manager.contracts.settings import SettingsResponse, SettingsUpdateRequest
from portfolio_manager.infrastructure.config.models import (
    AppConfig,
    DatabaseConfig,
    SessionConfig,
    Settings,
)

router = APIRouter(prefix="/api/v1", tags=["settings"])


def _to_response(settings_service: SettingsService) -> SettingsResponse:
    settings = settings_service.get_settings()
    return SettingsResponse.from_settings(
        settings, active_database_path=str(settings_service.active_database_path())
    )


@router.get("/settings", response_model=SettingsResponse)
async def get_settings(
    settings_service: SettingsService = Depends(get_settings_service),
) -> SettingsResponse:
    """Return current settings, including the active database path."""
    return _to_response(settings_service)


@router.put("/settings", response_model=SettingsResponse)
async def update_settings(
    body: SettingsUpdateRequest,
    settings_service: SettingsService = Depends(get_settings_service),
) -> SettingsResponse:
    """Persist settings. A database-path change reports ``restart_required``.

    The response's ``active_database_path`` differs from ``resolved_database_path``
    when a restart is pending, so the UI can surface the difference.
    """
    settings = Settings(
        app=AppConfig(log_level=body.log_level, theme=body.theme),
        session=SessionConfig(
            default_duration_minutes=body.default_duration_minutes,
            weekly_budget_hours=body.weekly_budget_hours,
        ),
        database=DatabaseConfig(path=body.database_path),
    )
    settings_service.update_settings(settings)
    return _to_response(settings_service)
