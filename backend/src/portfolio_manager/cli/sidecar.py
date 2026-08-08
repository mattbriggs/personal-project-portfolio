"""Sidecar entry point.

Launched by the Rust supervisor. Binds only to ``127.0.0.1`` on the supplied
port, reads the auth token from the environment or stdin (never argv), runs
migrations, and serves the FastAPI app via Uvicorn.

Usage::

    PORTFOLIO_SIDECAR_TOKEN=<token> python -m portfolio_manager.cli.sidecar \\
        --port 8765 [--production]
"""

import argparse
import logging

import uvicorn

from portfolio_manager.api.app import create_app
from portfolio_manager.bootstrap import build_container
from portfolio_manager.infrastructure.logging import configure_logging
from portfolio_manager.infrastructure.security.token import read_startup_token

#: Loopback host — the sidecar must never bind a routable interface.
HOST = "127.0.0.1"

logger = logging.getLogger(__name__)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Portfolio Manager FastAPI sidecar")
    parser.add_argument("--port", type=int, required=True, help="Loopback port to bind")
    parser.add_argument(
        "--production",
        action="store_true",
        help="Enable production hardening (disable docs).",
    )
    parser.add_argument("--log-level", default="INFO", help="Logging level (default INFO).")
    return parser.parse_args(argv)


def build_app(production: bool, token: str):  # noqa: ANN201
    """Build the FastAPI app with a wired container.

    :param production: Enable production hardening.
    :param token: Expected sidecar auth token.
    :returns: The FastAPI application.
    """
    container = build_container(token=token, production=production)
    return create_app(container)


def main(argv: list[str] | None = None) -> None:
    """Parse args, build the app, and run Uvicorn on the loopback port.

    :param argv: Optional argument vector (defaults to ``sys.argv``).
    """
    args = _parse_args(argv)
    configure_logging(args.log_level)
    token = read_startup_token()
    if not token:
        logger.warning("No sidecar token supplied; authentication is DISABLED.")

    app = build_app(production=args.production, token=token)
    logger.info("Starting sidecar on %s:%d", HOST, args.port)
    uvicorn.run(app, host=HOST, port=args.port, log_config=None, access_log=False)


if __name__ == "__main__":
    main()
