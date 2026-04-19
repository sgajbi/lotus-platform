from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from domain_product_discovery import DEFAULT_CATALOG_PATH, load_catalog
from generate_live_trust_certification import (
    build_live_trust_certification_report_from_paths,
    render_live_trust_certification_markdown,
)
from validate_trust_telemetry import (
    _iter_telemetry_paths,
    _load_validation_context,
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
DEFAULT_TELEMETRY_DIRECTORIES = [
    ROOT.parent / "lotus-core" / "contracts" / "trust-telemetry",
    ROOT.parent / "lotus-performance" / "contracts" / "trust-telemetry",
    ROOT.parent / "lotus-risk" / "contracts" / "trust-telemetry",
    ROOT.parent / "lotus-advise" / "contracts" / "trust-telemetry",
]
MESH_CERTIFICATION_STATUS_FILENAME = "mesh-certification-status.json"
MESH_CERTIFICATION_MARKDOWN_FILENAME = "mesh-certification-status.md"
MESH_CERTIFICATION_ISSUES_FILENAME = "mesh-certification-issues.json"
REQUIRED_PRODUCTS = {
    "lotus-core:PortfolioStateSnapshot:v1": "lotus-core",
    "lotus-performance:ReturnsSeriesBundle:v1": "lotus-performance",
    "lotus-risk:RiskMetricsReport:v1": "lotus-risk",
    "lotus-advise:AdvisoryProposalLifecycleRecord:v1": "lotus-advise",
}
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
    "catalog_drift",
    "gateway_publication_drift",
    "workbench_consumption_drift",
}
GateMode = Literal["advisory", "blocking"]


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

    discovered = []
    for directory in DEFAULT_TELEMETRY_DIRECTORIES:
        if directory.exists():
            discovered.extend(_iter_telemetry_paths(directory))
    return sorted(set(discovered))


def _telemetry_payloads_by_product(
    telemetry_paths: list[Path],
) -> dict[str, tuple[Path, dict[str, Any]]]:
    payloads: dict[str, tuple[Path, dict[str, Any]]] = {}
    for telemetry_path in telemetry_paths:
        payload = _load_json(telemetry_path)
        product_id = str(payload.get("product_id", ""))
        if product_id:
            payloads[product_id] = (telemetry_path, payload)
    return payloads


def _catalog_products_by_id(catalog_path: Path) -> dict[str, dict[str, Any]]:
    catalog = load_catalog(catalog_path)
    return {product["product_id"]: product for product in catalog.get("products", [])}


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
    if required_product and gate_mode == "blocking" and code in BLOCKING_REQUIRED_PRODUCT_CODES:
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
            source_evidence_path="../" + producer_repository + "/contracts/trust-telemetry",
        )


def _check_gateway_publication(
    *,
    gateway_root: Path,
    require_sibling_repos: bool,
    issues: list[MeshCertificationIssue],
) -> None:
    router_path = gateway_root / "src" / "app" / "routers" / "domain_products.py"
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
    missing_paths = [path for path in (router_path, service_path) if not path.exists()]
    if missing_paths:
        for path in missing_paths:
            _issue(
                issues,
                code="gateway_publication_drift",
                severity="error",
                producer_repository="lotus-gateway",
                remediation="Restore the gateway domain-product publication module.",
                source_evidence_path=path,
            )
        return

    router_text = router_path.read_text(encoding="utf-8")
    required_fragments = [
        'prefix="/api/v1/domain-products"',
        '"/catalog"',
        '"/products/{producer_repository}/{product_name}/{product_version}"',
        '"/dependency-graph"',
        '"/trust-certification"',
    ]
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


def _summary(issues: list[MeshCertificationIssue], required_products: list[dict[str, Any]]) -> dict[str, Any]:
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
    source_manifest_path: Path = DEFAULT_SOURCE_MANIFEST_PATH,
    dependency_graph_path: Path = DEFAULT_GRAPH_PATH,
    gateway_root: Path = DEFAULT_GATEWAY_ROOT,
    workbench_root: Path = DEFAULT_WORKBENCH_ROOT,
    gate_mode: GateMode,
    generated_at_utc: str,
    require_sibling_repos: bool = False,
    check_publication_surfaces: bool = True,
) -> dict[str, Any]:
    issues: list[MeshCertificationIssue] = []
    discovered_telemetry_paths = _iter_default_telemetry_paths(telemetry_paths or [])
    telemetry_payloads = _telemetry_payloads_by_product(discovered_telemetry_paths)
    context = _load_validation_context(catalog_path=catalog_path)
    live_report = build_live_trust_certification_report_from_paths(
        discovered_telemetry_paths,
        source_telemetry_path="mesh-certification:first-wave-telemetry",
        generated_at_utc=generated_at_utc,
        context=context,
    )

    _validate_source_manifest(source_manifest_path=source_manifest_path, issues=issues)
    _validate_required_products_in_catalog(
        products_by_id=_catalog_products_by_id(catalog_path),
        issues=issues,
        catalog_path=catalog_path,
    )
    _validate_required_telemetry(
        telemetry_payloads=telemetry_payloads,
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
        "governed_by_rfcs": ["RFC-0089"],
        "generated_at_utc": generated_at_utc,
        "gate_mode": gate_mode,
        "certification_state": _certification_state(sorted_issues),
        "required_products": required_products,
        "summary": _summary(sorted_issues, required_products),
        "issues": [asdict(issue) for issue in sorted_issues],
        "source_artifacts": {
            "source_manifest": source_manifest_path.as_posix(),
            "catalog": catalog_path.as_posix(),
            "dependency_graph": dependency_graph_path.as_posix(),
            "telemetry_inputs": [path.as_posix() for path in discovered_telemetry_paths],
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
        "| Severity | Code | Producer | Product | Remediation | Evidence |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if status["issues"]:
        for issue in status["issues"]:
            issue_rows.append(
                "| "
                f"`{issue['severity']}` | "
                f"`{issue['code']}` | "
                f"`{issue['producer_repository']}` | "
                f"`{issue.get('product_id')}` | "
                f"{issue['remediation']} | "
                f"`{issue['source_evidence_path']}` |"
            )
    else:
        issue_rows.append("| `none` | `none` | `none` | `none` | No mesh certification issues found. | `none` |")

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

    status = build_mesh_certification_status(
        telemetry_paths=args.telemetry_path,
        gate_mode=args.mode,
        generated_at_utc=args.generated_at_utc,
        require_sibling_repos=args.require_sibling_repos,
        check_publication_surfaces=not args.skip_publication_checks,
    )
    write_mesh_certification_status(status, output_directory=args.output_directory)
    print(
        "Mesh certification "
        f"{status['certification_state']} in {args.mode} mode; "
        f"{status['summary']['error_count']} error(s), "
        f"{status['summary']['warning_count']} warning(s), "
        f"{status['summary']['info_count']} info issue(s)."
    )
    print(f"Wrote mesh certification artifacts to {args.output_directory.resolve()}")
    return _exit_code(status)


if __name__ == "__main__":
    sys.exit(main())
