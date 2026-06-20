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
DEFAULT_ECOSYSTEM_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-ecosystem-completion.json"
)
DEFAULT_ECOSYSTEM_PROOF_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-ecosystem-proof.json"
)
DEFAULT_HARDENING_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-ecosystem-hardening.json"
)
DEFAULT_FINAL_CLOSURE_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-ecosystem-final-closure.json"
)

LIFECYCLE_STATUS = "slice-18-ecosystem-final-closure-implemented"
FINAL_CLOSURE_FEATURE_KEY = "platform.analytics.observability.ecosystem_final_closure"
REQUIRED_SOURCE_CONTRACTS = {
    "analytics-ui-observability-contract",
    "analytics-ui-observability-ecosystem-completion",
    "analytics-ui-observability-ecosystem-proof",
    "analytics-ui-observability-ecosystem-hardening",
}
REQUIRED_GITHUB_CHECKS = {
    "Cross-App Vocabulary Gate",
    "Feature Lane / Platform Repo Contracts",
    "Feature Lane / Workflow Lint",
    "PR Merge Gate / Platform Repo Contracts",
    "PR Merge Gate / Workflow Lint",
}
REQUIRED_MANAGE_PATHS = {
    "GET /api/v1/rebalance/runs",
    "GET /api/v1/rebalance/supportability/summary",
    "GET /api/v1/platform/capabilities",
}
REQUIRED_ADVISE_PROPOSAL_PATHS = {
    "POST /advisory/proposals/simulate",
    "POST /advisory/proposals",
    "GET /advisory/proposals",
    "GET /advisory/proposals/{proposal_id}",
    "GET /advisory/proposals/{proposal_id}/versions/{version_no}",
    "POST /advisory/proposals/{proposal_id}/versions",
    "POST /advisory/proposals/{proposal_id}/transitions",
    "POST /advisory/proposals/{proposal_id}/approvals",
    "GET /advisory/proposals/{proposal_id}/workflow-events",
    "GET /advisory/proposals/{proposal_id}/approvals",
    "GET /advisory/proposals/{proposal_id}/lineage",
}
REQUIRED_GATEWAY_CHECKS = {
    "Feature Lane / Lint Typecheck Unit",
    "Feature Lane / Workflow Lint",
    "PR Merge Gate / Lint Typecheck Unit",
    "PR Merge Gate / Integration Tests",
    "PR Merge Gate / Coverage Gate",
    "PR Merge Gate / Validate Docker Build",
    "PR Merge Gate / CI Local Docker Parity",
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


def validate_ecosystem_final_closure(
    *,
    observability_contract: dict[str, Any],
    ecosystem_contract: dict[str, Any],
    ecosystem_proof: dict[str, Any],
    hardening: dict[str, Any],
    final_closure: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    _validate_identity(errors, observability_contract, ecosystem_contract, final_closure)
    _validate_closure_scope(errors, final_closure)
    _validate_sources_and_slices(errors, ecosystem_contract, final_closure)
    _validate_supported_features(errors, observability_contract, final_closure)
    _validate_residual_scope(
        errors, observability_contract, ecosystem_proof, hardening, final_closure
    )
    _validate_proof_reconciliation(errors, ecosystem_proof, hardening, final_closure)
    _validate_downstream_boundary_hardening(errors, final_closure)
    _validate_required_proof(errors, final_closure)
    _validate_wiki_and_branch_hygiene(errors, final_closure)
    _validate_skills_guidance_review(errors, final_closure)
    return errors


def _validate_identity(
    errors: list[str],
    observability_contract: dict[str, Any],
    ecosystem_contract: dict[str, Any],
    final_closure: dict[str, Any],
) -> None:
    if (
        final_closure.get("contract_id")
        != "analytics-ui-observability-ecosystem-final-closure"
    ):
        errors.append(
            "contract_id must be analytics-ui-observability-ecosystem-final-closure"
        )
    if final_closure.get("governed_by_rfc") != "RFC-0108":
        errors.append("governed_by_rfc must be RFC-0108")
    if final_closure.get("lifecycle_status") != LIFECYCLE_STATUS:
        errors.append(f"lifecycle_status must be {LIFECYCLE_STATUS}")
    if observability_contract.get("lifecycle_status") != LIFECYCLE_STATUS:
        errors.append(
            "analytics-ui-observability-contract lifecycle_status must be "
            f"{LIFECYCLE_STATUS}"
        )
    if ecosystem_contract.get("lifecycle_status") != LIFECYCLE_STATUS:
        errors.append(
            "analytics-ui-observability-ecosystem-completion lifecycle_status must be "
            f"{LIFECYCLE_STATUS}"
        )


def _validate_closure_scope(
    errors: list[str], final_closure: dict[str, Any]
) -> None:
    scope = final_closure.get("closure_scope", {})
    if scope.get("implemented_scope_status") != "closed_for_implemented_scope":
        errors.append("closure_scope.implemented_scope_status must close implemented scope")
    if scope.get("supported_features_policy") != "implementation_backed_only":
        errors.append("closure_scope.supported_features_policy must be implementation_backed_only")
    if scope.get("residual_scope_policy") != "planned_until_separately_implemented":
        errors.append("closure_scope.residual_scope_policy must preserve planned residuals")


def _validate_sources_and_slices(
    errors: list[str],
    ecosystem_contract: dict[str, Any],
    final_closure: dict[str, Any],
) -> None:
    sources = set(final_closure.get("source_contracts", []))
    missing_sources = sorted(REQUIRED_SOURCE_CONTRACTS - sources)
    if missing_sources:
        errors.append(f"source_contracts missing {missing_sources}")

    expected_slice_status = {
        str(entry.get("slice_id")): str(entry.get("status"))
        for entry in ecosystem_contract.get("ecosystem_completion_slices", [])
        if isinstance(entry, dict)
    }
    closure_slice_status = {
        str(slice_id): str(status)
        for slice_id, status in final_closure.get("implemented_slice_status", {}).items()
    }
    if closure_slice_status != expected_slice_status:
        errors.append(
            "implemented_slice_status must match ecosystem completion slices: "
            f"expected {expected_slice_status}, actual {closure_slice_status}"
        )
    for required_slice in {"10", "11", "13", "15", "16", "17", "18"}:
        if closure_slice_status.get(required_slice) != "implemented":
            errors.append(f"Slice {required_slice} must be implemented for final closure")
    for partial_slice in {"12", "14"}:
        if closure_slice_status.get(partial_slice) != "partially_implemented":
            errors.append(
                f"Slice {partial_slice} must remain partially_implemented "
                "until residual owners complete the blocked scope"
            )


def _validate_supported_features(
    errors: list[str],
    observability_contract: dict[str, Any],
    final_closure: dict[str, Any],
) -> None:
    statuses = _feature_status(observability_contract)
    if statuses.get(FINAL_CLOSURE_FEATURE_KEY) != "implemented":
        errors.append(f"{FINAL_CLOSURE_FEATURE_KEY} must be implemented")

    audit = final_closure.get("supported_features_audit", {})
    if audit.get("policy") != "implementation_backed_only":
        errors.append("supported_features_audit.policy must be implementation_backed_only")
    implemented_reviewed = set(audit.get("implemented_feature_keys_reviewed", []))
    planned_reviewed = set(audit.get("planned_feature_keys_reviewed", []))

    implemented_missing = sorted(
        feature_key
        for feature_key, status in statuses.items()
        if status == "implemented" and feature_key not in implemented_reviewed
    )
    planned_missing = sorted(
        feature_key
        for feature_key, status in statuses.items()
        if status == "planned" and feature_key not in planned_reviewed
    )
    if implemented_missing:
        errors.append(
            "supported_features_audit.implemented_feature_keys_reviewed missing "
            f"{implemented_missing}"
        )
    if planned_missing:
        errors.append(
            "supported_features_audit.planned_feature_keys_reviewed missing "
            f"{planned_missing}"
        )
    overlap = implemented_reviewed & planned_reviewed
    if overlap:
        errors.append(
            "supported_features_audit must not review feature keys as both implemented "
            f"and planned: {sorted(overlap)}"
        )


def _validate_residual_scope(
    errors: list[str],
    observability_contract: dict[str, Any],
    ecosystem_proof: dict[str, Any],
    hardening: dict[str, Any],
    final_closure: dict[str, Any],
) -> None:
    statuses = _feature_status(observability_contract)
    proof_residual = {
        str(item.get("feature_key"))
        for item in ecosystem_proof.get("residual_scope", [])
        if isinstance(item, dict)
    }
    hardening_residual = {
        str(item.get("feature_key"))
        for item in hardening.get("residual_scope", [])
        if isinstance(item, dict)
    }
    closure_residual = {
        str(item.get("feature_key"))
        for item in final_closure.get("residual_scope", [])
        if isinstance(item, dict)
    }
    if closure_residual != proof_residual or closure_residual != hardening_residual:
        errors.append(
            "final residual scope must match proof and hardening residual scope: "
            f"final={sorted(closure_residual)}, proof={sorted(proof_residual)}, "
            f"hardening={sorted(hardening_residual)}"
        )
    for feature_key in closure_residual:
        if statuses.get(feature_key) != "planned":
            errors.append(f"{feature_key}: residual feature must remain planned")


def _validate_proof_reconciliation(
    errors: list[str],
    ecosystem_proof: dict[str, Any],
    hardening: dict[str, Any],
    final_closure: dict[str, Any],
) -> None:
    reconciliation = final_closure.get("proof_reconciliation", {})
    if reconciliation.get("ecosystem_proof_contract") != ecosystem_proof.get("contract_id"):
        errors.append("proof_reconciliation.ecosystem_proof_contract must match proof")
    if reconciliation.get("ecosystem_hardening_contract") != hardening.get("contract_id"):
        errors.append("proof_reconciliation.ecosystem_hardening_contract must match hardening")
    for flag in (
        "protected_diagnostics_reviewed",
        "dashboard_alerts_reviewed",
        "no_sensitive_content_reviewed",
        "no_open_p0_p1_reviewed",
    ):
        if reconciliation.get(flag) is not True:
            errors.append(f"proof_reconciliation.{flag} must be true")

    if not all(
        finding.get("severity") not in {"P0", "P1"} or finding.get("status") == "closed"
        for finding in hardening.get("findings", [])
        if isinstance(finding, dict)
    ):
        errors.append("hardening findings contain open P0/P1 work")


def _validate_downstream_gateway_evidence(
    errors: list[str], boundary: dict[str, Any]
) -> None:
    if boundary.get("status") != "implemented":
        errors.append("downstream_boundary_hardening.status must be implemented")
    if boundary.get("gateway_pr") != 179:
        errors.append("downstream_boundary_hardening.gateway_pr must be 179")
    if not str(boundary.get("gateway_merge_commit", "")).startswith("2414e7e"):
        errors.append(
            "downstream_boundary_hardening.gateway_merge_commit must reference 2414e7e"
        )
    if not str(boundary.get("gateway_wiki_publish_commit", "")).startswith("94ca9c7"):
        errors.append(
            "downstream_boundary_hardening.gateway_wiki_publish_commit must reference 94ca9c7"
        )


def _validate_downstream_manage_paths(
    errors: list[str], boundary: dict[str, Any]
) -> None:
    manage_paths = set(boundary.get("lotus_manage_allowed_paths", []))
    if manage_paths != REQUIRED_MANAGE_PATHS:
        errors.append(
            "downstream_boundary_hardening.lotus_manage_allowed_paths must be exactly "
            f"{sorted(REQUIRED_MANAGE_PATHS)}"
        )
    stale_manage_paths = [
        path
        for path in manage_paths
        if "/rebalance/proposals" in path or " /rebalance/" in path
    ]
    if stale_manage_paths:
        errors.append(
            "downstream_boundary_hardening must not allow stale lotus-manage "
            f"proposal or unversioned rebalance paths: {stale_manage_paths}"
        )


def _validate_downstream_advise_paths(
    errors: list[str], boundary: dict[str, Any]
) -> None:
    advise_paths = set(boundary.get("lotus_advise_proposal_paths", []))
    missing_advise_paths = sorted(REQUIRED_ADVISE_PROPOSAL_PATHS - advise_paths)
    if missing_advise_paths:
        errors.append(
            "downstream_boundary_hardening.lotus_advise_proposal_paths missing "
            f"{missing_advise_paths}"
        )
    if any("/rebalance/proposals" in path for path in advise_paths):
        errors.append(
            "downstream_boundary_hardening.lotus_advise_proposal_paths must use "
            "/advisory/proposals, not rebalance proposal paths"
        )


def _validate_downstream_forbidden_patterns(
    errors: list[str], boundary: dict[str, Any]
) -> None:
    forbidden_patterns = " ".join(boundary.get("forbidden_gateway_patterns", []))
    for required_fragment in (
        "lotus-manage /rebalance/proposals",
        "lotus-manage /api/v1/rebalance/proposals",
        "unversioned lotus-manage /rebalance",
    ):
        if required_fragment not in forbidden_patterns:
            errors.append(
                "downstream_boundary_hardening.forbidden_gateway_patterns must include "
                f"{required_fragment}"
            )


def _validate_downstream_ownership_decision(
    errors: list[str], boundary: dict[str, Any]
) -> None:
    ownership = str(boundary.get("ownership_decision", ""))
    for required_fragment in ("lotus-advise", "lotus-manage", "strategic DPM runs"):
        if required_fragment not in ownership:
            errors.append(
                "downstream_boundary_hardening.ownership_decision must record "
                f"{required_fragment}"
            )


def _validate_downstream_local_proof(
    errors: list[str], boundary: dict[str, Any]
) -> None:
    local_proof = " ".join(boundary.get("local_proof", []))
    for required_fragment in ("make check passed", "make test-integration passed"):
        if required_fragment not in local_proof:
            errors.append(
                "downstream_boundary_hardening.local_proof must include "
                f"{required_fragment}"
            )


def _validate_downstream_github_checks(
    errors: list[str], boundary: dict[str, Any]
) -> None:
    github_checks = set(boundary.get("github_checks", []))
    missing_gateway_checks = sorted(REQUIRED_GATEWAY_CHECKS - github_checks)
    if missing_gateway_checks:
        errors.append(
            "downstream_boundary_hardening.github_checks missing "
            f"{missing_gateway_checks}"
        )


def _validate_downstream_boundary_hardening(
    errors: list[str], final_closure: dict[str, Any]
) -> None:
    boundary = final_closure.get("downstream_boundary_hardening", {})
    _validate_downstream_gateway_evidence(errors, boundary)
    _validate_downstream_manage_paths(errors, boundary)
    _validate_downstream_advise_paths(errors, boundary)
    _validate_downstream_forbidden_patterns(errors, boundary)
    _validate_downstream_ownership_decision(errors, boundary)
    _validate_downstream_local_proof(errors, boundary)
    _validate_downstream_github_checks(errors, boundary)


def _validate_required_proof(
    errors: list[str], final_closure: dict[str, Any]
) -> None:
    commands = set(final_closure.get("local_proof_commands", []))
    for command_fragment in (
        "validate_analytics_ui_observability_contract.py",
        "validate_analytics_ui_ecosystem_completion.py",
        "validate_analytics_ui_ecosystem_hardening.py",
        "validate_analytics_ui_ecosystem_final_closure.py",
        "test_analytics_ui_ecosystem_final_closure.py",
        "git diff --check",
        "Sync-RepoWikis.ps1 -CheckOnly -Repository lotus-platform",
    ):
        if not any(command_fragment in command for command in commands):
            errors.append(f"local_proof_commands must include {command_fragment}")

    required_checks = set(final_closure.get("required_github_checks", []))
    missing_checks = sorted(REQUIRED_GITHUB_CHECKS - required_checks)
    if missing_checks:
        errors.append(f"required_github_checks missing {missing_checks}")


def _validate_wiki_and_branch_hygiene(
    errors: list[str], final_closure: dict[str, Any]
) -> None:
    wiki = final_closure.get("wiki_publication", {})
    if wiki.get("source_repository") != "lotus-platform":
        errors.append("wiki_publication.source_repository must be lotus-platform")
    if wiki.get("check_required") is not True:
        errors.append("wiki_publication.check_required must be true")
    if wiki.get("publish_required_after_merge") is not True:
        errors.append("wiki_publication.publish_required_after_merge must be true")
    if (
        wiki.get("publish_command")
        != "powershell -ExecutionPolicy Bypass -File automation\\Sync-RepoWikis.ps1 -Publish -Repository lotus-platform"
    ):
        errors.append("wiki_publication.publish_command must publish lotus-platform wiki")

    branch = final_closure.get("branch_hygiene", {})
    if branch.get("branch_name") != "feat/rfc-0108-slice-18-ecosystem-closure":
        errors.append("branch_hygiene.branch_name must name the Slice 18 feature branch")
    if branch.get("one_pr_per_slice") is not True:
        errors.append("branch_hygiene.one_pr_per_slice must be true")
    if branch.get("delete_after_merge") is not True:
        errors.append("branch_hygiene.delete_after_merge must be true")


def _validate_skills_guidance_review(
    errors: list[str], final_closure: dict[str, Any]
) -> None:
    review = final_closure.get("skills_guidance_review", {})
    if review.get("decision") not in {"no_change_required", "changed"}:
        errors.append("skills_guidance_review.decision is required")
    if not review.get("rationale"):
        errors.append("skills_guidance_review.rationale is required")
    reviewed_guidance = set(review.get("reviewed_guidance", []))
    for required in {
        "context/LOTUS-SKILL-ROUTING-MAP.md",
        "context/LOTUS-ENGINEERING-CONTEXT.md",
        "context/CONTEXT-REFERENCE-MAP.md",
        "context/PROCEDURAL-MEMORY-INDEX.md",
    }:
        if required not in reviewed_guidance:
            errors.append(f"skills_guidance_review.reviewed_guidance missing {required}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate RFC-0108 ecosystem final closure contract."
    )
    parser.add_argument(
        "--observability-contract",
        type=Path,
        default=DEFAULT_OBSERVABILITY_CONTRACT_PATH,
    )
    parser.add_argument(
        "--ecosystem-contract",
        type=Path,
        default=DEFAULT_ECOSYSTEM_CONTRACT_PATH,
    )
    parser.add_argument(
        "--ecosystem-proof", type=Path, default=DEFAULT_ECOSYSTEM_PROOF_PATH
    )
    parser.add_argument("--hardening", type=Path, default=DEFAULT_HARDENING_PATH)
    parser.add_argument("--final-closure", type=Path, default=DEFAULT_FINAL_CLOSURE_PATH)
    args = parser.parse_args()

    errors = validate_ecosystem_final_closure(
        observability_contract=_load_json(args.observability_contract),
        ecosystem_contract=_load_json(args.ecosystem_contract),
        ecosystem_proof=_load_json(args.ecosystem_proof),
        hardening=_load_json(args.hardening),
        final_closure=_load_json(args.final_closure),
    )
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Analytics UI ecosystem final closure validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
