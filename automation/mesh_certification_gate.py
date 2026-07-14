from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from domain_product_discovery import (
    CATALOG_FILENAME,
    DEFAULT_CATALOG_PATH,
    GRAPH_FILENAME,
    load_catalog,
    write_discovery_artifacts,
)
from generate_live_trust_certification import (
    build_live_trust_certification_report_from_paths,
    render_live_trust_certification_markdown,
)
from validate_trust_telemetry import (
    _iter_telemetry_paths,
    _load_validation_context,
)
from validate_mesh_slo_policies import (
    DEFAULT_SLO_POLICY_DIRECTORY,
    evaluate_mesh_slo_violations,
    validate_mesh_slo_policies,
)
from validate_mesh_access_policies import (
    DEFAULT_ACCESS_POLICY_DIRECTORY,
    validate_mesh_access_policies,
)
from generate_mesh_evidence_pack import (
    DEFAULT_EVIDENCE_POLICY_DIRECTORY,
    validate_mesh_evidence_policies,
)
from generate_enterprise_mesh_operating_report import (
    DEFAULT_HISTORY_DIRECTORY as DEFAULT_OPERATING_HISTORY_DIRECTORY,
    build_report_from_paths,
    write_enterprise_mesh_operating_report,
)
from mesh_maturity_scope import (
    REQUIRED_PRODUCTS,
    default_runtime_telemetry_directories,
    default_static_telemetry_directories,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_MANIFEST_PATH = (
    ROOT
    / "platform-contracts"
    / "domain-data-products"
    / "domain-product-source-manifest.v1.json"
)
DEFAULT_GRAPH_PATH = ROOT / "generated" / "domain-product-dependency-graph.json"
DEFAULT_OUTPUT_DIRECTORY = ROOT / "output" / "mesh-certification"
DEFAULT_GATEWAY_ROOT = ROOT.parent / "lotus-gateway"
DEFAULT_WORKBENCH_ROOT = ROOT.parent / "lotus-workbench"
DEFAULT_TELEMETRY_DIRECTORIES = default_static_telemetry_directories()
DEFAULT_RUNTIME_TELEMETRY_DIRECTORIES = default_runtime_telemetry_directories()
MESH_CERTIFICATION_STATUS_FILENAME = "mesh-certification-status.json"
MESH_CERTIFICATION_MARKDOWN_FILENAME = "mesh-certification-status.md"
MESH_CERTIFICATION_ISSUES_FILENAME = "mesh-certification-issues.json"
ENTERPRISE_MESH_CERTIFICATION_STATUS_FILENAME = (
    "enterprise-mesh-certification-status.json"
)
ENTERPRISE_MESH_CERTIFICATION_MARKDOWN_FILENAME = (
    "enterprise-mesh-certification-status.md"
)
ENTERPRISE_MESH_CERTIFICATION_ISSUES_FILENAME = (
    "enterprise-mesh-certification-issues.json"
)
LIVE_CERTIFICATION_CODE_MAP = {
    "invalid_trust_telemetry": "invalid_telemetry",
    "freshness_not_current": "stale_telemetry",
}
BLOCKING_REQUIRED_PRODUCT_CODES = {
    "missing_telemetry",
    "invalid_telemetry",
    "stale_telemetry",
    "product_blocked",
    "completeness_attention_required",
    "reconciliation_attention_required",
    "data_quality_attention_required",
    "lineage_not_materialized",
    "mesh_slo_freshness_violation",
    "mesh_slo_completeness_violation",
    "mesh_slo_reconciliation_violation",
    "mesh_slo_data_quality_violation",
    "mesh_slo_lineage_violation",
    "mesh_evidence_policy_drift",
    "mesh_lifecycle_drift",
    "catalog_drift",
    "gateway_publication_drift",
    "workbench_consumption_drift",
}
WARNING_SCOPED_PRODUCT_BLOCKS = {
    (
        "lotus-report:ClientReportEvidencePack:v1",
        "analytics_enriched_evidence_certification",
    )
}
ISSUE_FAMILY_BY_CODE = {
    "missing_telemetry": "telemetry",
    "invalid_telemetry": "telemetry",
    "stale_telemetry": "telemetry",
    "product_blocked": "telemetry",
    "completeness_attention_required": "telemetry",
    "reconciliation_attention_required": "telemetry",
    "data_quality_attention_required": "telemetry",
    "lineage_not_materialized": "telemetry",
    "mesh_slo_policy_drift": "slo",
    "mesh_slo_freshness_violation": "slo",
    "mesh_slo_completeness_violation": "slo",
    "mesh_slo_reconciliation_violation": "slo",
    "mesh_slo_data_quality_violation": "slo",
    "mesh_slo_lineage_violation": "slo",
    "mesh_access_policy_drift": "access",
    "mesh_evidence_policy_drift": "evidence",
    "mesh_lifecycle_drift": "lifecycle",
    "catalog_drift": "catalog",
    "gateway_publication_drift": "gateway",
    "workbench_consumption_drift": "workbench",
}
MATURITY_CHECK_FAMILIES = [
    "telemetry",
    "slo",
    "access",
    "lifecycle",
    "evidence",
    "catalog",
    "gateway",
    "workbench",
]
GateMode = Literal["advisory", "blocking"]
CatalogSource = Literal["checked-in", "current-repo-native", "explicit"]


@dataclass(frozen=True)
class MeshCertificationIssue:
    code: str
    severity: Literal["error", "warning", "info"]
    producer_repository: str
    product_id: str | None
    remediation: str
    source_evidence_path: str


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _issue(
    issues: list[MeshCertificationIssue],
    *,
    code: str,
    severity: Literal["error", "warning", "info"],
    producer_repository: str = "lotus-platform",
    product_id: str | None = None,
    remediation: str,
    source_evidence_path: Path | str,
) -> None:
    issues.append(
        MeshCertificationIssue(
            code=code,
            severity=severity,
            producer_repository=producer_repository,
            product_id=product_id,
            remediation=remediation,
            source_evidence_path=str(source_evidence_path).replace("\\", "/"),
        )
    )


def _iter_default_telemetry_paths(telemetry_paths: list[Path]) -> list[Path]:
    if telemetry_paths:
        discovered: list[Path] = []
        for path in telemetry_paths:
            discovered.extend(_iter_telemetry_paths(path))
        return sorted(set(discovered))

    runtime_paths: list[Path] = []
    runtime_product_ids: set[str] = set()
    for directory in DEFAULT_RUNTIME_TELEMETRY_DIRECTORIES:
        if not directory.exists():
            continue
        for path in _iter_telemetry_paths(directory):
            runtime_paths.append(path)
            try:
                product_id = _load_json(path).get("product_id")
            except (json.JSONDecodeError, OSError):
                continue
            if isinstance(product_id, str) and product_id:
                runtime_product_ids.add(product_id)

    fixture_paths: list[Path] = []
    for directory in DEFAULT_TELEMETRY_DIRECTORIES:
        if not directory.exists():
            continue
        for path in _iter_telemetry_paths(directory):
            try:
                product_id = _load_json(path).get("product_id")
            except (json.JSONDecodeError, OSError):
                fixture_paths.append(path)
                continue
            if product_id not in runtime_product_ids:
                fixture_paths.append(path)
    return sorted(set([*runtime_paths, *fixture_paths]))


def _load_telemetry_payloads(
    telemetry_paths: list[Path],
) -> tuple[
    dict[str, tuple[Path, dict[str, Any]]],
    list[Path],
    list[MeshCertificationIssue],
]:
    payloads: dict[str, tuple[Path, dict[str, Any]]] = {}
    valid_paths: list[Path] = []
    issues: list[MeshCertificationIssue] = []
    for telemetry_path in telemetry_paths:
        try:
            payload = _load_json(telemetry_path)
        except json.JSONDecodeError as exc:
            _issue(
                issues,
                code="invalid_telemetry",
                severity="error",
                remediation=f"Fix invalid JSON in trust telemetry snapshot: {exc}",
                source_evidence_path=telemetry_path,
            )
            continue
        product_id = str(payload.get("product_id", ""))
        if product_id:
            if product_id in payloads:
                _issue(
                    issues,
                    code="invalid_telemetry",
                    severity="error",
                    producer_repository=str(payload.get("producer_repository", "")),
                    product_id=product_id,
                    remediation=(
                        "Remove duplicate trust telemetry snapshots for this product; "
                        "the mesh gate requires one authoritative snapshot per product."
                    ),
                    source_evidence_path=telemetry_path,
                )
                continue
            payloads[product_id] = (telemetry_path, payload)
            valid_paths.append(telemetry_path)
    return payloads, valid_paths, issues


def _catalog_products_by_id(catalog_path: Path) -> dict[str, dict[str, Any]]:
    catalog = load_catalog(catalog_path)
    return {product["product_id"]: product for product in catalog.get("products", [])}


def _resolve_catalog_inputs(
    *,
    catalog_source: CatalogSource,
    explicit_catalog_path: Path | None,
    explicit_dependency_graph_path: Path | None,
    source_manifest_path: Path,
    output_directory: Path,
    generated_at_utc: str,
) -> tuple[Path, Path, CatalogSource]:
    if catalog_source == "current-repo-native":
        if explicit_catalog_path is not None or explicit_dependency_graph_path is not None:
            raise ValueError(
                "--catalog-source current-repo-native cannot be combined with "
                "--catalog-path or --dependency-graph-path"
            )
        discovery_directory = output_directory / "current-domain-product-discovery"
        write_discovery_artifacts(
            discovery_directory,
            generated_at_utc=generated_at_utc,
            source_manifest_path=source_manifest_path,
        )
        return (
            discovery_directory / CATALOG_FILENAME,
            discovery_directory / GRAPH_FILENAME,
            "current-repo-native",
        )

    if explicit_catalog_path is not None:
        return (
            explicit_catalog_path,
            explicit_dependency_graph_path
            or explicit_catalog_path.parent
            / GRAPH_FILENAME,
            "explicit",
        )

    if explicit_dependency_graph_path is not None:
        raise ValueError("--dependency-graph-path requires --catalog-path")

    return DEFAULT_CATALOG_PATH, DEFAULT_GRAPH_PATH, "checked-in"


def _validate_required_products_in_catalog(
    *,
    products_by_id: dict[str, dict[str, Any]],
    issues: list[MeshCertificationIssue],
    catalog_path: Path,
) -> None:
    for product_id, producer_repository in REQUIRED_PRODUCTS.items():
        product = products_by_id.get(product_id)
        if product is None:
            _issue(
                issues,
                code="catalog_drift",
                severity="error",
                producer_repository=producer_repository,
                product_id=product_id,
                remediation=(
                    "Regenerate domain-product discovery artifacts or restore the "
                    "required first-wave product declaration."
                ),
                source_evidence_path=catalog_path,
            )
            continue
        if product.get("producer_repository") != producer_repository:
            _issue(
                issues,
                code="catalog_drift",
                severity="error",
                producer_repository=producer_repository,
                product_id=product_id,
                remediation="Restore catalog producer identity for the required product.",
                source_evidence_path=catalog_path,
            )


def _validate_required_product_lifecycle(
    *,
    products_by_id: dict[str, dict[str, Any]],
    issues: list[MeshCertificationIssue],
    catalog_path: Path,
    gate_mode: GateMode,
) -> None:
    for product_id, producer_repository in REQUIRED_PRODUCTS.items():
        product = products_by_id.get(product_id)
        if product is None:
            continue
        deprecation_policy = product.get("deprecation_policy", {})
        lifecycle_status = product.get("lifecycle_status")
        deprecation_state = (
            deprecation_policy.get("state")
            if isinstance(deprecation_policy, dict)
            else None
        )
        successor_product = (
            deprecation_policy.get("successor_product")
            if isinstance(deprecation_policy, dict)
            else None
        )
        if (
            lifecycle_status == "active"
            and deprecation_state == "not_deprecated"
            and successor_product is None
        ):
            continue
        _issue(
            issues,
            code="mesh_lifecycle_drift",
            severity="error" if gate_mode == "blocking" else "warning",
            producer_repository=producer_repository,
            product_id=product_id,
            remediation=(
                "Restore the maturity-wave product to active/not-deprecated posture "
                "or add a governed successor and consumer-impact migration plan before "
                "allowing the product through enterprise certification."
            ),
            source_evidence_path=catalog_path,
        )


def _validate_required_products_in_graph(
    *,
    dependency_graph_path: Path,
    issues: list[MeshCertificationIssue],
) -> None:
    try:
        graph = _load_json(dependency_graph_path)
    except FileNotFoundError:
        _issue(
            issues,
            code="catalog_drift",
            severity="error",
            remediation="Regenerate the domain-product dependency graph.",
            source_evidence_path=dependency_graph_path,
        )
        return
    except json.JSONDecodeError as exc:
        _issue(
            issues,
            code="catalog_drift",
            severity="error",
            remediation=f"Fix invalid JSON in the dependency graph: {exc}",
            source_evidence_path=dependency_graph_path,
        )
        return

    graph_product_ids = {
        node.get("product_id")
        for node in graph.get("nodes", [])
        if isinstance(node, dict) and node.get("node_type") == "domain_product"
    }
    for product_id, producer_repository in REQUIRED_PRODUCTS.items():
        if product_id in graph_product_ids:
            continue
        _issue(
            issues,
            code="catalog_drift",
            severity="error",
            producer_repository=producer_repository,
            product_id=product_id,
            remediation=(
                "Regenerate the domain-product dependency graph so it includes "
                "the required first-wave product."
            ),
            source_evidence_path=dependency_graph_path,
        )


def _validate_source_manifest(
    *,
    source_manifest_path: Path,
    issues: list[MeshCertificationIssue],
) -> None:
    manifest = _load_json(source_manifest_path)
    repositories = {
        repository.get("repository"): repository
        for repository in manifest.get("repositories", [])
        if isinstance(repository, dict)
    }
    for producer_repository in sorted(set(REQUIRED_PRODUCTS.values())):
        entry = repositories.get(producer_repository)
        if entry is None:
            _issue(
                issues,
                code="catalog_drift",
                severity="error",
                producer_repository=producer_repository,
                product_id=None,
                remediation="Add the required producer repository to the source manifest.",
                source_evidence_path=source_manifest_path,
            )
            continue
        if entry.get("source_mode") != "repo_native":
            _issue(
                issues,
                code="catalog_drift",
                severity="error",
                producer_repository=producer_repository,
                product_id=None,
                remediation="Promote the producer source manifest entry to repo_native mode.",
                source_evidence_path=source_manifest_path,
            )


def _issue_from_live_certification(
    raw_issue: dict[str, str],
    *,
    telemetry_payloads: dict[str, tuple[Path, dict[str, Any]]],
    gate_mode: GateMode,
) -> MeshCertificationIssue:
    product_id = raw_issue["product_id"]
    telemetry_path, payload = telemetry_payloads.get(product_id, (Path("unknown"), {}))
    code = LIVE_CERTIFICATION_CODE_MAP.get(raw_issue["code"], raw_issue["code"])
    required_product = product_id in REQUIRED_PRODUCTS
    severity: Literal["error", "warning", "info"] = "warning"
    blocking = payload.get("blocking") if isinstance(payload, dict) else {}
    is_warning_scoped_block = (
        code == "product_blocked"
        and isinstance(blocking, dict)
        and bool(blocking.get("blocked_reason"))
        and (product_id, str(blocking.get("blocking_scope")))
        in WARNING_SCOPED_PRODUCT_BLOCKS
    )
    if (
        required_product
        and gate_mode == "blocking"
        and code in BLOCKING_REQUIRED_PRODUCT_CODES
        and not is_warning_scoped_block
    ):
        severity = "error"
    return MeshCertificationIssue(
        code=code,
        severity=severity,
        producer_repository=str(
            payload.get("producer_repository")
            or REQUIRED_PRODUCTS.get(product_id)
            or "unknown"
        ),
        product_id=product_id,
        remediation=raw_issue["detail"],
        source_evidence_path=telemetry_path.as_posix(),
    )


def _validate_required_telemetry(
    *,
    telemetry_payloads: dict[str, tuple[Path, dict[str, Any]]],
    issues: list[MeshCertificationIssue],
    gate_mode: GateMode,
) -> None:
    for product_id, producer_repository in REQUIRED_PRODUCTS.items():
        if product_id in telemetry_payloads:
            continue
        _issue(
            issues,
            code="missing_telemetry",
            severity="error" if gate_mode == "blocking" else "warning",
            producer_repository=producer_repository,
            product_id=product_id,
            remediation=(
                "Add or refresh the first-wave RFC-0087 trust telemetry snapshot "
                "for this required product."
            ),
            source_evidence_path="../"
            + producer_repository
            + "/contracts/trust-telemetry",
        )


def _validate_mesh_slo_policy_and_telemetry(
    *,
    telemetry_payloads: dict[str, tuple[Path, dict[str, Any]]],
    catalog_path: Path,
    slo_policy_path: Path,
    issues: list[MeshCertificationIssue],
    gate_mode: GateMode,
) -> None:
    policy_issues = validate_mesh_slo_policies(
        slo_policy_path,
        catalog_path=catalog_path,
    )
    for policy_issue in policy_issues:
        _issue(
            issues,
            code="mesh_slo_policy_drift",
            severity="error" if gate_mode == "blocking" else "warning",
            remediation=policy_issue,
            source_evidence_path=slo_policy_path,
        )

    for violation in evaluate_mesh_slo_violations(
        telemetry_payloads=telemetry_payloads,
        policy_path=slo_policy_path,
    ):
        severity: Literal["error", "warning", "info"] = (
            "error"
            if gate_mode == "blocking" and violation["severity"] == "blocking"
            else "warning"
        )
        _issue(
            issues,
            code=violation["code"],
            severity=severity,
            producer_repository=violation["producer_repository"],
            product_id=violation["product_id"],
            remediation=violation["remediation"],
            source_evidence_path=violation["policy_path"],
        )


def _validate_mesh_access_policy(
    *,
    access_policy_path: Path,
    catalog_path: Path,
    issues: list[MeshCertificationIssue],
    gate_mode: GateMode,
) -> None:
    access_issues = validate_mesh_access_policies(
        access_policy_path,
        catalog_path=catalog_path,
    )
    for access_issue in access_issues:
        _issue(
            issues,
            code="mesh_access_policy_drift",
            severity="error" if gate_mode == "blocking" else "warning",
            remediation=access_issue,
            source_evidence_path=access_policy_path,
        )


def _validate_mesh_evidence_policy(
    *,
    evidence_policy_path: Path,
    catalog_path: Path,
    issues: list[MeshCertificationIssue],
    gate_mode: GateMode,
) -> None:
    evidence_issues = validate_mesh_evidence_policies(
        evidence_policy_path,
        catalog_path=catalog_path,
    )
    for evidence_issue in evidence_issues:
        _issue(
            issues,
            code="mesh_evidence_policy_drift",
            severity="error" if gate_mode == "blocking" else "warning",
            remediation=evidence_issue,
            source_evidence_path=evidence_policy_path,
        )


def _check_gateway_publication(
    *,
    gateway_root: Path,
    require_sibling_repos: bool,
    issues: list[MeshCertificationIssue],
) -> None:
    router_root = gateway_root / "src" / "app" / "routers"
    router_contracts = [
        (
            router_root / "domain_product_catalog.py",
            ['prefix="/api/v1/domain-products"', '"/catalog"'],
        ),
        (
            router_root / "domain_product_detail.py",
            [
                'prefix="/api/v1/domain-products"',
                '"/products/{producer_repository}/{product_name}/{product_version}"',
            ],
        ),
        (
            router_root / "domain_product_graph.py",
            ['prefix="/api/v1/domain-products"', '"/dependency-graph"'],
        ),
        (
            router_root / "domain_product_trust.py",
            ['prefix="/api/v1/domain-products"', '"/trust-certification"'],
        ),
    ]
    service_path = (
        gateway_root / "src" / "app" / "services" / "domain_product_catalog_service.py"
    )
    if not gateway_root.exists():
        _issue(
            issues,
            code="gateway_publication_drift",
            severity="error" if require_sibling_repos else "info",
            remediation=(
                "Checkout lotus-gateway next to lotus-platform or disable sibling "
                "publication checks for platform-only CI."
            ),
            source_evidence_path=gateway_root,
        )
        return
    required_paths = [path for path, _ in router_contracts] + [service_path]
    missing_paths = [path for path in required_paths if not path.exists()]
    if missing_paths:
        for path in missing_paths:
            _issue(
                issues,
                code="gateway_publication_drift",
                severity="error",
                producer_repository="lotus-gateway",
                remediation="Restore the gateway domain-product publication module set.",
                source_evidence_path=path,
            )
        return

    for router_path, required_fragments in router_contracts:
        router_text = router_path.read_text(encoding="utf-8")
        for fragment in required_fragments:
            if fragment not in router_text:
                _issue(
                    issues,
                    code="gateway_publication_drift",
                    severity="error",
                    producer_repository="lotus-gateway",
                    remediation=f"Restore gateway route contract fragment: {fragment}",
                    source_evidence_path=router_path,
                )


def _check_workbench_consumption(
    *,
    workbench_root: Path,
    require_sibling_repos: bool,
    issues: list[MeshCertificationIssue],
) -> None:
    page_path = workbench_root / "src" / "app" / "data-products" / "page.tsx"
    api_path = workbench_root / "src" / "features" / "domain-products" / "api.ts"
    if not workbench_root.exists():
        _issue(
            issues,
            code="workbench_consumption_drift",
            severity="error" if require_sibling_repos else "info",
            producer_repository="lotus-workbench",
            remediation=(
                "Checkout lotus-workbench next to lotus-platform or disable sibling "
                "publication checks for platform-only CI."
            ),
            source_evidence_path=workbench_root,
        )
        return
    missing_paths = [path for path in (page_path, api_path) if not path.exists()]
    if missing_paths:
        for path in missing_paths:
            _issue(
                issues,
                code="workbench_consumption_drift",
                severity="error",
                producer_repository="lotus-workbench",
                remediation="Restore the Workbench domain-product discovery surface.",
                source_evidence_path=path,
            )
        return

    api_text = api_path.read_text(encoding="utf-8")
    if 'BFF_PROXY_BASE = "/api/bff/api/v1"' not in api_text:
        _issue(
            issues,
            code="workbench_consumption_drift",
            severity="error",
            producer_repository="lotus-workbench",
            remediation="Restore Workbench gateway/BFF-only domain-product consumption.",
            source_evidence_path=api_path,
        )
    forbidden_fragments = [
        "generated/domain-product",
        "platform-contracts/domain-data-products",
        "output/trust-certification",
    ]
    for fragment in forbidden_fragments:
        if fragment in api_text:
            _issue(
                issues,
                code="workbench_consumption_drift",
                severity="error",
                producer_repository="lotus-workbench",
                remediation=(
                    "Remove direct platform-file consumption from Workbench discovery; "
                    "consume gateway/BFF APIs only."
                ),
                source_evidence_path=api_path,
            )


def _certification_state(issues: list[MeshCertificationIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "failed"
    if any(issue.severity == "warning" for issue in issues):
        return "certified_with_warnings"
    return "certified"


def _issue_family(issue: MeshCertificationIssue | dict[str, Any]) -> str:
    code = issue.code if isinstance(issue, MeshCertificationIssue) else issue["code"]
    return ISSUE_FAMILY_BY_CODE.get(code, "unknown")


def _issue_family_summary(
    issues: list[MeshCertificationIssue],
) -> dict[str, dict[str, int]]:
    family_summary = {
        family: {"error_count": 0, "warning_count": 0, "info_count": 0}
        for family in MATURITY_CHECK_FAMILIES
    }
    for issue in issues:
        family = _issue_family(issue)
        family_summary.setdefault(
            family, {"error_count": 0, "warning_count": 0, "info_count": 0}
        )
        family_summary[family][f"{issue.severity}_count"] += 1
    return family_summary


def _maturity_check_status(
    issues: list[MeshCertificationIssue],
) -> list[dict[str, Any]]:
    by_family = _issue_family_summary(issues)
    statuses = []
    for family in MATURITY_CHECK_FAMILIES:
        counts = by_family[family]
        if counts["error_count"]:
            state = "failed"
        elif counts["warning_count"]:
            state = "attention_required"
        else:
            state = "passed"
        statuses.append({"family": family, "state": state, **counts})
    return statuses


def _summary(
    issues: list[MeshCertificationIssue], required_products: list[dict[str, Any]]
) -> dict[str, Any]:
    issue_family_summary = _issue_family_summary(issues)
    return {
        "certification_state": _certification_state(issues),
        "required_product_count": len(required_products),
        "certified_required_product_count": sum(
            1
            for product in required_products
            if product["certification_state"] == "certified"
        ),
        "attention_required_product_count": sum(
            1
            for product in required_products
            if product["certification_state"] != "certified"
        ),
        "issue_count": len(issues),
        "error_count": sum(1 for issue in issues if issue.severity == "error"),
        "warning_count": sum(1 for issue in issues if issue.severity == "warning"),
        "info_count": sum(1 for issue in issues if issue.severity == "info"),
        "missing_telemetry_count": sum(
            1 for issue in issues if issue.code == "missing_telemetry"
        ),
        "stale_telemetry_count": sum(
            1 for issue in issues if issue.code == "stale_telemetry"
        ),
        "blocked_product_count": sum(
            1 for issue in issues if issue.code == "product_blocked"
        ),
        "mesh_slo_violation_count": sum(
            1 for issue in issues if issue.code.startswith("mesh_slo_")
        ),
        "mesh_access_issue_count": sum(
            1 for issue in issues if _issue_family(issue) == "access"
        ),
        "mesh_evidence_issue_count": sum(
            1 for issue in issues if _issue_family(issue) == "evidence"
        ),
        "mesh_lifecycle_issue_count": sum(
            1 for issue in issues if _issue_family(issue) == "lifecycle"
        ),
        "issue_family_summary": issue_family_summary,
    }


def _required_product_status(
    *,
    live_report: dict[str, Any],
    issues: list[MeshCertificationIssue],
) -> list[dict[str, Any]]:
    live_by_product = {
        certification["product_id"]: certification
        for certification in live_report.get("product_certifications", [])
    }
    statuses = []
    for product_id, producer_repository in REQUIRED_PRODUCTS.items():
        product_issues = [issue for issue in issues if issue.product_id == product_id]
        live = live_by_product.get(product_id, {})
        statuses.append(
            {
                "product_id": product_id,
                "producer_repository": producer_repository,
                "certification_state": "certified"
                if not product_issues
                else "attention_required",
                "freshness_state": live.get("freshness_state"),
                "completeness_status": live.get("completeness_status"),
                "reconciliation_status": live.get("reconciliation_status"),
                "data_quality_status": live.get("data_quality_status"),
                "issue_count": len(product_issues),
            }
        )
    return statuses


def build_mesh_certification_status(
    *,
    telemetry_paths: list[Path] | None = None,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    catalog_source: CatalogSource = "checked-in",
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
    dependency_graph_path: Path = DEFAULT_GRAPH_PATH,
    slo_policy_path: Path = DEFAULT_SLO_POLICY_DIRECTORY,
    access_policy_path: Path = DEFAULT_ACCESS_POLICY_DIRECTORY,
    evidence_policy_path: Path = DEFAULT_EVIDENCE_POLICY_DIRECTORY,
    gateway_root: Path = DEFAULT_GATEWAY_ROOT,
    workbench_root: Path = DEFAULT_WORKBENCH_ROOT,
    gate_mode: GateMode,
    generated_at_utc: str,
    require_sibling_repos: bool = False,
    check_publication_surfaces: bool = True,
) -> dict[str, Any]:
    issues: list[MeshCertificationIssue] = []
    discovered_telemetry_paths = _iter_default_telemetry_paths(telemetry_paths or [])
    telemetry_payloads, valid_telemetry_paths, telemetry_issues = (
        _load_telemetry_payloads(discovered_telemetry_paths)
    )
    issues.extend(telemetry_issues)
    context = _load_validation_context(catalog_path=catalog_path)
    products_by_id = _catalog_products_by_id(catalog_path)
    live_report = build_live_trust_certification_report_from_paths(
        valid_telemetry_paths,
        source_telemetry_path="mesh-certification:first-wave-telemetry",
        generated_at_utc=generated_at_utc,
        context=context,
    )

    _validate_source_manifest(source_manifest_path=source_manifest_path, issues=issues)
    _validate_required_products_in_catalog(
        products_by_id=products_by_id,
        issues=issues,
        catalog_path=catalog_path,
    )
    _validate_required_product_lifecycle(
        products_by_id=products_by_id,
        issues=issues,
        catalog_path=catalog_path,
        gate_mode=gate_mode,
    )
    _validate_required_products_in_graph(
        dependency_graph_path=dependency_graph_path,
        issues=issues,
    )
    _validate_required_telemetry(
        telemetry_payloads=telemetry_payloads,
        issues=issues,
        gate_mode=gate_mode,
    )
    _validate_mesh_slo_policy_and_telemetry(
        telemetry_payloads=telemetry_payloads,
        catalog_path=catalog_path,
        slo_policy_path=slo_policy_path,
        issues=issues,
        gate_mode=gate_mode,
    )
    _validate_mesh_access_policy(
        access_policy_path=access_policy_path,
        catalog_path=catalog_path,
        issues=issues,
        gate_mode=gate_mode,
    )
    _validate_mesh_evidence_policy(
        evidence_policy_path=evidence_policy_path,
        catalog_path=catalog_path,
        issues=issues,
        gate_mode=gate_mode,
    )
    issues.extend(
        _issue_from_live_certification(
            raw_issue,
            telemetry_payloads=telemetry_payloads,
            gate_mode=gate_mode,
        )
        for raw_issue in live_report.get("issues", [])
    )
    if check_publication_surfaces:
        _check_gateway_publication(
            gateway_root=gateway_root,
            require_sibling_repos=require_sibling_repos,
            issues=issues,
        )
        _check_workbench_consumption(
            workbench_root=workbench_root,
            require_sibling_repos=require_sibling_repos,
            issues=issues,
        )

    required_products = _required_product_status(live_report=live_report, issues=issues)
    resolved_catalog_source: CatalogSource = catalog_source
    if catalog_source == "checked-in" and catalog_path != DEFAULT_CATALOG_PATH:
        resolved_catalog_source = "explicit"
    sorted_issues = sorted(
        issues,
        key=lambda issue: (
            {"error": 0, "warning": 1, "info": 2}[issue.severity],
            issue.producer_repository,
            issue.product_id or "",
            issue.code,
        ),
    )
    return {
        "contract_id": "lotus-mesh-certification-status",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0089", "RFC-0091"],
        "generated_at_utc": generated_at_utc,
        "gate_mode": gate_mode,
        "certification_state": _certification_state(sorted_issues),
        "required_products": required_products,
        "maturity_check_families": _maturity_check_status(sorted_issues),
        "summary": _summary(sorted_issues, required_products),
        "issues": [asdict(issue) for issue in sorted_issues],
        "source_artifacts": {
            "catalog_source": resolved_catalog_source,
            "source_manifest": source_manifest_path.as_posix(),
            "catalog": catalog_path.as_posix(),
            "dependency_graph": dependency_graph_path.as_posix(),
            "slo_policy_path": slo_policy_path.as_posix(),
            "access_policy_path": access_policy_path.as_posix(),
            "evidence_policy_path": evidence_policy_path.as_posix(),
            "telemetry_inputs": [
                path.as_posix() for path in discovered_telemetry_paths
            ],
            "gateway_root": gateway_root.as_posix(),
            "workbench_root": workbench_root.as_posix(),
        },
        "live_trust_certification": live_report,
    }


def render_mesh_certification_markdown(status: dict[str, Any]) -> str:
    summary = status["summary"]
    product_rows = [
        "| Product | Producer | State | Freshness | Completeness | Reconciliation | Data Quality | Issues |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for product in status["required_products"]:
        product_rows.append(
            "| "
            f"`{product['product_id']}` | "
            f"`{product['producer_repository']}` | "
            f"`{product['certification_state']}` | "
            f"`{product.get('freshness_state')}` | "
            f"`{product.get('completeness_status')}` | "
            f"`{product.get('reconciliation_status')}` | "
            f"`{product.get('data_quality_status')}` | "
            f"`{product['issue_count']}` |"
        )

    issue_rows = [
        "| Severity | Family | Code | Producer | Product | Remediation | Evidence |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if status["issues"]:
        for issue in status["issues"]:
            issue_rows.append(
                "| "
                f"`{issue['severity']}` | "
                f"`{_issue_family(issue)}` | "
                f"`{issue['code']}` | "
                f"`{issue['producer_repository']}` | "
                f"`{issue.get('product_id')}` | "
                f"{issue['remediation']} | "
                f"`{issue['source_evidence_path']}` |"
            )
    else:
        issue_rows.append(
            "| `none` | `none` | `none` | `none` | `none` | "
            "No mesh certification issues found. | `none` |"
        )

    family_rows = [
        "| Family | State | Errors | Warnings | Info |",
        "| --- | --- | --- | --- | --- |",
    ]
    for family in status["maturity_check_families"]:
        family_rows.append(
            "| "
            f"`{family['family']}` | "
            f"`{family['state']}` | "
            f"`{family['error_count']}` | "
            f"`{family['warning_count']}` | "
            f"`{family['info_count']}` |"
        )

    return "\n".join(
        [
            "# Lotus Mesh Certification Status",
            "",
            "This file is generated by the RFC-0089 mesh certification gate.",
            "",
            f"- Generated at UTC: `{status['generated_at_utc']}`",
            f"- Gate mode: `{status['gate_mode']}`",
            f"- Certification state: `{status['certification_state']}`",
            f"- Required products: `{summary['required_product_count']}`",
            f"- Certified required products: `{summary['certified_required_product_count']}`",
            f"- Attention required products: `{summary['attention_required_product_count']}`",
            f"- Errors: `{summary['error_count']}`",
            f"- Warnings: `{summary['warning_count']}`",
            f"- Info: `{summary['info_count']}`",
            "",
            "## Maturity Check Families",
            "",
            *family_rows,
            "",
            "## Required Products",
            "",
            *product_rows,
            "",
            "## Issues",
            "",
            *issue_rows,
            "",
            "## Embedded Live Trust Certification",
            "",
            render_live_trust_certification_markdown(
                status["live_trust_certification"]
            ),
        ]
    )


def write_mesh_certification_status(
    status: dict[str, Any],
    *,
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
    certification_history_directory: Path = DEFAULT_OPERATING_HISTORY_DIRECTORY,
) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    (output_directory / MESH_CERTIFICATION_STATUS_FILENAME).write_text(
        json.dumps(status, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_directory / MESH_CERTIFICATION_MARKDOWN_FILENAME).write_text(
        render_mesh_certification_markdown(status),
        encoding="utf-8",
    )
    (output_directory / MESH_CERTIFICATION_ISSUES_FILENAME).write_text(
        json.dumps(status["issues"], indent=2) + "\n",
        encoding="utf-8",
    )
    (output_directory / ENTERPRISE_MESH_CERTIFICATION_STATUS_FILENAME).write_text(
        json.dumps(status, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_directory / ENTERPRISE_MESH_CERTIFICATION_MARKDOWN_FILENAME).write_text(
        render_mesh_certification_markdown(status),
        encoding="utf-8",
    )
    (output_directory / ENTERPRISE_MESH_CERTIFICATION_ISSUES_FILENAME).write_text(
        json.dumps(status["issues"], indent=2) + "\n",
        encoding="utf-8",
    )
    operating_report = build_report_from_paths(
        mesh_status_path=output_directory
        / ENTERPRISE_MESH_CERTIFICATION_STATUS_FILENAME,
        history_directory=certification_history_directory,
        generated_at_utc=status["generated_at_utc"],
    )
    write_enterprise_mesh_operating_report(
        operating_report,
        output_directory=output_directory,
    )


def _exit_code(status: dict[str, Any]) -> int:
    if status["gate_mode"] == "blocking" and status["summary"]["error_count"] > 0:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the RFC-0089 Lotus mesh certification gate."
    )
    parser.add_argument(
        "--mode",
        choices=["advisory", "blocking"],
        default="blocking",
        help="Gate mode. Blocking mode exits non-zero when error issues are present.",
    )
    parser.add_argument(
        "--telemetry-path",
        action="append",
        type=Path,
        default=[],
        help=(
            "Telemetry snapshot file or directory. May be provided multiple times. "
            "Defaults to first-wave sibling repo telemetry directories."
        ),
    )
    parser.add_argument(
        "--generated-at-utc",
        required=True,
        help="UTC timestamp to stamp into generated outputs.",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Directory where mesh certification status artifacts should be written.",
    )
    parser.add_argument(
        "--catalog-source",
        choices=["checked-in", "current-repo-native"],
        default="checked-in",
        help=(
            "Catalog input mode. checked-in uses generated/domain-product-catalog.json; "
            "current-repo-native derives a temporary current catalog and graph from the "
            "source manifest without mutating checked-in generated artifacts."
        ),
    )
    parser.add_argument(
        "--catalog-path",
        type=Path,
        default=None,
        help=(
            "Explicit domain-product-catalog.json path. When provided without "
            "--dependency-graph-path, the sibling domain-product-dependency-graph.json "
            "in the same directory is used."
        ),
    )
    parser.add_argument(
        "--dependency-graph-path",
        type=Path,
        default=None,
        help="Explicit domain-product dependency graph path used with --catalog-path.",
    )
    parser.add_argument(
        "--source-manifest-path",
        type=Path,
        default=DEFAULT_SOURCE_MANIFEST_PATH,
        help="Domain-product source manifest used for manifest checks and current catalog generation.",
    )
    parser.add_argument(
        "--slo-policy-path",
        type=Path,
        default=DEFAULT_SLO_POLICY_DIRECTORY,
        help="Mesh SLO policy file or directory used for RFC-0091 SLO drift checks.",
    )
    parser.add_argument(
        "--access-policy-path",
        type=Path,
        default=DEFAULT_ACCESS_POLICY_DIRECTORY,
        help="Mesh access policy file or directory used for RFC-0091 access governance checks.",
    )
    parser.add_argument(
        "--evidence-policy-path",
        type=Path,
        default=DEFAULT_EVIDENCE_POLICY_DIRECTORY,
        help="Mesh evidence policy file or directory used for RFC-0091 evidence drift checks.",
    )
    parser.add_argument(
        "--require-sibling-repos",
        action="store_true",
        help="Treat missing lotus-gateway or lotus-workbench sibling checkouts as errors.",
    )
    parser.add_argument(
        "--skip-publication-checks",
        action="store_true",
        help="Skip gateway and Workbench publication/consumption drift checks.",
    )
    args = parser.parse_args(argv)
    try:
        catalog_path, dependency_graph_path, catalog_source = _resolve_catalog_inputs(
            catalog_source=args.catalog_source,
            explicit_catalog_path=args.catalog_path,
            explicit_dependency_graph_path=args.dependency_graph_path,
            source_manifest_path=args.source_manifest_path,
            output_directory=args.output_directory,
            generated_at_utc=args.generated_at_utc,
        )
    except ValueError as exc:
        parser.error(str(exc))

    status = build_mesh_certification_status(
        telemetry_paths=args.telemetry_path,
        catalog_path=catalog_path,
        catalog_source=catalog_source,
        source_manifest_path=args.source_manifest_path,
        dependency_graph_path=dependency_graph_path,
        gate_mode=args.mode,
        generated_at_utc=args.generated_at_utc,
        slo_policy_path=args.slo_policy_path,
        access_policy_path=args.access_policy_path,
        evidence_policy_path=args.evidence_policy_path,
        require_sibling_repos=args.require_sibling_repos,
        check_publication_surfaces=not args.skip_publication_checks,
    )
    write_mesh_certification_status(status, output_directory=args.output_directory)
    print(
        "Mesh certification "
        f"{status['certification_state']} in {args.mode} mode; "
        f"catalog source {catalog_source}; "
        f"{status['summary']['error_count']} error(s), "
        f"{status['summary']['warning_count']} warning(s), "
        f"{status['summary']['info_count']} info issue(s)."
    )
    print(f"Wrote mesh certification artifacts to {args.output_directory.resolve()}")
    return _exit_code(status)


if __name__ == "__main__":
    sys.exit(main())
