import os
from pathlib import Path

import pytest

from fileforge.db.connection import init_db


@pytest.fixture(autouse=True)
def test_db(tmp_path: Path):
    """Fixture to ensure all tests use an isolated temporary SQLite database."""
    db_file = tmp_path / "test_fileforge.db"
    os.environ["FILEFORGE_DB_PATH"] = str(db_file)
    init_db(db_file)
    yield db_file
    if "FILEFORGE_DB_PATH" in os.environ:
        del os.environ["FILEFORGE_DB_PATH"]


@pytest.fixture
def sandbox_dir(tmp_path: Path) -> Path:
    """Fixture to provide a clean temporary sandbox directory for file operations."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir(parents=True, exist_ok=True)
    return sandbox
