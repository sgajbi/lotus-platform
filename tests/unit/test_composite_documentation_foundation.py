"""Independent negative document contracts; no financial runtime claims."""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from automation import validate_composite_documentation_foundation as guard

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / guard.DOCS


@pytest.fixture
def publication():
    manifest = guard.read_json(DOCS / "source-manifest.v1.json")
    primary = (DOCS / "requirements.md").read_text(encoding="utf-8")
    requirements, baseline = guard.validate_publication(ROOT, manifest, primary)
    fixtures = guard.read_json(DOCS / "source/05_composite_numerical_oracles.json")["fixtures"]
    return manifest, primary, requirements, baseline, fixtures


@pytest.fixture
def ledger():
    return copy.deepcopy(guard.read_json(DOCS / "implementation-ledger.v1.json"))


def validate(ledger, publication):
    _, _, requirements, baseline, fixtures = publication
    immutable_target = (DOCS / "source/03_lotus_composite_implementation_requirements.txt").read_text(encoding="utf-8")
    guard.validate_ledger(ledger, requirements, baseline, fixtures, immutable_target)


def planned_admission():
    return {
        "owner_repository": "lotus-report",
        "owning_issue": "https://github.com/sgajbi/lotus-report/issues/417",
        "features": ["feature/composite-performance"],
        "requirement_ids": ["CMP-RPT-001"],
        "state": "PLANNED",
        "dependencies": ["https://github.com/sgajbi/lotus-performance/issues/540"],
        "source_observation": {
            "evidence_class": "COMMITTED_SOURCE_OBSERVATION", "repository": "lotus-report",
            "commit": "f62053d91a3a44d3c7dcacf14982ffce870febb4",
            "path": "src/app/report_ordering_catalogue/definitions.py",
            "scope": "Catalogue observation only; composite review remains planned.",
        },
        "scope": "First pinned composite-review Excel family; no financial recalculation.",
        "evaluation_plan": {
            "repository": "lotus-report", "state": "PLANNED", "actual_test_ref": None,
            "independent_cases": ["Parse workbook cells against accepted producer facts.",
                                  "Reject missing member/month and cross-tenant retrieval."],
        },
        "documentation_plan": {"internal": "Dataset and cell-lineage lifecycle dictionary.",
                               "external": "API tutorial and unavailable-state workbook legend."},
        "next_action": "Owner review current source and dependencies before a bounded implementation.",
    }


@pytest.mark.parametrize("features", [
    ["feature/composite-performance"],
    ["feature/core-banking-integration", "feature/composite-performance"],
])
def test_planned_single_and_shared_feature_admission_passes(ledger, publication, features):
    admission = planned_admission()
    admission["features"] = features
    ledger["delivery_admissions"] = [admission]
    validate(ledger, publication)
    assert {row["implementation_state"] for row in ledger["requirements"]} == {"NOT_ASSESSED"}


def test_unselected_foundation_requires_no_delivery_fields(ledger, publication):
    ledger.pop("delivery_admissions", None)
    validate(ledger, publication)


@pytest.mark.parametrize("field,value", [
    ("owner_repository", "lotus-platform"), ("owner_repository", ""),
    ("owning_issue", "https://github.com/sgajbi/lotus-platform/issues/923"),
    ("owning_issue", "https://github.com/sgajbi/lotus-report/issues/398"),
    ("features", []), ("features", ["feature/unknown"]),
    ("features", ["feature/core-banking-integration"]),
    ("features", ["feature/composite-performance", "feature/composite-performance"]),
    ("requirement_ids", []), ("requirement_ids", ["CMP-UNKNOWN-001"]),
    ("requirement_ids", ["CMP-RPT-001", "CMP-RPT-001"]),
    ("dependencies", None), ("dependencies", ["https://github.com/sgajbi/lotus-report/issues/417"]),
    ("dependencies", ["https://github.com/sgajbi/lotus-platform/issues/923"]),
    ("dependencies", ["not-an-issue"]),
    ("scope", ""), ("next_action", ""),
    ("state", "VERIFIED_IN_TARGET_ENVIRONMENT"),
    ("source_observation", {}), ("evaluation_plan", {}), ("documentation_plan", {}),
])
def test_invalid_planned_delivery_admission_fails(ledger, publication, field, value):
    admission = planned_admission()
    admission[field] = value
    ledger["delivery_admissions"] = [admission]
    with pytest.raises(guard.FoundationError, match="admission:"):
        validate(ledger, publication)


@pytest.mark.parametrize("field", list(planned_admission()))
def test_delivery_admission_required_fields_fail_closed(ledger, publication, field):
    admission = planned_admission()
    del admission[field]
    ledger["delivery_admissions"] = [admission]
    with pytest.raises(guard.FoundationError, match="admission:"):
        validate(ledger, publication)


@pytest.mark.parametrize("section,field,value", [
    ("source_observation", "evidence_class", "TARGET_ENVIRONMENT_ACCEPTANCE"),
    ("source_observation", "repository", "lotus-core"),
    ("source_observation", "commit", "main"),
    ("source_observation", "path", "../outside.md"),
    ("source_observation", "scope", ""),
    ("evaluation_plan", "state", "PASS"),
    ("evaluation_plan", "repository", "lotus-platform"),
    ("evaluation_plan", "actual_test_ref", "tests/unit/unrelated.py"),
    ("evaluation_plan", "independent_cases", []),
    ("evaluation_plan", "independent_cases", [""]),
    ("documentation_plan", "internal", ""),
    ("documentation_plan", "external", ""),
])
def test_plan_cannot_masquerade_as_assessed_or_executable_evidence(
    ledger, publication, section, field, value,
):
    admission = planned_admission()
    admission[section][field] = value
    ledger["delivery_admissions"] = [admission]
    with pytest.raises(guard.FoundationError, match="admission:"):
        validate(ledger, publication)


def test_duplicate_requirement_ownership_fails(ledger, publication):
    admission = planned_admission()
    ledger["delivery_admissions"] = [admission, copy.deepcopy(admission)]
    with pytest.raises(guard.FoundationError, match="admission:"):
        validate(ledger, publication)


def test_conflicting_issues_cannot_own_the_same_requirement(ledger, publication):
    original = planned_admission()
    conflicting = copy.deepcopy(original)
    conflicting["owning_issue"] = "https://github.com/sgajbi/lotus-report/issues/418"
    ledger["delivery_admissions"] = [original, conflicting]
    with pytest.raises(guard.FoundationError, match="admission:conflicting-ownership"):
        validate(ledger, publication)


def test_one_issue_can_own_multiple_known_requirements(ledger, publication):
    admission = planned_admission()
    admission["requirement_ids"].append("CMP-RPT-002")
    ledger["delivery_admissions"] = [admission]
    validate(ledger, publication)


@pytest.mark.parametrize("case,expected_exit", [
    ("valid", 0), ("no-prerequisite", 0), ("bad-owner", 1),
    ("missing-dependencies", 1), ("non-list-dependencies", 1),
    ("malformed-dependency", 1), ("duplicate-dependency", 1),
    ("self-dependency", 1), ("parent-dependency", 1),
])
def test_real_admission_cli_dependency_and_ownership_contract(tmp_path, ledger, case, expected_exit):
    for directory in (
        guard.DOCS, "rfcs", "wiki", "docs/standards",
        "platform-contracts/domain-data-products", "platform-contracts/domain-vocabulary",
        "codex/skills/lotus-app-issue-discovery",
    ):
        shutil.copytree(ROOT / directory, tmp_path / directory)
    admission = planned_admission()
    if case == "bad-owner":
        admission["owning_issue"] = ledger["programme_issue"]
    elif case == "no-prerequisite":
        admission["dependencies"] = []
    elif case == "missing-dependencies":
        del admission["dependencies"]
    elif case == "non-list-dependencies":
        admission["dependencies"] = admission["dependencies"][0]
    elif case == "malformed-dependency":
        admission["dependencies"] = ["not-an-issue"]
    elif case == "duplicate-dependency":
        admission["dependencies"] *= 2
    elif case == "self-dependency":
        admission["dependencies"] = [admission["owning_issue"]]
    elif case == "parent-dependency":
        admission["dependencies"] = [ledger["programme_issue"]]
    ledger["delivery_admissions"] = [admission]
    (tmp_path / guard.DOCS / "implementation-ledger.v1.json").write_text(
        json.dumps(ledger), encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, str(ROOT / "automation/validate_composite_documentation_foundation.py"),
         "--root", str(tmp_path)], capture_output=True, text=True, check=False,
    )
    assert result.returncode == expected_exit, result.stdout + result.stderr
    if expected_exit:
        assert "admission:" in result.stdout


def test_complete_real_foundation_passes():
    guard.validate_foundation(ROOT)


@pytest.mark.parametrize("catalogue", [
    "requirements", "source_crosswalk", "analytics", "reports", "scenarios",
    "source_decisions", "institutional_decisions", "service_objectives",
    "workload_profiles", "examples",
])
def test_missing_inventory_entry_fails(ledger, publication, catalogue):
    ledger[catalogue].pop()
    with pytest.raises(guard.FoundationError, match="inventory"):
        validate(ledger, publication)


@pytest.mark.parametrize("catalogue", ["requirements", "source_crosswalk", "analytics", "scenarios", "examples"])
def test_duplicate_inventory_entry_fails(ledger, publication, catalogue):
    ledger[catalogue].append(copy.deepcopy(ledger[catalogue][0]))
    with pytest.raises(guard.FoundationError, match="inventory"):
        validate(ledger, publication)


@pytest.mark.parametrize("catalogue", [
    "analytics", "reports", "scenarios", "institutional_decisions", "service_objectives",
])
def test_catalogue_cannot_promote_without_governed_evidence(ledger, publication, catalogue):
    ledger[catalogue][0]["state"] = "VERIFIED_IN_TARGET_ENVIRONMENT"
    expected_error = "decision:approval-boundary" if catalogue == "institutional_decisions" else "catalogue:state"
    with pytest.raises(guard.FoundationError, match=expected_error):
        validate(ledger, publication)


@pytest.mark.parametrize("catalogue", [
    "analytics", "reports", "scenarios", "institutional_decisions", "service_objectives",
])
@pytest.mark.parametrize("mutation", ["different_existing_source", "different_definition_line"])
def test_catalogue_requires_its_exact_immutable_definition(ledger, publication, catalogue, mutation):
    row = ledger[catalogue][0]
    if mutation == "different_existing_source":
        row["source_ref"] = "source/01_composite_requirements_source_baseline.txt"
    else:
        row["source_line"] = ledger[catalogue][1]["source_line"]
    with pytest.raises(guard.FoundationError, match="catalogue:source"):
        validate(ledger, publication)


@pytest.mark.parametrize("catalogue,expected_state", [
    ("analytics", "PLANNED"), ("reports", "PLANNED"), ("scenarios", "PLANNED"),
    ("institutional_decisions", "UNRESOLVED"), ("service_objectives", "PLANNED"),
])
def test_untampered_catalogue_retains_category_state(ledger, publication, catalogue, expected_state):
    assert {row["state"] for row in ledger[catalogue]} == {expected_state}
    validate(ledger, publication)


@pytest.mark.parametrize("catalogue", [
    "analytics", "reports", "scenarios", "institutional_decisions", "service_objectives",
])
def test_catalogue_cannot_redirect_to_unrelated_existing_document_section(ledger, publication, catalogue):
    ledger[catalogue][0]["document_ref"] = "requirements.md#1-product-outcomes-and-invariants"
    with pytest.raises(guard.FoundationError, match="catalogue:document-anchor"):
        validate(ledger, publication)


def test_family_mapping_cannot_replace_individual_requirement_ids(ledger, publication):
    ledger["source_crosswalk"][0]["target_ids"] = ["CMP-CAT"]
    with pytest.raises(guard.FoundationError, match="crosswalk:exact-targets"):
        validate(ledger, publication)


def test_reverse_crosswalk_must_match_source_rows(ledger, publication):
    ledger["requirements"][0]["origin"]["baseline_ids"] = []
    with pytest.raises(guard.FoundationError, match="origin:crosswalk"):
        validate(ledger, publication)


def test_source_line_and_commit_provenance_cannot_be_guessed(ledger, publication):
    ledger["requirements"][0]["origin"]["source_line"] += 1
    with pytest.raises(guard.FoundationError, match="origin:identity"):
        validate(ledger, publication)


@pytest.mark.parametrize("state", [
    "PARTIAL", "MISSING", "IMPLEMENTED_NOT_VERIFIED", "VERIFIED_IN_TEST",
    "VERIFIED_IN_TARGET_ENVIRONMENT", "BLOCKED_ON_APPROVED_POLICY_OR_SOURCE",
])
def test_status_promotion_without_owner_assessment_fails(ledger, publication, state):
    ledger["requirements"][0]["implementation_state"] = state
    with pytest.raises(guard.FoundationError, match="state:assessment-required"):
        validate(ledger, publication)


def assessment():
    # Synthetic metadata solely to exercise the guard schema, never published evidence.
    return {
        "evidence_class": "OWNER_SOURCE_ASSESSMENT", "repository": "lotus-performance",
        "commit": "a" * 40, "path": "tests/unit/example.py", "scope": "synthetic schema test",
        "result": "PASS", "run_ref": "https://github.com/sgajbi/lotus-performance/issues/1",
    }


def test_valid_scoped_source_assessment_can_record_partial_without_runtime_claim(ledger, publication):
    row = ledger["requirements"][0]
    row["implementation_state"] = "PARTIAL"
    row["evidence"]["assessment"] = assessment()
    validate(ledger, publication)


def test_specification_fixture_is_not_executable_evidence(ledger, publication):
    row = ledger["requirements"][0]
    row["implementation_state"] = "VERIFIED_IN_TEST"
    row["evidence"]["assessment"] = assessment()
    row["evidence"]["unit"] = [{**assessment(), "evidence_class": "SPECIFICATION_ORACLE"}]
    with pytest.raises(guard.FoundationError, match="evidence:class"):
        validate(ledger, publication)


def test_test_verified_requires_unit_and_integration_receipts(ledger, publication):
    row = ledger["requirements"][0]
    row["implementation_state"] = "VERIFIED_IN_TEST"
    row["evidence"]["assessment"] = assessment()
    with pytest.raises(guard.FoundationError, match="state:executable-evidence"):
        validate(ledger, publication)


def test_environment_verified_requires_distinct_target_environment_receipt(ledger, publication):
    row = ledger["requirements"][0]
    row["implementation_state"] = "VERIFIED_IN_TARGET_ENVIRONMENT"
    row["evidence"]["assessment"] = assessment()
    for key, cls in [("unit", "UNIT_TEST"), ("integration", "INTEGRATION_TEST")]:
        row["evidence"][key] = [{**assessment(), "evidence_class": cls, "actual_test_ref": "synthetic_test"}]
    with pytest.raises(guard.FoundationError, match="state:environment-evidence"):
        validate(ledger, publication)


def test_foreign_or_unqualified_issue_reference_fails(ledger, publication):
    ledger["requirements"][0]["related_issues"] = ["#608"]
    with pytest.raises(guard.FoundationError, match="requirement:issue"):
        validate(ledger, publication)


@pytest.mark.parametrize("field,value", [
    ("executed", True), ("evidence_class", "UNIT_TEST"), ("state", "VERIFIED_IN_TEST"),
    ("current_api_ref", "/invented/composite"), ("actual_test_ref", "copied_literal"),
])
def test_planned_oracle_cannot_masquerade_as_runtime_proof(ledger, publication, field, value):
    ledger["examples"][0][field] = value
    with pytest.raises(guard.FoundationError, match="example:(proof|runtime)-boundary"):
        validate(ledger, publication)


def test_missing_month_oracle_cannot_bind_to_survivor_chain_scenario(ledger, publication):
    ledger["examples"][-1]["scenario_ids"] = ["AT-044"]
    with pytest.raises(guard.FoundationError, match="example:scenario"):
        validate(ledger, publication)


def test_logical_requirement_cannot_claim_supported_api(ledger, publication):
    ledger["requirements"][0]["contract_api"]["current_api_ref"] = "/invented/route"
    with pytest.raises(guard.FoundationError, match="api:logical-boundary"):
        validate(ledger, publication)


def test_unknown_decision_cannot_be_silently_approved(ledger, publication):
    ledger["institutional_decisions"][0]["state"] = "APPROVED"
    with pytest.raises(guard.FoundationError, match="decision:approval-boundary"):
        validate(ledger, publication)


def test_workload_profile_is_target_not_capacity_certificate(ledger, publication):
    ledger["workload_profiles"][0]["state"] = "VERIFIED"
    with pytest.raises(guard.FoundationError, match="profiles:claim"):
        validate(ledger, publication)


def test_formula_change_fails_even_when_every_id_is_retained(publication):
    manifest, primary, *_ = publication
    altered = primary.replace("R_M = sum_i(w_i,M * r_i,M)", "R_M = mean_i(r_i,M)")
    assert altered != primary
    with pytest.raises(guard.FoundationError, match="publication:semantic-drift"):
        guard.validate_publication(ROOT, manifest, altered)


def test_unauthorized_editorial_substitution_cannot_hide_formula_change(publication):
    manifest, primary, *_ = publication
    manifest = copy.deepcopy(manifest)
    manifest["editorial_substitutions"].append({"from": "sum_i", "to": "mean_i"})
    with pytest.raises(guard.FoundationError, match="publication:undeclared-edit"):
        guard.validate_publication(ROOT, manifest, primary)


def test_withheld_content_cannot_enter_public_manifest(publication):
    manifest, primary, *_ = publication
    manifest = copy.deepcopy(manifest)
    manifest["inputs"][1]["publication_status"] = "PUBLISHED_IMMUTABLE_ARCHIVE"
    with pytest.raises(guard.FoundationError, match="manifest:withheld-boundary"):
        guard.validate_publication(ROOT, manifest, primary)


def test_archive_tampering_is_detected_before_content_is_used(tmp_path, publication):
    manifest, primary, *_ = publication
    shutil.copytree(DOCS / "source", tmp_path / guard.DOCS / "source")
    archive = tmp_path / guard.DOCS / manifest["inputs"][0]["archive_path"]
    archive.write_bytes(archive.read_bytes() + b"\nchanged\n")
    with pytest.raises(guard.FoundationError, match="archive:hash"):
        guard.validate_publication(tmp_path, manifest, primary)


def test_unexpected_archival_file_fails_closed(tmp_path, publication):
    manifest, primary, *_ = publication
    shutil.copytree(DOCS / "source", tmp_path / guard.DOCS / "source")
    (tmp_path / guard.DOCS / "source/unreviewed.txt").write_text("unexpected", encoding="utf-8")
    with pytest.raises(guard.FoundationError, match="archive:file-set"):
        guard.validate_publication(tmp_path, manifest, primary)


@pytest.mark.parametrize("old,new", [
    ('"return": "0.01"', '"return": "0.04"'),
    ('"cumulative_return": null', '"cumulative_return": "0.0302"'),
    ('"flow_rule": "FAIL"', '"flow_rule": "PASS"'),
    ('"complete_months": 24', '"complete_months": true'),
])
def test_numeric_state_nullability_and_scalar_drift_in_examples_fail(publication, old, new):
    fixtures = publication[-1]
    text = (DOCS / "worked-examples.md").read_text(encoding="utf-8")
    assert old in text
    with pytest.raises(guard.FoundationError, match="worked:literal-drift"):
        guard.validate_worked_examples(text.replace(old, new, 1), fixtures)


def test_broken_local_link_and_anchor_fail(tmp_path):
    page = tmp_path / "page.md"
    page.write_text("[target](absent.md)", encoding="utf-8")
    with pytest.raises(guard.FoundationError, match="link:missing-local-target"):
        guard.validate_local_links(tmp_path, page)
    page.write_text("# Present\n[target](#absent)", encoding="utf-8")
    with pytest.raises(guard.FoundationError, match="link:missing-heading"):
        guard.validate_local_links(tmp_path, page)


def test_existing_local_heading_passes(tmp_path):
    page = tmp_path / "page.md"
    page.write_text("# Present\n[target](#present)", encoding="utf-8")
    guard.validate_local_links(tmp_path, page)


def test_cli_failure_is_nonzero_and_does_not_echo_source_data(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "automation/validate_composite_documentation_foundation.py"), "--root", str(tmp_path)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1
    assert "FileNotFoundError" in result.stdout
    assert str(tmp_path) not in result.stdout
