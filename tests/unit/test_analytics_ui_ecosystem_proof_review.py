from __future__ import annotations

import copy
import json
from pathlib import Path

from automation.review_analytics_ui_ecosystem_proof import (
    EcosystemReviewInputs,
    review_ecosystem_proof,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DIR = ROOT / "context" / "contracts"
OBSERVABILITY_CONTRACT_PATH = CONTRACT_DIR / "analytics-ui-observability-contract.json"
ECOSYSTEM_COMPLETION_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-ecosystem-completion.json"
)
PROOF_CONTRACT_PATH = CONTRACT_DIR / "analytics-ui-observability-ecosystem-proof.json"
DASHBOARD_PATH = (
    ROOT
    / "platform-stack"
    / "grafana"
    / "dashboards"
    / "analytics-ui-observability-overview.json"
)
ALERT_RULES_PATH = (
    ROOT
    / "platform-stack"
    / "prometheus"
    / "rules"
    / "analytics-ui-observability.rules.yml"
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")


def _copy_contract_artifacts(tmp_path: Path) -> dict[str, Path]:
    paths = {
        "observability": tmp_path / "observability.json",
        "ecosystem": tmp_path / "ecosystem.json",
        "proof": tmp_path / "proof.json",
        "dashboard": tmp_path / "dashboard.json",
        "alerts": tmp_path / "rules.yml",
    }
    paths["observability"].write_text(
        OBSERVABILITY_CONTRACT_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    paths["ecosystem"].write_text(
        ECOSYSTEM_COMPLETION_CONTRACT_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    paths["proof"].write_text(
        PROOF_CONTRACT_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    paths["dashboard"].write_text(
        DASHBOARD_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    paths["alerts"].write_text(
        ALERT_RULES_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    return paths


def _valid_live_summary(evidence_dir: Path) -> dict:
    screenshots = []
    for panel in [
        "portfolio.summary",
        "portfolio.detailed",
        "performance.summary",
        "performance.analysis.contribution",
        "performance.advisor_brief",
        "performance.risk.snapshot",
        "performance.evidence",
    ]:
        screenshot_path = evidence_dir / f"{panel.replace('.', '-')}.png"
        screenshot_path.write_bytes(b"synthetic screenshot")
        screenshots.append(
            {
                "name": screenshot_path.name,
                "path": str(screenshot_path),
                "panel": panel,
                "state": "demo_ready",
            }
        )

    return {
        "portfolioId": "PB_SG_GLOBAL_BAL_001",
        "benchmarkCode": "BMK_PB_GLOBAL_BALANCED_60_40",
        "canonicalAsOfDate": "2026-04-10",
        "apiChecks": [
            {"description": "Foundation workspace", "status": "passed"},
            {"description": "Workbench portfolio route", "status": "passed"},
            {"description": "Performance summary", "status": "passed"},
            {"description": "Performance details", "status": "passed"},
            {"description": "Workbench performance route", "status": "passed"},
            {"description": "Risk summary", "status": "passed"},
            {"description": "Risk concentration", "status": "passed"},
            {"description": "Risk drawdown", "status": "passed"},
            {"description": "Risk rolling", "status": "passed"},
            {"description": "Risk attribution", "status": "passed"},
            {"description": "Advisor brief", "status": "passed"},
            {"description": "Advisor brief source metrics", "status": "passed"},
            {"description": "Advisor brief ACCEPT review action", "status": "passed"},
            {"description": "Advisor brief SUPERSEDE review action", "status": "passed"},
            {"description": "Advisor brief REVISE review action", "status": "passed"},
            {"description": "lotus-manage integration capabilities", "status": "passed"},
            {"description": "lotus-report integration capabilities", "status": "passed"},
            {"description": "Gateway platform capabilities", "status": "passed"},
        ],
        "workflowPackChecks": [
            {
                "action": "ACCEPT",
                "resultSupportabilityStatus": "READY",
                "taskFlowSupportabilityStatus": "READY",
            },
            {
                "action": "SUPERSEDE",
                "resultSupportabilityStatus": "HISTORICAL",
                "taskFlowSupportabilityStatus": "HISTORICAL",
            },
            {
                "action": "REVISE",
                "resultSupportabilityStatus": "HISTORICAL",
                "taskFlowSupportabilityStatus": "HISTORICAL",
            },
        ],
        "panelClassifications": [
            {"panel": "portfolio.summary", "state": "ready"},
            {"panel": "portfolio.detailed", "state": "ready"},
            {"panel": "performance.summary", "state": "ready"},
            {"panel": "performance.analysis.contribution", "state": "ready"},
            {"panel": "performance.analysis.attribution", "state": "ready"},
            {"panel": "performance.risk.snapshot", "state": "ready"},
            {"panel": "performance.risk.concentration", "state": "ready"},
            {"panel": "performance.risk.drawdown", "state": "ready"},
            {"panel": "performance.risk.rolling", "state": "ready"},
            {"panel": "performance.risk.historical_attribution", "state": "ready"},
            {"panel": "performance.advisor_brief", "state": "ready"},
            {"panel": "performance.evidence", "state": "ready"},
        ],
        "screenshots": screenshots,
    }


def _diagnostics_response() -> dict:
    return {
        "contractVersion": "analytics-ui-diagnostics.v1",
        "supportReference": "gdiag-risk-summary-permission-blocked",
        "route": "workbench-analytics",
        "panel": "risk-summary",
        "lookupStatus": "available",
        "supportabilityState": "permission_blocked",
        "auditEvent": "gateway.analytics.audit.protected_diagnostics_lookup",
        "safeDimensions": {
            "operation": "analytics.risk.calculate",
            "service": "lotus-risk",
            "state": "permission_blocked",
            "reason": "upstream_authorization_denied",
        },
        "operatorGuidance": ["Confirm caller entitlement."],
        "forbiddenFields": [
            "account_id",
            "advisor_behavior",
            "advisor_id",
            "client_id",
            "client_name",
            "correlation_id",
            "document_id",
            "holding_id",
            "household_id",
            "instrument_id",
            "model_output",
            "portfolio_id",
            "raw_entitlement_failure",
            "raw_prompt",
            "request_body",
            "response_body",
            "screen_content",
            "session_id",
            "simulation_session_id",
            "trace_id",
            "transaction_id",
            "upload_id",
        ],
    }


def _openapi_response() -> dict:
    return {
        "openapi": "3.1.0",
        "paths": {
            "/api/v1/analytics-ui/diagnostics/{support_reference}": {
                "get": {
                    "summary": "Resolve protected analytics diagnostics posture",
                    "description": (
                        "Protected diagnostics endpoint using support_reference and "
                        "emitting gateway.analytics.audit.protected_diagnostics_lookup."
                    ),
                }
            }
        },
    }


def _write_valid_evidence(tmp_path: Path) -> dict[str, Path]:
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    live_summary_path = evidence_dir / "live-validation-summary.json"
    _write_json(live_summary_path, _valid_live_summary(evidence_dir))
    (evidence_dir / "SHOT-INDEX.md").write_text(
        "# Screenshot Index\n\n- synthetic governed evidence\n", encoding="utf-8"
    )

    qa_summary_path = tmp_path / "qa-summary.json"
    _write_json(
        qa_summary_path,
        {"status": "ok", "governed_live_summary_path": str(live_summary_path)},
    )
    diagnostics_path = tmp_path / "diagnostics.json"
    openapi_path = tmp_path / "openapi.json"
    _write_json(diagnostics_path, _diagnostics_response())
    _write_json(openapi_path, _openapi_response())
    return {
        "qa": qa_summary_path,
        "live": live_summary_path,
        "diagnostics": diagnostics_path,
        "openapi": openapi_path,
    }


def _review(tmp_path: Path) -> tuple[dict, dict[str, Path], dict[str, Path]]:
    contracts = _copy_contract_artifacts(tmp_path)
    evidence = _write_valid_evidence(tmp_path)
    review = review_ecosystem_proof(
        EcosystemReviewInputs(
            qa_summary_path=evidence["qa"],
            proof_contract_path=contracts["proof"],
            observability_contract_path=contracts["observability"],
            ecosystem_completion_contract_path=contracts["ecosystem"],
            dashboard_path=contracts["dashboard"],
            alert_rules_path=contracts["alerts"],
            protected_diagnostics_response_path=evidence["diagnostics"],
            gateway_openapi_path=evidence["openapi"],
            output_path=None,
        )
    )
    return review, contracts, evidence


def test_ecosystem_proof_review_accepts_complete_evidence(tmp_path: Path) -> None:
    review, _contracts, _evidence = _review(tmp_path)

    assert review["status"] == "passed"
    assert review["errors"] == []
    assert review["evidence"]["screenshot_count"] == 7
    assert (
        review["evidence"]["protected_diagnostics_audit_event"]
        == "gateway.analytics.audit.protected_diagnostics_lookup"
    )
    assert "performance-analytics" in review["evidence"]["journeys"]


def test_ecosystem_proof_review_rejects_missing_required_journey_api(
    tmp_path: Path,
) -> None:
    _review_result, contracts, evidence = _review(tmp_path)
    live = json.loads(evidence["live"].read_text(encoding="utf-8"))
    live["apiChecks"] = [
        entry for entry in live["apiChecks"] if entry["description"] != "Risk rolling"
    ]
    _write_json(evidence["live"], live)

    review = review_ecosystem_proof(
        EcosystemReviewInputs(
            qa_summary_path=evidence["qa"],
            proof_contract_path=contracts["proof"],
            observability_contract_path=contracts["observability"],
            ecosystem_completion_contract_path=contracts["ecosystem"],
            dashboard_path=contracts["dashboard"],
            alert_rules_path=contracts["alerts"],
            protected_diagnostics_response_path=evidence["diagnostics"],
            gateway_openapi_path=evidence["openapi"],
            output_path=None,
        )
    )

    assert review["status"] == "failed"
    assert any("risk-analytics: missing API checks" in error for error in review["errors"])


def test_ecosystem_proof_review_rejects_missing_live_summary_reference(
    tmp_path: Path,
) -> None:
    _review_result, contracts, evidence = _review(tmp_path)
    _write_json(evidence["qa"], {"status": "ok"})

    review = review_ecosystem_proof(
        EcosystemReviewInputs(
            qa_summary_path=evidence["qa"],
            proof_contract_path=contracts["proof"],
            observability_contract_path=contracts["observability"],
            ecosystem_completion_contract_path=contracts["ecosystem"],
            dashboard_path=contracts["dashboard"],
            alert_rules_path=contracts["alerts"],
            protected_diagnostics_response_path=evidence["diagnostics"],
            gateway_openapi_path=evidence["openapi"],
            output_path=None,
        )
    )

    assert review["status"] == "failed"
    assert review["live_summary_path"] is None
    assert (
        "ecosystem QA summary does not reference a live validation summary"
        in review["errors"]
    )


def test_ecosystem_proof_review_rejects_diagnostics_sensitive_leak(
    tmp_path: Path,
) -> None:
    _review_result, contracts, evidence = _review(tmp_path)
    diagnostics = json.loads(evidence["diagnostics"].read_text(encoding="utf-8"))
    diagnostics["operatorGuidance"].append("Use portfolio_id PB_SG_GLOBAL_BAL_001")
    _write_json(evidence["diagnostics"], diagnostics)

    review = review_ecosystem_proof(
        EcosystemReviewInputs(
            qa_summary_path=evidence["qa"],
            proof_contract_path=contracts["proof"],
            observability_contract_path=contracts["observability"],
            ecosystem_completion_contract_path=contracts["ecosystem"],
            dashboard_path=contracts["dashboard"],
            alert_rules_path=contracts["alerts"],
            protected_diagnostics_response_path=evidence["diagnostics"],
            gateway_openapi_path=evidence["openapi"],
            output_path=None,
        )
    )

    assert review["status"] == "failed"
    assert any("protected diagnostics leaked forbidden fields" in error for error in review["errors"])


def test_ecosystem_proof_review_rejects_unimplemented_dashboard_metric(
    tmp_path: Path,
) -> None:
    _review_result, contracts, evidence = _review(tmp_path)
    dashboard = json.loads(contracts["dashboard"].read_text(encoding="utf-8"))
    drifted_dashboard = copy.deepcopy(dashboard)
    drifted_dashboard["panels"][0]["targets"][0]["expr"] = (
        "sum(rate(lotus_backend_metric_not_implemented_total[5m]))"
    )
    _write_json(contracts["dashboard"], drifted_dashboard)

    review = review_ecosystem_proof(
        EcosystemReviewInputs(
            qa_summary_path=evidence["qa"],
            proof_contract_path=contracts["proof"],
            observability_contract_path=contracts["observability"],
            ecosystem_completion_contract_path=contracts["ecosystem"],
            dashboard_path=contracts["dashboard"],
            alert_rules_path=contracts["alerts"],
            protected_diagnostics_response_path=evidence["diagnostics"],
            gateway_openapi_path=evidence["openapi"],
            output_path=None,
        )
    )

    assert review["status"] == "failed"
    assert any("dashboard references unimplemented metrics" in error for error in review["errors"])


def test_ecosystem_proof_review_rejects_residual_promotion(tmp_path: Path) -> None:
    _review_result, contracts, evidence = _review(tmp_path)
    observability = json.loads(contracts["observability"].read_text(encoding="utf-8"))
    for feature in observability["supported_feature_keys"]:
        if feature["feature_key"] == "workbench.analytics.observability.all_supported_surfaces":
            feature["status"] = "implemented"
    _write_json(contracts["observability"], observability)

    review = review_ecosystem_proof(
        EcosystemReviewInputs(
            qa_summary_path=evidence["qa"],
            proof_contract_path=contracts["proof"],
            observability_contract_path=contracts["observability"],
            ecosystem_completion_contract_path=contracts["ecosystem"],
            dashboard_path=contracts["dashboard"],
            alert_rules_path=contracts["alerts"],
            protected_diagnostics_response_path=evidence["diagnostics"],
            gateway_openapi_path=evidence["openapi"],
            output_path=None,
        )
    )

    assert review["status"] == "failed"
    assert any("residual feature must remain planned" in error for error in review["errors"])


def test_ecosystem_proof_review_rejects_missing_openapi_route(tmp_path: Path) -> None:
    _review_result, contracts, evidence = _review(tmp_path)
    _write_json(evidence["openapi"], {"openapi": "3.1.0", "paths": {}})

    review = review_ecosystem_proof(
        EcosystemReviewInputs(
            qa_summary_path=evidence["qa"],
            proof_contract_path=contracts["proof"],
            observability_contract_path=contracts["observability"],
            ecosystem_completion_contract_path=contracts["ecosystem"],
            dashboard_path=contracts["dashboard"],
            alert_rules_path=contracts["alerts"],
            protected_diagnostics_response_path=evidence["diagnostics"],
            gateway_openapi_path=evidence["openapi"],
            output_path=None,
        )
    )

    assert review["status"] == "failed"
    assert any("Gateway OpenAPI missing paths" in error for error in review["errors"])
