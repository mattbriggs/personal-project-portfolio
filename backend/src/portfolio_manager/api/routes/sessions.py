"""Session routes under ``/api/v1``."""

from fastapi import APIRouter, Depends, Query

from portfolio_manager.api.dependencies import get_sessions, get_settings_service
from portfolio_manager.application.services.session_service import SessionService
from portfolio_manager.application.services.settings_service import SettingsService
from portfolio_manager.contracts.common import OkResponse
from portfolio_manager.contracts.sessions import (
    SessionCreateRequest,
    SessionListResponse,
    SessionRescheduleRequest,
    SessionResponse,
    SessionStatusRequest,
    SessionUpdateRequest,
)
from portfolio_manager.domain.models import Session

router = APIRouter(prefix="/api/v1", tags=["sessions"])


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    week_key: str = Query(...),
    sessions: SessionService = Depends(get_sessions),
) -> SessionListResponse:
    """List all sessions for a given week."""
    items = sessions.get_sessions_for_week(week_key)
    return SessionListResponse(sessions=[SessionResponse.from_domain(s) for s in items])


@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(
    body: SessionCreateRequest,
    sessions: SessionService = Depends(get_sessions),
    settings: SettingsService = Depends(get_settings_service),
) -> SessionResponse:
    """Create a session, applying the configured default duration when omitted."""
    duration = body.duration_minutes
    if duration is None:
        duration = settings.get_settings().session.default_duration_minutes
    session = sessions.create_session(
        project_id=body.project_id,
        scheduled_date=body.scheduled_date,
        duration_minutes=duration,
        description=body.description,
        notes=body.notes,
        milestone_id=body.milestone_id,
        status=body.status,
    )
    return SessionResponse.from_domain(session)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int, sessions: SessionService = Depends(get_sessions)
) -> SessionResponse:
    """Fetch a single session."""
    return SessionResponse.from_domain(sessions.get_session(session_id))


@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    body: SessionUpdateRequest,
    sessions: SessionService = Depends(get_sessions),
) -> SessionResponse:
    """Update a session's editable fields (week key re-derived from date)."""
    existing = sessions.get_session(session_id)
    updated = Session(
        id=session_id,
        project_id=body.project_id,
        milestone_id=body.milestone_id,
        scheduled_date=body.scheduled_date,
        week_key=existing.week_key,
        duration_minutes=body.duration_minutes,
        status=body.status,
        description=body.description,
        notes=body.notes,
        created_at=existing.created_at,
        completed_at=existing.completed_at,
    )
    return SessionResponse.from_domain(sessions.update_session(updated))


@router.post("/sessions/{session_id}/status", response_model=SessionResponse)
async def set_status(
    session_id: int,
    body: SessionStatusRequest,
    sessions: SessionService = Depends(get_sessions),
) -> SessionResponse:
    """Transition a session to a new status."""
    return SessionResponse.from_domain(sessions.set_status(session_id, body.status))


@router.post("/sessions/{session_id}/reschedule", response_model=SessionResponse)
async def reschedule(
    session_id: int,
    body: SessionRescheduleRequest,
    sessions: SessionService = Depends(get_sessions),
) -> SessionResponse:
    """Reschedule a session and recompute its week key."""
    return SessionResponse.from_domain(sessions.reschedule_session(session_id, body.scheduled_date))


@router.delete("/sessions/{session_id}", response_model=OkResponse)
async def delete_session(
    session_id: int, sessions: SessionService = Depends(get_sessions)
) -> OkResponse:
    """Delete a session permanently."""
    sessions.delete_session(session_id)
    return OkResponse()
