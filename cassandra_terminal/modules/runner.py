from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectScript:
    name: str
    command: str
    source: str  # package.json, pyproject.toml, Makefile, Cargo.toml, scripts/
    description: str = ""


def detect_project_scripts(directory: Path | None = None) -> list[ProjectScript]:
    """Detect available runnable scripts in the specified or current directory."""
    dir_path = directory or Path.cwd()
    scripts: list[ProjectScript] = []

    # 1. Check package.json (Node.js / npm / yarn / pnpm / bun)
    pkg_file = dir_path / "package.json"
    if pkg_file.exists() and pkg_file.is_file():
        try:
            data = json.loads(pkg_file.read_text(encoding="utf-8"))
            if "scripts" in data and isinstance(data["scripts"], dict):
                # Detect package manager
                pm = "npm run"
                if (dir_path / "pnpm-lock.yaml").exists() and shutil.which("pnpm"):
                    pm = "pnpm"
                elif (dir_path / "yarn.lock").exists() and shutil.which("yarn"):
                    pm = "yarn"
                elif (dir_path / "bun.lockb").exists() or (dir_path / "bun.lock").exists():
                    if shutil.which("bun"):
                        pm = "bun run"

                for script_name, cmd in data["scripts"].items():
                    scripts.append(
                        ProjectScript(
                            name=script_name,
                            command=f"{pm} {script_name}",
                            source="package.json",
                            description=str(cmd),
                        )
                    )
        except Exception:
            pass

    # 2. Check pyproject.toml (Python / Poetry / PDM / Flit / Scripts)
    pyproject_file = dir_path / "pyproject.toml"
    if pyproject_file.exists() and pyproject_file.is_file():
        try:
            content = pyproject_file.read_text(encoding="utf-8")
            # Parse [project.scripts] or [tool.poetry.scripts]
            in_scripts_section = False
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("[") and stripped.endswith("]"):
                    in_scripts_section = any(
                        s in stripped
                        for s in [
                            "project.scripts",
                            "tool.poetry.scripts",
                            "tool.pdm.scripts",
                            "tool.hatch.envs",
                        ]
                    )
                    continue
                if in_scripts_section and "=" in stripped and not stripped.startswith("#"):
                    name, _, cmd = stripped.partition("=")
                    name = name.strip()
                    cmd = cmd.strip().strip('"').strip("'")
                    if name:
                        scripts.append(
                            ProjectScript(
                                name=name,
                                command=f"python -m {cmd}" if not cmd.startswith("python") else cmd,
                                source="pyproject.toml",
                                description=f"Entrypoint: {cmd}",
                            )
                        )
        except Exception:
            pass

    # 3. Check Makefile
    makefile = dir_path / "Makefile"
    if not makefile.exists():
        makefile = dir_path / "makefile"
    if makefile.exists() and makefile.is_file():
        try:
            content = makefile.read_text(encoding="utf-8")
            for line in content.splitlines():
                if (
                    line
                    and not line.startswith("\t")
                    and not line.startswith(" ")
                    and ":" in line
                    and not line.startswith("#")
                ):
                    target = line.split(":")[0].strip()
                    if target and not target.startswith(".") and "%" not in target:
                        scripts.append(
                            ProjectScript(
                                name=target,
                                command=f"make {target}",
                                source="Makefile",
                                description=f"Target: {target}",
                            )
                        )
        except Exception:
            pass

    # 4. Check Cargo.toml (Rust)
    cargo_file = dir_path / "Cargo.toml"
    if cargo_file.exists() and cargo_file.is_file():
        scripts.append(
            ProjectScript(
                name="run",
                command="cargo run",
                source="Cargo.toml",
                description="Run default binary target",
            )
        )
        scripts.append(
            ProjectScript(
                name="test",
                command="cargo test",
                source="Cargo.toml",
                description="Run all cargo tests",
            )
        )
        scripts.append(
            ProjectScript(
                name="build",
                command="cargo build",
                source="Cargo.toml",
                description="Build cargo debug binary",
            )
        )

    # 5. Check conventional scripts/ or bin/ folder
    for folder_name in ["scripts", "bin"]:
        folder = dir_path / folder_name
        if folder.exists() and folder.is_dir():
            for item in sorted(folder.iterdir()):
                if item.is_file() and not item.name.startswith("."):
                    ext = item.suffix.lower()
                    if ext in [".py", ".sh", ".bash", ".ps1", ".bat", ".cmd", ".js", ".ts", ""]:
                        cmd = str(item.relative_to(dir_path))
                        if ext == ".py":
                            cmd = f"python {cmd}"
                        elif ext == ".js":
                            cmd = f"node {cmd}"
                        elif ext == ".ts":
                            cmd = f"npx ts-node {cmd}"
                        elif ext == ".sh":
                            cmd = f"bash {cmd}"
                        elif ext in [".bat", ".cmd", ".ps1"] and os.name == "nt":
                            cmd = str(item.resolve())

                        scripts.append(
                            ProjectScript(
                                name=f"{folder_name}/{item.name}",
                                command=cmd,
                                source=f"{folder_name}/",
                                description=f"Script file in {folder_name}/",
                            )
                        )

    return scripts


def execute_script(command: str, cwd: Path | None = None) -> int:
    """Execute a script command directly with inherited terminal I/O."""
    work_dir = cwd or Path.cwd()
    try:
        process = subprocess.Popen(command, shell=True, cwd=work_dir)
        process.communicate()
        return process.returncode
    except KeyboardInterrupt:
        return 130
    except Exception as err:
        raise RuntimeError(f"Failed to execute command '{command}': {err}") from err
