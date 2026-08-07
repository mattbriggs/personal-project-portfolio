"""Filesystem path resolution for the local portfolio data directory.

Preserves the original ``~/.portfolio_manager`` location so existing databases,
configuration, and logs are found without manual migration.
"""

from pathlib import Path

#: Root directory for all Portfolio Manager local data.
CONFIG_DIR = Path.home() / ".portfolio_manager"

#: Default TOML configuration file path.
CONFIG_FILE = CONFIG_DIR / "config.toml"

#: Default SQLite database path.
DEFAULT_DB_PATH = CONFIG_DIR / "portfolio.db"

#: Directory for rotating log files.
LOG_DIR = CONFIG_DIR / "logs"


def ensure_config_dir() -> Path:
    """Create the config directory if absent and return it.

    :rtype: pathlib.Path
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR
