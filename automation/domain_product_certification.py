from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from domain_product_discovery import (
    CATALOG_FILENAME,
    DEFAULT_CATALOG_PATH,
    DEFAULT_GRAPH_PATH,
    DEFAULT_OUTPUT_DIRECTORY,
    GRAPH_FILENAME,
    load_catalog,
    load_dependency_graph,
)

CERTIFICATION_REPORT_FILENAME = "domain-product-certification-report.json"
CERTIFICATION_REPORT_MARKDOWN_FILENAME = "domain-product-certification-report.md"
DEFAULT_CERTIFICATION_REPORT_PATH = (
    DEFAULT_OUTPUT_DIRECTORY / CERTIFICATION_REPORT_FILENAME
)


def _add_certification_issue(
    issues: list[dict[str, Any]],
    *,
    code: str,
    severity: str,
    subject: str,
    detail: str,
) -> None:
    issues.append(
        {
            "code": code,
            "severity": severity,
            "subject": subject,
            "detail": detail,
        }
    )


def _certification_state(issue_count: int) -> str:
    return "certified" if issue_count == 0 else "attention_required"


def _build_product_certification(
    product: dict[str, Any],
    *,
    graph_product_node_ids: set[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    product_id = product["product_id"]

    if not product.get("required_trust_metadata"):
        _add_certification_issue(
            issues,
            code="missing_product_trust_metadata",
            severity="error",
            subject=product_id,
            detail="Product declaration must include required trust metadata.",
        )
    if not product.get("approved_consumers"):
        _add_certification_issue(
            issues,
            code="missing_approved_consumers",
            severity="warning",
            subject=product_id,
            detail="Product has no approved consumers, so mesh reuse is not currently enabled.",
        )
    if f"product:{product_id}" not in graph_product_node_ids:
        _add_certification_issue(
            issues,
            code="missing_graph_product_node",
            severity="error",
            subject=product_id,
            detail="Product is missing from the generated dependency graph.",
        )

    return (
        {
            "product_id": product_id,
            "producer_repository": product["producer_repository"],
            "product_name": product["product_name"],
            "product_version": product["product_version"],
            "lifecycle_status": product["lifecycle_status"],
            "certification_state": _certification_state(len(issues)),
            "checks": {
                "trust_metadata_declared": bool(product.get("required_trust_metadata")),
                "approved_consumers_declared": bool(product.get("approved_consumers")),
                "route_references_declared": bool(product.get("current_routes")),
                "lineage_required": bool(
                    product.get("lineage_policy", {}).get("lineage_required")
                ),
                "graph_node_present": f"product:{product_id}" in graph_product_node_ids,
                "deprecation_state": product.get("deprecation_policy", {}).get(
                    "state", "unknown"
                ),
            },
            "issue_count": len(issues),
        },
        issues,
    )


def _dependency_subject(consumer_repository: str, dependency_id: str) -> str:
    return f"{consumer_repository}:{dependency_id}"


def _dependency_graph_edge_present(
    *,
    consumer_repository: str,
    dependency_id: str,
    graph_consume_edges: set[tuple[str, str]],
) -> bool:
    return (
        f"repo:{consumer_repository}",
        f"product:{dependency_id}",
    ) in graph_consume_edges


def _dependency_checks(
    *,
    consumer_repository: str,
    dependency: dict[str, Any],
    product: dict[str, Any] | None,
    graph_consume_edges: set[tuple[str, str]],
) -> dict[str, bool]:
    return {
        "product_exists": product is not None,
        "approved_by_producer": bool(
            product and consumer_repository in product.get("approved_consumers", [])
        ),
        "required_metadata_subset_of_product": bool(
            product
            and set(dependency["required_trust_metadata"])
            <= set(product.get("required_trust_metadata", []))
        ),
        "graph_consume_edge_present": _dependency_graph_edge_present(
            consumer_repository=consumer_repository,
            dependency_id=dependency["dependency_id"],
            graph_consume_edges=graph_consume_edges,
        ),
        "validation_lanes_declared": bool(dependency.get("validation_lanes")),
        "failure_posture_declared": bool(dependency.get("failure_posture")),
    }


def _append_dependency_issues(
    issues: list[dict[str, Any]],
    *,
    consumer_repository: str,
    dependency: dict[str, Any],
    product: dict[str, Any] | None,
    checks: dict[str, bool],
) -> None:
    subject = _dependency_subject(consumer_repository, dependency["dependency_id"])
    if not checks["product_exists"]:
        _add_certification_issue(
            issues,
            code="missing_dependency_product",
            severity="error",
            subject=subject,
            detail="Consumer dependency points to a product missing from the catalog.",
        )
    if product is not None and not checks["approved_by_producer"]:
        _add_certification_issue(
            issues,
            code="consumer_not_approved",
            severity="error",
            subject=subject,
            detail="Consumer dependency is not reciprocally approved by the producer.",
        )
    if product is not None and not checks["required_metadata_subset_of_product"]:
        _add_certification_issue(
            issues,
            code="consumer_requires_unpublished_trust_metadata",
            severity="error",
            subject=subject,
            detail="Consumer requires trust metadata not declared by the producer product.",
        )
    if not checks["graph_consume_edge_present"]:
        _add_certification_issue(
            issues,
            code="missing_graph_consume_edge",
            severity="error",
            subject=subject,
            detail="Consumer dependency is missing from the generated dependency graph.",
        )
    if not checks["validation_lanes_declared"]:
        _add_certification_issue(
            issues,
            code="missing_dependency_validation_lanes",
            severity="error",
            subject=subject,
            detail="Consumer dependency does not declare validation lanes.",
        )
    if not checks["failure_posture_declared"]:
        _add_certification_issue(
            issues,
            code="missing_dependency_failure_posture",
            severity="error",
            subject=subject,
            detail="Consumer dependency does not declare failure posture.",
        )


def _build_dependency_certification(
    *,
    consumer_repository: str,
    dependency: dict[str, Any],
    product: dict[str, Any] | None,
    graph_consume_edges: set[tuple[str, str]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    checks = _dependency_checks(
        consumer_repository=consumer_repository,
        dependency=dependency,
        product=product,
        graph_consume_edges=graph_consume_edges,
    )
    _append_dependency_issues(
        issues,
        consumer_repository=consumer_repository,
        dependency=dependency,
        product=product,
        checks=checks,
    )
    return (
        {
            "dependency_id": dependency["dependency_id"],
            "producer_repository": dependency["producer_repository"],
            "product_name": dependency["product_name"],
            "required_product_version": dependency["required_product_version"],
            "certification_state": _certification_state(len(issues)),
            "checks": checks,
        },
        issues,
    )


def _build_consumer_certification(
    consumer: dict[str, Any],
    *,
    products_by_id: dict[str, dict[str, Any]],
    graph_consume_edges: set[tuple[str, str]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    dependency_certifications: list[dict[str, Any]] = []
    consumer_repository = consumer["consumer_repository"]

    for dependency in consumer["dependencies"]:
        dependency_id = dependency["dependency_id"]
        product = products_by_id.get(dependency_id)
        certification, dependency_issues = _build_dependency_certification(
            consumer_repository=consumer_repository,
            dependency=dependency,
            product=product,
            graph_consume_edges=graph_consume_edges,
        )
        dependency_certifications.append(certification)
        issues.extend(dependency_issues)

    return (
        {
            "consumer_repository": consumer_repository,
            "dependency_count": consumer["dependency_count"],
            "certification_state": _certification_state(len(issues)),
            "issue_count": len(issues),
            "dependencies": dependency_certifications,
        },
        issues,
    )


def build_certification_report(
    catalog: dict[str, Any],
    graph: dict[str, Any],
    *,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at_utc or catalog["generated_at_utc"]
    graph_product_node_ids = {
        node["node_id"]
        for node in graph.get("nodes", [])
        if node.get("node_type") == "domain_product"
    }
    graph_consume_edges = {
        (edge["from"], edge["to"])
        for edge in graph.get("edges", [])
        if edge.get("edge_type") == "consumes"
    }
    products_by_id = {product["product_id"]: product for product in catalog["products"]}
    issues: list[dict[str, Any]] = []

    product_certifications = []
    for product in catalog["products"]:
        certification, product_issues = _build_product_certification(
            product,
            graph_product_node_ids=graph_product_node_ids,
        )
        product_certifications.append(certification)
        issues.extend(product_issues)

    consumer_certifications = []
    for consumer in catalog["consumers"]:
        certification, consumer_issues = _build_consumer_certification(
            consumer,
            products_by_id=products_by_id,
            graph_consume_edges=graph_consume_edges,
        )
        consumer_certifications.append(certification)
        issues.extend(consumer_issues)

    manifest_repositories = catalog.get("source_manifest", {}).get("repositories", [])
    included_repositories = [
        entry["repository"]
        for entry in manifest_repositories
        if entry.get("catalog_inclusion") == "included"
    ]
    pending_repositories = [
        entry["repository"]
        for entry in manifest_repositories
        if entry.get("catalog_inclusion") != "included"
    ]

    return {
        "contract_id": "lotus-domain-product-certification-report",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0084", "RFC-0087", "RFC-0088"],
        "generated_at_utc": generated_at,
        "source_catalog": CATALOG_FILENAME,
        "source_graph": GRAPH_FILENAME,
        "summary": {
            "certification_state": _certification_state(len(issues)),
            "product_count": catalog["product_count"],
            "dependency_count": catalog["dependency_count"],
            "producer_repository_count": catalog["repository_count"],
            "included_repository_count": len(included_repositories),
            "pending_repository_count": len(pending_repositories),
            "issue_count": len(issues),
        },
        "source_manifest_posture": {
            "included_repositories": included_repositories,
            "pending_repositories": pending_repositories,
        },
        "product_certifications": product_certifications,
        "consumer_certifications": consumer_certifications,
        "issues": sorted(
            issues,
            key=lambda issue: (issue["severity"], issue["code"], issue["subject"]),
        ),
    }


def render_certification_report_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    product_rows = [
        "| Product | Producer | State | Issues | Trust Metadata | Routes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for product in report["product_certifications"]:
        checks = product["checks"]
        product_rows.append(
            "| "
            f"`{product['product_name']}` | "
            f"`{product['producer_repository']}` | "
            f"`{product['certification_state']}` | "
            f"`{product['issue_count']}` | "
            f"`{checks['trust_metadata_declared']}` | "
            f"`{checks['route_references_declared']}` |"
        )

    consumer_rows = [
        "| Consumer | State | Dependencies | Issues |",
        "| --- | --- | --- | --- |",
    ]
    for consumer in report["consumer_certifications"]:
        consumer_rows.append(
            "| "
            f"`{consumer['consumer_repository']}` | "
            f"`{consumer['certification_state']}` | "
            f"`{consumer['dependency_count']}` | "
            f"`{consumer['issue_count']}` |"
        )

    issue_rows = [
        "| Severity | Code | Subject | Detail |",
        "| --- | --- | --- | --- |",
    ]
    if report["issues"]:
        for issue in report["issues"]:
            issue_rows.append(
                "| "
                f"`{issue['severity']}` | "
                f"`{issue['code']}` | "
                f"`{issue['subject']}` | "
                f"{issue['detail']} |"
            )
    else:
        issue_rows.append(
            "| `none` | `none` | `none` | No certification issues found. |"
        )

    return "\n".join(
        [
            "# Lotus Domain Product Certification Report",
            "",
            "This file is generated from the governed domain-product catalog and dependency graph.",
            "",
            f"- Generated at UTC: `{report['generated_at_utc']}`",
            f"- Certification state: `{summary['certification_state']}`",
            f"- Product count: `{summary['product_count']}`",
            f"- Dependency count: `{summary['dependency_count']}`",
            f"- Included repositories: `{summary['included_repository_count']}`",
            f"- Pending repositories: `{summary['pending_repository_count']}`",
            f"- Issue count: `{summary['issue_count']}`",
            "",
            "## Product Certification",
            "",
            *product_rows,
            "",
            "## Consumer Certification",
            "",
            *consumer_rows,
            "",
            "## Issues",
            "",
            *issue_rows,
            "",
        ]
    )


def write_certification_report(
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
    *,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    graph_path: Path = DEFAULT_GRAPH_PATH,
    generated_at_utc: str | None = None,
) -> None:
    catalog = load_catalog(catalog_path)
    graph = load_dependency_graph(graph_path)
    report = build_certification_report(
        catalog,
        graph,
        generated_at_utc=generated_at_utc,
    )
    markdown = render_certification_report_markdown(report)
    output_directory.mkdir(parents=True, exist_ok=True)
    (output_directory / CERTIFICATION_REPORT_FILENAME).write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_directory / CERTIFICATION_REPORT_MARKDOWN_FILENAME).write_text(
        markdown,
        encoding="utf-8",
    )
