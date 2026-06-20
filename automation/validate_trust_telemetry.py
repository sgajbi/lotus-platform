from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from domain_product_discovery import DEFAULT_CATALOG_PATH, load_catalog


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRUST_METADATA_REGISTRY_PATH = (
    ROOT
    / "platform-contracts"
    / "domain-vocabulary"
    / "domain-data-product-trust-metadata.v1.json"
)
DEFAULT_SEMANTICS_REGISTRY_PATH = (
    ROOT
    / "platform-contracts"
    / "domain-vocabulary"
    / "domain-data-product-semantics.v1.json"
)
TELEMETRY_GLOB = "*.json"
REPOSITORY_PATTERN = re.compile(r"^lotus-[a-z0-9-]+$")
SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
PRODUCT_VERSION_PATTERN = re.compile(r"^(v[0-9]+|[0-9]+\.[0-9]+\.[0-9]+)$")
PRODUCT_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9]+$")
VALID_FRESHNESS_STATES = {"current", "stale", "unknown"}
VALID_VALIDATION_LANES = {
    "feature",
    "pr-merge",
    "main-releasability",
    "platform-end-to-end",
}
TRUST_STATUS_FIELDS = {
    "completeness_status": "completeness_statuses",
    "reconciliation_status": "reconciliation_statuses",
    "data_quality_status": "data_quality_statuses",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _append_issue(issues: list[str], path: Path, message: str) -> None:
    issues.append(f"{path}: {message}")


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_non_empty_list(value: object) -> bool:
    return isinstance(value, list) and bool(value)


def _registry_keys(registry_payload: dict[str, Any], path: tuple[str, ...]) -> set[str]:
    current: Any = registry_payload
    for key in path:
        current = current.get(key, {}) if isinstance(current, dict) else {}
    if not isinstance(current, list):
        return set()
    return {
        entry.get("key", "")
        for entry in current
        if isinstance(entry, dict) and isinstance(entry.get("key"), str)
    }


def _load_validation_context(
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    trust_metadata_registry_path: Path = DEFAULT_TRUST_METADATA_REGISTRY_PATH,
    semantics_registry_path: Path = DEFAULT_SEMANTICS_REGISTRY_PATH,
) -> dict[str, Any]:
    catalog = load_catalog(catalog_path)
    trust_registry = _load_json(trust_metadata_registry_path)
    semantics_registry = _load_json(semantics_registry_path)
    return {
        "products_by_id": {
            product["product_id"]: product for product in catalog.get("products", [])
        },
        "trust_metadata_keys": _registry_keys(
            trust_registry, ("trust_metadata_fields",)
        ),
        "evidence_access_classes": _registry_keys(
            trust_registry, ("evidence_access_classes",)
        ),
        "freshness_classes": _registry_keys(
            semantics_registry, ("trust_vocabularies", "freshness_classes")
        ),
        "completeness_statuses": _registry_keys(
            semantics_registry, ("trust_vocabularies", "completeness_statuses")
        ),
        "reconciliation_statuses": _registry_keys(
            semantics_registry, ("trust_vocabularies", "reconciliation_statuses")
        ),
        "data_quality_statuses": _registry_keys(
            semantics_registry, ("trust_vocabularies", "data_quality_statuses")
        ),
    }


def _validate_snapshot_contract_header(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
) -> None:
    if payload.get("contract_id") != "lotus-domain-product-trust-telemetry-snapshot":
        _append_issue(
            issues,
            path,
            "contract_id must be lotus-domain-product-trust-telemetry-snapshot",
        )
    if not isinstance(
        payload.get("contract_version"), str
    ) or not SEMVER_PATTERN.fullmatch(payload["contract_version"]):
        _append_issue(issues, path, "contract_version must be semantic versioning")
    if "RFC-0087" not in payload.get("governed_by_rfcs", []):
        _append_issue(issues, path, "governed_by_rfcs must include RFC-0087")


def _validate_snapshot_required_identity_fields(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
) -> None:
    for field_name in ("emitted_at_utc", "product_id", "source_repository"):
        if not _is_non_empty_string(payload.get(field_name)):
            _append_issue(issues, path, f"{field_name} must be a non-empty string")
    if not isinstance(
        payload.get("source_repository"), str
    ) or not REPOSITORY_PATTERN.fullmatch(payload.get("source_repository", "")):
        _append_issue(issues, path, "source_repository must match Lotus repo naming")


def _find_catalog_product(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any] | None:
    product_id = payload.get("product_id")
    product = context["products_by_id"].get(product_id)
    if product is None:
        _append_issue(
            issues, path, f"product_id does not exist in catalog: {product_id}"
        )
        return None
    return product


def _validate_catalog_identity_match(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
    product: dict[str, Any],
) -> None:
    expected_identity = {
        "producer_repository": product["producer_repository"],
        "product_name": product["product_name"],
        "product_version": product["product_version"],
    }
    for field_name, expected_value in expected_identity.items():
        observed_value = payload.get(field_name)
        if observed_value != expected_value:
            _append_issue(
                issues,
                path,
                f"{field_name} must match catalog product identity {expected_value}",
            )


def _validate_product_identity_shape(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
) -> None:
    if not REPOSITORY_PATTERN.fullmatch(str(payload.get("producer_repository", ""))):
        _append_issue(issues, path, "producer_repository must match Lotus repo naming")
    if not PRODUCT_NAME_PATTERN.fullmatch(str(payload.get("product_name", ""))):
        _append_issue(issues, path, "product_name must use stable product naming")
    if not PRODUCT_VERSION_PATTERN.fullmatch(str(payload.get("product_version", ""))):
        _append_issue(
            issues, path, "product_version must use vN or semantic versioning"
        )


def _validate_identity(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any] | None:
    _validate_snapshot_contract_header(issues, path, payload)
    _validate_snapshot_required_identity_fields(issues, path, payload)

    product = _find_catalog_product(issues, path, payload, context)
    if product is None:
        return None

    _validate_catalog_identity_match(issues, path, payload, product)
    _validate_product_identity_shape(issues, path, payload)
    return product


def _validate_freshness_vocabulary(
    issues: list[str],
    path: Path,
    freshness: dict[str, Any],
    context: dict[str, Any],
) -> None:
    if freshness.get("freshness_class") not in context["freshness_classes"]:
        _append_issue(
            issues,
            path,
            "freshness.freshness_class must reference the trust vocabulary registry",
        )
    if freshness.get("freshness_state") not in VALID_FRESHNESS_STATES:
        _append_issue(
            issues,
            path,
            "freshness.freshness_state must be current, stale, or unknown",
        )
    if not _is_non_empty_string(freshness.get("evaluated_at_utc")):
        _append_issue(
            issues,
            path,
            "freshness.evaluated_at_utc must be a non-empty string",
        )


def _validate_freshness_age(
    issues: list[str],
    path: Path,
    freshness: dict[str, Any],
) -> None:
    freshness_state = freshness.get("freshness_state")
    age_seconds = freshness.get("age_seconds")
    max_allowed_age_seconds = freshness.get("max_allowed_age_seconds")
    if age_seconds is not None and (
        not isinstance(age_seconds, int) or age_seconds < 0
    ):
        _append_issue(issues, path, "freshness.age_seconds must be >= 0")
    if max_allowed_age_seconds is not None and (
        not isinstance(max_allowed_age_seconds, int) or max_allowed_age_seconds < 1
    ):
        _append_issue(issues, path, "freshness.max_allowed_age_seconds must be >= 1")
    if (
        freshness_state == "current"
        and isinstance(age_seconds, int)
        and isinstance(max_allowed_age_seconds, int)
        and age_seconds > max_allowed_age_seconds
    ):
        _append_issue(
            issues,
            path,
            "freshness.freshness_state current conflicts with age_seconds greater than max_allowed_age_seconds",
        )


def _validate_freshness(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
    context: dict[str, Any],
) -> None:
    freshness = payload.get("freshness")
    if not isinstance(freshness, dict):
        _append_issue(issues, path, "freshness must be an object")
        return
    _validate_freshness_vocabulary(issues, path, freshness, context)
    _validate_freshness_age(issues, path, freshness)


def _validate_registry_statuses(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
    context: dict[str, Any],
) -> None:
    for field_name, context_key in TRUST_STATUS_FIELDS.items():
        if payload.get(field_name) not in context[context_key]:
            _append_issue(
                issues,
                path,
                f"{field_name} must reference the trust vocabulary registry",
            )


def _validate_statuses(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
    context: dict[str, Any],
) -> None:
    _validate_freshness(issues, path, payload, context)
    _validate_registry_statuses(issues, path, payload, context)


def _validate_lineage_and_blocking(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
    context: dict[str, Any],
) -> None:
    lineage = payload.get("lineage")
    if not isinstance(lineage, dict):
        _append_issue(issues, path, "lineage must be an object")
    else:
        if not isinstance(lineage.get("lineage_materialized"), bool):
            _append_issue(issues, path, "lineage.lineage_materialized must be boolean")
        if (
            lineage.get("evidence_access_class")
            not in context["evidence_access_classes"]
        ):
            _append_issue(
                issues,
                path,
                "lineage.evidence_access_class must reference the trust metadata registry",
            )
        evidence_uris = lineage.get("evidence_uris", [])
        if evidence_uris is not None and not isinstance(evidence_uris, list):
            _append_issue(issues, path, "lineage.evidence_uris must be an array")

    blocking = payload.get("blocking")
    if not isinstance(blocking, dict):
        _append_issue(issues, path, "blocking must be an object")
        return
    if not isinstance(blocking.get("blocked"), bool):
        _append_issue(issues, path, "blocking.blocked must be boolean")
    if blocking.get("blocked") is True and not _is_non_empty_string(
        blocking.get("blocked_reason")
    ):
        _append_issue(
            issues,
            path,
            "blocking.blocked_reason is required when blocking.blocked is true",
        )


def _validate_observed_metadata(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
    product: dict[str, Any] | None,
    context: dict[str, Any],
) -> None:
    observed = payload.get("observed_trust_metadata")
    if not isinstance(observed, dict):
        _append_issue(issues, path, "observed_trust_metadata must be an object")
        return
    unknown_fields = sorted(set(observed) - context["trust_metadata_keys"])
    if unknown_fields:
        _append_issue(
            issues,
            path,
            "observed_trust_metadata contains unknown fields: "
            + ", ".join(unknown_fields),
        )
    if product is not None:
        undeclared_fields = sorted(
            set(observed) - set(product.get("required_trust_metadata", []))
        )
        if undeclared_fields:
            _append_issue(
                issues,
                path,
                "observed_trust_metadata contains fields not declared by the product: "
                + ", ".join(undeclared_fields),
            )


def _validate_evidence(issues: list[str], path: Path, payload: dict[str, Any]) -> None:
    evidence = payload.get("evidence")
    if not isinstance(evidence, dict):
        _append_issue(issues, path, "evidence must be an object")
        return
    if not _is_non_empty_string(evidence.get("correlation_id")):
        _append_issue(issues, path, "evidence.correlation_id must be non-empty")
    validation_lanes = evidence.get("validation_lanes")
    if not _is_non_empty_list(validation_lanes):
        _append_issue(issues, path, "evidence.validation_lanes must be non-empty")
        return
    invalid_lanes = sorted(set(validation_lanes) - VALID_VALIDATION_LANES)
    if invalid_lanes:
        _append_issue(
            issues,
            path,
            "evidence.validation_lanes contains unsupported lanes: "
            + ", ".join(invalid_lanes),
        )


def validate_trust_telemetry_snapshot(
    path: Path,
    payload: dict[str, Any],
    *,
    context: dict[str, Any] | None = None,
) -> list[str]:
    context = context or _load_validation_context()
    issues: list[str] = []
    product = _validate_identity(issues, path, payload, context)
    _validate_statuses(issues, path, payload, context)
    _validate_lineage_and_blocking(issues, path, payload, context)
    _validate_observed_metadata(issues, path, payload, product, context)
    _validate_evidence(issues, path, payload)
    return issues


def _iter_telemetry_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(
        candidate
        for candidate in path.rglob(TELEMETRY_GLOB)
        if candidate.name != "trust-telemetry-snapshot.schema.json"
    )


def validate_trust_telemetry_path(
    path: Path,
    *,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    trust_metadata_registry_path: Path = DEFAULT_TRUST_METADATA_REGISTRY_PATH,
    semantics_registry_path: Path = DEFAULT_SEMANTICS_REGISTRY_PATH,
) -> list[str]:
    context = _load_validation_context(
        catalog_path,
        trust_metadata_registry_path,
        semantics_registry_path,
    )
    telemetry_paths = _iter_telemetry_paths(path)
    if not telemetry_paths:
        return [f"{path}: no trust telemetry snapshot files found"]

    issues: list[str] = []
    for telemetry_path in telemetry_paths:
        try:
            payload = _load_json(telemetry_path)
        except json.JSONDecodeError as exc:
            issues.append(f"{telemetry_path}: invalid JSON: {exc}")
            continue
        issues.extend(
            validate_trust_telemetry_snapshot(
                telemetry_path,
                payload,
                context=context,
            )
        )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Lotus domain-product trust telemetry snapshots."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Telemetry snapshot file or directory containing *.json snapshots.",
    )
    parser.add_argument(
        "--catalog",
        default=DEFAULT_CATALOG_PATH,
        type=Path,
        help="Generated domain-product catalog used to verify product identity.",
    )
    args = parser.parse_args(argv)

    issues = validate_trust_telemetry_path(args.path, catalog_path=args.catalog)
    if issues:
        for issue in issues:
            print(issue)
        return 1

    print(
        f"Validated {len(_iter_telemetry_paths(args.path))} trust telemetry snapshot(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
