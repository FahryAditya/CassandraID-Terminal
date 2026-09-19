from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from fileforge.db.connection import get_db
from fileforge.modules.activity import log_activity


class Workspace(BaseModel):
    id: int | None = None
    name: str
    path: str
    project_type: str
    created_at: str | None = None
    updated_at: str | None = None


class RecentProject(BaseModel):
    id: int | None = None
    name: str
    path: str
    project_type: str
    last_accessed: str


def detect_project_type(path: Path) -> str:
    """Analyze directory structure to identify project type statically without code execution."""
    if not path.exists() or not path.is_dir():
        return "Unknown"

    files = {f.name.lower() for f in path.iterdir() if f.is_file()}

    if "pyproject.toml" in files or "setup.py" in files or "requirements.txt" in files:
        if (path / "app.py").exists() or (path / "wsgi.py").exists():
            return "Python (Flask/Web)"
        return "Python"
    if "package.json" in files:
        if (
            (path / "next.config.js").exists()
            or (path / "next.config.mjs").exists()
            or (path / "next.config.ts").exists()
        ):
            return "Next.js"
        if (path / "vite.config.js").exists() or (path / "vite.config.ts").exists():
            return "Vite (Frontend)"
        return "Node.js"
    if "cargo.toml" in files:
        return "Rust"
    if "go.mod" in files:
        return "Go"
    if "pom.xml" in files or "build.gradle" in files or "build.gradle.kts" in files:
        return "Java"
    if "composer.json" in files:
        return "PHP"
    if "index.html" in files:
        return "Static Web"

    return "General / Generic"


# --- Workspace Management (Module D) ---


def add_workspace(path: Path, name: str | None = None, db_path: Path | None = None) -> Workspace:
    """Register a new workspace directory."""
    resolved_path = path.resolve()
    if not resolved_path.exists() or not resolved_path.is_dir():
        raise NotADirectoryError(f"Directory does not exist: {resolved_path}")

    ws_name = name.strip() if name else resolved_path.name
    proj_type = detect_project_type(resolved_path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db(db_path) as conn:
        conn.execute(
            """
            INSERT INTO workspaces (name, path, project_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                name=excluded.name,
                project_type=excluded.project_type,
                updated_at=excluded.updated_at
            """,
            (ws_name, str(resolved_path), proj_type, now, now),
        )

    log_activity(
        operation="WORKSPACE_ADD",
        target=str(resolved_path),
        result="SUCCESS",
        details=f"Registered workspace '{ws_name}' ({proj_type})",
        db_path=db_path,
    )
    return Workspace(
        name=ws_name,
        path=str(resolved_path),
        project_type=proj_type,
        created_at=now,
        updated_at=now,
    )


def list_workspaces(db_path: Path | None = None) -> list[Workspace]:
    """List all registered workspaces."""
    with get_db(db_path) as conn:
        rows = conn.execute(
            "SELECT id, name, path, project_type, created_at, updated_at FROM workspaces ORDER BY name ASC"
        ).fetchall()
        return [
            Workspace(
                id=row["id"],
                name=row["name"],
                path=row["path"],
                project_type=row["project_type"],
                created_at=str(row["created_at"]),
                updated_at=str(row["updated_at"]),
            )
            for row in rows
        ]


def remove_workspace(name_or_path: str, db_path: Path | None = None) -> bool:
    """Remove a workspace registration by name or path."""
    with get_db(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM workspaces WHERE name = ? OR path = ?",
            (name_or_path, name_or_path),
        )
        removed = cursor.rowcount > 0

    if removed:
        log_activity(
            operation="WORKSPACE_REMOVE",
            target=name_or_path,
            result="SUCCESS",
            details=f"Removed workspace '{name_or_path}'",
            db_path=db_path,
        )
    return removed


# --- Recent Projects (Module E) ---


def record_recent_project(path: Path, name: str | None = None, db_path: Path | None = None) -> None:
    """Record or bump a project in recent projects list."""
    resolved_path = path.resolve()
    proj_name = name.strip() if name else resolved_path.name
    proj_type = detect_project_type(resolved_path)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db(db_path) as conn:
        conn.execute(
            """
            INSERT INTO recent_projects (name, path, project_type, last_accessed)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                name=excluded.name,
                project_type=excluded.project_type,
                last_accessed=excluded.last_accessed
            """,
            (proj_name, str(resolved_path), proj_type, now),
        )


def get_recent_projects(limit: int = 10, db_path: Path | None = None) -> list[RecentProject]:
    """Get list of recently accessed projects."""
    with get_db(db_path) as conn:
        rows = conn.execute(
            "SELECT id, name, path, project_type, last_accessed FROM recent_projects ORDER BY last_accessed DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            RecentProject(
                id=row["id"],
                name=row["name"],
                path=row["path"],
                project_type=row["project_type"],
                last_accessed=str(row["last_accessed"]),
            )
            for row in rows
        ]


def remove_recent_project(project_name_id_or_path: str, db_path: Path | None = None) -> bool:
    """Remove a project from recent history without deleting real files."""
    with get_db(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM recent_projects WHERE id = ? OR path = ? OR name = ?",
            (project_name_id_or_path, project_name_id_or_path, project_name_id_or_path),
        )
        return cursor.rowcount > 0
