"""Tests for the init command."""

from pathlib import Path

from envguard.commands.init_cmd import execute_init
from envguard.reporters.json_reporter import JsonReporter


def test_execute_init(tmp_path: Path) -> None:
    # Setup project with python files containing env vars
    test_file = tmp_path / "main.py"
    test_file.write_text(
        "import os\napi = os.getenv('API_KEY')\nport = os.environ.get('PORT', '8080')\n"
    )

    schema_file = tmp_path / ".envguard.yml"
    reporter = JsonReporter()

    exit_code = execute_init(
        path=str(tmp_path),
        output_path=str(schema_file),
        languages=None,
        force=False,
        verbose=False,
        reporter=reporter,
    )

    assert exit_code == 0
    assert schema_file.exists()

    content = schema_file.read_text(encoding="utf-8")
    assert "API_KEY:" in content
    assert "PORT:" in content
    assert "default: '8080'" in content


def test_execute_init_no_force(tmp_path: Path) -> None:
    schema_file = tmp_path / ".envguard.yml"
    schema_file.write_text("old")

    reporter = JsonReporter()
    exit_code = execute_init(
        path=str(tmp_path),
        output_path=str(schema_file),
        languages=None,
        force=False,
        verbose=False,
        reporter=reporter,
    )

    assert exit_code == 1
    assert schema_file.read_text() == "old"

    # with force
    exit_code = execute_init(
        path=str(tmp_path),
        output_path=str(schema_file),
        languages=None,
        force=True,
        verbose=False,
        reporter=reporter,
    )
    assert exit_code == 0
    assert schema_file.read_text() != "old"
