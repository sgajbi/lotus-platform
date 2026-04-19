from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECLARATION_DIRECTORY = ROOT / "platform-contracts" / "domain-data-products"
DEFAULT_OUTPUT_DIRECTORY = ROOT / "generated"
VALIDATOR_PATH = DEFAULT_DECLARATION_DIRECTORY / "validate_domain_data_product_contracts.py"
PRODUCT_GLOB = "*-products.v1.json"
CONSUMER_GLOB = "*-consumers.v1.json"
CATALOG_FILENAME = "domain-product-catalog.json"
CATALOG_MARKDOWN_FILENAME = "domain-product-catalog.md"
GRAPH_FILENAME = "domain-product-dependency-graph.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_platform_validator():
    spec = importlib.util.spec_from_file_location("lotus_domain_product_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load platform domain-product validator from {VALIDATOR_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _product_id(producer_repository: str, product_name: str, product_version: str) -> str:
    return f"{producer_repository}:{product_name}:{product_version}"


def _load_declaration_sources(declaration_directory: Path) -> tuple[list[tuple[Path, dict[str, Any]]], list[tuple[Path, dict[str, Any]]]]:
    producer_payloads = [
        (path, _load_json(path)) for path in sorted(declaration_directory.rglob(PRODUCT_GLOB))
    ]
    consumer_payloads = [
        (path, _load_json(path)) for path in sorted(declaration_directory.rglob(CONSUMER_GLOB))
    ]
    return producer_payloads, consumer_payloads


def _build_catalog(
    declaration_directory: Path,
    *,
    generated_at_utc: str,
) -> dict[str, Any]:
    producer_payloads, consumer_payloads = _load_declaration_sources(declaration_directory)
    products: list[dict[str, Any]] = []
    consumers: list[dict[str, Any]] = []
    produced_by_repository: dict[str, int] = defaultdict(int)
    consumed_by_repository: dict[str, int] = defaultdict(int)

    for source_path, payload in producer_payloads:
        producer_repository = payload["producer_repository"]
        for product in payload["products"]:
            produced_by_repository[producer_repository] += 1
            products.append(
                {
                    "product_id": _product_id(
                        producer_repository,
                        product["product_name"],
                        product["product_version"],
                    ),
                    "product_name": product["product_name"],
                    "product_version": product["product_version"],
                    "producer_repository": producer_repository,
                    "owner_repository": product["owner_repository"],
                    "authoritative_domain": product["authoritative_domain"],
                    "product_family": product["product_family"],
                    "lifecycle_status": product["lifecycle_status"],
                    "request_scope": product["request_scope"],
                    "temporal_scope": product["temporal_scope"],
                    "temporal_semantics_ref": product["temporal_semantics_ref"],
                    "identifier_refs": product["identifier_refs"],
                    "required_trust_metadata": product["required_trust_metadata"],
                    "freshness_policy": product["freshness_policy"],
                    "completeness_policy": product["completeness_policy"],
                    "lineage_policy": product["lineage_policy"],
                    "security_profile_ref": product["security_profile_ref"],
                    "approved_consumers": product["approved_consumers"],
                    "current_routes": product.get("current_routes", []),
                    "deprecation_policy": product["deprecation_policy"],
                    "source_path": _relative_path(source_path),
                }
            )

    for source_path, payload in consumer_payloads:
        consumer_repository = payload["consumer_repository"]
        dependencies = []
        for dependency in payload["dependencies"]:
            consumed_by_repository[consumer_repository] += 1
            dependencies.append(
                {
                    "dependency_id": _product_id(
                        dependency["producer_repository"],
                        dependency["product_name"],
                        dependency["required_product_version"],
                    ),
                    "product_name": dependency["product_name"],
                    "producer_repository": dependency["producer_repository"],
                    "required_product_version": dependency["required_product_version"],
                    "required_trust_metadata": dependency["required_trust_metadata"],
                    "migration_posture": dependency["migration_posture"],
                    "consumption_mode": dependency["consumption_mode"],
                    "business_purpose": dependency["business_purpose"],
                    "validation_lanes": dependency["validation_lanes"],
                    "failure_posture": dependency["failure_posture"],
                }
            )
        consumers.append(
            {
                "consumer_repository": consumer_repository,
                "dependency_count": len(dependencies),
                "source_path": _relative_path(source_path),
                "dependencies": sorted(
                    dependencies,
                    key=lambda dependency: (
                        dependency["producer_repository"],
                        dependency["product_name"],
                        dependency["required_product_version"],
                    ),
                ),
            }
        )

    repository_names = sorted(set(produced_by_repository) | set(consumed_by_repository))

    return {
        "contract_id": "lotus-domain-product-catalog",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0084", "RFC-0088"],
        "generated_at_utc": generated_at_utc,
        "source_declaration_directory": _relative_path(declaration_directory),
        "product_count": len(products),
        "dependency_count": sum(consumer["dependency_count"] for consumer in consumers),
        "repository_count": len(repository_names),
        "repositories": [
            {
                "repository": repository,
                "produced_product_count": produced_by_repository[repository],
                "consumed_dependency_count": consumed_by_repository[repository],
            }
            for repository in repository_names
        ],
        "products": sorted(
            products,
            key=lambda product: (
                product["producer_repository"],
                product["product_name"],
                product["product_version"],
            ),
        ),
        "consumers": sorted(consumers, key=lambda consumer: consumer["consumer_repository"]),
    }


def _build_graph(catalog: dict[str, Any]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    for repository in catalog["repositories"]:
        repository_id = f"repo:{repository['repository']}"
        nodes[repository_id] = {
            "node_id": repository_id,
            "node_type": "repository",
            "repository": repository["repository"],
        }

    for product in catalog["products"]:
        product_id = f"product:{product['product_id']}"
        producer_id = f"repo:{product['producer_repository']}"
        nodes[product_id] = {
            "node_id": product_id,
            "node_type": "domain_product",
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "product_version": product["product_version"],
            "producer_repository": product["producer_repository"],
            "product_family": product["product_family"],
            "lifecycle_status": product["lifecycle_status"],
        }
        edges.append(
            {
                "edge_type": "produces",
                "from": producer_id,
                "to": product_id,
            }
        )
        for approved_consumer in product["approved_consumers"]:
            consumer_id = f"repo:{approved_consumer}"
            nodes.setdefault(
                consumer_id,
                {
                    "node_id": consumer_id,
                    "node_type": "repository",
                    "repository": approved_consumer,
                },
            )
            edges.append(
                {
                    "edge_type": "approves_consumer",
                    "from": product_id,
                    "to": consumer_id,
                }
            )

    for consumer in catalog["consumers"]:
        consumer_id = f"repo:{consumer['consumer_repository']}"
        for dependency in consumer["dependencies"]:
            product_id = f"product:{dependency['dependency_id']}"
            edges.append(
                {
                    "edge_type": "consumes",
                    "from": consumer_id,
                    "to": product_id,
                    "consumption_mode": dependency["consumption_mode"],
                    "failure_posture": dependency["failure_posture"],
                    "validation_lanes": dependency["validation_lanes"],
                }
            )

    return {
        "contract_id": "lotus-domain-product-dependency-graph",
        "contract_version": "1.0.0",
        "governed_by_rfcs": catalog["governed_by_rfcs"],
        "generated_at_utc": catalog["generated_at_utc"],
        "source_catalog": CATALOG_FILENAME,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": [nodes[node_id] for node_id in sorted(nodes)],
        "edges": sorted(
            edges,
            key=lambda edge: (
                edge["edge_type"],
                edge["from"],
                edge["to"],
            ),
        ),
    }


def _render_catalog_markdown(catalog: dict[str, Any]) -> str:
    product_rows = [
        "| Product | Producer | Version | Family | Lifecycle | Approved Consumers | Routes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for product in catalog["products"]:
        approved_consumers = ", ".join(product["approved_consumers"])
        routes = ", ".join(product["current_routes"]) if product["current_routes"] else "Not published"
        product_rows.append(
            "| "
            f"`{product['product_name']}` | "
            f"`{product['producer_repository']}` | "
            f"`{product['product_version']}` | "
            f"`{product['product_family']}` | "
            f"`{product['lifecycle_status']}` | "
            f"{approved_consumers} | "
            f"{routes} |"
        )

    dependency_rows = [
        "| Consumer | Upstream Product | Producer | Version | Mode | Failure Posture |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for consumer in catalog["consumers"]:
        for dependency in consumer["dependencies"]:
            dependency_rows.append(
                "| "
                f"`{consumer['consumer_repository']}` | "
                f"`{dependency['product_name']}` | "
                f"`{dependency['producer_repository']}` | "
                f"`{dependency['required_product_version']}` | "
                f"`{dependency['consumption_mode']}` | "
                f"`{dependency['failure_posture']}` |"
            )

    return "\n".join(
        [
            "# Lotus Domain Product Catalog",
            "",
            "This file is generated from governed domain-data-product declarations.",
            "",
            f"- Generated at UTC: `{catalog['generated_at_utc']}`",
            f"- Source declaration directory: `{catalog['source_declaration_directory']}`",
            f"- Product count: `{catalog['product_count']}`",
            f"- Dependency count: `{catalog['dependency_count']}`",
            "",
            "## Products",
            "",
            *product_rows,
            "",
            "## Dependencies",
            "",
            *dependency_rows,
            "",
        ]
    )


def generate_discovery_artifacts(
    declaration_directory: Path = DEFAULT_DECLARATION_DIRECTORY,
    *,
    generated_at_utc: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    declaration_directory = declaration_directory.resolve()
    validator = _load_platform_validator()
    validation_issues = validator.validate_contract_directory(declaration_directory)
    if validation_issues:
        raise ValueError("Domain product declarations are invalid:\n" + "\n".join(validation_issues))

    generated_at = generated_at_utc or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    catalog = _build_catalog(declaration_directory, generated_at_utc=generated_at)
    graph = _build_graph(catalog)
    markdown = _render_catalog_markdown(catalog)
    return catalog, graph, markdown


def write_discovery_artifacts(
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
    declaration_directory: Path = DEFAULT_DECLARATION_DIRECTORY,
    *,
    generated_at_utc: str | None = None,
) -> None:
    catalog, graph, markdown = generate_discovery_artifacts(
        declaration_directory,
        generated_at_utc=generated_at_utc,
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    (output_directory / CATALOG_FILENAME).write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    (output_directory / GRAPH_FILENAME).write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    (output_directory / CATALOG_MARKDOWN_FILENAME).write_text(markdown, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate Lotus domain-product discovery catalog and dependency graph artifacts."
    )
    parser.add_argument(
        "--declaration-directory",
        default=DEFAULT_DECLARATION_DIRECTORY,
        type=Path,
        help="Directory containing governed *-products.v1.json and *-consumers.v1.json declarations.",
    )
    parser.add_argument(
        "--output-directory",
        default=DEFAULT_OUTPUT_DIRECTORY,
        type=Path,
        help="Directory where generated discovery artifacts should be written.",
    )
    parser.add_argument(
        "--generated-at-utc",
        default=None,
        help="Optional UTC timestamp to stamp into generated outputs. Useful for deterministic tests.",
    )
    args = parser.parse_args(argv)

    write_discovery_artifacts(
        args.output_directory,
        args.declaration_directory,
        generated_at_utc=args.generated_at_utc,
    )
    print(
        "Generated domain-product discovery artifacts in "
        f"{args.output_directory.resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
