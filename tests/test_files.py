from pathlib import Path

import pytest

from fileforge.modules.files import (
    execute_organize,
    list_directory,
    plan_organize,
    safe_copy,
    safe_delete,
    safe_move,
    safe_rename,
    search_files,
)


def test_list_directory(sandbox_dir: Path):
    (sandbox_dir / "file1.txt").write_text("hello", encoding="utf-8")
    (sandbox_dir / "file2.py").write_text("print(1)", encoding="utf-8")
    sub = sandbox_dir / "subdir"
    sub.mkdir()

    items = list_directory(sandbox_dir)
    assert len(items) == 3
    names = [item.name for item in items]
    assert "file1.txt" in names
    assert "file2.py" in names
    assert "subdir" in names


def test_search_files(sandbox_dir: Path):
    sub = sandbox_dir / "nested"
    sub.mkdir()
    (sandbox_dir / "app.py").write_text("pass", encoding="utf-8")
    (sub / "helper.py").write_text("pass", encoding="utf-8")
    (sub / "style.css").write_text("body {}", encoding="utf-8")

    results_py = search_files(sandbox_dir, query="", extension="py", recursive=True)
    assert len(results_py) == 2

    results_helper = search_files(sandbox_dir, query="helper", recursive=True)
    assert len(results_helper) == 1
    assert results_helper[0].name == "helper.py"


def test_safe_copy_and_move(sandbox_dir: Path):
    src_file = sandbox_dir / "test.txt"
    src_file.write_text("content", encoding="utf-8")
    dst_file = sandbox_dir / "test_copy.txt"

    # Test copy
    safe_copy(src_file, dst_file)
    assert dst_file.exists()
    assert dst_file.read_text(encoding="utf-8") == "content"

    # Test move
    moved_file = sandbox_dir / "test_moved.txt"
    safe_move(dst_file, moved_file)
    assert moved_file.exists()
    assert not dst_file.exists()


def test_safe_copy_collision_no_overwrite(sandbox_dir: Path):
    src = sandbox_dir / "a.txt"
    dst = sandbox_dir / "b.txt"
    src.write_text("a", encoding="utf-8")
    dst.write_text("b", encoding="utf-8")

    with pytest.raises(FileExistsError):
        safe_copy(src, dst, overwrite=False)


def test_safe_rename(sandbox_dir: Path):
    src = sandbox_dir / "old.txt"
    src.write_text("hello", encoding="utf-8")

    renamed = safe_rename(src, "new.txt")
    assert renamed.exists()
    assert not src.exists()
    assert renamed.name == "new.txt"


def test_safe_delete(sandbox_dir: Path):
    file_to_del = sandbox_dir / "delete_me.txt"
    file_to_del.write_text("bye", encoding="utf-8")

    safe_delete(file_to_del)
    assert not file_to_del.exists()


def test_organize_files_dry_run_and_apply(sandbox_dir: Path):
    (sandbox_dir / "photo.jpg").write_text("img", encoding="utf-8")
    (sandbox_dir / "script.py").write_text("py", encoding="utf-8")
    (sandbox_dir / "document.pdf").write_text("pdf", encoding="utf-8")

    plans = plan_organize(sandbox_dir)
    assert len(plans) == 3

    # Dry run shouldn't move files
    execute_organize(plans, dry_run=True)
    assert (sandbox_dir / "photo.jpg").exists()

    # Execute move
    moved = execute_organize(plans, dry_run=False)
    assert moved == 3
    assert (sandbox_dir / "Images" / "photo.jpg").exists()
    assert (sandbox_dir / "Code" / "script.py").exists()
    assert (sandbox_dir / "Documents" / "document.pdf").exists()
