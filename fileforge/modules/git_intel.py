import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitStatus:
    is_repo: bool
    branch: str = ""
    is_clean: bool = True
    staged_count: int = 0
    modified_count: int = 0
    untracked_count: int = 0
    last_commit: str = ""


@dataclass
class HealthCheck:
    name: str
    passed: bool
    description: str


@dataclass
class ProjectHealth:
    score: int
    checks: list[HealthCheck]
    suggestions: list[str]


def get_git_status(path: Path) -> GitStatus:
    """Safely inspect git repository status for a given directory."""
    target = path.resolve()
    if not (target / ".git").exists() or not shutil.which("git"):
        return GitStatus(is_repo=False)

    try:
        # Get active branch name
        branch_res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(target),
            capture_output=True,
            text=True,
            check=False,
        )
        branch = branch_res.stdout.strip() if branch_res.returncode == 0 else "HEAD"

        # Get status porcelain
        status_res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(target),
            capture_output=True,
            text=True,
            check=False,
        )

        staged = 0
        modified = 0
        untracked = 0

        if status_res.returncode == 0:
            lines = status_res.stdout.splitlines()
            for line in lines:
                if not line.strip():
                    continue
                index_status = line[0] if len(line) > 0 else " "
                work_status = line[1] if len(line) > 1 else " "

                if index_status in ("M", "A", "D", "R", "C"):
                    staged += 1
                if work_status in ("M", "D"):
                    modified += 1
                if index_status == "?" and work_status == "?":
                    untracked += 1

        is_clean = staged == 0 and modified == 0 and untracked == 0

        # Get last commit message
        commit_res = subprocess.run(
            ["git", "log", "-1", "--format=%h - %s (%cr)"],
            cwd=str(target),
            capture_output=True,
            text=True,
            check=False,
        )
        last_commit = commit_res.stdout.strip() if commit_res.returncode == 0 else "No commits yet"

        return GitStatus(
            is_repo=True,
            branch=branch,
            is_clean=is_clean,
            staged_count=staged,
            modified_count=modified,
            untracked_count=untracked,
            last_commit=last_commit,
        )
    except Exception:
        return GitStatus(
            is_repo=True, branch="unknown", is_clean=True, last_commit="Error reading git"
        )


def check_project_health(path: Path) -> ProjectHealth:
    """Analyze repository and codebase health based on standard developer hygiene."""
    target = path.resolve()
    checks: list[HealthCheck] = []
    suggestions: list[str] = []

    files = (
        {f.name.lower() for f in target.iterdir() if f.is_file()}
        if target.exists() and target.is_dir()
        else set()
    )
    dirs = (
        {d.name.lower() for d in target.iterdir() if d.is_dir()}
        if target.exists() and target.is_dir()
        else set()
    )

    # 1. Check README
    has_readme = any("readme" in f for f in files)
    checks.append(
        HealthCheck(
            name="Documentation (README)",
            passed=has_readme,
            description="Project overview and documentation file exists",
        )
    )
    if not has_readme:
        suggestions.append("Create a README.md to document project purpose and instructions.")

    # 2. Check .gitignore
    has_gitignore = ".gitignore" in files
    checks.append(
        HealthCheck(
            name="Version Control (.gitignore)",
            passed=has_gitignore,
            description="Ignore rules to prevent tracking virtualenvs, secrets, and caches",
        )
    )
    if not has_gitignore:
        suggestions.append(
            "Add a .gitignore file to avoid accidentally committing build artifacts and secrets."
        )

    # 3. Check License
    has_license = any("license" in f or "copying" in f for f in files)
    checks.append(
        HealthCheck(
            name="License (LICENSE)",
            passed=has_license,
            description="Open-source or proprietary software license defined",
        )
    )
    if not has_license:
        suggestions.append(
            "Add a LICENSE file (e.g. MIT, Apache-2.0) to clarify code usage rights."
        )

    # 4. Check Tests directory
    has_tests = ("tests" in dirs) or ("test" in dirs) or ("__tests__" in dirs)
    checks.append(
        HealthCheck(
            name="Test Suite (tests/)",
            passed=has_tests,
            description="Automated tests directory configured",
        )
    )
    if not has_tests:
        suggestions.append("Create a tests/ directory to write unit and integration tests.")

    # 5. Check Linter / Config
    has_linter = any(
        f in files
        for f in (
            "pyproject.toml",
            "ruff.toml",
            ".eslintrc",
            ".eslintrc.json",
            ".eslintrc.js",
            "biome.json",
            ".prettierrc",
            "cargo.toml",
        )
    )
    checks.append(
        HealthCheck(
            name="Code Quality / Tooling Config",
            passed=has_linter,
            description="Linter, formatter, or project configuration file present",
        )
    )
    if not has_linter:
        suggestions.append(
            "Configure a linter/formatter config file (e.g., pyproject.toml or biome.json)."
        )

    # Calculate Score
    passed_count = sum(1 for c in checks if c.passed)
    score = int((passed_count / len(checks)) * 100) if checks else 100

    return ProjectHealth(score=score, checks=checks, suggestions=suggestions)
