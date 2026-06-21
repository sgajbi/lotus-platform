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
        ecosystem["lifecycle_status"] == "slice-18-ecosystem-final-closure-implemented"
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


def test_analytics_ui_ecosystem_completion_records_gateway_backed_archive_retrieval() -> (
    None
):
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    archive_row = next(
        row
        for row in ecosystem["app_gap_matrix"]
        if row["repository"] == "lotus-archive"
    )

    assert (
        "gateway_backed_workbench_archive_retrieval_implemented"
        in archive_row["gap_classification"]
    )
    assert (
        "workbench_archive_surface_reconciliation_not_supported"
        not in (archive_row["gap_classification"])
    )
    assert "workbenchRetrievalSupported=false" not in archive_row["blockers"][0]
    assert (
        "direct Workbench-to-archive non-support" in archive_row["wiki_source_decision"]
    )


def test_analytics_ui_ecosystem_completion_records_core_metric_label_proof() -> None:
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    core_row = next(
        row for row in ecosystem["app_gap_matrix"] if row["repository"] == "lotus-core"
    )

    assert "explicit_metric_labels_proven" in core_row["gap_classification"]
    assert "no_sensitive_metric_labels_proven" in core_row["gap_classification"]
    assert "lotus-core PR #329" in str(ecosystem["ecosystem_completion_slices"])
    assert "state/reason/freshness_bucket" in core_row["blockers"][0]
    assert "Prometheus metric label proof" in core_row["required_proof"]
    assert "no-sensitive metric label proof" in core_row["required_proof"]
    assert (
        "operator/business feature-state diagrams" in core_row["wiki_source_decision"]
    )


def test_analytics_ui_ecosystem_completion_records_risk_metric_label_proof() -> None:
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    risk_row = next(
        row for row in ecosystem["app_gap_matrix"] if row["repository"] == "lotus-risk"
    )

    assert "explicit_metric_labels_proven" in risk_row["gap_classification"]
    assert "no_sensitive_metric_labels_proven" in risk_row["gap_classification"]
    assert "lotus-risk PR #109" in str(ecosystem["ecosystem_completion_slices"])
    assert "explicit metric_labels" in risk_row["blockers"][0]
    assert "no-sensitive metric label proof" in risk_row["required_proof"]
    assert "operator flow diagram" in risk_row["wiki_source_decision"]


def test_analytics_ui_ecosystem_completion_records_advise_metric_label_proof() -> None:
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    advise_row = next(
        row
        for row in ecosystem["app_gap_matrix"]
        if row["repository"] == "lotus-advise"
    )

    assert "explicit_metric_labels_proven" in advise_row["gap_classification"]
    assert "no_sensitive_metric_labels_proven" in advise_row["gap_classification"]
    assert "lotus-advise PR #109" in str(ecosystem["ecosystem_completion_slices"])
    assert "supportability.metric_labels" in advise_row["blockers"][0]
    assert "no-sensitive metric label proof" in advise_row["required_proof"]
    assert "API surface" in advise_row["wiki_source_decision"]


def test_analytics_ui_ecosystem_completion_requires_slice_13_implemented() -> None:
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    statuses = {
        entry["slice_id"]: entry["status"]
        for entry in ecosystem["ecosystem_completion_slices"]
    }

    assert statuses[10] == "implemented"
    assert statuses[11] == "implemented"
    assert statuses[12] == "partially_implemented"
    assert statuses[13] == "implemented"
    assert statuses[14] == "partially_implemented"
    assert statuses[15] == "implemented"
    assert statuses[16] == "implemented"
    assert statuses[17] == "implemented"
    assert statuses[18] == "implemented"


def test_analytics_ui_ecosystem_completion_rejects_missing_repository() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = copy.deepcopy(_load_json(ECOSYSTEM_CONTRACT_PATH))
    ecosystem["participating_repositories"].remove("lotus-ai")

    errors = _validate(observability, ecosystem)

    assert any("participating_repositories missing" in error for error in errors)
    assert any("lotus-ai" in error for error in errors)


def test_analytics_ui_ecosystem_completion_rejects_slice_13_regression() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = copy.deepcopy(_load_json(ECOSYSTEM_CONTRACT_PATH))
    for entry in ecosystem["ecosystem_completion_slices"]:
        if entry["slice_id"] == 13:
            entry["status"] = "partially_implemented"

    errors = _validate(observability, ecosystem)

    assert any("Slice 13 must be implemented" in error for error in errors)


def test_analytics_ui_ecosystem_completion_rejects_unknown_feature_key() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = copy.deepcopy(_load_json(ECOSYSTEM_CONTRACT_PATH))
    ecosystem["app_gap_matrix"][0]["feature_keys"].append(
        "platform.analytics.observability.unknown"
    )

    errors = _validate(observability, ecosystem)

    assert any("unsupported feature keys" in error for error in errors)


def test_analytics_ui_ecosystem_completion_rejects_invalid_gap_matrix_posture() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = copy.deepcopy(_load_json(ECOSYSTEM_CONTRACT_PATH))
    ecosystem["app_gap_matrix"][0]["posture"] = "mostly_done"

    errors = _validate(observability, ecosystem)

    assert any("invalid posture mostly_done" in error for error in errors)


def test_analytics_ui_ecosystem_completion_rejects_missing_gap_matrix_field() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = copy.deepcopy(_load_json(ECOSYSTEM_CONTRACT_PATH))
    ecosystem["app_gap_matrix"][0]["required_proof"] = ""

    errors = _validate(observability, ecosystem)

    assert any("required_proof is required" in error for error in errors)


def test_analytics_ui_ecosystem_completion_rejects_missing_branch_policy() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = copy.deepcopy(_load_json(ECOSYSTEM_CONTRACT_PATH))
    ecosystem["branch_policy"]["runtime_work_blocked_before_slice_10_merge"] = False

    errors = _validate(observability, ecosystem)

    assert any(
        "runtime_work_blocked_before_slice_10_merge" in error for error in errors
    )


def test_analytics_ui_ecosystem_completion_rejects_all_path_regression() -> None:
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    for feature in observability["supported_feature_keys"]:
        if (
            feature["feature_key"]
            == "gateway.analytics.observability.all_ui_fanout_paths"
        ):
            feature["status"] = "planned"

    errors = _validate(observability, ecosystem)

    assert any(
        "gateway.analytics.observability.all_ui_fanout_paths: Slice 13 feature must be implemented"
        in error
        for error in errors
    )


def test_analytics_ui_ecosystem_completion_requires_slice_10_contract_feature() -> (
    None
):
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    for feature in observability["supported_feature_keys"]:
        if (
            feature["feature_key"]
            == "platform.analytics.observability.ecosystem_completion_contract"
        ):
            feature["status"] = "planned"

    errors = _validate(observability, ecosystem)

    assert any(
        "platform.analytics.observability.ecosystem_completion_contract must be implemented after Slice 10"
        in error
        for error in errors
    )


def test_analytics_ui_ecosystem_completion_requires_slice_11_scaffold_feature() -> (
    None
):
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    for feature in observability["supported_feature_keys"]:
        if (
            feature["feature_key"]
            == "platform.analytics.observability.scaffold_ci_enforcement"
        ):
            feature["status"] = "planned"

    errors = _validate(observability, ecosystem)

    assert any(
        "platform.analytics.observability.scaffold_ci_enforcement must be implemented after Slice 11"
        in error
        for error in errors
    )


@pytest.mark.parametrize(
    "feature_key",
    [
        "analytics.backend.observability.freshness_supportability",
        "advise.observability.advisory_supportability",
        "ai.observability.ai_surface_supportability",
        "archive.observability.archive_supportability",
        "core.observability.portfolio_supportability",
        "performance.observability.calculation_supportability",
        "render.observability.render_supportability",
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


def test_analytics_ui_ecosystem_completion_requires_slice_13_features_implemented() -> (
    None
):
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    for feature in observability["supported_feature_keys"]:
        if feature["feature_key"] in {
            "gateway.analytics.observability.fanout_metrics",
            "gateway.analytics.observability.protected_diagnostics",
            "gateway.analytics.observability.all_ui_fanout_paths",
        }:
            feature["status"] = "planned"

    errors = _validate(observability, ecosystem)

    assert any(
        "gateway.analytics.observability.fanout_metrics must be implemented after Slice 13 proof"
        in error
        for error in errors
    )
    assert any(
        "gateway.analytics.observability.protected_diagnostics must be implemented after Slice 13 proof"
        in error
        for error in errors
    )


def test_analytics_ui_ecosystem_completion_requires_slice_15_feature_implemented() -> (
    None
):
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    for feature in observability["supported_feature_keys"]:
        if (
            feature["feature_key"]
            == "platform.analytics.observability.ecosystem_dashboards_alerts"
        ):
            feature["status"] = "planned"

    errors = _validate(observability, ecosystem)

    assert any(
        "platform.analytics.observability.ecosystem_dashboards_alerts: Slice 15 feature must be implemented"
        in error
        or "platform.analytics.observability.ecosystem_dashboards_alerts: Slice 16 platform feature must be implemented"
        in error
        for error in errors
    )


def test_analytics_ui_ecosystem_completion_requires_slice_16_feature_implemented() -> (
    None
):
    observability = copy.deepcopy(_load_json(OBSERVABILITY_CONTRACT_PATH))
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    for feature in observability["supported_feature_keys"]:
        if (
            feature["feature_key"]
            == "platform.analytics.observability.ecosystem_implementation_proof"
        ):
            feature["status"] = "planned"

    errors = _validate(observability, ecosystem)

    assert any(
        "platform.analytics.observability.ecosystem_implementation_proof: Slice 16 platform feature must be implemented"
        in error
        for error in errors
    )
