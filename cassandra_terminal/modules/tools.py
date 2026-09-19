import hashlib
import os
import re
import shutil
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from cassandra_terminal.modules.activity import log_activity


@dataclass
class DuplicateGroup:
    file_hash: str
    file_size: int
    files: list[Path]


@dataclass
class DirectorySizeItem:
    name: str
    path: Path
    size_bytes: int
    is_junk_candidate: bool = False

    @property
    def formatted_size(self) -> str:
        size = float(self.size_bytes)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:3.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"


@dataclass
class RenamePlanItem:
    original_path: Path
    new_path: Path
    collision: bool = False


# Known junk / heavy build folders that developers often clean
KNOWN_JUNK_FOLDERS = {
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "dist",
    "build",
    ".next",
    ".turbo",
    ".nuxt",
    ".output",
    "target",
    "bin",
    "obj",
    ".cache",
}


# --- 1. Duplicate File Finder ---


def compute_file_hash(file_path: Path, chunk_size: int = 65536) -> str:
    """Compute SHA-256 hash of a file using buffered reading."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicate_files(target_dir: Path, min_size_bytes: int = 1) -> list[DuplicateGroup]:
    """Scan directory recursively to find duplicate files based on content hash."""
    target = target_dir.resolve()
    if not target.exists() or not target.is_dir():
        raise NotADirectoryError(f"Target is not a directory: {target}")

    # Group files by size first (quick filter)
    size_map: dict[int, list[Path]] = {}
    for root, dirs, files in os.walk(target, followlinks=False):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file_name in files:
            full_path = Path(root) / file_name
            try:
                st = full_path.stat()
                if st.st_size >= min_size_bytes and not full_path.is_symlink():
                    size_map.setdefault(st.st_size, []).append(full_path)
            except OSError:
                continue

    # For sizes with multiple files, compare hashes
    hash_map: dict[tuple[int, str], list[Path]] = {}
    for size, paths in size_map.items():
        if len(paths) < 2:
            continue
        for p in paths:
            try:
                f_hash = compute_file_hash(p)
                hash_map.setdefault((size, f_hash), []).append(p)
            except OSError:
                continue

    duplicate_groups: list[DuplicateGroup] = []
    for (size, f_hash), paths in hash_map.items():
        if len(paths) > 1:
            duplicate_groups.append(
                DuplicateGroup(
                    file_hash=f_hash,
                    file_size=size,
                    files=paths,
                )
            )

    duplicate_groups.sort(key=lambda g: g.file_size * (len(g.files) - 1), reverse=True)
    return duplicate_groups


# --- 2. Disk Usage Analyzer & Cleaner ---


def get_directory_size(path: Path) -> int:
    """Recursively calculate total bytes in a directory."""
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file() and not entry.is_symlink():
                try:
                    total += entry.stat().st_size
                except OSError:
                    continue
    except OSError:
        pass
    return total


def analyze_disk_usage(target_dir: Path) -> list[DirectorySizeItem]:
    """Scan immediate subdirectories and report their sizes."""
    target = target_dir.resolve()
    if not target.exists() or not target.is_dir():
        raise NotADirectoryError(f"Target is not a directory: {target}")

    items: list[DirectorySizeItem] = []
    for entry in target.iterdir():
        if entry.is_dir():
            size = get_directory_size(entry)
            is_junk = entry.name.lower() in KNOWN_JUNK_FOLDERS
            items.append(
                DirectorySizeItem(
                    name=entry.name,
                    path=entry,
                    size_bytes=size,
                    is_junk_candidate=is_junk,
                )
            )

    items.sort(key=lambda x: x.size_bytes, reverse=True)
    return items


def clean_junk_directories(
    target_dir: Path,
    targets: list[str] | None = None,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Clean junk/cache folders. Returns (folders_removed_count, freed_bytes)."""
    target = target_dir.resolve()
    junk_names = set(targets) if targets else KNOWN_JUNK_FOLDERS

    cleaned_count = 0
    freed_bytes = 0

    candidates: list[Path] = []
    for root, dirs, _ in os.walk(target, followlinks=False):
        for d in dirs:
            if d.lower() in junk_names:
                candidates.append(Path(root) / d)

    for folder in candidates:
        if folder.exists() and folder.is_dir():
            size = get_directory_size(folder)
            freed_bytes += size
            cleaned_count += 1
            if not dry_run:
                shutil.rmtree(folder, ignore_errors=True)

    if not dry_run and cleaned_count > 0:
        log_activity(
            operation="DISK_CLEAN",
            target=str(target),
            result="SUCCESS",
            details=f"Cleaned {cleaned_count} junk directories, freed {freed_bytes} bytes",
        )

    return cleaned_count, freed_bytes


# --- 3. Batch Renamer ---


def plan_batch_rename(
    target_dir: Path,
    pattern: str = "",
    replacement: str = "",
    prefix: str = "",
    suffix: str = "",
    numbering: bool = False,
    start_number: int = 1,
) -> list[RenamePlanItem]:
    """Preview batch rename operations on files in a directory."""
    target = target_dir.resolve()
    if not target.exists() or not target.is_dir():
        raise NotADirectoryError(f"Target is not a directory: {target}")

    plans: list[RenamePlanItem] = []
    entries = sorted(
        [f for f in target.iterdir() if f.is_file() and not f.name.startswith(".")],
        key=lambda x: x.name.lower(),
    )

    for idx, f in enumerate(entries):
        stem = f.stem
        ext = f.suffix

        new_stem = stem
        if pattern:
            new_stem = re.sub(pattern, replacement, new_stem)

        if numbering:
            new_stem = f"{new_stem}_{start_number + idx:03d}"

        new_name = f"{prefix}{new_stem}{suffix}{ext}"
        new_path = target / new_name

        collision = new_path.exists() and new_path != f
        plans.append(RenamePlanItem(original_path=f, new_path=new_path, collision=collision))

    return plans


def execute_batch_rename(plans: list[RenamePlanItem], dry_run: bool = False) -> int:
    """Execute batch rename plan."""
    if dry_run:
        return len(plans)

    renamed_count = 0
    for plan in plans:
        if plan.collision or plan.original_path == plan.new_path:
            continue
        plan.original_path.rename(plan.new_path)
        renamed_count += 1

    if renamed_count > 0:
        log_activity(
            operation="BATCH_RENAME",
            target=str(plans[0].original_path.parent) if plans else "none",
            result="SUCCESS",
            details=f"Batch renamed {renamed_count} files",
        )
    return renamed_count


# --- 4. Archive Tools (Zip & Tar with Zip-Slip protection) ---


def create_archive(
    source_path: Path, output_file: Path | None = None, archive_type: str = "zip"
) -> Path:
    """Create a zip or tar.gz archive from a file or folder."""
    src = source_path.resolve()
    if not src.exists():
        raise FileNotFoundError(f"Source does not exist: {src}")

    if not output_file:
        out_ext = ".zip" if archive_type == "zip" else ".tar.gz"
        out_path = src.parent / f"{src.name}{out_ext}"
    else:
        out_path = output_file.resolve()

    out_path.parent.mkdir(parents=True, exist_ok=True)

    if archive_type == "zip":
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if src.is_dir():
                for root, _, files in os.walk(src):
                    for file in files:
                        full_p = Path(root) / file
                        rel_p = full_p.relative_to(src.parent)
                        zf.write(full_p, rel_p)
            else:
                zf.write(src, src.name)
    else:  # tar.gz
        with tarfile.open(out_path, "w:gz") as tf:
            tf.add(src, arcname=src.name)

    log_activity(
        operation="ARCHIVE_CREATE",
        target=str(src),
        result="SUCCESS",
        details=f"Created {out_path.name}",
    )
    return out_path


def extract_archive(archive_file: Path, dest_dir: Path | None = None) -> Path:
    """Extract a zip or tar archive safely with path traversal (Zip Slip) prevention."""
    archive = archive_file.resolve()
    if not archive.exists():
        raise FileNotFoundError(f"Archive file does not exist: {archive}")

    dest = dest_dir.resolve() if dest_dir else archive.parent / archive.stem
    dest.mkdir(parents=True, exist_ok=True)

    if archive.suffix.lower() == ".zip":
        with zipfile.ZipFile(archive, "r") as zf:
            for member in zf.infolist():
                # Security: prevent path traversal attacks
                target_path = (dest / member.filename).resolve()
                try:
                    target_path.relative_to(dest)
                except ValueError:
                    raise PermissionError(
                        f"Security error: archive member '{member.filename}' attempts path traversal."
                    )
            zf.extractall(dest)
    elif ".tar" in archive.name.lower():
        with tarfile.open(archive, "r:*") as tf:
            for member in tf.getmembers():
                target_path = (dest / member.name).resolve()
                try:
                    target_path.relative_to(dest)
                except ValueError:
                    raise PermissionError(
                        f"Security error: tar member '{member.name}' attempts path traversal."
                    )
            tf.extractall(dest)
    else:
        raise ValueError(
            f"Unsupported archive format: '{archive.suffix}'. Supported: .zip, .tar, .tar.gz"
        )

    log_activity(
        operation="ARCHIVE_EXTRACT",
        target=str(archive),
        result="SUCCESS",
        details=f"Extracted to {dest}",
    )
    return dest
