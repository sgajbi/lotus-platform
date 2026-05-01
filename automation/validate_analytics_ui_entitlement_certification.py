from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "context" / "contracts"
DEFAULT_OBSERVABILITY_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-contract.json"
)
DEFAULT_ENTITLEMENT_CERTIFICATION_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-entitlement-certification.json"
)

LIFECYCLE_STATUS = "slice-19-entitlement-certification-governance"
CERTIFICATION_FEATURE_KEY = (
    "workbench.analytics.observability.caller_context_entitlement_certification"
)
REQUIRED_AUDIT_EVENTS = {
    "gateway.analytics.audit.analytics_read_allowed",
    "gateway.analytics.audit.analytics_read_denied",
}
REQUIRED_FORBIDDEN_FIELDS = {
    "client_id",
    "client_name",
    "correlation_id",
    "portfolio_id",
    "raw_entitlement_failure",
    "request_body",
    "response_body",
    "screen_content",
    "support_reference",
    "trace_id",
}
REQUIRED_EVIDENCE_TYPES = {
    "gateway-allow-deny-audit-log",
    "caller-context-contract-test",
    "workbench-permission-blocked-panel-proof",
    "protected-diagnostics-proof",
}
REQUIRED_IMPLEMENTATION_EVIDENCE = {
    (
        "workbench-advisor-brief",
        "caller-context-contract-test",
        "sgajbi/lotus-gateway#176",
    ),
    (
        "workbench-advisor-brief",
        "gateway-allow-deny-audit-log",
        "sgajbi/lotus-gateway#177",
    ),
}
REQUIRED_CHECKS = {
    "Feature Lane / Platform Repo Contracts",
    "Feature Lane / Workflow Lint",
    "PR Merge Gate / Platform Repo Contracts",
    "PR Merge Gate / Workflow Lint",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _feature_status(observability_contract: dict[str, Any]) -> dict[str, str]:
    return {
        str(feature.get("feature_key")): str(feature.get("status"))
        for feature in observability_contract.get("supported_feature_keys", [])
        if isinstance(feature, dict)
    }


def _gateway_event_status(observability_contract: dict[str, Any]) -> dict[str, bool]:
    telemetry = observability_contract.get("telemetry_contract", {})
    return {
        str(event.get("event_name")): bool(event.get("implemented"))
        for event in telemetry.get("gateway_log_events", [])
        if isinstance(event, dict)
    }


def validate_entitlement_certification(
    *,
    observability_contract: dict[str, Any],
    certification: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    _validate_identity(errors, certification)
    _validate_scope(errors, certification)
    _validate_caller_context(errors, observability_contract, certification)
    _validate_read_paths(errors, observability_contract, certification)
    _validate_denial_semantics(errors, certification)
    _validate_forbidden_fields(errors, observability_contract, certification)
    _validate_evidence(errors, certification)
    _validate_implementation_evidence(errors, certification)
    _validate_residual_scope(errors, observability_contract, certification)
    _validate_required_proof(errors, certification)
    return errors


def _validate_identity(errors: list[str], certification: dict[str, Any]) -> None:
    if certification.get("contract_id") != "analytics-ui-observability-entitlement-certification":
        errors.append(
            "contract_id must be analytics-ui-observability-entitlement-certification"
        )
    if certification.get("governed_by_rfc") != "RFC-0108":
        errors.append("governed_by_rfc must be RFC-0108")
    if certification.get("lifecycle_status") != LIFECYCLE_STATUS:
        errors.append(f"lifecycle_status must be {LIFECYCLE_STATUS}")


def _validate_scope(errors: list[str], certification: dict[str, Any]) -> None:
    scope = certification.get("certification_scope", {})
    if scope.get("status") != "governance_ready_implementation_pending":
        errors.append("certification_scope.status must remain governance_ready_implementation_pending")
    if scope.get("policy") != "implementation_backed_only":
        errors.append("certification_scope.policy must be implementation_backed_only")
    if scope.get("source_contract") != "analytics-ui-observability-contract":
        errors.append("certification_scope.source_contract must reference analytics-ui-observability-contract")


def _validate_caller_context(
    errors: list[str],
    observability_contract: dict[str, Any],
    certification: dict[str, Any],
) -> None:
    allowed_labels = set(observability_contract.get("allowed_labels", []))
    requirements = certification.get("caller_context_requirements", [])
    if not isinstance(requirements, list) or len(requirements) < 3:
        errors.append("caller_context_requirements must define service, entitlement, and diagnostics requirements")
        return
    requirement_ids = {str(requirement.get("requirement_id")) for requirement in requirements}
    for required_id in {
        "caller-service-identity",
        "entitlement-decision-boundary",
        "operator-diagnostics-boundary",
    }:
        if required_id not in requirement_ids:
            errors.append(f"caller_context_requirements missing {required_id}")
    for requirement in requirements:
        fields = set(requirement.get("required_fields", []))
        unsupported = sorted(fields - allowed_labels)
        if unsupported:
            errors.append(
                f"{requirement.get('requirement_id')}: required_fields not allowed labels: {unsupported}"
            )


def _validate_read_paths(
    errors: list[str],
    observability_contract: dict[str, Any],
    certification: dict[str, Any],
) -> None:
    event_status = _gateway_event_status(observability_contract)
    missing_events = sorted(
        event for event in REQUIRED_AUDIT_EVENTS if event_status.get(event) is not True
    )
    if missing_events:
        errors.append(f"required audit events are not implemented: {missing_events}")

    read_paths = certification.get("certified_read_paths", [])
    if not isinstance(read_paths, list) or not read_paths:
        errors.append("certified_read_paths must not be empty")
        return
    for path in read_paths:
        path_id = str(path.get("path_id", "<missing>"))
        if path.get("status") != "implementation_pending":
            errors.append(f"{path_id}: status must remain implementation_pending before live proof")
        events = set(path.get("required_audit_events", []))
        if events != REQUIRED_AUDIT_EVENTS:
            errors.append(f"{path_id}: required_audit_events must equal {sorted(REQUIRED_AUDIT_EVENTS)}")
        owners = set(path.get("owner_repositories", []))
        if "lotus-gateway" not in owners or "lotus-workbench" not in owners:
            errors.append(f"{path_id}: owner_repositories must include lotus-gateway and lotus-workbench")


def _validate_denial_semantics(errors: list[str], certification: dict[str, Any]) -> None:
    denial = certification.get("denial_semantics", {})
    if denial.get("required_audit_event") != "gateway.analytics.audit.analytics_read_denied":
        errors.append("denial_semantics.required_audit_event must be analytics_read_denied")
    if denial.get("required_reason") != "upstream_authorization_denied":
        errors.append("denial_semantics.required_reason must be upstream_authorization_denied")
    if denial.get("required_state") != "permission_blocked":
        errors.append("denial_semantics.required_state must be permission_blocked")
    if set(denial.get("allowed_status_classes", [])) != {"4xx"}:
        errors.append("denial_semantics.allowed_status_classes must equal ['4xx']")


def _validate_forbidden_fields(
    errors: list[str],
    observability_contract: dict[str, Any],
    certification: dict[str, Any],
) -> None:
    contract_forbidden = set(observability_contract.get("forbidden_fields", []))
    forbidden = set(certification.get("forbidden_evidence_fields", []))
    missing = sorted(REQUIRED_FORBIDDEN_FIELDS - forbidden)
    if missing:
        errors.append(f"forbidden_evidence_fields missing {missing}")
    unsupported = sorted(forbidden - contract_forbidden - {"support_reference"})
    if unsupported:
        errors.append(f"forbidden_evidence_fields are not governed forbidden fields: {unsupported}")


def _validate_evidence(errors: list[str], certification: dict[str, Any]) -> None:
    evidence = certification.get("required_evidence", [])
    evidence_types = {
        str(item.get("evidence_type"))
        for item in evidence
        if isinstance(item, dict)
    }
    missing = sorted(REQUIRED_EVIDENCE_TYPES - evidence_types)
    if missing:
        errors.append(f"required_evidence missing {missing}")
    for item in evidence:
        if item.get("evidence_type") == "protected-diagnostics-proof":
            if item.get("status") != "implemented":
                errors.append("protected-diagnostics-proof must remain implemented")
        elif item.get("status") != "required_before_promotion":
            errors.append(f"{item.get('evidence_type')}: status must be required_before_promotion")


def _validate_implementation_evidence(
    errors: list[str],
    certification: dict[str, Any],
) -> None:
    evidence = certification.get("implementation_evidence", [])
    if not isinstance(evidence, list) or not evidence:
        errors.append("implementation_evidence must record implementation-backed proof references")
        return

    path_ids = {
        str(path.get("path_id"))
        for path in certification.get("certified_read_paths", [])
        if isinstance(path, dict)
    }
    observed: set[tuple[str, str, str]] = set()
    for item in evidence:
        if not isinstance(item, dict):
            errors.append("implementation_evidence entries must be objects")
            continue
        evidence_id = str(item.get("evidence_id", "<missing>"))
        path_id = str(item.get("path_id", ""))
        if path_id not in path_ids:
            errors.append(f"{evidence_id}: path_id must reference a certified_read_paths entry")
        if item.get("status") != "implemented":
            errors.append(f"{evidence_id}: status must be implemented for recorded PR evidence")
        if item.get("owner_repo") != "lotus-gateway":
            errors.append(f"{evidence_id}: owner_repo must be lotus-gateway for this evidence")
        pull_request = str(item.get("pull_request", ""))
        merge_commit = str(item.get("merge_commit", ""))
        if not pull_request.startswith("sgajbi/lotus-gateway#"):
            errors.append(f"{evidence_id}: pull_request must reference sgajbi/lotus-gateway")
        if len(merge_commit) != 40:
            errors.append(f"{evidence_id}: merge_commit must be a 40-character SHA")
        for evidence_type in item.get("evidence_types", []):
            observed.add((path_id, str(evidence_type), pull_request))

    missing = sorted(REQUIRED_IMPLEMENTATION_EVIDENCE - observed)
    if missing:
        errors.append(f"implementation_evidence missing required proof references: {missing}")


def _validate_residual_scope(
    errors: list[str],
    observability_contract: dict[str, Any],
    certification: dict[str, Any],
) -> None:
    statuses = _feature_status(observability_contract)
    if statuses.get(CERTIFICATION_FEATURE_KEY) not in {None, "planned"}:
        errors.append(f"{CERTIFICATION_FEATURE_KEY} must remain planned until runtime proof")
    residual_keys = {
        str(item.get("feature_key"))
        for item in certification.get("residual_scope", [])
        if isinstance(item, dict)
    }
    if CERTIFICATION_FEATURE_KEY not in residual_keys:
        errors.append(f"residual_scope must include {CERTIFICATION_FEATURE_KEY}")


def _validate_required_proof(errors: list[str], certification: dict[str, Any]) -> None:
    checks = set(certification.get("required_github_checks", []))
    missing_checks = sorted(REQUIRED_CHECKS - checks)
    if missing_checks:
        errors.append(f"required_github_checks missing {missing_checks}")
    commands = "\n".join(str(command) for command in certification.get("local_proof_commands", []))
    for required_fragment in (
        "validate_analytics_ui_entitlement_certification.py",
        "test_analytics_ui_entitlement_certification.py",
        "ruff check",
    ):
        if required_fragment not in commands:
            errors.append(f"local_proof_commands must include {required_fragment}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the RFC-0108 analytics UI entitlement certification contract."
    )
    parser.add_argument(
        "--observability-contract",
        type=Path,
        default=DEFAULT_OBSERVABILITY_CONTRACT_PATH,
    )
    parser.add_argument(
        "--certification-contract",
        type=Path,
        default=DEFAULT_ENTITLEMENT_CERTIFICATION_PATH,
    )
    args = parser.parse_args()

    errors = validate_entitlement_certification(
        observability_contract=_load_json(args.observability_contract),
        certification=_load_json(args.certification_contract),
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Analytics UI entitlement certification contract is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
