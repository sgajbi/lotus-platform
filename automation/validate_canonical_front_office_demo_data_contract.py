from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "context" / "contracts" / "canonical-front-office-demo-data-contract.json"
INVARIANTS_PATH = (
    ROOT / "context" / "contracts" / "canonical-front-office-demo-data-invariants.json"
)
SEED_SCRIPT_PATH = ROOT / "automation" / "Invoke-DpmCommandCenterSeed.ps1"
REQUIRED_CONTRACT_VERSION = "1.1.0"

REQUIRED_DPM_IDENTITIES = {
    "portfolio_id": "PB_SG_GLOBAL_BAL_001",
    "mandate_id": "MANDATE_PB_SG_GLOBAL_BAL_001",
    "portfolio_manager_id": "PM_SG_DPM_001",
    "book_id": "BOOK_SG_BALANCED_DPM",
    "tenant_id": "default",
    "command_center_as_of_date": "2026-05-03",
}
REQUIRED_ADVISOR_BOOK_IDENTITIES = {
    "portfolio_id": "PB_SG_GLOBAL_BAL_001",
    "portfolio_manager_id": "PM_SG_001",
    "role_type": "portfolio_manager",
    "role_scope": "portfolio_management",
    "assignment_effective_from_policy": "date_policy.seed_start_date",
    "assignment_version": 1,
    "source_system": "LOTUS_FRONT_OFFICE_SEED",
    "source_record_id": "pb_sg_global_bal_001_pm_sg_001_portfolio_manager_v1",
    "quality_status": "accepted",
    "source_product": "PortfolioManagerBookMembership:v1",
    "gateway_validation_endpoint": "/api/v1/advisor-book/portfolios",
    "expected_workbench_panel": "advisor.book_overview",
    "tenant_identity_posture": "trusted_context_only",
    "tenant_identity_follow_up": "lotus-core#798",
}
REQUIRED_SOURCE_PRODUCTS = {
    "DiscretionaryMandateBinding:v1",
    "ModelPortfolioTargets:v1",
    "DpmEligibilitySnapshot:v1",
    "DpmTaxLotSnapshot:v1",
    "DpmMarketDataCoverage:v1",
}
REQUIRED_GATEWAY_ENDPOINTS = {
    "/api/v1/dpm/command-center",
    "/api/v1/dpm/command-center/exceptions",
    "/api/v1/dpm/command-center/mandates/by-portfolio/{portfolio_id}",
    "/api/v1/dpm/command-center/mandates/{mandate_id}/health",
}
REQUIRED_COVERAGE_ASSERTIONS = {
    "advisor_book_seed_must_persist_authoritative_portfolio_manager_assignment_before_workbench_validation",
    "advisor_book_evidence_must_bind_manager_business_date_and_source_lineage",
    "dpm_command_center_seed_refresh_must_persist_mandate_before_workbench_validation",
    "dpm_command_center_validation_must_cover_populated_ready_partial_and_empty_states",
    "dpm_command_center_evidence_must_record_source_product_lineage",
    "dpm_command_center_degraded_and_blocked_seed_fixtures_require_source_owner_cases",
}
REQUIRED_ECONOMIC_INVARIANTS = {
    "advisor_book_assignment_identity_is_deterministic",
}
REQUIRED_SEED_STEPS = {
    "manage-refresh-from-core",
    "manage-monitoring-run-once",
    "manage-mandate-health-source-contexts",
    "manage-action-register-stateful-simulation",
    "manage-campaign-definition-upsert",
    "gateway-mandate-by-portfolio",
    "gateway-mandate-health",
    "gateway-command-center-summary",
    "gateway-outcome-review-create",
    "gateway-outcome-review-list",
    "gateway-command-center-partial-posture",
    "gateway-command-center-empty-posture",
}


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _string_set(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _add_missing(
    errors: list[str],
    *,
    path: str,
    observed: set[str],
    required: set[str],
) -> None:
    missing = sorted(required - observed)
    if missing:
        errors.append(f"{path} is missing: {', '.join(missing)}")


def validate_contract(
    contract: dict[str, Any],
    invariants: dict[str, Any],
    seed_script: str,
) -> list[str]:
    errors: list[str] = []
    if contract.get("contract_version") != REQUIRED_CONTRACT_VERSION:
        errors.append(f"canonical contract version must be {REQUIRED_CONTRACT_VERSION}")
    if invariants.get("contract_version") != REQUIRED_CONTRACT_VERSION:
        errors.append(f"canonical invariants version must be {REQUIRED_CONTRACT_VERSION}")
    dpm = contract.get("dpm_command_center")
    advisor_book = contract.get("advisor_book")
    if not isinstance(dpm, dict):
        errors.append("canonical contract must define dpm_command_center")
    if not isinstance(advisor_book, dict):
        errors.append("canonical contract must define advisor_book")

    if isinstance(dpm, dict):
        _validate_dpm_identity(errors, dpm)
        _validate_source_products(errors, dpm)
        _validate_surface_states(errors, dpm, invariants)
        _validate_campaign_definition(errors, dpm)
        _validate_multi_portfolio_wave(errors, dpm)
    if isinstance(advisor_book, dict):
        _validate_advisor_book(errors, advisor_book, invariants)
    _validate_invariants(errors, invariants)
    _validate_seed_script(errors, seed_script)
    return errors


def _validate_dpm_identity(errors: list[str], dpm: dict[str, Any]) -> None:
    for field, expected in REQUIRED_DPM_IDENTITIES.items():
        if dpm.get(field) != expected:
            errors.append(f"dpm_command_center.{field} must be {expected}")
    if dpm.get("seed_refresh_endpoint") != (
        "lotus-manage:/api/v1/mandates/{mandate_id}/refresh-from-core"
    ):
        errors.append("dpm_command_center.seed_refresh_endpoint must use lotus-manage refresh")


def _validate_advisor_book(
    errors: list[str],
    advisor_book: dict[str, Any],
    invariants: dict[str, Any],
) -> None:
    for field, expected in REQUIRED_ADVISOR_BOOK_IDENTITIES.items():
        if advisor_book.get(field) != expected:
            errors.append(f"advisor_book.{field} must be {expected}")
    support_states = invariants.get("required_support_states")
    if not isinstance(support_states, dict) or support_states.get(
        "advisor.book_overview"
    ) != "partial":
        errors.append("invariants.required_support_states.advisor.book_overview must be partial")


def _validate_source_products(errors: list[str], dpm: dict[str, Any]) -> None:
    _add_missing(
        errors,
        path="dpm_command_center.source_products",
        observed=_string_set(dpm.get("source_products")),
        required=REQUIRED_SOURCE_PRODUCTS,
    )
    _add_missing(
        errors,
        path="dpm_command_center.gateway_validation_endpoints",
        observed=_string_set(dpm.get("gateway_validation_endpoints")),
        required=REQUIRED_GATEWAY_ENDPOINTS,
    )


def _validate_surface_states(
    errors: list[str],
    dpm: dict[str, Any],
    invariants: dict[str, Any],
) -> None:
    if dpm.get("validated_surface_states") != ["ready", "partial", "empty"]:
        errors.append("dpm_command_center.validated_surface_states must be ready, partial, empty")
    if dpm.get("future_surface_states") != ["degraded", "blocked"]:
        errors.append("dpm_command_center.future_surface_states must preserve degraded, blocked")
    support_states = invariants.get("required_support_states")
    if not isinstance(support_states, dict) or support_states.get("dpm.command_center") != "ready":
        errors.append("invariants.required_support_states.dpm.command_center must be ready")


def _validate_campaign_definition(errors: list[str], dpm: dict[str, Any]) -> None:
    campaign = dpm.get("campaign_definition_scenario")
    if not isinstance(campaign, dict):
        errors.append("dpm_command_center.campaign_definition_scenario is required")
        return
    if campaign.get("candidate_source_product") != "DpmPortfolioUniverseCandidate:v1":
        errors.append("campaign_definition_scenario.candidate_source_product must be governed")
    selection_basis = campaign.get("candidate_selection_basis")
    if not isinstance(selection_basis, dict):
        errors.append("campaign_definition_scenario.candidate_selection_basis is required")
        return
    if selection_basis.get("basis_type") != "EFFECTIVE_DISCRETIONARY_MANDATE_BINDING":
        errors.append("campaign selection basis must use effective discretionary mandate binding")
    if selection_basis.get("source_table") != "portfolio_mandate_bindings":
        errors.append("campaign selection basis must name the source table")
    if "does not discover a global universe" not in str(selection_basis.get("downstream_boundary")):
        errors.append("campaign selection basis must bound platform-local discovery")


def _validate_multi_portfolio_wave(errors: list[str], dpm: dict[str, Any]) -> None:
    wave = dpm.get("multi_portfolio_wave_scenario")
    if not isinstance(wave, dict):
        errors.append("dpm_command_center.multi_portfolio_wave_scenario is required")
        return
    if wave.get("source_scope") != "manage_live_validation_scenario_seed":
        errors.append("multi_portfolio_wave_scenario.source_scope must stay manage-owned")
    portfolios = wave.get("portfolios")
    if not isinstance(portfolios, list) or len(portfolios) < 3:
        errors.append("multi_portfolio_wave_scenario.portfolios must include at least 3 items")
        return
    if not all(isinstance(item, dict) and item.get("source_refs") for item in portfolios):
        errors.append("multi_portfolio_wave_scenario.portfolios must carry source_refs")


def _validate_invariants(errors: list[str], invariants: dict[str, Any]) -> None:
    coverage = _string_set(invariants.get("required_coverage_assertions"))
    _add_missing(
        errors,
        path="invariants.required_coverage_assertions",
        observed=coverage,
        required=REQUIRED_COVERAGE_ASSERTIONS,
    )
    economic_invariants = _string_set(invariants.get("economic_invariants"))
    _add_missing(
        errors,
        path="invariants.economic_invariants",
        observed=economic_invariants,
        required=REQUIRED_ECONOMIC_INVARIANTS,
    )
    thresholds = invariants.get("minimum_thresholds")
    if not isinstance(thresholds, dict):
        errors.append("invariants.minimum_thresholds must be an object")
        return
    threshold_requirements = {
        "advisor_book_authoritative_memberships": 1,
        "dpm_command_center_mandates": 1,
        "dpm_command_center_health_dimensions": 1,
        "dpm_multi_portfolio_wave_candidates": 3,
    }
    for field, minimum in threshold_requirements.items():
        observed = thresholds.get(field)
        if not isinstance(observed, int) or observed < minimum:
            errors.append(f"invariants.minimum_thresholds.{field} must be >= {minimum}")


def _validate_seed_script(errors: list[str], seed_script: str) -> None:
    for required in REQUIRED_SEED_STEPS:
        if required not in seed_script:
            errors.append(f"Invoke-DpmCommandCenterSeed.ps1 is missing step {required}")
    if "MANDATE_PB_SG_GLOBAL_BAL_001" in seed_script:
        errors.append("Invoke-DpmCommandCenterSeed.ps1 must read mandate identity from contract")
    for required in (
        "canonical-front-office-demo-data-contract.json",
        "dpm_command_center",
        "posture_checks",
        "ready-populated-command-center",
        "partial-selector-command-center",
        "empty-filter-command-center",
        "source-owned selection_basis evidence",
        "DpmRealizedOutcomeSnapshot:v1",
    ):
        if required not in seed_script:
            errors.append(f"Invoke-DpmCommandCenterSeed.ps1 must include {required}")


def validate_default_paths() -> list[str]:
    return validate_contract(
        contract=_load_json_object(CONTRACT_PATH),
        invariants=_load_json_object(INVARIANTS_PATH),
        seed_script=SEED_SCRIPT_PATH.read_text(encoding="utf-8"),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the canonical front-office demo data contract."
    )
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--invariants", type=Path, default=INVARIANTS_PATH)
    parser.add_argument("--seed-script", type=Path, default=SEED_SCRIPT_PATH)
    args = parser.parse_args(argv)

    errors = validate_contract(
        contract=_load_json_object(args.contract),
        invariants=_load_json_object(args.invariants),
        seed_script=args.seed_script.read_text(encoding="utf-8"),
    )
    if errors:
        print("Canonical front-office demo data contract validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Canonical front-office demo data contract validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
