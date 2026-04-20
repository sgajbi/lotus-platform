from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Literal

from domain_product_discovery import DEFAULT_CATALOG_PATH, load_catalog
from validate_trust_telemetry import _iter_telemetry_paths


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SLO_POLICY_DIRECTORY = ROOT / "platform-contracts" / "mesh-slo"
SLO_POLICY_GLOB = "*.slo.v1.json"
REQUIRED_PRODUCTS = {
    "lotus-core:PortfolioStateSnapshot:v1": "lotus-core",
    "lotus-performance:ReturnsSeriesBundle:v1": "lotus-performance",
    "lotus-risk:RiskMetricsReport:v1": "lotus-risk",
    "lotus-advise:AdvisoryProposalLifecycleRecord:v1": "lotus-advise",
    "lotus-report:ClientReportEvidencePack:v1": "lotus-report",
    "lotus-manage:PortfolioActionRegister:v1": "lotus-manage",
}
ViolationSeverity = Literal["blocking", "advisory"]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _catalog_by_id(catalog_path: Path) -> dict[str, dict[str, Any]]:
    catalog = load_catalog(catalog_path)
    return {product["product_id"]: product for product in catalog.get("products", [])}


def _iter_policy_paths(policy_path: Path) -> list[Path]:
    if policy_path.is_file():
        return [policy_path]
    return sorted(policy_path.rglob(SLO_POLICY_GLOB))


def _severity(policy_section: dict[str, Any]) -> ViolationSeverity:
    return "blocking" if policy_section.get("violation_severity") == "blocking" else "advisory"


def load_mesh_slo_policies(policy_path: Path = DEFAULT_SLO_POLICY_DIRECTORY) -> dict[str, tuple[Path, dict[str, Any]]]:
    policies: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in _iter_policy_paths(policy_path):
        payload = _load_json(path)
        product_id = payload.get("product_id")
        if isinstance(product_id, str):
            policies[product_id] = (path, payload)
    return policies


def validate_mesh_slo_policies(
    policy_path: Path = DEFAULT_SLO_POLICY_DIRECTORY,
    *,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    required_products: dict[str, str] = REQUIRED_PRODUCTS,
) -> list[str]:
    products_by_id = _catalog_by_id(catalog_path)
    issues: list[str] = []
    paths = _iter_policy_paths(policy_path)
    if not paths:
        return [f"{policy_path}: no mesh SLO policy files found"]

    seen_product_ids: set[str] = set()
    for path in paths:
        try:
            payload = _load_json(path)
        except json.JSONDecodeError as exc:
            issues.append(f"{path}: invalid JSON: {exc}")
            continue

        product_id = payload.get("product_id")
        if not isinstance(product_id, str) or not product_id:
            issues.append(f"{path}: product_id must be a non-empty string")
            continue
        if product_id in seen_product_ids:
            issues.append(f"{path}: duplicate SLO policy for {product_id}")
        seen_product_ids.add(product_id)

        product = products_by_id.get(product_id)
        if product is None:
            issues.append(f"{path}: product_id does not exist in catalog: {product_id}")
            continue

        expected_repository = product["producer_repository"]
        if payload.get("contract_id") != "lotus-mesh-slo-policy":
            issues.append(f"{path}: contract_id must be lotus-mesh-slo-policy")
        if "RFC-0091" not in payload.get("governed_by_rfcs", []):
            issues.append(f"{path}: governed_by_rfcs must include RFC-0091")
        if payload.get("producer_repository") != expected_repository:
            issues.append(
                f"{path}: producer_repository must match catalog identity {expected_repository}"
            )

        freshness = payload.get("freshness", {})
        if not isinstance(freshness, dict) or not isinstance(
            freshness.get("max_allowed_age_seconds"), int
        ) or freshness.get("max_allowed_age_seconds") < 1:
            issues.append(f"{path}: freshness.max_allowed_age_seconds must be >= 1")

        for section_name, field_name in (
            ("completeness", "required_status"),
            ("reconciliation", "required_status"),
            ("data_quality", "required_status"),
        ):
            section = payload.get(section_name, {})
            if not isinstance(section, dict) or not isinstance(section.get(field_name), str):
                issues.append(f"{path}: {section_name}.{field_name} must be a string")
            if section.get("violation_severity") not in {"blocking", "advisory"}:
                issues.append(
                    f"{path}: {section_name}.violation_severity must be blocking or advisory"
                )

        lineage = payload.get("lineage", {})
        if not isinstance(lineage, dict) or not isinstance(
            lineage.get("lineage_materialized_required"), bool
        ):
            issues.append(
                f"{path}: lineage.lineage_materialized_required must be boolean"
            )
        if lineage.get("violation_severity") not in {"blocking", "advisory"}:
            issues.append(
                f"{path}: lineage.violation_severity must be blocking or advisory"
            )

        escalation = payload.get("escalation", {})
        if not isinstance(escalation, dict) or not escalation.get("owner_repository"):
            issues.append(f"{path}: escalation.owner_repository is required")
        if isinstance(escalation, dict) and escalation.get("owner_repository") != expected_repository:
            issues.append(
                f"{path}: escalation.owner_repository must match {expected_repository}"
            )
        if not isinstance(escalation, dict) or not escalation.get("remediation"):
            issues.append(f"{path}: escalation.remediation is required")

    for product_id, repository in required_products.items():
        if product_id not in seen_product_ids:
            issues.append(
                f"{policy_path}: missing required mesh SLO policy for {repository} product {product_id}"
            )
    return issues


def evaluate_mesh_slo_violations(
    *,
    telemetry_payloads: dict[str, tuple[Path, dict[str, Any]]],
    policies: dict[str, tuple[Path, dict[str, Any]]] | None = None,
    policy_path: Path = DEFAULT_SLO_POLICY_DIRECTORY,
) -> list[dict[str, Any]]:
    policies = policies or load_mesh_slo_policies(policy_path)
    violations: list[dict[str, Any]] = []

    for product_id, (telemetry_path, telemetry) in telemetry_payloads.items():
        policy_entry = policies.get(product_id)
        if policy_entry is None:
            continue
        policy_path_for_product, policy = policy_entry
        producer_repository = str(policy.get("producer_repository"))
        escalation = policy.get("escalation", {})

        freshness = telemetry.get("freshness", {})
        freshness_policy = policy.get("freshness", {})
        age_seconds = freshness.get("age_seconds") if isinstance(freshness, dict) else None
        max_allowed_age_seconds = freshness_policy.get("max_allowed_age_seconds")
        if isinstance(age_seconds, int) and isinstance(max_allowed_age_seconds, int):
            if age_seconds > max_allowed_age_seconds:
                violations.append(
                    _violation(
                        code="mesh_slo_freshness_violation",
                        product_id=product_id,
                        producer_repository=producer_repository,
                        severity=_severity(freshness_policy),
                        detail=(
                            f"Telemetry age {age_seconds}s exceeds SLO "
                            f"{max_allowed_age_seconds}s."
                        ),
                        telemetry_path=telemetry_path,
                        policy_path=policy_path_for_product,
                        escalation=escalation,
                    )
                )

        _append_status_violation(
            violations,
            telemetry=telemetry,
            telemetry_path=telemetry_path,
            policy=policy,
            policy_path=policy_path_for_product,
            product_id=product_id,
            producer_repository=producer_repository,
            section_name="completeness",
            telemetry_field="completeness_status",
            code="mesh_slo_completeness_violation",
            escalation=escalation,
        )
        _append_status_violation(
            violations,
            telemetry=telemetry,
            telemetry_path=telemetry_path,
            policy=policy,
            policy_path=policy_path_for_product,
            product_id=product_id,
            producer_repository=producer_repository,
            section_name="reconciliation",
            telemetry_field="reconciliation_status",
            code="mesh_slo_reconciliation_violation",
            escalation=escalation,
        )
        _append_status_violation(
            violations,
            telemetry=telemetry,
            telemetry_path=telemetry_path,
            policy=policy,
            policy_path=policy_path_for_product,
            product_id=product_id,
            producer_repository=producer_repository,
            section_name="data_quality",
            telemetry_field="data_quality_status",
            code="mesh_slo_data_quality_violation",
            escalation=escalation,
        )

        lineage_policy = policy.get("lineage", {})
        lineage = telemetry.get("lineage", {})
        if (
            isinstance(lineage_policy, dict)
            and lineage_policy.get("lineage_materialized_required") is True
            and isinstance(lineage, dict)
            and lineage.get("lineage_materialized") is not True
        ):
            violations.append(
                _violation(
                    code="mesh_slo_lineage_violation",
                    product_id=product_id,
                    producer_repository=producer_repository,
                    severity=_severity(lineage_policy),
                    detail="Lineage is not materialized but the SLO requires it.",
                    telemetry_path=telemetry_path,
                    policy_path=policy_path_for_product,
                    escalation=escalation,
                )
            )
    return violations


def _append_status_violation(
    violations: list[dict[str, Any]],
    *,
    telemetry: dict[str, Any],
    telemetry_path: Path,
    policy: dict[str, Any],
    policy_path: Path,
    product_id: str,
    producer_repository: str,
    section_name: str,
    telemetry_field: str,
    code: str,
    escalation: dict[str, Any],
) -> None:
    section = policy.get(section_name, {})
    required_status = section.get("required_status") if isinstance(section, dict) else None
    observed_status = telemetry.get(telemetry_field)
    if isinstance(required_status, str) and observed_status != required_status:
        violations.append(
            _violation(
                code=code,
                product_id=product_id,
                producer_repository=producer_repository,
                severity=_severity(section),
                detail=(
                    f"{telemetry_field} is {observed_status}; SLO requires "
                    f"{required_status}."
                ),
                telemetry_path=telemetry_path,
                policy_path=policy_path,
                escalation=escalation,
            )
        )


def _violation(
    *,
    code: str,
    product_id: str,
    producer_repository: str,
    severity: ViolationSeverity,
    detail: str,
    telemetry_path: Path,
    policy_path: Path,
    escalation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "product_id": product_id,
        "producer_repository": producer_repository,
        "detail": detail,
        "telemetry_path": telemetry_path.as_posix(),
        "policy_path": policy_path.as_posix(),
        "remediation": str(escalation.get("remediation", detail)),
    }


def _load_telemetry_payloads(telemetry_path: Path) -> dict[str, tuple[Path, dict[str, Any]]]:
    payloads: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in _iter_telemetry_paths(telemetry_path):
        payload = _load_json(path)
        product_id = payload.get("product_id")
        if isinstance(product_id, str):
            payloads[product_id] = (path, payload)
    return payloads


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and evaluate RFC-0091 mesh SLO policies."
    )
    parser.add_argument("--policy-path", type=Path, default=DEFAULT_SLO_POLICY_DIRECTORY)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--telemetry-path", type=Path, default=None)
    args = parser.parse_args(argv)

    issues = validate_mesh_slo_policies(args.policy_path, catalog_path=args.catalog)
    if args.telemetry_path is not None:
        violations = evaluate_mesh_slo_violations(
            telemetry_payloads=_load_telemetry_payloads(args.telemetry_path),
            policy_path=args.policy_path,
        )
        issues.extend(
            f"{violation['telemetry_path']}: {violation['code']}: {violation['detail']}"
            for violation in violations
        )

    if issues:
        for issue in issues:
            print(issue)
        return 1
    print("Mesh SLO policies validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
