from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PRODUCT_GLOB = "*-products.v1.json"
CONSUMER_GLOB = "*-consumers.v1.json"
SEMANTICS_REGISTRY_FILENAME = "domain-data-product-semantics.v1.json"
TRUST_METADATA_REGISTRY_FILENAME = "domain-data-product-trust-metadata.v1.json"
REPOSITORY_PATTERN = re.compile(r"^lotus-[a-z0-9-]+$")
SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
PRODUCT_VERSION_PATTERN = re.compile(r"^(v[0-9]+|[0-9]+\.[0-9]+\.[0-9]+)$")
PRODUCT_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9]+$")

REQUIRED_PRODUCT_FIELDS = {
    "product_name",
    "product_version",
    "owner_repository",
    "product_family",
    "authoritative_domain",
    "lifecycle_status",
    "request_scope",
    "temporal_scope",
    "temporal_semantics_ref",
    "identifier_refs",
    "required_trust_metadata",
    "freshness_policy",
    "completeness_policy",
    "lineage_policy",
    "security_profile_ref",
    "approved_consumers",
    "deprecation_policy",
}

REQUIRED_DEPENDENCY_FIELDS = {
    "product_name",
    "producer_repository",
    "required_product_version",
    "required_trust_metadata",
    "migration_posture",
    "consumption_mode",
    "business_purpose",
    "validation_lanes",
    "failure_posture",
}


def _find_semantics_registry_path(directory: Path) -> Path:
    return directory.resolve().parent / "domain-vocabulary" / SEMANTICS_REGISTRY_FILENAME


def _find_trust_metadata_registry_path(directory: Path) -> Path:
    return directory.resolve().parent / "domain-vocabulary" / TRUST_METADATA_REGISTRY_FILENAME


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _append_issue(issues: list[str], path: Path, message: str) -> None:
    issues.append(f"{path}: {message}")


def _is_non_empty_list(value: object) -> bool:
    return isinstance(value, list) and len(value) > 0


def _parse_product_version(version: str) -> tuple[int, ...] | None:
    if re.fullmatch(r"^v[0-9]+$", version):
        return (0, int(version[1:]))
    semver = SEMVER_PATTERN.fullmatch(version)
    if semver:
        return (1, *[int(part) for part in version.split(".")])
    return None


def _validate_registry_entry_list(
    issues: list[str],
    path: Path,
    *,
    field_name: str,
    entries: object,
    required_string_fields: tuple[str, ...],
) -> set[str]:
    keys: set[str] = set()

    if not _is_non_empty_list(entries):
        _append_issue(issues, path, f"{field_name} must be a non-empty array")
        return keys

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            _append_issue(issues, path, f"{field_name}[{index}] must be an object")
            continue

        key = entry.get("key")
        if not isinstance(key, str) or not re.fullmatch(r"^[a-z][a-z0-9_]+$", key):
            _append_issue(issues, path, f"{field_name}[{index}].key must be snake_case")
        elif key in keys:
            _append_issue(issues, path, f"{field_name} contains duplicate key {key}")
        else:
            keys.add(key)

        for required_field in required_string_fields:
            value = entry.get(required_field)
            if not isinstance(value, str) or not value.strip():
                _append_issue(
                    issues,
                    path,
                    f"{field_name}[{index}].{required_field} must be a non-empty string",
                )

    return keys


def validate_semantics_registry(path: Path, payload: dict) -> list[str]:
    issues: list[str] = []

    if payload.get("contract_id") != "domain-data-product-semantics":
        _append_issue(issues, path, "contract_id must be 'domain-data-product-semantics'")
    if not isinstance(payload.get("contract_version"), str) or not SEMVER_PATTERN.fullmatch(
        payload["contract_version"]
    ):
        _append_issue(issues, path, "contract_version must be semver")
    if payload.get("governed_by_rfc") != "RFC-0084":
        _append_issue(issues, path, "governed_by_rfc must be 'RFC-0084'")
    if payload.get("domain") != "domain_data_product_semantics":
        _append_issue(issues, path, "domain must be 'domain_data_product_semantics'")
    if not isinstance(payload.get("description"), str) or not payload["description"].strip():
        _append_issue(issues, path, "description must be a non-empty string")

    identifier_keys = _validate_registry_entry_list(
        issues,
        path,
        field_name="identifiers",
        entries=payload.get("identifiers"),
        required_string_fields=("semantic_id", "stability", "lifecycle", "description"),
    )
    temporal_keys = _validate_registry_entry_list(
        issues,
        path,
        field_name="temporal_semantics",
        entries=payload.get("temporal_semantics"),
        required_string_fields=("semantic_id", "category", "description"),
    )

    for field_name, keys in (("identifiers", identifier_keys), ("temporal_semantics", temporal_keys)):
        entries = payload.get(field_name, [])
        if not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            semantic_id = entry.get("semantic_id")
            if not isinstance(semantic_id, str) or not semantic_id.startswith("lotus."):
                _append_issue(issues, path, f"{field_name}[{index}].semantic_id must start with lotus.")

    trust_vocabularies = payload.get("trust_vocabularies")
    if not isinstance(trust_vocabularies, dict):
        _append_issue(issues, path, "trust_vocabularies must be an object")
    else:
        for field_name in (
            "freshness_classes",
            "completeness_statuses",
            "reconciliation_statuses",
            "data_quality_statuses",
        ):
            _validate_registry_entry_list(
                issues,
                path,
                field_name=f"trust_vocabularies.{field_name}",
                entries=trust_vocabularies.get(field_name),
                required_string_fields=("meaning",),
            )

    return issues


def validate_trust_metadata_registry(path: Path, payload: dict) -> list[str]:
    issues: list[str] = []

    if payload.get("contract_id") != "domain-data-product-trust-metadata":
        _append_issue(issues, path, "contract_id must be 'domain-data-product-trust-metadata'")
    if not isinstance(payload.get("contract_version"), str) or not SEMVER_PATTERN.fullmatch(
        payload["contract_version"]
    ):
        _append_issue(issues, path, "contract_version must be semver")
    if payload.get("governed_by_rfc") != "RFC-0084":
        _append_issue(issues, path, "governed_by_rfc must be 'RFC-0084'")
    if payload.get("domain") != "domain_data_product_trust":
        _append_issue(issues, path, "domain must be 'domain_data_product_trust'")
    if not isinstance(payload.get("description"), str) or not payload["description"].strip():
        _append_issue(issues, path, "description must be a non-empty string")

    evidence_access_classes = _validate_registry_entry_list(
        issues,
        path,
        field_name="evidence_access_classes",
        entries=payload.get("evidence_access_classes"),
        required_string_fields=("description",),
    )

    trust_metadata_fields = payload.get("trust_metadata_fields")
    trust_metadata_keys = _validate_registry_entry_list(
        issues,
        path,
        field_name="trust_metadata_fields",
        entries=trust_metadata_fields,
        required_string_fields=("semantic_id", "evidence_access_class", "description"),
    )
    if isinstance(trust_metadata_fields, list):
        for index, entry in enumerate(trust_metadata_fields):
            if not isinstance(entry, dict):
                continue
            semantic_id = entry.get("semantic_id")
            if not isinstance(semantic_id, str) or not semantic_id.startswith("lotus."):
                _append_issue(issues, path, f"trust_metadata_fields[{index}].semantic_id must start with lotus.")
            evidence_access_class = entry.get("evidence_access_class")
            if evidence_access_class not in evidence_access_classes:
                _append_issue(
                    issues,
                    path,
                    f"trust_metadata_fields[{index}].evidence_access_class must reference a registered evidence access class",
                )

    lineage_bundle_classes = payload.get("lineage_bundle_classes")
    if not _is_non_empty_list(lineage_bundle_classes):
        _append_issue(issues, path, "lineage_bundle_classes must be a non-empty array")
    else:
        seen_bundle_keys: set[str] = set()
        for index, entry in enumerate(lineage_bundle_classes):
            if not isinstance(entry, dict):
                _append_issue(issues, path, f"lineage_bundle_classes[{index}] must be an object")
                continue

            key = entry.get("key")
            if not isinstance(key, str) or not re.fullmatch(r"^[a-z][a-z0-9_]+$", key):
                _append_issue(issues, path, f"lineage_bundle_classes[{index}].key must be snake_case")
            elif key in seen_bundle_keys:
                _append_issue(issues, path, f"lineage_bundle_classes contains duplicate key {key}")
            else:
                seen_bundle_keys.add(key)

            description = entry.get("description")
            if not isinstance(description, str) or not description.strip():
                _append_issue(issues, path, f"lineage_bundle_classes[{index}].description must be a non-empty string")

            evidence_access_class = entry.get("evidence_access_class")
            if evidence_access_class not in evidence_access_classes:
                _append_issue(
                    issues,
                    path,
                    f"lineage_bundle_classes[{index}].evidence_access_class must reference a registered evidence access class",
                )

            required_fields = entry.get("required_fields")
            if not _is_non_empty_list(required_fields):
                _append_issue(issues, path, f"lineage_bundle_classes[{index}].required_fields must be a non-empty array")
            else:
                seen_required_fields: set[str] = set()
                for required_index, required_field in enumerate(required_fields):
                    if not isinstance(required_field, str) or not re.fullmatch(r"^[a-z][a-z0-9_]+$", required_field):
                        _append_issue(
                            issues,
                            path,
                            f"lineage_bundle_classes[{index}].required_fields[{required_index}] must be snake_case",
                        )
                        continue
                    if required_field in seen_required_fields:
                        _append_issue(
                            issues,
                            path,
                            f"lineage_bundle_classes[{index}].required_fields contains duplicate field {required_field}",
                        )
                    if required_field not in trust_metadata_keys:
                        _append_issue(
                            issues,
                            path,
                            f"lineage_bundle_classes[{index}].required_fields contains unknown trust metadata field {required_field}",
                        )
                    seen_required_fields.add(required_field)

    return issues


def _validate_product_identity(
    issues: list[str],
    path: Path,
    *,
    index: int,
    product: dict,
    producer_repository: str,
    seen_products: set[tuple[str, str]],
) -> None:
    product_name = product["product_name"]
    product_version = product["product_version"]
    if not isinstance(product_name, str) or not PRODUCT_NAME_PATTERN.fullmatch(product_name):
        _append_issue(issues, path, f"products[{index}].product_name must use stable product naming")
    if not isinstance(product_version, str) or not PRODUCT_VERSION_PATTERN.fullmatch(
        product_version
    ):
        _append_issue(
            issues,
            path,
            f"products[{index}].product_version must use vN or semantic versioning",
        )

    key = (str(product_name), str(product_version))
    if key in seen_products:
        _append_issue(
            issues,
            path,
            f"duplicate product declaration for {product_name} {product_version}",
        )
    else:
        seen_products.add(key)

    if product["owner_repository"] != producer_repository:
        _append_issue(
            issues,
            path,
            f"products[{index}].owner_repository must match producer_repository",
        )


def _validate_product_approved_consumers(
    issues: list[str],
    path: Path,
    *,
    index: int,
    product: dict,
) -> None:
    approved_consumers = product["approved_consumers"]
    if not _is_non_empty_list(approved_consumers):
        _append_issue(issues, path, f"products[{index}].approved_consumers must be non-empty")
        return

    invalid_consumers = [
        consumer
        for consumer in approved_consumers
        if not isinstance(consumer, str) or not REPOSITORY_PATTERN.fullmatch(consumer)
    ]
    if invalid_consumers:
        _append_issue(
            issues,
            path,
            f"products[{index}].approved_consumers contains invalid repo names",
        )
    if len(set(approved_consumers)) != len(approved_consumers):
        _append_issue(
            issues,
            path,
            f"products[{index}].approved_consumers must not contain duplicates",
        )


def _validate_product_registry_references(
    issues: list[str],
    path: Path,
    *,
    index: int,
    product: dict,
    identifier_keys: set[str] | None,
    temporal_keys: set[str] | None,
    freshness_classes: set[str] | None,
    completeness_statuses: set[str] | None,
    trust_metadata_keys: set[str] | None,
) -> None:
    if not _is_non_empty_list(product["required_trust_metadata"]):
        _append_issue(
            issues,
            path,
            f"products[{index}].required_trust_metadata must be non-empty",
        )
    elif trust_metadata_keys is not None:
        unknown_trust_metadata = [
            trust_metadata_field
            for trust_metadata_field in product["required_trust_metadata"]
            if trust_metadata_field not in trust_metadata_keys
        ]
        if unknown_trust_metadata:
            _append_issue(
                issues,
                path,
                f"products[{index}].required_trust_metadata contains unknown fields: {', '.join(unknown_trust_metadata)}",
            )
    if identifier_keys is not None:
        identifier_refs = product["identifier_refs"]
        if not _is_non_empty_list(identifier_refs):
            _append_issue(issues, path, f"products[{index}].identifier_refs must be non-empty")
        else:
            unknown_identifier_refs = [
                identifier_ref for identifier_ref in identifier_refs if identifier_ref not in identifier_keys
            ]
            if unknown_identifier_refs:
                _append_issue(
                    issues,
                    path,
                    f"products[{index}].identifier_refs contains unknown identifiers: {', '.join(unknown_identifier_refs)}",
                )
    if temporal_keys is not None and product["temporal_semantics_ref"] not in temporal_keys:
        _append_issue(
            issues,
            path,
            f"products[{index}].temporal_semantics_ref must reference a registered temporal semantic",
        )
    if freshness_classes is not None and product["freshness_policy"]["freshness_class"] not in freshness_classes:
        _append_issue(
            issues,
            path,
            f"products[{index}].freshness_policy.freshness_class must reference the trust vocabulary registry",
        )
    if (
        completeness_statuses is not None
        and product["completeness_policy"]["default_status"] not in completeness_statuses
    ):
        _append_issue(
            issues,
            path,
            f"products[{index}].completeness_policy.default_status must reference the trust vocabulary registry",
        )


def _validate_product_lineage_policy(
    issues: list[str],
    path: Path,
    *,
    index: int,
    product: dict,
    evidence_access_classes: set[str] | None,
    lineage_bundle_class_keys: set[str] | None,
) -> None:
    if (
        evidence_access_classes is not None
        and product["lineage_policy"]["evidence_access_class_ref"] not in evidence_access_classes
    ):
        _append_issue(
            issues,
            path,
            f"products[{index}].lineage_policy.evidence_access_class_ref must reference the trust metadata registry",
        )
    lineage_bundle_class_ref = product["lineage_policy"].get("lineage_bundle_class_ref")
    if product["lineage_policy"]["evidence_bundle_required"]:
        if not isinstance(lineage_bundle_class_ref, str):
            _append_issue(
                issues,
                path,
                f"products[{index}].lineage_policy.lineage_bundle_class_ref is required when evidence_bundle_required is true",
            )
        elif lineage_bundle_class_keys is not None and lineage_bundle_class_ref not in lineage_bundle_class_keys:
            _append_issue(
                issues,
                path,
                f"products[{index}].lineage_policy.lineage_bundle_class_ref must reference the trust metadata registry",
            )
    elif (
        lineage_bundle_class_ref is not None
        and lineage_bundle_class_keys is not None
        and lineage_bundle_class_ref not in lineage_bundle_class_keys
    ):
        _append_issue(
            issues,
            path,
            f"products[{index}].lineage_policy.lineage_bundle_class_ref must reference the trust metadata registry",
        )
    for optional_list_field in ("current_routes",):
        if optional_list_field in product and not _is_non_empty_list(product[optional_list_field]):
            _append_issue(
                issues,
                path,
                f"products[{index}].{optional_list_field} must be non-empty when present",
            )


def _validate_product_deprecation_policy(
    issues: list[str],
    path: Path,
    *,
    index: int,
    product: dict,
) -> None:
    deprecation_policy = product["deprecation_policy"]
    if not isinstance(deprecation_policy, dict):
        return

    state = deprecation_policy.get("state")
    successor = deprecation_policy.get("successor_product")
    if product["lifecycle_status"] == "deprecated" and state == "not_deprecated":
        _append_issue(
            issues,
            path,
            f"products[{index}] deprecated products must not use deprecation state not_deprecated",
        )
    if state in {"announced", "migration_required", "retired"} and successor is None:
        _append_issue(
            issues,
            path,
            f"products[{index}] deprecated states require successor_product or explicit retirement target",
        )


def validate_producer_contract(
    path: Path,
    payload: dict,
    *,
    identifier_keys: set[str] | None = None,
    temporal_keys: set[str] | None = None,
    freshness_classes: set[str] | None = None,
    completeness_statuses: set[str] | None = None,
    trust_metadata_keys: set[str] | None = None,
    evidence_access_classes: set[str] | None = None,
    lineage_bundle_class_keys: set[str] | None = None,
) -> list[str]:
    issues: list[str] = []

    if payload.get("contract_id") != "domain-data-products":
        _append_issue(issues, path, "contract_id must be 'domain-data-products'")
    if payload.get("governed_by_rfc") != "RFC-0084":
        _append_issue(issues, path, "governed_by_rfc must be 'RFC-0084'")

    producer_repository = payload.get("producer_repository")
    if not isinstance(producer_repository, str) or not REPOSITORY_PATTERN.fullmatch(
        producer_repository
    ):
        _append_issue(issues, path, "producer_repository must match lotus repo naming")

    contract_version = payload.get("contract_version")
    if not isinstance(contract_version, str) or not SEMVER_PATTERN.fullmatch(contract_version):
        _append_issue(issues, path, "contract_version must be semantic versioning")

    products = payload.get("products")
    if not _is_non_empty_list(products):
        _append_issue(issues, path, "products must be a non-empty array")
        return issues

    seen_products: set[tuple[str, str]] = set()
    for index, product in enumerate(products):
        if not isinstance(product, dict):
            _append_issue(issues, path, f"products[{index}] must be an object")
            continue

        missing = sorted(REQUIRED_PRODUCT_FIELDS - set(product))
        if missing:
            _append_issue(
                issues,
                path,
                f"products[{index}] missing required fields: {', '.join(missing)}",
            )
            continue

        _validate_product_identity(
            issues,
            path,
            index=index,
            product=product,
            producer_repository=producer_repository,
            seen_products=seen_products,
        )
        _validate_product_approved_consumers(issues, path, index=index, product=product)
        _validate_product_registry_references(
            issues,
            path,
            index=index,
            product=product,
            identifier_keys=identifier_keys,
            temporal_keys=temporal_keys,
            freshness_classes=freshness_classes,
            completeness_statuses=completeness_statuses,
            trust_metadata_keys=trust_metadata_keys,
        )
        _validate_product_lineage_policy(
            issues,
            path,
            index=index,
            product=product,
            evidence_access_classes=evidence_access_classes,
            lineage_bundle_class_keys=lineage_bundle_class_keys,
        )
        _validate_product_deprecation_policy(issues, path, index=index, product=product)

    return issues


def validate_consumer_contract(path: Path, payload: dict) -> list[str]:
    return validate_consumer_contract_with_context(path, payload)


def validate_consumer_contract_with_context(
    path: Path,
    payload: dict,
    *,
    trust_metadata_keys: set[str] | None = None,
) -> list[str]:
    issues: list[str] = []

    if payload.get("contract_id") != "domain-data-product-consumers":
        _append_issue(issues, path, "contract_id must be 'domain-data-product-consumers'")
    if payload.get("governed_by_rfc") != "RFC-0084":
        _append_issue(issues, path, "governed_by_rfc must be 'RFC-0084'")

    consumer_repository = payload.get("consumer_repository")
    if not isinstance(consumer_repository, str) or not REPOSITORY_PATTERN.fullmatch(
        consumer_repository
    ):
        _append_issue(issues, path, "consumer_repository must match lotus repo naming")

    contract_version = payload.get("contract_version")
    if not isinstance(contract_version, str) or not SEMVER_PATTERN.fullmatch(contract_version):
        _append_issue(issues, path, "contract_version must be semantic versioning")

    dependencies = payload.get("dependencies")
    if not _is_non_empty_list(dependencies):
        _append_issue(issues, path, "dependencies must be a non-empty array")
        return issues

    seen_dependencies: set[tuple[str, str, str]] = set()
    for index, dependency in enumerate(dependencies):
        if not isinstance(dependency, dict):
            _append_issue(issues, path, f"dependencies[{index}] must be an object")
            continue

        missing = sorted(REQUIRED_DEPENDENCY_FIELDS - set(dependency))
        if missing:
            _append_issue(
                issues,
                path,
                f"dependencies[{index}] missing required fields: {', '.join(missing)}",
            )
            continue

        product_name = dependency["product_name"]
        producer_repository = dependency["producer_repository"]
        required_version = dependency["required_product_version"]
        key = (str(product_name), str(producer_repository), str(required_version))
        if key in seen_dependencies:
            _append_issue(
                issues,
                path,
                f"duplicate dependency declaration for {product_name} from {producer_repository} {required_version}",
            )
        else:
            seen_dependencies.add(key)

        if producer_repository == consumer_repository:
            _append_issue(
                issues,
                path,
                f"dependencies[{index}] should not point a consumer to itself as upstream producer",
            )
        if not isinstance(product_name, str) or not PRODUCT_NAME_PATTERN.fullmatch(product_name):
            _append_issue(issues, path, f"dependencies[{index}].product_name must use stable product naming")
        if not isinstance(required_version, str) or not PRODUCT_VERSION_PATTERN.fullmatch(
            required_version
        ):
            _append_issue(
                issues,
                path,
                f"dependencies[{index}].required_product_version must use vN or semantic versioning",
            )
        if not _is_non_empty_list(dependency["validation_lanes"]):
            _append_issue(issues, path, f"dependencies[{index}].validation_lanes must be non-empty")
        if not _is_non_empty_list(dependency["required_trust_metadata"]):
            _append_issue(issues, path, f"dependencies[{index}].required_trust_metadata must be non-empty")
        elif trust_metadata_keys is not None:
            unknown_trust_metadata = [
                trust_metadata_field
                for trust_metadata_field in dependency["required_trust_metadata"]
                if trust_metadata_field not in trust_metadata_keys
            ]
            if unknown_trust_metadata:
                _append_issue(
                    issues,
                    path,
                    f"dependencies[{index}].required_trust_metadata contains unknown fields: {', '.join(unknown_trust_metadata)}",
                )

        migration_posture = dependency["migration_posture"]
        if not isinstance(migration_posture, dict):
            _append_issue(issues, path, f"dependencies[{index}].migration_posture must be an object")
            continue

        status = migration_posture.get("status")
        if status not in {"current", "approved_transition"}:
            _append_issue(
                issues,
                path,
                f"dependencies[{index}].migration_posture.status must be current or approved_transition",
            )
            continue

        target_product_version = migration_posture.get("target_product_version")
        if status == "current":
            if target_product_version is not None:
                _append_issue(
                    issues,
                    path,
                    f"dependencies[{index}].migration_posture.target_product_version must be null or omitted when status is current",
                )
        if status == "approved_transition":
            if not isinstance(target_product_version, str) or not PRODUCT_VERSION_PATTERN.fullmatch(target_product_version):
                _append_issue(
                    issues,
                    path,
                    f"dependencies[{index}].migration_posture.target_product_version must use vN or semantic versioning when status is approved_transition",
                )
            for required_field in ("justification", "sunset_condition"):
                value = migration_posture.get(required_field)
                if not isinstance(value, str) or not value.strip():
                    _append_issue(
                        issues,
                        path,
                        f"dependencies[{index}].migration_posture.{required_field} must be a non-empty string when status is approved_transition",
                    )

    return issues


def validate_cross_references(
    producer_payloads: list[tuple[Path, dict]],
    consumer_payloads: list[tuple[Path, dict]],
) -> list[str]:
    issues: list[str] = []
    product_index: dict[tuple[str, str, str], dict] = {}
    latest_product_version_index: dict[tuple[str, str], tuple[str, dict]] = {}

    for _, payload in producer_payloads:
        for product in payload.get("products", []):
            key = (
                product.get("product_name", ""),
                product.get("owner_repository", ""),
                product.get("product_version", ""),
            )
            product_index[key] = product
            if product.get("lifecycle_status") == "retired":
                continue
            latest_key = (
                product.get("product_name", ""),
                product.get("owner_repository", ""),
            )
            version = product.get("product_version", "")
            parsed_version = _parse_product_version(version) if isinstance(version, str) else None
            if parsed_version is None:
                continue
            current_latest = latest_product_version_index.get(latest_key)
            if current_latest is None:
                latest_product_version_index[latest_key] = (version, product)
                continue
            current_latest_version = current_latest[0]
            parsed_current_latest = _parse_product_version(current_latest_version)
            if parsed_current_latest is None or parsed_version > parsed_current_latest:
                latest_product_version_index[latest_key] = (version, product)

    for path, payload in consumer_payloads:
        for index, dependency in enumerate(payload.get("dependencies", [])):
            key = (
                dependency.get("product_name", ""),
                dependency.get("producer_repository", ""),
                dependency.get("required_product_version", ""),
            )
            upstream = product_index.get(key)
            if upstream is None:
                _append_issue(
                    issues,
                    path,
                    f"dependencies[{index}] references unknown product declaration {key[0]} from {key[1]} {key[2]}",
                )
                continue

            if payload.get("consumer_repository") not in upstream.get("approved_consumers", []):
                _append_issue(
                    issues,
                    path,
                    f"dependencies[{index}] consumer is not approved by upstream product declaration",
                )

            missing_trust_metadata = [
                field
                for field in dependency.get("required_trust_metadata", [])
                if field not in upstream.get("required_trust_metadata", [])
            ]
            if missing_trust_metadata:
                _append_issue(
                    issues,
                    path,
                    f"dependencies[{index}] upstream product declaration is missing required trust metadata: {', '.join(missing_trust_metadata)}",
                )

            latest_key = (
                dependency.get("product_name", ""),
                dependency.get("producer_repository", ""),
            )
            latest_product = latest_product_version_index.get(latest_key)
            migration_posture = dependency.get("migration_posture", {})
            if latest_product is None:
                continue

            latest_version = latest_product[0]
            required_version = dependency.get("required_product_version", "")
            migration_status = migration_posture.get("status")
            target_product_version = migration_posture.get("target_product_version")

            if required_version == latest_version:
                if migration_status == "approved_transition":
                    _append_issue(
                        issues,
                        path,
                        f"dependencies[{index}] migration_posture approved_transition is unnecessary because required_product_version already matches the latest declared version",
                    )
                continue

            if migration_status != "approved_transition" or target_product_version != latest_version:
                _append_issue(
                    issues,
                    path,
                    f"dependencies[{index}] version drift requires approved_transition migration posture to latest version {latest_version}",
                )

    return issues


def validate_contract_directory(directory: Path) -> list[str]:
    issues: list[str] = []
    semantics_registry_path = _find_semantics_registry_path(directory)
    trust_metadata_registry_path = _find_trust_metadata_registry_path(directory)
    producer_paths = sorted(directory.rglob(PRODUCT_GLOB))
    consumer_paths = sorted(directory.rglob(CONSUMER_GLOB))

    producer_payloads: list[tuple[Path, dict]] = []
    consumer_payloads: list[tuple[Path, dict]] = []
    identifier_keys: set[str] | None = None
    temporal_keys: set[str] | None = None
    freshness_classes: set[str] | None = None
    completeness_statuses: set[str] | None = None
    trust_metadata_keys: set[str] | None = None
    evidence_access_classes: set[str] | None = None
    lineage_bundle_class_keys: set[str] | None = None

    if producer_paths and not semantics_registry_path.exists():
        _append_issue(
            issues,
            semantics_registry_path,
            "semantics registry is required when validating domain data product declarations",
        )
    elif semantics_registry_path.exists():
        semantics_payload = _load_json(semantics_registry_path)
        issues.extend(validate_semantics_registry(semantics_registry_path, semantics_payload))
        identifier_keys = {
            identifier.get("key", "")
            for identifier in semantics_payload.get("identifiers", [])
            if isinstance(identifier, dict)
        }
        temporal_keys = {
            semantic.get("key", "")
            for semantic in semantics_payload.get("temporal_semantics", [])
            if isinstance(semantic, dict)
        }
        freshness_classes = {
            entry.get("key", "")
            for entry in semantics_payload.get("trust_vocabularies", {}).get("freshness_classes", [])
            if isinstance(entry, dict)
        }
        completeness_statuses = {
            entry.get("key", "")
            for entry in semantics_payload.get("trust_vocabularies", {}).get("completeness_statuses", [])
            if isinstance(entry, dict)
        }

    if producer_paths and not trust_metadata_registry_path.exists():
        _append_issue(
            issues,
            trust_metadata_registry_path,
            "trust metadata registry is required when validating domain data product declarations",
        )
    elif trust_metadata_registry_path.exists():
        trust_metadata_payload = _load_json(trust_metadata_registry_path)
        issues.extend(validate_trust_metadata_registry(trust_metadata_registry_path, trust_metadata_payload))
        trust_metadata_keys = {
            entry.get("key", "")
            for entry in trust_metadata_payload.get("trust_metadata_fields", [])
            if isinstance(entry, dict)
        }
        evidence_access_classes = {
            entry.get("key", "")
            for entry in trust_metadata_payload.get("evidence_access_classes", [])
            if isinstance(entry, dict)
        }
        lineage_bundle_class_keys = {
            entry.get("key", "")
            for entry in trust_metadata_payload.get("lineage_bundle_classes", [])
            if isinstance(entry, dict)
        }

    for path in producer_paths:
        payload = _load_json(path)
        producer_payloads.append((path, payload))
        issues.extend(
            validate_producer_contract(
                path,
                payload,
                identifier_keys=identifier_keys,
                temporal_keys=temporal_keys,
                freshness_classes=freshness_classes,
                completeness_statuses=completeness_statuses,
                trust_metadata_keys=trust_metadata_keys,
                evidence_access_classes=evidence_access_classes,
                lineage_bundle_class_keys=lineage_bundle_class_keys,
            )
        )

    for path in consumer_paths:
        payload = _load_json(path)
        consumer_payloads.append((path, payload))
        issues.extend(
            validate_consumer_contract_with_context(
                path,
                payload,
                trust_metadata_keys=trust_metadata_keys,
            )
        )

    issues.extend(validate_cross_references(producer_payloads, consumer_payloads))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Lotus domain-data-product producer and consumer declaration files."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=Path(__file__).resolve().parent,
        type=Path,
        help="Directory to scan for *-products.v1.json and *-consumers.v1.json files.",
    )
    args = parser.parse_args(argv)

    directory = args.directory.resolve()
    producer_paths = sorted(directory.rglob(PRODUCT_GLOB))
    consumer_paths = sorted(directory.rglob(CONSUMER_GLOB))

    if not producer_paths and not consumer_paths:
        print(f"No domain-data-product declaration files found in {directory}")
        return 0

    issues = validate_contract_directory(directory)
    if issues:
        for issue in issues:
            print(issue)
        return 1

    print(
        f"Validated {len(producer_paths)} producer declarations and {len(consumer_paths)} consumer declarations in {directory}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
