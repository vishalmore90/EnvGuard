"""Tests for the scan command."""

from pathlib import Path

from envguard.commands.scan_cmd import execute_scan
from envguard.reporters.json_reporter import JsonReporter


def test_scan_finds_secrets_and_exits(tmp_path: Path) -> None:
    # Create a python file with an AWS secret
    test_file = tmp_path / "main.py"
    test_file.write_text("import os\nAWS_KEY = 'AKIAIOSFODNN7EXAMPLE'\n")

    reporter = JsonReporter()
    exit_code = execute_scan(
        path=str(tmp_path),
        output_format="json",
        min_entropy=4.5,
        exclude=(),
        verbose=False,
        reporter=reporter,
    )

    # Should return 1 because a HIGH confidence secret was found
    assert exit_code == 1


def test_scan_no_secrets_exits_cleanly(tmp_path: Path) -> None:
    # Create a safe python file
    test_file = tmp_path / "main.py"
    test_file.write_text("print('Hello, safe world')\n")

    reporter = JsonReporter()
    exit_code = execute_scan(
        path=str(tmp_path),
        output_format="json",
        min_entropy=4.5,
        exclude=(),
        verbose=False,
        reporter=reporter,
    )

    # Should return 0
    assert exit_code == 0
