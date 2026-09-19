from pathlib import Path

from cassandra_terminal.modules.workspace import (
    add_workspace,
    detect_project_type,
    get_recent_projects,
    list_workspaces,
    record_recent_project,
    remove_recent_project,
    remove_workspace,
)


def test_detect_project_type(sandbox_dir: Path):
    py_dir = sandbox_dir / "py_proj"
    py_dir.mkdir()
    (py_dir / "pyproject.toml").write_text("", encoding="utf-8")
    assert detect_project_type(py_dir) == "Python"

    node_dir = sandbox_dir / "node_proj"
    node_dir.mkdir()
    (node_dir / "package.json").write_text("{}", encoding="utf-8")
    assert detect_project_type(node_dir) == "Node.js"

    rust_dir = sandbox_dir / "rust_proj"
    rust_dir.mkdir()
    (rust_dir / "Cargo.toml").write_text("", encoding="utf-8")
    assert detect_project_type(rust_dir) == "Rust"


def test_workspace_crud(sandbox_dir: Path):
    ws_path = sandbox_dir / "my_workspace"
    ws_path.mkdir()

    ws = add_workspace(ws_path, name="Workspace 1")
    assert ws.name == "Workspace 1"

    workspaces = list_workspaces()
    assert len(workspaces) == 1
    assert workspaces[0].name == "Workspace 1"

    removed = remove_workspace("Workspace 1")
    assert removed is True
    assert len(list_workspaces()) == 0


def test_recent_projects(sandbox_dir: Path):
    proj_path = sandbox_dir / "proj_x"
    proj_path.mkdir()

    record_recent_project(proj_path, name="Proj X")
    recents = get_recent_projects()
    assert len(recents) == 1
    assert recents[0].name == "Proj X"

    remove_recent_project("Proj X")
    assert len(get_recent_projects()) == 0
