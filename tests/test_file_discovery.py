"""Tests for file discovery utilities."""

from __future__ import annotations

from pathlib import Path

from envguard.utils.file_discovery import (
    ALL_SUPPORTED_EXTENSIONS,
    JS_EXTENSIONS,
    PYTHON_EXTENSIONS,
    auto_detect_languages,
    discover_files,
)


class TestDiscoverFiles:
    def test_finds_python_files(self, tmp_project: Path) -> None:
        (tmp_project / "app.py").write_text("# py")
        (tmp_project / "config.py").write_text("# py")
        result = discover_files(tmp_project, extensions=PYTHON_EXTENSIONS)
        names = [f.name for f in result]
        assert "app.py" in names
        assert "config.py" in names

    def test_finds_js_files(self, tmp_project: Path) -> None:
        (tmp_project / "index.js").write_text("// js")
        (tmp_project / "utils.ts").write_text("// ts")
        result = discover_files(tmp_project, extensions=JS_EXTENSIONS)
        names = [f.name for f in result]
        assert "index.js" in names
        assert "utils.ts" in names

    def test_finds_nested_files(self, tmp_project: Path) -> None:
        sub = tmp_project / "src" / "api"
        sub.mkdir(parents=True)
        (sub / "routes.py").write_text("# py")
        result = discover_files(tmp_project, extensions=PYTHON_EXTENSIONS)
        assert any(f.name == "routes.py" for f in result)

    def test_excludes_node_modules(self, tmp_project: Path) -> None:
        nm = tmp_project / "node_modules" / "some_pkg"
        nm.mkdir(parents=True)
        (nm / "index.js").write_text("// should be excluded")
        (tmp_project / "app.js").write_text("// included")
        result = discover_files(tmp_project, extensions=JS_EXTENSIONS)
        # Check no result has "node_modules" as a path *component*, not as
        # a substring — important on Windows where pytest temp dirs may contain
        # "node_modules" in the directory name (e.g. test_excludes_node_modules0)
        node_modules_dir = str(tmp_project / "node_modules")
        assert not any(str(f).startswith(node_modules_dir) for f in result)

    def test_excludes_venv(self, tmp_project: Path) -> None:
        venv_dir = tmp_project / ".venv" / "lib"
        venv_dir.mkdir(parents=True)
        (venv_dir / "site.py").write_text("# excluded")
        (tmp_project / "app.py").write_text("# included")
        result = discover_files(tmp_project, extensions=PYTHON_EXTENSIONS)
        paths = [str(f) for f in result]
        assert not any(".venv" in p for p in paths)

    def test_excludes_pycache(self, tmp_project: Path) -> None:
        cache = tmp_project / "__pycache__"
        cache.mkdir()
        (cache / "app.cpython-313.pyc").write_text("")
        (tmp_project / "app.py").write_text("# included")
        result = discover_files(tmp_project, extensions=PYTHON_EXTENSIONS)
        paths = [str(f) for f in result]
        assert not any("__pycache__" in p for p in paths)

    def test_excludes_git_directory(self, tmp_project: Path) -> None:
        git = tmp_project / ".git" / "hooks"
        git.mkdir(parents=True)
        (git / "pre-commit").write_text("#!/bin/sh")
        (tmp_project / "app.py").write_text("# included")
        result = discover_files(tmp_project, extensions=ALL_SUPPORTED_EXTENSIONS)
        paths = [str(f) for f in result]
        assert not any(".git" in p for p in paths)

    def test_does_not_include_wrong_extension(self, tmp_project: Path) -> None:
        (tmp_project / "README.md").write_text("# README")
        (tmp_project / "app.py").write_text("# py")
        result = discover_files(tmp_project, extensions=PYTHON_EXTENSIONS)
        names = [f.name for f in result]
        assert "README.md" not in names

    def test_default_extensions_include_all_supported(self, tmp_project: Path) -> None:
        (tmp_project / "app.py").write_text("# py")
        (tmp_project / "app.js").write_text("// js")
        result = discover_files(tmp_project)
        names = [f.name for f in result]
        assert "app.py" in names
        assert "app.js" in names

    def test_results_are_sorted(self, tmp_project: Path) -> None:
        (tmp_project / "z_file.py").write_text("# z")
        (tmp_project / "a_file.py").write_text("# a")
        result = discover_files(tmp_project, extensions=PYTHON_EXTENSIONS)
        assert result == sorted(result)

    def test_empty_directory_returns_empty(self, tmp_project: Path) -> None:
        result = discover_files(tmp_project)
        assert result == []

    def test_extra_exclude_dirs(self, tmp_project: Path) -> None:
        custom = tmp_project / "generated"
        custom.mkdir()
        (custom / "output.py").write_text("# generated")
        (tmp_project / "app.py").write_text("# included")
        result = discover_files(
            tmp_project,
            extensions=PYTHON_EXTENSIONS,
            extra_exclude_dirs=frozenset({"generated"}),
        )
        names = [f.name for f in result]
        assert "output.py" not in names
        assert "app.py" in names


class TestAutoDetectLanguages:
    def test_detects_python(self, tmp_project: Path) -> None:
        (tmp_project / "app.py").write_text("# py")
        langs = auto_detect_languages(tmp_project)
        assert "python" in langs

    def test_detects_javascript(self, tmp_project: Path) -> None:
        (tmp_project / "app.js").write_text("// js")
        langs = auto_detect_languages(tmp_project)
        assert "javascript" in langs

    def test_detects_both(self, tmp_project: Path) -> None:
        (tmp_project / "app.py").write_text("# py")
        (tmp_project / "app.js").write_text("// js")
        langs = auto_detect_languages(tmp_project)
        assert "python" in langs
        assert "javascript" in langs

    def test_empty_project_returns_empty(self, tmp_project: Path) -> None:
        langs = auto_detect_languages(tmp_project)
        assert langs == []
