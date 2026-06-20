from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from domain_product_discovery import DEFAULT_CATALOG_PATH, load_catalog
from mesh_maturity_scope import REQUIRED_PRODUCTS


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACCESS_POLICY_DIRECTORY = ROOT / "platform-contracts" / "mesh-access"
ACCESS_POLICY_GLOB = "*.access.v1.json"
VALID_DEFAULT_POSTURES = {"restricted", "internal", "public"}
VALID_CUSTOMER_STATES = {"usable", "requestable", "restricted", "blocked"}
VALID_OPERATOR_STATES = {
    "usable",
    "requestable",
    "restricted_with_reason",
    "blocked_with_reason",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _catalog_by_id(catalog_path: Path) -> dict[str, dict[str, Any]]:
    catalog = load_catalog(catalog_path)
    return {product["product_id"]: product for product in catalog.get("products", [])}


def _iter_policy_paths(policy_path: Path) -> list[Path]:
    if policy_path.is_file():
        return [policy_path]
    return sorted(policy_path.rglob(ACCESS_POLICY_GLOB))


def load_mesh_access_policies(
    policy_path: Path = DEFAULT_ACCESS_POLICY_DIRECTORY,
) -> dict[str, tuple[Path, dict[str, Any]]]:
    policies: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in _iter_policy_paths(policy_path):
        payload = _load_json(path)
        product_id = payload.get("product_id")
        if isinstance(product_id, str):
            policies[product_id] = (path, payload)
    return policies


def _validate_mesh_access_product_id(
    *,
    path: Path,
    payload: dict[str, Any],
    products_by_id: dict[str, dict[str, Any]],
    seen_product_ids: set[str],
    issues: list[str],
) -> tuple[str | None, dict[str, Any] | None]:
    product_id = payload.get("product_id")
    if not isinstance(product_id, str) or not product_id:
        issues.append(f"{path}: product_id must be a non-empty string")
        return None, None
    if product_id in seen_product_ids:
        issues.append(f"{path}: duplicate access policy for {product_id}")
    seen_product_ids.add(product_id)

    product = products_by_id.get(product_id)
    if product is None:
        issues.append(f"{path}: product_id does not exist in catalog: {product_id}")
        return product_id, None
    return product_id, product


def _validate_mesh_access_contract_identity(
    *,
    path: Path,
    payload: dict[str, Any],
    expected_repository: str,
    issues: list[str],
) -> None:
    if payload.get("contract_id") != "lotus-mesh-access-policy":
        issues.append(f"{path}: contract_id must be lotus-mesh-access-policy")
    if "RFC-0091" not in payload.get("governed_by_rfcs", []):
        issues.append(f"{path}: governed_by_rfcs must include RFC-0091")
    if payload.get("producer_repository") != expected_repository:
        issues.append(
            f"{path}: producer_repository must match catalog identity {expected_repository}"
        )
    if payload.get("default_posture") not in VALID_DEFAULT_POSTURES:
        issues.append(f"{path}: default_posture must be governed")


def _validate_allowed_consumers(
    *,
    path: Path,
    payload: dict[str, Any],
    product: dict[str, Any],
    issues: list[str],
) -> None:
    allowed_consumers = payload.get("allowed_consumers")
    if not isinstance(allowed_consumers, list) or not allowed_consumers:
        issues.append(f"{path}: allowed_consumers must be a non-empty array")
        return
    approved_consumers = product.get("approved_consumers", [])
    for index, consumer in enumerate(allowed_consumers):
        _validate_allowed_consumer(
            issues,
            path,
            index,
            consumer,
            approved_consumers=approved_consumers,
        )


def _validate_denial_posture(
    *, path: Path, payload: dict[str, Any], issues: list[str]
) -> None:
    denial_posture = payload.get("denial_posture", {})
    if not isinstance(denial_posture, dict):
        issues.append(f"{path}: denial_posture must be an object")
        return
    if denial_posture.get("customer_visible_state") not in VALID_CUSTOMER_STATES:
        issues.append(
            f"{path}: denial_posture.customer_visible_state must be governed"
        )
    if denial_posture.get("operator_visible_state") not in VALID_OPERATOR_STATES:
        issues.append(
            f"{path}: denial_posture.operator_visible_state must be governed"
        )
    if not denial_posture.get("reason"):
        issues.append(f"{path}: denial_posture.reason is required")


def _validate_access_audit(
    *,
    path: Path,
    payload: dict[str, Any],
    expected_repository: str,
    issues: list[str],
) -> None:
    audit = payload.get("audit", {})
    if not isinstance(audit, dict):
        issues.append(f"{path}: audit must be an object")
        return
    if audit.get("owner_repository") != expected_repository:
        issues.append(f"{path}: audit.owner_repository must match producer")
    if not audit.get("policy_owner"):
        issues.append(f"{path}: audit.policy_owner is required")
    if not audit.get("decision_evidence"):
        issues.append(f"{path}: audit.decision_evidence is required")


def _validate_mesh_access_policy_payload(
    *,
    path: Path,
    payload: dict[str, Any],
    products_by_id: dict[str, dict[str, Any]],
    seen_product_ids: set[str],
    issues: list[str],
) -> None:
    _, product = _validate_mesh_access_product_id(
        path=path,
        payload=payload,
        products_by_id=products_by_id,
        seen_product_ids=seen_product_ids,
        issues=issues,
    )
    if product is None:
        return

    expected_repository = product["producer_repository"]
    _validate_mesh_access_contract_identity(
        path=path,
        payload=payload,
        expected_repository=expected_repository,
        issues=issues,
    )
    _validate_allowed_consumers(
        path=path,
        payload=payload,
        product=product,
        issues=issues,
    )
    _validate_denial_posture(path=path, payload=payload, issues=issues)
    _validate_access_audit(
        path=path,
        payload=payload,
        expected_repository=expected_repository,
        issues=issues,
    )


def validate_mesh_access_policies(
    policy_path: Path = DEFAULT_ACCESS_POLICY_DIRECTORY,
    *,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    required_products: dict[str, str] = REQUIRED_PRODUCTS,
) -> list[str]:
    products_by_id = _catalog_by_id(catalog_path)
    issues: list[str] = []
    paths = _iter_policy_paths(policy_path)
    if not paths:
        return [f"{policy_path}: no mesh access policy files found"]

    seen_product_ids: set[str] = set()
    for path in paths:
        try:
            payload = _load_json(path)
        except json.JSONDecodeError as exc:
            issues.append(f"{path}: invalid JSON: {exc}")
            continue

        _validate_mesh_access_policy_payload(
            path=path,
            payload=payload,
            products_by_id=products_by_id,
            seen_product_ids=seen_product_ids,
            issues=issues,
        )

    for product_id, repository in required_products.items():
        if product_id not in seen_product_ids:
            issues.append(
                f"{policy_path}: missing required mesh access policy for {repository} product {product_id}"
            )
    return issues


def _validate_allowed_consumer(
    issues: list[str],
    path: Path,
    index: int,
    consumer: object,
    *,
    approved_consumers: object,
) -> None:
    prefix = f"allowed_consumers[{index}]"
    if not isinstance(consumer, dict):
        issues.append(f"{path}: {prefix} must be an object")
        return
    consumer_repository = consumer.get("consumer_repository")
    if not isinstance(consumer_repository, str) or not consumer_repository:
        issues.append(f"{path}: {prefix}.consumer_repository must be a non-empty string")
    elif not _is_allowed_consumer_repository(
        consumer_repository=consumer_repository,
        approved_consumers=approved_consumers,
    ):
        issues.append(
            f"{path}: {prefix}.consumer_repository must be lotus-gateway or approved by the product catalog"
        )
    for field_name in ("tenant_scope", "roles", "use_cases"):
        if not _is_non_empty_string_list(consumer.get(field_name)):
            issues.append(f"{path}: {prefix}.{field_name} must be non-empty strings")


def _is_allowed_consumer_repository(
    *, consumer_repository: str, approved_consumers: object
) -> bool:
    if consumer_repository == "lotus-gateway":
        return True
    return (
        isinstance(approved_consumers, list)
        and consumer_repository in approved_consumers
    )


def _is_non_empty_string_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item for item in value)
    )


def access_posture_for_context(
    *,
    policy: dict[str, Any],
    consumer_repository: str,
    tenant_id: str,
    role: str,
    use_case: str,
) -> dict[str, Any]:
    for consumer in policy.get("allowed_consumers", []):
        if not isinstance(consumer, dict):
            continue
        if consumer.get("consumer_repository") != consumer_repository:
            continue
        if tenant_id not in consumer.get("tenant_scope", []):
            continue
        if role not in consumer.get("roles", []):
            continue
        if use_case not in consumer.get("use_cases", []):
            continue
        return {
            "access_state": "usable",
            "customer_visible_state": "usable",
            "operator_visible_state": "usable",
            "reason": "Access allowed by mesh access policy.",
        }

    denial = policy.get("denial_posture", {})
    return {
        "access_state": "restricted",
        "customer_visible_state": denial.get("customer_visible_state", "restricted"),
        "operator_visible_state": denial.get(
            "operator_visible_state", "restricted_with_reason"
        ),
        "reason": denial.get("reason", "Access is restricted by mesh access policy."),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate RFC-0091 mesh access policies."
    )
    parser.add_argument(
        "--policy-path", type=Path, default=DEFAULT_ACCESS_POLICY_DIRECTORY
    )
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_PATH)
    args = parser.parse_args(argv)

    issues = validate_mesh_access_policies(args.policy_path, catalog_path=args.catalog)
    if issues:
        for issue in issues:
            print(issue)
        return 1
    print("Mesh access policies validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
