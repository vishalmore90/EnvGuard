"""Tests for reporters."""

import json

import pytest
from rich.console import Console

from envguard.reporters.json_reporter import JsonReporter
from envguard.reporters.rich_reporter import RichReporter
from envguard.scanners.models import ScanResult
from envguard.schema.validator import ValidationError


def test_json_reporter_init(capsys: pytest.CaptureFixture[str]) -> None:
    reporter = JsonReporter()
    scan = ScanResult()
    reporter.report_init(scan, ".envguard.yml")

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["command"] == "init"
    assert data["schema_path"] == ".envguard.yml"


def test_json_reporter_check(capsys: pytest.CaptureFixture[str]) -> None:
    reporter = JsonReporter()
    errors = [
        ValidationError("API_KEY", "Missing", is_error=True),
        ValidationError("DEBUG", "Optional", is_error=False),
    ]
    reporter.report_check(errors, 2)

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["command"] == "check"
    assert data["error_count"] == 1
    assert data["warning_count"] == 1
    assert data["passed"] is False


def test_rich_reporter_init(capsys: pytest.CaptureFixture[str]) -> None:
    # Use standard console without terminal codes for testing
    console = Console(force_terminal=False, force_jupyter=False)
    reporter = RichReporter(console=console)
    scan = ScanResult()
    reporter.report_init(scan, ".envguard.yml")

    captured = capsys.readouterr()
    assert "EnvGuard Initialized" in captured.out
    assert "Variables Found" in captured.out


def test_rich_reporter_check(capsys: pytest.CaptureFixture[str]) -> None:
    console = Console(force_terminal=False, force_jupyter=False)
    reporter = RichReporter(console=console)

    # Test clean
    reporter.report_check([], 5)
    captured = capsys.readouterr()
    assert "passed validation" in captured.out

    # Test errors
    errors = [ValidationError("API_KEY", "Missing", is_error=True)]
    reporter.report_check(errors, 1)
    captured = capsys.readouterr()
    assert "Validation Results" in captured.out
    assert "ERROR" in captured.out
    assert "Failed with 1 errors" in captured.out
