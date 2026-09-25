"""Regex-based scanner for JavaScript and TypeScript source files.

Detects the following environment variable access patterns:
    - process.env.KEY            (member expression)
    - process.env["KEY"]         (bracket notation, double quotes)
    - process.env['KEY']         (bracket notation, single quotes)

Design decision: regex is used here rather than a full JS/TS AST parser
(e.g. esprima, tree-sitter) because:
  1. It avoids a non-Python runtime dependency entirely.
  2. The `process.env` access patterns are syntactically simple and
     consistent — they don't require structural understanding.
  3. An AST parser can be added as a post-MVP language plugin without
     changing the BaseScanner interface.

Limitation: dynamic keys (process.env[varName]) cannot be statically
resolved and are silently skipped.
"""

from __future__ import annotations

import re
from pathlib import Path

from envguard.scanners.base import BaseScanner
from envguard.scanners.models import EnvVarReference

# Matches:  process.env.KEY_NAME
_PATTERN_MEMBER = re.compile(
    r"process\.env\.([A-Z_][A-Z0-9_]*)",
    re.ASCII,
)

# Matches:  process.env["KEY_NAME"] or process.env['KEY_NAME']
_PATTERN_BRACKET = re.compile(
    r"""process\.env\[["']([A-Z_][A-Z0-9_]*)["']\]""",
    re.ASCII,
)

# Combined: try bracket first (more specific), then member.
# We compile separately to be able to report the access_pattern accurately.
_ALL_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (_PATTERN_BRACKET, "process.env[]"),
    (_PATTERN_MEMBER, "process.env."),
]

# env var names are conventionally SCREAMING_SNAKE_CASE, but some projects
# use mixed case. We capture [A-Z_][A-Z0-9_]* as the minimum — this matches
# the overwhelming majority of real env var names and avoids false positives
# from CSS class names, HTML attributes, etc.


class JavaScriptScanner(BaseScanner):
    """Regex-based scanner for JavaScript and TypeScript source files."""

    def supported_extensions(self) -> list[str]:
        return [".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"]

    def scan_file(self, file_path: Path) -> list[EnvVarReference]:
        """
        Scan a JS/TS file line-by-line for process.env references.

        Returns an empty list on any I/O error.
        Duplicate (name, line) pairs are deduplicated.
        """
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return []

        references: list[EnvVarReference] = []
        seen: set[tuple[str, int]] = set()  # (name, line_number) dedup

        for line_number, line in enumerate(source.splitlines(), start=1):
            # Skip comment lines (basic heuristic: // and /* lines)
            stripped = line.lstrip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue

            for pattern, access_pattern in _ALL_PATTERNS:
                for match in pattern.finditer(line):
                    name = match.group(1)
                    key = (name, line_number)
                    if key in seen:
                        continue
                    seen.add(key)
                    references.append(
                        EnvVarReference(
                            name=name,
                            file_path=str(file_path),
                            line_number=line_number,
                            access_pattern=access_pattern,
                            # JS doesn't have a standard "default value"
                            # syntax at the env access site — defaults are
                            # usually applied with || or ?? at a higher level.
                            has_default=False,
                            default_value=None,
                        )
                    )

        return references
