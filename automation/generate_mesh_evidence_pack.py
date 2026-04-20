from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Literal

from domain_product_discovery import DEFAULT_CATALOG_PATH, load_catalog
from mesh_maturity_scope import REQUIRED_PRODUCTS
from validate_mesh_access_policies import (
    DEFAULT_ACCESS_POLICY_DIRECTORY,
    load_mesh_access_policies,
    validate_mesh_access_policies,
)
from validate_mesh_slo_policies import (
    DEFAULT_SLO_POLICY_DIRECTORY,
    load_mesh_slo_policies,
    validate_mesh_slo_policies,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MESH_CERTIFICATION_STATUS_PATH = (
    ROOT / "output" / "mesh-certification" / "mesh-certification-status.json"
)
DEFAULT_EVIDENCE_POLICY_DIRECTORY = ROOT / "platform-contracts" / "mesh-evidence"
DEFAULT_OUTPUT_DIRECTORY = ROOT / "output" / "mesh-evidence-packs"
EVIDENCE_POLICY_GLOB = "*.evidence-pack-policy.v1.json"
Audience = Literal["customer-public", "customer-authorized", "operator"]
ACCESS_LEVELS_BY_AUDIENCE: dict[Audience, set[str]] = {
    "customer-public": {"public_customer"},
    "customer-authorized": {"public_customer", "restricted_customer"},
    "operator": {"public_customer", "restricted_customer", "operator_only"},
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _iter_policy_paths(policy_path: Path) -> list[Path]:
    if policy_path.is_file():
        return [policy_path]
    return sorted(policy_path.rglob(EVIDENCE_POLICY_GLOB))


def load_mesh_evidence_policies(
    policy_path: Path = DEFAULT_EVIDENCE_POLICY_DIRECTORY,
) -> dict[str, tuple[Path, dict[str, Any]]]:
    policies: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in _iter_policy_paths(policy_path):
        payload = _load_json(path)
        product_id = payload.get("product_id")
        if isinstance(product_id, str):
            policies[product_id] = (path, payload)
    return policies


def validate_mesh_evidence_policies(
    policy_path: Path = DEFAULT_EVIDENCE_POLICY_DIRECTORY,
    *,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    required_products: dict[str, str] = REQUIRED_PRODUCTS,
) -> list[str]:
    catalog = load_catalog(catalog_path)
    products_by_id = {
        product["product_id"]: product for product in catalog.get("products", [])
    }
    paths = _iter_policy_paths(policy_path)
    if not paths:
        return [f"{policy_path}: no mesh evidence policy files found"]

    issues: list[str] = []
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
            issues.append(f"{path}: duplicate evidence policy for {product_id}")
        seen_product_ids.add(product_id)

        product = products_by_id.get(product_id)
        if product is None:
            issues.append(f"{path}: product_id does not exist in catalog: {product_id}")
            continue
        if payload.get("contract_id") != "lotus-mesh-evidence-pack-policy":
            issues.append(
                f"{path}: contract_id must be lotus-mesh-evidence-pack-policy"
            )
        if "RFC-0091" not in payload.get("governed_by_rfcs", []):
            issues.append(f"{path}: governed_by_rfcs must include RFC-0091")
        if payload.get("producer_repository") != product["producer_repository"]:
            issues.append(
                f"{path}: producer_repository must match catalog identity {product['producer_repository']}"
            )

        field_access_classes = payload.get("field_access_classes")
        if not isinstance(field_access_classes, dict) or not field_access_classes:
            issues.append(f"{path}: field_access_classes must be a non-empty object")
        else:
            invalid_classes = sorted(
                {
                    value
                    for value in field_access_classes.values()
                    if value
                    not in {
                        "public_customer",
                        "restricted_customer",
                        "operator_only",
                        "internal_only",
                    }
                }
            )
            if invalid_classes:
                issues.append(
                    f"{path}: field_access_classes contains invalid classes: {', '.join(invalid_classes)}"
                )

        required_sections = payload.get("required_manifest_sections")
        if not isinstance(required_sections, list) or not required_sections:
            issues.append(f"{path}: required_manifest_sections must be non-empty")
        elif isinstance(field_access_classes, dict):
            missing_classification = sorted(
                section
                for section in required_sections
                if section not in field_access_classes
            )
            if missing_classification:
                issues.append(
                    f"{path}: required_manifest_sections missing field access classes: "
                    + ", ".join(missing_classification)
                )

    for product_id, repository in required_products.items():
        if product_id not in seen_product_ids:
            issues.append(
                f"{policy_path}: missing required mesh evidence policy for {repository} product {product_id}"
            )
    return issues


def build_certification_history_record(
    *,
    mesh_status: dict[str, Any],
    generated_at_utc: str,
    pack_id: str,
    source_status_path: Path,
) -> dict[str, Any]:
    summary = mesh_status.get("summary", {})
    return {
        "contract_id": "lotus-mesh-certification-history-record",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0091"],
        "pack_id": pack_id,
        "generated_at_utc": generated_at_utc,
        "source_status_path": source_status_path.as_posix(),
        "mesh_certification_generated_at_utc": mesh_status.get("generated_at_utc"),
        "certification_state": mesh_status.get("certification_state"),
        "gate_mode": mesh_status.get("gate_mode"),
        "summary": {
            "required_product_count": summary.get("required_product_count", 0),
            "certified_required_product_count": summary.get(
                "certified_required_product_count", 0
            ),
            "attention_required_product_count": summary.get(
                "attention_required_product_count", 0
            ),
            "error_count": summary.get("error_count", 0),
            "warning_count": summary.get("warning_count", 0),
            "mesh_slo_violation_count": summary.get("mesh_slo_violation_count", 0),
        },
        "product_history": [
            {
                "product_id": product["product_id"],
                "producer_repository": product["producer_repository"],
                "certification_state": product["certification_state"],
                "freshness_state": product.get("freshness_state"),
                "completeness_status": product.get("completeness_status"),
                "reconciliation_status": product.get("reconciliation_status"),
                "data_quality_status": product.get("data_quality_status"),
                "issue_count": product.get("issue_count", 0),
            }
            for product in mesh_status.get("required_products", [])
        ],
    }


def build_evidence_pack_manifest(
    *,
    mesh_status: dict[str, Any],
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    evidence_policy_path: Path = DEFAULT_EVIDENCE_POLICY_DIRECTORY,
    slo_policy_path: Path = DEFAULT_SLO_POLICY_DIRECTORY,
    access_policy_path: Path = DEFAULT_ACCESS_POLICY_DIRECTORY,
    source_status_path: Path = DEFAULT_MESH_CERTIFICATION_STATUS_PATH,
    generated_at_utc: str,
    pack_id: str,
    audience: Audience,
) -> dict[str, Any]:
    policy_issues = [
        *validate_mesh_evidence_policies(
            evidence_policy_path, catalog_path=catalog_path
        ),
        *validate_mesh_slo_policies(slo_policy_path, catalog_path=catalog_path),
        *validate_mesh_access_policies(access_policy_path, catalog_path=catalog_path),
    ]
    if policy_issues:
        raise ValueError("; ".join(policy_issues))

    products_by_id = {
        product["product_id"]: product
        for product in load_catalog(catalog_path).get("products", [])
    }
    evidence_policies = load_mesh_evidence_policies(evidence_policy_path)
    slo_policies = load_mesh_slo_policies(slo_policy_path)
    access_policies = load_mesh_access_policies(access_policy_path)
    live_by_product = {
        certification["product_id"]: certification
        for certification in mesh_status.get("live_trust_certification", {}).get(
            "product_certifications", []
        )
    }

    included_access_classes = ACCESS_LEVELS_BY_AUDIENCE[audience]
    product_manifests = []
    for product_status in mesh_status.get("required_products", []):
        product_id = product_status["product_id"]
        product = products_by_id[product_id]
        policy = evidence_policies[product_id][1]
        field_access = policy["field_access_classes"]
        sections = _build_sections(
            product=product,
            product_status=product_status,
            live_certification=live_by_product.get(product_id, {}),
            slo_policy=slo_policies[product_id][1],
            access_policy=access_policies[product_id][1],
            field_access=field_access,
            included_access_classes=included_access_classes,
            mesh_status=mesh_status,
        )
        product_manifests.append(
            {
                "product_id": product_id,
                "producer_repository": product_status["producer_repository"],
                "included_section_count": len(sections),
                "sections": sections,
            }
        )

    return {
        "contract_id": "lotus-mesh-evidence-pack-manifest",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0091"],
        "pack_id": pack_id,
        "audience": audience,
        "included_access_classes": sorted(included_access_classes),
        "generated_at_utc": generated_at_utc,
        "source_status_path": source_status_path.as_posix(),
        "certification_state": mesh_status.get("certification_state"),
        "summary": {
            "product_count": len(product_manifests),
            "issue_count": mesh_status.get("summary", {}).get("issue_count", 0),
            "customer_filtered": audience == "customer-public",
        },
        "products": product_manifests,
    }


def _build_sections(
    *,
    product: dict[str, Any],
    product_status: dict[str, Any],
    live_certification: dict[str, Any],
    slo_policy: dict[str, Any],
    access_policy: dict[str, Any],
    field_access: dict[str, str],
    included_access_classes: set[str],
    mesh_status: dict[str, Any],
) -> list[dict[str, Any]]:
    section_payloads = {
        "product_identity": {
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "product_version": product["product_version"],
            "producer_repository": product["producer_repository"],
            "lifecycle_status": product.get("lifecycle_status"),
        },
        "certification_state": {
            "certification_state": product_status["certification_state"],
            "freshness_state": product_status.get("freshness_state"),
            "completeness_status": product_status.get("completeness_status"),
            "reconciliation_status": product_status.get("reconciliation_status"),
            "data_quality_status": product_status.get("data_quality_status"),
            "issue_count": product_status.get("issue_count", 0),
        },
        "source_declaration": {
            "source_path": product.get("source_path"),
            "authoritative_domain": product.get("authoritative_domain"),
            "product_family": product.get("product_family"),
        },
        "runtime_telemetry": {
            "emitted_at_utc": live_certification.get("emitted_at_utc"),
            "source_repository": live_certification.get("source_repository"),
            "telemetry_path": live_certification.get("telemetry_path"),
            "lineage_materialized": live_certification.get("lineage_materialized"),
            "blocked": live_certification.get("blocked"),
        },
        "slo_posture": {
            "freshness": slo_policy.get("freshness"),
            "completeness": slo_policy.get("completeness"),
            "reconciliation": slo_policy.get("reconciliation"),
            "data_quality": slo_policy.get("data_quality"),
            "lineage": slo_policy.get("lineage"),
        },
        "access_posture": {
            "default_posture": access_policy.get("default_posture"),
            "denial_posture": access_policy.get("denial_posture"),
            "allowed_consumers": access_policy.get("allowed_consumers"),
        },
        "dependency_graph": {
            "dependency_graph": mesh_status.get("source_artifacts", {}).get(
                "dependency_graph"
            )
        },
        "validation_lanes": {
            "gate_mode": mesh_status.get("gate_mode"),
            "validation_lanes": ["feature", "pr-merge"],
        },
        "source_artifacts": mesh_status.get("source_artifacts", {}),
        "operator_remediation": {
            "issues": mesh_status.get("issues", []),
        },
    }
    sections = []
    for section_name, payload in section_payloads.items():
        access_class = field_access.get(section_name, "internal_only")
        if access_class not in included_access_classes:
            continue
        sections.append(
            {
                "section": section_name,
                "access_class": access_class,
                "payload": payload,
            }
        )
    return sections


def render_evidence_pack_markdown(manifest: dict[str, Any]) -> str:
    product_rows = [
        "| Product | Producer | Sections |",
        "| --- | --- | --- |",
    ]
    for product in manifest["products"]:
        product_rows.append(
            "| "
            f"`{product['product_id']}` | "
            f"`{product['producer_repository']}` | "
            f"`{product['included_section_count']}` |"
        )
    return "\n".join(
        [
            "# Lotus Mesh Evidence Pack",
            "",
            f"- Pack ID: `{manifest['pack_id']}`",
            f"- Audience: `{manifest['audience']}`",
            f"- Certification state: `{manifest['certification_state']}`",
            f"- Generated at UTC: `{manifest['generated_at_utc']}`",
            "",
            "## Products",
            "",
            *product_rows,
            "",
        ]
    )


def write_mesh_evidence_pack(
    *,
    mesh_status_path: Path = DEFAULT_MESH_CERTIFICATION_STATUS_PATH,
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
    generated_at_utc: str,
    audience: Audience,
    pack_id: str | None = None,
) -> dict[str, Any]:
    mesh_status = _load_json(mesh_status_path)
    pack_id = (
        pack_id
        or f"mesh-evidence-{generated_at_utc.replace(':', '').replace('-', '')}-{audience}"
    )
    pack_directory = output_directory / pack_id
    manifest = build_evidence_pack_manifest(
        mesh_status=mesh_status,
        source_status_path=mesh_status_path,
        generated_at_utc=generated_at_utc,
        pack_id=pack_id,
        audience=audience,
    )
    history = build_certification_history_record(
        mesh_status=mesh_status,
        source_status_path=mesh_status_path,
        generated_at_utc=generated_at_utc,
        pack_id=pack_id,
    )
    _write_json(pack_directory / "evidence-pack-manifest.json", manifest)
    (pack_directory / "evidence-pack-manifest.md").write_text(
        render_evidence_pack_markdown(manifest),
        encoding="utf-8",
    )
    _write_json(pack_directory / "certification-history-record.json", history)
    _write_json(
        output_directory / "certification-history" / f"{pack_id}.json",
        history,
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate RFC-0091 certification history and evidence-pack manifests."
    )
    parser.add_argument(
        "--mesh-status-path",
        type=Path,
        default=DEFAULT_MESH_CERTIFICATION_STATUS_PATH,
    )
    parser.add_argument(
        "--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY
    )
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument(
        "--audience",
        choices=["customer-public", "customer-authorized", "operator"],
        default="customer-authorized",
    )
    parser.add_argument("--pack-id", default=None)
    args = parser.parse_args(argv)
    manifest = write_mesh_evidence_pack(
        mesh_status_path=args.mesh_status_path,
        output_directory=args.output_directory,
        generated_at_utc=args.generated_at_utc,
        audience=args.audience,
        pack_id=args.pack_id,
    )
    print(
        "Generated mesh evidence pack "
        f"{manifest['pack_id']} for {manifest['audience']} with "
        f"{manifest['summary']['product_count']} product(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
