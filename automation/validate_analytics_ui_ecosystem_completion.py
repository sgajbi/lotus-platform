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

REQUIRED_REPOSITORIES = {
    "lotus-platform",
    "lotus-workbench",
    "lotus-gateway",
    "lotus-core",
    "lotus-performance",
    "lotus-risk",
    "lotus-advise",
    "lotus-manage",
    "lotus-report",
    "lotus-render",
    "lotus-archive",
    "lotus-ai",
}

REQUIRED_SLICE_IDS = set(range(10, 19))

IMPLEMENTED_SLICE_10_FEATURE_KEY = (
    "platform.analytics.observability.ecosystem_completion_contract"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_ecosystem_completion(
    *,
    observability_contract: dict[str, Any],
    ecosystem_contract: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    _validate_identity(errors, observability_contract, ecosystem_contract)
    _validate_repositories(errors, ecosystem_contract)
    _validate_slices(errors, ecosystem_contract)
    _validate_supported_features(errors, observability_contract, ecosystem_contract)
    _validate_gap_matrix(errors, observability_contract, ecosystem_contract)
    _validate_required_checks_and_branch_policy(errors, ecosystem_contract)
    return errors


def _validate_identity(
    errors: list[str],
    observability_contract: dict[str, Any],
    ecosystem_contract: dict[str, Any],
) -> None:
    if (
        ecosystem_contract.get("contract_id")
        != "analytics-ui-observability-ecosystem-completion"
    ):
        errors.append(
            "contract_id must be analytics-ui-observability-ecosystem-completion"
        )
    if ecosystem_contract.get("governed_by_rfc") != "RFC-0108":
        errors.append("governed_by_rfc must be RFC-0108")
    if (
        ecosystem_contract.get("lifecycle_status")
        != "slice-10-ecosystem-contract-implemented"
    ):
        errors.append(
            "lifecycle_status must be slice-10-ecosystem-contract-implemented"
        )
    if (
        observability_contract.get("lifecycle_status")
        != "slice-10-ecosystem-contract-implemented"
    ):
        errors.append(
            "analytics-ui-observability-contract lifecycle_status must be "
            "slice-10-ecosystem-contract-implemented"
        )


def _validate_repositories(
    errors: list[str], ecosystem_contract: dict[str, Any]
) -> None:
    participating = set(ecosystem_contract.get("participating_repositories", []))
    missing = REQUIRED_REPOSITORIES - participating
    extra = participating - REQUIRED_REPOSITORIES
    if missing:
        errors.append(f"participating_repositories missing {sorted(missing)}")
    if extra:
        errors.append(f"participating_repositories contains unknown repos {sorted(extra)}")

    matrix_repositories = {
        str(row.get("repository"))
        for row in ecosystem_contract.get("app_gap_matrix", [])
        if isinstance(row, dict)
    }
    missing_matrix = REQUIRED_REPOSITORIES - matrix_repositories
    if missing_matrix:
        errors.append(f"app_gap_matrix missing repositories {sorted(missing_matrix)}")


def _validate_slices(errors: list[str], ecosystem_contract: dict[str, Any]) -> None:
    slices = ecosystem_contract.get("ecosystem_completion_slices", [])
    slice_status = {
        int(slice_entry.get("slice_id")): str(slice_entry.get("status"))
        for slice_entry in slices
        if isinstance(slice_entry, dict) and str(slice_entry.get("slice_id")).isdigit()
    }
    missing = REQUIRED_SLICE_IDS - set(slice_status)
    if missing:
        errors.append(f"ecosystem_completion_slices missing {sorted(missing)}")
    if slice_status.get(10) != "implemented":
        errors.append("Slice 10 must be implemented")
    for slice_id in range(11, 19):
        if slice_status.get(slice_id) != "planned":
            errors.append(f"Slice {slice_id} must remain planned after Slice 10")
    for slice_entry in slices:
        if not slice_entry.get("purpose"):
            errors.append(f"Slice {slice_entry.get('slice_id')}: purpose is required")
        if not slice_entry.get("required_proof"):
            errors.append(
                f"Slice {slice_entry.get('slice_id')}: required_proof is required"
            )


def _feature_status(observability_contract: dict[str, Any]) -> dict[str, str]:
    return {
        str(feature.get("feature_key")): str(feature.get("status"))
        for feature in observability_contract.get("supported_feature_keys", [])
        if isinstance(feature, dict)
    }


def _validate_supported_features(
    errors: list[str],
    observability_contract: dict[str, Any],
    ecosystem_contract: dict[str, Any],
) -> None:
    statuses = _feature_status(observability_contract)
    if statuses.get(IMPLEMENTED_SLICE_10_FEATURE_KEY) != "implemented":
        errors.append(
            f"{IMPLEMENTED_SLICE_10_FEATURE_KEY} must be implemented after Slice 10"
        )

    protected = set(
        ecosystem_contract.get("first_wave_evidence", {}).get(
            "protected_feature_keys", []
        )
    )
    missing_protected = protected - set(statuses)
    if missing_protected:
        errors.append(
            "first_wave_evidence.protected_feature_keys missing from supported "
            f"features: {sorted(missing_protected)}"
        )
    for feature_key in protected:
        if statuses.get(feature_key) != "implemented":
            errors.append(f"{feature_key}: first-wave protected feature must stay implemented")

    matrix_feature_keys = {
        str(feature_key)
        for row in ecosystem_contract.get("app_gap_matrix", [])
        if isinstance(row, dict)
        for feature_key in row.get("feature_keys", [])
    }
    missing_matrix_features = matrix_feature_keys - set(statuses)
    if missing_matrix_features:
        errors.append(
            "app_gap_matrix references unsupported feature keys: "
            f"{sorted(missing_matrix_features)}"
        )

    for feature_key in matrix_feature_keys - protected:
        if feature_key == IMPLEMENTED_SLICE_10_FEATURE_KEY:
            continue
        if statuses.get(feature_key) != "planned":
            errors.append(f"{feature_key}: ecosystem feature must remain planned")


def _validate_gap_matrix(
    errors: list[str],
    observability_contract: dict[str, Any],
    ecosystem_contract: dict[str, Any],
) -> None:
    statuses = _feature_status(observability_contract)
    for row in ecosystem_contract.get("app_gap_matrix", []):
        repo = str(row.get("repository", "<missing>"))
        posture = row.get("posture")
        if posture not in {
            "implemented",
            "partially_implemented",
            "planned",
            "not_applicable_with_rationale",
            "blocked_with_owner",
        }:
            errors.append(f"{repo}: invalid posture {posture}")
        for required_field in (
            "role",
            "feature_keys",
            "gap_classification",
            "blockers",
            "required_proof",
            "wiki_source_decision",
            "runbook_requirements",
        ):
            value = row.get(required_field)
            if not value:
                errors.append(f"{repo}: {required_field} is required")
        for feature_key in row.get("feature_keys", []):
            if feature_key not in statuses:
                errors.append(f"{repo}: unknown feature key {feature_key}")
        if posture == "implemented":
            not_implemented = [
                feature_key
                for feature_key in row.get("feature_keys", [])
                if statuses.get(feature_key) != "implemented"
            ]
            if not_implemented:
                errors.append(
                    f"{repo}: implemented posture has planned features "
                    f"{sorted(not_implemented)}"
                )
        if repo != "lotus-platform" and posture == "implemented":
            errors.append(f"{repo}: non-platform rows must not be fully implemented in Slice 10")


def _validate_required_checks_and_branch_policy(
    errors: list[str], ecosystem_contract: dict[str, Any]
) -> None:
    required_checks = set(ecosystem_contract.get("required_github_checks", []))
    for check_name in {
        "Cross-App Vocabulary Gate",
        "Feature Lane / Platform Repo Contracts",
        "Feature Lane / Workflow Lint",
        "PR Merge Gate / Platform Repo Contracts",
        "PR Merge Gate / Workflow Lint",
    }:
        if check_name not in required_checks:
            errors.append(f"required_github_checks missing {check_name}")

    branch_policy = ecosystem_contract.get("branch_policy", {})
    if branch_policy.get("one_pr_per_slice") is not True:
        errors.append("branch_policy.one_pr_per_slice must be true")
    if branch_policy.get("runtime_work_blocked_before_slice_10_merge") is not True:
        errors.append(
            "branch_policy.runtime_work_blocked_before_slice_10_merge must be true"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate RFC-0108 ecosystem observability completion contract."
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
    args = parser.parse_args()

    errors = validate_ecosystem_completion(
        observability_contract=_load_json(args.observability_contract),
        ecosystem_contract=_load_json(args.ecosystem_contract),
    )
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Analytics UI ecosystem completion validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
