from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from fileforge.db.connection import get_db


class ActivityLog(BaseModel):
    id: int | None = None
    timestamp: str
    operation: str
    target: str
    result: str
    details: str | None = None


def log_activity(
    operation: str,
    target: str,
    result: str = "SUCCESS",
    details: str | None = None,
    db_path: Path | None = None,
) -> None:
    """Record an operation in the activity logs."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db(db_path) as conn:
        conn.execute(
            """
            INSERT INTO activity_logs (timestamp, operation, target, result, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (now, operation, target, result, details),
        )


def get_activity_logs(
    limit: int = 50,
    operation_filter: str | None = None,
    db_path: Path | None = None,
) -> list[ActivityLog]:
    """Retrieve activity logs with optional filtering."""
    query = "SELECT id, timestamp, operation, target, result, details FROM activity_logs"
    params: list[Any] = []

    if operation_filter:
        query += " WHERE operation LIKE ?"
        params.append(f"%{operation_filter}%")

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    with get_db(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        return [
            ActivityLog(
                id=row["id"],
                timestamp=str(row["timestamp"]),
                operation=row["operation"],
                target=row["target"],
                result=row["result"],
                details=row["details"],
            )
            for row in rows
        ]


def clear_activity_logs(db_path: Path | None = None) -> int:
    """Clear all activity logs."""
    with get_db(db_path) as conn:
        cursor = conn.execute("DELETE FROM activity_logs")
        return cursor.rowcount
