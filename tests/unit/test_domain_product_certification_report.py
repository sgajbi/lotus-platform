from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DISCOVERY_PATH = ROOT / "automation" / "domain_product_discovery.py"
CERTIFICATION_PATH = ROOT / "automation" / "domain_product_certification.py"
CATALOG_PATH = ROOT / "generated" / "domain-product-catalog.json"
GRAPH_PATH = ROOT / "generated" / "domain-product-dependency-graph.json"
CERTIFICATION_REPORT_PATH = (
    ROOT / "generated" / "domain-product-certification-report.json"
)
CERTIFICATION_MARKDOWN_PATH = (
    ROOT / "generated" / "domain-product-certification-report.md"
)
CHECKED_IN_GENERATED_AT = "2026-04-19T00:00:00Z"


def _load_discovery_module():
    spec = importlib.util.spec_from_file_location(
        "domain_product_certification", DISCOVERY_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_certification_module():
    import sys

    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    spec = importlib.util.spec_from_file_location(
        "domain_product_certification", CERTIFICATION_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_domain_product_certification_report_certifies_current_catalog_and_graph() -> (
    None
):
    discovery = _load_discovery_module()
    certification = _load_certification_module()
    catalog = discovery.load_catalog(CATALOG_PATH)
    graph = discovery.load_dependency_graph(GRAPH_PATH)

    report = certification.build_certification_report(
        catalog,
        graph,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    assert report["contract_id"] == "lotus-domain-product-certification-report"
    assert report["governed_by_rfcs"] == ["RFC-0084", "RFC-0087", "RFC-0088"]
    assert report["summary"]["certification_state"] == "certified"
    assert report["summary"]["product_count"] == catalog["product_count"]
    assert report["summary"]["dependency_count"] == catalog["dependency_count"]
    assert report["summary"]["issue_count"] == 0
    assert report["source_manifest_posture"]["included_repositories"] == [
        "lotus-core",
        "lotus-performance",
        "lotus-risk",
        "lotus-advise",
        "lotus-report",
        "lotus-manage",
    ]
    assert report["source_manifest_posture"]["pending_repositories"] == []


def test_domain_product_certification_report_checks_consumer_producer_reciprocity() -> (
    None
):
    discovery = _load_discovery_module()
    certification = _load_certification_module()
    catalog = discovery.load_catalog(CATALOG_PATH)
    graph = discovery.load_dependency_graph(GRAPH_PATH)

    report = certification.build_certification_report(catalog, graph)

    risk_consumer = next(
        consumer
        for consumer in report["consumer_certifications"]
        if consumer["consumer_repository"] == "lotus-risk"
    )
    returns_dependency = next(
        dependency
        for dependency in risk_consumer["dependencies"]
        if dependency["dependency_id"] == "lotus-performance:ReturnsSeriesBundle:v1"
    )

    assert risk_consumer["certification_state"] == "certified"
    assert returns_dependency["checks"]["product_exists"] is True
    assert returns_dependency["checks"]["approved_by_producer"] is True
    assert returns_dependency["checks"]["required_metadata_subset_of_product"] is True
    assert returns_dependency["checks"]["graph_consume_edge_present"] is True


def test_domain_product_certification_report_flags_broken_dependency() -> None:
    discovery = _load_discovery_module()
    certification = _load_certification_module()
    catalog = discovery.load_catalog(CATALOG_PATH)
    graph = discovery.load_dependency_graph(GRAPH_PATH)
    broken_catalog = json.loads(json.dumps(catalog))
    broken_catalog["consumers"][0]["dependencies"][0]["dependency_id"] = (
        "lotus-core:Missing:v1"
    )

    report = certification.build_certification_report(broken_catalog, graph)

    assert report["summary"]["certification_state"] == "attention_required"
    assert any(
        issue["code"] == "missing_dependency_product" for issue in report["issues"]
    )
    assert any(
        issue["code"] == "missing_graph_consume_edge" for issue in report["issues"]
    )


def test_domain_product_dependency_certification_reports_dependency_contract_gaps() -> (
    None
):
    certification = _load_certification_module()
    dependency = {
        "dependency_id": "lotus-performance:ReturnsSeriesBundle:v1",
        "producer_repository": "lotus-performance",
        "product_name": "ReturnsSeriesBundle",
        "required_product_version": "v1",
        "required_trust_metadata": ["freshness", "lineage", "unsupported"],
        "validation_lanes": [],
        "failure_posture": "",
    }
    product = {
        "product_id": "lotus-performance:ReturnsSeriesBundle:v1",
        "approved_consumers": ["lotus-risk"],
        "required_trust_metadata": ["freshness", "lineage"],
    }

    dependency_certification, issues = certification._build_dependency_certification(
        consumer_repository="lotus-report",
        dependency=dependency,
        product=product,
        graph_consume_edges=set(),
    )

    assert dependency_certification["certification_state"] == "attention_required"
    assert dependency_certification["checks"] == {
        "product_exists": True,
        "approved_by_producer": False,
        "required_metadata_subset_of_product": False,
        "graph_consume_edge_present": False,
        "validation_lanes_declared": False,
        "failure_posture_declared": False,
    }
    assert {issue["code"] for issue in issues} == {
        "consumer_not_approved",
        "consumer_requires_unpublished_trust_metadata",
        "missing_graph_consume_edge",
        "missing_dependency_validation_lanes",
        "missing_dependency_failure_posture",
    }


def test_domain_product_certification_report_markdown_is_customer_readable() -> None:
    discovery = _load_discovery_module()
    certification = _load_certification_module()
    catalog = discovery.load_catalog(CATALOG_PATH)
    graph = discovery.load_dependency_graph(GRAPH_PATH)
    report = certification.build_certification_report(
        catalog,
        graph,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    markdown = certification.render_certification_report_markdown(report)

    assert "# Lotus Domain Product Certification Report" in markdown
    assert "Certification state: `certified`" in markdown
    assert "| `ReturnsSeriesBundle` | `lotus-performance` | `certified` |" in markdown
    assert (
        "| `AdvisoryProposalLifecycleRecord` | `lotus-advise` | `certified` |"
        in markdown
    )
    assert "| `lotus-risk` | `certified` | `6` | `0` |" in markdown
    assert "| `lotus-report` | `certified` | `2` | `0` |" in markdown


def test_checked_in_domain_product_certification_outputs_are_current(
    tmp_path: Path,
) -> None:
    certification = _load_certification_module()

    certification.write_certification_report(
        tmp_path,
        catalog_path=CATALOG_PATH,
        graph_path=GRAPH_PATH,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    assert CERTIFICATION_REPORT_PATH.read_text(encoding="utf-8") == (
        tmp_path / "domain-product-certification-report.json"
    ).read_text(encoding="utf-8")
    assert CERTIFICATION_MARKDOWN_PATH.read_text(encoding="utf-8") == (
        tmp_path / "domain-product-certification-report.md"
    ).read_text(encoding="utf-8")
