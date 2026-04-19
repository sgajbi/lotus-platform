from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "automation" / "domain_product_discovery.py"
DECLARATION_DIRECTORY = ROOT / "platform-contracts" / "domain-data-products"
SOURCE_MANIFEST_PATH = DECLARATION_DIRECTORY / "domain-product-source-manifest.v1.json"
GENERATED_DIRECTORY = ROOT / "generated"
CHECKED_IN_GENERATED_AT = "2026-04-19T00:00:00Z"


def _load_generator_module():
    spec = importlib.util.spec_from_file_location("domain_product_discovery_generator", GENERATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_domain_product_discovery_generator_builds_catalog_from_governed_declarations() -> None:
    generator = _load_generator_module()

    catalog, graph, markdown = generator.generate_discovery_artifacts(
        DECLARATION_DIRECTORY,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    product_ids = {product["product_id"] for product in catalog["products"]}
    dependency_edges = {
        (consumer["consumer_repository"], dependency["dependency_id"])
        for consumer in catalog["consumers"]
        for dependency in consumer["dependencies"]
    }

    assert catalog["contract_id"] == "lotus-domain-product-catalog"
    assert catalog["governed_by_rfcs"] == ["RFC-0084", "RFC-0088"]
    assert catalog["generated_at_utc"] == CHECKED_IN_GENERATED_AT
    assert catalog["source_manifest_path"] == "platform-contracts/domain-data-products/domain-product-source-manifest.v1.json"
    assert catalog["source_manifest"]["repositories"][0]["repository"] == "lotus-core"
    assert "lotus-core:PortfolioStateSnapshot:v1" in product_ids
    assert "lotus-performance:ReturnsSeriesBundle:v1" in product_ids
    assert "lotus-risk:RiskMetricsReport:v1" in product_ids
    assert ("lotus-risk", "lotus-performance:ReturnsSeriesBundle:v1") in dependency_edges
    assert ("lotus-performance", "lotus-core:PortfolioTimeseriesInput:v1") in dependency_edges
    assert catalog["product_count"] == len(catalog["products"])
    assert catalog["dependency_count"] == sum(
        consumer["dependency_count"] for consumer in catalog["consumers"]
    )

    assert graph["contract_id"] == "lotus-domain-product-dependency-graph"
    assert graph["source_catalog"] == "domain-product-catalog.json"
    assert any(
        edge["edge_type"] == "consumes"
        and edge["from"] == "repo:lotus-risk"
        and edge["to"] == "product:lotus-performance:ReturnsSeriesBundle:v1"
        for edge in graph["edges"]
    )
    assert "| `ReturnsSeriesBundle` | `lotus-performance` | `v1` |" in markdown
    assert "| `lotus-risk` | `ReturnsSeriesBundle` | `lotus-performance` | `v1` |" in markdown


def test_domain_product_source_manifest_tracks_repo_native_rollout_without_reading_active_branches() -> None:
    generator = _load_generator_module()

    assert generator.validate_source_manifest(SOURCE_MANIFEST_PATH) == []

    manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    by_repository = {entry["repository"]: entry for entry in manifest["repositories"]}

    assert by_repository["lotus-performance"]["repo_native_status"] == "implemented"
    assert by_repository["lotus-risk"]["repo_native_status"] == "implemented"
    assert by_repository["lotus-advise"]["catalog_inclusion"] == "pending_platform_declaration"
    assert by_repository["lotus-core"]["repo_native_status"] == "pending_clean_slate_confirmation"


def test_domain_product_discovery_generator_writes_json_and_markdown_outputs(tmp_path: Path) -> None:
    generator = _load_generator_module()

    generator.write_discovery_artifacts(
        tmp_path,
        DECLARATION_DIRECTORY,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    catalog = json.loads((tmp_path / "domain-product-catalog.json").read_text(encoding="utf-8"))
    graph = json.loads((tmp_path / "domain-product-dependency-graph.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "domain-product-catalog.md").read_text(encoding="utf-8")

    assert catalog["product_count"] > 0
    assert graph["edge_count"] >= catalog["dependency_count"]
    assert "This file is generated from governed domain-data-product declarations." in markdown


def test_checked_in_domain_product_discovery_outputs_are_not_stale(tmp_path: Path) -> None:
    generator = _load_generator_module()

    generator.write_discovery_artifacts(
        tmp_path,
        DECLARATION_DIRECTORY,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    for artifact_name in (
        "domain-product-catalog.json",
        "domain-product-dependency-graph.json",
        "domain-product-catalog.md",
    ):
        assert (GENERATED_DIRECTORY / artifact_name).read_text(encoding="utf-8") == (
            tmp_path / artifact_name
        ).read_text(encoding="utf-8")
