"""Logging configuration for Portfolio Manager.

Sets up a rotating file handler writing to
``~/.portfolio_manager/logs/app.log`` and optionally a console handler for
development.  Call :func:`configure_logging` once at application startup.
"""

import logging
import logging.handlers
from pathlib import Path


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    log_level: str = "INFO",
    log_dir: Path | None = None,
) -> None:
    """Configure the root logger for the application.

    Creates the log directory if it does not exist, attaches a
    :class:`~logging.handlers.RotatingFileHandler` capped at 5 MB with two
    backup files, and sets the root log level.

    :param log_level: Logging level name (``DEBUG``, ``INFO``, ``WARNING``,
        ``ERROR``, ``CRITICAL``).  Case-insensitive.
    :type log_level: str
    :param log_dir: Directory for log files.  Defaults to
        ``~/.portfolio_manager/logs/``.
    :type log_dir: pathlib.Path | None
    """
    if log_dir is None:
        log_dir = Path.home() / ".portfolio_manager" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=2,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Avoid duplicate handlers if configure_logging is called more than once.
    root.handlers.clear()
    root.addHandler(file_handler)
