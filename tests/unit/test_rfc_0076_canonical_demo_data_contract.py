from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def test_rfc_0076_slice_one_contract_artifacts_are_governed_and_traceable() -> None:
    rfc = (ROOT / "rfcs" / "RFC-0076-canonical-front-office-demo-data-contract.md").read_text(
        encoding="utf-8"
    )
    checklist = (ROOT / "rfcs" / "RFC-0076-implementation-checklist.md").read_text(
        encoding="utf-8"
    )
    evidence = (ROOT / "rfcs" / "RFC-0076-slice-1-contract-spec-evidence.md").read_text(
        encoding="utf-8"
    )
    slice_two_evidence = (
        ROOT / "rfcs" / "RFC-0076-slice-2-core-contract-enforcement-evidence.md"
    ).read_text(encoding="utf-8")
    contract_readme = (ROOT / "context" / "contracts" / "README.md").read_text(encoding="utf-8")

    assert "## Decision" in rfc
    assert "## Skills, Context, and Documentation Implications" in rfc
    assert "### Slice 5: Documentation, Agent Context, Skill Alignment, and Branch Hygiene" in rfc
    assert "- Status: In Progress" in checklist

    for required_item in (
        "- [x] Canonical portfolio ID confirmed as `PB_SG_GLOBAL_BAL_001`.",
        "- [x] Canonical benchmark ID confirmed as `BMK_PB_GLOBAL_BALANCED_60_40`.",
        "- [x] Canonical as-of date confirmed as `2026-04-10`.",
        "- [x] Add governed contract artifact directory under `context/contracts`.",
        "- [x] Add machine-readable canonical demo data contract.",
        "- [x] Add machine-readable canonical demo invariants contract.",
        "- [x] Add platform tests that validate contract presence and required fields.",
        "- [x] Add slice evidence documenting what was introduced and why.",
        "- [x] Update `lotus-core` seed tooling to read or mirror the governed contract.",
        "- [x] Enforce required coverage and deterministic economics in code.",
        "- [x] Add focused tests for economic invariants and stale coverage failure modes.",
        "- [x] Add slice evidence documenting the `lotus-core` adoption path.",
    ):
        assert required_item in checklist

    for required_item in (
        "# RFC-0076 Slice 1 Contract Spec Evidence",
        "PB_SG_GLOBAL_BAL_001",
        "BMK_PB_GLOBAL_BALANCED_60_40",
        "2026-04-10",
        "machine-readable contract",
        "no context or skill docs were changed in this slice",
    ):
        assert required_item in evidence

    for required_item in (
        "# RFC-0076 Slice 2 Core Contract Enforcement Evidence",
        "https://github.com/sgajbi/lotus-core/pull/303",
        "tools/front_office_seed_contract.py",
        "does not hard-depend on `lotus-platform` at runtime",
        "20 passed in 0.55s",
    ):
        assert required_item in slice_two_evidence

    for required_item in (
        "# Context Contracts",
        "canonical-front-office-demo-data-contract.json",
        "canonical-front-office-demo-data-invariants.json",
    ):
        assert required_item in contract_readme


def test_rfc_0076_contract_json_records_governed_identity_and_ownership() -> None:
    contract = _load_json("context/contracts/canonical-front-office-demo-data-contract.json")

    assert contract["contract_id"] == "canonical-front-office-demo-data-contract"
    assert contract["contract_version"] == "1.0.0"
    assert contract["governed_by_rfc"] == "RFC-0076"

    portfolio = contract["portfolio"]
    assert portfolio["portfolio_id"] == "PB_SG_GLOBAL_BAL_001"
    assert portfolio["base_currency"] == "USD"
    assert "YTD" in portfolio["supported_analysis_windows"]

    benchmark = contract["benchmark"]
    assert benchmark["benchmark_code"] == "BMK_PB_GLOBAL_BALANCED_60_40"
    assert benchmark["weight_model"] == {"equity": 0.6, "fixed_income": 0.4}

    date_policy = contract["date_policy"]
    assert date_policy["canonical_as_of_date"] == "2026-04-10"
    assert date_policy["refresh_policy"] == "fixed_until_governed_change"
    assert date_policy["warmup_start_date"] == "2025-01-06"

    assert "multi_currency_exposure" in contract["required_asset_coverage"]
    assert "projected_cashflow" in contract["required_transaction_coverage"]
    assert "risk_free_rates" in contract["required_reference_data"]
    assert "risk_historical_attribution" in contract["required_derived_state"]

    ownership = contract["ownership"]
    assert "seed_identity" in ownership["lotus-core"]
    assert "return_path_support" in ownership["lotus-performance"]
    assert "rolling_risk_support" in ownership["lotus-risk"]
    assert "truthful_downstream_contracts" in ownership["lotus-gateway"]
    assert "no_fake_supportability" in ownership["lotus-workbench"]

    assert contract["validation_layers"] == [
        "data_contract",
        "derived_state_readiness",
        "product_surface_readiness",
    ]


def test_rfc_0076_invariants_json_records_thresholds_and_supported_surface_expectations() -> None:
    invariants = _load_json("context/contracts/canonical-front-office-demo-data-invariants.json")

    assert invariants["contract_id"] == "canonical-front-office-demo-data-invariants"
    assert invariants["contract_version"] == "1.0.0"
    assert invariants["canonical_portfolio_id"] == "PB_SG_GLOBAL_BAL_001"
    assert invariants["canonical_benchmark_code"] == "BMK_PB_GLOBAL_BALANCED_60_40"
    assert invariants["canonical_as_of_date"] == "2026-04-10"

    minimums = invariants["minimum_thresholds"]
    assert minimums["transactions"] >= 30
    assert minimums["valued_positions"] >= 6
    assert minimums["risk_rolling_windows"] >= 4
    assert minimums["risk_attribution_contributors"] >= 7

    support_states = invariants["required_support_states"]
    assert support_states["portfolio.summary"] == "ready"
    assert support_states["performance.summary"] == "ready"
    assert support_states["performance.evidence"] == "truthfully_degraded"

    required_coverage = invariants["required_coverage_assertions"]
    assert (
        "derived_state_must_reach_canonical_as_of_date_before_product_surface_validation"
        in required_coverage
    )

    economic_invariants = invariants["economic_invariants"]
    assert "transaction_ids_are_deterministic" in economic_invariants
    assert "positions_and_cash_legs_reconcile_after_seeded_activity" in economic_invariants
