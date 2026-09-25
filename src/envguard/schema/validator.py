"""Schema validation engine."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from envguard.schema.models import EnvGuardSchema, EnvVarDefinition


@dataclass
class ValidationError:
    """Represents a single validation failure."""

    var_name: str
    message: str
    is_error: bool = True  # False implies a warning


class SchemaValidator:
    """Validates actual environment values against a schema."""

    def __init__(self, schema: EnvGuardSchema) -> None:
        self.schema = schema

    def validate_environment(
        self, env_vars: dict[str, str] | None = None
    ) -> list[ValidationError]:
        """
        Validate a dictionary of env vars (or os.environ) against the schema.

        Args:
            env_vars: A dict of environment variables. Defaults to os.environ.

        Returns:
            A list of ValidationErrors. Empty list means success.
        """
        if env_vars is None:
            env_vars = dict(os.environ)

        errors: list[ValidationError] = []

        for name, var_def in self.schema.variables.items():
            value = env_vars.get(name)

            # Check presence
            if value is None or value.strip() == "":
                if var_def.required:
                    errors.append(
                        ValidationError(name, f"Missing required variable: {name}")
                    )
                else:
                    errors.append(
                        ValidationError(
                            name, f"Optional variable not set: {name}", is_error=False
                        )
                    )
                continue

            # Check type/constraints
            error = self._validate_value(name, value, var_def)
            if error:
                errors.append(ValidationError(name, error))

        return errors

    def _validate_value(
        self, name: str, value: str, var_def: EnvVarDefinition
    ) -> str | None:
        """Validate a specific value against its definition."""
        t = var_def.type

        try:
            if t == "integer":
                int(value)
            elif t == "float":
                float(value)
            elif t == "boolean":
                if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
                    return f"Invalid boolean: '{value}'"
            elif t == "url":
                parsed = urlparse(value)
                if not all([parsed.scheme, parsed.netloc]):
                    return f"Invalid URL: '{value}'"
            elif t == "email":
                if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                    return f"Invalid email: '{value}'"
            elif t == "choice":
                if var_def.choices and value not in var_def.choices:
                    return (
                        f"Invalid choice '{value}'. Must be one of: {var_def.choices}"
                    )
            elif t == "path":
                pass  # any non-empty string is a valid path for now
            # 'string' requires no special validation here
        except ValueError:
            return f"Invalid {t}: '{value}'"

        return None
