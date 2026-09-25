"""Tests for schema loader."""

from pathlib import Path

import pytest
import yaml

from envguard.schema.loader import load_schema, save_schema
from envguard.schema.models import EnvGuardSchema, EnvVarDefinition


def test_load_schema_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / ".envguard.yml"
    with pytest.raises(FileNotFoundError):
        load_schema(missing)


def test_load_schema_invalid_yaml(tmp_path: Path) -> None:
    bad_yaml = tmp_path / ".envguard.yml"
    bad_yaml.write_text("unclosed: [ array")
    with pytest.raises(yaml.YAMLError):
        load_schema(bad_yaml)


def test_load_schema_invalid_type(tmp_path: Path) -> None:
    bad_type = tmp_path / ".envguard.yml"
    bad_type.write_text("- just\n- a\n- list\n")
    with pytest.raises(TypeError, match="must be a dictionary"):
        load_schema(bad_type)


def test_load_schema_empty(tmp_path: Path) -> None:
    empty = tmp_path / ".envguard.yml"
    empty.write_text("")
    schema = load_schema(empty)
    assert schema.version == "1"
    assert schema.variables == {}


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    schema_path = tmp_path / ".envguard.yml"

    schema = EnvGuardSchema(
        version="2",
        variables={
            "TEST_VAR": EnvVarDefinition(
                required=False,
                type="choice",
                choices=["A", "B"],
                description="Test description",
                sensitive=True,
            )
        },
    )

    save_schema(schema, schema_path)

    # Verify it was written properly
    assert schema_path.exists()
    content = schema_path.read_text(encoding="utf-8")
    assert "version: '2'" in content
    assert "TEST_VAR:" in content
    assert "sensitive: true" in content

    # Load it back
    loaded = load_schema(schema_path)
    assert loaded.version == "2"
    assert "TEST_VAR" in loaded.variables

    var = loaded.variables["TEST_VAR"]
    assert var.required is False
    assert var.type == "choice"
    assert var.choices == ["A", "B"]
    assert var.description == "Test description"
    assert var.sensitive is True
