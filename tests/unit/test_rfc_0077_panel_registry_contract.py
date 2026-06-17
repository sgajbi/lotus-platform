from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def test_rfc_0077_is_implementation_grade_and_includes_final_slice() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0077-workbench-panel-registry-and-evidence-contract.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "# RFC-0077: Workbench Panel Registry and Evidence Contract",
        "## Decision",
        "## Proposed Registry Artifacts",
        "context/contracts/workbench-panel-registry.json",
        "context/contracts/workbench-panel-registry.schema.json",
        "## Registry Model",
        "## State Model",
        "## Ownership and Boundary Rules",
        "### Slice 1: Registry Specification and Testable Contract",
        "### Slice 2: Workbench Validator Adoption",
        "### Slice 3: Gateway and Panel Supportability Alignment",
        "### Slice 4: Documentation, Agent Context, Skill Alignment, and Branch Hygiene",
        "## Skills, Context, and Documentation Implications",
        "## Approval Request",
        "supported_blank",
        "performance.evidence",
        "RFC-0076",
        "RFC-0079",
    ):
        assert required_item in rfc


def test_rfc_0077_defines_minimum_panel_inventory_and_governed_acceptance_rules() -> None:
    rfc = (
        ROOT / "rfcs" / "RFC-0077-workbench-panel-registry-and-evidence-contract.md"
    ).read_text(encoding="utf-8")

    for required_item in (
        "portfolio.summary",
        "portfolio.detailed",
        "performance.summary",
        "performance.analysis.contribution",
        "performance.analysis.attribution",
        "performance.advisor_brief",
        "performance.risk.snapshot",
        "performance.risk.drawdown",
        "performance.risk.concentration",
        "performance.risk.rolling",
        "performance.risk.historical_attribution",
        "performance.evidence",
        "supported blank panels fail validation",
        "partial and unavailable panels include owner and rationale",
        "new governed panel work requires registry updates",
    ):
        assert required_item in rfc


def test_rfc_0077_registry_contract_artifacts_are_present_and_governed() -> None:
    readme = (ROOT / "context" / "contracts" / "README.md").read_text(encoding="utf-8")
    checklist = (ROOT / "rfcs" / "RFC-0077-implementation-checklist.md").read_text(
        encoding="utf-8"
    )
    evidence = (ROOT / "rfcs" / "RFC-0077-slice-1-registry-spec-evidence.md").read_text(
        encoding="utf-8"
    )
    schema = _load_json("context/contracts/workbench-panel-registry.schema.json")
    registry = _load_json("context/contracts/workbench-panel-registry.json")

    assert "workbench-panel-registry.schema.json" in readme
    assert "workbench-panel-registry.json" in readme
    assert "- [x] Add `context/contracts/workbench-panel-registry.schema.json`." in checklist
    assert "- [x] Add `context/contracts/workbench-panel-registry.json`." in checklist
    assert "performance.evidence" in evidence
    assert "supported_blank" in evidence

    assert schema["properties"]["contract_id"]["const"] == "workbench-panel-registry"
    assert schema["properties"]["governed_by_rfc"]["const"] == "RFC-0077"
    panel_schema = schema["$defs"]["panelEntry"]["properties"]
    assert "workflow_panel" in panel_schema["panel_kind"]["enum"]
    assert "lotus-advise" in panel_schema["owning_service"]["enum"]
    assert "lotus-ai" in panel_schema["owning_service"]["enum"]
    assert "lotus-manage" in panel_schema["owning_service"]["enum"]

    assert registry["contract_id"] == "workbench-panel-registry"
    assert registry["contract_version"] == "1.0.0"
    assert registry["governed_by_rfc"] == "RFC-0077"
    assert registry["canonical_data_contract"] == "canonical-front-office-demo-data-contract"

    panels = registry["panels"]
    assert len(panels) >= 12
    assert len({panel["panel_id"] for panel in panels}) == len(panels)

    panel_by_id = {panel["panel_id"]: panel for panel in panels}
    expected_gateway_endpoints = {
        "portfolio.summary": "/api/v1/workbench/{portfolio_id}/overview",
        "portfolio.detailed": "/api/v1/workbench/{portfolio_id}/overview",
        "performance.summary": "/api/v1/workbench/{portfolio_id}/performance/summary",
        "performance.analysis.contribution": "/api/v1/workbench/{portfolio_id}/performance/details",
        "performance.analysis.attribution": "/api/v1/workbench/{portfolio_id}/performance/details",
        "performance.advisor_brief": "/api/v1/workbench/{portfolio_id}/performance/advisor-brief",
        "performance.risk.snapshot": "/api/v1/workbench/{portfolio_id}/risk/summary",
        "performance.risk.drawdown": "/api/v1/workbench/{portfolio_id}/risk/drawdown",
        "performance.risk.concentration": "/api/v1/workbench/{portfolio_id}/risk/concentration",
        "performance.risk.rolling": "/api/v1/workbench/{portfolio_id}/risk/rolling",
        "performance.risk.historical_attribution": "/api/v1/workbench/{portfolio_id}/risk/attribution",
        "performance.evidence": None,
        "dpm.command_center": "/api/v1/dpm/command-center",
        "dpm.outcome_review": "/api/v1/dpm/command-center/outcome-reviews",
        "dpm.wave_command_center": "/api/v1/dpm/command-center/waves",
        "dpm.portfolio_memory": "/api/v1/dpm/command-center/portfolios/{portfolio_id}/memory",
        "dpm.proof_pack": "/api/v1/dpm/command-center/proof-packs/{proof_pack_id}",
        "dpm.construction_alternatives": "/api/v1/dpm/command-center/construction/alternative-sets/generate",
        "dpm.pm_operating_quality": "/api/v1/dpm/command-center/pm-operating-quality/score-runs",
        "dpm.copilot_workspace": None,
        "proposal.memo_evidence_pack": "/api/v1/proposals/{proposal_id}/versions/{version_no}/memo",
        "advisory.advisor_cockpit": "/api/v1/advisor-cockpit/actions",
        "advisory.advisory_copilot": "/api/v1/advisory-copilot/actions",
        "advisory.bank_demo_proof": "/api/v1/advisory/bank-demo-proof/supported-claim-register",
    }

    for panel_id, expected_endpoint in expected_gateway_endpoints.items():
        assert panel_by_id[panel_id]["gateway_endpoint"] == expected_endpoint

    assert panel_by_id["performance.evidence"]["required_support_state"] == "ready"
    assert "ready" in panel_by_id["performance.evidence"]["allowed_states"]
    assert panel_by_id["performance.evidence"]["owner_follow_up_rfc"] == "RFC-0079"
    assert panel_by_id["performance.risk.rolling"]["screenshot_policy"]["screenshot_name"] == (
        "performance-risk-live.png"
    )
    assert panel_by_id["performance.analysis.attribution"]["required_support_state"] == "ready"
    assert panel_by_id["performance.analysis.attribution"]["known_limitations"] == []
    assert "supported_blank" not in panel_by_id["portfolio.summary"]["allowed_states"]
    assert panel_by_id["dpm.command_center"]["owning_service"] == "lotus-manage"
    assert panel_by_id["dpm.command_center"]["required_support_state"] == "ready"
    assert panel_by_id["dpm.command_center"]["allowed_states"] == [
        "ready",
        "partial",
        "empty",
        "loading",
        "error",
    ]
    assert panel_by_id["dpm.command_center"]["screenshot_policy"]["screenshot_name"] == (
        "dpm-command-center-live.png"
    )
    assert panel_by_id["dpm.command_center"]["known_limitations"] == []
    assert panel_by_id["dpm.command_center"]["owner_follow_up_rfc"] is None
    assert panel_by_id["dpm.wave_command_center"]["owning_service"] == "lotus-manage"
    assert panel_by_id["dpm.wave_command_center"]["required_support_state"] == "ready"
    assert panel_by_id["dpm.wave_command_center"]["screenshot_policy"]["screenshot_name"] == (
        "dpm-wave-command-center-live.png"
    )
    assert "external OMS execution" in panel_by_id["dpm.wave_command_center"]["known_limitations"][0]
    assert panel_by_id["dpm.portfolio_memory"]["owning_service"] == "lotus-manage"
    assert panel_by_id["dpm.portfolio_memory"]["required_support_state"] == "ready"
    assert (
        "READY, PARTIAL, or BLOCKED"
        in panel_by_id["dpm.portfolio_memory"]["validation_rules"]["ready"][1]
    )
    assert panel_by_id["dpm.portfolio_memory"]["screenshot_policy"]["screenshot_name"] == (
        "dpm-portfolio-memory-live.png"
    )
    assert "local timeline reconstruction" in panel_by_id["dpm.portfolio_memory"][
        "known_limitations"
    ][0]
    assert panel_by_id["dpm.proof_pack"]["owning_service"] == "lotus-manage"
    assert panel_by_id["dpm.proof_pack"]["required_support_state"] == "ready"
    assert panel_by_id["dpm.proof_pack"]["screenshot_policy"]["screenshot_name"] == (
        "dpm-proof-pack-live.png"
    )
    assert "hash generation" in panel_by_id["dpm.proof_pack"]["known_limitations"][0]
    assert panel_by_id["dpm.construction_alternatives"]["owning_service"] == "lotus-manage"
    assert panel_by_id["dpm.construction_alternatives"]["required_support_state"] == "ready"
    assert panel_by_id["dpm.construction_alternatives"]["screenshot_policy"]["screenshot_name"] == (
        "dpm-construction-alternatives-live.png"
    )
    assert "OMS execution" in panel_by_id["dpm.construction_alternatives"]["known_limitations"][0]
    assert panel_by_id["dpm.pm_operating_quality"]["owning_service"] == "lotus-manage"
    assert panel_by_id["dpm.pm_operating_quality"]["required_support_state"] == "ready"
    assert panel_by_id["dpm.pm_operating_quality"]["screenshot_policy"]["screenshot_name"] == (
        "dpm-pm-operating-quality-live.png"
    )
    assert "rank PMs" in panel_by_id["dpm.pm_operating_quality"]["known_limitations"][0]
    assert panel_by_id["dpm.copilot_workspace"]["owning_service"] == "lotus-ai"
    assert panel_by_id["dpm.copilot_workspace"]["required_support_state"] == "ready"
    assert panel_by_id["dpm.copilot_workspace"]["screenshot_policy"]["screenshot_name"] == (
        "dpm-copilot-workspace-live.png"
    )
    assert "store prompts" in panel_by_id["dpm.copilot_workspace"]["known_limitations"][0]
    assert panel_by_id["proposal.memo_evidence_pack"]["owning_service"] == "lotus-advise"
    assert panel_by_id["proposal.memo_evidence_pack"]["required_support_state"] == "ready"
    assert panel_by_id["proposal.memo_evidence_pack"]["allowed_states"] == [
        "ready",
        "loading",
        "empty",
        "partial",
        "unavailable",
        "error",
    ]
    assert panel_by_id["proposal.memo_evidence_pack"]["screenshot_policy"]["screenshot_name"] == (
        "proposal-memo-evidence-pack-live.png"
    )
    assert "client-ready release" in panel_by_id["proposal.memo_evidence_pack"][
        "known_limitations"
    ][0]
    assert panel_by_id["advisory.advisor_cockpit"]["owning_service"] == "lotus-advise"
    assert panel_by_id["advisory.advisor_cockpit"]["required_support_state"] == "ready"
    assert panel_by_id["advisory.advisor_cockpit"]["allowed_states"] == [
        "ready",
        "loading",
        "empty",
        "partial",
        "unavailable",
        "error",
    ]
    assert panel_by_id["advisory.advisor_cockpit"]["screenshot_policy"]["screenshot_name"] == (
        "advisory-advisor-cockpit-live.png"
    )
    assert "idempotency key" in panel_by_id["advisory.advisor_cockpit"]["validation_rules"][
        "ready"
    ][3]
    assert "OMS execution" in panel_by_id["advisory.advisor_cockpit"]["validation_rules"][
        "ready"
    ][4]
    assert panel_by_id["advisory.advisory_copilot"]["owning_service"] == "lotus-advise"
    assert panel_by_id["advisory.advisory_copilot"]["required_support_state"] == "ready"
    assert panel_by_id["advisory.advisory_copilot"]["allowed_states"] == [
        "ready",
        "loading",
        "empty",
        "partial",
        "unavailable",
        "error",
    ]
    assert panel_by_id["advisory.advisory_copilot"]["screenshot_policy"]["screenshot_name"] == (
        "advisory-advisory-copilot-live.png"
    )
    assert "idempotency protection" in panel_by_id["advisory.advisory_copilot"][
        "validation_rules"
    ]["ready"][3]
    assert "client-ready publication" in panel_by_id["advisory.advisory_copilot"][
        "known_limitations"
    ][0]
    assert panel_by_id["advisory.bank_demo_proof"]["owning_service"] == "lotus-advise"
    assert panel_by_id["advisory.bank_demo_proof"]["required_support_state"] == "ready"
    assert panel_by_id["advisory.bank_demo_proof"]["allowed_states"] == [
        "ready",
        "loading",
        "partial",
        "unavailable",
        "error",
    ]
    assert panel_by_id["advisory.bank_demo_proof"]["screenshot_policy"]["screenshot_name"] == (
        "advisory-bank-demo-proof-live.png"
    )
    assert "supported-claim register" in panel_by_id["advisory.bank_demo_proof"][
        "validation_rules"
    ]["ready"][1]
    assert "client-ready approval" in panel_by_id["advisory.bank_demo_proof"][
        "validation_rules"
    ]["ready"][3]
    assert "proof-pack capture" in panel_by_id["advisory.bank_demo_proof"][
        "known_limitations"
    ][0]
