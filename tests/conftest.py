"""Shared test configuration and fixtures for EnvGuard tests."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Click CliRunner for testing CLI commands."""
    return CliRunner()


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create an empty temporary project directory."""
    project = tmp_path / "test_project"
    project.mkdir()
    return project


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Remove all environment variables that might interfere with tests."""
    # Store and clear env vars that could affect validation tests
    env_vars_to_clear = [
        key for key in os.environ if key.startswith(("DATABASE_", "API_", "SECRET_"))
    ]
    for var in env_vars_to_clear:
        monkeypatch.delenv(var, raising=False)
    yield
