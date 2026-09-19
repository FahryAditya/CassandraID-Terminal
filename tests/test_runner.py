from __future__ import annotations

import json
from pathlib import Path

from cassandra_terminal.modules.runner import detect_project_scripts


def test_detect_scripts_package_json(tmp_path: Path) -> None:
    pkg = tmp_path / "package.json"
    pkg.write_text(
        json.dumps(
            {
                "name": "test-pkg",
                "scripts": {"dev": "vite", "build": "vite build", "test": "vitest"},
            }
        ),
        encoding="utf-8",
    )

    scripts = detect_project_scripts(tmp_path)
    names = [s.name for s in scripts]
    assert "dev" in names
    assert "build" in names
    assert "test" in names
    assert any(s.source == "package.json" for s in scripts)


def test_detect_scripts_makefile(tmp_path: Path) -> None:
    makefile = tmp_path / "Makefile"
    makefile.write_text(
        "build:\n\t@echo 'Building'\n\ntest:\n\tpytest\n",
        encoding="utf-8",
    )

    scripts = detect_project_scripts(tmp_path)
    names = [s.name for s in scripts]
    assert "build" in names
    assert "test" in names
    assert any(s.source == "Makefile" for s in scripts)


def test_detect_scripts_empty_dir(tmp_path: Path) -> None:
    scripts = detect_project_scripts(tmp_path)
    assert scripts == []
