from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COLLECTOR_PATH = ROOT / "automation" / "collect_trust_telemetry.py"
GENERATED_AT_UTC = "2026-04-20T00:00:00Z"
REQUIRED_PRODUCT_METADATA = {
    "lotus-core:PortfolioStateSnapshot:v1": {
        "tenant_id": "TENANT_PRIVATE_BANKING_DEMO",
        "generated_at": GENERATED_AT_UTC,
        "as_of_date": "2026-04-20",
        "restatement_version": "restatement:2026-04-20:0",
        "reconciliation_status": "reconciled",
        "data_quality_status": "quality_passed",
        "latest_evidence_timestamp": GENERATED_AT_UTC,
        "source_batch_fingerprint": "sha256:portfolio-state-snapshot-test",
        "snapshot_id": "PB_SG_GLOBAL_BAL_001:2026-04-20",
        "content_hash": "sha256:" + "1" * 64,
        "policy_version": "portfolio-state-snapshot-policy.v1",
        "correlation_id": "corr-lotus-core",
    },
    "lotus-core:DpmSourceReadiness:v1": {
        "tenant_id": "TENANT_PRIVATE_BANKING_DEMO",
        "generated_at": GENERATED_AT_UTC,
        "as_of_date": "2026-04-20",
        "restatement_version": "restatement:2026-04-20:0",
        "reconciliation_status": "reconciled",
        "data_quality_status": "quality_passed",
        "latest_evidence_timestamp": GENERATED_AT_UTC,
        "source_batch_fingerprint": "sha256:dpm-source-readiness-test",
        "snapshot_id": "dpm-source-readiness-test",
        "content_hash": "sha256:" + "2" * 64,
        "policy_version": "dpm-source-readiness-policy.v1",
        "correlation_id": "corr-lotus-core-dpm",
    },
    "lotus-performance:ReturnsSeriesBundle:v1": {
        "generated_at": GENERATED_AT_UTC,
        "as_of_date": "2026-04-20",
        "correlation_id": "corr-lotus-performance",
    },
    "lotus-risk:RiskMetricsReport:v1": {
        "as_of_date": "2026-04-20",
        "lineage_version": "risk-audit-lineage.v1",
        "request_fingerprint": "sha256:risk-request-test",
        "source_services": ["lotus-risk", "lotus-performance", "lotus-core"],
        "upstream_request_fingerprints": {
            "lotus-performance:/integration/returns/series": "sha256:returns-test",
            "lotus-core:/query/portfolio-state": "sha256:portfolio-state-test",
        },
        "benchmark_context": "MSCI_ACWI_PRIVATE_BANKING_DEMO",
        "risk_free_context": "SGD_OVERNIGHT_DEMO",
        "correlation_id": "rfc-0087-lotus-risk-risk-metrics",
    },
    "lotus-advise:AdvisoryProposalLifecycleRecord:v1": {
        "generated_at": GENERATED_AT_UTC,
        "correlation_id": "corr-lotus-advise",
    },
    "lotus-advise:AdvisoryProposalMemoEvidencePack:v1": {
        "generated_at": GENERATED_AT_UTC,
        "content_hash": "sha256:advisory-proposal-memo-evidence-pack-test",
        "correlation_id": "corr-lotus-advise-memo",
    },
    "lotus-report:ClientReportEvidencePack:v1": {
        "tenant_id": "TENANT_PRIVATE_BANKING_DEMO",
        "tenant_admission": "caller_admitted",
        "generated_at": GENERATED_AT_UTC,
        "as_of_date": "2026-04-20",
        "reconciliation_status": "reconciled",
        "reconciliation_reason_code": "policy_evidence_verified",
        "data_quality_status": "quality_passed",
        "lineage_bundle_id": "lineage:lotus-report:client-report-evidence-pack:test",
        "correlation_id": "corr-lotus-report",
    },
    "lotus-manage:PortfolioActionRegister:v1": {
        "tenant_id": "TENANT_PRIVATE_BANKING_DEMO",
        "generated_at": GENERATED_AT_UTC,
        "as_of_date": "2026-04-20",
        "reconciliation_status": "reconciled",
        "data_quality_status": "quality_passed",
        "lineage_bundle_id": "lineage:lotus-manage:portfolio-action-register:test",
        "source_batch_fingerprint": "sha256:portfolio-action-register-test",
        "producer_generated_at": GENERATED_AT_UTC,
        "evidence_as_of_date": "2026-04-20",
        "temporal_identity_status": "available",
        "correlation_id": "corr-lotus-manage",
    },
}


def _load_collector_module():
    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    spec = importlib.util.spec_from_file_location(
        "collect_trust_telemetry_test", COLLECTOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _snapshot(product_id: str, *, emitted_at_utc: str = GENERATED_AT_UTC) -> dict:
    producer_repository, product_name, product_version = product_id.split(":")
    observed_metadata = {
        "product_name": product_name,
        "product_version": product_version,
        **REQUIRED_PRODUCT_METADATA[product_id],
    }
    return {
        "contract_id": "lotus-domain-product-trust-telemetry-snapshot",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0087"],
        "emitted_at_utc": emitted_at_utc,
        "product_id": product_id,
        "producer_repository": producer_repository,
        "product_name": product_name,
        "product_version": product_version,
        "source_repository": producer_repository,
        "runtime_source": {
            "emission_mode": "deterministic_test_runtime",
            "service_version": "test",
            "environment": "local",
        },
        "freshness": {
            "freshness_class": "daily",
            "freshness_state": "current",
            "evaluated_at_utc": GENERATED_AT_UTC,
            "observed_at_utc": emitted_at_utc,
            "age_seconds": 0,
            "max_allowed_age_seconds": 86400,
        },
        "completeness_status": "complete",
        "reconciliation_status": "reconciled",
        "data_quality_status": "quality_passed",
        "lineage": {
            "lineage_materialized": True,
            "lineage_bundle_id": f"lineage:{producer_repository}:{product_name}:test",
            "evidence_access_class": "customer_consumable",
            "evidence_uris": [f"{producer_repository}://evidence/{product_name}/test"],
        },
        "blocking": {"blocked": False},
        "observed_trust_metadata": observed_metadata,
        "evidence": {
            "correlation_id": f"corr-{producer_repository}",
            "validation_lanes": ["feature", "pr-merge"],
            "source_event_id": f"source-event:{producer_repository}:{product_name}:test",
            "source_artifact_uri": f"{producer_repository}://trust-telemetry/{product_name}.json",
        },
    }


def _write_snapshot(directory: Path, product_id: str, *, filename: str | None = None) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    snapshot_path = directory / (filename or f"{product_id.replace(':', '-')}.json")
    snapshot_path.write_text(json.dumps(_snapshot(product_id), indent=2), encoding="utf-8")
    return snapshot_path


def _write_required_static_fixtures(directory: Path) -> None:
    for product_id in REQUIRED_PRODUCT_METADATA:
        _write_snapshot(directory, product_id)


def test_trust_telemetry_collection_prefers_runtime_over_static_fixture(
    tmp_path: Path,
) -> None:
    collector = _load_collector_module()
    fixture_dir = tmp_path / "fixtures"
    runtime_dir = tmp_path / "runtime"
    output_dir = tmp_path / "collection"
    _write_required_static_fixtures(fixture_dir)
    runtime_path = _write_snapshot(
        runtime_dir,
        "lotus-performance:ReturnsSeriesBundle:v1",
        filename="runtime-returns.json",
    )

    manifest = collector.collect_trust_telemetry(
        runtime_directories=[runtime_dir],
        fixture_directories=[fixture_dir],
        output_directory=output_dir,
        generated_at_utc=GENERATED_AT_UTC,
    )

    snapshots = {entry["product_id"]: entry for entry in manifest["snapshots"]}
    returns_entry = snapshots["lotus-performance:ReturnsSeriesBundle:v1"]
    assert returns_entry["selected_source_mode"] == "runtime"
    assert returns_entry["source_path"] == runtime_path.as_posix()
    assert returns_entry["fixture_fallback"] is False
    assert manifest["summary"]["runtime_snapshot_count"] == 1
    assert manifest["summary"]["static_fixture_snapshot_count"] == 7
    assert manifest["summary"]["error_count"] == 0
    assert Path(returns_entry["collected_path"]).exists()


def test_trust_telemetry_collection_marks_fixture_fallback_explicitly(
    tmp_path: Path,
) -> None:
    collector = _load_collector_module()
    fixture_dir = tmp_path / "fixtures"
    output_dir = tmp_path / "collection"
    _write_required_static_fixtures(fixture_dir)

    manifest = collector.collect_trust_telemetry(
        runtime_directories=[tmp_path / "empty-runtime"],
        fixture_directories=[fixture_dir],
        output_directory=output_dir,
        generated_at_utc=GENERATED_AT_UTC,
    )

    assert manifest["summary"]["runtime_snapshot_count"] == 0
    assert manifest["summary"]["static_fixture_snapshot_count"] == 8
    assert all(entry["fixture_fallback"] is True for entry in manifest["snapshots"])
    assert all(
        entry["fallback_reason"] == "No runtime telemetry snapshot was available for this product."
        for entry in manifest["snapshots"]
    )


def test_trust_telemetry_collection_rejects_missing_required_metadata(
    tmp_path: Path,
) -> None:
    collector = _load_collector_module()
    fixture_dir = tmp_path / "fixtures"
    output_dir = tmp_path / "collection"
    _write_required_static_fixtures(fixture_dir)
    core_path = next(fixture_dir.glob("lotus-core-PortfolioStateSnapshot-v1.json"))
    core_snapshot = json.loads(core_path.read_text(encoding="utf-8"))
    core_snapshot["observed_trust_metadata"] = {}
    core_path.write_text(json.dumps(core_snapshot), encoding="utf-8")

    manifest = collector.collect_trust_telemetry(
        runtime_directories=[tmp_path / "empty-runtime"],
        fixture_directories=[fixture_dir],
        output_directory=output_dir,
        generated_at_utc=GENERATED_AT_UTC,
    )

    assert all(
        snapshot["product_id"] != "lotus-core:PortfolioStateSnapshot:v1"
        for snapshot in manifest["snapshots"]
    )
    assert manifest["summary"]["missing_required_product_count"] == 1
    assert manifest["summary"]["missing_candidate_product_count"] == 1
    invalid_details = [
        issue["detail"]
        for issue in manifest["issues"]
        if issue["code"] == "invalid_snapshot"
        and issue["product_id"] == "lotus-core:PortfolioStateSnapshot:v1"
    ]
    assert len(invalid_details) == 14
    assert all("missing required product field" in detail for detail in invalid_details)


def test_trust_telemetry_collection_ignores_adjacent_non_snapshot_json(
    tmp_path: Path,
) -> None:
    collector = _load_collector_module()
    fixture_dir = tmp_path / "fixtures"
    output_dir = tmp_path / "collection"
    _write_required_static_fixtures(fixture_dir)
    (fixture_dir / "aggregate-proof.json").write_text(
        json.dumps(
            {
                "contract_id": "lotus-idea-runtime-trust-telemetry-product-coverage",
                "repository": "lotus-idea",
                "coverage_status": "incomplete",
            }
        ),
        encoding="utf-8",
    )

    manifest = collector.collect_trust_telemetry(
        runtime_directories=[tmp_path / "empty-runtime"],
        fixture_directories=[fixture_dir],
        output_directory=output_dir,
        generated_at_utc=GENERATED_AT_UTC,
    )

    ignored = [
        issue
        for issue in manifest["issues"]
        if issue["code"] == "ignored_non_snapshot_json"
    ]
    assert len(ignored) == 1
    assert ignored[0]["severity"] == "info"
    assert manifest["summary"]["static_fixture_snapshot_count"] == 8
    assert manifest["summary"]["error_count"] == 0


def test_trust_telemetry_collection_reports_missing_required_products(
    tmp_path: Path,
) -> None:
    collector = _load_collector_module()
    fixture_dir = tmp_path / "fixtures"
    output_dir = tmp_path / "collection"
    _write_snapshot(fixture_dir, "lotus-core:PortfolioStateSnapshot:v1")

    manifest = collector.collect_trust_telemetry(
        runtime_directories=[tmp_path / "empty-runtime"],
        fixture_directories=[fixture_dir],
        output_directory=output_dir,
        generated_at_utc=GENERATED_AT_UTC,
    )

    missing_products = {
        issue["product_id"]
        for issue in manifest["issues"]
        if issue["code"] == "missing_required_product"
    }
    assert missing_products == {
            "lotus-advise:AdvisoryProposalLifecycleRecord:v1",
            "lotus-advise:AdvisoryProposalMemoEvidencePack:v1",
            "lotus-manage:PortfolioActionRegister:v1",
            "lotus-core:DpmSourceReadiness:v1",
            "lotus-performance:ReturnsSeriesBundle:v1",
            "lotus-risk:RiskMetricsReport:v1",
        }
    assert manifest["summary"]["error_count"] == 6
    missing_candidates = {
        issue["product_id"]
        for issue in manifest["issues"]
        if issue["code"] == "missing_candidate_product"
    }
    assert missing_candidates == {
        "lotus-report:ClientReportEvidencePack:v1",
        "lotus-idea:IdeaCandidate:v1",
    }
    assert manifest["summary"]["missing_candidate_product_count"] == 2


def test_trust_telemetry_collection_cli_writes_manifest(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "fixtures"
    output_dir = tmp_path / "collection"
    _write_required_static_fixtures(fixture_dir)

    result = subprocess.run(
        [
            sys.executable,
            str(COLLECTOR_PATH),
            "--fixture-directory",
            str(fixture_dir),
            "--runtime-directory",
            str(tmp_path / "empty-runtime"),
            "--output-directory",
            str(output_dir),
            "--generated-at-utc",
            GENERATED_AT_UTC,
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "8 static fixture fallback(s)" in result.stdout
    manifest = json.loads(
        (output_dir / "trust-telemetry-collection-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["contract_id"] == "lotus-trust-telemetry-collection-manifest"
