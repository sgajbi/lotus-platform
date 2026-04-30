from __future__ import annotations

import copy
import json
from pathlib import Path

from automation.validate_analytics_ui_scaffold_ci_enforcement import (
    validate_scaffold_ci_enforcement,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = ROOT / "context" / "contracts"
OBSERVABILITY_CONTRACT_PATH = CONTRACT_DIR / "analytics-ui-observability-contract.json"
ECOSYSTEM_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-ecosystem-completion.json"
)
SCAFFOLD_CI_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-scaffold-ci-enforcement.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(observability: dict, ecosystem: dict, scaffold_ci: dict) -> list[str]:
    return validate_scaffold_ci_enforcement(
        observability_contract=observability,
        ecosystem_contract=ecosystem,
        scaffold_ci_contract=scaffold_ci,
    )


def test_scaffold_ci_contract_artifacts_are_present_and_governed() -> None:
    readme = (CONTRACT_DIR / "README.md").read_text(encoding="utf-8")
    schema = _load_json(
        CONTRACT_DIR / "analytics-ui-observability-scaffold-ci-enforcement.schema.json"
    )
    contract = _load_json(SCAFFOLD_CI_CONTRACT_PATH)

    assert "analytics-ui-observability-scaffold-ci-enforcement.schema.json" in readme
    assert "analytics-ui-observability-scaffold-ci-enforcement.json" in readme
    assert (
        schema["properties"]["contract_id"]["const"]
        == "analytics-ui-observability-scaffold-ci-enforcement"
    )
    assert contract["governed_by_rfc"] == "RFC-0108"
    assert contract["lifecycle_status"] == "slice-11-scaffold-ci-enforcement-implemented"


def test_scaffold_ci_validator_accepts_baseline() -> None:
    assert (
        _validate(
            _load_json(OBSERVABILITY_CONTRACT_PATH),
            _load_json(ECOSYSTEM_CONTRACT_PATH),
            _load_json(SCAFFOLD_CI_CONTRACT_PATH),
        )
        == []
    )


def test_scaffold_ci_contract_proves_backend_scaffold_defaults() -> None:
    contract = _load_json(SCAFFOLD_CI_CONTRACT_PATH)
    defaults = {entry["id"]: entry for entry in contract["backend_scaffold_defaults"]}

    assert "backend_health_metadata_metrics" in defaults
    assert "backend_no_sensitive_content_guard" in defaults
    assert "backend_makefile_ci_gates" in defaults
    assert "scripts/no_sensitive_content_guard.py" in defaults[
        "backend_no_sensitive_content_guard"
    ]["required_terms"]
    assert "supported-features-gate" in defaults["backend_makefile_ci_gates"][
        "required_terms"
    ]


def test_scaffold_ci_contract_proves_ui_surface_template_defaults() -> None:
    contract = _load_json(SCAFFOLD_CI_CONTRACT_PATH)
    defaults = {entry["id"]: entry for entry in contract["ui_surface_scaffold_defaults"]}

    assert "workbench_bounded_panel_state_template" in defaults
    assert "workbench_safe_label_and_attention_template" in defaults
    assert "LOTUS_FORBIDDEN_OBSERVABILITY_FIELDS" in defaults[
        "workbench_safe_label_and_attention_template"
    ]["required_terms"]


def test_scaffold_ci_contract_rejects_missing_scaffold_term() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    scaffold_ci = copy.deepcopy(_load_json(SCAFFOLD_CI_CONTRACT_PATH))
    scaffold_ci["backend_scaffold_defaults"][0]["required_terms"].append(
        "definitely_missing_scaffold_marker"
    )

    errors = _validate(observability, ecosystem, scaffold_ci)

    assert any("definitely_missing_scaffold_marker" in error for error in errors)


def test_scaffold_ci_contract_rejects_missing_validator_wiring() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    scaffold_ci = copy.deepcopy(_load_json(SCAFFOLD_CI_CONTRACT_PATH))
    scaffold_ci["reusable_validators"] = [
        entry
        for entry in scaffold_ci["reusable_validators"]
        if entry["id"] != "analytics_ui_scaffold_ci_enforcement"
    ]

    errors = _validate(observability, ecosystem, scaffold_ci)

    assert any("reusable_validators missing" in error for error in errors)


def test_scaffold_ci_contract_rejects_runtime_feature_promotion() -> None:
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    scaffold_ci = _load_json(SCAFFOLD_CI_CONTRACT_PATH)
    for feature in observability["supported_feature_keys"]:
        if feature["feature_key"] == "analytics.backend.observability.freshness_supportability":
            feature["status"] = "implemented"

    errors = _validate(observability, ecosystem, scaffold_ci)

    assert any(
        "analytics.backend.observability.freshness_supportability: runtime feature must remain planned"
        in error
        for error in errors
    )


def test_scaffold_ci_contract_rejects_unimplemented_slice_11_feature_key() -> None:
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    scaffold_ci = _load_json(SCAFFOLD_CI_CONTRACT_PATH)
    for feature in observability["supported_feature_keys"]:
        if feature["feature_key"] == "platform.analytics.observability.scaffold_ci_enforcement":
            feature["status"] = "planned"

    errors = _validate(observability, ecosystem, scaffold_ci)

    assert any("scaffold_ci_enforcement must be implemented" in error for error in errors)
