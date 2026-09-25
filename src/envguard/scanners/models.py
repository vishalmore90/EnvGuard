"""Shared data models for scanner results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EnvVarReference:
    """Represents a single environment variable reference found in source code."""

    name: str
    """The environment variable name, e.g. 'DATABASE_URL'."""

    file_path: str
    """Absolute or relative path to the source file where the reference was found."""

    line_number: int
    """1-indexed line number of the reference in the source file."""

    access_pattern: str
    """How the variable was accessed, e.g. 'os.environ[]', 'os.getenv', 'process.env'."""

    has_default: bool = False
    """Whether a default/fallback value was provided at the call site."""

    default_value: str | None = None
    """The default value if extractable from the source, otherwise None."""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EnvVarReference):
            return NotImplemented
        return (
            self.name == other.name
            and self.file_path == other.file_path
            and self.line_number == other.line_number
        )

    def __hash__(self) -> int:
        return hash((self.name, self.file_path, self.line_number))


@dataclass
class ScanResult:
    """Aggregated result from scanning a project."""

    references: list[EnvVarReference] = field(default_factory=list)
    """All env var references found."""

    scanned_files: list[str] = field(default_factory=list)
    """Files that were scanned."""

    skipped_files: list[str] = field(default_factory=list)
    """Files skipped due to errors (binary, permission denied, parse failure)."""

    warnings: list[str] = field(default_factory=list)
    """Non-fatal issues encountered during scanning."""

    @property
    def unique_names(self) -> set[str]:
        """Return the set of unique environment variable names found."""
        return {ref.name for ref in self.references}

    @property
    def file_count(self) -> int:
        return len(self.scanned_files)

    @property
    def reference_count(self) -> int:
        return len(self.references)
