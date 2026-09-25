"""YAML schema loader and saver."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from envguard.schema.models import EnvGuardSchema

logger = logging.getLogger(__name__)


def load_schema(path: Path) -> EnvGuardSchema:
    """
    Load an EnvGuard schema from a YAML file.

    Args:
        path: Path to the .envguard.yml file.

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If the YAML is invalid.
        TypeError: If the schema structure is invalid.
    """
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return EnvGuardSchema()

    if not isinstance(data, dict):
        raise TypeError("Root of schema must be a dictionary")

    return EnvGuardSchema.from_dict(data)


def save_schema(schema: EnvGuardSchema, path: Path) -> None:
    """
    Save an EnvGuard schema to a YAML file.

    Args:
        schema: The schema to save.
        path: Path to the destination .envguard.yml file.
    """
    # Convert dataclasses back to dict
    variables_dict = {}
    for name, var_def in schema.variables.items():
        var_dict: dict[str, object] = {}
        if not var_def.required:
            var_dict["required"] = False
        if var_def.type != "string":
            var_dict["type"] = var_def.type
        if var_def.choices:
            var_dict["choices"] = var_def.choices
        if var_def.description:
            var_dict["description"] = var_def.description
        if var_def.example:
            var_dict["example"] = var_def.example
        if var_def.default is not None:
            var_dict["default"] = var_def.default
        if var_def.sensitive:
            var_dict["sensitive"] = True

        variables_dict[name] = var_dict

    data = {
        "version": schema.version,
        "variables": variables_dict,
    }

    # Custom dump to make it look nice
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
