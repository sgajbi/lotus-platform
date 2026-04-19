from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_trust_telemetry import (
    DEFAULT_CATALOG_PATH,
    _iter_telemetry_paths,
    _load_json,
    _load_validation_context,
    validate_trust_telemetry_snapshot,
)


LIVE_TRUST_CERTIFICATION_FILENAME = "domain-product-live-trust-certification.json"
LIVE_TRUST_CERTIFICATION_MARKDOWN_FILENAME = (
    "domain-product-live-trust-certification.md"
)
DEFAULT_OUTPUT_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "output" / "trust-certification"
)
ATTENTION_COMPLETENESS_STATES = {
    "stale",
    "unreconciled",
    "break_open",
    "blocked",
    "unknown",
}
ATTENTION_RECONCILIATION_STATES = {
    "stale",
    "unreconciled",
    "break_open",
    "blocked",
    "unknown",
}
ATTENTION_DATA_QUALITY_STATES = {
    "quality_failed",
    "quality_blocked",
    "quality_unknown",
}


def _add_issue(
    issues: list[dict[str, str]],
    *,
    code: str,
    severity: str,
    product_id: str,
    detail: str,
) -> None:
    issues.append(
        {
            "code": code,
            "severity": severity,
            "product_id": product_id,
            "detail": detail,
        }
    )


def _certification_state(issues: list[dict[str, str]]) -> str:
    return "certified" if not issues else "attention_required"


def _evaluate_snapshot(
    path: Path,
    payload: dict[str, Any],
    *,
    context: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    product_id = str(payload.get("product_id", "unknown"))
    issues: list[dict[str, str]] = []

    validation_issues = validate_trust_telemetry_snapshot(
        path, payload, context=context
    )
    for validation_issue in validation_issues:
        _add_issue(
            issues,
            code="invalid_trust_telemetry",
            severity="error",
            product_id=product_id,
            detail=validation_issue,
        )

    freshness = payload.get("freshness", {})
    freshness_state = (
        freshness.get("freshness_state") if isinstance(freshness, dict) else None
    )
    if freshness_state != "current":
        _add_issue(
            issues,
            code="freshness_not_current",
            severity="warning",
            product_id=product_id,
            detail=f"Freshness state is {freshness_state}.",
        )

    completeness_status = payload.get("completeness_status")
    if completeness_status in ATTENTION_COMPLETENESS_STATES:
        _add_issue(
            issues,
            code="completeness_attention_required",
            severity="warning",
            product_id=product_id,
            detail=f"Completeness status is {completeness_status}.",
        )

    reconciliation_status = payload.get("reconciliation_status")
    if reconciliation_status in ATTENTION_RECONCILIATION_STATES:
        _add_issue(
            issues,
            code="reconciliation_attention_required",
            severity="warning",
            product_id=product_id,
            detail=f"Reconciliation status is {reconciliation_status}.",
        )

    data_quality_status = payload.get("data_quality_status")
    if data_quality_status in ATTENTION_DATA_QUALITY_STATES:
        _add_issue(
            issues,
            code="data_quality_attention_required",
            severity="warning",
            product_id=product_id,
            detail=f"Data quality status is {data_quality_status}.",
        )

    lineage = payload.get("lineage", {})
    if isinstance(lineage, dict) and lineage.get("lineage_materialized") is not True:
        _add_issue(
            issues,
            code="lineage_not_materialized",
            severity="warning",
            product_id=product_id,
            detail="Lineage is not materialized for the product telemetry snapshot.",
        )

    blocking = payload.get("blocking", {})
    if isinstance(blocking, dict) and blocking.get("blocked") is True:
        _add_issue(
            issues,
            code="product_blocked",
            severity="error",
            product_id=product_id,
            detail=f"Product is blocked: {blocking.get('blocked_reason')}",
        )

    certification = {
        "product_id": product_id,
        "producer_repository": payload.get("producer_repository"),
        "product_name": payload.get("product_name"),
        "product_version": payload.get("product_version"),
        "source_repository": payload.get("source_repository"),
        "telemetry_path": path.as_posix(),
        "emitted_at_utc": payload.get("emitted_at_utc"),
        "certification_state": _certification_state(issues),
        "freshness_state": freshness_state,
        "completeness_status": completeness_status,
        "reconciliation_status": reconciliation_status,
        "data_quality_status": data_quality_status,
        "lineage_materialized": lineage.get("lineage_materialized")
        if isinstance(lineage, dict)
        else None,
        "blocked": blocking.get("blocked") if isinstance(blocking, dict) else None,
        "issue_count": len(issues),
    }
    return certification, issues


def build_live_trust_certification_report(
    telemetry_path: Path,
    *,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    generated_at_utc: str,
) -> dict[str, Any]:
    context = _load_validation_context(catalog_path=catalog_path)
    telemetry_paths = _iter_telemetry_paths(telemetry_path)
    certifications: list[dict[str, Any]] = []
    issues: list[dict[str, str]] = []

    for snapshot_path in telemetry_paths:
        payload = _load_json(snapshot_path)
        certification, snapshot_issues = _evaluate_snapshot(
            snapshot_path,
            payload,
            context=context,
        )
        certifications.append(certification)
        issues.extend(snapshot_issues)

    return {
        "contract_id": "lotus-domain-product-live-trust-certification",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0087"],
        "generated_at_utc": generated_at_utc,
        "source_telemetry_path": telemetry_path.as_posix(),
        "summary": {
            "certification_state": _certification_state(issues),
            "telemetry_snapshot_count": len(telemetry_paths),
            "certified_snapshot_count": sum(
                1
                for certification in certifications
                if certification["certification_state"] == "certified"
            ),
            "attention_required_count": sum(
                1
                for certification in certifications
                if certification["certification_state"] == "attention_required"
            ),
            "issue_count": len(issues),
        },
        "product_certifications": sorted(
            certifications,
            key=lambda certification: (
                certification["producer_repository"] or "",
                certification["product_name"] or "",
                certification["product_version"] or "",
            ),
        ),
        "issues": sorted(
            issues,
            key=lambda issue: (issue["severity"], issue["code"], issue["product_id"]),
        ),
    }


def render_live_trust_certification_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    certification_rows = [
        "| Product | Producer | State | Freshness | Completeness | Reconciliation | Data Quality | Blocked | Issues |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for certification in report["product_certifications"]:
        certification_rows.append(
            "| "
            f"`{certification['product_name']}` | "
            f"`{certification['producer_repository']}` | "
            f"`{certification['certification_state']}` | "
            f"`{certification['freshness_state']}` | "
            f"`{certification['completeness_status']}` | "
            f"`{certification['reconciliation_status']}` | "
            f"`{certification['data_quality_status']}` | "
            f"`{certification['blocked']}` | "
            f"`{certification['issue_count']}` |"
        )

    issue_rows = [
        "| Severity | Code | Product | Detail |",
        "| --- | --- | --- | --- |",
    ]
    if report["issues"]:
        for issue in report["issues"]:
            issue_rows.append(
                "| "
                f"`{issue['severity']}` | "
                f"`{issue['code']}` | "
                f"`{issue['product_id']}` | "
                f"{issue['detail']} |"
            )
    else:
        issue_rows.append("| `none` | `none` | `none` | No live trust issues found. |")

    return "\n".join(
        [
            "# Lotus Domain Product Live Trust Certification",
            "",
            "This file is generated from governed RFC-0087 trust telemetry snapshots.",
            "",
            f"- Generated at UTC: `{report['generated_at_utc']}`",
            f"- Certification state: `{summary['certification_state']}`",
            f"- Telemetry snapshots: `{summary['telemetry_snapshot_count']}`",
            f"- Certified snapshots: `{summary['certified_snapshot_count']}`",
            f"- Attention required: `{summary['attention_required_count']}`",
            f"- Issue count: `{summary['issue_count']}`",
            "",
            "## Product Trust Certification",
            "",
            *certification_rows,
            "",
            "## Issues",
            "",
            *issue_rows,
            "",
        ]
    )


def write_live_trust_certification_report(
    telemetry_path: Path,
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
    *,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    generated_at_utc: str,
) -> None:
    report = build_live_trust_certification_report(
        telemetry_path,
        catalog_path=catalog_path,
        generated_at_utc=generated_at_utc,
    )
    markdown = render_live_trust_certification_markdown(report)
    output_directory.mkdir(parents=True, exist_ok=True)
    (output_directory / LIVE_TRUST_CERTIFICATION_FILENAME).write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_directory / LIVE_TRUST_CERTIFICATION_MARKDOWN_FILENAME).write_text(
        markdown,
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate live trust certification artifacts from RFC-0087 telemetry snapshots."
    )
    parser.add_argument(
        "telemetry_path",
        type=Path,
        help="Telemetry snapshot file or directory containing *.json snapshots.",
    )
    parser.add_argument(
        "--output-directory",
        default=DEFAULT_OUTPUT_DIRECTORY,
        type=Path,
        help="Directory where live trust certification artifacts should be written.",
    )
    parser.add_argument(
        "--catalog",
        default=DEFAULT_CATALOG_PATH,
        type=Path,
        help="Generated domain-product catalog used to verify product identity.",
    )
    parser.add_argument(
        "--generated-at-utc",
        required=True,
        help="UTC timestamp to stamp into generated outputs.",
    )
    args = parser.parse_args(argv)

    write_live_trust_certification_report(
        args.telemetry_path,
        args.output_directory,
        catalog_path=args.catalog,
        generated_at_utc=args.generated_at_utc,
    )
    print(
        "Generated live trust certification artifacts in "
        f"{args.output_directory.resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
