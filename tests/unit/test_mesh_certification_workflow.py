from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "mesh-certification-gate.yml"


REQUIRED_REPOS = {
    "lotus-core": "sgajbi/lotus-core",
    "lotus-performance": "sgajbi/lotus-performance",
    "lotus-risk": "sgajbi/lotus-risk",
    "lotus-advise": "sgajbi/lotus-advise",
    "lotus-gateway": "sgajbi/lotus-gateway",
    "lotus-workbench": "sgajbi/lotus-workbench",
}


REQUIRED_PATH_FILTERS = {
    ".github/workflows/mesh-certification-gate.yml",
    "automation/mesh_certification_gate.py",
    "automation/Invoke-PlatformRepoChecks.ps1",
    "platform-contracts/domain-data-products/**",
    "platform-contracts/trust-telemetry/**",
    "generated/domain-product-catalog.json",
    "generated/domain-product-dependency-graph.json",
    "rfcs/RFC-0089-*",
    "rfcs/RFC-0090-*",
}


def _workflow() -> dict[str, Any]:
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _triggers(workflow: dict[str, Any]) -> dict[str, Any]:
    return workflow.get("on", workflow.get(True, {}))


def _steps(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    return workflow["jobs"]["mesh-certification"]["steps"]


def _step_by_name(workflow: dict[str, Any], name: str) -> dict[str, Any]:
    return next(step for step in _steps(workflow) if step.get("name") == name)


def test_mesh_certification_workflow_uses_least_privilege_triggers() -> None:
    workflow = _workflow()
    triggers = _triggers(workflow)

    assert workflow["permissions"] == {"contents": "read"}
    assert set(triggers["pull_request"]["branches"]) == {"main"}
    assert set(triggers["pull_request"]["paths"]) == REQUIRED_PATH_FILTERS
    assert "pull_request_target" not in triggers


def test_mesh_certification_workflow_exposes_explicit_branch_overrides() -> None:
    workflow = _workflow()
    inputs = _triggers(workflow)["workflow_dispatch"]["inputs"]

    assert set(inputs) == {
        "lotus_core_ref",
        "lotus_performance_ref",
        "lotus_risk_ref",
        "lotus_advise_ref",
        "lotus_gateway_ref",
        "lotus_workbench_ref",
    }
    for input_contract in inputs.values():
        assert input_contract["required"] is False
        assert input_contract["type"] == "string"
        assert "Empty means main." in input_contract["description"]


def test_mesh_certification_workflow_checks_out_expected_sibling_layout() -> None:
    workflow = _workflow()
    steps = _steps(workflow)
    platform_checkout = _step_by_name(workflow, "Checkout lotus-platform")

    assert platform_checkout["uses"] == "actions/checkout@v6"
    assert platform_checkout["with"]["path"] == "lotus-platform"

    checkout_steps = {
        step["with"]["path"]: step
        for step in steps
        if step.get("uses") == "actions/checkout@v6" and "repository" in step.get("with", {})
    }
    assert set(checkout_steps) == set(REQUIRED_REPOS)

    for repo_path, repository in REQUIRED_REPOS.items():
        checkout = checkout_steps[repo_path]
        assert checkout["with"]["repository"] == repository
        assert checkout["with"]["path"] == repo_path
        assert checkout["with"]["ref"].endswith("|| 'main' }}")


def test_mesh_certification_workflow_calls_existing_blocking_gate_only() -> None:
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    workflow = _workflow()
    gate_step = _step_by_name(workflow, "Run blocking mesh certification")

    assert gate_step["continue-on-error"] is True
    assert gate_step["working-directory"] == "lotus-platform"
    assert "python automation/mesh_certification_gate.py" in gate_step["run"]
    assert "--mode blocking" in gate_step["run"]
    assert "--require-sibling-repos" in gate_step["run"]
    assert "missing_telemetry" not in workflow_text
    assert "gateway_publication_drift" not in workflow_text
    assert "workbench_consumption_drift" not in workflow_text


def test_mesh_certification_workflow_uploads_artifacts_and_fails_after_summary() -> None:
    workflow = _workflow()
    upload_step = _step_by_name(workflow, "Upload mesh certification artifacts")
    summary_step = _step_by_name(workflow, "Append mesh certification summary")
    fail_step = _step_by_name(workflow, "Fail when mesh certification fails")

    assert upload_step["if"] == "always()"
    assert upload_step["uses"] == "actions/upload-artifact@v5"
    assert "mesh-certification-status.json" in upload_step["with"]["path"]
    assert "mesh-certification-status.md" in upload_step["with"]["path"]
    assert "mesh-certification-issues.json" in upload_step["with"]["path"]
    assert upload_step["with"]["if-no-files-found"] == "warn"

    assert summary_step["if"] == "always()"
    assert summary_step["env"]["LOTUS_PLATFORM_REF"] == "${{ github.event.pull_request.head.sha || github.sha }}"
    assert "docs/operations/mesh-certification-gate-runbook.md" in summary_step["run"]
    assert "Certification state" in summary_step["run"]
    assert "checkout, setup, or CI infrastructure failure" in summary_step["run"]
    assert "| lotus-platform | $LOTUS_PLATFORM_REF |" in summary_step["run"]

    assert fail_step["if"] == "steps.mesh_gate.outcome == 'failure'"
    assert fail_step["run"] == "exit 1"
