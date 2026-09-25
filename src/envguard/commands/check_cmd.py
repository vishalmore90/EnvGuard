"""Implementation of the 'check' command."""

import logging
import os
from pathlib import Path

from envguard.reporters.base import BaseReporter
from envguard.schema.loader import load_schema
from envguard.schema.validator import SchemaValidator

logger = logging.getLogger(__name__)


def parse_dotenv(file_path: Path) -> dict[str, str]:
    """Extremely basic parser for .env files."""
    env_vars: dict[str, str] = {}
    if not file_path.exists():
        return env_vars

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                # Strip quotes if present
                val = val.strip()
                if (val.startswith('"') and val.endswith('"')) or (
                    val.startswith("'") and val.endswith("'")
                ):
                    val = val[1:-1]
                env_vars[key.strip()] = val
    return env_vars


def execute_check(
    schema_path: str,
    env_file: str | None,
    ci_mode: bool,
    verbose: bool,
    reporter: BaseReporter,
) -> int:
    """Execute the check command to validate environment."""
    s_path = Path(schema_path)
    if not s_path.exists():
        reporter.report_error(
            f"Schema file {schema_path} not found. Run 'envguard init' first."
        )
        return 1

    try:
        schema = load_schema(s_path)
    except Exception as e:
        reporter.report_error(f"Failed to load schema: {e}")
        return 1

    validator = SchemaValidator(schema)

    if env_file:
        e_path = Path(env_file)
        if not e_path.exists():
            reporter.report_error(f"Environment file {env_file} not found.")
            return 1
        env_vars = parse_dotenv(e_path)
    else:
        env_vars = dict(os.environ)

    errors = validator.validate_environment(env_vars)

    reporter.report_check(errors, len(schema.variables))

    has_errors = any(e.is_error for e in errors)
    has_warnings = any(not e.is_error for e in errors)

    if has_errors:
        return 1
    if ci_mode and has_warnings:
        return 1

    return 0
