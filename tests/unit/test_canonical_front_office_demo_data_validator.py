from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


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


def test_default_path_validation_does_not_require_a_core_checkout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validator = _validator()

    def fail_if_resolved(*_args, **_kwargs):
        pytest.fail("default Platform validation must not resolve a Core checkout")

    monkeypatch.setattr(validator, "_resolve_core_repo", fail_if_resolved)

    assert validator.validate_default_paths() == []


def test_validator_rejects_missing_core_executable_advisor_book_seed_proof(
    tmp_path: Path,
) -> None:
    """Every Core-backed proof must report its own absence.

    Named rather than counted: a count says nothing about which proof went
    missing, and it fails whenever another producer check is added even though
    both findings are correct.
    """
    errors = _validator().validate_default_paths(core_repo=tmp_path)

    assert any(
        "executable advisor-book seed validator is missing" in error
        for error in errors
    )
    assert any("source tenant authority is missing" in error for error in errors)


@pytest.mark.parametrize(
    ("field", "drifted_value"),
    [
        ("status", "partial"),
        ("portfolio_id", "PB_OTHER"),
        ("portfolio_manager_id", "advisor_sg_001"),
        ("as_of_date", "2099-12-31"),
        ("role_type", "investment_advisor"),
        ("role_scope", "advisory"),
        ("effective_from", "2099-01-01"),
        ("effective_to", "2099-12-31"),
        ("assignment_version", 2),
        ("source_system", "UNTRUSTED_SEED"),
        ("source_record_id", "drifted-record"),
        ("observed_at", "2099-12-31T00:00:00Z"),
        ("quality_status", "rejected"),
        ("source_product", "PortfolioManagerBookMembership:v2"),
        ("source_product_route", "/integration/legacy-advisor-book"),
        ("source_product_consumers", ["lotus-manage"]),
        (
            "source_product_consumers",
            ["lotus-gateway", "lotus-manage", "lotus-gateway"],
        ),
        ("source_product_owner", "lotus-gateway"),
        ("source_product_serving_plane", "query_service"),
        ("source_product_route_family", "Operational Read"),
        ("ingestion_endpoint", "/ingest/legacy-advisor-book"),
        ("assignment_count", 2),
    ],
)
def test_validator_rejects_drifted_core_executable_seed_evidence(
    monkeypatch, tmp_path, field, drifted_value
) -> None:
    validator = _validator()
    proof_path = tmp_path / validator.CORE_SEED_VALIDATOR_RELATIVE_PATH
    proof_path.parent.mkdir(parents=True)
    proof_path.write_text("# test executable proof\n", encoding="utf-8")
    contract = _contract()
    expected_evidence = validator._required_core_seed_evidence(contract)
    evidence = dict(expected_evidence)
    evidence[field] = drifted_value
    monkeypatch.setattr(
        validator.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0], 0, stdout=json.dumps(evidence), stderr=""
        ),
    )

    errors = validator._validate_core_advisor_book_seed(tmp_path, contract)

    assert errors == [
        f"lotus-core advisor-book seed evidence.{field} must be {expected_evidence[field]}"
    ]


def test_validator_accepts_source_product_consumers_in_producer_order(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    validator = _validator()
    proof_path = tmp_path / validator.CORE_SEED_VALIDATOR_RELATIVE_PATH
    proof_path.parent.mkdir(parents=True)
    proof_path.write_text("# test executable proof\n", encoding="utf-8")
    contract = _contract()
    evidence = validator._required_core_seed_evidence(contract)
    evidence["source_product_consumers"] = ["lotus-manage", "lotus-gateway"]
    monkeypatch.setattr(
        validator.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0], 0, stdout=json.dumps(evidence), stderr=""
        ),
    )

    assert validator._validate_core_advisor_book_seed(tmp_path, contract) == []


def test_validator_rejects_drift_from_canonical_dpm_seed_identity() -> None:
    contract = _contract()
    contract["dpm_command_center"]["portfolio_manager_id"] = "PM_LOCAL_SMOKE"

    errors = _validator().validate_contract(contract, _invariants(), _seed_script())

    assert "dpm_command_center.portfolio_manager_id must be PM_SG_DPM_001" in errors


def test_validator_rejects_dpm_health_date_drift_from_canonical_valuation() -> None:
    contract = _contract()
    contract["dpm_command_center"]["command_center_as_of_date"] = "2026-05-03"

    errors = _validator().validate_contract(contract, _invariants(), _seed_script())

    assert (
        "dpm_command_center.command_center_as_of_date must match "
        "date_policy.canonical_as_of_date" in errors
    )
    assert (
        "dpm_command_center.command_center_as_of_date must match "
        "invariants.canonical_as_of_date" in errors
    )


def test_validator_rejects_dpm_health_date_invariant_drift() -> None:
    invariants = _invariants()
    invariants["canonical_as_of_date"] = "2026-05-03"

    errors = _validator().validate_contract(_contract(), invariants, _seed_script())

    assert (
        "dpm_command_center.command_center_as_of_date must match "
        "invariants.canonical_as_of_date" in errors
    )


@pytest.mark.parametrize("tenant_id", [None, "", "default", "tenant-other"])
def test_validator_rejects_campaign_tenant_outside_workbench_caller_scope(
    tenant_id: str | None,
) -> None:
    contract = _contract()
    contract["dpm_command_center"]["campaign_definition_scenario"][
        "tenant_id"
    ] = tenant_id

    errors = _validator().validate_contract(contract, _invariants(), _seed_script())

    assert (
        "campaign_definition_scenario.tenant_id must match the governed "
        "Workbench caller tenant" in errors
    )


@pytest.mark.parametrize("tenant_id", [None, "", "default", "tenant-other"])
def test_validator_rejects_workbench_caller_tenant_drift(
    tenant_id: str | None,
) -> None:
    contract = _contract()
    contract["dpm_command_center"]["workbench_caller_tenant_id"] = tenant_id

    errors = _validator().validate_contract(contract, _invariants(), _seed_script())

    assert (
        "dpm_command_center.workbench_caller_tenant_id must match the governed "
        "Workbench caller tenant" in errors
    )
    assert (
        "campaign_definition_scenario.tenant_id must match "
        "dpm_command_center.workbench_caller_tenant_id" in errors
    )


def test_validator_rejects_stale_canonical_source_ref_version() -> None:
    contract = _contract()
    source_ref = contract["dpm_command_center"]["multi_portfolio_wave_scenario"][
        "portfolios"
    ][0]["source_refs"][0]
    source_ref["source_version"] = "1.1.0"

    errors = _validator().validate_contract(contract, _invariants(), _seed_script())

    assert (
        "multi_portfolio_wave_scenario source refs must match canonical contract version"
        in errors
    )


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


def test_validator_rejects_missing_date_aligned_cash_evidence() -> None:
    seed_script = _seed_script().replace("gateway-date-aligned-cash-evidence", "")

    errors = _validator().validate_contract(_contract(), _invariants(), seed_script)

    assert (
        "Invoke-DpmCommandCenterSeed.ps1 is missing step gateway-date-aligned-cash-evidence"
        in errors
    )


def test_validator_rejects_cash_evidence_after_persistent_seed_write() -> None:
    seed_script = _seed_script().replace(
        "resolving date-aligned canonical cash evidence before persistent writes",
        "resolving cash evidence after persistent writes",
    )

    errors = _validator().validate_contract(_contract(), _invariants(), seed_script)

    assert (
        "Invoke-DpmCommandCenterSeed.ps1 must resolve date-aligned cash evidence "
        "before its first persistent seed write" in errors
    )


def test_validator_rejects_missing_health_date_identity_assertion() -> None:
    seed_script = _seed_script().replace("gateway-mandate-health-date-match", "")

    errors = _validator().validate_contract(_contract(), _invariants(), seed_script)

    assert (
        "Invoke-DpmCommandCenterSeed.ps1 must verify source-owned health identity "
        "with gateway-mandate-health-date-match" in errors
    )


def _tenant_errors(mutate) -> list[str]:
    """Validate a mutated contract, keeping only the tenant findings."""
    validator = _validator()
    contract = _contract()
    mutate(contract)
    return [
        error
        for error in validator.validate_contract(
            contract, _invariants(), _seed_script()
        )
        if "tenant" in error.lower()
    ]


def test_the_published_contract_names_its_source_owned_core_tenant() -> None:
    """The value a consumer needs must be readable without inference."""
    portfolio = _contract()["portfolio"]

    assert portfolio["source_tenant_id"] == "tenant-sg"
    assert portfolio["source_tenant_authority"]["repository"] == "lotus-core"
    assert (
        portfolio["source_tenant_authority"]["constant"]
        == "FRONT_OFFICE_PORTFOLIO_TENANT_ID"
    )


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda c: c["portfolio"].pop("source_tenant_id"), id="absent"),
        pytest.param(
            lambda c: c["portfolio"].__setitem__("source_tenant_id", "   "),
            id="blank",
        ),
        pytest.param(
            lambda c: c["portfolio"].__setitem__("source_tenant_id", 7),
            id="not-a-string",
        ),
        pytest.param(
            lambda c: c["portfolio"].__setitem__("source_tenant_id", "tenant-hk"),
            id="foreign-tenant",
        ),
    ],
)
def test_a_missing_or_wrong_source_tenant_fails_closed(mutate) -> None:
    assert _tenant_errors(mutate)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(
            lambda c: c["portfolio"].pop("source_tenant_authority"), id="absent"
        ),
        pytest.param(
            lambda c: c["portfolio"]["source_tenant_authority"].__setitem__(
                "repository", "lotus-gateway"
            ),
            id="wrong-producer",
        ),
        pytest.param(
            lambda c: c["portfolio"]["source_tenant_authority"].__setitem__("path", ""),
            id="blank-path",
        ),
        pytest.param(
            lambda c: c["portfolio"]["source_tenant_authority"].__setitem__(
                "constant", ""
            ),
            id="blank-constant",
        ),
    ],
)
def test_the_source_tenant_authority_must_be_resolvable(mutate) -> None:
    """The provenance has to be usable, because the producer check resolves it."""
    assert _tenant_errors(mutate)


def test_the_caller_tenant_cannot_stand_in_for_the_source_tenant() -> None:
    """This is the defect the field exists to prevent.

    `dpm_command_center.workbench_caller_tenant_id` is present and correct in
    this fixture, and holds the same value the source tenant should. If the
    validator let that satisfy the requirement, a consumer reading an admission
    header as provenance would look correct until a portfolio was seeded under a
    different tenant.
    """
    def drop_source_only(contract: dict) -> None:
        contract["portfolio"].pop("source_tenant_id")
        assert (
            contract["dpm_command_center"]["workbench_caller_tenant_id"] == "tenant-sg"
        )

    assert _tenant_errors(drop_source_only)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(
            lambda c: c["portfolio"].pop("tenant_identity_separation"), id="absent"
        ),
        pytest.param(
            lambda c: c["portfolio"]["tenant_identity_separation"].__setitem__(
                "source_ownership_field",
                "dpm_command_center.workbench_caller_tenant_id",
            ),
            id="collapsed-onto-caller",
        ),
        pytest.param(
            lambda c: c["portfolio"]["tenant_identity_separation"].__setitem__(
                "consumer_rule", ""
            ),
            id="no-consumer-rule",
        ),
    ],
)
def test_the_two_tenant_facts_must_stay_separately_published(mutate) -> None:
    assert _tenant_errors(mutate)


def test_the_source_tenant_is_proven_against_the_producer(tmp_path: Path) -> None:
    """Agreement with lotus-core is measured, not asserted."""
    validator = _validator()
    contract = _contract()
    authority = contract["portfolio"]["source_tenant_authority"]
    seed = tmp_path / authority["path"]
    seed.parent.mkdir(parents=True, exist_ok=True)
    seed.write_text(
        f'{authority["constant"]} = "{contract["portfolio"]["source_tenant_id"]}"'
        + chr(10),
        encoding="utf-8",
    )

    assert validator._validate_core_portfolio_source_tenant(tmp_path, contract) == []


def test_a_producer_seeding_a_different_tenant_fails_closed(tmp_path: Path) -> None:
    """The drift this contract exists to catch."""
    validator = _validator()
    contract = _contract()
    authority = contract["portfolio"]["source_tenant_authority"]
    seed = tmp_path / authority["path"]
    seed.parent.mkdir(parents=True, exist_ok=True)
    seed.write_text(f'{authority["constant"]} = "tenant-hk"' + chr(10), encoding="utf-8")

    errors = validator._validate_core_portfolio_source_tenant(tmp_path, contract)

    assert errors
    assert "tenant-hk" in errors[0]


@pytest.mark.parametrize(
    ("filename", "contents"),
    [
        pytest.param(None, None, id="authority-file-absent"),
        pytest.param(
            "seed.py", 'SOMETHING_ELSE = "tenant-sg"', id="constant-not-defined"
        ),
    ],
)
def test_an_unprovable_source_tenant_is_an_error_not_a_pass(
    tmp_path: Path, filename, contents
) -> None:
    """Absence must not read as agreement.

    A missing file or an unreadable constant produces no mismatch to report, and
    a check that only reports mismatches would return the same empty list it
    returns when the producer agrees.
    """
    validator = _validator()
    contract = _contract()
    authority = dict(contract["portfolio"]["source_tenant_authority"])
    if filename is not None:
        authority["path"] = filename
        (tmp_path / filename).write_text(contents, encoding="utf-8")
    contract["portfolio"]["source_tenant_authority"] = authority

    assert validator._validate_core_portfolio_source_tenant(tmp_path, contract)
