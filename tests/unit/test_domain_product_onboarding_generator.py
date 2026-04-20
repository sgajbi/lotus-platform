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

    relative_paths = {
        path.relative_to(tmp_path).as_posix() for path in written_paths
    }
    assert relative_paths == {
        "contracts/domain-data-products/lotus-report-products.v1.json",
        "contracts/trust-telemetry/client-report-evidence-pack.telemetry.v1.json",
        "platform-contracts/mesh-slo/lotus-report-client-report-evidence-pack.slo.v1.json",
        "platform-contracts/mesh-access/lotus-report-client-report-evidence-pack.access.v1.json",
        "platform-contracts/mesh-evidence/lotus-report-client-report-evidence-pack.evidence-pack-policy.v1.json",
        "README.md",
        "PRODUCT-ONBOARDING-CHECKLIST.md",
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

    assert generator.validate_domain_product_onboarding_bundle(
        output_directory=tmp_path,
        repository="lotus-report",
        product_name="ClientReportEvidencePack",
        product_version="v1",
    ) == []

    checklist = (tmp_path / "PRODUCT-ONBOARDING-CHECKLIST.md").read_text(
        encoding="utf-8"
    )
    assert "--repository lotus-report --product-name ClientReportEvidencePack" in checklist


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
