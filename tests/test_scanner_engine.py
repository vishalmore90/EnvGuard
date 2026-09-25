"""Tests for the ScannerEngine orchestration class."""

from __future__ import annotations

from pathlib import Path

import pytest

from envguard.scanners.engine import ScannerEngine


@pytest.fixture
def engine() -> ScannerEngine:
    return ScannerEngine()


def test_engine_initializes_scanners(engine: ScannerEngine) -> None:
    assert len(engine.scanners) == 2
    types = [type(s).__name__ for s in engine.scanners]
    assert "PythonScanner" in types
    assert "JavaScriptScanner" in types


def test_scan_missing_directory(engine: ScannerEngine, tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist"
    result = engine.scan_project(missing)
    assert len(result.warnings) == 1
    assert "Directory not found" in result.warnings[0]


def test_auto_detect_no_languages(engine: ScannerEngine, tmp_project: Path) -> None:
    (tmp_project / "README.md").write_text("# Hello")
    result = engine.scan_project(tmp_project)
    assert len(result.warnings) == 1
    assert "Could not auto-detect" in result.warnings[0]


def test_scan_explicit_language_no_scanners(
    engine: ScannerEngine, tmp_project: Path
) -> None:
    result = engine.scan_project(tmp_project, languages=["ruby"])
    assert len(result.warnings) == 1
    assert "No scanners found" in result.warnings[0]


def test_scan_project_end_to_end(engine: ScannerEngine, tmp_project: Path) -> None:
    # Setup a mixed project
    (tmp_project / "app.py").write_text('import os\nos.getenv("PY_VAR")\n')
    (tmp_project / "index.js").write_text("const x = process.env.JS_VAR;\n")

    # Should auto-detect both and scan both
    result = engine.scan_project(tmp_project)

    assert result.file_count == 2
    assert result.reference_count == 2

    names = result.unique_names
    assert "PY_VAR" in names
    assert "JS_VAR" in names


def test_scan_project_filter_by_language(
    engine: ScannerEngine, tmp_project: Path
) -> None:
    (tmp_project / "app.py").write_text('import os\nos.getenv("PY_VAR")\n')
    (tmp_project / "index.js").write_text("const x = process.env.JS_VAR;\n")

    # Explicitly request only Python
    result = engine.scan_project(tmp_project, languages=["python"])

    assert result.file_count == 1
    names = result.unique_names
    assert "PY_VAR" in names
    assert "JS_VAR" not in names


def test_scan_project_handles_scanner_error(
    engine: ScannerEngine, tmp_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_project / "app.py").write_text('import os\nos.getenv("PY_VAR")\n')

    # Mock scanner to raise an unexpected exception
    from envguard.scanners.python_scanner import PythonScanner

    def mock_scan_file(*args: object, **kwargs: object) -> list[object]:
        raise ValueError("Boom")

    monkeypatch.setattr(PythonScanner, "scan_file", mock_scan_file)

    result = engine.scan_project(tmp_project)

    # Should not crash, should add to skipped_files
    assert result.reference_count == 0
    assert result.file_count == 0
    assert len(result.skipped_files) == 1
    assert "app.py" in result.skipped_files[0]
