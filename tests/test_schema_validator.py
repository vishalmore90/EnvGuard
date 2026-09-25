"""Tests for schema validator."""

from envguard.schema.models import EnvGuardSchema, EnvVarDefinition
from envguard.schema.validator import SchemaValidator


def test_validate_missing_required() -> None:
    schema = EnvGuardSchema(variables={"API_KEY": EnvVarDefinition(required=True)})
    validator = SchemaValidator(schema)
    errors = validator.validate_environment({})

    assert len(errors) == 1
    assert errors[0].var_name == "API_KEY"
    assert errors[0].is_error is True
    assert "Missing required" in errors[0].message


def test_validate_missing_optional() -> None:
    schema = EnvGuardSchema(variables={"PORT": EnvVarDefinition(required=False)})
    validator = SchemaValidator(schema)
    errors = validator.validate_environment({})

    assert len(errors) == 1
    assert errors[0].var_name == "PORT"
    assert errors[0].is_error is False  # Should be a warning
    assert "Optional" in errors[0].message


def test_validate_integer() -> None:
    schema = EnvGuardSchema(variables={"PORT": EnvVarDefinition(type="integer")})
    validator = SchemaValidator(schema)

    # Valid
    errors = validator.validate_environment({"PORT": "8080"})
    assert len(errors) == 0

    # Invalid
    errors = validator.validate_environment({"PORT": "eighty"})
    assert len(errors) == 1
    assert "Invalid integer" in errors[0].message


def test_validate_boolean() -> None:
    schema = EnvGuardSchema(variables={"DEBUG": EnvVarDefinition(type="boolean")})
    validator = SchemaValidator(schema)

    # Valid
    assert len(validator.validate_environment({"DEBUG": "true"})) == 0
    assert len(validator.validate_environment({"DEBUG": "False"})) == 0
    assert len(validator.validate_environment({"DEBUG": "1"})) == 0

    # Invalid
    errors = validator.validate_environment({"DEBUG": "enabled"})
    assert len(errors) == 1
    assert "Invalid boolean" in errors[0].message


def test_validate_choice() -> None:
    schema = EnvGuardSchema(
        variables={
            "LOG_LEVEL": EnvVarDefinition(type="choice", choices=["INFO", "DEBUG"])
        }
    )
    validator = SchemaValidator(schema)

    # Valid
    assert len(validator.validate_environment({"LOG_LEVEL": "INFO"})) == 0

    # Invalid
    errors = validator.validate_environment({"LOG_LEVEL": "WARN"})
    assert len(errors) == 1
    assert "Invalid choice" in errors[0].message


def test_validate_url() -> None:
    schema = EnvGuardSchema(variables={"DB": EnvVarDefinition(type="url")})
    validator = SchemaValidator(schema)

    # Valid
    assert len(validator.validate_environment({"DB": "postgresql://localhost"})) == 0

    # Invalid
    errors = validator.validate_environment({"DB": "localhost"})
    assert len(errors) == 1
    assert "Invalid URL" in errors[0].message
