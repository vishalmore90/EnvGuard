"""Tests for the check command."""

from pathlib import Path

from envguard.commands.check_cmd import execute_check
from envguard.reporters.json_reporter import JsonReporter
from envguard.schema.loader import save_schema
from envguard.schema.models import EnvGuardSchema, EnvVarDefinition


def test_execute_check_dotenv(tmp_path: Path) -> None:
    schema_path = tmp_path / ".envguard.yml"
    env_path = tmp_path / ".env"

    schema = EnvGuardSchema(
        variables={
            "API_KEY": EnvVarDefinition(required=True),
            "PORT": EnvVarDefinition(required=False, type="integer"),
        }
    )
    save_schema(schema, schema_path)

    # Create valid dotenv
    env_path.write_text("API_KEY=test\nPORT=8080\n")

    reporter = JsonReporter()
    exit_code = execute_check(
        schema_path=str(schema_path),
        env_file=str(env_path),
        ci_mode=False,
        verbose=False,
        reporter=reporter,
    )
    assert exit_code == 0

    # Invalid dotenv
    env_path.write_text("API_KEY=test\nPORT=not_an_int\n")
    exit_code = execute_check(
        schema_path=str(schema_path),
        env_file=str(env_path),
        ci_mode=False,
        verbose=False,
        reporter=reporter,
    )
    assert exit_code == 1


def test_execute_check_ci_mode(tmp_path: Path) -> None:
    schema_path = tmp_path / ".envguard.yml"
    env_path = tmp_path / ".env"

    # Schema with an optional variable that isn't provided
    schema = EnvGuardSchema(
        variables={
            "API_KEY": EnvVarDefinition(required=True),
            "OPTIONAL_FEATURE": EnvVarDefinition(required=False),
        }
    )
    save_schema(schema, schema_path)

    env_path.write_text("API_KEY=test\n")

    reporter = JsonReporter()

    # Normal mode -> exit 0 (warning only)
    exit_code = execute_check(
        schema_path=str(schema_path),
        env_file=str(env_path),
        ci_mode=False,
        verbose=False,
        reporter=reporter,
    )
    assert exit_code == 0

    # CI mode -> exit 1 (warnings become errors)
    exit_code_ci = execute_check(
        schema_path=str(schema_path),
        env_file=str(env_path),
        ci_mode=True,
        verbose=False,
        reporter=reporter,
    )
    assert exit_code_ci == 1
