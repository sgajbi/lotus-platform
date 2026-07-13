from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any, Mapping, Sequence
from uuid import UUID


CONTRACT_VERSION = "lotus.endpoint-example-parity-contract.v1"
ALLOWED_NORMALIZATION_STRATEGIES = frozenset(
    {"rfc3339", "uuid", "non_empty_string", "environment_string"}
)
FORBIDDEN_NORMALIZATION_TOKENS = frozenset(
    {
        "blockers",
        "certificationBlockers",
        "certificationReady",
        "certificationStatus",
        "contractVersion",
        "lifecycleStatus",
        "readinessStatus",
        "schemaVersion",
        "supportabilityStatus",
        "supportedFeaturePromoted",
        "version",
    }
)
FAILURE_CODES = frozenset(
    {
        "array_length_mismatch",
        "duplicate_normalization_pointer",
        "forbidden_governance_normalization",
        "invalid_normalization_rule",
        "invalid_normalization_pointer",
        "missing_documented_field",
        "normalization_target_missing",
        "normalization_value_invalid",
        "stale_documented_field",
        "type_mismatch",
        "unsupported_normalization_strategy",
        "value_mismatch",
    }
)
_ENVIRONMENT_VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@-]{0,255}$")
_INVALID_POINTER_ESCAPE = re.compile(r"~(?![01])")


@dataclass(frozen=True)
class ExampleParityViolation:
    code: str
    pointer: str
    detail: str


def compare_endpoint_examples(
    documented: Any,
    runtime: Any,
    *,
    normalizations: Sequence[Mapping[str, str]] = (),
) -> tuple[ExampleParityViolation, ...]:
    documented_copy = deepcopy(documented)
    runtime_copy = deepcopy(runtime)
    normalization_errors = _apply_normalizations(
        documented_copy,
        runtime_copy,
        normalizations=normalizations,
    )
    if normalization_errors:
        return tuple(normalization_errors)

    violations: list[ExampleParityViolation] = []
    _compare(documented_copy, runtime_copy, pointer="", violations=violations)
    return tuple(violations)


def _apply_normalizations(
    documented: Any,
    runtime: Any,
    *,
    normalizations: Sequence[Mapping[str, str]],
) -> list[ExampleParityViolation]:
    errors: list[ExampleParityViolation] = []
    seen: set[str] = set()
    for index, rule in enumerate(normalizations):
        if not isinstance(rule, Mapping):
            errors.append(
                ExampleParityViolation(
                    "invalid_normalization_rule",
                    f"<normalizations[{index}]>",
                    "normalization rules must be objects",
                )
            )
            continue
        pointer = rule.get("pointer", "")
        strategy = rule.get("strategy", "")
        context = (
            pointer
            if isinstance(pointer, str) and pointer
            else f"<normalizations[{index}]>"
        )
        if not isinstance(pointer, str) or not pointer.startswith("/"):
            errors.append(
                ExampleParityViolation(
                    "invalid_normalization_pointer",
                    context,
                    "normalization pointers must be absolute RFC 6901 JSON pointers",
                )
            )
            continue
        if _INVALID_POINTER_ESCAPE.search(pointer):
            errors.append(
                ExampleParityViolation(
                    "invalid_normalization_pointer",
                    pointer,
                    "normalization pointers must use valid RFC 6901 escaping",
                )
            )
            continue
        if pointer in seen:
            errors.append(
                ExampleParityViolation(
                    "duplicate_normalization_pointer",
                    pointer,
                    "each normalized field must be declared exactly once",
                )
            )
            continue
        seen.add(pointer)
        if (
            not isinstance(strategy, str)
            or strategy not in ALLOWED_NORMALIZATION_STRATEGIES
        ):
            errors.append(
                ExampleParityViolation(
                    "unsupported_normalization_strategy",
                    pointer,
                    "normalization strategy is not approved by the platform contract",
                )
            )
            continue

        tokens = _pointer_tokens(pointer)
        forbidden = next(
            (token for token in tokens if token in FORBIDDEN_NORMALIZATION_TOKENS),
            None,
        )
        if forbidden is not None:
            errors.append(
                ExampleParityViolation(
                    "forbidden_governance_normalization",
                    pointer,
                    f"governance field {forbidden!r} must use exact structural comparison",
                )
            )
            continue

        documented_location = _resolve_pointer(documented, tokens)
        runtime_location = _resolve_pointer(runtime, tokens)
        if documented_location is None or runtime_location is None:
            errors.append(
                ExampleParityViolation(
                    "normalization_target_missing",
                    pointer,
                    "normalization target must exist in both examples",
                )
            )
            continue

        documented_parent, documented_key = documented_location
        runtime_parent, runtime_key = runtime_location
        documented_value = documented_parent[documented_key]
        runtime_value = runtime_parent[runtime_key]
        if not (
            _normalization_value_valid(documented_value, strategy)
            and _normalization_value_valid(runtime_value, strategy)
        ):
            errors.append(
                ExampleParityViolation(
                    "normalization_value_invalid",
                    pointer,
                    "both values must satisfy the declared normalization strategy",
                )
            )
            continue

        sentinel = {"$normalized": strategy, "$pointer": pointer}
        documented_parent[documented_key] = sentinel
        runtime_parent[runtime_key] = deepcopy(sentinel)
    return errors


def _pointer_tokens(pointer: str) -> tuple[str, ...]:
    return tuple(
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer[1:].split("/")
    )


def _resolve_pointer(value: Any, tokens: Sequence[str]) -> tuple[Any, str | int] | None:
    current = value
    for token in tokens[:-1]:
        if isinstance(current, dict) and token in current:
            current = current[token]
            continue
        if isinstance(current, list) and token.isdigit() and int(token) < len(current):
            current = current[int(token)]
            continue
        return None

    final = tokens[-1]
    if isinstance(current, dict) and final in current:
        return current, final
    if isinstance(current, list) and final.isdigit() and int(final) < len(current):
        return current, int(final)
    return None


def _normalization_value_valid(value: Any, strategy: str) -> bool:
    if not isinstance(value, str):
        return False
    if strategy == "non_empty_string":
        return bool(value.strip()) and value == value.strip()
    if strategy == "environment_string":
        return _ENVIRONMENT_VALUE.fullmatch(value) is not None
    if strategy == "uuid":
        try:
            return str(UUID(value)) == value.lower()
        except ValueError:
            return False
    if strategy == "rfc3339":
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return False
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    return False


def _compare(
    documented: Any,
    runtime: Any,
    *,
    pointer: str,
    violations: list[ExampleParityViolation],
) -> None:
    documented_type = _json_type(documented)
    runtime_type = _json_type(runtime)
    display_pointer = pointer or "/"
    if documented_type != runtime_type:
        violations.append(
            ExampleParityViolation(
                "type_mismatch",
                display_pointer,
                f"documented type {documented_type} does not match runtime type {runtime_type}",
            )
        )
        return

    if isinstance(documented, dict):
        documented_keys = set(documented)
        runtime_keys = set(runtime)
        for key in sorted(runtime_keys - documented_keys):
            violations.append(
                ExampleParityViolation(
                    "missing_documented_field",
                    _join_pointer(pointer, key),
                    "runtime field is missing from the documented example",
                )
            )
        for key in sorted(documented_keys - runtime_keys):
            violations.append(
                ExampleParityViolation(
                    "stale_documented_field",
                    _join_pointer(pointer, key),
                    "documented field is absent from the runtime example",
                )
            )
        for key in sorted(documented_keys & runtime_keys):
            _compare(
                documented[key],
                runtime[key],
                pointer=_join_pointer(pointer, key),
                violations=violations,
            )
        return

    if isinstance(documented, list):
        if len(documented) != len(runtime):
            violations.append(
                ExampleParityViolation(
                    "array_length_mismatch",
                    display_pointer,
                    "documented and runtime arrays must have the same length",
                )
            )
            return
        for index, (documented_item, runtime_item) in enumerate(
            zip(documented, runtime)
        ):
            _compare(
                documented_item,
                runtime_item,
                pointer=_join_pointer(pointer, str(index)),
                violations=violations,
            )
        return

    if documented != runtime:
        violations.append(
            ExampleParityViolation(
                "value_mismatch",
                display_pointer,
                "documented and runtime values differ",
            )
        )


def _json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _join_pointer(pointer: str, token: str) -> str:
    escaped = token.replace("~", "~0").replace("/", "~1")
    return f"{pointer}/{escaped}"
