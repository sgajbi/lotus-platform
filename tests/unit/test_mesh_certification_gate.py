from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "automation" / "mesh_certification_gate.py"


def _load_gate_module():
    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    spec = importlib.util.spec_from_file_location(
        "mesh_certification_gate_test", GATE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _metadata(product_id: str, product_name: str, product_version: str) -> dict:
    common = {
        "product_name": product_name,
        "product_version": product_version,
    }
    if product_id == "lotus-core:PortfolioStateSnapshot:v1":
        return {
            **common,
            "tenant_id": "tenant-private-bank",
            "generated_at": "2026-04-19T00:00:00Z",
            "as_of_date": "2026-04-19",
            "restatement_version": "1",
            "reconciliation_status": "reconciled",
            "data_quality_status": "quality_passed",
            "latest_evidence_timestamp": "2026-04-19T00:00:00Z",
            "source_batch_fingerprint": "batch-001",
            "snapshot_id": "snapshot-001",
            "policy_version": "2026.04",
            "correlation_id": "corr-001",
        }
    if product_id == "lotus-risk:RiskMetricsReport:v1":
        return {
            **common,
            "as_of_date": "2026-04-19",
            "lineage_version": "lineage-001",
            "request_fingerprint": "request-001",
            "source_services": "lotus-core,lotus-performance",
            "upstream_request_fingerprints": "core-001,performance-001",
            "benchmark_context": "MSCI_ACWI",
            "risk_free_context": "SOFR",
        }
    if product_id == "lotus-advise:AdvisoryProposalLifecycleRecord:v1":
        return {
            **common,
            "generated_at": "2026-04-19T00:00:00Z",
            "correlation_id": "corr-001",
        }
    return {
        **common,
        "generated_at": "2026-04-19T00:00:00Z",
        "as_of_date": "2026-04-19",
        "correlation_id": "corr-001",
    }


def _snapshot(product_id: str) -> dict:
    producer, product_name, product_version = product_id.split(":")
    return {
        "contract_id": "lotus-domain-product-trust-telemetry-snapshot",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0087"],
        "emitted_at_utc": "2026-04-19T00:00:00Z",
        "product_id": product_id,
        "producer_repository": producer,
        "product_name": product_name,
        "product_version": product_version,
        "source_repository": producer,
        "freshness": {
            "freshness_class": "daily",
            "freshness_state": "current",
            "evaluated_at_utc": "2026-04-19T00:00:00Z",
            "age_seconds": 60,
            "max_allowed_age_seconds": 86400,
        },
        "completeness_status": "complete",
        "reconciliation_status": "not_applicable",
        "data_quality_status": "quality_passed",
        "lineage": {
            "lineage_materialized": True,
            "evidence_access_class": "customer_consumable",
        },
        "blocking": {"blocked": False},
        "observed_trust_metadata": _metadata(
            product_id, product_name, product_version
        ),
        "evidence": {
            "correlation_id": "corr-001",
            "validation_lanes": ["feature", "pr-merge"],
        },
    }


def _write_required_snapshots(tmp_path: Path, *, stale_risk: bool = False) -> list[Path]:
    gate = _load_gate_module()
    telemetry_paths = []
    for product_id in gate.REQUIRED_PRODUCTS:
        payload = _snapshot(product_id)
        if stale_risk and product_id == "lotus-risk:RiskMetricsReport:v1":
            payload["freshness"]["freshness_state"] = "stale"
            payload["completeness_status"] = "stale"
            payload["data_quality_status"] = "quality_failed"
            payload["lineage"]["lineage_materialized"] = False
        path = tmp_path / f"{product_id.replace(':', '-')}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        telemetry_paths.append(path)
    return telemetry_paths


def test_mesh_certification_gate_certifies_required_products(tmp_path: Path) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)

    status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    assert status["contract_id"] == "lotus-mesh-certification-status"
    assert status["certification_state"] == "certified"
    assert status["summary"]["certified_required_product_count"] == 4
    assert status["summary"]["error_count"] == 0
    assert [product["product_id"] for product in status["required_products"]] == [
        "lotus-core:PortfolioStateSnapshot:v1",
        "lotus-performance:ReturnsSeriesBundle:v1",
        "lotus-risk:RiskMetricsReport:v1",
        "lotus-advise:AdvisoryProposalLifecycleRecord:v1",
    ]


def test_mesh_certification_gate_blocks_missing_and_stale_required_products(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path, stale_risk=True)
    telemetry_paths = [
        path
        for path in telemetry_paths
        if "lotus-advise-AdvisoryProposalLifecycleRecord-v1" not in path.name
    ]

    status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    issue_codes = {issue["code"] for issue in status["issues"]}
    assert status["certification_state"] == "failed"
    assert status["summary"]["error_count"] >= 2
    assert "missing_telemetry" in issue_codes
    assert "stale_telemetry" in issue_codes
    assert "data_quality_attention_required" in issue_codes
    assert gate._exit_code(status) == 1


def test_mesh_certification_gate_advisory_mode_reports_without_blocking(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path, stale_risk=True)

    status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        gate_mode="advisory",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    assert status["certification_state"] == "certified_with_warnings"
    assert status["summary"]["warning_count"] > 0
    assert status["summary"]["error_count"] == 0
    assert gate._exit_code(status) == 0


def test_mesh_certification_gate_writes_json_markdown_and_issues(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)
    status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )
    output_dir = tmp_path / "mesh-certification"

    gate.write_mesh_certification_status(status, output_directory=output_dir)

    rendered_status = json.loads(
        (output_dir / "mesh-certification-status.json").read_text(encoding="utf-8")
    )
    rendered_issues = json.loads(
        (output_dir / "mesh-certification-issues.json").read_text(encoding="utf-8")
    )
    markdown = (output_dir / "mesh-certification-status.md").read_text(
        encoding="utf-8"
    )
    assert rendered_status["certification_state"] == "certified"
    assert rendered_issues == []
    assert "# Lotus Mesh Certification Status" in markdown
    assert "lotus-core:PortfolioStateSnapshot:v1" in markdown


def test_mesh_certification_gate_detects_gateway_and_workbench_drift(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)
    gateway_root = tmp_path / "lotus-gateway"
    workbench_root = tmp_path / "lotus-workbench"
    gateway_router = gateway_root / "src" / "app" / "routers" / "domain_products.py"
    gateway_service = (
        gateway_root / "src" / "app" / "services" / "domain_product_catalog_service.py"
    )
    workbench_page = workbench_root / "src" / "app" / "data-products" / "page.tsx"
    workbench_api = (
        workbench_root / "src" / "features" / "domain-products" / "api.ts"
    )
    gateway_router.parent.mkdir(parents=True)
    gateway_service.parent.mkdir(parents=True)
    workbench_page.parent.mkdir(parents=True)
    workbench_api.parent.mkdir(parents=True)
    gateway_router.write_text(
        'router = APIRouter(prefix="/api/v1/domain-products")\n',
        encoding="utf-8",
    )
    gateway_service.write_text("# service exists\n", encoding="utf-8")
    workbench_page.write_text("// page exists\n", encoding="utf-8")
    workbench_api.write_text(
        'const BFF_PROXY_BASE = "/api/bff/api/v1";\n'
        'const bad = "generated/domain-product-catalog.json";\n',
        encoding="utf-8",
    )

    status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        gateway_root=gateway_root,
        workbench_root=workbench_root,
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
    )

    issue_codes = {issue["code"] for issue in status["issues"]}
    assert "gateway_publication_drift" in issue_codes
    assert "workbench_consumption_drift" in issue_codes
    assert status["summary"]["error_count"] >= 2
