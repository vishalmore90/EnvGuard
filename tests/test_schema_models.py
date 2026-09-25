"""Tests for schema models."""

from envguard.schema.models import EnvGuardSchema, EnvVarDefinition


def test_env_var_definition_defaults() -> None:
    var = EnvVarDefinition()
    assert var.required is True
    assert var.type == "string"
    assert var.choices == []
    assert var.description == ""
    assert var.example == ""
    assert var.default is None
    assert var.sensitive is False


def test_env_var_definition_from_dict() -> None:
    data = {
        "required": False,
        "type": "integer",
        "default": "8080",
        "description": "Port",
        "unknown_key": "should be ignored",
    }
    var = EnvVarDefinition.from_dict(data)
    assert var.required is False
    assert var.type == "integer"
    assert var.default == "8080"
    assert var.description == "Port"
    assert not hasattr(var, "unknown_key")


def test_envguard_schema_defaults() -> None:
    schema = EnvGuardSchema()
    assert schema.version == "1"
    assert schema.variables == {}


def test_envguard_schema_from_dict() -> None:
    data: dict[str, object] = {
        "version": "1.1",
        "variables": {
            "API_KEY": {"required": True, "sensitive": True},
            "DEBUG": {"required": False, "type": "boolean"},
        },
    }
    schema = EnvGuardSchema.from_dict(data)
    assert schema.version == "1.1"
    assert len(schema.variables) == 2

    assert schema.variables["API_KEY"].required is True
    assert schema.variables["API_KEY"].sensitive is True

    assert schema.variables["DEBUG"].required is False
    assert schema.variables["DEBUG"].type == "boolean"
