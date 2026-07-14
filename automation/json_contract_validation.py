from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must be a JSON object")
    return payload


def validate_json_schema_subset(schema_path: Path, document_path: Path) -> list[str]:
    schema = load_json_object(schema_path)
    document = load_json_object(document_path)
    errors: list[str] = []
    _validate_node(document, schema, [document_path.name], errors, root_schema=schema)
    return errors


def _validate_node(
    value: Any,
    schema: dict[str, Any],
    path: list[str],
    errors: list[str],
    *,
    root_schema: dict[str, Any],
) -> None:
    schema = _resolve_ref(schema, root_schema)
    if "const" in schema and value != schema["const"]:
        errors.append(f"{'.'.join(path)}: must be {schema['const']!r}")
        return

    expected_type = schema.get("type")
    if expected_type is not None and not _matches_schema_type(value, expected_type):
        errors.append(f"{'.'.join(path)}: invalid type")
        return

    enum = schema.get("enum")
    if enum is not None and value not in enum:
        errors.append(f"{'.'.join(path)}: must be one of {', '.join(enum)}")

    minimum = schema.get("minimum")
    if isinstance(minimum, int) and isinstance(value, int) and value < minimum:
        errors.append(f"{'.'.join(path)}: must be greater than or equal to {minimum}")

    _validate_string_constraints(value, schema, path, errors)
    _validate_object_constraints(value, schema, path, errors, root_schema=root_schema)
    _validate_array_constraints(value, schema, path, errors, root_schema=root_schema)


def _resolve_ref(schema: dict[str, Any], root_schema: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not isinstance(ref, str):
        return schema
    if not ref.startswith("#/$defs/"):
        return schema
    name = ref.removeprefix("#/$defs/")
    resolved = root_schema.get("$defs", {}).get(name)
    return resolved if isinstance(resolved, dict) else schema


def _validate_string_constraints(
    value: Any,
    schema: dict[str, Any],
    path: list[str],
    errors: list[str],
) -> None:
    if not isinstance(value, str):
        return
    pattern = schema.get("pattern")
    if isinstance(pattern, str) and not re.search(pattern, value):
        errors.append(f"{'.'.join(path)}: does not match pattern {pattern}")
    min_length = schema.get("minLength")
    if isinstance(min_length, int) and len(value) < min_length:
        errors.append(f"{'.'.join(path)}: is shorter than {min_length} characters")
    max_length = schema.get("maxLength")
    if isinstance(max_length, int) and len(value) > max_length:
        errors.append(f"{'.'.join(path)}: is longer than {max_length} characters")


def _validate_object_constraints(
    value: Any,
    schema: dict[str, Any],
    path: list[str],
    errors: list[str],
    *,
    root_schema: dict[str, Any],
) -> None:
    if not isinstance(value, dict):
        return
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    for field in required:
        if field not in value:
            errors.append(f"{'.'.join(path)}: '{field}' is a required property")
    if schema.get("additionalProperties") is False:
        unexpected = sorted(set(value) - set(properties))
        if unexpected:
            quoted = ", ".join(repr(field) for field in unexpected)
            errors.append(f"{'.'.join(path)}: Additional properties are not allowed ({quoted})")
    for field, field_schema in properties.items():
        if field in value and isinstance(field_schema, dict):
            _validate_node(
                value[field],
                field_schema,
                [*path, field],
                errors,
                root_schema=root_schema,
            )


def _validate_array_constraints(
    value: Any,
    schema: dict[str, Any],
    path: list[str],
    errors: list[str],
    *,
    root_schema: dict[str, Any],
) -> None:
    if not isinstance(value, list):
        return
    min_items = schema.get("minItems")
    if isinstance(min_items, int) and len(value) < min_items:
        errors.append(f"{'.'.join(path)}: must contain at least {min_items} items")
    if schema.get("uniqueItems") is True:
        canonical_items = [json.dumps(item, sort_keys=True) for item in value]
        if len(set(canonical_items)) != len(canonical_items):
            errors.append(f"{'.'.join(path)}: items must be unique")
    item_schema = schema.get("items")
    if isinstance(item_schema, dict):
        for index, item in enumerate(value):
            _validate_node(
                item,
                item_schema,
                [*path, str(index)],
                errors,
                root_schema=root_schema,
            )


def _matches_schema_type(value: Any, expected_type: str | list[str]) -> bool:
    if isinstance(expected_type, list):
        return any(_matches_schema_type(value, item) for item in expected_type)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    return False
