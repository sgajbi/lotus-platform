from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "automation" / "mesh_certification_gate.py"


def _write_gateway_domain_product_publication(gateway_root: Path) -> None:
    router_root = gateway_root / "src" / "app" / "routers"
    service_path = (
        gateway_root / "src" / "app" / "services" / "domain_product_catalog_service.py"
    )
    router_root.mkdir(parents=True)
    service_path.parent.mkdir(parents=True)
    service_path.write_text("# service exists\n", encoding="utf-8")
    routes = {
        "domain_product_catalog.py": '"/catalog"',
        "domain_product_detail.py": (
            '"/products/{producer_repository}/{product_name}/{product_version}"'
        ),
        "domain_product_graph.py": '"/dependency-graph"',
        "domain_product_trust.py": '"/trust-certification"',
    }
    for module_name, route_fragment in routes.items():
        (router_root / module_name).write_text(
            'router = APIRouter(prefix="/api/v1/domain-products")\n'
            f"@router.get({route_fragment})\n",
            encoding="utf-8",
        )


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
    if product_id in {
        "lotus-core:PortfolioStateSnapshot:v1",
        "lotus-core:DpmSourceReadiness:v1",
    }:
        snapshot_id = (
            "dpm-source-readiness-001"
            if product_id == "lotus-core:DpmSourceReadiness:v1"
            else "snapshot-001"
        )
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
            "snapshot_id": snapshot_id,
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
    if product_id == "lotus-advise:AdvisoryProposalMemoEvidencePack:v1":
        return {
            **common,
            "generated_at": "2026-04-19T00:00:00Z",
            "content_hash": "sha256:advisory-proposal-memo-evidence-pack",
            "correlation_id": "corr-001",
        }
    if product_id == "lotus-report:ClientReportEvidencePack:v1":
        return {
            **common,
            "tenant_id": "tenant-private-bank",
            "tenant_admission": "caller_admitted",
            "generated_at": "2026-04-19T00:00:00Z",
            "as_of_date": "2026-04-19",
            "reconciliation_status": "reconciled",
            "reconciliation_reason_code": "policy_evidence_verified",
            "data_quality_status": "quality_passed",
            "source_batch_fingerprint": "client-report-evidence-pack-001",
            "lineage_bundle_id": "lineage-report-001",
            "correlation_id": "corr-001",
        }
    if product_id == "lotus-manage:PortfolioActionRegister:v1":
        return {
            **common,
            "tenant_id": "tenant-private-bank",
            "generated_at": "2026-04-19T00:00:00Z",
            "as_of_date": "2026-04-19",
            "reconciliation_status": "reconciled",
            "data_quality_status": "quality_passed",
            "lineage_bundle_id": "lineage-manage-001",
            "source_batch_fingerprint": "portfolio-action-register-001",
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
    reconciliation_status = (
        "reconciled"
        if product_id
        in {
            "lotus-core:PortfolioStateSnapshot:v1",
            "lotus-core:DpmSourceReadiness:v1",
            "lotus-performance:ReturnsSeriesBundle:v1",
            "lotus-risk:RiskMetricsReport:v1",
            "lotus-report:ClientReportEvidencePack:v1",
            "lotus-manage:PortfolioActionRegister:v1",
        }
        else "not_applicable"
    )
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
        "reconciliation_status": reconciliation_status,
        "data_quality_status": "quality_passed",
        "lineage": {
            "lineage_materialized": True,
            "evidence_access_class": "customer_consumable",
        },
        "blocking": {"blocked": False},
        "observed_trust_metadata": _metadata(product_id, product_name, product_version),
        "evidence": {
            "correlation_id": "corr-001",
            "validation_lanes": ["feature", "pr-merge"],
        },
    }


def _write_required_snapshots(
    tmp_path: Path, *, stale_risk: bool = False
) -> list[Path]:
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


def test_default_telemetry_selection_prefers_runtime_per_product(
    tmp_path: Path, monkeypatch
) -> None:
    gate = _load_gate_module()
    runtime_dir = tmp_path / "runtime"
    fixture_dir = tmp_path / "fixtures"
    runtime_dir.mkdir()
    fixture_dir.mkdir()
    runtime = _snapshot("lotus-advise:AdvisoryProposalLifecycleRecord:v1")
    runtime["evidence"]["source"] = "runtime"
    fixture = _snapshot("lotus-advise:AdvisoryProposalLifecycleRecord:v1")
    other_fixture = _snapshot("lotus-risk:RiskMetricsReport:v1")
    (runtime_dir / "advise.json").write_text(json.dumps(runtime), encoding="utf-8")
    (fixture_dir / "advise.json").write_text(json.dumps(fixture), encoding="utf-8")
    (fixture_dir / "risk.json").write_text(json.dumps(other_fixture), encoding="utf-8")
    monkeypatch.setattr(gate, "DEFAULT_RUNTIME_TELEMETRY_DIRECTORIES", [runtime_dir])
    monkeypatch.setattr(gate, "DEFAULT_TELEMETRY_DIRECTORIES", [fixture_dir])

    selected = gate._iter_default_telemetry_paths([])

    assert set(selected) == {runtime_dir / "advise.json", fixture_dir / "risk.json"}
    assert fixture_dir / "advise.json" not in selected


def test_default_telemetry_selection_does_not_hide_invalid_runtime(
    tmp_path: Path, monkeypatch
) -> None:
    gate = _load_gate_module()
    runtime_dir = tmp_path / "runtime"
    fixture_dir = tmp_path / "fixtures"
    runtime_dir.mkdir()
    fixture_dir.mkdir()
    (runtime_dir / "invalid.json").write_text("{not-json", encoding="utf-8")
    fixture = _snapshot("lotus-advise:AdvisoryProposalLifecycleRecord:v1")
    (fixture_dir / "advise.json").write_text(json.dumps(fixture), encoding="utf-8")
    monkeypatch.setattr(gate, "DEFAULT_RUNTIME_TELEMETRY_DIRECTORIES", [runtime_dir])
    monkeypatch.setattr(gate, "DEFAULT_TELEMETRY_DIRECTORIES", [fixture_dir])

    selected = gate._iter_default_telemetry_paths([])
    _, _, issues = gate._load_telemetry_payloads(selected)

    assert runtime_dir / "invalid.json" in selected
    assert fixture_dir / "advise.json" in selected
    assert [issue.code for issue in issues] == ["invalid_telemetry"]


def test_catalog_input_resolver_generates_current_repo_native_artifacts(
    tmp_path: Path, monkeypatch
) -> None:
    gate = _load_gate_module()
    generated_directories: list[Path] = []

    def fake_write_discovery_artifacts(output_directory: Path, **kwargs) -> None:
        generated_directories.append(output_directory)
        output_directory.mkdir(parents=True)
        (output_directory / "domain-product-catalog.json").write_text(
            json.dumps({"contract_id": "lotus-domain-product-catalog"}),
            encoding="utf-8",
        )
        (output_directory / "domain-product-dependency-graph.json").write_text(
            json.dumps({"contract_id": "lotus-domain-product-dependency-graph"}),
            encoding="utf-8",
        )

    monkeypatch.setattr(gate, "write_discovery_artifacts", fake_write_discovery_artifacts)
    output_directory = tmp_path / "mesh-certification"

    catalog_path, graph_path, source = gate._resolve_catalog_inputs(
        catalog_source="current-repo-native",
        explicit_catalog_path=None,
        explicit_dependency_graph_path=None,
        source_manifest_path=tmp_path / "source-manifest.json",
        output_directory=output_directory,
        generated_at_utc="2026-07-14T00:00:00Z",
    )

    assert source == "current-repo-native"
    assert generated_directories == [
        output_directory / "current-domain-product-discovery"
    ]
    assert catalog_path == (
        output_directory
        / "current-domain-product-discovery"
        / "domain-product-catalog.json"
    )
    assert graph_path == (
        output_directory
        / "current-domain-product-discovery"
        / "domain-product-dependency-graph.json"
    )


def test_catalog_input_resolver_infers_explicit_graph_path(tmp_path: Path) -> None:
    gate = _load_gate_module()
    catalog_path = tmp_path / "branch-current" / "domain-product-catalog.json"

    resolved_catalog, resolved_graph, source = gate._resolve_catalog_inputs(
        catalog_source="checked-in",
        explicit_catalog_path=catalog_path,
        explicit_dependency_graph_path=None,
        source_manifest_path=tmp_path / "source-manifest.json",
        output_directory=tmp_path / "mesh-certification",
        generated_at_utc="2026-07-14T00:00:00Z",
    )

    assert source == "explicit"
    assert resolved_catalog == catalog_path
    assert resolved_graph == catalog_path.parent / "domain-product-dependency-graph.json"


def test_mesh_policy_validators_receive_selected_catalog(
    tmp_path: Path, monkeypatch
) -> None:
    gate = _load_gate_module()
    selected_catalog = tmp_path / "domain-product-catalog.json"
    selected_catalog.write_text(
        (ROOT / "generated" / "domain-product-catalog.json").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )
    selected_graph = tmp_path / "domain-product-dependency-graph.json"
    selected_graph.write_text(
        (ROOT / "generated" / "domain-product-dependency-graph.json").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )
    received_catalog_paths: list[Path] = []

    def fake_validate_mesh_slo_policies(policy_path: Path, *, catalog_path: Path):
        received_catalog_paths.append(catalog_path)
        return []

    def fake_validate_mesh_access_policies(policy_path: Path, *, catalog_path: Path):
        received_catalog_paths.append(catalog_path)
        return []

    monkeypatch.setattr(
        gate, "validate_mesh_slo_policies", fake_validate_mesh_slo_policies
    )
    monkeypatch.setattr(
        gate, "validate_mesh_access_policies", fake_validate_mesh_access_policies
    )

    status = gate.build_mesh_certification_status(
        telemetry_paths=_write_required_snapshots(tmp_path),
        catalog_path=selected_catalog,
        dependency_graph_path=selected_graph,
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    assert status["summary"]["error_count"] == 0
    assert status["source_artifacts"]["catalog_source"] == "explicit"
    assert received_catalog_paths == [selected_catalog, selected_catalog]


def test_mesh_certification_gate_current_repo_native_catalog_replaces_stale_catalog(
    tmp_path: Path, monkeypatch
) -> None:
    gate = _load_gate_module()
    telemetry_dir = tmp_path / "telemetry"
    telemetry_dir.mkdir()
    telemetry_paths = _write_required_snapshots(telemetry_dir)
    checked_in_catalog = json.loads(
        (ROOT / "generated" / "domain-product-catalog.json").read_text(
            encoding="utf-8"
        )
    )
    checked_in_graph = json.loads(
        (ROOT / "generated" / "domain-product-dependency-graph.json").read_text(
            encoding="utf-8"
        )
    )
    stale_catalog = {
        **checked_in_catalog,
        "products": [
            product
            for product in checked_in_catalog["products"]
            if product["product_id"] != "lotus-manage:PortfolioActionRegister:v1"
        ],
    }
    stale_catalog_path = tmp_path / "stale-domain-product-catalog.json"
    stale_graph_path = tmp_path / "stale-domain-product-dependency-graph.json"
    stale_catalog_path.write_text(json.dumps(stale_catalog), encoding="utf-8")
    stale_graph_path.write_text(json.dumps(checked_in_graph), encoding="utf-8")

    stale_status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        catalog_path=stale_catalog_path,
        dependency_graph_path=stale_graph_path,
        gate_mode="blocking",
        generated_at_utc="2026-07-14T00:00:00Z",
        check_publication_surfaces=False,
    )

    assert stale_status["certification_state"] == "failed"
    assert any(
        issue["code"] == "catalog_drift"
        and issue["product_id"] == "lotus-manage:PortfolioActionRegister:v1"
        for issue in stale_status["issues"]
    )

    def fake_write_discovery_artifacts(output_directory: Path, **kwargs) -> None:
        output_directory.mkdir(parents=True)
        (output_directory / "domain-product-catalog.json").write_text(
            json.dumps(checked_in_catalog),
            encoding="utf-8",
        )
        (output_directory / "domain-product-dependency-graph.json").write_text(
            json.dumps(checked_in_graph),
            encoding="utf-8",
        )

    monkeypatch.setattr(gate, "write_discovery_artifacts", fake_write_discovery_artifacts)
    output_directory = tmp_path / "mesh-certification"

    exit_code = gate.main(
        [
            "--mode",
            "blocking",
            "--generated-at-utc",
            "2026-07-14T00:00:00Z",
            "--skip-publication-checks",
            "--catalog-source",
            "current-repo-native",
            "--telemetry-path",
            str(telemetry_dir),
            "--output-directory",
            str(output_directory),
        ]
    )

    status = json.loads(
        (output_directory / "mesh-certification-status.json").read_text(
            encoding="utf-8"
        )
    )
    assert exit_code == 0
    assert status["certification_state"] == "certified"
    assert status["source_artifacts"]["catalog_source"] == "current-repo-native"
    assert status["source_artifacts"]["catalog"].endswith(
        "current-domain-product-discovery/domain-product-catalog.json"
    )


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
    assert status["governed_by_rfcs"] == ["RFC-0089", "RFC-0091"]
    assert status["certification_state"] == "certified"
    assert status["summary"]["certified_required_product_count"] == 7
    assert status["summary"]["error_count"] == 0
    assert status["summary"]["mesh_lifecycle_issue_count"] == 0
    assert status["summary"]["mesh_evidence_issue_count"] == 0
    assert {family["family"] for family in status["maturity_check_families"]} == {
        "telemetry",
        "slo",
        "access",
        "lifecycle",
        "evidence",
        "catalog",
        "gateway",
        "workbench",
    }
    assert all(
        family["state"] == "passed" for family in status["maturity_check_families"]
    )
    assert [product["product_id"] for product in status["required_products"]] == [
        "lotus-core:PortfolioStateSnapshot:v1",
        "lotus-core:DpmSourceReadiness:v1",
        "lotus-performance:ReturnsSeriesBundle:v1",
        "lotus-risk:RiskMetricsReport:v1",
        "lotus-advise:AdvisoryProposalLifecycleRecord:v1",
        "lotus-advise:AdvisoryProposalMemoEvidencePack:v1",
        "lotus-manage:PortfolioActionRegister:v1",
    ]


def test_mesh_certification_gate_allows_scoped_report_analytics_block(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)
    report_path = tmp_path / "lotus-report-ClientReportEvidencePack-v1.json"
    report_path.write_text(
        json.dumps(_snapshot("lotus-report:ClientReportEvidencePack:v1")),
        encoding="utf-8",
    )
    telemetry_paths.append(report_path)
    report_payload = json.loads(report_path.read_text(encoding="utf-8"))
    report_payload["completeness_status"] = "partial"
    report_payload["data_quality_status"] = "quality_warning"
    report_payload["blocking"] = {
        "blocked": True,
        "blocking_scope": "analytics_enriched_evidence_certification",
        "blocked_reason": (
            "upstream performance and risk producer declarations do not yet "
            "approve lotus-report"
        ),
    }
    report_path.write_text(json.dumps(report_payload), encoding="utf-8")

    status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    assert status["certification_state"] == "certified_with_warnings"
    assert status["summary"]["error_count"] == 0
    assert status["summary"]["warning_count"] == 1
    assert status["summary"]["certified_required_product_count"] == 7
    assert status["summary"]["attention_required_product_count"] == 0
    assert status["issues"] == [
        {
            "code": "product_blocked",
            "severity": "warning",
            "producer_repository": "lotus-report",
            "product_id": "lotus-report:ClientReportEvidencePack:v1",
            "remediation": (
                "Product is blocked: upstream performance and risk producer "
                "declarations do not yet approve lotus-report"
            ),
            "source_evidence_path": report_path.as_posix(),
        }
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


def test_mesh_certification_gate_blocks_mesh_slo_violations(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)
    risk_path = next(path for path in telemetry_paths if "lotus-risk" in path.name)
    risk_snapshot = json.loads(risk_path.read_text(encoding="utf-8"))
    risk_snapshot["freshness"]["age_seconds"] = 90000
    risk_path.write_text(json.dumps(risk_snapshot), encoding="utf-8")

    status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    assert status["certification_state"] == "failed"
    assert status["summary"]["mesh_slo_violation_count"] == 1
    assert any(
        issue["code"] == "mesh_slo_freshness_violation"
        and issue["product_id"] == "lotus-risk:RiskMetricsReport:v1"
        for issue in status["issues"]
    )


def test_mesh_certification_gate_reports_candidate_slo_violation_as_warning(
    monkeypatch,
) -> None:
    gate = _load_gate_module()
    candidate_product_id = "lotus-report:ClientReportEvidencePack:v1"
    monkeypatch.setattr(gate, "validate_mesh_slo_policies", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        gate,
        "evaluate_mesh_slo_violations",
        lambda **kwargs: [
            {
                "code": "mesh_slo_reconciliation_violation",
                "severity": "blocking",
                "producer_repository": "lotus-report",
                "product_id": candidate_product_id,
                "remediation": "Define and prove a reconciliation policy.",
                "policy_path": "report-slo.json",
            }
        ],
    )
    issues = []

    gate._validate_mesh_slo_policy_and_telemetry(
        telemetry_payloads={},
        catalog_path=ROOT / "generated" / "domain-product-catalog.json",
        slo_policy_path=ROOT / "platform-contracts" / "mesh-slo",
        issues=issues,
        gate_mode="blocking",
    )

    assert candidate_product_id not in gate.REQUIRED_PRODUCTS
    assert len(issues) == 1
    assert issues[0].code == "mesh_slo_reconciliation_violation"
    assert issues[0].severity == "warning"


def test_mesh_certification_gate_blocks_missing_access_policies(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)
    empty_access_policy_dir = tmp_path / "empty-access"
    empty_access_policy_dir.mkdir()

    status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        access_policy_path=empty_access_policy_dir,
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    assert status["certification_state"] == "failed"
    assert any(
        issue["code"] == "mesh_access_policy_drift" for issue in status["issues"]
    )
    assert status["source_artifacts"]["access_policy_path"] == (
        empty_access_policy_dir.as_posix()
    )


def test_mesh_certification_gate_blocks_missing_evidence_policies(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)
    empty_evidence_policy_dir = tmp_path / "empty-evidence"
    empty_evidence_policy_dir.mkdir()

    status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        evidence_policy_path=empty_evidence_policy_dir,
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    assert status["certification_state"] == "failed"
    assert status["summary"]["mesh_evidence_issue_count"] > 0
    assert any(
        issue["code"] == "mesh_evidence_policy_drift" for issue in status["issues"]
    )
    assert status["source_artifacts"]["evidence_policy_path"] == (
        empty_evidence_policy_dir.as_posix()
    )


def test_mesh_certification_gate_blocks_required_manage_product_lifecycle_drift(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)
    catalog_path = tmp_path / "domain-product-catalog.json"
    catalog = json.loads(
        (ROOT / "generated" / "domain-product-catalog.json").read_text(encoding="utf-8")
    )
    for product in catalog["products"]:
        if product["product_id"] == "lotus-manage:PortfolioActionRegister:v1":
            product["lifecycle_status"] = "deprecated"
            product["deprecation_policy"] = {
                "state": "deprecated",
                "successor_product": None,
            }
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

    status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        catalog_path=catalog_path,
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    assert status["certification_state"] == "failed"
    assert status["summary"]["mesh_lifecycle_issue_count"] == 1
    assert any(
        issue["code"] == "mesh_lifecycle_drift"
        and issue["product_id"] == "lotus-manage:PortfolioActionRegister:v1"
        for issue in status["issues"]
    )


def test_mesh_certification_gate_reports_invalid_json_snapshot(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)
    invalid_path = tmp_path / "invalid-telemetry.json"
    invalid_path.write_text("{not-json", encoding="utf-8")

    status = gate.build_mesh_certification_status(
        telemetry_paths=[*telemetry_paths, invalid_path],
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    assert status["certification_state"] == "failed"
    assert any(issue["code"] == "invalid_telemetry" for issue in status["issues"])
    assert gate._exit_code(status) == 1


def test_mesh_certification_gate_reports_dependency_graph_drift(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)
    graph_path = tmp_path / "domain-product-dependency-graph.json"
    graph_path.write_text(
        json.dumps(
            {
                "contract_id": "lotus-domain-product-dependency-graph",
                "contract_version": "1.0.0",
                "nodes": [],
                "edges": [],
            }
        ),
        encoding="utf-8",
    )

    status = gate.build_mesh_certification_status(
        telemetry_paths=telemetry_paths,
        dependency_graph_path=graph_path,
        gate_mode="blocking",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    catalog_drift_issues = [
        issue for issue in status["issues"] if issue["code"] == "catalog_drift"
    ]
    assert status["certification_state"] == "failed"
    assert len(catalog_drift_issues) == len(gate.REQUIRED_PRODUCTS)
    assert all(
        "dependency graph" in issue["remediation"] for issue in catalog_drift_issues
    )


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


def test_mesh_certification_gate_advisory_mode_tolerates_missing_snapshots() -> None:
    gate = _load_gate_module()

    status = gate.build_mesh_certification_status(
        telemetry_paths=[Path("does-not-exist")],
        gate_mode="advisory",
        generated_at_utc="2026-04-19T00:00:00Z",
        check_publication_surfaces=False,
    )

    assert status["certification_state"] == "certified_with_warnings"
    assert status["summary"]["missing_telemetry_count"] == 7
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
    rendered_enterprise_status = json.loads(
        (output_dir / "enterprise-mesh-certification-status.json").read_text(
            encoding="utf-8"
        )
    )
    markdown = (output_dir / "mesh-certification-status.md").read_text(encoding="utf-8")
    assert rendered_status["certification_state"] == "certified"
    assert rendered_enterprise_status == rendered_status
    assert rendered_issues == []
    assert "# Lotus Mesh Certification Status" in markdown
    assert "## Maturity Check Families" in markdown
    assert "lotus-core:PortfolioStateSnapshot:v1" in markdown
    assert (output_dir / "enterprise-mesh-certification-status.md").exists()
    assert (output_dir / "enterprise-mesh-certification-issues.json").exists()
    operating_report = json.loads(
        (output_dir / "enterprise-mesh-operating-report.json").read_text(
            encoding="utf-8"
        )
    )
    assert operating_report["contract_id"] == "lotus-enterprise-mesh-operating-report"
    assert operating_report["operating_state"] == "production_ready_limited_history"
    assert (output_dir / "enterprise-mesh-operating-report.md").exists()


def test_mesh_certification_gate_accepts_split_gateway_publication_modules(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)
    gateway_root = tmp_path / "lotus-gateway"
    workbench_root = tmp_path / "lotus-workbench"
    workbench_page = workbench_root / "src" / "app" / "data-products" / "page.tsx"
    workbench_api = workbench_root / "src" / "features" / "domain-products" / "api.ts"
    _write_gateway_domain_product_publication(gateway_root)
    workbench_page.parent.mkdir(parents=True)
    workbench_api.parent.mkdir(parents=True)
    workbench_page.write_text("// page exists\n", encoding="utf-8")
    workbench_api.write_text(
        'const BFF_PROXY_BASE = "/api/bff/api/v1";\n',
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
    assert "gateway_publication_drift" not in issue_codes


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
    workbench_api = workbench_root / "src" / "features" / "domain-products" / "api.ts"
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


def test_mesh_certification_gate_detects_missing_split_gateway_module(
    tmp_path: Path,
) -> None:
    gate = _load_gate_module()
    telemetry_paths = _write_required_snapshots(tmp_path)
    gateway_root = tmp_path / "lotus-gateway"
    workbench_root = tmp_path / "lotus-workbench"
    workbench_page = workbench_root / "src" / "app" / "data-products" / "page.tsx"
    workbench_api = workbench_root / "src" / "features" / "domain-products" / "api.ts"
    _write_gateway_domain_product_publication(gateway_root)
    (gateway_root / "src" / "app" / "routers" / "domain_product_trust.py").unlink()
    workbench_page.parent.mkdir(parents=True)
    workbench_api.parent.mkdir(parents=True)
    workbench_page.write_text("// page exists\n", encoding="utf-8")
    workbench_api.write_text(
        'const BFF_PROXY_BASE = "/api/bff/api/v1";\n',
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
