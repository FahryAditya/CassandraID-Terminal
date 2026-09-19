from __future__ import annotations

from pathlib import Path

from cassandra_terminal.modules.finder import calculate_match_score, find_files_fuzzy


def test_calculate_match_score() -> None:
    assert calculate_match_score("main.py", "main.py") == 100.0
    assert calculate_match_score("main", "main.py") == 80.0
    assert calculate_match_score("ai", "main.py") == 60.0
    assert calculate_match_score("xyz123", "abc.txt") == 0.0


def test_find_files_fuzzy(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "index.ts").write_text("console.log('hi');")
    (tmp_path / "src" / "utils.ts").write_text("export const x = 1;")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.js").write_text("ignore me")

    results = find_files_fuzzy("utils", root_dir=tmp_path)
    assert len(results) >= 1
    assert "utils.ts" in results[0].relative_path

    # Verify node_modules is ignored
    ignored = find_files_fuzzy("ignored", root_dir=tmp_path)
    assert len(ignored) == 0
