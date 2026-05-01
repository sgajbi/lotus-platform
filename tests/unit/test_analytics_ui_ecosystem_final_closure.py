from __future__ import annotations

import copy
import json
from pathlib import Path

from automation.validate_analytics_ui_ecosystem_final_closure import (
    validate_ecosystem_final_closure,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = ROOT / "context" / "contracts"
OBSERVABILITY_CONTRACT_PATH = CONTRACT_DIR / "analytics-ui-observability-contract.json"
ECOSYSTEM_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-ecosystem-completion.json"
)
ECOSYSTEM_PROOF_PATH = CONTRACT_DIR / "analytics-ui-observability-ecosystem-proof.json"
HARDENING_PATH = CONTRACT_DIR / "analytics-ui-observability-ecosystem-hardening.json"
FINAL_CLOSURE_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-ecosystem-final-closure.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(
    observability: dict,
    ecosystem: dict,
    proof: dict,
    hardening: dict,
    final_closure: dict,
) -> list[str]:
    return validate_ecosystem_final_closure(
        observability_contract=observability,
        ecosystem_contract=ecosystem,
        ecosystem_proof=proof,
        hardening=hardening,
        final_closure=final_closure,
    )


def test_ecosystem_final_closure_artifacts_are_present_and_governed() -> None:
    readme = (CONTRACT_DIR / "README.md").read_text(encoding="utf-8")
    schema = _load_json(
        CONTRACT_DIR / "analytics-ui-observability-ecosystem-final-closure.schema.json"
    )
    final_closure = _load_json(FINAL_CLOSURE_PATH)

    assert "analytics-ui-observability-ecosystem-final-closure.schema.json" in readme
    assert "analytics-ui-observability-ecosystem-final-closure.json" in readme
    assert (
        schema["properties"]["contract_id"]["const"]
        == "analytics-ui-observability-ecosystem-final-closure"
    )
    assert schema["properties"]["governed_by_rfc"]["const"] == "RFC-0108"
    assert (
        final_closure["lifecycle_status"]
        == "slice-18-ecosystem-final-closure-implemented"
    )


def test_ecosystem_final_closure_validator_accepts_baseline() -> None:
    assert (
        _validate(
            _load_json(OBSERVABILITY_CONTRACT_PATH),
            _load_json(ECOSYSTEM_CONTRACT_PATH),
            _load_json(ECOSYSTEM_PROOF_PATH),
            _load_json(HARDENING_PATH),
            _load_json(FINAL_CLOSURE_PATH),
        )
        == []
    )


def test_ecosystem_final_closure_preserves_core_metric_label_hardening() -> None:
    final_closure = _load_json(FINAL_CLOSURE_PATH)
    residual_text = str(final_closure["residual_scope"])

    assert "lotus-core PR #329" in residual_text
    assert "metric_labels" in residual_text
    assert "no-sensitive metric-label proof" in residual_text


def test_ecosystem_final_closure_preserves_risk_metric_label_hardening() -> None:
    final_closure = _load_json(FINAL_CLOSURE_PATH)
    residual_text = str(final_closure["residual_scope"])

    assert "lotus-risk PR #109" in residual_text
    assert "metric_labels" in residual_text
    assert "no-sensitive metric-label proof" in residual_text


def test_ecosystem_final_closure_preserves_performance_metric_label_hardening() -> None:
    final_closure = _load_json(FINAL_CLOSURE_PATH)
    residual_text = str(final_closure["residual_scope"])

    assert "lotus-performance PR #141" in residual_text
    assert "metric_labels" in residual_text
    assert "no-sensitive metric-label proof" in residual_text


def test_ecosystem_final_closure_rejects_unimplemented_slice_18_feature() -> None:
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    proof = _load_json(ECOSYSTEM_PROOF_PATH)
    hardening = _load_json(HARDENING_PATH)
    final_closure = _load_json(FINAL_CLOSURE_PATH)
    for feature in observability["supported_feature_keys"]:
        if (
            feature["feature_key"]
            == "platform.analytics.observability.ecosystem_final_closure"
        ):
            feature["status"] = "planned"

    errors = _validate(observability, ecosystem, proof, hardening, final_closure)

    assert any(
        "platform.analytics.observability.ecosystem_final_closure must be implemented"
        in error
        for error in errors
    )


def test_ecosystem_final_closure_rejects_residual_scope_drift() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    proof = _load_json(ECOSYSTEM_PROOF_PATH)
    hardening = _load_json(HARDENING_PATH)
    final_closure = copy.deepcopy(_load_json(FINAL_CLOSURE_PATH))
    final_closure["residual_scope"] = final_closure["residual_scope"][:-1]

    errors = _validate(observability, ecosystem, proof, hardening, final_closure)

    assert any(
        "final residual scope must match proof and hardening" in error
        for error in errors
    )


def test_ecosystem_final_closure_rejects_missing_wiki_publish_command() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    proof = _load_json(ECOSYSTEM_PROOF_PATH)
    hardening = _load_json(HARDENING_PATH)
    final_closure = copy.deepcopy(_load_json(FINAL_CLOSURE_PATH))
    final_closure["wiki_publication"]["publish_command"] = "manual"

    errors = _validate(observability, ecosystem, proof, hardening, final_closure)

    assert any("wiki_publication.publish_command" in error for error in errors)


def test_ecosystem_final_closure_rejects_missing_required_check() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    proof = _load_json(ECOSYSTEM_PROOF_PATH)
    hardening = _load_json(HARDENING_PATH)
    final_closure = copy.deepcopy(_load_json(FINAL_CLOSURE_PATH))
    final_closure["required_github_checks"].remove(
        "PR Merge Gate / Platform Repo Contracts"
    )

    errors = _validate(observability, ecosystem, proof, hardening, final_closure)

    assert any("required_github_checks missing" in error for error in errors)


def test_ecosystem_final_closure_rejects_open_p1_hardening_finding() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    proof = _load_json(ECOSYSTEM_PROOF_PATH)
    hardening = copy.deepcopy(_load_json(HARDENING_PATH))
    final_closure = _load_json(FINAL_CLOSURE_PATH)
    hardening["findings"].append(
        {
            "finding_id": "RFC0108-ECOSYSTEM-FINAL-CLOSURE-OPEN-P1",
            "severity": "P1",
            "status": "planned_residual",
            "summary": "test-only open finding",
            "evidence": "test-only evidence",
        }
    )

    errors = _validate(observability, ecosystem, proof, hardening, final_closure)

    assert any("open P0/P1" in error for error in errors)
