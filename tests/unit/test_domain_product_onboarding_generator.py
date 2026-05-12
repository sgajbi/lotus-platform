from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "automation" / "generate_domain_product_onboarding.py"


def _load_generator_module():
    spec = importlib.util.spec_from_file_location(
        "domain_product_onboarding_test", GENERATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_domain_product_onboarding_scaffold_writes_complete_bundle(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()

    written_paths = generator.scaffold_domain_product_onboarding(
        repository="lotus-report",
        product_name="ClientReportEvidencePack",
        product_version="v1",
        authoritative_domain="reporting",
        product_family="client_reporting",
        output_directory=tmp_path,
    )

    relative_paths = {path.relative_to(tmp_path).as_posix() for path in written_paths}
    assert relative_paths == {
        "contracts/domain-data-products/lotus-report-products.v1.json",
        "contracts/analytics-products/client-report-evidence-pack.analytics-profile.v1.json",
        "contracts/source-data-products/client-report-evidence-pack.api-profile.v1.json",
        "contracts/trust-telemetry/client-report-evidence-pack.telemetry.v1.json",
        "platform-contracts/mesh-slo/lotus-report-client-report-evidence-pack.slo.v1.json",
        "platform-contracts/mesh-access/lotus-report-client-report-evidence-pack.access.v1.json",
        "platform-contracts/mesh-evidence/lotus-report-client-report-evidence-pack.evidence-pack-policy.v1.json",
        "README.md",
        "PRODUCT-ONBOARDING-CHECKLIST.md",
        "docs/API-CERTIFICATION-CHECKLIST.md",
        "docs/INGESTION-PIPELINE-CHECKLIST.md",
        "docs/ANALYTICS-DATA-PRODUCT-CERTIFICATION-CHECKLIST.md",
    }

    product_declaration = json.loads(
        (
            tmp_path
            / "contracts"
            / "domain-data-products"
            / "lotus-report-products.v1.json"
        ).read_text(encoding="utf-8")
    )
    product = product_declaration["products"][0]
    assert product["product_name"] == "ClientReportEvidencePack"
    assert product["product_version"] == "v1"
    assert product["owner_repository"] == "lotus-report"
    assert product["authoritative_domain"] == "reporting"
    assert product["product_family"] == "client_reporting"
    assert product["approved_consumers"] == ["lotus-gateway"]

    telemetry = json.loads(
        (
            tmp_path
            / "contracts"
            / "trust-telemetry"
            / "client-report-evidence-pack.telemetry.v1.json"
        ).read_text(encoding="utf-8")
    )
    assert telemetry["product_id"] == "lotus-report:ClientReportEvidencePack:v1"
    assert telemetry["producer_repository"] == "lotus-report"
    assert telemetry["lineage"]["lineage_materialized"] is True

    source_api_profile = json.loads(
        (
            tmp_path
            / "contracts"
            / "source-data-products"
            / "client-report-evidence-pack.api-profile.v1.json"
        ).read_text(encoding="utf-8")
    )
    assert source_api_profile["contract_id"] == "lotus-source-data-product-api-profile"
    assert (
        source_api_profile["product_id"] == "lotus-report:ClientReportEvidencePack:v1"
    )
    assert source_api_profile["source_ingestion"]["required"] is True
    assert source_api_profile["serving_api"]["required"] is True
    assert source_api_profile["certification"]["api_certification_required"] is True
    assert (
        source_api_profile["certification"]["live_canonical_evidence_required"] is True
    )
    assert (
        source_api_profile["downstream_consumption"][
            "duplicate_endpoint_review_required"
        ]
        is True
    )
    analytics_profile = json.loads(
        (
            tmp_path
            / "contracts"
            / "analytics-products"
            / "client-report-evidence-pack.analytics-profile.v1.json"
        ).read_text(encoding="utf-8")
    )
    assert analytics_profile["contract_id"] == "lotus-analytics-data-product-profile"
    assert analytics_profile["product_id"] == "lotus-report:ClientReportEvidencePack:v1"
    assert (
        analytics_profile["analytics_methodology"][
            "deterministic_worked_examples_required"
        ]
        is True
    )
    assert (
        analytics_profile["computation_contract"][
            "raw_vs_final_result_evidence_required"
        ]
        is True
    )
    assert (
        analytics_profile["computation_contract"][
            "materiality_threshold_policy_required"
        ]
        is True
    )
    assert analytics_profile["computation_contract"]["status_contract_required"] is True
    assert (
        analytics_profile["computation_contract"]["source_alignment_controls_required"]
        is True
    )
    assert (
        analytics_profile["computation_contract"][
            "support_safe_daily_evidence_required"
        ]
        is True
    )
    assert (
        analytics_profile["downstream_realization"][
            "same_rfc_consumer_updates_required"
        ]
        is True
    )

    assert (
        generator.validate_domain_product_onboarding_bundle(
            output_directory=tmp_path,
            repository="lotus-report",
            product_name="ClientReportEvidencePack",
            product_version="v1",
        )
        == []
    )

    checklist = (tmp_path / "PRODUCT-ONBOARDING-CHECKLIST.md").read_text(
        encoding="utf-8"
    )
    assert (
        "--repository lotus-report --product-name ClientReportEvidencePack" in checklist
    )
    assert "Source API profile" in checklist
    assert "Analytics product profile" in checklist

    api_certification = (
        tmp_path / "docs" / "API-CERTIFICATION-CHECKLIST.md"
    ).read_text(encoding="utf-8")
    assert "every request option" in api_certification
    assert "every output family" in api_certification
    assert "Live canonical validation" in api_certification

    ingestion = (tmp_path / "docs" / "INGESTION-PIPELINE-CHECKLIST.md").read_text(
        encoding="utf-8"
    )
    assert "Authoritative source systems" in ingestion
    assert "Idempotency keys" in ingestion
    assert "Canonical demo seed data" in ingestion

    analytics_certification = (
        tmp_path / "docs" / "ANALYTICS-DATA-PRODUCT-CERTIFICATION-CHECKLIST.md"
    ).read_text(encoding="utf-8")
    assert "Methodology documentation" in analytics_certification
    assert "Raw result" in analytics_certification
    assert "materiality classification" in analytics_certification
    assert "source-alignment controls" in analytics_certification
    assert "Support-safe daily" in analytics_certification
    assert "Gateway preserves" in analytics_certification
    assert "Workbench renders" in analytics_certification
    assert "All downstream consumers" in analytics_certification
    assert "mesh certification" in analytics_certification


def test_domain_product_onboarding_validation_rejects_identity_drift(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()
    generator.scaffold_domain_product_onboarding(
        repository="lotus-manage",
        product_name="PortfolioActionRegister",
        product_version="v1",
        authoritative_domain="portfolio_management",
        product_family="portfolio_operations",
        output_directory=tmp_path,
    )
    telemetry_path = (
        tmp_path
        / "contracts"
        / "trust-telemetry"
        / "portfolio-action-register.telemetry.v1.json"
    )
    telemetry = json.loads(telemetry_path.read_text(encoding="utf-8"))
    telemetry["product_id"] = "lotus-manage:WrongProduct:v1"
    telemetry_path.write_text(json.dumps(telemetry, indent=2) + "\n", encoding="utf-8")

    issues = generator.validate_domain_product_onboarding_bundle(
        output_directory=tmp_path,
        repository="lotus-manage",
        product_name="PortfolioActionRegister",
        product_version="v1",
    )

    assert issues == [
        "telemetry policy product_id does not match lotus-manage:PortfolioActionRegister:v1"
    ]


def test_domain_product_onboarding_validation_rejects_weak_source_api_profile(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()
    generator.scaffold_domain_product_onboarding(
        repository="lotus-core",
        product_name="DiscretionaryMandateBinding",
        product_version="v1",
        authoritative_domain="portfolio_management",
        product_family="dpm_source_data",
        output_directory=tmp_path,
    )
    source_profile_path = (
        tmp_path
        / "contracts"
        / "source-data-products"
        / "discretionary-mandate-binding.api-profile.v1.json"
    )
    source_profile = json.loads(source_profile_path.read_text(encoding="utf-8"))
    source_profile["certification"]["mesh_certification_required"] = False
    source_profile_path.write_text(
        json.dumps(source_profile, indent=2) + "\n",
        encoding="utf-8",
    )

    issues = generator.validate_domain_product_onboarding_bundle(
        output_directory=tmp_path,
        repository="lotus-core",
        product_name="DiscretionaryMandateBinding",
        product_version="v1",
    )

    assert issues == [
        "source_api_profile certification.mesh_certification_required must be true"
    ]


def test_domain_product_onboarding_validation_rejects_weak_analytics_profile(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()
    generator.scaffold_domain_product_onboarding(
        repository="lotus-performance",
        product_name="ContributionAnalytics",
        product_version="v1",
        authoritative_domain="performance_analytics",
        product_family="analytics_output",
        output_directory=tmp_path,
    )
    analytics_profile_path = (
        tmp_path
        / "contracts"
        / "analytics-products"
        / "contribution-analytics.analytics-profile.v1.json"
    )
    analytics_profile = json.loads(analytics_profile_path.read_text(encoding="utf-8"))
    analytics_profile["computation_contract"][
        "raw_vs_final_result_evidence_required"
    ] = False
    analytics_profile_path.write_text(
        json.dumps(analytics_profile, indent=2) + "\n",
        encoding="utf-8",
    )

    issues = generator.validate_domain_product_onboarding_bundle(
        output_directory=tmp_path,
        repository="lotus-performance",
        product_name="ContributionAnalytics",
        product_version="v1",
    )

    assert issues == [
        "analytics_product_profile computation_contract.raw_vs_final_result_evidence_required must be true"
    ]


def test_domain_product_onboarding_validation_rejects_incomplete_bundle(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()
    generator.scaffold_domain_product_onboarding(
        repository="lotus-report",
        product_name="ClientReportEvidencePack",
        product_version="v1",
        authoritative_domain="reporting",
        product_family="client_reporting",
        output_directory=tmp_path,
    )
    (tmp_path / "PRODUCT-ONBOARDING-CHECKLIST.md").unlink()

    issues = generator.validate_domain_product_onboarding_bundle(
        output_directory=tmp_path,
        repository="lotus-report",
        product_name="ClientReportEvidencePack",
        product_version="v1",
    )

    assert issues == [
        f"{tmp_path / 'PRODUCT-ONBOARDING-CHECKLIST.md'}: required onboarding file is missing"
    ]


def test_domain_product_onboarding_cli_check_fails_with_actionable_issue(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(GENERATOR_PATH),
            "--repository",
            "lotus-report",
            "--product-name",
            "ClientReportEvidencePack",
            "--product-version",
            "v1",
            "--output-directory",
            str(tmp_path),
            "--check",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "required onboarding file is missing" in result.stdout
