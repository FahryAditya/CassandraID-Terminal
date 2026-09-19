from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from cassandra_terminal.db.connection import get_db


@dataclass
class ProjectNote:
    id: int
    project_path: str
    content: str
    status: str  # 'pending' or 'done'
    created_at: str
    updated_at: str


def get_current_project_key(custom_path: Path | None = None) -> str:
    """Get canonical workspace path string."""
    return str((custom_path or Path.cwd()).resolve())


def add_note(content: str, project_path: str | None = None) -> int:
    """Add a new task/note for the project."""
    now_str = datetime.now().isoformat()
    p_path = project_path or get_current_project_key()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO project_notes (project_path, content, status, created_at, updated_at)
            VALUES (?, ?, 'pending', ?, ?)
            """,
            (p_path, content.strip(), now_str, now_str),
        )
        return int(cursor.lastrowid)


def list_notes(
    project_path: str | None = None,
    filter_status: Literal["all", "pending", "done"] = "all",
) -> list[ProjectNote]:
    """Retrieve notes for the project with optional status filter."""
    p_path = project_path or get_current_project_key()
    with get_db() as conn:
        cursor = conn.cursor()
        if filter_status == "all":
            cursor.execute(
                """
                SELECT id, project_path, content, status, created_at, updated_at
                FROM project_notes
                WHERE project_path = ?
                ORDER BY CASE status WHEN 'pending' THEN 0 ELSE 1 END, id DESC
                """,
                (p_path,),
            )
        else:
            cursor.execute(
                """
                SELECT id, project_path, content, status, created_at, updated_at
                FROM project_notes
                WHERE project_path = ? AND status = ?
                ORDER BY id DESC
                """,
                (p_path, filter_status),
            )

        rows = cursor.fetchall()
        return [
            ProjectNote(
                id=r["id"],
                project_path=r["project_path"],
                content=r["content"],
                status=r["status"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in rows
        ]


def toggle_note_status(note_id: int) -> tuple[bool, str]:
    """Toggle note status between 'pending' and 'done'."""
    now_str = datetime.now().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM project_notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        if not row:
            return False, "not_found"

        new_status = "done" if row["status"] == "pending" else "pending"
        cursor.execute(
            "UPDATE project_notes SET status = ?, updated_at = ? WHERE id = ?",
            (new_status, now_str, note_id),
        )
        return True, new_status


def delete_note(note_id: int) -> bool:
    """Delete a specific note by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM project_notes WHERE id = ?", (note_id,))
        return cursor.rowcount > 0


def clear_completed_notes(project_path: str | None = None) -> int:
    """Remove all completed ('done') notes for the project."""
    p_path = project_path or get_current_project_key()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM project_notes WHERE project_path = ? AND status = 'done'",
            (p_path,),
        )
        return cursor.rowcount
