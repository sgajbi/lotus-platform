from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from automation.validate_analytics_ui_ecosystem_completion import (
    REQUIRED_REPOSITORIES,
    validate_ecosystem_completion,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = ROOT / "context" / "contracts"
OBSERVABILITY_CONTRACT_PATH = CONTRACT_DIR / "analytics-ui-observability-contract.json"
ECOSYSTEM_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-ecosystem-completion.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(observability: dict, ecosystem: dict) -> list[str]:
    return validate_ecosystem_completion(
        observability_contract=observability,
        ecosystem_contract=ecosystem,
    )


def test_analytics_ui_ecosystem_completion_artifacts_are_present_and_governed() -> None:
    readme = (CONTRACT_DIR / "README.md").read_text(encoding="utf-8")
    schema = _load_json(
        CONTRACT_DIR / "analytics-ui-observability-ecosystem-completion.schema.json"
    )
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)

    assert "analytics-ui-observability-ecosystem-completion.schema.json" in readme
    assert "analytics-ui-observability-ecosystem-completion.json" in readme
    assert (
        schema["properties"]["contract_id"]["const"]
        == "analytics-ui-observability-ecosystem-completion"
    )
    assert schema["properties"]["governed_by_rfc"]["const"] == "RFC-0108"
    assert ecosystem["contract_id"] == "analytics-ui-observability-ecosystem-completion"
    assert ecosystem["governed_by_rfc"] == "RFC-0108"
    assert (
        ecosystem["lifecycle_status"]
        == "slice-12-backend-supportability-partial-implemented"
    )


def test_analytics_ui_ecosystem_completion_validator_accepts_baseline() -> None:
    assert (
        _validate(
            _load_json(OBSERVABILITY_CONTRACT_PATH),
            _load_json(ECOSYSTEM_CONTRACT_PATH),
        )
        == []
    )


def test_analytics_ui_ecosystem_completion_covers_every_lotus_repository() -> None:
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    participating = set(ecosystem["participating_repositories"])
    gap_repositories = {row["repository"] for row in ecosystem["app_gap_matrix"]}

    assert participating == REQUIRED_REPOSITORIES
    assert gap_repositories == REQUIRED_REPOSITORIES


def test_analytics_ui_ecosystem_completion_requires_slice_12_partial_only() -> None:
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    statuses = {
        entry["slice_id"]: entry["status"]
        for entry in ecosystem["ecosystem_completion_slices"]
    }

    assert statuses[10] == "implemented"
    assert statuses[11] == "implemented"
    assert statuses[12] == "partially_implemented"
    assert {statuses[slice_id] for slice_id in range(13, 19)} == {"planned"}


def test_analytics_ui_ecosystem_completion_rejects_missing_repository() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = copy.deepcopy(_load_json(ECOSYSTEM_CONTRACT_PATH))
    ecosystem["participating_repositories"].remove("lotus-ai")

    errors = _validate(observability, ecosystem)

    assert any("participating_repositories missing" in error for error in errors)
    assert any("lotus-ai" in error for error in errors)


def test_analytics_ui_ecosystem_completion_rejects_premature_slice_completion() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = copy.deepcopy(_load_json(ECOSYSTEM_CONTRACT_PATH))
    for entry in ecosystem["ecosystem_completion_slices"]:
        if entry["slice_id"] == 12:
            entry["status"] = "implemented"

    errors = _validate(observability, ecosystem)

    assert any("Slice 12 must be partially_implemented" in error for error in errors)


def test_analytics_ui_ecosystem_completion_rejects_unknown_feature_key() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = copy.deepcopy(_load_json(ECOSYSTEM_CONTRACT_PATH))
    ecosystem["app_gap_matrix"][0]["feature_keys"].append(
        "platform.analytics.observability.unknown"
    )

    errors = _validate(observability, ecosystem)

    assert any("unsupported feature keys" in error for error in errors)


def test_analytics_ui_ecosystem_completion_rejects_missing_branch_policy() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = copy.deepcopy(_load_json(ECOSYSTEM_CONTRACT_PATH))
    ecosystem["branch_policy"]["runtime_work_blocked_before_slice_10_merge"] = False

    errors = _validate(observability, ecosystem)

    assert any(
        "runtime_work_blocked_before_slice_10_merge" in error for error in errors
    )


def test_analytics_ui_ecosystem_completion_rejects_premature_feature_promotion() -> (
    None
):
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    for feature in observability["supported_feature_keys"]:
        if feature["feature_key"] == "gateway.analytics.observability.fanout_metrics":
            feature["status"] = "implemented"

    errors = _validate(observability, ecosystem)

    assert any(
        "gateway.analytics.observability.fanout_metrics: ecosystem feature must remain planned"
        in error
        for error in errors
    )


@pytest.mark.parametrize(
    "feature_key",
    [
        "advise.observability.advisory_supportability",
        "performance.observability.calculation_supportability",
        "report.observability.evidence_surface_supportability",
        "risk.observability.calculation_supportability",
        "manage.observability.action_register_supportability",
    ],
)
def test_analytics_ui_ecosystem_completion_requires_slice_12_features_implemented(
    feature_key: str,
) -> None:
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    for feature in observability["supported_feature_keys"]:
        if feature["feature_key"] == feature_key:
            feature["status"] = "planned"

    errors = _validate(observability, ecosystem)

    assert any(
        f"{feature_key} must be implemented after Slice 12 partial proof" in error
        for error in errors
    )
