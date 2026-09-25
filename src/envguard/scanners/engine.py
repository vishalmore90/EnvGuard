"""Orchestration engine for source code scanning."""

from __future__ import annotations

import logging
from pathlib import Path

from envguard.scanners.base import BaseScanner
from envguard.scanners.js_scanner import JavaScriptScanner
from envguard.scanners.models import ScanResult
from envguard.scanners.python_scanner import PythonScanner
from envguard.utils.file_discovery import auto_detect_languages, discover_files

logger = logging.getLogger(__name__)


class ScannerEngine:
    """
    Orchestrator that handles the end-to-end scanning process.

    Responsibilities:
      - File discovery based on specified or auto-detected languages.
      - Routing files to the appropriate language scanner.
      - Aggregating results into a single ScanResult.
    """

    def __init__(self) -> None:
        self.scanners: list[BaseScanner] = [
            PythonScanner(),
            JavaScriptScanner(),
        ]

    def scan_project(
        self,
        root: Path,
        languages: list[str] | None = None,
        extra_exclude_dirs: frozenset[str] | None = None,
    ) -> ScanResult:
        """
        Scan a directory and all its subdirectories for env var usage.

        Args:
            root: The root directory to scan.
            languages: Specific languages to scan (e.g. ['python', 'javascript']).
                       If None, auto-detects languages present in the project.
            extra_exclude_dirs: Additional directories to skip during file discovery.

        Returns:
            A populated ScanResult object.
        """
        result = ScanResult()

        if not root.exists() or not root.is_dir():
            result.warnings.append(f"Directory not found: {root}")
            return result

        if languages is None:
            languages = auto_detect_languages(root)
            if not languages:
                result.warnings.append("Could not auto-detect any supported languages.")
                return result

        # Filter scanners based on requested languages
        active_scanners = self._get_scanners_for_languages(languages)
        if not active_scanners:
            result.warnings.append(
                f"No scanners found for requested languages: {languages}"
            )
            return result

        # Collect all extensions handled by active scanners
        active_extensions: set[str] = set()
        for scanner in active_scanners:
            active_extensions.update(scanner.supported_extensions())

        # Discover files
        files_to_scan = discover_files(
            root,
            extensions=frozenset(active_extensions),
            extra_exclude_dirs=extra_exclude_dirs,
        )

        # Route files to appropriate scanners
        for file_path in files_to_scan:
            file_scanner = self._get_scanner_for_file(file_path, active_scanners)
            if not file_scanner:
                result.skipped_files.append(str(file_path))
                continue

            try:
                refs = file_scanner.scan_file(file_path)
                result.references.extend(refs)
                result.scanned_files.append(str(file_path))
            except Exception as e:
                # Catch-all for unexpected errors (scanners should handle expected ones)
                logger.debug(f"Failed to scan {file_path}: {e}")
                result.skipped_files.append(str(file_path))

        return result

    def _get_scanners_for_languages(self, languages: list[str]) -> list[BaseScanner]:
        """Return subset of scanners that match requested language names."""
        active: list[BaseScanner] = []
        normalized_langs = [lang.lower() for lang in languages]

        for scanner in self.scanners:
            if (
                isinstance(scanner, PythonScanner) and "python" in normalized_langs
            ) or (
                isinstance(scanner, JavaScriptScanner)
                and (
                    "javascript" in normalized_langs or "typescript" in normalized_langs
                )
            ):
                active.append(scanner)

        return active

    def _get_scanner_for_file(
        self, file_path: Path, scanners: list[BaseScanner]
    ) -> BaseScanner | None:
        """Find the first scanner that claims to support this file."""
        for scanner in scanners:
            if scanner.can_scan(file_path):
                return scanner
        return None
