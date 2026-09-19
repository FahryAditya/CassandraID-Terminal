import os
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from cassandra_terminal.modules.activity import log_activity


@dataclass
class FileItem:
    name: str
    path: Path
    is_dir: bool
    size: int
    modified_time: datetime
    extension: str

    @property
    def formatted_size(self) -> str:
        if self.is_dir:
            return "<DIR>"
        size = float(self.size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:3.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    @property
    def formatted_time(self) -> str:
        return self.modified_time.strftime("%Y-%m-%d %H:%M:%S")


def list_directory(
    target_path: Path,
    sort_by: str = "name",
    reverse: bool = False,
    show_hidden: bool = False,
) -> list[FileItem]:
    """List entries in a directory with file metadata."""
    target = target_path.resolve()
    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {target}")
    if not target.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {target}")

    items: list[FileItem] = []
    for entry in target.iterdir():
        if not show_hidden and entry.name.startswith("."):
            continue
        try:
            stat = entry.stat()
            is_dir = entry.is_dir()
            items.append(
                FileItem(
                    name=entry.name,
                    path=entry,
                    is_dir=is_dir,
                    size=stat.st_size if not is_dir else 0,
                    modified_time=datetime.fromtimestamp(stat.st_mtime),
                    extension=entry.suffix.lower() if not is_dir else "",
                )
            )
        except OSError:
            # In case of permission errors on specific items
            continue

    # Sorting
    if sort_by == "size":
        items.sort(key=lambda x: (not x.is_dir, x.size), reverse=reverse)
    elif sort_by == "date" or sort_by == "modified":
        items.sort(key=lambda x: (not x.is_dir, x.modified_time), reverse=reverse)
    elif sort_by == "type" or sort_by == "ext":
        items.sort(key=lambda x: (not x.is_dir, x.extension, x.name.lower()), reverse=reverse)
    else:  # default 'name'
        items.sort(key=lambda x: (not x.is_dir, x.name.lower()), reverse=reverse)

    return items


def search_files(
    target_path: Path,
    query: str,
    extension: str | None = None,
    recursive: bool = True,
    case_sensitive: bool = False,
    max_results: int = 200,
) -> list[FileItem]:
    """Search for files and directories matching query / extension."""
    target = target_path.resolve()
    if not target.exists():
        raise FileNotFoundError(f"Search path does not exist: {target}")

    query_str = query if case_sensitive else query.lower()
    ext_filter = extension.lower() if extension else None
    if ext_filter and not ext_filter.startswith("."):
        ext_filter = f".{ext_filter}"

    results: list[FileItem] = []

    def match_entry(entry: Path) -> bool:
        entry_name = entry.name if case_sensitive else entry.name.lower()
        if query_str and query_str not in entry_name:
            return False
        if ext_filter and entry.suffix.lower() != ext_filter:
            return False
        return True

    if recursive:
        for root, dirs, files in os.walk(target, followlinks=False):
            # Exclude hidden directories from deep search
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for name in files + dirs:
                full_path = Path(root) / name
                if match_entry(full_path):
                    try:
                        stat = full_path.stat()
                        is_dir = full_path.is_dir()
                        results.append(
                            FileItem(
                                name=name,
                                path=full_path,
                                is_dir=is_dir,
                                size=stat.st_size if not is_dir else 0,
                                modified_time=datetime.fromtimestamp(stat.st_mtime),
                                extension=full_path.suffix.lower() if not is_dir else "",
                            )
                        )
                    except OSError:
                        continue
                if len(results) >= max_results:
                    return results
    else:
        for entry in target.iterdir():
            if match_entry(entry):
                try:
                    stat = entry.stat()
                    is_dir = entry.is_dir()
                    results.append(
                        FileItem(
                            name=entry.name,
                            path=entry,
                            is_dir=is_dir,
                            size=stat.st_size if not is_dir else 0,
                            modified_time=datetime.fromtimestamp(stat.st_mtime),
                            extension=entry.suffix.lower() if not is_dir else "",
                        )
                    )
                except OSError:
                    continue

    return results


def safe_copy(
    src: Path,
    dst: Path,
    overwrite: bool = False,
    confirm_callback: Callable[[str], bool] | None = None,
) -> Path:
    """Safely copy a file or directory with collision detection."""
    src = src.resolve()
    dst = dst.resolve()

    if not src.exists():
        raise FileNotFoundError(f"Source does not exist: {src}")

    # If destination is an existing directory, place copy inside it
    if dst.exists() and dst.is_dir() and not src.is_dir():
        dst = dst / src.name

    if dst.exists() and not overwrite:
        if confirm_callback:
            if not confirm_callback(f"Target '{dst}' already exists. Overwrite?"):
                raise FileExistsError(f"Operation cancelled: '{dst}' already exists.")
        else:
            raise FileExistsError(f"Destination already exists: '{dst}'. Overwrite is False.")

    if src.is_dir():
        if dst.exists() and overwrite:
            shutil.rmtree(dst)
        shutil.copytree(src, dst, dirs_exist_ok=overwrite)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    log_activity(operation="COPY", target=str(src), result="SUCCESS", details=f"Copied to {dst}")
    return dst


def safe_move(
    src: Path,
    dst: Path,
    overwrite: bool = False,
    confirm_callback: Callable[[str], bool] | None = None,
) -> Path:
    """Safely move a file or directory."""
    src = src.resolve()
    dst = dst.resolve()

    if not src.exists():
        raise FileNotFoundError(f"Source does not exist: {src}")

    if dst.exists() and dst.is_dir() and not src.is_dir():
        dst = dst / src.name

    if dst.exists() and not overwrite:
        if confirm_callback:
            if not confirm_callback(f"Target '{dst}' already exists. Overwrite?"):
                raise FileExistsError(f"Operation cancelled: '{dst}' already exists.")
        else:
            raise FileExistsError(f"Destination already exists: '{dst}'. Overwrite is False.")

    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and overwrite:
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()

    shutil.move(str(src), str(dst))
    log_activity(operation="MOVE", target=str(src), result="SUCCESS", details=f"Moved to {dst}")
    return dst


def safe_rename(src: Path, new_name: str) -> Path:
    """Safely rename a file or directory in its current location."""
    src = src.resolve()
    if not src.exists():
        raise FileNotFoundError(f"Source does not exist: {src}")

    if "/" in new_name or "\\" in new_name:
        raise ValueError("New name must be a valid filename, not a path.")

    dst = src.parent / new_name
    if dst.exists():
        raise FileExistsError(f"An item with name '{new_name}' already exists in '{src.parent}'.")

    src.rename(dst)
    log_activity(
        operation="RENAME", target=str(src), result="SUCCESS", details=f"Renamed to {dst.name}"
    )
    return dst


def safe_delete(
    target: Path,
    recursive: bool = False,
    confirm_callback: Callable[[str], bool] | None = None,
) -> None:
    """Safely delete a file or directory with confirmation requirement."""
    target = target.resolve()
    if not target.exists():
        raise FileNotFoundError(f"Target does not exist: {target}")

    if target.is_dir() and not recursive:
        # Check if dir is empty
        if any(target.iterdir()):
            raise OSError(
                f"Directory '{target}' is not empty. Use recursive flag to delete non-empty directories."
            )

    if confirm_callback:
        msg = f"Are you sure you want to permanently delete {'directory' if target.is_dir() else 'file'}: '{target}'?"
        if not confirm_callback(msg):
            raise PermissionError("Deletion cancelled by user confirmation.")

    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()

    log_activity(
        operation="DELETE", target=str(target), result="SUCCESS", details="Permanently deleted"
    )


@dataclass
class OrganizePlan:
    source: Path
    destination: Path
    category: str
    collision: bool = False


ORGANIZER_CATEGORIES = {
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp"],
    "Documents": [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".txt", ".md", ".csv"],
    "Code": [
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".html",
        ".css",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".sql",
        ".rs",
        ".go",
        ".c",
        ".cpp",
    ],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z", ".bz2"],
    "Audio_Video": [".mp3", ".wav", ".mp4", ".mkv", ".mov", ".avi", ".flac"],
}


def plan_organize(
    directory: Path,
    custom_rules: dict[str, list[str]] | None = None,
) -> list[OrganizePlan]:
    """Generate a file organization plan based on categories."""
    target_dir = directory.resolve()
    if not target_dir.exists() or not target_dir.is_dir():
        raise NotADirectoryError(f"Target is not a valid directory: {target_dir}")

    rules = custom_rules or ORGANIZER_CATEGORIES
    ext_to_cat: dict[str, str] = {}
    for cat, exts in rules.items():
        for ext in exts:
            ext_to_cat[ext.lower()] = cat

    plans: list[OrganizePlan] = []
    for item in target_dir.iterdir():
        if item.is_dir() or item.name.startswith("."):
            continue
        ext = item.suffix.lower()
        category = ext_to_cat.get(ext, "Others")
        dest_folder = target_dir / category
        dest_file = dest_folder / item.name
        plans.append(
            OrganizePlan(
                source=item,
                destination=dest_file,
                category=category,
                collision=dest_file.exists(),
            )
        )
    return plans


def execute_organize(
    plans: list[OrganizePlan],
    dry_run: bool = False,
) -> int:
    """Execute organization plans."""
    if dry_run:
        return len(plans)

    moved_count = 0
    for plan in plans:
        if plan.collision:
            continue
        plan.destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(plan.source), str(plan.destination))
        moved_count += 1

    log_activity(
        operation="ORGANIZE",
        target=str(plans[0].source.parent) if plans else "none",
        result="SUCCESS",
        details=f"Organized {moved_count} files into categorized directories.",
    )
    return moved_count
