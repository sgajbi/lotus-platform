from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "context" / "contracts"
DEFAULT_OBSERVABILITY_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-contract.json"
)
DEFAULT_ECOSYSTEM_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-ecosystem-completion.json"
)
DEFAULT_SCAFFOLD_CI_CONTRACT_PATH = (
    CONTRACT_DIR / "analytics-ui-observability-scaffold-ci-enforcement.json"
)

IMPLEMENTED_FEATURE_KEY = (
    "platform.analytics.observability.scaffold_ci_enforcement"
)
RUNTIME_FEATURE_PREFIXES = (
    "core.",
    "performance.",
    "risk.",
    "advise.",
    "manage.",
    "report.",
    "render.",
    "archive.",
    "ai.",
)
EXPLICIT_RUNTIME_FEATURE_KEYS = {
    "analytics.backend.observability.freshness_supportability",
    "gateway.analytics.observability.fanout_metrics",
    "gateway.analytics.observability.protected_diagnostics",
    "gateway.analytics.observability.all_ui_fanout_paths",
    "workbench.analytics.observability.freshness_degraded_state",
    "workbench.analytics.observability.all_supported_surfaces",
}
POST_SLICE_11_LIFECYCLE_STATUSES = {
    "slice-11-scaffold-ci-enforcement-implemented",
    "slice-12-backend-supportability-partial-implemented",
    "slice-13-gateway-fanout-metrics-partial-implemented",
    "slice-13-gateway-fanout-metrics-implemented",
    "slice-14-workbench-supported-client-reads-partial-implemented",
    "slice-15-ecosystem-dashboards-alerts-implemented",
    "slice-16-ecosystem-implementation-proof-implemented",
    "slice-17-ecosystem-hardening-certified",
    "slice-18-ecosystem-final-closure-implemented",
}
POST_SLICE_11_IMPLEMENTED_RUNTIME_FEATURE_KEYS = {
    "analytics.backend.observability.freshness_supportability",
    "advise.observability.advisory_supportability",
    "ai.observability.ai_surface_supportability",
    "archive.observability.archive_supportability",
    "core.observability.portfolio_supportability",
    "gateway.analytics.observability.all_ui_fanout_paths",
    "gateway.analytics.observability.fanout_metrics",
    "gateway.analytics.observability.protected_diagnostics",
    "manage.observability.action_register_supportability",
    "performance.observability.calculation_supportability",
    "render.observability.render_supportability",
    "report.observability.evidence_surface_supportability",
    "risk.observability.calculation_supportability",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_scaffold_ci_enforcement(
    *,
    observability_contract: dict[str, Any],
    ecosystem_contract: dict[str, Any],
    scaffold_ci_contract: dict[str, Any],
    root: Path = ROOT,
) -> list[str]:
    errors: list[str] = []
    _validate_identity(errors, observability_contract, ecosystem_contract, scaffold_ci_contract)
    _validate_feature_promotion(errors, observability_contract)
    _validate_runtime_policy(errors, scaffold_ci_contract)
    _validate_artifact_terms(errors, scaffold_ci_contract, root)
    _validate_reusable_validators(errors, scaffold_ci_contract, root)
    return errors


def _feature_status(observability_contract: dict[str, Any]) -> dict[str, str]:
    return {
        str(feature.get("feature_key")): str(feature.get("status"))
        for feature in observability_contract.get("supported_feature_keys", [])
        if isinstance(feature, dict)
    }


def _validate_identity(
    errors: list[str],
    observability_contract: dict[str, Any],
    ecosystem_contract: dict[str, Any],
    scaffold_ci_contract: dict[str, Any],
) -> None:
    if (
        scaffold_ci_contract.get("contract_id")
        != "analytics-ui-observability-scaffold-ci-enforcement"
    ):
        errors.append(
            "contract_id must be analytics-ui-observability-scaffold-ci-enforcement"
        )
    if scaffold_ci_contract.get("governed_by_rfc") != "RFC-0108":
        errors.append("governed_by_rfc must be RFC-0108")
    if (
        scaffold_ci_contract.get("lifecycle_status")
        != "slice-11-scaffold-ci-enforcement-implemented"
    ):
        errors.append(
            "lifecycle_status must be slice-11-scaffold-ci-enforcement-implemented"
        )
    if observability_contract.get("lifecycle_status") not in POST_SLICE_11_LIFECYCLE_STATUSES:
        errors.append(
            "analytics-ui-observability-contract lifecycle_status must be "
            "slice-11-scaffold-ci-enforcement-implemented or a later RFC-0108 "
            "ecosystem lifecycle status"
        )
    if ecosystem_contract.get("lifecycle_status") not in POST_SLICE_11_LIFECYCLE_STATUSES:
        errors.append(
            "analytics-ui-observability-ecosystem-completion lifecycle_status must be "
            "slice-11-scaffold-ci-enforcement-implemented or a later RFC-0108 "
            "ecosystem lifecycle status"
        )
    source_contracts = set(scaffold_ci_contract.get("source_contracts", []))
    required = {
        "analytics-ui-observability-contract",
        "analytics-ui-observability-ecosystem-completion",
    }
    missing = required - source_contracts
    if missing:
        errors.append(f"source_contracts missing {sorted(missing)}")


def _validate_feature_promotion(
    errors: list[str], observability_contract: dict[str, Any]
) -> None:
    statuses = _feature_status(observability_contract)
    _validate_scaffold_ci_feature_status(errors, statuses)
    _validate_runtime_feature_statuses(errors, statuses)


def _validate_scaffold_ci_feature_status(
    errors: list[str], statuses: dict[str, str]
) -> None:
    if statuses.get(IMPLEMENTED_FEATURE_KEY) != "implemented":
        errors.append(f"{IMPLEMENTED_FEATURE_KEY} must be implemented after Slice 11")


def _is_runtime_feature(feature_key: str) -> bool:
    return feature_key.startswith(RUNTIME_FEATURE_PREFIXES) or (
        feature_key in EXPLICIT_RUNTIME_FEATURE_KEYS
    )


def _validate_runtime_feature_statuses(
    errors: list[str], statuses: dict[str, str]
) -> None:
    for feature_key, status in statuses.items():
        if (
            _is_runtime_feature(feature_key)
            and status != "planned"
            and feature_key not in POST_SLICE_11_IMPLEMENTED_RUNTIME_FEATURE_KEYS
        ):
            errors.append(f"{feature_key}: runtime feature must remain planned in Slice 11")


def _validate_runtime_policy(
    errors: list[str], scaffold_ci_contract: dict[str, Any]
) -> None:
    policy = scaffold_ci_contract.get("runtime_work_policy", {})
    if policy.get("no_app_runtime_promotion_in_slice_11") is not True:
        errors.append("runtime_work_policy.no_app_runtime_promotion_in_slice_11 must be true")
    if policy.get("platform_owned_reusable_baseline") is not True:
        errors.append("runtime_work_policy.platform_owned_reusable_baseline must be true")


def _validate_artifact_terms(
    errors: list[str],
    scaffold_ci_contract: dict[str, Any],
    root: Path,
) -> None:
    for section_name in (
        "backend_scaffold_defaults",
        "ui_surface_scaffold_defaults",
        "ci_enforcement",
    ):
        entries = scaffold_ci_contract.get(section_name, [])
        if not entries:
            errors.append(f"{section_name} must not be empty")
            continue
        for entry in entries:
            entry_id = str(entry.get("id", "<missing>"))
            path_value = entry.get("artifact_path")
            if not path_value:
                errors.append(f"{section_name}.{entry_id}: artifact_path is required")
                continue
            path = root / str(path_value)
            if not path.exists():
                errors.append(f"{section_name}.{entry_id}: missing artifact {path_value}")
                continue
            text = path.read_text(encoding="utf-8")
            for term in entry.get("required_terms", []):
                if str(term) not in text:
                    errors.append(
                        f"{section_name}.{entry_id}: {path_value} missing required term {term!r}"
                    )


def _validate_reusable_validators(
    errors: list[str],
    scaffold_ci_contract: dict[str, Any],
    root: Path,
) -> None:
    validators = scaffold_ci_contract.get("reusable_validators", [])
    required_paths = {
        "automation/validate_analytics_ui_observability_contract.py",
        "automation/validate_analytics_ui_ecosystem_completion.py",
        "automation/validate_analytics_ui_scaffold_ci_enforcement.py",
    }
    actual_paths = {str(entry.get("path")) for entry in validators if isinstance(entry, dict)}
    missing = required_paths - actual_paths
    if missing:
        errors.append(f"reusable_validators missing {sorted(missing)}")
    for entry in validators:
        path_value = str(entry.get("path", ""))
        if not path_value:
            errors.append("reusable_validators entries require path")
            continue
        if not (root / path_value).exists():
            errors.append(f"reusable validator path does not exist: {path_value}")
        if entry.get("required_for_ci") is not True:
            errors.append(f"{path_value}: required_for_ci must be true")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate RFC-0108 Slice 11 scaffold and CI enforcement contract."
    )
    parser.add_argument(
        "--observability-contract",
        type=Path,
        default=DEFAULT_OBSERVABILITY_CONTRACT_PATH,
    )
    parser.add_argument(
        "--ecosystem-contract",
        type=Path,
        default=DEFAULT_ECOSYSTEM_CONTRACT_PATH,
    )
    parser.add_argument(
        "--scaffold-ci-contract",
        type=Path,
        default=DEFAULT_SCAFFOLD_CI_CONTRACT_PATH,
    )
    args = parser.parse_args()

    errors = validate_scaffold_ci_enforcement(
        observability_contract=_load_json(args.observability_contract),
        ecosystem_contract=_load_json(args.ecosystem_contract),
        scaffold_ci_contract=_load_json(args.scaffold_ci_contract),
    )
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Analytics UI scaffold CI enforcement validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
