from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "automation" / "domain_product_discovery.py"
DECLARATION_DIRECTORY = ROOT / "platform-contracts" / "domain-data-products"
SOURCE_MANIFEST_PATH = DECLARATION_DIRECTORY / "domain-product-source-manifest.v1.json"
GENERATED_DIRECTORY = ROOT / "generated"
CHECKED_IN_GENERATED_AT = "2026-06-24T00:00:00Z"


def _load_generator_module():
    spec = importlib.util.spec_from_file_location(
        "domain_product_discovery_generator", GENERATOR_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_domain_product_discovery_generator_builds_catalog_from_governed_declarations() -> (
    None
):
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
    assert (
        catalog["source_manifest_path"]
        == "platform-contracts/domain-data-products/domain-product-source-manifest.v1.json"
    )
    assert catalog["source_manifest"]["repositories"][0]["repository"] == "lotus-core"
    assert "lotus-core:PortfolioStateSnapshot:v1" in product_ids
    assert "lotus-performance:ReturnsSeriesBundle:v1" in product_ids
    assert "lotus-risk:RiskMetricsReport:v1" in product_ids
    assert (
        "lotus-risk",
        "lotus-performance:ReturnsSeriesBundle:v1",
    ) in dependency_edges
    assert (
        "lotus-performance",
        "lotus-core:PortfolioTimeseriesInput:v1",
    ) in dependency_edges
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
    assert (
        "| `lotus-risk` | `ReturnsSeriesBundle` | `lotus-performance` | `v1` |"
        in markdown
    )


def test_domain_product_source_manifest_promotes_repo_native_sources_to_catalog() -> (
    None
):
    generator = _load_generator_module()

    assert generator.validate_source_manifest(SOURCE_MANIFEST_PATH) == []

    manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    by_repository = {entry["repository"]: entry for entry in manifest["repositories"]}

    assert by_repository["lotus-performance"]["repo_native_status"] == "implemented"
    assert by_repository["lotus-performance"]["source_mode"] == "repo_native"
    assert by_repository["lotus-performance"]["catalog_inclusion"] == "included"
    assert by_repository["lotus-risk"]["repo_native_status"] == "implemented"
    assert by_repository["lotus-risk"]["source_mode"] == "repo_native"
    assert by_repository["lotus-risk"]["catalog_inclusion"] == "included"
    assert by_repository["lotus-advise"]["source_mode"] == "repo_native"
    assert by_repository["lotus-advise"]["catalog_inclusion"] == "included"
    assert by_repository["lotus-report"]["repo_native_status"] == "implemented"
    assert by_repository["lotus-report"]["source_mode"] == "repo_native"
    assert by_repository["lotus-report"]["catalog_inclusion"] == "included"
    assert by_repository["lotus-manage"]["repo_native_status"] == "implemented"
    assert by_repository["lotus-manage"]["source_mode"] == "repo_native"
    assert by_repository["lotus-manage"]["catalog_inclusion"] == "included"
    assert by_repository["lotus-idea"]["repo_native_status"] == "implemented"
    assert by_repository["lotus-idea"]["source_mode"] == "repo_native"
    assert by_repository["lotus-idea"]["catalog_inclusion"] == "included"
    assert by_repository["lotus-core"]["repo_native_status"] == "implemented"
    assert by_repository["lotus-core"]["source_mode"] == "repo_native"
    assert by_repository["lotus-core"]["catalog_inclusion"] == "included"


def test_domain_product_source_manifest_rejects_missing_repo_native_source(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()
    manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["repositories"] = [
        {
            "repository": "lotus-missing",
            "source_mode": "repo_native",
            "catalog_inclusion": "included",
            "repo_native_status": "implemented",
            "repo_native_declaration_path": "contracts/domain-data-products",
            "platform_declaration_paths": [],
            "notes": "Deliberately missing source for validation coverage.",
        }
    ]
    manifest_path = tmp_path / "domain-product-source-manifest.v1.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    issues = generator.validate_source_manifest(manifest_path)

    assert any(
        "repo-native declaration directory does not exist" in issue for issue in issues
    )


def test_domain_product_discovery_uses_repo_native_source_paths() -> None:
    generator = _load_generator_module()

    catalog, _, _ = generator.generate_discovery_artifacts(
        DECLARATION_DIRECTORY,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    source_paths = {product["source_path"] for product in catalog["products"]}
    consumer_source_paths = {
        consumer["source_path"] for consumer in catalog["consumers"]
    }

    assert (
        catalog["source_declaration_directory"]
        == "federated:domain-product-source-manifest"
    )
    assert any(
        source_path.endswith(
            "lotus-advise/contracts/domain-data-products/lotus-advise-products.v1.json"
        )
        for source_path in source_paths
    )
    assert any(
        source_path.endswith(
            "lotus-report/contracts/domain-data-products/lotus-report-consumers.v1.json"
        )
        for source_path in consumer_source_paths
    )
    assert any(
        source_path.endswith(
            "lotus-manage/contracts/domain-data-products/lotus-manage-consumers.v1.json"
        )
        for source_path in consumer_source_paths
    )
    assert not any("_federated/" in source_path for source_path in source_paths)
    assert not any(
        "_federated/" in source_path for source_path in consumer_source_paths
    )


def test_domain_product_discovery_normalizes_federated_checkout_paths() -> None:
    generator = _load_generator_module()
    federated_path = (
        ROOT
        / "_federated"
        / "lotus-advise"
        / "contracts"
        / "domain-data-products"
        / "lotus-advise-products.v1.json"
    )

    assert generator._relative_path(federated_path) == (
        "lotus-advise/contracts/domain-data-products/lotus-advise-products.v1.json"
    )


def test_domain_product_discovery_generator_writes_json_and_markdown_outputs(
    tmp_path: Path,
) -> None:
    generator = _load_generator_module()

    generator.write_discovery_artifacts(
        tmp_path,
        DECLARATION_DIRECTORY,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    catalog = json.loads(
        (tmp_path / "domain-product-catalog.json").read_text(encoding="utf-8")
    )
    graph = json.loads(
        (tmp_path / "domain-product-dependency-graph.json").read_text(encoding="utf-8")
    )
    markdown = (tmp_path / "domain-product-catalog.md").read_text(encoding="utf-8")

    assert catalog["product_count"] > 0
    assert graph["edge_count"] >= catalog["dependency_count"]
    assert (
        "This file is generated from governed domain-data-product declarations."
        in markdown
    )


def test_checked_in_domain_product_discovery_outputs_are_not_stale(
    tmp_path: Path,
) -> None:
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


def test_domain_product_discovery_check_reports_stale_outputs(tmp_path: Path) -> None:
    generator = _load_generator_module()

    generator.write_discovery_artifacts(
        tmp_path,
        DECLARATION_DIRECTORY,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )
    (tmp_path / "domain-product-catalog.md").write_text("stale\n", encoding="utf-8")

    issues = generator.check_discovery_artifacts(
        tmp_path,
        DECLARATION_DIRECTORY,
        generated_at_utc=CHECKED_IN_GENERATED_AT,
    )

    assert issues == [
        f"{tmp_path / 'domain-product-catalog.md'}: generated discovery artifact is stale"
    ]
