"""FastAPI application factory.

Assembles the ASGI app around a wired :class:`Container`. In production mode the
interactive docs (Swagger/ReDoc) and the OpenAPI schema endpoint are disabled,
and a request-body size limit is enforced. CORS is intentionally not enabled —
the only client is the loopback Rust forwarder.
"""

import logging

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from portfolio_manager.api.exception_handlers import register_exception_handlers
from portfolio_manager.api.middleware.authentication import AuthenticationMiddleware
from portfolio_manager.api.middleware.correlation import CorrelationMiddleware
from portfolio_manager.api.middleware.request_logging import RequestLoggingMiddleware
from portfolio_manager.api.routes import (
    dashboard,
    health,
    milestones,
    projects,
    reviews,
    scores,
    sessions,
    settings,
)
from portfolio_manager.bootstrap import Container

logger = logging.getLogger(__name__)

#: Maximum accepted request body size (1 MiB); plan documents are text.
MAX_BODY_BYTES = 1_048_576


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests whose declared ``Content-Length`` exceeds the limit."""

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001, ANN201
        length = request.headers.get("content-length")
        if length is not None and length.isdigit() and int(length) > MAX_BODY_BYTES:
            return JSONResponse(
                status_code=413,
                content={"code": "VALIDATION_ERROR", "message": "Request body too large."},
            )
        return await call_next(request)


def create_app(container: Container) -> FastAPI:
    """Create the FastAPI application for a wired *container*.

    :param container: The application container (services + runtime metadata).
    :returns: The configured FastAPI app.
    :rtype: fastapi.FastAPI
    """
    docs_enabled = not container.production
    app = FastAPI(
        title="Portfolio Manager Sidecar",
        version="2.0.0",
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )
    app.state.container = container

    # Middleware: added last runs first. Correlation must precede auth so error
    # responses carry a correlation ID.
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(AuthenticationMiddleware, expected_token=container.token)
    app.add_middleware(BodySizeLimitMiddleware)
    app.add_middleware(CorrelationMiddleware)

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(dashboard.router)
    app.include_router(projects.router)
    app.include_router(sessions.router)
    app.include_router(milestones.router)
    app.include_router(reviews.router)
    app.include_router(scores.router)
    app.include_router(settings.router)

    logger.info("FastAPI app created (production=%s)", container.production)
    return app
