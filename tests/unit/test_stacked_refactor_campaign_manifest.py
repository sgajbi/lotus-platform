from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from automation.validate_stacked_refactor_campaign_manifest import (
    validate_stacked_refactor_campaign_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_PATH = (
    ROOT
    / "platform-contracts"
    / "agent-engineering"
    / "examples"
    / "stacked-refactor-campaign-valid.json"
)
SCHEMA_PATH = (
    ROOT
    / "platform-contracts"
    / "agent-engineering"
    / "stacked-refactor-campaign-manifest.schema.json"
)


def _manifest() -> dict:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def test_stacked_refactor_campaign_contract_files_are_registered() -> None:
    readme = (ROOT / "platform-contracts/agent-engineering/README.md").read_text(
        encoding="utf-8"
    )
    playbook = (ROOT / "context/playbooks/PR-LOOP-PLAYBOOK.md").read_text(
        encoding="utf-8"
    )
    task_ledger_playbook = (
        ROOT / "context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md"
    ).read_text(encoding="utf-8")
    premerge_skill = (
        ROOT / "codex/skills/lotus-pr-premerge-gate/SKILL.md"
    ).read_text(encoding="utf-8")

    assert SCHEMA_PATH.exists()
    assert EXAMPLE_PATH.exists()
    for content in (readme, playbook, task_ledger_playbook, premerge_skill):
        assert "stacked-refactor-campaign" in content


def test_stacked_refactor_campaign_manifest_accepts_ordered_stack() -> None:
    assert validate_stacked_refactor_campaign_manifest(_manifest()) == []


def test_stacked_refactor_campaign_manifest_rejects_stale_predecessor_sha() -> None:
    manifest = _manifest()
    manifest["tranches"][1]["required_predecessor_main_sha"] = (
        "9999999999999999999999999999999999999999"
    )

    errors = validate_stacked_refactor_campaign_manifest(manifest)

    assert any("required_predecessor_main_sha must equal previous" in error for error in errors)


def test_stacked_refactor_campaign_manifest_rejects_stale_base_sha() -> None:
    manifest = _manifest()
    manifest["tranches"][2]["base_sha"] = "9999999999999999999999999999999999999999"

    errors = validate_stacked_refactor_campaign_manifest(manifest)

    assert any("base_sha must equal predecessor main SHA" in error for error in errors)


def test_stacked_refactor_campaign_manifest_rejects_premature_issue_closure() -> None:
    manifest = _manifest()
    manifest["tranches"][0]["issue_closure_decision"] = (
        "close_after_final_validated_main"
    )

    errors = validate_stacked_refactor_campaign_manifest(manifest)

    assert any("non-final tranches must keep campaign issues open" in error for error in errors)


def test_stacked_refactor_campaign_manifest_rejects_final_closure_sha_mismatch() -> None:
    manifest = _manifest()
    manifest["final_aggregate_closure"]["exact_main_sha"] = (
        "9999999999999999999999999999999999999999"
    )

    errors = validate_stacked_refactor_campaign_manifest(manifest)

    assert any("exact_main_sha must equal final main SHA" in error for error in errors)


def test_stacked_refactor_campaign_manifest_rejects_open_campaign_with_closed_issues() -> None:
    manifest = _manifest()
    manifest["final_aggregate_closure"]["status"] = "open"
    manifest["final_aggregate_closure"]["campaign_issues_closed"] = True

    errors = validate_stacked_refactor_campaign_manifest(manifest)

    assert any("open campaign must not mark campaign_issues_closed true" in error for error in errors)


def test_stacked_refactor_campaign_manifest_rejects_missing_tranche_decision() -> None:
    manifest = _manifest()
    manifest["tranches"][1].pop("tranche_decision")

    errors = validate_stacked_refactor_campaign_manifest(manifest)

    assert any("Record an explicit tranche/split decision" in error for error in errors)


def test_stacked_refactor_campaign_manifest_rejects_schema_drift() -> None:
    manifest = _manifest()
    manifest["unsupported_field"] = "must not pass"
    manifest["tranches"][0]["local_evidence"] = [{"not": "a string"}]

    errors = validate_stacked_refactor_campaign_manifest(manifest)

    assert any("schema $: Additional properties are not allowed" in error for error in errors)
    assert any("schema $.tranches.0.local_evidence.0" in error for error in errors)


def test_stacked_refactor_campaign_cli_and_agent_contract_validator_pass() -> None:
    manifest_result = subprocess.run(
        [
            sys.executable,
            "automation/validate_stacked_refactor_campaign_manifest.py",
            "--manifest",
            str(EXAMPLE_PATH),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert manifest_result.returncode == 0, manifest_result.stdout + manifest_result.stderr

    aggregate_result = subprocess.run(
        [sys.executable, "automation/validate_agent_engineering_contracts.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert aggregate_result.returncode == 0, aggregate_result.stdout + aggregate_result.stderr


def test_stacked_refactor_campaign_manifest_does_not_mutate_fixture() -> None:
    manifest = _manifest()
    original = copy.deepcopy(manifest)

    validate_stacked_refactor_campaign_manifest(manifest)

    assert manifest == original
