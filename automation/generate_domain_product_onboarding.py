from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "output" / "domain-product-onboarding"
PRODUCT_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9]+$")
REPOSITORY_PATTERN = re.compile(r"^lotus-[a-z0-9-]+$")
PRODUCT_VERSION_PATTERN = re.compile(r"^(v[0-9]+|[0-9]+\.[0-9]+\.[0-9]+)$")


def _product_id(repository: str, product_name: str, product_version: str) -> str:
    return f"{repository}:{product_name}:{product_version}"


def _kebab(value: str) -> str:
    tokens = re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z]|$)", value)
    return "-".join(token.lower() for token in tokens if token)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _product_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
    authoritative_domain: str,
    product_family: str,
) -> dict[str, Any]:
    return {
        "contract_id": "domain-data-products",
        "contract_version": "1.0.0",
        "governed_by_rfc": "RFC-0084",
        "producer_repository": repository,
        "authoritative_domain": authoritative_domain,
        "products": [
            {
                "product_name": product_name,
                "product_version": product_version,
                "owner_repository": repository,
                "product_family": product_family,
                "authoritative_domain": authoritative_domain,
                "lifecycle_status": "preview",
                "request_scope": {
                    "scope_level": "portfolio",
                    "supports_bulk": False,
                },
                "temporal_scope": {
                    "primary_time_field": "as_of_date",
                    "freshness_basis": "as_of_date",
                    "supports_restatement": True,
                },
                "temporal_semantics_ref": "as_of_date",
                "identifier_refs": ["portfolio_id", "tenant_id", "correlation_id"],
                "required_trust_metadata": [
                    "product_name",
                    "product_version",
                    "tenant_id",
                    "generated_at",
                    "as_of_date",
                    "reconciliation_status",
                    "data_quality_status",
                    "correlation_id",
                ],
                "serving_plane": "replace_with_service_or_query_plane",
                "current_routes": ["replace_with_gateway_or_domain_route"],
                "freshness_policy": {
                    "freshness_class": "daily",
                    "max_allowed_age_description": "Replace with product-specific freshness policy.",
                },
                "completeness_policy": {
                    "default_status": "complete",
                    "partial_allowed": False,
                },
                "lineage_policy": {
                    "lineage_required": True,
                    "evidence_bundle_required": True,
                    "evidence_access_class_ref": "customer_consumable",
                },
                "security_profile_ref": "business_consumer_access:client_confidential:retain_for_client_record:audit_read_and_export",
                "approved_consumers": ["lotus-gateway"],
                "deprecation_policy": {
                    "state": "not_deprecated",
                    "successor_product": None,
                },
            }
        ],
    }


def _telemetry_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
) -> dict[str, Any]:
    product_id = _product_id(repository, product_name, product_version)
    return {
        "contract_id": "lotus-domain-product-trust-telemetry-snapshot",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0087", "RFC-0091"],
        "emitted_at_utc": "replace_with_runtime_utc_timestamp",
        "product_id": product_id,
        "producer_repository": repository,
        "product_name": product_name,
        "product_version": product_version,
        "source_repository": repository,
        "runtime_source": {
            "emission_mode": "deterministic_local_or_service_runtime",
            "service_version": "replace_with_service_version",
            "environment": "local",
        },
        "freshness": {
            "freshness_class": "daily",
            "freshness_state": "current",
            "evaluated_at_utc": "replace_with_runtime_utc_timestamp",
            "observed_at_utc": "replace_with_runtime_utc_timestamp",
            "age_seconds": 0,
            "max_allowed_age_seconds": 86400,
        },
        "completeness_status": "complete",
        "reconciliation_status": "reconciled",
        "data_quality_status": "quality_passed",
        "lineage": {
            "lineage_materialized": True,
            "lineage_bundle_id": f"lineage:{repository}:{_kebab(product_name)}:replace",
            "evidence_access_class": "customer_consumable",
            "evidence_uris": [f"{repository}://evidence/{_kebab(product_name)}/replace"],
        },
        "blocking": {"blocked": False},
        "observed_trust_metadata": {
            "product_name": product_name,
            "product_version": product_version,
            "tenant_id": "replace_with_tenant_id",
            "generated_at": "replace_with_runtime_utc_timestamp",
            "as_of_date": "replace_with_as_of_date",
            "reconciliation_status": "reconciled",
            "data_quality_status": "quality_passed",
            "correlation_id": f"replace_with_correlation_id:{product_id}",
        },
        "evidence": {
            "correlation_id": f"replace_with_correlation_id:{product_id}",
            "validation_lanes": ["feature", "pr-merge"],
            "source_event_id": f"source-event:{repository}:{_kebab(product_name)}:replace",
            "source_artifact_uri": f"{repository}://contracts/trust-telemetry/{_kebab(product_name)}.telemetry.v1.json",
        },
    }


def _slo_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
) -> dict[str, Any]:
    return {
        "contract_id": "lotus-mesh-slo-policy",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0091"],
        "product_id": _product_id(repository, product_name, product_version),
        "producer_repository": repository,
        "freshness": {
            "max_allowed_age_seconds": 86400,
            "violation_severity": "blocking",
        },
        "completeness": {"required_status": "complete", "violation_severity": "blocking"},
        "reconciliation": {
            "required_status": "reconciled",
            "violation_severity": "blocking",
        },
        "data_quality": {
            "required_status": "quality_passed",
            "violation_severity": "blocking",
        },
        "lineage": {
            "lineage_materialized_required": True,
            "violation_severity": "blocking",
        },
        "certification": {
            "max_certification_age_seconds": 86400,
            "violation_severity": "blocking",
        },
        "escalation": {
            "owner_repository": repository,
            "owner_role": "replace_with_domain_owner",
            "remediation": "Refresh runtime evidence or block publication until trust posture is restored.",
        },
    }


def _access_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
) -> dict[str, Any]:
    return {
        "contract_id": "lotus-mesh-access-policy",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0091"],
        "product_id": _product_id(repository, product_name, product_version),
        "producer_repository": repository,
        "default_posture": "restricted",
        "allowed_consumers": [
            {
                "consumer_repository": "lotus-gateway",
                "tenant_scope": ["replace_with_tenant_or_all"],
                "roles": ["operator", "advisor"],
                "use_cases": ["discovery", "evidence_review"],
            }
        ],
        "denial_posture": {
            "customer_visible_state": "requestable",
            "operator_visible_state": "restricted_with_reason",
            "reason": "Access policy requires explicit tenant, role, consumer, and use-case approval.",
        },
    }


def _evidence_payload(
    *,
    repository: str,
    product_name: str,
    product_version: str,
) -> dict[str, Any]:
    return {
        "contract_id": "lotus-mesh-evidence-pack-policy",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0091"],
        "product_id": _product_id(repository, product_name, product_version),
        "producer_repository": repository,
        "field_access_classes": {
            "product_identity": "public_customer",
            "runtime_telemetry": "restricted_customer",
            "lineage_evidence": "restricted_customer",
            "operator_remediation": "operator_only",
            "internal_debug": "internal_only",
        },
        "required_manifest_sections": [
            "product_identity",
            "source_declaration",
            "runtime_telemetry",
            "slo_posture",
            "access_posture",
            "dependency_graph",
            "certification_state",
            "validation_lanes",
        ],
    }


def _readme(
    *,
    repository: str,
    product_name: str,
    product_version: str,
    authoritative_domain: str,
    product_family: str,
) -> str:
    product_id = _product_id(repository, product_name, product_version)
    return "\n".join(
        [
            f"# Domain Product Onboarding Bundle - {product_id}",
            "",
            "This bundle is a scaffold for repo-native Lotus data-product onboarding.",
            "It is not product authority until the owning repository replaces placeholders,",
            "adds repo-native tests, emits runtime telemetry, and passes platform certification.",
            "",
            "## Product Identity",
            "",
            f"- Repository: `{repository}`",
            f"- Product: `{product_name}`",
            f"- Version: `{product_version}`",
            f"- Product ID: `{product_id}`",
            f"- Authoritative domain: `{authoritative_domain}`",
            f"- Product family: `{product_family}`",
            "",
            "## Ownership Rules",
            "",
            "- Keep source truth in the producer repository.",
            "- Keep generated catalog, graph, trust, and evidence artifacts derived.",
            "- Publish through `lotus-gateway`; do not make gateway the product registry.",
            "- Expose customer/operator discovery through Workbench only after gateway support exists.",
            "- Treat placeholders as blockers before production certification.",
            "",
        ]
    )


def _checklist(
    *,
    repository: str,
    product_name: str,
    product_version: str,
    written_paths: list[Path],
    output_directory: Path,
) -> str:
    product_id = _product_id(repository, product_name, product_version)
    lines = [
        f"# Domain Product Onboarding Checklist - {product_id}",
        "",
        "This checklist is generated by `automation/generate_domain_product_onboarding.py`.",
        "",
        "## Generated Files",
        "",
    ]
    for path in written_paths:
        lines.append(f"- `{_relative(path, output_directory)}`")

    lines.extend(
        [
            "",
            "## Required Implementation Slices",
            "",
            "- Producer declaration: replace scaffold placeholders and validate domain-product contracts.",
            "- Runtime telemetry: emit or generate deterministic local telemetry from repo-native commands.",
            "- SLO policy: tune blocking and advisory thresholds with owner escalation.",
            "- Access policy: define tenant, role, consumer, and use-case entitlement.",
            "- Evidence policy: classify public, restricted, operator-only, and internal-only fields.",
            "- Lifecycle policy: define active, preview, deprecated, replaced, blocked, or retired posture.",
            "- Gateway publication: expose the product only through governed gateway APIs.",
            "- Workbench discovery: consume gateway/BFF only and render degraded states truthfully.",
            "- Tests: add repo-native unit/contract tests and platform cross-repo certification proof.",
            "- Documentation: update repo context, operator docs, and customer/operator evidence notes.",
            "",
            "## Validation Commands",
            "",
            "```powershell",
            (
                "python automation/generate_domain_product_onboarding.py "
                f"--repository {repository} --product-name {product_name} "
                f"--product-version {product_version} --output-directory <bundle> --check"
            ),
            "python automation/generate_enterprise_mesh_maturity_matrix.py --check --generated-at-utc 2026-04-20T00:00:00Z",
            "python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def scaffold_domain_product_onboarding(
    *,
    repository: str,
    product_name: str,
    product_version: str,
    authoritative_domain: str,
    product_family: str,
    output_directory: Path,
) -> list[Path]:
    _validate_identity_inputs(
        repository=repository,
        product_name=product_name,
        product_version=product_version,
    )
    product_slug = _kebab(product_name)
    written_paths = [
        output_directory
        / "contracts"
        / "domain-data-products"
        / f"{repository}-products.v1.json",
        output_directory
        / "contracts"
        / "trust-telemetry"
        / f"{product_slug}.telemetry.v1.json",
        output_directory
        / "platform-contracts"
        / "mesh-slo"
        / f"{repository}-{product_slug}.slo.v1.json",
        output_directory
        / "platform-contracts"
        / "mesh-access"
        / f"{repository}-{product_slug}.access.v1.json",
        output_directory
        / "platform-contracts"
        / "mesh-evidence"
        / f"{repository}-{product_slug}.evidence-pack-policy.v1.json",
    ]
    payloads = [
        _product_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
            authoritative_domain=authoritative_domain,
            product_family=product_family,
        ),
        _telemetry_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
        ),
        _slo_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
        ),
        _access_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
        ),
        _evidence_payload(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
        ),
    ]
    for path, payload in zip(written_paths, payloads, strict=True):
        _write_json(path, payload)

    readme_path = output_directory / "README.md"
    readme_path.write_text(
        _readme(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
            authoritative_domain=authoritative_domain,
            product_family=product_family,
        ),
        encoding="utf-8",
    )

    checklist_path = output_directory / "PRODUCT-ONBOARDING-CHECKLIST.md"
    checklist_path.parent.mkdir(parents=True, exist_ok=True)
    checklist_path.write_text(
        _checklist(
            repository=repository,
            product_name=product_name,
            product_version=product_version,
            written_paths=[*written_paths, readme_path, checklist_path],
            output_directory=output_directory,
        ),
        encoding="utf-8",
    )
    return [*written_paths, readme_path, checklist_path]


def _validate_identity_inputs(
    *, repository: str, product_name: str, product_version: str
) -> None:
    if not REPOSITORY_PATTERN.fullmatch(repository):
        raise ValueError("repository must match lotus-*")
    if not PRODUCT_NAME_PATTERN.fullmatch(product_name):
        raise ValueError("product_name must be PascalCase without separators")
    if not PRODUCT_VERSION_PATTERN.fullmatch(product_version):
        raise ValueError("product_version must be vN or semantic versioning")


def _load_required_json(path: Path, issues: list[str]) -> dict[str, Any]:
    if not path.exists():
        issues.append(f"{path}: required onboarding file is missing")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(f"{path}: invalid JSON: {exc}")
        return {}


def validate_domain_product_onboarding_bundle(
    *,
    output_directory: Path,
    repository: str,
    product_name: str,
    product_version: str,
) -> list[str]:
    _validate_identity_inputs(
        repository=repository,
        product_name=product_name,
        product_version=product_version,
    )
    product_slug = _kebab(product_name)
    product_id = _product_id(repository, product_name, product_version)
    required_paths = {
        "product": output_directory
        / "contracts"
        / "domain-data-products"
        / f"{repository}-products.v1.json",
        "telemetry": output_directory
        / "contracts"
        / "trust-telemetry"
        / f"{product_slug}.telemetry.v1.json",
        "slo": output_directory
        / "platform-contracts"
        / "mesh-slo"
        / f"{repository}-{product_slug}.slo.v1.json",
        "access": output_directory
        / "platform-contracts"
        / "mesh-access"
        / f"{repository}-{product_slug}.access.v1.json",
        "evidence": output_directory
        / "platform-contracts"
        / "mesh-evidence"
        / f"{repository}-{product_slug}.evidence-pack-policy.v1.json",
        "readme": output_directory / "README.md",
        "checklist": output_directory / "PRODUCT-ONBOARDING-CHECKLIST.md",
    }
    issues: list[str] = []
    payloads = {
        key: _load_required_json(path, issues)
        for key, path in required_paths.items()
        if key not in {"readme", "checklist"}
    }

    product_payload = payloads.get("product", {})
    if product_payload.get("contract_id") != "domain-data-products":
        issues.append("product declaration contract_id must be domain-data-products")
    if product_payload.get("producer_repository") != repository:
        issues.append("product declaration producer_repository does not match")
    products = product_payload.get("products", [])
    if not products:
        issues.append("product declaration must include at least one product")
    else:
        product = products[0]
        if product.get("product_name") != product_name:
            issues.append("product declaration product_name does not match")
        if product.get("product_version") != product_version:
            issues.append("product declaration product_version does not match")
        if product.get("owner_repository") != repository:
            issues.append("product declaration owner_repository does not match")

    for key in ("telemetry", "slo", "access", "evidence"):
        payload = payloads.get(key, {})
        if payload.get("product_id") != product_id:
            issues.append(f"{key} policy product_id does not match {product_id}")
        if payload.get("producer_repository") != repository:
            issues.append(f"{key} policy producer_repository does not match")

    readme_path = required_paths["readme"]
    if not readme_path.exists():
        issues.append(f"{readme_path}: required onboarding file is missing")
    else:
        readme = readme_path.read_text(encoding="utf-8")
        for required_text in (
            product_id,
            "Keep source truth in the producer repository",
            "Publish through `lotus-gateway`",
            "Treat placeholders as blockers before production certification",
        ):
            if required_text not in readme:
                issues.append(f"README missing required guidance: {required_text}")

    checklist_path = required_paths["checklist"]
    if not checklist_path.exists():
        issues.append(f"{checklist_path}: required onboarding file is missing")
    else:
        checklist = checklist_path.read_text(encoding="utf-8")
        for section in (
            "Producer declaration",
            "Runtime telemetry",
            "SLO policy",
            "Access policy",
            "Evidence policy",
            "Lifecycle policy",
            "Gateway publication",
            "Workbench discovery",
            "Tests",
            "Documentation",
        ):
            if section not in checklist:
                issues.append(f"checklist missing section: {section}")

    return issues


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate or validate an RFC-0091 domain-product onboarding bundle."
    )
    parser.add_argument("--repository", required=True)
    parser.add_argument("--product-name", required=True)
    parser.add_argument("--product-version", default="v1")
    parser.add_argument("--authoritative-domain", default="replace_with_domain")
    parser.add_argument("--product-family", default="replace_with_product_family")
    parser.add_argument("--output-directory", type=Path, default=None)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    output_directory = args.output_directory or (
        DEFAULT_OUTPUT_ROOT / f"{args.repository}-{_kebab(args.product_name)}"
    )
    if args.check:
        issues = validate_domain_product_onboarding_bundle(
            output_directory=output_directory,
            repository=args.repository,
            product_name=args.product_name,
            product_version=args.product_version,
        )
        for issue in issues:
            print(issue)
        return 1 if issues else 0

    written_paths = scaffold_domain_product_onboarding(
        repository=args.repository,
        product_name=args.product_name,
        product_version=args.product_version,
        authoritative_domain=args.authoritative_domain,
        product_family=args.product_family,
        output_directory=output_directory,
    )
    print(f"Wrote {len(written_paths)} onboarding files to {output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
