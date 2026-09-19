from pathlib import Path

import pytest

from cassandra_terminal.modules.generator import (
    generate_project,
    get_available_templates,
    preview_template_structure,
)


def test_get_available_templates():
    templates = get_available_templates()
    keys = [t.key for t in templates]
    assert "python-basic" in keys
    assert "python-cli" in keys
    assert "python-pkg" in keys
    assert "flask-app" in keys
    assert "nextjs-ts" in keys
    assert "static-web" in keys


def test_preview_template_structure():
    files = preview_template_structure("python-cli", "my-tool")
    assert any("cli.py" in f for f in files)
    assert any("pyproject.toml" in f for f in files)


def test_generate_all_templates(sandbox_dir: Path):
    templates = get_available_templates()
    for tpl in templates:
        proj_name = f"proj_{tpl.key.replace('-', '_')}"
        proj_dir = generate_project(
            template_key=tpl.key,
            project_name=proj_name,
            target_dir=sandbox_dir,
            author_name="Tester",
            description="Test description",
        )
        assert proj_dir.exists()
        assert (proj_dir / "README.md").exists()


def test_generator_duplicate_folder_fails(sandbox_dir: Path):
    generate_project("python-basic", "duplicate_app", target_dir=sandbox_dir)
    with pytest.raises(FileExistsError):
        generate_project("python-basic", "duplicate_app", target_dir=sandbox_dir)
