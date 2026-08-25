from __future__ import annotations

import importlib.util
import json
import re
import shutil
import tempfile
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECLARATION_DIRECTORY = ROOT / "platform-contracts" / "domain-data-products"
DEFAULT_DOMAIN_VOCABULARY_DIRECTORY = ROOT / "platform-contracts" / "domain-vocabulary"
DEFAULT_OUTPUT_DIRECTORY = ROOT / "generated"
VALIDATOR_PATH = (
    DEFAULT_DECLARATION_DIRECTORY / "validate_domain_data_product_contracts.py"
)
DEFAULT_SOURCE_MANIFEST_PATH = (
    DEFAULT_DECLARATION_DIRECTORY / "domain-product-source-manifest.v1.json"
)
PRODUCT_GLOB = "*-products.v1.json"
CONSUMER_GLOB = "*-consumers.v1.json"
CATALOG_FILENAME = "domain-product-catalog.json"
CATALOG_MARKDOWN_FILENAME = "domain-product-catalog.md"
GRAPH_FILENAME = "domain-product-dependency-graph.json"
DEFAULT_CATALOG_PATH = DEFAULT_OUTPUT_DIRECTORY / CATALOG_FILENAME
DEFAULT_GRAPH_PATH = DEFAULT_OUTPUT_DIRECTORY / GRAPH_FILENAME
REPOSITORY_PATTERN = re.compile(r"^lotus-[a-z0-9-]+$")
SOURCE_MODES = {
    "platform_contract_mirror",
    "repo_native_pending_platform_mirror",
    "repo_native",
}
CATALOG_INCLUSION_STATES = {
    "included",
    "pending_platform_declaration",
    "pending_repo_native_aggregation",
}
REPO_NATIVE_STATES = {"implemented", "planned", "pending_clean_slate_confirmation"}
FEDERATED_SOURCE_SENTINEL = "federated:domain-product-source-manifest"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog(catalog_path: Path = DEFAULT_CATALOG_PATH) -> dict[str, Any]:
    catalog = _load_json(catalog_path)
    if catalog.get("contract_id") != "lotus-domain-product-catalog":
        raise ValueError(f"{catalog_path}: not a Lotus domain-product catalog")
    return catalog


def load_dependency_graph(graph_path: Path = DEFAULT_GRAPH_PATH) -> dict[str, Any]:
    graph = _load_json(graph_path)
    if graph.get("contract_id") != "lotus-domain-product-dependency-graph":
        raise ValueError(f"{graph_path}: not a Lotus domain-product dependency graph")
    return graph


def find_products(
    catalog: dict[str, Any],
    *,
    producer_repository: str | None = None,
    approved_consumer: str | None = None,
    lifecycle_status: str | None = None,
    search: str | None = None,
) -> list[dict[str, Any]]:
    normalized_search = search.casefold() if search else None
    products: list[dict[str, Any]] = []
    for product in catalog.get("products", []):
        if not _product_matches_filters(
            product,
            producer_repository=producer_repository,
            approved_consumer=approved_consumer,
            lifecycle_status=lifecycle_status,
        ):
            continue
        if normalized_search and not _product_matches_search(
            product, normalized_search=normalized_search
        ):
            continue
        products.append(product)

    return sorted(products, key=_product_sort_key)


def _product_matches_filters(
    product: dict[str, Any],
    *,
    producer_repository: str | None,
    approved_consumer: str | None,
    lifecycle_status: str | None,
) -> bool:
    if (
        producer_repository
        and product.get("producer_repository") != producer_repository
    ):
        return False
    if approved_consumer and approved_consumer not in product.get(
        "approved_consumers", []
    ):
        return False
    return not (
        lifecycle_status and product.get("lifecycle_status") != lifecycle_status
    )


def _product_matches_search(
    product: dict[str, Any],
    *,
    normalized_search: str,
) -> bool:
    searchable = " ".join(
        str(product.get(field, ""))
        for field in (
            "product_id",
            "product_name",
            "producer_repository",
            "authoritative_domain",
            "product_family",
        )
    ).casefold()
    return normalized_search in searchable


def _product_sort_key(product: dict[str, Any]) -> tuple[str, str, str]:
    return (
        product["producer_repository"],
        product["product_name"],
        product["product_version"],
    )


def get_product(
    catalog: dict[str, Any],
    *,
    product_id: str | None = None,
    producer_repository: str | None = None,
    product_name: str | None = None,
    product_version: str | None = None,
) -> dict[str, Any]:
    if product_id is None:
        if not producer_repository or not product_name or not product_version:
            raise ValueError(
                "product lookup requires product_id or producer_repository, product_name, and product_version"
            )
        product_id = _product_id(producer_repository, product_name, product_version)

    matches = [
        product
        for product in catalog.get("products", [])
        if product.get("product_id") == product_id
    ]
    if not matches:
        raise LookupError(f"domain product not found: {product_id}")
    return matches[0]


def get_consumer_dependencies(
    catalog: dict[str, Any],
    *,
    consumer_repository: str,
) -> dict[str, Any]:
    for consumer in catalog.get("consumers", []):
        if consumer.get("consumer_repository") == consumer_repository:
            return consumer
    raise LookupError(f"domain-product consumer not found: {consumer_repository}")


def get_graph_neighborhood(
    graph: dict[str, Any],
    *,
    node_id: str,
) -> dict[str, Any]:
    nodes_by_id = {node["node_id"]: node for node in graph.get("nodes", [])}
    if node_id not in nodes_by_id:
        raise LookupError(f"domain-product graph node not found: {node_id}")

    edges = [
        edge
        for edge in graph.get("edges", [])
        if edge.get("from") == node_id or edge.get("to") == node_id
    ]
    connected_node_ids = {node_id}
    for edge in edges:
        connected_node_ids.add(edge["from"])
        connected_node_ids.add(edge["to"])

    return {
        "node": nodes_by_id[node_id],
        "connected_nodes": [
            nodes_by_id[connected_id] for connected_id in sorted(connected_node_ids)
        ],
        "edges": sorted(
            edges, key=lambda edge: (edge["edge_type"], edge["from"], edge["to"])
        ),
    }


def _load_platform_validator():
    spec = importlib.util.spec_from_file_location(
        "lotus_domain_product_validator", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Unable to load platform domain-product validator from {VALIDATOR_PATH}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _relative_path(path: Path, *, source_root: Path | None = None) -> str:
    resolved = path.resolve()
    if "_federated" in resolved.parts:
        federated_index = resolved.parts.index("_federated")
        return Path(*resolved.parts[federated_index + 1 :]).as_posix()
    if source_root is not None:
        try:
            return resolved.relative_to(source_root.resolve()).as_posix()
        except ValueError:
            pass
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        try:
            return resolved.relative_to(ROOT.parent).as_posix()
        except ValueError:
            return resolved.as_posix()


def _product_id(
    producer_repository: str, product_name: str, product_version: str
) -> str:
    return f"{producer_repository}:{product_name}:{product_version}"


def _validate_source_manifest_identity(
    *, manifest_path: Path, manifest: dict[str, Any], issues: list[str]
) -> None:
    if manifest.get("contract_id") != "lotus-domain-product-source-manifest":
        issues.append(
            f"{manifest_path}: contract_id must be lotus-domain-product-source-manifest"
        )
    if manifest.get("contract_version") != "1.0.0":
        issues.append(f"{manifest_path}: contract_version must be 1.0.0")
    if "RFC-0088" not in manifest.get("governed_by_rfcs", []):
        issues.append(f"{manifest_path}: governed_by_rfcs must include RFC-0088")


def _append_source_manifest_repository_identity_issues(
    *,
    manifest_path: Path,
    index: int,
    entry: dict[str, Any],
    seen_repositories: set[str],
    issues: list[str],
) -> str | None:
    repository = entry.get("repository")
    if not isinstance(repository, str) or not REPOSITORY_PATTERN.fullmatch(repository):
        issues.append(
            f"{manifest_path}: repositories[{index}].repository must be a Lotus repository name"
        )
        return None
    if repository in seen_repositories:
        issues.append(
            f"{manifest_path}: repositories contains duplicate repository {repository}"
        )
        return repository
    seen_repositories.add(repository)
    return repository


def _validate_source_manifest_repository_posture(
    *,
    manifest_path: Path,
    index: int,
    entry: dict[str, Any],
    issues: list[str],
) -> str | None:
    if entry.get("source_mode") not in SOURCE_MODES:
        issues.append(
            f"{manifest_path}: repositories[{index}].source_mode is not governed"
        )
    if entry.get("catalog_inclusion") not in CATALOG_INCLUSION_STATES:
        issues.append(
            f"{manifest_path}: repositories[{index}].catalog_inclusion is not governed"
        )
    if entry.get("repo_native_status") not in REPO_NATIVE_STATES:
        issues.append(
            f"{manifest_path}: repositories[{index}].repo_native_status is not governed"
        )

    repo_native_path = entry.get("repo_native_declaration_path")
    if (
        not isinstance(repo_native_path, str)
        or repo_native_path != "contracts/domain-data-products"
    ):
        issues.append(
            f"{manifest_path}: repositories[{index}].repo_native_declaration_path must be contracts/domain-data-products"
        )
        return None
    return repo_native_path


def _validate_repo_native_source_directory(
    *,
    manifest_path: Path,
    index: int,
    repository: str | None,
    repo_native_path: str | None,
    repo_native_status: object,
    source_root: Path,
    issues: list[str],
) -> None:
    if repo_native_status != "implemented":
        issues.append(
            f"{manifest_path}: repositories[{index}] repo_native sources require repo_native_status implemented"
        )
    if isinstance(repository, str) and isinstance(repo_native_path, str):
        repo_native_directory = source_root / repository / repo_native_path
    else:
        repo_native_directory = None
    if repo_native_directory is not None and not repo_native_directory.exists():
        issues.append(
            f"{manifest_path}: repositories[{index}] repo-native declaration directory does not exist: {repo_native_directory}"
        )


def _validate_platform_declaration_paths(
    *,
    manifest_path: Path,
    index: int,
    platform_paths: object,
    issues: list[str],
) -> bool:
    if not isinstance(platform_paths, list):
        issues.append(
            f"{manifest_path}: repositories[{index}].platform_declaration_paths must be an array"
        )
        return False
    return True


def _validate_platform_declaration_path_entries(
    *,
    manifest_path: Path,
    index: int,
    platform_paths: list[object],
    issues: list[str],
) -> None:
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


def _validate_source_manifest_repository_entry(
    *,
    manifest_path: Path,
    index: int,
    entry: object,
    seen_repositories: set[str],
    source_root: Path,
    issues: list[str],
) -> None:
    if not isinstance(entry, dict):
        issues.append(f"{manifest_path}: repositories[{index}] must be an object")
        return

    repository = _append_source_manifest_repository_identity_issues(
        manifest_path=manifest_path,
        index=index,
        entry=entry,
        seen_repositories=seen_repositories,
        issues=issues,
    )
    repo_native_path = _validate_source_manifest_repository_posture(
        manifest_path=manifest_path,
        index=index,
        entry=entry,
        issues=issues,
    )

    source_mode = entry.get("source_mode")
    catalog_inclusion = entry.get("catalog_inclusion")
    platform_paths = entry.get("platform_declaration_paths")
    platform_paths_valid = _validate_platform_declaration_paths(
        manifest_path=manifest_path,
        index=index,
        platform_paths=platform_paths,
        issues=issues,
    )
    if (
        platform_paths_valid
        and catalog_inclusion == "included"
        and source_mode == "platform_contract_mirror"
        and not platform_paths
    ):
        issues.append(
            f"{manifest_path}: repositories[{index}] included platform-mirror repositories must list platform declaration paths"
        )
    if source_mode == "repo_native":
        _validate_repo_native_source_directory(
            manifest_path=manifest_path,
            index=index,
            repository=repository,
            repo_native_path=repo_native_path,
            repo_native_status=entry.get("repo_native_status"),
            source_root=source_root,
            issues=issues,
        )
    if platform_paths_valid:
        _validate_platform_declaration_path_entries(
            manifest_path=manifest_path,
            index=index,
            platform_paths=platform_paths,
            issues=issues,
        )


def validate_source_manifest(
    manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
    *,
    source_root: Path | None = None,
) -> list[str]:
    manifest = _load_json(manifest_path)
    resolved_source_root = (source_root or ROOT.parent).resolve()
    issues: list[str] = []
    _validate_source_manifest_identity(
        manifest_path=manifest_path,
        manifest=manifest,
        issues=issues,
    )

    repositories = manifest.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        issues.append(f"{manifest_path}: repositories must be a non-empty array")
        return issues

    seen_repositories: set[str] = set()
    for index, entry in enumerate(repositories):
        _validate_source_manifest_repository_entry(
            manifest_path=manifest_path,
            index=index,
            entry=entry,
            seen_repositories=seen_repositories,
            source_root=resolved_source_root,
            issues=issues,
        )

    return issues


def _load_source_manifest(
    manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
    *,
    source_root: Path | None = None,
) -> dict[str, Any]:
    issues = validate_source_manifest(manifest_path, source_root=source_root)
    if issues:
        raise ValueError(
            "Domain product source manifest is invalid:\n" + "\n".join(issues)
        )
    return _load_json(manifest_path)


def _load_declaration_sources(
    declaration_directory: Path,
) -> tuple[list[tuple[Path, dict[str, Any]]], list[tuple[Path, dict[str, Any]]]]:
    producer_payloads = [
        (path, _load_json(path))
        for path in sorted(declaration_directory.rglob(PRODUCT_GLOB))
    ]
    consumer_payloads = [
        (path, _load_json(path))
        for path in sorted(declaration_directory.rglob(CONSUMER_GLOB))
    ]
    return producer_payloads, consumer_payloads


def _source_paths_from_manifest(
    source_manifest: dict[str, Any],
    *,
    source_root: Path | None = None,
) -> list[Path]:
    resolved_source_root = (source_root or ROOT.parent).resolve()
    source_paths: list[Path] = []
    for entry in source_manifest["repositories"]:
        if entry["catalog_inclusion"] != "included":
            continue

        if entry["source_mode"] == "repo_native":
            repo_directory = (
                resolved_source_root
                / entry["repository"]
                / entry["repo_native_declaration_path"]
            )
            source_paths.extend(sorted(repo_directory.rglob(PRODUCT_GLOB)))
            source_paths.extend(sorted(repo_directory.rglob(CONSUMER_GLOB)))
            continue

        for platform_path in entry["platform_declaration_paths"]:
            source_paths.append(ROOT / platform_path)

    return sorted(source_paths)


def _load_declaration_sources_from_manifest(
    source_manifest: dict[str, Any],
    *,
    source_root: Path | None = None,
) -> tuple[list[tuple[Path, dict[str, Any]]], list[tuple[Path, dict[str, Any]]]]:
    producer_payloads: list[tuple[Path, dict[str, Any]]] = []
    consumer_payloads: list[tuple[Path, dict[str, Any]]] = []
    for source_path in _source_paths_from_manifest(
        source_manifest, source_root=source_root
    ):
        payload = _load_json(source_path)
        if source_path.match(PRODUCT_GLOB):
            producer_payloads.append((source_path, payload))
        elif source_path.match(CONSUMER_GLOB):
            consumer_payloads.append((source_path, payload))

    return producer_payloads, consumer_payloads


def _copy_validation_source(source_path: Path, target_directory: Path) -> None:
    target_path = target_directory / source_path.name
    if target_path.exists():
        raise ValueError(
            "Duplicate domain-product declaration filename in federated source set: "
            f"{source_path.name}"
        )
    shutil.copy2(source_path, target_path)


def _validate_declaration_sources(
    producer_payloads: list[tuple[Path, dict[str, Any]]],
    consumer_payloads: list[tuple[Path, dict[str, Any]]],
) -> None:
    with tempfile.TemporaryDirectory(
        prefix="lotus-domain-product-federated-validation-"
    ) as temp_dir_string:
        temp_dir = Path(temp_dir_string)
        validation_contract_dir = temp_dir / "domain-data-products"
        validation_vocabulary_dir = temp_dir / "domain-vocabulary"
        validation_contract_dir.mkdir(parents=True)
        validation_vocabulary_dir.mkdir(parents=True)

        for registry_path in DEFAULT_DOMAIN_VOCABULARY_DIRECTORY.glob("*.json"):
            shutil.copy2(registry_path, validation_vocabulary_dir / registry_path.name)
        for source_path, _ in [*producer_payloads, *consumer_payloads]:
            _copy_validation_source(source_path, validation_contract_dir)

        validator = _load_platform_validator()
        validation_issues = validator.validate_contract_directory(
            validation_contract_dir
        )
        if validation_issues:
            raise ValueError(
                "Domain product declarations are invalid:\n"
                + "\n".join(validation_issues)
            )


def _build_product_entry(
    source_path: Path,
    *,
    producer_repository: str,
    product: dict[str, Any],
    source_root: Path | None = None,
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
        "source_path": _relative_path(source_path, source_root=source_root),
    }


def _build_dependency_entry(dependency: dict[str, Any]) -> dict[str, Any]:
    entry = {
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
    if "failure_posture_conditions" in dependency:
        entry["failure_posture_conditions"] = dependency["failure_posture_conditions"]
    return entry


def _build_catalog_from_sources(
    producer_payloads: list[tuple[Path, dict[str, Any]]],
    consumer_payloads: list[tuple[Path, dict[str, Any]]],
    *,
    generated_at_utc: str,
    source_declaration_directory: str,
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
    source_manifest: dict[str, Any] | None = None,
    source_root: Path | None = None,
) -> dict[str, Any]:
    source_manifest = source_manifest or _load_source_manifest(source_manifest_path)
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
                    source_root=source_root,
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
                "source_path": _relative_path(source_path, source_root=source_root),
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
        "source_declaration_directory": source_declaration_directory,
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
        "consumers": sorted(
            consumers, key=lambda consumer: consumer["consumer_repository"]
        ),
    }


def _build_catalog(
    declaration_directory: Path,
    *,
    generated_at_utc: str,
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
    source_root: Path | None = None,
) -> dict[str, Any]:
    producer_payloads, consumer_payloads = _load_declaration_sources(
        declaration_directory
    )
    return _build_catalog_from_sources(
        producer_payloads,
        consumer_payloads,
        generated_at_utc=generated_at_utc,
        source_declaration_directory=_relative_path(declaration_directory),
        source_manifest_path=source_manifest_path,
        source_root=source_root,
    )


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
            if "failure_posture_conditions" in dependency:
                edges[-1]["failure_posture_conditions"] = dependency[
                    "failure_posture_conditions"
                ]

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
        routes = (
            ", ".join(product["current_routes"])
            if product["current_routes"]
            else "Not published"
        )
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

    has_conditional_failure_postures = any(
        dependency.get("failure_posture_conditions")
        for consumer in catalog["consumers"]
        for dependency in consumer["dependencies"]
    )
    dependency_rows = [
        (
            "| Consumer | Upstream Product | Producer | Version | Mode | Failure Posture | "
            "Conditional Overrides |"
            if has_conditional_failure_postures
            else "| Consumer | Upstream Product | Producer | Version | Mode | Failure Posture |"
        ),
        (
            "| --- | --- | --- | --- | --- | --- | --- |"
            if has_conditional_failure_postures
            else "| --- | --- | --- | --- | --- | --- |"
        ),
    ]
    for consumer in catalog["consumers"]:
        for dependency in consumer["dependencies"]:
            row = (
                "| "
                f"`{consumer['consumer_repository']}` | "
                f"`{dependency['product_name']}` | "
                f"`{dependency['producer_repository']}` | "
                f"`{dependency['required_product_version']}` | "
                f"`{dependency['consumption_mode']}` | "
                f"`{dependency['failure_posture']}` |"
            )
            if has_conditional_failure_postures:
                row = row[:-1] + f" {_render_failure_posture_conditions(dependency)} |"
            dependency_rows.append(row)

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


def _render_failure_posture_conditions(dependency: dict[str, Any]) -> str:
    conditions = dependency.get("failure_posture_conditions", [])
    if not conditions:
        return "None"
    return "<br>".join(
        f"`{condition['posture']}` when {condition['condition']}"
        for condition in conditions
    )


def generate_discovery_artifacts(
    declaration_directory: Path = DEFAULT_DECLARATION_DIRECTORY,
    *,
    generated_at_utc: str | None = None,
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
    source_root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    declaration_directory = declaration_directory.resolve()
    source_manifest = _load_source_manifest(
        source_manifest_path, source_root=source_root
    )
    producer_payloads, consumer_payloads = _load_declaration_sources_from_manifest(
        source_manifest, source_root=source_root
    )
    if not producer_payloads:
        raise ValueError("No producer domain-product declarations found to catalog")
    _validate_declaration_sources(producer_payloads, consumer_payloads)

    generated_at = generated_at_utc or datetime.now(UTC).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    catalog = _build_catalog_from_sources(
        producer_payloads,
        consumer_payloads,
        generated_at_utc=generated_at,
        source_declaration_directory=FEDERATED_SOURCE_SENTINEL,
        source_manifest_path=source_manifest_path,
        source_manifest=source_manifest,
        source_root=source_root,
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
    source_root: Path | None = None,
) -> None:
    catalog, graph, markdown = generate_discovery_artifacts(
        declaration_directory,
        generated_at_utc=generated_at_utc,
        source_manifest_path=source_manifest_path,
        source_root=source_root,
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    (output_directory / CATALOG_FILENAME).write_text(
        json.dumps(catalog, indent=2) + "\n", encoding="utf-8"
    )
    (output_directory / GRAPH_FILENAME).write_text(
        json.dumps(graph, indent=2) + "\n", encoding="utf-8"
    )
    (output_directory / CATALOG_MARKDOWN_FILENAME).write_text(
        markdown, encoding="utf-8"
    )


def check_discovery_artifacts(
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
    declaration_directory: Path = DEFAULT_DECLARATION_DIRECTORY,
    *,
    generated_at_utc: str,
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
    source_root: Path | None = None,
) -> list[str]:
    with tempfile.TemporaryDirectory(
        prefix="lotus-domain-product-discovery-check-"
    ) as temp_dir_string:
        temp_dir = Path(temp_dir_string)
        write_discovery_artifacts(
            temp_dir,
            declaration_directory,
            generated_at_utc=generated_at_utc,
            source_manifest_path=source_manifest_path,
            source_root=source_root,
        )

        issues: list[str] = []
        for artifact_name in (
            CATALOG_FILENAME,
            GRAPH_FILENAME,
            CATALOG_MARKDOWN_FILENAME,
        ):
            expected_path = temp_dir / artifact_name
            actual_path = output_directory / artifact_name
            if not actual_path.exists():
                issues.append(f"{actual_path}: generated discovery artifact is missing")
                continue
            if actual_path.read_text(encoding="utf-8") != expected_path.read_text(
                encoding="utf-8"
            ):
                issues.append(f"{actual_path}: generated discovery artifact is stale")

        return issues
