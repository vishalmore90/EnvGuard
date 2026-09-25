"""Implementation of the 'init' command."""

import logging
from pathlib import Path

from envguard.reporters.base import BaseReporter
from envguard.scanners.engine import ScannerEngine
from envguard.schema.loader import save_schema
from envguard.schema.models import EnvGuardSchema, EnvVarDefinition

logger = logging.getLogger(__name__)


def execute_init(
    path: str,
    output_path: str,
    languages: str | None,
    force: bool,
    verbose: bool,
    reporter: BaseReporter,
) -> int:
    """Execute the init command to scaffold a schema."""
    output_file = Path(output_path)

    if not force and output_file.exists():
        reporter.report_error(
            f"Schema file {output_path} already exists. Use --force to overwrite."
        )
        return 1

    engine = ScannerEngine()

    # Process languages option
    langs = None
    if languages:
        langs = [lang.strip().lower() for lang in languages.split(",")]

    scan_result = engine.scan_project(Path(path), langs)

    # Build schema
    variables = {}
    for name in sorted(scan_result.unique_names):
        # We can extract default value or type hints if our scanners provided them
        var_def = EnvVarDefinition(required=True)
        # Try to pull in scanned context if available
        for ref in scan_result.references:
            if ref.name == name and ref.has_default and ref.default_value is not None:
                var_def.default = ref.default_value
                var_def.required = False
                break

        variables[name] = var_def

    schema = EnvGuardSchema(version="1", variables=variables)

    try:
        save_schema(schema, output_file)
        reporter.report_init(scan_result, output_path)
        return 0
    except Exception as e:
        reporter.report_error(f"Failed to write schema: {e}")
        return 1
