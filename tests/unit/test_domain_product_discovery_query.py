from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DISCOVERY_PATH = ROOT / "automation" / "domain_product_discovery.py"
QUERY_PATH = ROOT / "automation" / "query_domain_product_discovery.py"
CATALOG_PATH = ROOT / "generated" / "domain-product-catalog.json"
GRAPH_PATH = ROOT / "generated" / "domain-product-dependency-graph.json"


def _load_module(path: Path, module_name: str):
    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_domain_product_query_filters_by_producer_and_approved_consumer() -> None:
    discovery = _load_module(DISCOVERY_PATH, "domain_product_discovery_query_test")
    catalog = discovery.load_catalog(CATALOG_PATH)

    products = discovery.find_products(
        catalog,
        producer_repository="lotus-core",
        approved_consumer="lotus-risk",
        search="Portfolio",
    )

    product_ids = {product["product_id"] for product in products}
    assert "lotus-core:PortfolioStateSnapshot:v1" in product_ids
    assert all(product["producer_repository"] == "lotus-core" for product in products)
    assert all("lotus-risk" in product["approved_consumers"] for product in products)


def test_domain_product_query_filters_by_lifecycle_status() -> None:
    discovery = _load_module(DISCOVERY_PATH, "domain_product_discovery_lifecycle_test")
    catalog = discovery.load_catalog(CATALOG_PATH)

    products = discovery.find_products(catalog, lifecycle_status="active")

    assert products
    assert all(product["lifecycle_status"] == "active" for product in products)


def test_domain_product_query_returns_empty_list_for_search_miss() -> None:
    discovery = _load_module(DISCOVERY_PATH, "domain_product_discovery_search_test")
    catalog = discovery.load_catalog(CATALOG_PATH)

    products = discovery.find_products(catalog, search="does-not-exist-in-catalog")

    assert products == []


def test_domain_product_query_requires_full_identity_or_product_id() -> None:
    discovery = _load_module(DISCOVERY_PATH, "domain_product_discovery_product_test")
    catalog = discovery.load_catalog(CATALOG_PATH)

    product = discovery.get_product(
        catalog,
        producer_repository="lotus-performance",
        product_name="ReturnsSeriesBundle",
        product_version="v1",
    )

    assert product["product_id"] == "lotus-performance:ReturnsSeriesBundle:v1"
    assert product["required_trust_metadata"]


def test_domain_product_query_returns_consumer_dependencies() -> None:
    discovery = _load_module(DISCOVERY_PATH, "domain_product_discovery_consumer_test")
    catalog = discovery.load_catalog(CATALOG_PATH)

    consumer = discovery.get_consumer_dependencies(
        catalog, consumer_repository="lotus-risk"
    )

    dependency_ids = {
        dependency["dependency_id"] for dependency in consumer["dependencies"]
    }
    assert "lotus-performance:ReturnsSeriesBundle:v1" in dependency_ids
    assert consumer["dependency_count"] == len(consumer["dependencies"])


def test_domain_product_query_returns_graph_neighborhood() -> None:
    discovery = _load_module(DISCOVERY_PATH, "domain_product_discovery_graph_test")
    graph = discovery.load_dependency_graph(GRAPH_PATH)

    neighborhood = discovery.get_graph_neighborhood(graph, node_id="repo:lotus-risk")

    assert neighborhood["node"]["repository"] == "lotus-risk"
    assert any(edge["edge_type"] == "consumes" for edge in neighborhood["edges"])
    assert any(
        node["node_id"] == "repo:lotus-risk" for node in neighborhood["connected_nodes"]
    )


def test_domain_product_query_cli_outputs_machine_readable_json(capsys) -> None:
    query = _load_module(QUERY_PATH, "query_domain_product_discovery_cli_test")

    exit_code = query.main(
        [
            "--catalog",
            str(CATALOG_PATH),
            "list-products",
            "--producer",
            "lotus-performance",
            "--approved-consumer",
            "lotus-risk",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    product_ids = {product["product_id"] for product in payload["products"]}
    assert exit_code == 0
    assert payload["product_count"] >= 1
    assert "lotus-performance:ReturnsSeriesBundle:v1" in product_ids


def test_domain_product_query_cli_reports_unknown_product(capsys) -> None:
    query = _load_module(QUERY_PATH, "query_domain_product_discovery_error_test")

    exit_code = query.main(
        [
            "--catalog",
            str(CATALOG_PATH),
            "product",
            "--product-id",
            "lotus-core:Missing:v1",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "domain product not found: lotus-core:Missing:v1" in captured.out
