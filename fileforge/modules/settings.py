from pathlib import Path

from fileforge.db.connection import get_db

DEFAULT_SETTINGS = {
    "theme": "deep-space",
    "require_confirmation": "true",
    "default_workspace": "",
    "max_tree_depth": "4",
    "recent_projects_limit": "10",
}

# Safeguards that cannot be disabled
PROTECTED_SETTINGS = {
    "require_confirmation": ["true"],
}


def get_setting(key: str, default: str | None = None, db_path: Path | None = None) -> str:
    """Get a setting value, falling back to defaults."""
    with get_db(db_path) as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if row:
            return row["value"]
    return default if default is not None else DEFAULT_SETTINGS.get(key, "")


def get_all_settings(db_path: Path | None = None) -> dict[str, str]:
    """Get all settings merged with default settings."""
    settings = dict(DEFAULT_SETTINGS)
    with get_db(db_path) as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        for row in rows:
            settings[row["key"]] = row["value"]
    return settings


def set_setting(key: str, value: str, db_path: Path | None = None) -> None:
    """Set a setting value with validation against safety guards."""
    key = key.strip()
    value = str(value).strip()

    # Safety guard: destructive confirmation safeguard cannot be casually disabled
    if key == "require_confirmation" and value.lower() in ("false", "0", "no"):
        raise ValueError(
            "Destructive action safeguards ('require_confirmation') cannot be disabled in settings."
        )

    with get_db(db_path) as conn:
        conn.execute(
            """
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (key, value),
        )
