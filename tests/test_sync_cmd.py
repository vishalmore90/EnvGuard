"""Tests for the sync command."""

from pathlib import Path

from envguard.commands.sync_cmd import execute_sync
from envguard.reporters.json_reporter import JsonReporter
from envguard.schema.loader import save_schema
from envguard.schema.models import EnvGuardSchema, EnvVarDefinition


def test_sync_generates_example(tmp_path: Path) -> None:
    schema_path = tmp_path / ".envguard.yml"
    output_path = tmp_path / ".env.example"

    schema = EnvGuardSchema(
        variables={
            "API_KEY": EnvVarDefinition(
                required=True, description="The API Key", example="sk_test_123"
            ),
            "PORT": EnvVarDefinition(required=False, type="integer", default="8080"),
        }
    )
    save_schema(schema, schema_path)

    reporter = JsonReporter()
    exit_code = execute_sync(str(schema_path), str(output_path), False, reporter)

    assert exit_code == 0
    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")
    assert "sk_test_123" in content
    assert "API_KEY=sk_test_123" in content
    assert "# The API Key" in content
    assert "Type: integer" in content
    assert "PORT=8080" in content


def test_sync_requires_force_to_overwrite(tmp_path: Path) -> None:
    schema_path = tmp_path / ".envguard.yml"
    output_path = tmp_path / ".env.example"

    schema = EnvGuardSchema()
    save_schema(schema, schema_path)

    # Pre-create the output
    output_path.write_text("old")

    reporter = JsonReporter()
    exit_code = execute_sync(str(schema_path), str(output_path), False, reporter)

    # Should fail because it exists and not forced
    assert exit_code == 1
    assert output_path.read_text() == "old"

    # Now with force
    exit_code2 = execute_sync(str(schema_path), str(output_path), True, reporter)
    assert exit_code2 == 0
    assert output_path.read_text(encoding="utf-8") != "old"


def test_sync_handles_missing_schema(tmp_path: Path) -> None:
    schema_path = tmp_path / "missing.yml"
    output_path = tmp_path / ".env.example"

    reporter = JsonReporter()
    exit_code = execute_sync(str(schema_path), str(output_path), False, reporter)

    assert exit_code == 1
    assert not output_path.exists()
