import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from cassandra_terminal.config import get_db_path
from cassandra_terminal.db.schema import CREATE_TABLES_SQL

_INITIALIZED_DBS: set[str] = set()


def init_db(db_path: Path | None = None) -> Path:
    """Initialize database tables if not already initialized."""
    path = db_path or get_db_path()
    path_str = str(path.resolve())

    if path_str not in _INITIALIZED_DBS:
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as conn:
            conn.executescript(CREATE_TABLES_SQL)
            conn.commit()
        _INITIALIZED_DBS.add(path_str)
    return path


@contextmanager
def get_db(db_path: Path | None = None) -> Generator[sqlite3.Connection, None, None]:
    """Provide a transactional scope around a series of database operations."""
    path = init_db(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
