from __future__ import annotations

import copy
import json
from pathlib import Path

from automation.validate_analytics_ui_rollout_readiness import (
    validate_rollout_readiness,
)


ROOT = Path(__file__).resolve().parents[2]
OBSERVABILITY_CONTRACT_PATH = (
    ROOT / "context" / "contracts" / "analytics-ui-observability-contract.json"
)
ROLLOUT_CONTRACT_PATH = (
    ROOT
    / "context"
    / "contracts"
    / "analytics-ui-observability-rollout-readiness.json"
)
PANEL_REGISTRY_PATH = ROOT / "context" / "contracts" / "workbench-panel-registry.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(observability_contract: dict, rollout_contract: dict) -> list[str]:
    return validate_rollout_readiness(
        observability_contract=observability_contract,
        rollout_contract=rollout_contract,
        panel_registry=_load_json(PANEL_REGISTRY_PATH),
    )


def test_analytics_ui_rollout_readiness_artifacts_are_present_and_governed() -> None:
    readme = (ROOT / "context" / "contracts" / "README.md").read_text(encoding="utf-8")
    schema = _load_json(
        ROOT
        / "context"
        / "contracts"
        / "analytics-ui-observability-rollout-readiness.schema.json"
    )
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)

    assert "analytics-ui-observability-rollout-readiness.schema.json" in readme
    assert "analytics-ui-observability-rollout-readiness.json" in readme
    assert (
        schema["properties"]["contract_id"]["const"]
        == "analytics-ui-observability-rollout-readiness"
    )
    assert schema["properties"]["governed_by_rfc"]["const"] == "RFC-0108"
    assert rollout["contract_id"] == "analytics-ui-observability-rollout-readiness"
    assert rollout["governed_by_rfc"] == "RFC-0108"
    assert rollout["lifecycle_status"] == "slice-9-rollout-readiness-implemented"


def test_analytics_ui_rollout_readiness_validator_accepts_baseline() -> None:
    assert (
        _validate(
            _load_json(OBSERVABILITY_CONTRACT_PATH),
            _load_json(ROLLOUT_CONTRACT_PATH),
        )
        == []
    )


def test_analytics_ui_rollout_readiness_records_route_and_panel_scope() -> None:
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    certified_groups = {
        group["route"]: group for group in rollout["certified_route_groups"]
    }

    assert set(certified_groups) == {
        "/portfolio?portfolioId={portfolio_id}",
        "/portfolio?portfolioId={portfolio_id}&tab=detailed",
        "/performance?portfolioId={portfolio_id}",
        "/performance?portfolioId={portfolio_id}&mode=analysis",
        "/performance?portfolioId={portfolio_id}&mode=advisor",
        "/performance?portfolioId={portfolio_id}&mode=risk",
        "/performance?portfolioId={portfolio_id}&mode=evidence",
        "/workbench/{portfolio_id}",
        "/workbench/{portfolio_id}?mode=construction",
        "/workbench/{portfolio_id}?mode=quality",
        "/workbench/{portfolio_id}?mode=copilot",
        "/proposals/{proposalId}",
        "/recommendations?portfolioId={portfolio_id}&mode=cockpit",
        "/recommendations?portfolioId={portfolio_id}&mode=proof",
    }
    assert certified_groups[
        "/performance?portfolioId={portfolio_id}&mode=evidence"
    ]["certification_status"] == "certified_partial"
    assert "performance.evidence" in certified_groups[
        "/performance?portfolioId={portfolio_id}&mode=evidence"
    ]["panel_ids"]
    assert certified_groups["/workbench/{portfolio_id}"][
        "certification_status"
    ] == "certified"
    assert "dpm.outcome_review" in certified_groups["/workbench/{portfolio_id}"][
        "panel_ids"
    ]
    assert "dpm.proof_pack" in certified_groups["/workbench/{portfolio_id}"][
        "panel_ids"
    ]
    assert "dpm.wave_command_center" in certified_groups["/workbench/{portfolio_id}"][
        "panel_ids"
    ]
    assert "dpm.construction_alternatives" in certified_groups[
        "/workbench/{portfolio_id}?mode=construction"
    ][
        "panel_ids"
    ]
    assert "dpm.pm_operating_quality" in certified_groups[
        "/workbench/{portfolio_id}?mode=quality"
    ][
        "panel_ids"
    ]
    assert "dpm.copilot_workspace" in certified_groups[
        "/workbench/{portfolio_id}?mode=copilot"
    ][
        "panel_ids"
    ]
    assert "proposal.narrative_posture" in certified_groups["/proposals/{proposalId}"][
        "panel_ids"
    ]
    assert "proposal.memo_evidence_pack" in certified_groups["/proposals/{proposalId}"][
        "panel_ids"
    ]
    assert "client-ready release" in certified_groups["/proposals/{proposalId}"][
        "evidence_basis"
    ]
    assert "advisory.advisor_cockpit" in certified_groups[
        "/recommendations?portfolioId={portfolio_id}&mode=cockpit"
    ]["panel_ids"]
    assert "OMS execution" in certified_groups[
        "/recommendations?portfolioId={portfolio_id}&mode=cockpit"
    ]["evidence_basis"]
    assert "/recommendations?portfolioId={portfolio_id}&mode=copilot" not in certified_groups
    assert "advisory.bank_demo_proof" in certified_groups[
        "/recommendations?portfolioId={portfolio_id}&mode=proof"
    ]["panel_ids"]
    assert "client-publication boundary" in certified_groups[
        "/recommendations?portfolioId={portfolio_id}&mode=proof"
    ]["evidence_basis"]


def test_analytics_ui_rollout_readiness_requires_known_panel_ids() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = copy.deepcopy(_load_json(ROLLOUT_CONTRACT_PATH))
    rollout["certified_route_groups"][0]["panel_ids"].append("unknown.panel")

    errors = _validate(observability, rollout)

    assert any("unknown panel_id unknown.panel" in error for error in errors)


def test_analytics_ui_rollout_readiness_requires_validator_proof_cases() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = copy.deepcopy(_load_json(ROLLOUT_CONTRACT_PATH))
    rollout["validator_proof_cases"] = [
        case
        for case in rollout["validator_proof_cases"]
        if case["proof_type"] != "forbidden-label"
    ]

    errors = _validate(observability, rollout)

    assert any("forbidden-label proof" in error for error in errors)


def test_analytics_ui_rollout_readiness_rejects_residual_status_drift() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = copy.deepcopy(_load_json(ROLLOUT_CONTRACT_PATH))
    rollout["residual_scope"][0]["status"] = "implemented"

    errors = _validate(observability, rollout)

    assert any("residual status must remain planned" in error for error in errors)
