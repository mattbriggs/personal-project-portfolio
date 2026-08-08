"""Health and readiness routes.

``/health`` reports process liveness; ``/ready`` reports operational readiness
(database reachable). Both are unauthenticated and expose no sensitive data
(ADR-007), letting the Rust supervisor distinguish liveness from readiness.
"""

from fastapi import APIRouter, Depends

from portfolio_manager.api.dependencies import get_container
from portfolio_manager.bootstrap import Container

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Report process liveness.

    :returns: ``{"status": "ok"}``.
    :rtype: dict[str, str]
    """
    return {"status": "ok"}


@router.get("/ready")
async def ready(container: Container = Depends(get_container)) -> dict[str, str]:
    """Report operational readiness by probing the database.

    :returns: ``{"status": "ready"}`` when the database responds.
    :rtype: dict[str, str]
    """
    container.db.fetchone("SELECT 1")
    return {"status": "ready"}
