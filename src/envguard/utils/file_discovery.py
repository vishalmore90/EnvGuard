"""File discovery utilities for scanning project source files.

Provides path-walking with configurable extension filtering and
automatic exclusion of common non-source directories.
"""

from __future__ import annotations

from pathlib import Path

# Directories that are never source code and should always be skipped.
# These are matched against any path component, not just the top level.
_DEFAULT_EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        # Python
        "__pycache__",
        ".venv",
        "venv",
        "env",
        ".eggs",
        "*.egg-info",
        "dist",
        "build",
        ".tox",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        # JavaScript
        "node_modules",
        ".next",
        ".nuxt",
        "out",
        "coverage",
        # General
        ".idea",
        ".vscode",
        "vendor",
        "third_party",
    }
)

# File extensions grouped by language for convenience
PYTHON_EXTENSIONS: frozenset[str] = frozenset({".py"})
JS_EXTENSIONS: frozenset[str] = frozenset(
    {".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"}
)
ALL_SUPPORTED_EXTENSIONS: frozenset[str] = PYTHON_EXTENSIONS | JS_EXTENSIONS


def _is_excluded_dir(directory: Path, exclude_dirs: frozenset[str]) -> bool:
    """Return True if the directory name matches any exclude pattern."""
    name = directory.name
    # Direct name match
    if name in exclude_dirs:
        return True
    # Glob-style *.egg-info match (simple suffix check)
    for pattern in exclude_dirs:
        if pattern.startswith("*") and name.endswith(pattern[1:]):
            return True
    return False


def discover_files(
    root: Path,
    extensions: frozenset[str] | None = None,
    extra_exclude_dirs: frozenset[str] | None = None,
) -> list[Path]:
    """
    Recursively discover source files under `root` matching `extensions`.

    Args:
        root: Project root directory to search.
        extensions: Set of lowercase file extensions to include (e.g. {'.py'}).
                    Defaults to all supported extensions.
        extra_exclude_dirs: Additional directory names to exclude, merged with
                            the built-in exclusion list.

    Returns:
        Sorted list of Path objects for all matching files.

    Notes:
        - Hidden directories (names starting with '.') that are not already in
          the exclusion list are NOT automatically excluded — only the built-in
          list is applied.
        - Symlinks are followed for files but not for directories (to avoid loops).
        - Files that cannot be accessed are silently skipped.
    """
    if extensions is None:
        extensions = ALL_SUPPORTED_EXTENSIONS

    exclude_dirs = _DEFAULT_EXCLUDE_DIRS
    if extra_exclude_dirs:
        exclude_dirs = exclude_dirs | extra_exclude_dirs

    found: list[Path] = []
    _walk(root, extensions, exclude_dirs, found)
    return sorted(found)


def _walk(
    directory: Path,
    extensions: frozenset[str],
    exclude_dirs: frozenset[str],
    results: list[Path],
) -> None:
    """Recursive directory walker — avoids excluded dirs and handles errors."""
    try:
        entries = list(directory.iterdir())
    except (PermissionError, OSError):
        return

    for entry in entries:
        try:
            if entry.is_dir():
                if not _is_excluded_dir(entry, exclude_dirs):
                    _walk(entry, extensions, exclude_dirs, results)
            elif entry.is_file():
                if entry.suffix.lower() in extensions:
                    results.append(entry)
        except OSError:
            # Skip entries we can't stat
            continue


def auto_detect_languages(root: Path) -> list[str]:
    """
    Detect which languages are present in the project by sampling file extensions.

    Returns a list of language names, e.g. ['python', 'javascript'].
    This is a fast heuristic — it only checks extensions, not file content.
    """
    languages: list[str] = []
    py_files = discover_files(root, extensions=PYTHON_EXTENSIONS)
    if py_files:
        languages.append("python")

    js_files = discover_files(root, extensions=JS_EXTENSIONS)
    if js_files:
        languages.append("javascript")

    return languages
