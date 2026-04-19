from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from domain_product_discovery import (
    DEFAULT_CATALOG_PATH,
    DEFAULT_GRAPH_PATH,
    find_products,
    get_consumer_dependencies,
    get_graph_neighborhood,
    get_product,
    load_catalog,
    load_dependency_graph,
)


def _emit_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _product_summary(product: dict[str, Any]) -> dict[str, Any]:
    return {
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "product_version": product["product_version"],
        "producer_repository": product["producer_repository"],
        "authoritative_domain": product["authoritative_domain"],
        "product_family": product["product_family"],
        "lifecycle_status": product["lifecycle_status"],
        "approved_consumers": product["approved_consumers"],
        "required_trust_metadata": product["required_trust_metadata"],
        "current_routes": product["current_routes"],
        "source_path": product["source_path"],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Query Lotus generated domain-product discovery artifacts without changing platform "
            "catalog or graph source of truth."
        )
    )
    parser.add_argument(
        "--catalog",
        default=DEFAULT_CATALOG_PATH,
        type=Path,
        help="Path to generated domain-product-catalog.json.",
    )
    parser.add_argument(
        "--graph",
        default=DEFAULT_GRAPH_PATH,
        type=Path,
        help="Path to generated domain-product-dependency-graph.json.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_products = subparsers.add_parser(
        "list-products",
        help="List governed domain products with optional filters.",
    )
    list_products.add_argument("--producer", dest="producer_repository")
    list_products.add_argument("--approved-consumer")
    list_products.add_argument("--lifecycle", dest="lifecycle_status")
    list_products.add_argument("--search")

    product = subparsers.add_parser(
        "product",
        help="Show one governed domain product by full identity.",
    )
    product.add_argument("--product-id")
    product.add_argument("--producer")
    product.add_argument("--name")
    product.add_argument("--version")

    consumer = subparsers.add_parser(
        "consumer",
        help="Show declared dependencies for one consumer repository.",
    )
    consumer.add_argument("repository")

    graph = subparsers.add_parser(
        "graph-neighborhood",
        help="Show graph edges connected to one repository or product node.",
    )
    graph.add_argument("node_id")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "list-products":
            catalog = load_catalog(args.catalog)
            products = find_products(
                catalog,
                producer_repository=args.producer_repository,
                approved_consumer=args.approved_consumer,
                lifecycle_status=args.lifecycle_status,
                search=args.search,
            )
            _emit_json(
                {
                    "contract_id": catalog["contract_id"],
                    "contract_version": catalog["contract_version"],
                    "generated_at_utc": catalog["generated_at_utc"],
                    "product_count": len(products),
                    "products": [_product_summary(product) for product in products],
                }
            )
            return 0

        if args.command == "product":
            catalog = load_catalog(args.catalog)
            product = get_product(
                catalog,
                product_id=args.product_id,
                producer_repository=args.producer,
                product_name=args.name,
                product_version=args.version,
            )
            _emit_json({"product": product})
            return 0

        if args.command == "consumer":
            catalog = load_catalog(args.catalog)
            _emit_json(
                {
                    "consumer": get_consumer_dependencies(
                        catalog, consumer_repository=args.repository
                    )
                }
            )
            return 0

        if args.command == "graph-neighborhood":
            graph = load_dependency_graph(args.graph)
            _emit_json(
                {"neighborhood": get_graph_neighborhood(graph, node_id=args.node_id)}
            )
            return 0

    except (LookupError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}")
        return 1

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
