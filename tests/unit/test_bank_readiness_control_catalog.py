from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "automation" / "validate_bank_readiness_control_catalog.py"
PLANNER_PATH = (
    ROOT
    / "codex"
    / "skills"
    / "lotus-app-issue-discovery"
    / "scripts"
    / "plan_issue_discovery_campaign.py"
)
DISCOVERY_VALIDATOR_PATH = (
    ROOT
    / "codex"
    / "skills"
    / "lotus-app-issue-discovery"
    / "scripts"
    / "validate_issue_discovery_skill.py"
)
CATALOG_PATH = (
    ROOT
    / "platform-contracts"
    / "bank-readiness"
    / "bank-ready-control-catalog.v1.json"
)


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_bank_readiness_control_catalog", VALIDATOR_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def _load_planner():
    spec = importlib.util.spec_from_file_location(
        "plan_issue_discovery_campaign", PLANNER_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_planner_from_path(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "plan_issue_discovery_campaign_copy", path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_discovery_validator():
    module_name = "validate_issue_discovery_skill"
    spec = importlib.util.spec_from_file_location(module_name, DISCOVERY_VALIDATOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_canonical_bank_readiness_catalog_is_valid() -> None:
    validator = _load_validator()

    assert validator.validate_catalog_path() == []


def test_catalog_rejects_duplicate_and_missing_control_identity() -> None:
    validator = _load_validator()
    payload = _catalog()
    payload["controls"][1]["control_id"] = payload["controls"][0]["control_id"]

    errors = validator.validate_catalog(payload)

    assert any("duplicate control_id" in error for error in errors)
    assert any("expected BR-001 through BR-025" in error for error in errors)


def test_catalog_rejects_unknown_profile_reference_lens_and_empty_ci_expectations() -> (
    None
):
    validator = _load_validator()
    payload = _catalog()
    control = payload["controls"][0]
    control["applicable_profiles"] = ["unknown-profile"]
    control["external_reference_ids"] = ["UNKNOWN-REFERENCE"]
    control["issue_discovery_lenses"] = ["lens/not-governed"]
    control["ci_expectations"] = []

    errors = validator.validate_catalog(payload)

    assert any("unknown profiles" in error for error in errors)
    assert any("unknown references" in error for error in errors)
    assert any("unknown lenses" in error for error in errors)
    assert any("ci_expectations" in error for error in errors)


def test_catalog_rejects_unqualified_certification_claim() -> None:
    validator = _load_validator()
    payload = copy.deepcopy(_catalog())
    payload["controls"][0]["risk"] = "The repository is ISO 27001 certified."

    errors = validator.validate_catalog(payload)

    assert any("unsupported unqualified claim" in error for error in errors)


def test_catalog_rejects_weakened_maturity_evidence_progression() -> None:
    validator = _load_validator()
    payload = _catalog()
    payload["maturity_levels"][4]["minimum_evidence_class"] = "source_design_contract"

    errors = validator.validate_catalog(payload)

    assert any("evidence progression" in error for error in errors)


def test_catalog_preserves_local_ci_production_and_completion_layer_contract() -> None:
    payload = _catalog()

    assert len(payload["controls"]) == 25
    assert set(payload["completion_layers"]) == {
        "documented_design",
        "implementation_or_configuration",
        "positive_and_negative_verification",
        "regression_enforcement",
        "discoverable_evidence",
        "accountable_ownership",
    }
    for control in payload["controls"]:
        assert control["local_expectations"]
        assert control["ci_expectations"]
        assert control["production_expectations"]
        assert control["evidence_requirements"]
        assert control["owner_roles"]


def test_catalog_validator_is_wired_into_platform_repo_checks() -> None:
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(
        encoding="utf-8"
    )

    assert (
        "Invoke-CheckedCommand $toolingPython "
        "automation/validate_bank_readiness_control_catalog.py"
    ) in repo_checks


def test_issue_discovery_plan_selects_only_applicable_bank_readiness_controls() -> None:
    planner = _load_planner()

    plan = planner.render_plan(
        "sgajbi/lotus-core",
        "source-domain",
        limit=3,
        include_bank_readiness=True,
    )

    assert "Repository profile: `source-domain-service`" in plan
    assert "`BR-001`" in plan
    assert "`BR-009`" in plan
    assert "`BR-024`" not in plan
    assert "never infer runtime, deployment, or independent verification" in plan
    assert "do not create one issue per control row" in plan


def test_issue_discovery_planner_resolves_platform_root_from_deployed_skill_copy(
    tmp_path, monkeypatch
) -> None:
    deployed_script = (
        tmp_path
        / ".codex"
        / "skills"
        / "lotus-app-issue-discovery"
        / "scripts"
        / "plan_issue_discovery_campaign.py"
    )
    deployed_script.parent.mkdir(parents=True)
    deployed_script.write_text(
        PLANNER_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )

    project_root = tmp_path / "projects"
    idea_root = project_root / "lotus-idea"
    idea_root.mkdir(parents=True)
    catalog_path = (
        project_root
        / "lotus-platform"
        / "platform-contracts"
        / "bank-readiness"
        / "bank-ready-control-catalog.v1.json"
    )
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(
        json.dumps(
            {
                "controls": [
                    {
                        "control_id": "BR-999",
                        "applicable_profiles": ["workflow-service"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(idea_root)
    planner = _load_planner_from_path(deployed_script)

    assert planner.CONTROL_CATALOG_PATH == catalog_path.resolve()
    assert planner.load_bank_readiness_controls("workflow") == [
        {"control_id": "BR-999", "applicable_profiles": ["workflow-service"]}
    ]


def test_human_and_agent_layers_reference_but_do_not_fork_control_definitions() -> None:
    standing_contract = (
        ROOT / "platform-standards" / "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md"
    ).read_text(encoding="utf-8")
    implementation_playbook = (
        ROOT
        / "platform-standards"
        / "LOTUS_BANK_READY_ENGINEERING_IMPLEMENTATION_PLAYBOOK.md"
    ).read_text(encoding="utf-8")
    discovery_skill = (
        ROOT / "codex" / "skills" / "lotus-app-issue-discovery" / "SKILL.md"
    ).read_text(encoding="utf-8")
    routing_map = (ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md").read_text(
        encoding="utf-8"
    )

    for surface in (
        standing_contract,
        implementation_playbook,
        discovery_skill,
        routing_map,
    ):
        assert "bank-ready-control-catalog.v1.json" in surface

    assert "| `BR-001` |" not in standing_contract
    assert "| `BR-001` |" not in implementation_playbook
    assert "| `BR-001` |" not in discovery_skill
    assert "Human documents may group or reference those IDs" in implementation_playbook


def test_issue_discovery_validator_enforces_bank_readiness_routing() -> None:
    validator = _load_discovery_validator()

    assert validator.validate() == []


def test_catalog_preserves_stateful_cleanup_and_exact_identity_review_lessons() -> None:
    controls = {control["control_id"]: control for control in _catalog()["controls"]}

    assert "logical-to-physical routing identity" in " ".join(
        controls["BR-007"]["ci_expectations"]
    )
    assert "exact governed resource or work identity" in " ".join(
        controls["BR-012"]["ci_expectations"]
    )
    assert "authoritative schema relationship inventory" in " ".join(
        controls["BR-017"]["local_expectations"]
    )
    assert "newly related durable child" in " ".join(
        controls["BR-017"]["ci_expectations"]
    )

    fix_forward = (
        ROOT / "context" / "playbooks" / "FIX-FORWARD-PATTERNS.md"
    ).read_text(encoding="utf-8")
    backend_skill = (
        ROOT / "codex" / "skills" / "lotus-backend-delivery-governance" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "Stateful Cleanup And Readiness Integrity Pattern" in fix_forward
    assert "Stateful Cleanup And Readiness Integrity Pattern" in backend_skill
