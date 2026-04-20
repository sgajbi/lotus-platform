from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "automation" / "generate_mesh_evidence_pack.py"
POLICY_DIRECTORY = ROOT / "platform-contracts" / "mesh-evidence"
GENERATED_AT_UTC = "2026-04-20T00:00:00Z"


def _load_generator_module():
    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    spec = importlib.util.spec_from_file_location(
        "generate_mesh_evidence_pack_test", GENERATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _mesh_status() -> dict:
    products = [
        {
            "product_id": "lotus-core:PortfolioStateSnapshot:v1",
            "producer_repository": "lotus-core",
            "certification_state": "certified",
            "freshness_state": "current",
            "completeness_status": "complete",
            "reconciliation_status": "reconciled",
            "data_quality_status": "quality_passed",
            "issue_count": 0,
        },
        {
            "product_id": "lotus-performance:ReturnsSeriesBundle:v1",
            "producer_repository": "lotus-performance",
            "certification_state": "certified",
            "freshness_state": "current",
            "completeness_status": "complete",
            "reconciliation_status": "reconciled",
            "data_quality_status": "quality_passed",
            "issue_count": 0,
        },
        {
            "product_id": "lotus-risk:RiskMetricsReport:v1",
            "producer_repository": "lotus-risk",
            "certification_state": "certified",
            "freshness_state": "current",
            "completeness_status": "complete",
            "reconciliation_status": "reconciled",
            "data_quality_status": "quality_passed",
            "issue_count": 0,
        },
        {
            "product_id": "lotus-advise:AdvisoryProposalLifecycleRecord:v1",
            "producer_repository": "lotus-advise",
            "certification_state": "certified",
            "freshness_state": "current",
            "completeness_status": "complete",
            "reconciliation_status": "not_applicable",
            "data_quality_status": "quality_passed",
            "issue_count": 0,
        },
    ]
    live_certifications = []
    for product in products:
        producer, product_name, product_version = product["product_id"].split(":")
        live_certifications.append(
            {
                "product_id": product["product_id"],
                "producer_repository": producer,
                "product_name": product_name,
                "product_version": product_version,
                "source_repository": producer,
                "telemetry_path": f"{producer}/contracts/trust-telemetry/{product_name}.json",
                "emitted_at_utc": GENERATED_AT_UTC,
                "certification_state": "certified",
                "freshness_state": product["freshness_state"],
                "completeness_status": product["completeness_status"],
                "reconciliation_status": product["reconciliation_status"],
                "data_quality_status": product["data_quality_status"],
                "lineage_materialized": True,
                "blocked": False,
                "issue_count": 0,
            }
        )
    return {
        "contract_id": "lotus-mesh-certification-status",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0089"],
        "generated_at_utc": GENERATED_AT_UTC,
        "gate_mode": "blocking",
        "certification_state": "certified",
        "required_products": products,
        "summary": {
            "required_product_count": 4,
            "certified_required_product_count": 4,
            "attention_required_product_count": 0,
            "issue_count": 0,
            "error_count": 0,
            "warning_count": 0,
            "mesh_slo_violation_count": 0,
        },
        "issues": [],
        "source_artifacts": {
            "source_manifest": "platform-contracts/domain-data-products/domain-product-source-manifest.v1.json",
            "catalog": "generated/domain-product-catalog.json",
            "dependency_graph": "generated/domain-product-dependency-graph.json",
            "slo_policy_path": "platform-contracts/mesh-slo",
            "access_policy_path": "platform-contracts/mesh-access",
            "telemetry_inputs": ["lotus-core/contracts/trust-telemetry/example.json"],
        },
        "live_trust_certification": {
            "contract_id": "lotus-domain-product-live-trust-certification",
            "contract_version": "1.0.0",
            "governed_by_rfcs": ["RFC-0087"],
            "generated_at_utc": GENERATED_AT_UTC,
            "source_telemetry_path": "test",
            "summary": {
                "certification_state": "certified",
                "telemetry_snapshot_count": 4,
                "certified_snapshot_count": 4,
                "attention_required_count": 0,
                "issue_count": 0,
            },
            "product_certifications": live_certifications,
            "issues": [],
        },
    }


def test_checked_in_mesh_evidence_policies_are_valid() -> None:
    generator = _load_generator_module()

    assert generator.validate_mesh_evidence_policies(POLICY_DIRECTORY) == []


def test_evidence_pack_manifest_filters_customer_public_sections() -> None:
    generator = _load_generator_module()

    manifest = generator.build_evidence_pack_manifest(
        mesh_status=_mesh_status(),
        generated_at_utc=GENERATED_AT_UTC,
        pack_id="pack-public",
        audience="customer-public",
    )

    assert manifest["audience"] == "customer-public"
    assert manifest["included_access_classes"] == ["public_customer"]
    for product in manifest["products"]:
        section_names = {section["section"] for section in product["sections"]}
        assert section_names == {"product_identity", "certification_state"}
        section_text = json.dumps(product["sections"])
        assert "telemetry_path" not in section_text
        assert "source_artifacts" not in section_text
        assert "allowed_consumers" not in section_text


def test_evidence_pack_manifest_includes_restricted_sections_for_authorized_customer() -> None:
    generator = _load_generator_module()

    manifest = generator.build_evidence_pack_manifest(
        mesh_status=_mesh_status(),
        generated_at_utc=GENERATED_AT_UTC,
        pack_id="pack-authorized",
        audience="customer-authorized",
    )

    first_product = manifest["products"][0]
    section_names = {section["section"] for section in first_product["sections"]}
    assert "runtime_telemetry" in section_names
    assert "slo_posture" in section_names
    assert "access_posture" in section_names
    assert "source_artifacts" not in section_names


def test_write_mesh_evidence_pack_persists_manifest_and_history(tmp_path: Path) -> None:
    generator = _load_generator_module()
    status_path = tmp_path / "mesh-certification-status.json"
    status_path.write_text(json.dumps(_mesh_status()), encoding="utf-8")

    manifest = generator.write_mesh_evidence_pack(
        mesh_status_path=status_path,
        output_directory=tmp_path / "packs",
        generated_at_utc=GENERATED_AT_UTC,
        audience="operator",
        pack_id="pack-operator",
    )

    pack_directory = tmp_path / "packs" / "pack-operator"
    assert manifest["pack_id"] == "pack-operator"
    assert (pack_directory / "evidence-pack-manifest.json").exists()
    assert (pack_directory / "evidence-pack-manifest.md").exists()
    history = json.loads(
        (pack_directory / "certification-history-record.json").read_text(
            encoding="utf-8"
        )
    )
    assert history["contract_id"] == "lotus-mesh-certification-history-record"
    assert history["summary"]["certified_required_product_count"] == 4
    assert (
        tmp_path
        / "packs"
        / "certification-history"
        / "pack-operator.json"
    ).exists()


def test_mesh_evidence_policy_validation_rejects_missing_required_product(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()
    for policy_path in POLICY_DIRECTORY.glob("*.evidence-pack-policy.v1.json"):
        if "lotus-core" not in policy_path.name:
            (tmp_path / policy_path.name).write_text(
                policy_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

    issues = generator.validate_mesh_evidence_policies(tmp_path)

    assert issues == [
        f"{tmp_path}: missing required mesh evidence policy for lotus-core product lotus-core:PortfolioStateSnapshot:v1"
    ]


def test_mesh_evidence_policy_validation_requires_classified_sections(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()
    policy_path = tmp_path / "bad.evidence-pack-policy.v1.json"
    policy = json.loads(
        (
            POLICY_DIRECTORY
            / "lotus-core-portfolio-state-snapshot.evidence-pack-policy.v1.json"
        ).read_text(encoding="utf-8")
    )
    policy["required_manifest_sections"].append("unclassified_section")
    policy_path.write_text(json.dumps(policy), encoding="utf-8")

    issues = generator.validate_mesh_evidence_policies(
        policy_path,
        required_products={},
    )

    assert issues == [
        f"{policy_path}: required_manifest_sections missing field access classes: unclassified_section"
    ]
