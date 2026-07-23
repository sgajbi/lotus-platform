from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from mesh_maturity_scope import (
    CERTIFICATION_CANDIDATE_PRODUCT_IDS,
    CERTIFICATION_CANDIDATE_REPOSITORIES,
    REQUIRED_PRODUCT_IDS,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG_PATH = ROOT / "generated" / "domain-product-catalog.json"
DEFAULT_OUTPUT_DIRECTORY = ROOT / "generated"
MATRIX_FILENAME = "enterprise-mesh-maturity-matrix.json"
MATRIX_MARKDOWN_FILENAME = "enterprise-mesh-maturity-matrix.md"
DEFAULT_GENERATED_AT_UTC = "2026-04-20T00:00:00Z"

LOTUS_REPOSITORIES = [
    "lotus-platform",
    "lotus-core",
    "lotus-performance",
    "lotus-risk",
    "lotus-advise",
    "lotus-report",
    "lotus-manage",
    "lotus-gateway",
    "lotus-workbench",
    "lotus-idea",
    "lotus-ai",
]

FIRST_WAVE_PRODUCTS = set(REQUIRED_PRODUCT_IDS)
CERTIFICATION_CANDIDATE_PRODUCTS = set(CERTIFICATION_CANDIDATE_PRODUCT_IDS)

CANDIDATE_PRODUCTS: list[dict[str, str]] = []

SUPPORT_REPOSITORY_POSTURE = {
    "lotus-platform": {
        "classification": "not_mesh_participant",
        "mesh_role": "platform_governance",
        "rationale": "Owns contracts, validators, generated evidence, CI, and certification enforcement rather than product truth.",
    },
    "lotus-gateway": {
        "classification": "not_mesh_participant",
        "mesh_role": "api_face",
        "rationale": "Publishes catalog, trust, access, and evidence APIs without becoming a product authority.",
    },
    "lotus-workbench": {
        "classification": "not_mesh_participant",
        "mesh_role": "discovery_and_operator_ux",
        "rationale": "Consumes gateway/BFF APIs for discovery and evidence UX; it must not read platform files directly.",
    },
    "lotus-ai": {
        "classification": "not_mesh_participant",
        "mesh_role": "explicit_posture_decision",
        "rationale": "Not included until it owns a stable governed product or a catalog-consuming capability.",
    },
}

CONSUMER_ONLY_REPOSITORIES: set[str] = set()
REPO_NATIVE_PARTICIPATION_REPOSITORIES = {
    "lotus-core",
    "lotus-performance",
    "lotus-risk",
    "lotus-advise",
    "lotus-report",
    "lotus-manage",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _catalog_products_by_repo(
    catalog: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    by_repo: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for product in catalog.get("products", []):
        by_repo[product["producer_repository"]].append(product)
    return {
        repo: sorted(products, key=lambda item: item["product_id"])
        for repo, products in by_repo.items()
    }


def _catalog_consumers_by_repo(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        consumer["consumer_repository"]: consumer
        for consumer in catalog.get("consumers", [])
    }


def _source_manifest_by_repo(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        entry["repository"]: entry
        for entry in catalog.get("source_manifest", {}).get("repositories", [])
    }


def _repository_entry(
    repository: str,
    *,
    products: list[dict[str, Any]],
    consumer: dict[str, Any] | None,
    manifest_entry: dict[str, Any] | None,
) -> dict[str, Any]:
    if repository in SUPPORT_REPOSITORY_POSTURE:
        support_posture = SUPPORT_REPOSITORY_POSTURE[repository]
        return {
            "repository": repository,
            **support_posture,
            "produced_product_count": 0,
            "consumed_dependency_count": 0,
            "repo_native_status": "not_applicable",
            "ambiguous_participation": False,
            "required_next_step": support_posture["rationale"],
        }

    first_wave_product_count = sum(
        1 for product in products if product["product_id"] in FIRST_WAVE_PRODUCTS
    )
    certification_candidate_product_count = sum(
        1
        for product in products
        if product["product_id"] in CERTIFICATION_CANDIDATE_PRODUCTS
    )
    consumed_dependency_count = (consumer or {}).get("dependency_count", 0)
    if first_wave_product_count:
        classification = "certified_first_wave"
        mesh_role = "producer"
        required_next_step = (
            "Maintain repo-native declaration, trust telemetry, SLO, access, "
            "lifecycle, evidence-pack, and certification-gate posture."
        )
    elif certification_candidate_product_count:
        classification = "certification_candidate"
        mesh_role = "producer"
        required_next_step = (
            "Complete runtime telemetry, durable repository, Gateway/Workbench "
            "discovery, and supported-feature proof before promotion."
        )
    elif repository in CONSUMER_ONLY_REPOSITORIES:
        classification = "consumer_only"
        mesh_role = "candidate_expansion"
        required_next_step = "Promote the RFC-0091 candidate product or keep the repository explicitly consumer-only."
    elif products:
        classification = "deferred"
        mesh_role = "producer"
        required_next_step = (
            "Decide whether these non-first-wave products enter a later maturity wave."
        )
    else:
        classification = "deferred"
        mesh_role = "unclassified"
        required_next_step = (
            "Classify repository participation before implementation continues."
        )

    return {
        "repository": repository,
        "classification": classification,
        "mesh_role": mesh_role,
        "rationale": _repository_rationale(
            classification=classification,
            product_count=len(products),
            dependency_count=consumed_dependency_count,
        ),
        "produced_product_count": len(products),
        "first_wave_product_count": first_wave_product_count,
        "certification_candidate_product_count": certification_candidate_product_count,
        "consumed_dependency_count": consumed_dependency_count,
        "repo_native_status": (manifest_entry or {}).get(
            "repo_native_status", "not_in_source_manifest"
        ),
        "source_mode": (manifest_entry or {}).get(
            "source_mode", "not_in_source_manifest"
        ),
        "ambiguous_participation": False,
        "required_next_step": required_next_step,
    }


def _repository_rationale(
    *, classification: str, product_count: int, dependency_count: int
) -> str:
    if classification == "certified_first_wave":
        return "Produces one or more RFC-0089 required products and is included in the first enterprise maturity wave."
    if classification == "certification_candidate":
        return "Produces one or more implementation-backed certification candidates selected for policy coverage but not blocking maturity enforcement."
    if classification == "consumer_only":
        return "Currently participates through consumer declarations and is a candidate expansion repository."
    if classification == "deferred" and product_count:
        return "Produces catalog products that are not yet selected for RFC-0091 maturity enforcement."
    if dependency_count:
        return "Consumes governed products but is not selected as a maturity-wave producer yet."
    return "No current maturity-wave product participation."


def _product_entries(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    product_entries: list[dict[str, Any]] = []
    for product in sorted(
        catalog.get("products", []), key=lambda item: item["product_id"]
    ):
        product_id = product["product_id"]
        if product_id in FIRST_WAVE_PRODUCTS:
            classification = "certified_first_wave"
            maturity_wave = "enterprise_wave_1"
            required_next_step = (
                "Maintain RFC-0091 runtime, SLO, access, lifecycle, evidence-pack, "
                "and certification-gate controls."
            )
        elif product_id in CERTIFICATION_CANDIDATE_PRODUCTS:
            classification = "certification_candidate"
            maturity_wave = "enterprise_wave_candidate"
            required_next_step = (
                "Keep fail-closed until runtime trust telemetry, durable records, "
                "Gateway/Workbench discovery, and supported-feature proof are certified."
            )
        else:
            classification = "deferred"
            maturity_wave = "future_wave"
            required_next_step = (
                "Keep outside blocking maturity gate until explicitly promoted."
            )
        product_entries.append(
            {
                "product_id": product_id,
                "product_name": product["product_name"],
                "product_version": product["product_version"],
                "producer_repository": product["producer_repository"],
                "classification": classification,
                "maturity_wave": maturity_wave,
                "lifecycle_status": product.get("lifecycle_status", "unknown"),
                "source_path": product.get("source_path", ""),
                "required_next_step": required_next_step,
            }
        )

    product_entries.extend(
        {
            **candidate,
            "maturity_wave": "enterprise_wave_1_candidate",
            "lifecycle_status": "planned",
            "source_path": "not_declared_yet",
        }
        for candidate in CANDIDATE_PRODUCTS
    )
    return sorted(product_entries, key=lambda item: item["product_id"])


def build_enterprise_mesh_maturity_matrix(
    *,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    generated_at_utc: str = DEFAULT_GENERATED_AT_UTC,
) -> dict[str, Any]:
    catalog = _load_json(catalog_path)
    products_by_repo = _catalog_products_by_repo(catalog)
    consumers_by_repo = _catalog_consumers_by_repo(catalog)
    manifest_by_repo = _source_manifest_by_repo(catalog)
    official_repositories = set(LOTUS_REPOSITORIES)
    catalog_repositories = (
        set(products_by_repo) | set(consumers_by_repo) | set(manifest_by_repo)
    )
    unknown_repositories = sorted(catalog_repositories - official_repositories)
    missing_manifest_repositories = sorted(
        REPO_NATIVE_PARTICIPATION_REPOSITORIES - set(manifest_by_repo)
    )
    catalog_product_ids = {
        product["product_id"]
        for products in products_by_repo.values()
        for product in products
    }
    missing_required_products = sorted(FIRST_WAVE_PRODUCTS - catalog_product_ids)

    repositories = [
        _repository_entry(
            repository,
            products=products_by_repo.get(repository, []),
            consumer=consumers_by_repo.get(repository),
            manifest_entry=manifest_by_repo.get(repository),
        )
        for repository in LOTUS_REPOSITORIES
    ]
    products = _product_entries(catalog)
    ambiguous_repositories = sorted(
        {
            entry["repository"]
            for entry in repositories
            if entry["ambiguous_participation"]
        }
        | set(unknown_repositories)
        | set(missing_manifest_repositories)
        | {
            product_id.split(":", maxsplit=1)[0]
            for product_id in missing_required_products
        }
    )

    return {
        "contract_id": "lotus-enterprise-mesh-maturity-matrix",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0091"],
        "generated_at_utc": generated_at_utc,
        "source_catalog_path": _relative_path(catalog_path),
        "implementation_boundary": {
            "required_first_wave_repositories": [
                "lotus-core",
                "lotus-performance",
                "lotus-risk",
                "lotus-advise",
                "lotus-report",
                "lotus-manage",
            ],
            "candidate_expansion_repositories": [],
            "certification_candidate_repositories": list(
                CERTIFICATION_CANDIDATE_REPOSITORIES
            ),
            "explicit_posture_decision_repositories": ["lotus-ai"],
            "future_wave_catalog_repositories": [
                repository
                for repository in ["lotus-idea"]
                if repository not in CERTIFICATION_CANDIDATE_REPOSITORIES
            ],
            "api_face": "lotus-gateway",
            "discovery_and_operator_ux": "lotus-workbench",
            "platform_governance": "lotus-platform",
        },
        "summary": {
            "repository_count": len(repositories),
            "product_count": len(products),
            "certified_first_wave_product_count": sum(
                1
                for product in products
                if product["classification"] == "certified_first_wave"
            ),
            "candidate_product_count": sum(
                1
                for product in products
                if product["classification"] == "certification_candidate"
            ),
            "ambiguous_repository_count": len(ambiguous_repositories),
        },
        "repositories": repositories,
        "products": products,
        "ambiguous_repositories": ambiguous_repositories,
        "unknown_repositories": unknown_repositories,
        "missing_manifest_repositories": missing_manifest_repositories,
        "missing_required_products": missing_required_products,
    }


def render_enterprise_mesh_maturity_matrix_markdown(matrix: dict[str, Any]) -> str:
    lines = [
        "# Enterprise Mesh Maturity Matrix",
        "",
        "This file is generated from governed domain-product catalog evidence and RFC-0091 maturity-wave rules.",
        "",
        f"- Generated at: `{matrix['generated_at_utc']}`",
        f"- Source catalog: `{matrix['source_catalog_path']}`",
        f"- Repository count: `{matrix['summary']['repository_count']}`",
        f"- Product count: `{matrix['summary']['product_count']}`",
        f"- Certified first-wave products: `{matrix['summary']['certified_first_wave_product_count']}`",
        f"- Candidate products: `{matrix['summary']['candidate_product_count']}`",
        f"- Ambiguous repositories: `{matrix['summary']['ambiguous_repository_count']}`",
        "",
        "## Repository Maturity",
        "",
        "| Repository | Classification | Mesh role | Produced | Consumed | Next step |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for repository in matrix["repositories"]:
        lines.append(
            "| `{repository}` | `{classification}` | `{mesh_role}` | `{produced}` | `{consumed}` | {next_step} |".format(
                repository=repository["repository"],
                classification=repository["classification"],
                mesh_role=repository["mesh_role"],
                produced=repository["produced_product_count"],
                consumed=repository["consumed_dependency_count"],
                next_step=repository["required_next_step"],
            )
        )

    lines.extend(
        [
            "",
            "## Product Maturity",
            "",
            "| Product | Producer | Classification | Wave | Lifecycle | Next step |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for product in matrix["products"]:
        lines.append(
            "| `{product_id}` | `{producer}` | `{classification}` | `{wave}` | `{lifecycle}` | {next_step} |".format(
                product_id=product["product_id"],
                producer=product["producer_repository"],
                classification=product["classification"],
                wave=product["maturity_wave"],
                lifecycle=product["lifecycle_status"],
                next_step=product["required_next_step"],
            )
        )

    return "\n".join(lines) + "\n"


def write_enterprise_mesh_maturity_matrix(
    *,
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    generated_at_utc: str = DEFAULT_GENERATED_AT_UTC,
) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    matrix = build_enterprise_mesh_maturity_matrix(
        catalog_path=catalog_path,
        generated_at_utc=generated_at_utc,
    )
    (output_directory / MATRIX_FILENAME).write_text(
        json.dumps(matrix, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_directory / MATRIX_MARKDOWN_FILENAME).write_text(
        render_enterprise_mesh_maturity_matrix_markdown(matrix),
        encoding="utf-8",
    )


def check_enterprise_mesh_maturity_matrix(
    *,
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    generated_at_utc: str = DEFAULT_GENERATED_AT_UTC,
) -> list[str]:
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temporary_directory:
        temp_output = Path(temporary_directory)
        write_enterprise_mesh_maturity_matrix(
            output_directory=temp_output,
            catalog_path=catalog_path,
            generated_at_utc=generated_at_utc,
        )
        issues: list[str] = []
        for artifact_name in (MATRIX_FILENAME, MATRIX_MARKDOWN_FILENAME):
            expected = (temp_output / artifact_name).read_text(encoding="utf-8")
            actual_path = output_directory / artifact_name
            if not actual_path.exists():
                issues.append(f"{actual_path}: generated maturity artifact is missing")
                continue
            actual = actual_path.read_text(encoding="utf-8")
            if actual != expected:
                issues.append(f"{actual_path}: generated maturity artifact is stale")
        return issues


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate or validate the RFC-0091 enterprise mesh maturity matrix."
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Domain-product catalog path.",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Directory for generated maturity matrix artifacts.",
    )
    parser.add_argument(
        "--generated-at-utc",
        default=DEFAULT_GENERATED_AT_UTC,
        help="Deterministic generated_at_utc value for artifacts.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate checked-in generated maturity matrix artifacts without writing them.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.check:
        issues = check_enterprise_mesh_maturity_matrix(
            output_directory=args.output_directory,
            catalog_path=args.catalog,
            generated_at_utc=args.generated_at_utc,
        )
        for issue in issues:
            print(issue)
        return 1 if issues else 0

    write_enterprise_mesh_maturity_matrix(
        output_directory=args.output_directory,
        catalog_path=args.catalog,
        generated_at_utc=args.generated_at_utc,
    )
    print(f"Wrote enterprise mesh maturity matrix artifacts to {args.output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
