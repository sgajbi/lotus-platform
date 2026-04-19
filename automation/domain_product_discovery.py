from __future__ import annotations

import importlib.util
import json
import re
import tempfile
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECLARATION_DIRECTORY = ROOT / "platform-contracts" / "domain-data-products"
DEFAULT_OUTPUT_DIRECTORY = ROOT / "generated"
VALIDATOR_PATH = DEFAULT_DECLARATION_DIRECTORY / "validate_domain_data_product_contracts.py"
DEFAULT_SOURCE_MANIFEST_PATH = DEFAULT_DECLARATION_DIRECTORY / "domain-product-source-manifest.v1.json"
PRODUCT_GLOB = "*-products.v1.json"
CONSUMER_GLOB = "*-consumers.v1.json"
CATALOG_FILENAME = "domain-product-catalog.json"
CATALOG_MARKDOWN_FILENAME = "domain-product-catalog.md"
GRAPH_FILENAME = "domain-product-dependency-graph.json"
REPOSITORY_PATTERN = re.compile(r"^lotus-[a-z0-9-]+$")
SOURCE_MODES = {"platform_contract_mirror", "repo_native_pending_platform_mirror", "repo_native"}
CATALOG_INCLUSION_STATES = {"included", "pending_platform_declaration", "pending_repo_native_aggregation"}
REPO_NATIVE_STATES = {"implemented", "planned", "pending_clean_slate_confirmation"}


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


def validate_source_manifest(manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH) -> list[str]:
    manifest = _load_json(manifest_path)
    issues: list[str] = []
    if manifest.get("contract_id") != "lotus-domain-product-source-manifest":
        issues.append(f"{manifest_path}: contract_id must be lotus-domain-product-source-manifest")
    if manifest.get("contract_version") != "1.0.0":
        issues.append(f"{manifest_path}: contract_version must be 1.0.0")
    if "RFC-0088" not in manifest.get("governed_by_rfcs", []):
        issues.append(f"{manifest_path}: governed_by_rfcs must include RFC-0088")

    repositories = manifest.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        issues.append(f"{manifest_path}: repositories must be a non-empty array")
        return issues

    seen_repositories: set[str] = set()
    for index, entry in enumerate(repositories):
        if not isinstance(entry, dict):
            issues.append(f"{manifest_path}: repositories[{index}] must be an object")
            continue

        repository = entry.get("repository")
        if not isinstance(repository, str) or not REPOSITORY_PATTERN.fullmatch(repository):
            issues.append(f"{manifest_path}: repositories[{index}].repository must be a Lotus repository name")
        elif repository in seen_repositories:
            issues.append(f"{manifest_path}: repositories contains duplicate repository {repository}")
        else:
            seen_repositories.add(repository)

        if entry.get("source_mode") not in SOURCE_MODES:
            issues.append(f"{manifest_path}: repositories[{index}].source_mode is not governed")
        if entry.get("catalog_inclusion") not in CATALOG_INCLUSION_STATES:
            issues.append(f"{manifest_path}: repositories[{index}].catalog_inclusion is not governed")
        if entry.get("repo_native_status") not in REPO_NATIVE_STATES:
            issues.append(f"{manifest_path}: repositories[{index}].repo_native_status is not governed")

        repo_native_path = entry.get("repo_native_declaration_path")
        if not isinstance(repo_native_path, str) or repo_native_path != "contracts/domain-data-products":
            issues.append(
                f"{manifest_path}: repositories[{index}].repo_native_declaration_path must be contracts/domain-data-products"
            )

        platform_paths = entry.get("platform_declaration_paths")
        if not isinstance(platform_paths, list):
            issues.append(f"{manifest_path}: repositories[{index}].platform_declaration_paths must be an array")
            continue
        if entry.get("catalog_inclusion") == "included" and not platform_paths:
            issues.append(
                f"{manifest_path}: repositories[{index}] included repositories must list platform declaration paths"
            )
        for path_index, platform_path in enumerate(platform_paths):
            if not isinstance(platform_path, str):
                issues.append(
                    f"{manifest_path}: repositories[{index}].platform_declaration_paths[{path_index}] must be a string"
                )
                continue
            resolved_path = ROOT / platform_path
            if not resolved_path.exists():
                issues.append(
                    f"{manifest_path}: repositories[{index}].platform_declaration_paths[{path_index}] does not exist: {platform_path}"
                )

    return issues


def _load_source_manifest(manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH) -> dict[str, Any]:
    issues = validate_source_manifest(manifest_path)
    if issues:
        raise ValueError("Domain product source manifest is invalid:\n" + "\n".join(issues))
    return _load_json(manifest_path)


def _load_declaration_sources(
    declaration_directory: Path,
) -> tuple[list[tuple[Path, dict[str, Any]]], list[tuple[Path, dict[str, Any]]]]:
    producer_payloads = [
        (path, _load_json(path)) for path in sorted(declaration_directory.rglob(PRODUCT_GLOB))
    ]
    consumer_payloads = [
        (path, _load_json(path)) for path in sorted(declaration_directory.rglob(CONSUMER_GLOB))
    ]
    return producer_payloads, consumer_payloads


def _build_product_entry(
    source_path: Path,
    *,
    producer_repository: str,
    product: dict[str, Any],
) -> dict[str, Any]:
    return {
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


def _build_dependency_entry(dependency: dict[str, Any]) -> dict[str, Any]:
    return {
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


def _build_catalog(
    declaration_directory: Path,
    *,
    generated_at_utc: str,
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
) -> dict[str, Any]:
    producer_payloads, consumer_payloads = _load_declaration_sources(declaration_directory)
    source_manifest = _load_source_manifest(source_manifest_path)
    products: list[dict[str, Any]] = []
    consumers: list[dict[str, Any]] = []
    produced_by_repository: dict[str, int] = defaultdict(int)
    consumed_by_repository: dict[str, int] = defaultdict(int)

    for source_path, payload in producer_payloads:
        producer_repository = payload["producer_repository"]
        for product in payload["products"]:
            produced_by_repository[producer_repository] += 1
            products.append(
                _build_product_entry(
                    source_path,
                    producer_repository=producer_repository,
                    product=product,
                )
            )

    for source_path, payload in consumer_payloads:
        consumer_repository = payload["consumer_repository"]
        dependencies = []
        for dependency in payload["dependencies"]:
            consumed_by_repository[consumer_repository] += 1
            dependencies.append(_build_dependency_entry(dependency))
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
        "source_manifest_path": _relative_path(source_manifest_path),
        "source_manifest": source_manifest,
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


def _ensure_repository_node(nodes: dict[str, dict[str, Any]], repository: str) -> str:
    repository_id = f"repo:{repository}"
    nodes.setdefault(
        repository_id,
        {
            "node_id": repository_id,
            "node_type": "repository",
            "repository": repository,
        },
    )
    return repository_id


def _build_product_graph_node(product: dict[str, Any]) -> dict[str, Any]:
    return {
        "node_id": f"product:{product['product_id']}",
        "node_type": "domain_product",
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "product_version": product["product_version"],
        "producer_repository": product["producer_repository"],
        "product_family": product["product_family"],
        "lifecycle_status": product["lifecycle_status"],
    }


def _build_graph(catalog: dict[str, Any]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    for repository in catalog["repositories"]:
        _ensure_repository_node(nodes, repository["repository"])

    for product in catalog["products"]:
        product_id = f"product:{product['product_id']}"
        producer_id = _ensure_repository_node(nodes, product["producer_repository"])
        nodes[product_id] = _build_product_graph_node(product)
        edges.append(
            {
                "edge_type": "produces",
                "from": producer_id,
                "to": product_id,
            }
        )
        for approved_consumer in product["approved_consumers"]:
            consumer_id = _ensure_repository_node(nodes, approved_consumer)
            edges.append(
                {
                    "edge_type": "approves_consumer",
                    "from": product_id,
                    "to": consumer_id,
                }
            )

    for consumer in catalog["consumers"]:
        consumer_id = _ensure_repository_node(nodes, consumer["consumer_repository"])
        for dependency in consumer["dependencies"]:
            edges.append(
                {
                    "edge_type": "consumes",
                    "from": consumer_id,
                    "to": f"product:{dependency['dependency_id']}",
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
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    declaration_directory = declaration_directory.resolve()
    validator = _load_platform_validator()
    validation_issues = validator.validate_contract_directory(declaration_directory)
    if validation_issues:
        raise ValueError("Domain product declarations are invalid:\n" + "\n".join(validation_issues))

    generated_at = generated_at_utc or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    catalog = _build_catalog(
        declaration_directory,
        generated_at_utc=generated_at,
        source_manifest_path=source_manifest_path,
    )
    graph = _build_graph(catalog)
    markdown = _render_catalog_markdown(catalog)
    return catalog, graph, markdown


def write_discovery_artifacts(
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
    declaration_directory: Path = DEFAULT_DECLARATION_DIRECTORY,
    *,
    generated_at_utc: str | None = None,
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
) -> None:
    catalog, graph, markdown = generate_discovery_artifacts(
        declaration_directory,
        generated_at_utc=generated_at_utc,
        source_manifest_path=source_manifest_path,
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    (output_directory / CATALOG_FILENAME).write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    (output_directory / GRAPH_FILENAME).write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    (output_directory / CATALOG_MARKDOWN_FILENAME).write_text(markdown, encoding="utf-8")


def check_discovery_artifacts(
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
    declaration_directory: Path = DEFAULT_DECLARATION_DIRECTORY,
    *,
    generated_at_utc: str,
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="lotus-domain-product-discovery-check-") as temp_dir_string:
        temp_dir = Path(temp_dir_string)
        write_discovery_artifacts(
            temp_dir,
            declaration_directory,
            generated_at_utc=generated_at_utc,
            source_manifest_path=source_manifest_path,
        )

        issues: list[str] = []
        for artifact_name in (CATALOG_FILENAME, GRAPH_FILENAME, CATALOG_MARKDOWN_FILENAME):
            expected_path = temp_dir / artifact_name
            actual_path = output_directory / artifact_name
            if not actual_path.exists():
                issues.append(f"{actual_path}: generated discovery artifact is missing")
                continue
            if actual_path.read_text(encoding="utf-8") != expected_path.read_text(encoding="utf-8"):
                issues.append(f"{actual_path}: generated discovery artifact is stale")

        return issues
