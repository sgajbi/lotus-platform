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

LIFECYCLE_STATUS = "slice-17-ecosystem-hardening-certified"
HARDENING_FEATURE_KEY = (
    "platform.analytics.observability.ecosystem_hardening_certification"
)
FINAL_CLOSURE_FEATURE_KEY = "platform.analytics.observability.ecosystem_final_closure"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _feature_status(observability_contract: dict[str, Any]) -> dict[str, str]:
    return {
        str(feature.get("feature_key")): str(feature.get("status"))
        for feature in observability_contract.get("supported_feature_keys", [])
        if isinstance(feature, dict)
    }


def validate_ecosystem_hardening(
    *,
    observability_contract: dict[str, Any],
    ecosystem_contract: dict[str, Any],
    ecosystem_proof: dict[str, Any],
    hardening: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    _validate_identity(errors, observability_contract, ecosystem_contract, hardening)
    _validate_source_contracts(errors, hardening)
    _validate_repository_reviews(errors, ecosystem_contract, hardening)
    _validate_api_and_proof(errors, ecosystem_proof, hardening)
    _validate_supported_features(errors, observability_contract, ecosystem_proof, hardening)
    _validate_findings(errors, hardening)
    _validate_required_checks(errors, hardening)
    return errors


def _validate_identity(
    errors: list[str],
    observability_contract: dict[str, Any],
    ecosystem_contract: dict[str, Any],
    hardening: dict[str, Any],
) -> None:
    if hardening.get("contract_id") != "analytics-ui-observability-ecosystem-hardening":
        errors.append("contract_id must be analytics-ui-observability-ecosystem-hardening")
    if hardening.get("governed_by_rfc") != "RFC-0108":
        errors.append("governed_by_rfc must be RFC-0108")
    if hardening.get("lifecycle_status") != LIFECYCLE_STATUS:
        errors.append(f"lifecycle_status must be {LIFECYCLE_STATUS}")
    if observability_contract.get("lifecycle_status") != LIFECYCLE_STATUS:
        errors.append(
            f"analytics-ui-observability-contract lifecycle_status must be {LIFECYCLE_STATUS}"
        )
    if ecosystem_contract.get("lifecycle_status") != LIFECYCLE_STATUS:
        errors.append(
            "analytics-ui-observability-ecosystem-completion lifecycle_status must "
            f"be {LIFECYCLE_STATUS}"
        )


def _validate_source_contracts(errors: list[str], hardening: dict[str, Any]) -> None:
    required = {
        "analytics-ui-observability-contract",
        "analytics-ui-observability-ecosystem-completion",
        "analytics-ui-observability-ecosystem-proof",
    }
    actual = set(hardening.get("source_contracts", []))
    missing = sorted(required - actual)
    if missing:
        errors.append(f"source_contracts missing {missing}")


def _validate_repository_reviews(
    errors: list[str],
    ecosystem_contract: dict[str, Any],
    hardening: dict[str, Any],
) -> None:
    matrix_by_repo = {
        str(row.get("repository")): row
        for row in ecosystem_contract.get("app_gap_matrix", [])
        if isinstance(row, dict)
    }
    review_by_repo = {
        str(review.get("repository")): review
        for review in hardening.get("repository_reviews", [])
        if isinstance(review, dict)
    }
    missing = sorted(set(matrix_by_repo) - set(review_by_repo))
    extra = sorted(set(review_by_repo) - set(matrix_by_repo))
    if missing:
        errors.append(f"repository_reviews missing {missing}")
    if extra:
        errors.append(f"repository_reviews contains unknown repositories {extra}")

    for repo, review in review_by_repo.items():
        matrix_row = matrix_by_repo.get(repo, {})
        reviewed_features = set(review.get("feature_keys_reviewed", []))
        matrix_features = set(matrix_row.get("feature_keys", []))
        missing_features = sorted(matrix_features - reviewed_features)
        if missing_features:
            errors.append(f"{repo}: feature_keys_reviewed missing {missing_features}")
        if review.get("no_open_p0_p1") is not True:
            errors.append(f"{repo}: no_open_p0_p1 must be true")
        if not review.get("ci_evidence"):
            errors.append(f"{repo}: ci_evidence is required")
        if (
            repo == "lotus-platform"
            and review.get("review_status") != "certified_current_scope"
        ):
            errors.append("lotus-platform: review_status must certify current scope")


def _validate_api_and_proof(
    errors: list[str],
    ecosystem_proof: dict[str, Any],
    hardening: dict[str, Any],
) -> None:
    reconciliation = hardening.get("proof_reconciliation", {})
    if (
        reconciliation.get("ecosystem_proof_contract")
        != ecosystem_proof.get("contract_id")
    ):
        errors.append("proof_reconciliation.ecosystem_proof_contract must match proof")
    if reconciliation.get("protected_diagnostics_reviewed") is not True:
        errors.append("protected diagnostics must be reviewed")
    if reconciliation.get("dashboard_alerts_reviewed") is not True:
        errors.append("dashboard and alert proof must be reviewed")
    if reconciliation.get("no_sensitive_content_reviewed") is not True:
        errors.append("no-sensitive-content proof must be reviewed")

    required_paths = set(ecosystem_proof.get("openapi_proof", {}).get("required_paths", []))
    reviewed_paths = set(reconciliation.get("openapi_paths_reviewed", []))
    missing_paths = sorted(required_paths - reviewed_paths)
    if missing_paths:
        errors.append(f"proof_reconciliation.openapi_paths_reviewed missing {missing_paths}")

    if not any(
        item.get("openapi_required") is True
        and item.get("certification_status") == "certified"
        for item in hardening.get("api_certification_review", [])
    ):
        errors.append("api_certification_review must certify at least one OpenAPI surface")
    for item in hardening.get("api_certification_review", []):
        surface = str(item.get("surface", "<missing>"))
        if item.get("openapi_required") is True and item.get("certification_status") not in {
            "certified",
            "planned_residual",
        }:
            errors.append(f"{surface}: OpenAPI-required surface must be certified or planned")
        if not item.get("evidence"):
            errors.append(f"{surface}: evidence is required")


def _validate_supported_features(
    errors: list[str],
    observability_contract: dict[str, Any],
    ecosystem_proof: dict[str, Any],
    hardening: dict[str, Any],
) -> None:
    statuses = _feature_status(observability_contract)
    if statuses.get(HARDENING_FEATURE_KEY) != "implemented":
        errors.append(f"{HARDENING_FEATURE_KEY} must be implemented for Slice 17")
    if statuses.get(FINAL_CLOSURE_FEATURE_KEY) != "planned":
        errors.append(f"{FINAL_CLOSURE_FEATURE_KEY} must remain planned before Slice 18")

    audit = hardening.get("supported_features_audit", {})
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
    if HARDENING_FEATURE_KEY not in implemented_reviewed:
        errors.append(f"supported_features_audit must review {HARDENING_FEATURE_KEY}")
    if FINAL_CLOSURE_FEATURE_KEY not in planned_reviewed:
        errors.append(f"supported_features_audit must keep {FINAL_CLOSURE_FEATURE_KEY} planned")
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
    if hardening_residual != proof_residual:
        errors.append(
            "residual_scope must match ecosystem proof residual scope: "
            f"expected {sorted(proof_residual)}, actual {sorted(hardening_residual)}"
        )
    for feature_key in hardening_residual:
        if statuses.get(feature_key) != "planned":
            errors.append(f"{feature_key}: residual feature must remain planned")


def _validate_findings(errors: list[str], hardening: dict[str, Any]) -> None:
    for finding in hardening.get("findings", []):
        severity = finding.get("severity")
        status = finding.get("status")
        finding_id = str(finding.get("finding_id", "<missing>"))
        if severity in {"P0", "P1"} and status != "closed":
            errors.append(f"{finding_id}: P0/P1 findings must be closed")
        if status == "planned_residual" and severity in {"P0", "P1"}:
            errors.append(f"{finding_id}: P0/P1 findings cannot be planned residual")
        if not finding.get("summary") or not finding.get("evidence"):
            errors.append(f"{finding_id}: summary and evidence are required")


def _validate_required_checks(errors: list[str], hardening: dict[str, Any]) -> None:
    required_commands = set(hardening.get("required_local_commands", []))
    for command_fragment in (
        "validate_analytics_ui_observability_contract.py",
        "validate_analytics_ui_ecosystem_completion.py",
        "validate_analytics_ui_ecosystem_hardening.py",
        "test_analytics_ui_ecosystem_hardening.py",
    ):
        if not any(command_fragment in command for command in required_commands):
            errors.append(f"required_local_commands must include {command_fragment}")

    required_checks = set(hardening.get("required_github_checks", []))
    for check_name in (
        "Cross-App Vocabulary Gate",
        "Feature Lane / Platform Repo Contracts",
        "PR Merge Gate / Platform Repo Contracts",
    ):
        if check_name not in required_checks:
            errors.append(f"required_github_checks missing {check_name}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate RFC-0108 ecosystem hardening certification contract."
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
    args = parser.parse_args()

    errors = validate_ecosystem_hardening(
        observability_contract=_load_json(args.observability_contract),
        ecosystem_contract=_load_json(args.ecosystem_contract),
        ecosystem_proof=_load_json(args.ecosystem_proof),
        hardening=_load_json(args.hardening),
    )
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Analytics UI ecosystem hardening validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
