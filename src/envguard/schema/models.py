"""Data models for the EnvGuard schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# Supported validation types
SchemaType = Literal[
    "string",
    "integer",
    "float",
    "boolean",
    "url",
    "email",
    "choice",
    "path",
]


@dataclass
class EnvVarDefinition:
    """Definition of a single environment variable from the schema."""

    # Core validation
    required: bool = True
    type: SchemaType = "string"

    # Optional constraints
    choices: list[str] = field(default_factory=list)

    # Metadata/Documentation
    description: str = ""
    example: str = ""
    default: str | None = None

    # Security
    sensitive: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> EnvVarDefinition:
        """Create a definition from a raw dictionary (from YAML)."""
        # Ensure we don't pass unknown kwargs
        valid_keys = {
            "required",
            "type",
            "choices",
            "description",
            "example",
            "default",
            "sensitive",
        }
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)  # type: ignore


@dataclass
class EnvGuardSchema:
    """The full parsed .envguard.yml schema."""

    version: str = "1"
    variables: dict[str, EnvVarDefinition] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> EnvGuardSchema:
        """Create a schema from a raw dictionary (from YAML)."""
        version = str(data.get("version", "1"))

        raw_vars = data.get("variables", {})
        if not isinstance(raw_vars, dict):
            raise TypeError("'variables' must be a dictionary")

        variables = {
            k: EnvVarDefinition.from_dict(v if isinstance(v, dict) else {})
            for k, v in raw_vars.items()
        }

        return cls(version=version, variables=variables)
