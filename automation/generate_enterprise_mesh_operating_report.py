from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Literal


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MESH_STATUS_PATH = (
    ROOT / "output" / "mesh-certification" / "enterprise-mesh-certification-status.json"
)
DEFAULT_HISTORY_DIRECTORY = (
    ROOT / "output" / "mesh-evidence-packs" / "certification-history"
)
DEFAULT_OUTPUT_DIRECTORY = ROOT / "output" / "mesh-certification"
OPERATING_REPORT_JSON_FILENAME = "enterprise-mesh-operating-report.json"
OPERATING_REPORT_MARKDOWN_FILENAME = "enterprise-mesh-operating-report.md"
OperatingState = Literal[
    "production_ready",
    "production_ready_limited_history",
    "attention_required",
    "blocked",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _iter_history_records(history_directory: Path) -> list[dict[str, Any]]:
    if not history_directory.exists():
        return []
    records = []
    for path in sorted(history_directory.glob("*.json")):
        try:
            payload = _load_json(path)
        except json.JSONDecodeError:
            continue
        if payload.get("contract_id") == "lotus-mesh-certification-history-record":
            records.append({**payload, "_source_path": path.as_posix()})
    return sorted(records, key=lambda record: str(record.get("generated_at_utc", "")))


def _operating_state(
    *,
    current_status: dict[str, Any],
    history_records: list[dict[str, Any]],
) -> OperatingState:
    summary = current_status.get("summary", {})
    if summary.get("error_count", 0) > 0 or current_status.get(
        "certification_state"
    ) == "failed":
        return "blocked"
    if summary.get("warning_count", 0) > 0:
        return "attention_required"
    if len(history_records) < 2:
        return "production_ready_limited_history"
    return "production_ready"


def _severity_rank(severity: str) -> int:
    return {"error": 0, "warning": 1, "info": 2}.get(severity, 3)


def _build_escalation_queue(current_status: dict[str, Any]) -> list[dict[str, Any]]:
    queue = []
    for issue in current_status.get("issues", []):
        queue.append(
            {
                "severity": issue.get("severity"),
                "family": _issue_family(issue),
                "code": issue.get("code"),
                "owner_repository": issue.get("producer_repository"),
                "product_id": issue.get("product_id"),
                "remediation": issue.get("remediation"),
                "source_evidence_path": issue.get("source_evidence_path"),
            }
        )
    return sorted(
        queue,
        key=lambda item: (
            _severity_rank(str(item.get("severity"))),
            str(item.get("owner_repository")),
            str(item.get("product_id")),
            str(item.get("code")),
        ),
    )


def _issue_family(issue: dict[str, Any]) -> str:
    code = str(issue.get("code", ""))
    if code in {"missing_telemetry", "invalid_telemetry", "stale_telemetry"}:
        return "telemetry"
    if code.startswith("mesh_slo_"):
        return "slo"
    if code.startswith("mesh_access_"):
        return "access"
    if code.startswith("mesh_evidence_"):
        return "evidence"
    if code.startswith("mesh_lifecycle_"):
        return "lifecycle"
    if code == "catalog_drift":
        return "catalog"
    if code == "gateway_publication_drift":
        return "gateway"
    if code == "workbench_consumption_drift":
        return "workbench"
    return "unknown"


def _consecutive_certified_runs(history_records: list[dict[str, Any]]) -> int:
    count = 0
    for record in reversed(history_records):
        if record.get("certification_state") != "certified":
            break
        count += 1
    return count


def _last_failed_at(history_records: list[dict[str, Any]]) -> str | None:
    for record in reversed(history_records):
        if record.get("certification_state") == "failed":
            return str(record.get("generated_at_utc"))
    return None


def _regression_since_previous(
    *, current_status: dict[str, Any], history_records: list[dict[str, Any]]
) -> bool:
    if not history_records:
        return False
    previous_state = history_records[-1].get("certification_state")
    current_state = current_status.get("certification_state")
    return previous_state == "certified" and current_state != "certified"


def _product_operating_posture(
    *,
    current_status: dict[str, Any],
    history_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    current_products = current_status.get("required_products", [])
    prior_issue_counts: dict[str, int] = {}
    for record in history_records:
        for product in record.get("product_history", []):
            product_id = product.get("product_id")
            if isinstance(product_id, str):
                prior_issue_counts[product_id] = prior_issue_counts.get(
                    product_id, 0
                ) + int(product.get("issue_count", 0) or 0)

    posture = []
    for product in current_products:
        product_id = product["product_id"]
        current_issue_count = int(product.get("issue_count", 0) or 0)
        posture.append(
            {
                "product_id": product_id,
                "producer_repository": product["producer_repository"],
                "operating_state": "healthy"
                if current_issue_count == 0
                else "attention_required",
                "certification_state": product.get("certification_state"),
                "freshness_state": product.get("freshness_state"),
                "completeness_status": product.get("completeness_status"),
                "reconciliation_status": product.get("reconciliation_status"),
                "data_quality_status": product.get("data_quality_status"),
                "current_issue_count": current_issue_count,
                "historical_issue_count": prior_issue_counts.get(product_id, 0),
            }
        )
    return posture


def build_enterprise_mesh_operating_report(
    *,
    current_status: dict[str, Any],
    history_records: list[dict[str, Any]],
    generated_at_utc: str,
    source_status_path: Path,
    history_directory: Path,
) -> dict[str, Any]:
    operating_state = _operating_state(
        current_status=current_status,
        history_records=history_records,
    )
    escalation_queue = _build_escalation_queue(current_status)
    summary = current_status.get("summary", {})
    return {
        "contract_id": "lotus-enterprise-mesh-operating-report",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0092"],
        "generated_at_utc": generated_at_utc,
        "source_status_path": source_status_path.as_posix(),
        "history_directory": history_directory.as_posix(),
        "operating_state": operating_state,
        "current_certification": {
            "certification_state": current_status.get("certification_state"),
            "gate_mode": current_status.get("gate_mode"),
            "required_product_count": summary.get("required_product_count", 0),
            "certified_required_product_count": summary.get(
                "certified_required_product_count", 0
            ),
            "attention_required_product_count": summary.get(
                "attention_required_product_count", 0
            ),
            "error_count": summary.get("error_count", 0),
            "warning_count": summary.get("warning_count", 0),
            "info_count": summary.get("info_count", 0),
        },
        "drift_trend": {
            "history_record_count": len(history_records),
            "consecutive_certified_runs": _consecutive_certified_runs(
                history_records
            ),
            "last_failed_at_utc": _last_failed_at(history_records),
            "regression_since_previous": _regression_since_previous(
                current_status=current_status,
                history_records=history_records,
            ),
        },
        "escalation_queue": escalation_queue,
        "product_operating_posture": _product_operating_posture(
            current_status=current_status,
            history_records=history_records,
        ),
        "operator_guidance": _operator_guidance(
            operating_state=operating_state,
            escalation_queue=escalation_queue,
        ),
    }


def _operator_guidance(
    *, operating_state: OperatingState, escalation_queue: list[dict[str, Any]]
) -> list[str]:
    if operating_state == "production_ready":
        return [
            "Continue scheduled mesh certification and evidence-pack publication.",
            "Promote additional domain products only through the onboarding scaffold and certification gate.",
        ]
    if operating_state == "production_ready_limited_history":
        return [
            "Current certification is clean, but retain limited-history wording until multiple certification history records exist.",
            "Generate evidence packs on successive release days so trend posture becomes audit-ready.",
        ]
    if operating_state == "attention_required":
        return [
            "Review warning issues before customer evidence export.",
            "Fix stale or degraded products before promoting new consumers.",
        ]
    owners = sorted(
        {
            str(item.get("owner_repository"))
            for item in escalation_queue
            if item.get("severity") == "error"
        }
    )
    owner_text = ", ".join(owners) if owners else "the owning producer repositories"
    return [
        f"Block mesh promotion until errors are resolved by {owner_text}.",
        "Use the mesh certification gate runbook issue-code table for fix-forward sequencing.",
    ]


def render_enterprise_mesh_operating_report_markdown(report: dict[str, Any]) -> str:
    current = report["current_certification"]
    trend = report["drift_trend"]
    product_rows = [
        "| Product | Producer | Operating State | Certification | Current Issues | Historical Issues |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for product in report["product_operating_posture"]:
        product_rows.append(
            "| "
            f"`{product['product_id']}` | "
            f"`{product['producer_repository']}` | "
            f"`{product['operating_state']}` | "
            f"`{product['certification_state']}` | "
            f"`{product['current_issue_count']}` | "
            f"`{product['historical_issue_count']}` |"
        )

    escalation_rows = [
        "| Severity | Family | Owner | Product | Code | Remediation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if report["escalation_queue"]:
        for item in report["escalation_queue"]:
            escalation_rows.append(
                "| "
                f"`{item['severity']}` | "
                f"`{item['family']}` | "
                f"`{item['owner_repository']}` | "
                f"`{item.get('product_id')}` | "
                f"`{item['code']}` | "
                f"{item['remediation']} |"
            )
    else:
        escalation_rows.append(
            "| `none` | `none` | `none` | `none` | `none` | No active escalation items. |"
        )

    guidance_rows = [f"- {line}" for line in report["operator_guidance"]]
    return "\n".join(
        [
            "# Lotus Enterprise Mesh Operating Report",
            "",
            "This file is generated from mesh certification status and certification history.",
            "",
            f"- Generated at UTC: `{report['generated_at_utc']}`",
            f"- Operating state: `{report['operating_state']}`",
            f"- Certification state: `{current['certification_state']}`",
            f"- Gate mode: `{current['gate_mode']}`",
            f"- Required products: `{current['required_product_count']}`",
            f"- Certified required products: `{current['certified_required_product_count']}`",
            f"- Attention required products: `{current['attention_required_product_count']}`",
            f"- Errors: `{current['error_count']}`",
            f"- Warnings: `{current['warning_count']}`",
            "",
            "## Drift Trend",
            "",
            f"- History records: `{trend['history_record_count']}`",
            f"- Consecutive certified runs: `{trend['consecutive_certified_runs']}`",
            f"- Last failed at UTC: `{trend['last_failed_at_utc']}`",
            f"- Regression since previous: `{trend['regression_since_previous']}`",
            "",
            "## Product Operating Posture",
            "",
            *product_rows,
            "",
            "## Escalation Queue",
            "",
            *escalation_rows,
            "",
            "## Operator Guidance",
            "",
            *guidance_rows,
            "",
        ]
    )


def write_enterprise_mesh_operating_report(
    report: dict[str, Any],
    *,
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    _write_json(output_directory / OPERATING_REPORT_JSON_FILENAME, report)
    (output_directory / OPERATING_REPORT_MARKDOWN_FILENAME).write_text(
        render_enterprise_mesh_operating_report_markdown(report),
        encoding="utf-8",
    )


def build_report_from_paths(
    *,
    mesh_status_path: Path = DEFAULT_MESH_STATUS_PATH,
    history_directory: Path = DEFAULT_HISTORY_DIRECTORY,
    generated_at_utc: str,
) -> dict[str, Any]:
    return build_enterprise_mesh_operating_report(
        current_status=_load_json(mesh_status_path),
        history_records=_iter_history_records(history_directory),
        generated_at_utc=generated_at_utc,
        source_status_path=mesh_status_path,
        history_directory=history_directory,
    )


def _check_outputs(report: dict[str, Any], output_directory: Path) -> list[str]:
    expected_json = json.dumps(report, indent=2) + "\n"
    expected_markdown = render_enterprise_mesh_operating_report_markdown(report)
    issues = []
    json_path = output_directory / OPERATING_REPORT_JSON_FILENAME
    markdown_path = output_directory / OPERATING_REPORT_MARKDOWN_FILENAME
    if not json_path.exists() or json_path.read_text(encoding="utf-8") != expected_json:
        issues.append(f"{json_path}: operating report JSON is not current")
    if (
        not markdown_path.exists()
        or markdown_path.read_text(encoding="utf-8") != expected_markdown
    ):
        issues.append(f"{markdown_path}: operating report Markdown is not current")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the RFC-0092 enterprise mesh operating report."
    )
    parser.add_argument("--mesh-status-path", type=Path, default=DEFAULT_MESH_STATUS_PATH)
    parser.add_argument(
        "--history-directory", type=Path, default=DEFAULT_HISTORY_DIRECTORY
    )
    parser.add_argument(
        "--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY
    )
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report_from_paths(
        mesh_status_path=args.mesh_status_path,
        history_directory=args.history_directory,
        generated_at_utc=args.generated_at_utc,
    )
    if args.check:
        issues = _check_outputs(report, args.output_directory)
        if issues:
            for issue in issues:
                print(issue)
            return 1
        print("Enterprise mesh operating report is current.")
        return 0

    write_enterprise_mesh_operating_report(report, output_directory=args.output_directory)
    print(
        "Generated enterprise mesh operating report "
        f"{report['operating_state']} with "
        f"{len(report['escalation_queue'])} escalation item(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
