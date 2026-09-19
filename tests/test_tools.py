from pathlib import Path

from cassandra_terminal.modules.git_intel import check_project_health, get_git_status
from cassandra_terminal.modules.tools import (
    analyze_disk_usage,
    clean_junk_directories,
    create_archive,
    execute_batch_rename,
    extract_archive,
    find_duplicate_files,
    plan_batch_rename,
)


def test_find_duplicate_files(sandbox_dir: Path):
    (sandbox_dir / "original.txt").write_text("duplicate content 123", encoding="utf-8")
    (sandbox_dir / "copy.txt").write_text("duplicate content 123", encoding="utf-8")
    (sandbox_dir / "unique.txt").write_text("unique content 456", encoding="utf-8")

    dupes = find_duplicate_files(sandbox_dir)
    assert len(dupes) == 1
    assert len(dupes[0].files) == 2


def test_analyze_and_clean_disk_usage(sandbox_dir: Path):
    junk_folder = sandbox_dir / "node_modules"
    junk_folder.mkdir()
    (junk_folder / "dummy.js").write_text("console.log(1)", encoding="utf-8")

    usage = analyze_disk_usage(sandbox_dir)
    assert any(item.name == "node_modules" and item.is_junk_candidate for item in usage)

    cleaned_count, freed = clean_junk_directories(sandbox_dir, dry_run=False)
    assert cleaned_count == 1
    assert freed > 0
    assert not junk_folder.exists()


def test_batch_rename(sandbox_dir: Path):
    (sandbox_dir / "doc_a.txt").write_text("a", encoding="utf-8")
    (sandbox_dir / "doc_b.txt").write_text("b", encoding="utf-8")

    plans = plan_batch_rename(sandbox_dir, pattern="doc_", replacement="file_")
    assert len(plans) == 2

    renamed = execute_batch_rename(plans, dry_run=False)
    assert renamed == 2
    assert (sandbox_dir / "file_a.txt").exists()
    assert (sandbox_dir / "file_b.txt").exists()


def test_create_and_extract_archive(sandbox_dir: Path):
    src_folder = sandbox_dir / "my_data"
    src_folder.mkdir()
    (src_folder / "info.txt").write_text("important data", encoding="utf-8")

    archive_path = create_archive(src_folder, archive_type="zip")
    assert archive_path.exists()

    extract_dest = sandbox_dir / "extracted_data"
    extract_archive(archive_path, dest_dir=extract_dest)
    assert (extract_dest / "my_data" / "info.txt").exists()


def test_project_health_check(sandbox_dir: Path):
    (sandbox_dir / "README.md").write_text("# Test", encoding="utf-8")
    (sandbox_dir / ".gitignore").write_text(".venv", encoding="utf-8")

    health = check_project_health(sandbox_dir)
    assert health.score >= 40
    assert any(c.name == "Documentation (README)" and c.passed for c in health.checks)


def test_git_status_non_git_dir(sandbox_dir: Path):
    git = get_git_status(sandbox_dir)
    assert git.is_repo is False
