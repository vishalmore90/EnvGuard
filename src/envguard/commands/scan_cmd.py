"""Implementation of the 'scan' command for secret detection."""

import logging
from pathlib import Path

from rich.console import Console
from rich.table import Table

from envguard.reporters.base import BaseReporter
from envguard.secrets.detector import SecretDetector
from envguard.utils.file_discovery import discover_files

logger = logging.getLogger(__name__)


def execute_scan(
    path: str,
    output_format: str,
    min_entropy: float,
    exclude: tuple[str, ...],
    verbose: bool,
    reporter: BaseReporter,
) -> int:
    """
    Scan the project for hardcoded secrets.
    """
    detector = SecretDetector(min_entropy=min_entropy)

    # Use our file discovery logic (currently hardcoding python extensions)
    # The detector skips non .py files anyway in this MVP, but we can filter upfront.
    files = discover_files(Path(path), extensions=frozenset({".py"}))

    all_findings = []

    for file_path in files:
        # Check against basic excludes if needed
        # In MVP, basic string match for exclude
        skip = False
        for ex in exclude:
            if ex in str(file_path):
                skip = True
                break
        if skip:
            continue

        findings = detector.scan_file(str(file_path))
        all_findings.extend(findings)

    if output_format == "json":
        import json

        out = {
            "command": "scan",
            "files_scanned": len(files),
            "findings": [
                {
                    "file": f.file_path,
                    "line": f.line_number,
                    "variable": f.variable_name,
                    "snippet": f.value_snippet,
                    "confidence": f.confidence,
                    "reason": f.reason,
                }
                for f in all_findings
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        # Rich output formatting
        console = Console()
        console.print(f"Scanned {len(files)} files for secrets.\n")

        if not all_findings:
            console.print("[green]✓ No hardcoded secrets found![/green]")
        else:
            table = Table(title="Secret Scan Results")
            table.add_column("Confidence")
            table.add_column("Location")
            table.add_column("Variable")
            table.add_column("Snippet")
            table.add_column("Reason")

            # Sort by confidence HIGH -> MEDIUM -> LOW
            confidence_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
            sorted_findings = sorted(
                all_findings, key=lambda x: confidence_order.get(x.confidence, 3)
            )

            for f in sorted_findings:
                if f.confidence == "HIGH":
                    color = "red"
                elif f.confidence == "MEDIUM":
                    color = "yellow"
                else:
                    color = "blue"

                table.add_row(
                    f"[{color}]{f.confidence}[/{color}]",
                    f"{f.file_path}:{f.line_number}",
                    f.variable_name or "N/A",
                    f.value_snippet,
                    f.reason,
                )

            console.print(table)

    # Exit 1 if any HIGH confidence secrets are found, else 0
    if any(f.confidence == "HIGH" for f in all_findings):
        return 1
    return 0
