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
    }

    for panel_id, expected_endpoint in expected_gateway_endpoints.items():
        assert panel_by_id[panel_id]["gateway_endpoint"] == expected_endpoint

    assert panel_by_id["performance.evidence"]["required_support_state"] == "unavailable"
    assert panel_by_id["performance.evidence"]["owner_follow_up_rfc"] == "RFC-0079"
    assert panel_by_id["performance.risk.rolling"]["screenshot_policy"]["screenshot_name"] == (
        "performance-risk-live.png"
    )
    assert panel_by_id["performance.analysis.attribution"]["required_support_state"] == "partial"
    assert "supported_blank" not in panel_by_id["portfolio.summary"]["allowed_states"]
