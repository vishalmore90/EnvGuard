"""Abstract base class for all source code scanners."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from envguard.scanners.models import EnvVarReference


class BaseScanner(ABC):
    """
    Abstract scanner interface.

    Each language scanner implements this interface, allowing the scanner
    engine to call them uniformly without knowing language-specific details.
    """

    @abstractmethod
    def scan_file(self, file_path: Path) -> list[EnvVarReference]:
        """
        Scan a single source file and return all env var references found.

        Args:
            file_path: Path to the file to scan.

        Returns:
            List of EnvVarReference objects, one per detected usage.
            Returns an empty list if no references are found.

        Notes:
            Implementations should handle parse errors gracefully and return
            an empty list rather than raising exceptions. Use the warnings
            mechanism on ScanResult for non-fatal issues.
        """
        ...

    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """
        Return the list of file extensions this scanner handles.

        Returns:
            List of lowercase extensions including the dot, e.g. ['.py'] or
            ['.js', '.ts', '.jsx', '.tsx'].
        """
        ...

    def can_scan(self, file_path: Path) -> bool:
        """Return True if this scanner can handle the given file."""
        return file_path.suffix.lower() in self.supported_extensions()
