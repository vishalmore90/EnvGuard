"""AST-based scanner for Python source files.

Detects the following environment variable access patterns:
    - os.environ["KEY"]          (Subscript access)
    - os.environ.get("KEY")      (Method call, no default)
    - os.environ.get("KEY", "x") (Method call, with default)
    - os.getenv("KEY")           (Function call, no default)
    - os.getenv("KEY", "x")      (Function call, with default)

Import aliasing is tracked:
    - import os
    - from os import environ
    - from os import environ as env
    - from os import getenv
    - from os import getenv as get_env

Dynamic keys (where the key is a variable, not a string literal) are
silently skipped — they cannot be statically resolved.
"""

from __future__ import annotations

import ast
from pathlib import Path

from envguard.scanners.base import BaseScanner
from envguard.scanners.models import EnvVarReference


class _ImportTracker(ast.NodeVisitor):
    """
    First-pass visitor that records how os.environ / os.getenv were imported.

    This is necessary to handle aliased imports correctly. After visiting,
    check self.environ_aliases and self.getenv_aliases for the names that
    should be treated as os.environ / os.getenv respectively.
    """

    def __init__(self) -> None:
        # Names in scope that refer to `os.environ`
        self.environ_aliases: set[str] = set()
        # Names in scope that refer to `os.getenv`
        self.getenv_aliases: set[str] = set()
        # Whether `import os` (or alias) is present
        self.os_names: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "os":
                # `import os` or `import os as something`
                self.os_names.add(alias.asname if alias.asname else "os")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module != "os":
            return
        for alias in node.names:
            local_name = alias.asname if alias.asname else alias.name
            if alias.name == "environ":
                self.environ_aliases.add(local_name)
            elif alias.name == "getenv":
                self.getenv_aliases.add(local_name)
        self.generic_visit(node)


class _EnvVarVisitor(ast.NodeVisitor):
    """
    Second-pass visitor that collects all environment variable references.

    Relies on _ImportTracker results to correctly resolve aliased names.
    """

    def __init__(
        self,
        file_path: str,
        os_names: set[str],
        environ_aliases: set[str],
        getenv_aliases: set[str],
    ) -> None:
        self._file_path = file_path
        self._os_names = os_names
        self._environ_aliases = environ_aliases
        self._getenv_aliases = getenv_aliases
        self.references: list[EnvVarReference] = []

    # ------------------------------------------------------------------
    # Pattern: os.environ["KEY"]  (Subscript)
    # ------------------------------------------------------------------
    def visit_Subscript(self, node: ast.Subscript) -> None:
        key_name = self._extract_environ_subscript_key(node)
        if key_name is not None:
            self.references.append(
                EnvVarReference(
                    name=key_name,
                    file_path=self._file_path,
                    line_number=node.lineno,
                    access_pattern="os.environ[]",
                    has_default=False,
                    default_value=None,
                )
            )
        self.generic_visit(node)

    def _extract_environ_subscript_key(self, node: ast.Subscript) -> str | None:
        """
        Return the key string if node is `os.environ["KEY"]` or
        `environ["KEY"]` (aliased), else None.
        """
        value = node.value

        # os.environ["KEY"] — value is an Attribute node
        if (
            isinstance(value, ast.Attribute)
            and value.attr == "environ"
            and isinstance(value.value, ast.Name)
            and value.value.id in self._os_names
        ):
            return self._extract_constant_slice(node.slice)

        # environ["KEY"] — value is a Name node (from os import environ)
        if isinstance(value, ast.Name) and value.id in self._environ_aliases:
            return self._extract_constant_slice(node.slice)

        return None

    # ------------------------------------------------------------------
    # Pattern: os.environ.get("KEY") and os.getenv("KEY")  (Call)
    # ------------------------------------------------------------------
    def visit_Call(self, node: ast.Call) -> None:
        ref = self._extract_call_reference(node)
        if ref is not None:
            self.references.append(ref)
        self.generic_visit(node)

    def _extract_call_reference(self, node: ast.Call) -> EnvVarReference | None:
        func = node.func

        # os.environ.get("KEY") or environ.get("KEY")
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "get"
            and self._is_environ_node(func.value)
            and node.args
        ):
            key_name = self._extract_constant_arg(node.args[0])
            if key_name:
                default = self._extract_default(node)
                return EnvVarReference(
                    name=key_name,
                    file_path=self._file_path,
                    line_number=node.lineno,
                    access_pattern="os.environ.get",
                    has_default=default is not None or len(node.args) > 1,
                    default_value=default,
                )

        # os.getenv("KEY") or getenv("KEY")
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "getenv"
            and isinstance(func.value, ast.Name)
            and func.value.id in self._os_names
            and node.args
        ):
            key_name = self._extract_constant_arg(node.args[0])
            if key_name:
                default = self._extract_default(node)
                return EnvVarReference(
                    name=key_name,
                    file_path=self._file_path,
                    line_number=node.lineno,
                    access_pattern="os.getenv",
                    has_default=default is not None or len(node.args) > 1,
                    default_value=default,
                )

        if isinstance(func, ast.Name) and func.id in self._getenv_aliases and node.args:
            key_name = self._extract_constant_arg(node.args[0])
            if key_name:
                default = self._extract_default(node)
                return EnvVarReference(
                    name=key_name,
                    file_path=self._file_path,
                    line_number=node.lineno,
                    access_pattern="os.getenv",
                    has_default=default is not None or len(node.args) > 1,
                    default_value=default,
                )

        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _is_environ_node(self, node: ast.expr) -> bool:
        """Return True if node refers to os.environ or an aliased environ."""
        # os.environ
        if (
            isinstance(node, ast.Attribute)
            and node.attr == "environ"
            and isinstance(node.value, ast.Name)
            and node.value.id in self._os_names
        ):
            return True
        # environ (from os import environ)
        return isinstance(node, ast.Name) and node.id in self._environ_aliases

    def _extract_constant_slice(self, node: ast.expr) -> str | None:
        """Extract a string constant from a subscript slice node."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    def _extract_constant_arg(self, node: ast.expr) -> str | None:
        """Extract a string constant from a call argument."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    def _extract_default(self, node: ast.Call) -> str | None:
        """
        Try to extract the default value from the second positional arg.

        Returns the string value if the second arg is a string constant.
        Returns None if there is no second arg, or if the value is a non-string
        constant (e.g. None, 0, False) — those are still recorded as
        has_default=True by the caller, but default_value will be None.
        """
        if len(node.args) > 1:
            second = node.args[1]
            if isinstance(second, ast.Constant) and isinstance(second.value, str):
                return second.value
        return None


class PythonScanner(BaseScanner):
    """AST-based scanner for Python source files."""

    def supported_extensions(self) -> list[str]:
        return [".py"]

    def scan_file(self, file_path: Path) -> list[EnvVarReference]:
        """
        Parse the Python file and extract all env var references.

        Returns an empty list on any parse or I/O error — callers
        should use ScanResult.skipped_files to track these.
        """
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return []

        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError:
            return []

        # First pass: collect import aliases
        tracker = _ImportTracker()
        tracker.visit(tree)

        # If neither `import os` nor any `from os import ...` was seen,
        # there's nothing for us to find.
        if (
            not tracker.os_names
            and not tracker.environ_aliases
            and not tracker.getenv_aliases
        ):
            return []

        # Second pass: collect references
        visitor = _EnvVarVisitor(
            file_path=str(file_path),
            os_names=tracker.os_names,
            environ_aliases=tracker.environ_aliases,
            getenv_aliases=tracker.getenv_aliases,
        )
        visitor.visit(tree)

        return visitor.references
