from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_PATH = ROOT / "context" / "contracts" / "analytics-ui-observability-contract.json"


def _load_contract(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("contract_id") != "analytics-ui-observability-contract":
        errors.append("contract_id must be analytics-ui-observability-contract")
    if contract.get("governed_by_rfc") != "RFC-0108":
        errors.append("governed_by_rfc must be RFC-0108")
    if contract.get("lifecycle_status") not in {"implementation-not-started", "slice-0-implemented"}:
        errors.append("lifecycle_status must be implementation-not-started or slice-0-implemented")

    allowed_labels = set(contract.get("allowed_labels", []))
    forbidden_fields = set(contract.get("forbidden_fields", []))
    overlap = allowed_labels & forbidden_fields
    if overlap:
        errors.append(f"allowed_labels must not include forbidden fields: {sorted(overlap)}")

    metric_families = contract.get("metric_families", [])
    if not metric_families:
        errors.append("metric_families must define planned metric candidates")
    for metric in metric_families:
        name = metric.get("metric_name", "<missing>")
        if metric.get("implemented") is not False:
            errors.append(f"{name}: implemented must remain false before implementation proof")
        labels = set(metric.get("labels", []))
        unexpected_labels = labels - allowed_labels
        if unexpected_labels:
            errors.append(f"{name}: labels are not in allowed_labels: {sorted(unexpected_labels)}")
        forbidden_labels = labels & forbidden_fields
        if forbidden_labels:
            errors.append(f"{name}: labels include forbidden fields: {sorted(forbidden_labels)}")
        if not metric.get("purpose"):
            errors.append(f"{name}: purpose is required")

    if contract.get("dashboards"):
        errors.append("dashboards must remain empty until implemented metrics exist")
    if contract.get("alerts"):
        errors.append("alerts must remain empty until implemented metrics and thresholds exist")

    required_states = {
        "loading",
        "ready",
        "empty",
        "partial",
        "stale",
        "degraded",
        "error",
        "permission_blocked",
        "unsupported",
    }
    states = set(contract.get("state_vocabulary", []))
    missing_states = required_states - states
    if missing_states:
        errors.append(f"state_vocabulary missing required states: {sorted(missing_states)}")

    feature_keys = contract.get("supported_feature_keys", [])
    if not feature_keys:
        errors.append("supported_feature_keys must list planned governance keys")
    for feature in feature_keys:
        key = feature.get("feature_key", "<missing>")
        status = feature.get("status")
        if key == "platform.scaffolding.analytics_ui_observability_baseline":
            if status not in {"planned", "implemented"}:
                errors.append(f"{key}: status must be planned or implemented")
        elif status != "planned":
            errors.append(f"{key}: status must remain planned until implementation proof exists")
        if not feature.get("promotion_evidence"):
            errors.append(f"{key}: promotion_evidence is required")

    evidence_requirements = contract.get("evidence_requirements", {})
    required_artifact_types = {
        "browser",
        "gateway-api",
        "backend-log-metric",
        "dashboard",
        "sensitive-data-assertion",
        "github-check",
    }
    artifact_types = set(evidence_requirements.get("artifact_types", []))
    missing_artifacts = required_artifact_types - artifact_types
    if missing_artifacts:
        errors.append(f"evidence_requirements missing artifact types: {sorted(missing_artifacts)}")

    scaffold_requirements = set(contract.get("scaffold_requirements", []))
    for required in {
        "structured JSON event logging",
        "product-safe problem-details errors",
        "OpenAPI quality gate",
        "supported-features placeholder",
        "RFC implementation evidence directory",
    }:
        if required not in scaffold_requirements:
            errors.append(f"scaffold_requirements missing {required}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate RFC-0108 analytics UI observability contract.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    args = parser.parse_args()

    errors = validate_contract(_load_contract(args.contract))
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Analytics UI observability contract validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
