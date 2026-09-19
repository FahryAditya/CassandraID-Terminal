from pathlib import Path

from typer.testing import CliRunner

from cassandra_terminal.cli.main import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "cassandra" in result.output.lower() and "version" in result.output.lower()


def test_cli_templates_list():
    result = runner.invoke(app, ["templates", "list"])
    assert result.exit_code == 0
    assert "python-cli" in result.output
    assert "nextjs-ts" in result.output


def test_cli_files_list(sandbox_dir: Path):
    (sandbox_dir / "sample.txt").write_text("content", encoding="utf-8")
    result = runner.invoke(app, ["files", "list", str(sandbox_dir)])
    assert result.exit_code == 0
    assert "sample.txt" in result.output


def test_cli_workspace_add_and_list(sandbox_dir: Path):
    ws = sandbox_dir / "my_ws"
    ws.mkdir()
    result_add = runner.invoke(app, ["workspace", "add", str(ws), "--name", "TestWS"])
    assert result_add.exit_code == 0
    assert "Registered workspace" in result_add.output

    result_list = runner.invoke(app, ["workspace", "list"])
    assert result_list.exit_code == 0
    assert "TestWS" in result_list.output


def test_cli_create_project(sandbox_dir: Path):
    result = runner.invoke(
        app,
        ["create", "python-basic", "test_app", "--target", str(sandbox_dir), "--author", "Dev"],
    )
    assert result.exit_code == 0
    assert "successfully created" in result.output
    assert (sandbox_dir / "test_app" / "main.py").exists()


def test_cli_settings():
    result = runner.invoke(app, ["settings"])
    assert result.exit_code == 0
    assert "theme" in result.output


def test_cli_dashboard_non_interactive():
    result = runner.invoke(app, ["dashboard", "--no-interactive"])
    assert result.exit_code == 0
    assert "Command Center" in result.output
    assert "Directory" in result.output
