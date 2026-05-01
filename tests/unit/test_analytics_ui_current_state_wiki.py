from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WIKI_PATH = ROOT / "wiki" / "Analytics-UI-Observability.md"
HOME_PATH = ROOT / "wiki" / "Home.md"
SIDEBAR_PATH = ROOT / "wiki" / "_Sidebar.md"
RFC_INDEX_PATH = ROOT / "wiki" / "RFC-Index.md"
RUNBOOK_PATH = ROOT / "docs" / "operations" / "analytics-ui-observability-runbook.md"
OBSERVABILITY_CONTRACT_PATH = (
    ROOT / "context" / "contracts" / "analytics-ui-observability-contract.json"
)
ECOSYSTEM_CONTRACT_PATH = (
    ROOT
    / "context"
    / "contracts"
    / "analytics-ui-observability-ecosystem-completion.json"
)
ECOSYSTEM_PROOF_PATH = (
    ROOT / "context" / "contracts" / "analytics-ui-observability-ecosystem-proof.json"
)
ECOSYSTEM_HARDENING_PATH = (
    ROOT
    / "context"
    / "contracts"
    / "analytics-ui-observability-ecosystem-hardening.json"
)
ECOSYSTEM_FINAL_CLOSURE_PATH = (
    ROOT
    / "context"
    / "contracts"
    / "analytics-ui-observability-ecosystem-final-closure.json"
)
RISK_API_VOCABULARY_PATH = (
    ROOT / "platform-contracts" / "api-vocabulary" / "lotus-risk-api-vocabulary.v1.json"
)
PERFORMANCE_API_VOCABULARY_PATH = (
    ROOT
    / "platform-contracts"
    / "api-vocabulary"
    / "lotus-performance-api-vocabulary.v1.json"
)
ADVISE_API_VOCABULARY_PATH = (
    ROOT
    / "platform-contracts"
    / "api-vocabulary"
    / "lotus-advise-api-vocabulary.v1.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> dict:
    return json.loads(_read(path))


def test_analytics_ui_observability_wiki_is_linked_from_operator_entry_points() -> None:
    wiki = _read(WIKI_PATH)
    home = _read(HOME_PATH)
    sidebar = _read(SIDEBAR_PATH)
    runbook = _read(RUNBOOK_PATH)

    assert "# Analytics UI Observability" in wiki
    assert "[Analytics UI Observability](Analytics-UI-Observability)" in home
    assert "[Analytics UI Observability](Analytics-UI-Observability)" in sidebar
    assert "wiki/Analytics-UI-Observability.md" in runbook


def test_analytics_ui_observability_wiki_records_implementation_backed_scope() -> None:
    wiki = _read(WIKI_PATH)
    observability = _load_json(OBSERVABILITY_CONTRACT_PATH)
    ecosystem = _load_json(ECOSYSTEM_CONTRACT_PATH)
    proof = _load_json(ECOSYSTEM_PROOF_PATH)
    hardening = _load_json(ECOSYSTEM_HARDENING_PATH)
    final_closure = _load_json(ECOSYSTEM_FINAL_CLOSURE_PATH)
    feature_evidence = {
        feature["feature_key"]: feature["promotion_evidence"]
        for feature in observability["supported_feature_keys"]
    }
    performance_row = next(
        row
        for row in ecosystem["app_gap_matrix"]
        if row["repository"] == "lotus-performance"
    )
    core_row = next(
        row for row in ecosystem["app_gap_matrix"] if row["repository"] == "lotus-core"
    )
    advise_row = next(
        row
        for row in ecosystem["app_gap_matrix"]
        if row["repository"] == "lotus-advise"
    )

    required_evidence = [
        "lotus-performance PRs #138, #139, #140, and #141",
        "lotus-risk PRs #107, #108, and #109",
        "lotus-core PR #329",
        "lotus-advise PR #109",
        "`lotus-risk` PR #109",
        "`lotus-advise` PR #109",
        "state`, `reason`, and `freshness_bucket",
        "Gateway PRs #166 through #172",
        "Workbench PRs #118 through #129",
        "Workbench PR #132",
        "PB_SG_GLOBAL_BAL_001",
        "context/contracts/",
        "rfc-0108-performance-layout-hardening-qa",
    ]
    for evidence in required_evidence:
        assert evidence in wiki

    assert (
        "PR #140"
        in feature_evidence["performance.observability.calculation_supportability"]
    )
    assert (
        "PR #141"
        in feature_evidence["performance.observability.calculation_supportability"]
    )
    assert (
        "metric_labels"
        in feature_evidence["performance.observability.calculation_supportability"]
    )
    assert (
        "no-sensitive Prometheus exposition proof"
        in feature_evidence["performance.observability.calculation_supportability"]
    )
    assert (
        "PR #140"
        in feature_evidence["analytics.backend.observability.freshness_supportability"]
    )
    assert (
        "PR #141"
        in feature_evidence["analytics.backend.observability.freshness_supportability"]
    )
    assert "PR #140" in performance_row["blockers"][0]
    assert "PR #141" in performance_row["blockers"][0]
    assert "PR #140" in performance_row["wiki_source_decision"]
    assert "PR #141" in performance_row["wiki_source_decision"]
    risk_evidence = feature_evidence["risk.observability.calculation_supportability"]
    assert "lotus-risk PR #109" in risk_evidence
    assert "metric_labels" in risk_evidence
    assert "no-sensitive label rejection" in risk_evidence
    assert (
        "metric_labels"
        in feature_evidence["core.observability.portfolio_supportability"]
    )
    assert "PR #329" in feature_evidence["core.observability.portfolio_supportability"]
    assert "no_sensitive_metric_labels_proven" in core_row["gap_classification"]
    assert "no_sensitive_metric_labels_proven" in advise_row["gap_classification"]
    assert "PR #329" in str(ecosystem["ecosystem_completion_slices"])
    assert "lotus-advise PR #109" in str(ecosystem["ecosystem_completion_slices"])
    assert "PR #140" in str(proof["residual_scope"])
    assert "PR #140" in str(hardening["repository_reviews"])
    assert "PR #141" in str(hardening["repository_reviews"])
    assert "PR #109" in str(hardening["repository_reviews"])
    assert "PR #329" in str(hardening["repository_reviews"])
    assert "lotus-advise PR #109" in str(hardening["repository_reviews"])
    assert "PR #140" in str(final_closure["residual_scope"])
    assert "PR #141" in str(final_closure["residual_scope"])
    assert "PR #109" in str(final_closure["residual_scope"])
    assert "PR #329" in str(final_closure["residual_scope"])
    assert "lotus-advise PR #109" in str(final_closure["residual_scope"])


def test_platform_risk_api_vocabulary_records_supportability_metric_labels() -> None:
    vocabulary = _load_json(RISK_API_VOCABULARY_PATH)
    metric_labels_attribute = next(
        attribute
        for attribute in vocabulary["attributeCatalog"]
        if attribute["semanticId"] == "lotus.metric_labels"
    )
    observed_names = {
        field["name"]
        for endpoint in vocabulary["endpoints"]
        for payload in (endpoint["request"], endpoint["response"])
        for field in payload["fields"]
    }

    assert metric_labels_attribute["canonicalTerm"] == "metric_labels"
    assert (
        "lotus_risk_calculation_supportability_total"
        in (metric_labels_attribute["description"])
    )
    assert "metadata.calculation_supportability.metric_labels" in observed_names


def test_platform_performance_api_vocabulary_records_supportability_metric_labels() -> (
    None
):
    vocabulary = _load_json(PERFORMANCE_API_VOCABULARY_PATH)
    metric_labels_attribute = next(
        attribute
        for attribute in vocabulary["attributeCatalog"]
        if attribute["semanticId"] == "lotus.metric_labels"
    )
    observed_names = {
        field["name"]
        for endpoint in vocabulary["endpoints"]
        for payload in (endpoint["request"], endpoint["response"])
        for field in payload["fields"]
    }

    assert metric_labels_attribute["canonicalTerm"] == "metric_labels"
    assert (
        "lotus_performance_calculation_supportability_total"
        in (metric_labels_attribute["description"])
    )
    assert "calculation_supportability.metric_labels" in observed_names


def test_platform_advise_api_vocabulary_records_supportability_metric_labels() -> None:
    vocabulary = _load_json(ADVISE_API_VOCABULARY_PATH)
    metric_labels_attribute = next(
        attribute
        for attribute in vocabulary["attributeCatalog"]
        if attribute["semanticId"] == "lotus.metric_labels"
    )
    observed_names = {
        field["name"]
        for endpoint in vocabulary["endpoints"]
        for payload in (endpoint["request"], endpoint["response"])
        for field in payload["fields"]
    }

    assert metric_labels_attribute["canonicalTerm"] == "metric_labels"
    assert (
        "lotus_advise_advisory_supportability_total"
        in (metric_labels_attribute["description"])
    )
    assert "supportability.metric_labels" in observed_names


def test_analytics_ui_observability_wiki_preserves_residual_boundaries() -> None:
    wiki = _read(WIKI_PATH)
    rfc_index = _read(RFC_INDEX_PATH)

    assert "RFC-0108 is closed for current implementation-backed claims" in wiki
    assert "Full RFC-0079 risk/evidence scope" in wiki
    assert "complete Workbench all-supported-surface" in wiki
    assert "lotus-platform/platform-stack" in wiki
    assert "governed `lotus-workbench` runtime" in wiki
    assert "lotus-performance PR #140" in rfc_index
    assert "lotus-performance PR #141" in rfc_index
    assert "lotus-risk PR #109" in rfc_index
    assert "lotus-advise PR #109" in rfc_index
