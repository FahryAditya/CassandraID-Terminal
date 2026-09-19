from __future__ import annotations

import difflib
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

DEFAULT_IGNORES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".idea",
    ".vscode",
    ".gemini",
    ".agents",
    "target",
}


@dataclass
class FoundFile:
    path: Path
    relative_path: str
    score: float
    size: int
    is_dir: bool


def find_files_fuzzy(
    query: str,
    root_dir: Path | None = None,
    limit: int = 25,
    include_dirs: bool = False,
    ignore_patterns: set[str] | None = None,
) -> list[FoundFile]:
    """Find files matching the query with fuzzy scoring."""
    root = (root_dir or Path.cwd()).resolve()
    ignores = ignore_patterns or DEFAULT_IGNORES
    query_lower = query.lower().strip()

    matches: list[FoundFile] = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter out ignored directories in-place for speed
        dirnames[:] = [d for d in dirnames if d not in ignores and not d.startswith(".")]

        current_dir = Path(dirpath)

        if include_dirs:
            for dirname in dirnames:
                dir_full = current_dir / dirname
                rel_path = str(dir_full.relative_to(root)).replace("\\", "/")
                score = calculate_match_score(query_lower, rel_path.lower())
                if score > 0:
                    matches.append(
                        FoundFile(
                            path=dir_full,
                            relative_path=rel_path + "/",
                            score=score,
                            size=0,
                            is_dir=True,
                        )
                    )

        for filename in filenames:
            file_full = current_dir / filename
            rel_path = str(file_full.relative_to(root)).replace("\\", "/")
            score = calculate_match_score(query_lower, rel_path.lower())
            if score > 0:
                try:
                    size = file_full.stat().st_size
                except Exception:
                    size = 0

                matches.append(
                    FoundFile(
                        path=file_full,
                        relative_path=rel_path,
                        score=score,
                        size=size,
                        is_dir=False,
                    )
                )

    # Sort primarily by score descending, then by shortest path
    matches.sort(key=lambda x: (-x.score, len(x.relative_path)))
    return matches[:limit]


def calculate_match_score(query: str, target: str) -> float:
    """Calculate matching score between query and target path."""
    if not query:
        return 1.0

    target_name = Path(target).name.lower()
    # Exact name match gets highest score
    if query == target_name:
        return 100.0
    # Prefix match on filename
    if target_name.startswith(query):
        return 80.0
    # Substring in filename
    if query in target_name:
        return 60.0
    # Substring in full path
    if query in target:
        return 40.0

    # Fuzzy ratio using SequenceMatcher
    ratio = difflib.SequenceMatcher(None, query, target_name).ratio()
    if ratio > 0.4:
        return ratio * 30.0

    return 0.0


def open_file_in_editor(file_path: Path, editor: str | None = None) -> bool:
    """Open a file using the specified editor or system default."""
    resolved = file_path.resolve()
    target_str = str(resolved)

    if editor:
        editor_exe = shutil.which(editor) or editor
        try:
            subprocess.Popen([editor_exe, target_str], shell=False)
            return True
        except Exception:
            pass

    # Try common popular editors first if available
    for candidate in ["code", "cursor", "subl", "nvim", "vim"]:
        if shutil.which(candidate):
            try:
                subprocess.Popen([candidate, target_str], shell=False)
                return True
            except Exception:
                continue

    # Fallback to system default handler
    try:
        if os.name == "nt":
            os.startfile(target_str)  # type: ignore[attr-defined]
            return True
        elif os.name == "posix":
            cmd = "open" if "darwin" in os.sys.platform else "xdg-open"
            subprocess.Popen([cmd, target_str])
            return True
    except Exception:
        pass

    return False
