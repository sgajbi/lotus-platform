from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = (
    ROOT / "automation" / "validate_canonical_front_office_demo_data_contract.py"
)
CONTRACT_PATH = (
    ROOT / "context" / "contracts" / "canonical-front-office-demo-data-contract.json"
)
INVARIANTS_PATH = (
    ROOT / "context" / "contracts" / "canonical-front-office-demo-data-invariants.json"
)
SEED_SCRIPT_PATH = ROOT / "automation" / "Invoke-DpmCommandCenterSeed.ps1"


def _validator():
    spec = importlib.util.spec_from_file_location(
        "validate_canonical_front_office_demo_data_contract", VALIDATOR_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _invariants() -> dict:
    return json.loads(INVARIANTS_PATH.read_text(encoding="utf-8"))


def _seed_script() -> str:
    return SEED_SCRIPT_PATH.read_text(encoding="utf-8")


def test_canonical_front_office_demo_data_contract_passes_focused_validation() -> None:
    assert _validator().validate_default_paths() == []


def test_validator_rejects_missing_core_executable_advisor_book_seed_proof(
    tmp_path,
) -> None:
    errors = _validator().validate_default_paths(core_repo=tmp_path)

    assert len(errors) == 1
    assert "executable advisor-book seed validator is missing" in errors[0]


def test_validator_rejects_drifted_core_executable_seed_evidence(
    monkeypatch, tmp_path
) -> None:
    validator = _validator()
    proof_path = tmp_path / validator.CORE_SEED_VALIDATOR_RELATIVE_PATH
    proof_path.parent.mkdir(parents=True)
    proof_path.write_text("# test executable proof\n", encoding="utf-8")
    evidence = dict(validator.REQUIRED_CORE_SEED_EVIDENCE)
    evidence["portfolio_manager_id"] = "advisor_sg_001"
    monkeypatch.setattr(
        validator.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0], 0, stdout=json.dumps(evidence), stderr=""
        ),
    )

    errors = validator._validate_core_advisor_book_seed(tmp_path)

    assert errors == [
        "lotus-core advisor-book seed evidence.portfolio_manager_id must be PM_SG_001"
    ]


def test_validator_rejects_drift_from_canonical_dpm_seed_identity() -> None:
    contract = _contract()
    contract["dpm_command_center"]["portfolio_manager_id"] = "PM_LOCAL_SMOKE"

    errors = _validator().validate_contract(contract, _invariants(), _seed_script())

    assert "dpm_command_center.portfolio_manager_id must be PM_SG_DPM_001" in errors


def test_validator_rejects_drift_from_canonical_advisor_book_identity() -> None:
    contract = _contract()
    contract["advisor_book"]["portfolio_id"] = "PB_OTHER"
    contract["advisor_book"]["as_of_date"] = "2099-12-31"
    contract["advisor_book"]["portfolio_manager_id"] = "advisor_sg_001"
    contract["advisor_book"]["tenant_identity_posture"] = "source_confirmed"

    errors = _validator().validate_contract(contract, _invariants(), _seed_script())

    assert "advisor_book.portfolio_id must be PB_SG_GLOBAL_BAL_001" in errors
    assert "advisor_book.as_of_date must be 2026-04-10" in errors
    assert (
        "advisor_book.as_of_date must match date_policy.canonical_as_of_date" in errors
    )
    assert (
        "advisor_book.as_of_date must match invariants.canonical_as_of_date" in errors
    )
    assert "advisor_book.portfolio_manager_id must be PM_SG_001" in errors
    assert "advisor_book.tenant_identity_posture must be trusted_context_only" in errors


def test_validator_rejects_advisor_book_canonical_date_policy_drift() -> None:
    contract = _contract()
    contract["date_policy"]["canonical_as_of_date"] = "2099-12-31"

    errors = _validator().validate_contract(contract, _invariants(), _seed_script())

    assert (
        "advisor_book.as_of_date must match date_policy.canonical_as_of_date" in errors
    )


def test_validator_requires_advisor_book_membership_and_lineage_invariants() -> None:
    invariants = _invariants()
    invariants["minimum_thresholds"]["advisor_book_authoritative_memberships"] = 0
    invariants["required_coverage_assertions"] = [
        assertion
        for assertion in invariants["required_coverage_assertions"]
        if not assertion.startswith("advisor_book_")
    ]
    invariants["economic_invariants"] = [
        invariant
        for invariant in invariants["economic_invariants"]
        if invariant != "advisor_book_assignment_identity_is_deterministic"
    ]

    errors = _validator().validate_contract(_contract(), invariants, _seed_script())

    assert any(
        "advisor_book_authoritative_memberships must be >= 1" in error
        for error in errors
    )
    assert any(
        "advisor_book_seed_must_persist_authoritative_portfolio_manager_assignment"
        in error
        for error in errors
    )
    assert any(
        "advisor_book_evidence_must_bind_manager_business_date_and_source_lineage"
        in error
        for error in errors
    )
    assert any(
        "advisor_book_assignment_identity_is_deterministic" in error for error in errors
    )


def test_validator_rejects_missing_required_source_product_lineage() -> None:
    contract = _contract()
    contract["dpm_command_center"]["source_products"] = [
        "DiscretionaryMandateBinding:v1",
    ]

    errors = _validator().validate_contract(contract, _invariants(), _seed_script())

    assert any("ModelPortfolioTargets:v1" in error for error in errors)
    assert any("DpmMarketDataCoverage:v1" in error for error in errors)


def test_validator_rejects_seed_script_hardcoded_mandate_identity() -> None:
    errors = _validator().validate_contract(
        _contract(),
        _invariants(),
        f"{_seed_script()}\nMANDATE_PB_SG_GLOBAL_BAL_001\n",
    )

    assert (
        "Invoke-DpmCommandCenterSeed.ps1 must read mandate identity from contract"
        in errors
    )


def test_validator_rejects_missing_ready_partial_empty_posture_evidence() -> None:
    seed_script = _seed_script().replace("gateway-command-center-empty-posture", "")

    errors = _validator().validate_contract(_contract(), _invariants(), seed_script)

    assert (
        "Invoke-DpmCommandCenterSeed.ps1 is missing step "
        "gateway-command-center-empty-posture"
    ) in errors
