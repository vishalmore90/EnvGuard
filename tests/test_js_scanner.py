"""Tests for the JavaScript/TypeScript regex-based scanner."""

from __future__ import annotations

from pathlib import Path

import pytest

from envguard.scanners.js_scanner import JavaScriptScanner


@pytest.fixture
def scanner() -> JavaScriptScanner:
    return JavaScriptScanner()


@pytest.fixture
def js_fixtures(fixtures_dir: Path) -> Path:
    return fixtures_dir / "js_project"


class TestSupportedExtensions:
    def test_includes_js(self, scanner: JavaScriptScanner) -> None:
        assert ".js" in scanner.supported_extensions()

    def test_includes_ts(self, scanner: JavaScriptScanner) -> None:
        assert ".ts" in scanner.supported_extensions()

    def test_includes_jsx(self, scanner: JavaScriptScanner) -> None:
        assert ".jsx" in scanner.supported_extensions()

    def test_includes_tsx(self, scanner: JavaScriptScanner) -> None:
        assert ".tsx" in scanner.supported_extensions()

    def test_does_not_include_py(self, scanner: JavaScriptScanner) -> None:
        assert ".py" not in scanner.supported_extensions()

    def test_can_scan_js(self, scanner: JavaScriptScanner, tmp_path: Path) -> None:
        f = tmp_path / "file.js"
        f.touch()
        assert scanner.can_scan(f) is True

    def test_cannot_scan_py(self, scanner: JavaScriptScanner, tmp_path: Path) -> None:
        f = tmp_path / "file.py"
        f.touch()
        assert scanner.can_scan(f) is False


class TestJSPatterns:
    """Test all access patterns using the index.js fixture."""

    def test_detects_member_expression(
        self, scanner: JavaScriptScanner, js_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(js_fixtures / "index.js")
        names = [r.name for r in refs]
        assert "DATABASE_URL" in names

    def test_member_expression_pattern_label(
        self, scanner: JavaScriptScanner, js_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(js_fixtures / "index.js")
        ref = next(r for r in refs if r.name == "DATABASE_URL")
        assert ref.access_pattern == "process.env."

    def test_detects_bracket_double_quote(
        self, scanner: JavaScriptScanner, js_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(js_fixtures / "index.js")
        names = [r.name for r in refs]
        assert "API_KEY" in names

    def test_bracket_double_quote_pattern_label(
        self, scanner: JavaScriptScanner, js_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(js_fixtures / "index.js")
        ref = next(r for r in refs if r.name == "API_KEY")
        assert ref.access_pattern == "process.env[]"

    def test_detects_bracket_single_quote(
        self, scanner: JavaScriptScanner, js_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(js_fixtures / "index.js")
        names = [r.name for r in refs]
        assert "DEBUG" in names

    def test_detects_with_fallback_operator(
        self, scanner: JavaScriptScanner, js_fixtures: Path
    ) -> None:
        """process.env.PORT || '3000' — PORT should be detected."""
        refs = scanner.scan_file(js_fixtures / "index.js")
        names = [r.name for r in refs]
        assert "PORT" in names
        assert "NODE_ENV" in names

    def test_skips_comment_lines(
        self, scanner: JavaScriptScanner, js_fixtures: Path
    ) -> None:
        """process.env references inside // comments should be skipped."""
        refs = scanner.scan_file(js_fixtures / "index.js")
        names = [r.name for r in refs]
        assert "SHOULD_NOT_BE_DETECTED" not in names

    def test_skips_dynamic_bracket(
        self, scanner: JavaScriptScanner, js_fixtures: Path
    ) -> None:
        """process.env[key] (dynamic) should not produce a reference."""
        refs = scanner.scan_file(js_fixtures / "index.js")
        names = [r.name for r in refs]
        assert "SOME_KEY" not in names


class TestTSPatterns:
    """Test TypeScript fixture with type annotations."""

    def test_detects_in_ts_file(
        self, scanner: JavaScriptScanner, js_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(js_fixtures / "config.ts")
        names = [r.name for r in refs]
        assert "DATABASE_URL" in names
        assert "REDIS_URL" in names
        assert "SECRET_KEY" in names
        assert "PORT" in names

    def test_ts_bracket_pattern(
        self, scanner: JavaScriptScanner, js_fixtures: Path
    ) -> None:
        refs = scanner.scan_file(js_fixtures / "config.ts")
        ref = next(r for r in refs if r.name == "SECRET_KEY")
        assert ref.access_pattern == "process.env[]"


class TestInlineScanning:
    """Unit tests using inline source content."""

    def _scan(
        self, scanner: JavaScriptScanner, source: str, tmp_path: Path, ext: str = ".js"
    ) -> list:
        f = tmp_path / f"test{ext}"
        f.write_text(source)
        return scanner.scan_file(f)

    def test_file_path_is_set(self, scanner: JavaScriptScanner, tmp_path: Path) -> None:
        f = tmp_path / "app.js"
        f.write_text("const x = process.env.MY_KEY;\n")
        refs = scanner.scan_file(f)
        assert refs[0].file_path == str(f)

    def test_correct_line_numbers(
        self, scanner: JavaScriptScanner, tmp_path: Path
    ) -> None:
        source = "// line 1\nconst x = process.env.MY_KEY;\n"
        refs = self._scan(scanner, source, tmp_path)
        assert refs[0].line_number == 2

    def test_no_process_env_returns_empty(
        self, scanner: JavaScriptScanner, tmp_path: Path
    ) -> None:
        refs = self._scan(scanner, "const x = 42;\n", tmp_path)
        assert refs == []

    def test_missing_file_returns_empty(
        self, scanner: JavaScriptScanner, tmp_path: Path
    ) -> None:
        refs = scanner.scan_file(tmp_path / "nonexistent.js")
        assert refs == []

    def test_empty_file(self, scanner: JavaScriptScanner, tmp_path: Path) -> None:
        refs = self._scan(scanner, "", tmp_path)
        assert refs == []

    def test_lowercase_key_not_detected(
        self, scanner: JavaScriptScanner, tmp_path: Path
    ) -> None:
        """process.env.myVar — lowercase var names should not match."""
        refs = self._scan(scanner, "const x = process.env.myVar;\n", tmp_path)
        assert refs == []

    def test_same_var_on_same_line_deduplicated(
        self, scanner: JavaScriptScanner, tmp_path: Path
    ) -> None:
        """Same name accessed twice on one line should appear once."""
        refs = self._scan(
            scanner, "const x = process.env.MY_KEY || process.env.MY_KEY;\n", tmp_path
        )
        assert len([r for r in refs if r.name == "MY_KEY"]) == 1

    def test_tsx_extension(self, scanner: JavaScriptScanner, tmp_path: Path) -> None:
        refs = self._scan(
            scanner, "const key = process.env.NEXT_PUBLIC_API;\n", tmp_path, ext=".tsx"
        )
        assert refs[0].name == "NEXT_PUBLIC_API"
