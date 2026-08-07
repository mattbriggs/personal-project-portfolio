"""Token authentication middleware.

Requires a valid ``X-API-Key`` on every route except the unauthenticated health
routes (``/health`` and ``/ready``, which expose no sensitive data — see ADR-007).
Rejects missing/invalid tokens with ``401`` and a structured error body. Auth
headers are never logged.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from portfolio_manager.contracts.errors import ErrorCode, ErrorResponse
from portfolio_manager.infrastructure.logging.context import correlation_id
from portfolio_manager.infrastructure.security.token import tokens_match

API_KEY_HEADER = "X-API-Key"

#: Paths that do not require authentication (health only).
_PUBLIC_PATHS: frozenset[str] = frozenset({"/health", "/ready"})


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Enforce ``X-API-Key`` on all non-health routes.

    :param app: The wrapped ASGI app.
    :param expected_token: The per-launch token. If empty, auth is disabled
        (used in tests and unauthenticated local development).
    """

    def __init__(self, app, expected_token: str) -> None:  # noqa: ANN001
        super().__init__(app)
        self._expected_token = expected_token

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Validate the token unless the route is public or auth is disabled.

        :param request: The inbound request.
        :param call_next: The next handler.
        :rtype: starlette.responses.Response
        """
        if not self._expected_token or request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        provided = request.headers.get(API_KEY_HEADER)
        if not tokens_match(self._expected_token, provided):
            body = ErrorResponse(
                code=ErrorCode.AUTHENTICATION_FAILED,
                message="Missing or invalid API key.",
                correlation_id=correlation_id.get(),
                retryable=False,
            )
            return JSONResponse(status_code=401, content=body.model_dump(mode="json"))
        return await call_next(request)
