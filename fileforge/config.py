import os
from pathlib import Path

import platformdirs

APP_NAME = "CassandraID-Terminal"
APP_AUTHOR = "CassandraID"


def get_app_dir() -> Path:
    """Return the application data directory based on OS."""
    override = os.environ.get("FILEFORGE_DATA_DIR") or os.environ.get("CASSANDRA_DATA_DIR")
    if override:
        path = Path(override)
    else:
        path = Path(platformdirs.user_data_dir(APP_NAME, APP_AUTHOR))
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_db_path() -> Path:
    """Return the SQLite database path."""
    override = os.environ.get("FILEFORGE_DB_PATH") or os.environ.get("CASSANDRA_DB_PATH")
    if override:
        return Path(override)
    return get_app_dir() / "cassandra.db"
