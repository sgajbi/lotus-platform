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
DEFAULT_ROLLOUT_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-rollout-readiness.json"
)
DEFAULT_HARDENING_REVIEW_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-hardening-review.json"
)
DEFAULT_FINAL_CLOSURE_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-final-closure.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_final_closure(
    *,
    observability_contract: dict[str, Any],
    rollout_contract: dict[str, Any],
    hardening_review: dict[str, Any],
    final_closure: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if final_closure.get("contract_id") != "analytics-ui-observability-final-closure":
        errors.append("contract_id must be analytics-ui-observability-final-closure")
    if final_closure.get("governed_by_rfc") != "RFC-0108":
        errors.append("governed_by_rfc must be RFC-0108")
    if final_closure.get("lifecycle_status") != "final-closure-implemented":
        errors.append("lifecycle_status must be final-closure-implemented")

    allowed_reopened_lifecycle = {
        "final-closure-implemented",
        "slice-10-ecosystem-contract-implemented",
        "slice-11-scaffold-ci-enforcement-implemented",
        "slice-13-gateway-fanout-metrics-partial-implemented",
        "slice-13-gateway-fanout-metrics-implemented",
        "slice-14-workbench-supported-client-reads-partial-implemented",
        "slice-15-ecosystem-dashboards-alerts-implemented",
    }
    if observability_contract.get("lifecycle_status") not in allowed_reopened_lifecycle:
        errors.append(
            "analytics-ui-observability-contract lifecycle_status must be "
            "final-closure-implemented, slice-10-ecosystem-contract-implemented, "
            "slice-11-scaffold-ci-enforcement-implemented, or "
            "slice-13-gateway-fanout-metrics-partial-implemented, or "
            "slice-13-gateway-fanout-metrics-implemented, or "
            "slice-14-workbench-supported-client-reads-partial-implemented, or "
            "slice-15-ecosystem-dashboards-alerts-implemented"
        )

    closure_scope = final_closure.get("closure_scope", {})
    if closure_scope.get("implemented_scope_status") != "closed_for_implemented_scope":
        errors.append("closure_scope.implemented_scope_status must close implemented scope")
    if closure_scope.get("supported_features_policy") != "implementation_backed_only":
        errors.append("closure_scope.supported_features_policy must be implementation_backed_only")
    if closure_scope.get("residual_scope_policy") != "planned_until_separately_implemented":
        errors.append("closure_scope.residual_scope_policy must preserve planned residuals")

    _validate_merged_prs(errors, final_closure)
    _validate_required_commands_and_checks(errors, final_closure)
    _validate_wiki_publication(errors, final_closure)
    _validate_skills_guidance_review(errors, final_closure)
    _validate_residual_scope(
        errors, observability_contract, rollout_contract, hardening_review, final_closure
    )
    _validate_clean_state_requirements(errors, final_closure)
    return errors


def _validate_merged_prs(errors: list[str], final_closure: dict[str, Any]) -> None:
    prs = final_closure.get("merged_prs", [])
    pr_numbers = {pr.get("pr_number") for pr in prs if isinstance(pr, dict)}
    for required_pr in {225, 233, 234, 235}:
        if required_pr not in pr_numbers:
            errors.append(f"merged_prs missing PR #{required_pr}")
    for pr in prs:
        if not pr.get("merge_commit") or not pr.get("scope"):
            errors.append(f"PR #{pr.get('pr_number', '<missing>')}: merge_commit and scope are required")


def _validate_required_commands_and_checks(
    errors: list[str], final_closure: dict[str, Any]
) -> None:
    commands = set(final_closure.get("local_proof_commands", []))
    for command_fragment in (
        "validate_analytics_ui_observability_contract.py",
        "validate_analytics_ui_rollout_readiness.py",
        "validate_analytics_ui_hardening_review.py",
        "validate_analytics_ui_final_closure.py",
        "test_analytics_ui_final_closure.py",
        "Sync-RepoWikis.ps1 -CheckOnly -Repository lotus-platform",
    ):
        if not any(command_fragment in command for command in commands):
            errors.append(f"local_proof_commands must include {command_fragment}")

    required_checks = set(final_closure.get("required_github_checks", []))
    for check_name in (
        "Cross-App Vocabulary Gate",
        "Feature Lane / Platform Repo Contracts",
        "Feature Lane / Workflow Lint",
        "PR Merge Gate / Platform Repo Contracts",
        "PR Merge Gate / Workflow Lint",
    ):
        if check_name not in required_checks:
            errors.append(f"required_github_checks missing {check_name}")


def _validate_wiki_publication(errors: list[str], final_closure: dict[str, Any]) -> None:
    wiki = final_closure.get("wiki_publication", {})
    if wiki.get("source_repository") != "lotus-platform":
        errors.append("wiki_publication.source_repository must be lotus-platform")
    if wiki.get("publish_required_after_merge") is not True:
        errors.append("wiki publication must be required after merge")
    if wiki.get("check_required") is not True:
        errors.append("wiki check must be required")
    if wiki.get("pre_merge_drift_expected") is not True:
        errors.append("wiki_publication.pre_merge_drift_expected must be true")
    drift_files = set(wiki.get("expected_pre_merge_drift_files", []))
    if "RFC-Index.md" not in drift_files:
        errors.append("wiki_publication.expected_pre_merge_drift_files missing RFC-Index.md")
    if (
        wiki.get("publish_command")
        != "powershell -ExecutionPolicy Bypass -File automation\\Sync-RepoWikis.ps1 -Publish -Repository lotus-platform"
    ):
        errors.append("wiki_publication.publish_command must publish lotus-platform wiki")


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
    }:
        if required not in reviewed_guidance:
            errors.append(f"skills_guidance_review.reviewed_guidance missing {required}")


def _validate_residual_scope(
    errors: list[str],
    observability_contract: dict[str, Any],
    rollout_contract: dict[str, Any],
    hardening_review: dict[str, Any],
    final_closure: dict[str, Any],
) -> None:
    feature_status = {
        str(feature.get("feature_key")): str(feature.get("status"))
        for feature in observability_contract.get("supported_feature_keys", [])
        if isinstance(feature, dict)
    }
    rollout_residual = {
        str(item.get("feature_key"))
        for item in rollout_contract.get("residual_scope", [])
        if isinstance(item, dict)
    }
    hardening_residual = {
        str(item.get("feature_key"))
        for item in hardening_review.get("residual_scope", [])
        if isinstance(item, dict)
    }
    final_residual = {
        str(item.get("feature_key"))
        for item in final_closure.get("residual_scope", [])
        if isinstance(item, dict)
    }
    if final_residual != rollout_residual or final_residual != hardening_residual:
        errors.append(
            "final residual scope must match rollout and hardening residual scope: "
            f"final={sorted(final_residual)}, rollout={sorted(rollout_residual)}, "
            f"hardening={sorted(hardening_residual)}"
        )
    for feature_key in final_residual:
        if feature_status.get(feature_key) != "planned":
            errors.append(f"{feature_key}: residual feature must remain planned")


def _validate_clean_state_requirements(
    errors: list[str], final_closure: dict[str, Any]
) -> None:
    requirements = set(final_closure.get("clean_state_requirements", []))
    for required in {
        "lotus-platform main clean after merge",
        "lotus-workbench main clean after merge",
        "lotus-gateway main clean after merge",
        "lotus-manage main clean after merge",
        "feature branch deleted locally and remotely after squash merge",
    }:
        if required not in requirements:
            errors.append(f"clean_state_requirements missing {required}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate RFC-0108 analytics UI final closure contract."
    )
    parser.add_argument(
        "--observability-contract",
        type=Path,
        default=DEFAULT_OBSERVABILITY_CONTRACT_PATH,
    )
    parser.add_argument(
        "--rollout-contract", type=Path, default=DEFAULT_ROLLOUT_CONTRACT_PATH
    )
    parser.add_argument(
        "--hardening-review", type=Path, default=DEFAULT_HARDENING_REVIEW_PATH
    )
    parser.add_argument("--final-closure", type=Path, default=DEFAULT_FINAL_CLOSURE_PATH)
    args = parser.parse_args()

    errors = validate_final_closure(
        observability_contract=_load_json(args.observability_contract),
        rollout_contract=_load_json(args.rollout_contract),
        hardening_review=_load_json(args.hardening_review),
        final_closure=_load_json(args.final_closure),
    )
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Analytics UI final closure validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
