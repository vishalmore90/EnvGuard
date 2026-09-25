"""Tests for the Python AST-based scanner."""

from __future__ import annotations

from pathlib import Path

import pytest

from envguard.scanners.python_scanner import PythonScanner


@pytest.fixture
def scanner() -> PythonScanner:
    return PythonScanner()


@pytest.fixture
def py_fixtures(fixtures_dir: Path) -> Path:
    return fixtures_dir / "python_project"


class TestSupportedExtensions:
    def test_only_py(self, scanner: PythonScanner) -> None:
        assert scanner.supported_extensions() == [".py"]

    def test_can_scan_py(self, scanner: PythonScanner, tmp_path: Path) -> None:
        f = tmp_path / "file.py"
        f.touch()
        assert scanner.can_scan(f) is True

    def test_cannot_scan_js(self, scanner: PythonScanner, tmp_path: Path) -> None:
        f = tmp_path / "file.js"
        f.touch()
        assert scanner.can_scan(f) is False


class TestStandardPatterns:
    """Test all 5 access patterns using the app.py fixture."""

    def test_detects_environ_subscript(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(py_fixtures / "app.py")
        names = [r.name for r in refs]
        assert "DATABASE_URL" in names

    def test_environ_subscript_pattern_label(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(py_fixtures / "app.py")
        db_ref = next(r for r in refs if r.name == "DATABASE_URL")
        assert db_ref.access_pattern == "os.environ[]"
        assert db_ref.has_default is False
        assert db_ref.default_value is None

    def test_detects_getenv(self, scanner: PythonScanner, py_fixtures: Path) -> None:
        refs = scanner.scan_file(py_fixtures / "app.py")
        names = [r.name for r in refs]
        assert "API_KEY" in names

    def test_getenv_pattern_label(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(py_fixtures / "app.py")
        ref = next(r for r in refs if r.name == "API_KEY")
        assert ref.access_pattern == "os.getenv"
        assert ref.has_default is False

    def test_detects_getenv_with_default(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(py_fixtures / "app.py")
        ref = next(r for r in refs if r.name == "DEBUG")
        assert ref.has_default is True
        assert ref.default_value == "false"

    def test_detects_environ_get(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(py_fixtures / "app.py")
        names = [r.name for r in refs]
        assert "REDIS_URL" in names

    def test_environ_get_no_default(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(py_fixtures / "app.py")
        ref = next(r for r in refs if r.name == "REDIS_URL")
        assert ref.access_pattern == "os.environ.get"
        assert ref.has_default is False

    def test_detects_environ_get_with_default(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(py_fixtures / "app.py")
        ref = next(r for r in refs if r.name == "PORT")
        assert ref.has_default is True
        assert ref.default_value == "8000"

    def test_skips_dynamic_keys(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        """Dynamic keys (os.environ.get(variable)) should not produce references."""
        refs = scanner.scan_file(py_fixtures / "app.py")
        names = [r.name for r in refs]
        assert "SOME_KEY" not in names

    def test_correct_line_numbers(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        """Line numbers should be 1-indexed and accurate."""
        refs = scanner.scan_file(py_fixtures / "app.py")
        for ref in refs:
            assert ref.line_number >= 1


class TestImportAliasing:
    """Test all import aliasing forms using config.py fixture."""

    def test_detects_via_os_alias(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        """import os as operating_system → operating_system.getenv() detected."""
        refs = scanner.scan_file(py_fixtures / "config.py")
        names = [r.name for r in refs]
        assert "LOG_LEVEL" in names

    def test_detects_via_from_os_import_environ(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        """from os import environ → environ["KEY"] detected."""
        refs = scanner.scan_file(py_fixtures / "config.py")
        names = [r.name for r in refs]
        assert "SECRET_KEY" in names

    def test_detects_via_getenv_alias(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        """from os import getenv as get_env → get_env("KEY") detected."""
        refs = scanner.scan_file(py_fixtures / "config.py")
        names = [r.name for r in refs]
        assert "SENTRY_DSN" in names

    def test_detects_via_environ_alias(
        self, scanner: PythonScanner, py_fixtures: Path
    ) -> None:
        """from os import environ as env → env.get("KEY") detected."""
        refs = scanner.scan_file(py_fixtures / "config.py")
        names = [r.name for r in refs]
        assert "ALLOWED_HOSTS" in names


class TestInlineScanning:
    """Unit tests using inline source code (no fixture files required)."""

    def _scan(self, scanner: PythonScanner, source: str, tmp_path: Path) -> list:
        f = tmp_path / "test.py"
        f.write_text(source)
        return scanner.scan_file(f)

    def test_file_path_is_set(self, scanner: PythonScanner, tmp_path: Path) -> None:
        f = tmp_path / "myapp.py"
        f.write_text("import os\nos.getenv('KEY')\n")
        refs = scanner.scan_file(f)
        assert refs[0].file_path == str(f)

    def test_no_os_import_returns_empty(
        self, scanner: PythonScanner, tmp_path: Path
    ) -> None:
        refs = self._scan(scanner, "x = 'no env vars here'\n", tmp_path)
        assert refs == []

    def test_invalid_syntax_returns_empty(
        self, scanner: PythonScanner, tmp_path: Path
    ) -> None:
        refs = self._scan(scanner, "def (\n", tmp_path)
        assert refs == []

    def test_missing_file_returns_empty(
        self, scanner: PythonScanner, tmp_path: Path
    ) -> None:
        refs = scanner.scan_file(tmp_path / "nonexistent.py")
        assert refs == []

    def test_integer_default_captured(
        self, scanner: PythonScanner, tmp_path: Path
    ) -> None:
        refs = self._scan(scanner, "import os\nos.getenv('TIMEOUT', '30')\n", tmp_path)
        assert refs[0].has_default is True
        assert refs[0].default_value == "30"

    def test_none_default_has_default_false(
        self, scanner: PythonScanner, tmp_path: Path
    ) -> None:
        """os.getenv('KEY', None) — second arg present but not a string constant."""
        refs = self._scan(scanner, "import os\nos.getenv('KEY', None)\n", tmp_path)
        # has_default is True (second arg exists) but default_value is None
        assert refs[0].has_default is True
        assert refs[0].default_value is None

    def test_empty_file(self, scanner: PythonScanner, tmp_path: Path) -> None:
        refs = self._scan(scanner, "", tmp_path)
        assert refs == []
