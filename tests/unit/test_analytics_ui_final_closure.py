from __future__ import annotations

import copy
import json
from pathlib import Path

from automation.validate_analytics_ui_final_closure import validate_final_closure


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = ROOT / "context" / "contracts"
OBSERVABILITY_CONTRACT_PATH = CONTRACT_DIR / "analytics-ui-observability-contract.json"
ROLLOUT_CONTRACT_PATH = CONTRACT_DIR / "analytics-ui-observability-rollout-readiness.json"
HARDENING_REVIEW_PATH = CONTRACT_DIR / "analytics-ui-observability-hardening-review.json"
FINAL_CLOSURE_PATH = CONTRACT_DIR / "analytics-ui-observability-final-closure.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(observability: dict, rollout: dict, hardening: dict, closure: dict) -> list[str]:
    return validate_final_closure(
        observability_contract=observability,
        rollout_contract=rollout,
        hardening_review=hardening,
        final_closure=closure,
    )


def test_analytics_ui_final_closure_artifacts_are_present_and_governed() -> None:
    readme = (CONTRACT_DIR / "README.md").read_text(encoding="utf-8")
    schema = _load_json(
        CONTRACT_DIR / "analytics-ui-observability-final-closure.schema.json"
    )
    closure = _load_json(FINAL_CLOSURE_PATH)

    assert "analytics-ui-observability-final-closure.schema.json" in readme
    assert "analytics-ui-observability-final-closure.json" in readme
    assert (
        schema["properties"]["contract_id"]["const"]
        == "analytics-ui-observability-final-closure"
    )
    assert schema["properties"]["governed_by_rfc"]["const"] == "RFC-0108"
    assert closure["contract_id"] == "analytics-ui-observability-final-closure"
    assert closure["governed_by_rfc"] == "RFC-0108"
    assert closure["lifecycle_status"] == "final-closure-implemented"


def test_analytics_ui_final_closure_validator_accepts_baseline() -> None:
    assert (
        _validate(
            _load_json(OBSERVABILITY_CONTRACT_PATH),
            _load_json(ROLLOUT_CONTRACT_PATH),
            _load_json(HARDENING_REVIEW_PATH),
            _load_json(FINAL_CLOSURE_PATH),
        )
        == []
    )


def test_analytics_ui_final_closure_rejects_missing_pr_evidence() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    hardening = _load_json(HARDENING_REVIEW_PATH)
    closure = copy.deepcopy(_load_json(FINAL_CLOSURE_PATH))
    closure["merged_prs"] = [
        pr for pr in closure["merged_prs"] if pr["pr_number"] != 235
    ]

    errors = _validate(observability, rollout, hardening, closure)

    assert any("merged_prs missing PR #235" in error for error in errors)


def test_analytics_ui_final_closure_rejects_skill_review_without_decision() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    hardening = _load_json(HARDENING_REVIEW_PATH)
    closure = copy.deepcopy(_load_json(FINAL_CLOSURE_PATH))
    closure["skills_guidance_review"]["decision"] = ""

    errors = _validate(observability, rollout, hardening, closure)

    assert any("skills_guidance_review.decision" in error for error in errors)


def test_analytics_ui_final_closure_rejects_residual_scope_mismatch() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    hardening = _load_json(HARDENING_REVIEW_PATH)
    closure = copy.deepcopy(_load_json(FINAL_CLOSURE_PATH))
    closure["residual_scope"] = closure["residual_scope"][1:]

    errors = _validate(observability, rollout, hardening, closure)

    assert any("final residual scope must match" in error for error in errors)


def test_analytics_ui_final_closure_rejects_missing_clean_state_requirement() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    hardening = _load_json(HARDENING_REVIEW_PATH)
    closure = copy.deepcopy(_load_json(FINAL_CLOSURE_PATH))
    closure["clean_state_requirements"].remove("lotus-gateway main clean after merge")

    errors = _validate(observability, rollout, hardening, closure)

    assert any("lotus-gateway main clean after merge" in error for error in errors)


def test_analytics_ui_final_closure_requires_wiki_publish_evidence() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    rollout = _load_json(ROLLOUT_CONTRACT_PATH)
    hardening = _load_json(HARDENING_REVIEW_PATH)
    closure = copy.deepcopy(_load_json(FINAL_CLOSURE_PATH))
    closure["wiki_publication"]["pre_merge_drift_expected"] = False
    closure["wiki_publication"]["expected_pre_merge_drift_files"] = []

    errors = _validate(observability, rollout, hardening, closure)

    assert any("pre_merge_drift_expected" in error for error in errors)
    assert any("RFC-Index.md" in error for error in errors)
