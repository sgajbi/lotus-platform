from __future__ import annotations

import copy
import json
from pathlib import Path

from automation.validate_analytics_ui_ecosystem_hardening import (
    validate_ecosystem_hardening,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = ROOT / "context" / "contracts"
OBSERVABILITY_CONTRACT_PATH = CONTRACT_DIR / "analytics-ui-observability-contract.json"
ECOSYSTEM_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-ecosystem-completion.json"
)
ECOSYSTEM_PROOF_PATH = CONTRACT_DIR / "analytics-ui-observability-ecosystem-proof.json"
HARDENING_PATH = CONTRACT_DIR / "analytics-ui-observability-ecosystem-hardening.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate(
    observability_contract: dict,
    ecosystem_contract: dict,
    ecosystem_proof: dict,
    hardening: dict,
) -> list[str]:
    return validate_ecosystem_hardening(
        observability_contract=observability_contract,
        ecosystem_contract=ecosystem_contract,
        ecosystem_proof=ecosystem_proof,
        hardening=hardening,
    )


def test_ecosystem_hardening_artifacts_are_present_and_governed() -> None:
    readme = (CONTRACT_DIR / "README.md").read_text(encoding="utf-8")
    schema = _load_json(
        CONTRACT_DIR / "analytics-ui-observability-ecosystem-hardening.schema.json"
    )
    hardening = _load_json(HARDENING_PATH)

    assert "analytics-ui-observability-ecosystem-hardening.schema.json" in readme
    assert "analytics-ui-observability-ecosystem-hardening.json" in readme
    assert (
        schema["properties"]["contract_id"]["const"]
        == "analytics-ui-observability-ecosystem-hardening"
    )
    assert schema["properties"]["governed_by_rfc"]["const"] == "RFC-0108"
    assert hardening["contract_id"] == "analytics-ui-observability-ecosystem-hardening"
    assert hardening["governed_by_rfc"] == "RFC-0108"
    assert hardening["lifecycle_status"] == "slice-17-ecosystem-hardening-certified"


def test_ecosystem_hardening_validator_accepts_baseline() -> None:
    assert (
        _validate(
            _load_json(OBSERVABILITY_CONTRACT_PATH),
            _load_json(ECOSYSTEM_CONTRACT_PATH),
            _load_json(ECOSYSTEM_PROOF_PATH),
            _load_json(HARDENING_PATH),
        )
        == []
    )


def test_ecosystem_hardening_records_archive_reconciliation_evidence() -> None:
    hardening = _load_json(HARDENING_PATH)
    archive_review = next(
        review
        for review in hardening["repository_reviews"]
        if review["repository"] == "lotus-archive"
    )

    assert "Workbench PR #126 implements Gateway/BFF-backed archive metadata" in (
        archive_review["ci_evidence"]
    )
    assert "direct Workbench-to-archive calls remain unsupported" in (
        archive_review["ci_evidence"]
    )
    assert "archive-surface reconciliation remain planned" not in (
        archive_review["ci_evidence"]
    )


def test_ecosystem_hardening_records_core_metric_label_proof() -> None:
    hardening = _load_json(HARDENING_PATH)
    core_review = next(
        review
        for review in hardening["repository_reviews"]
        if review["repository"] == "lotus-core"
    )

    assert "lotus-core PR #329" in core_review["ci_evidence"]
    assert "explicit metric_labels" in core_review["ci_evidence"]
    assert "state, reason, and freshness_bucket" in core_review["ci_evidence"]
    assert "no-sensitive label rejection" in core_review["ci_evidence"]
    assert "lotus-core portfolio readiness supportability" in str(
        hardening["api_certification_review"]
    )


def test_ecosystem_hardening_records_risk_metric_label_proof() -> None:
    hardening = _load_json(HARDENING_PATH)
    risk_review = next(
        review
        for review in hardening["repository_reviews"]
        if review["repository"] == "lotus-risk"
    )

    assert "lotus-risk PR #109" in risk_review["ci_evidence"]
    assert "explicit metric_labels" in risk_review["ci_evidence"]
    assert "lotus_risk_calculation_supportability_total" in risk_review["ci_evidence"]
    assert "lotus_analytics_freshness_bucket_total" in risk_review["ci_evidence"]
    assert "no-sensitive label rejection" in risk_review["ci_evidence"]


def test_ecosystem_hardening_rejects_missing_repository_review() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    proof = _load_json(ECOSYSTEM_PROOF_PATH)
    hardening = copy.deepcopy(_load_json(HARDENING_PATH))
    hardening["repository_reviews"] = [
        review
        for review in hardening["repository_reviews"]
        if review["repository"] != "lotus-risk"
    ]

    errors = _validate(observability, ecosystem, proof, hardening)

    assert any("repository_reviews missing" in error for error in errors)


def test_ecosystem_hardening_rejects_open_p1_finding() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    proof = _load_json(ECOSYSTEM_PROOF_PATH)
    hardening = copy.deepcopy(_load_json(HARDENING_PATH))
    hardening["findings"].append(
        {
            "finding_id": "RFC0108-ECOSYSTEM-HARDENING-OPEN-P1",
            "severity": "P1",
            "status": "planned_residual",
            "summary": "test-only open finding",
            "evidence": "test-only evidence",
        }
    )

    errors = _validate(observability, ecosystem, proof, hardening)

    assert any("P0/P1 findings must be closed" in error for error in errors)


def test_ecosystem_hardening_rejects_unreviewed_planned_feature() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    proof = _load_json(ECOSYSTEM_PROOF_PATH)
    hardening = copy.deepcopy(_load_json(HARDENING_PATH))
    hardening["supported_features_audit"]["planned_feature_keys_reviewed"].remove(
        "workbench.analytics.observability.all_supported_surfaces"
    )

    errors = _validate(observability, ecosystem, proof, hardening)

    assert any("planned_feature_keys_reviewed missing" in error for error in errors)


def test_ecosystem_hardening_rejects_unreconciled_openapi_path() -> None:
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    proof = copy.deepcopy(_load_json(ECOSYSTEM_PROOF_PATH))
    hardening = _load_json(HARDENING_PATH)
    proof["openapi_proof"]["required_paths"].append("/api/v1/test-only")

    errors = _validate(observability, ecosystem, proof, hardening)

    assert any("openapi_paths_reviewed missing" in error for error in errors)
