from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OBSERVABILITY_CONTRACT_PATH = (
    ROOT / "context" / "contracts" / "analytics-ui-observability-contract.json"
)
DEFAULT_ROLLOUT_CONTRACT_PATH = (
    ROOT
    / "context"
    / "contracts"
    / "analytics-ui-observability-rollout-readiness.json"
)
DEFAULT_PANEL_REGISTRY_PATH = ROOT / "context" / "contracts" / "workbench-panel-registry.json"
SUPPORTED_CERTIFICATION_STATUSES = {"certified", "certified_partial"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_contract_identity(
    *, errors: list[str], rollout_contract: dict[str, Any]
) -> None:
    if rollout_contract.get("contract_id") != "analytics-ui-observability-rollout-readiness":
        errors.append("contract_id must be analytics-ui-observability-rollout-readiness")
    if rollout_contract.get("governed_by_rfc") != "RFC-0108":
        errors.append("governed_by_rfc must be RFC-0108")
    if rollout_contract.get("lifecycle_status") != "slice-9-rollout-readiness-implemented":
        errors.append("lifecycle_status must be slice-9-rollout-readiness-implemented")


def _validate_source_proof(*, errors: list[str], source_proof: dict[str, Any]) -> None:
    if source_proof.get("source_slice") != "Slice 8":
        errors.append("source_proof.source_slice must be Slice 8")
    if source_proof.get("canonical_portfolio") != "PB_SG_GLOBAL_BAL_001":
        errors.append("source_proof.canonical_portfolio must be PB_SG_GLOBAL_BAL_001")
    if source_proof.get("canonical_benchmark") != "BMK_PB_GLOBAL_BALANCED_60_40":
        errors.append(
            "source_proof.canonical_benchmark must be BMK_PB_GLOBAL_BALANCED_60_40"
        )
    if not source_proof.get("merge_commit"):
        errors.append("source_proof.merge_commit is required")
    if not source_proof.get("pull_request"):
        errors.append("source_proof.pull_request is required")
    if not source_proof.get("evidence_artifacts"):
        errors.append("source_proof.evidence_artifacts must be non-empty")


def _registry_panels(panel_registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(panel.get("panel_id")): panel
        for panel in panel_registry.get("panels", [])
        if isinstance(panel, dict)
    }


def _route_group_mapping(
    *, errors: list[str], group: Any, index: int
) -> Mapping[str, Any] | None:
    if isinstance(group, Mapping):
        return group
    errors.append(f"certified_route_groups[{index}] must be an object")
    return None


def _route_group_panel_ids(group: Mapping[str, Any]) -> list[str]:
    panel_ids = group.get("panel_ids", [])
    if not isinstance(panel_ids, list):
        return []
    return [str(panel_id) for panel_id in panel_ids]


def _validate_route_group_status(
    *, errors: list[str], route: str, group: Mapping[str, Any]
) -> None:
    status = group.get("certification_status")
    if status not in SUPPORTED_CERTIFICATION_STATUSES:
        errors.append(f"{route}: certification_status is not supported")
    if status == "certified_partial" and not group.get("residual_scope"):
        errors.append(f"{route}: certified_partial groups require residual_scope")


def _validate_route_group_evidence(
    *, errors: list[str], route: str, group: Mapping[str, Any], panel_ids: list[str]
) -> None:
    if not panel_ids:
        errors.append(f"{route}: panel_ids must be non-empty")
    if not group.get("evidence_basis"):
        errors.append(f"{route}: evidence_basis is required")


def _validate_route_group_panel_routes(
    *,
    errors: list[str],
    route: str,
    panel_ids: list[str],
    registry_panels: dict[str, dict[str, Any]],
) -> set[str]:
    certified_panel_ids: set[str] = set()
    for panel_id in panel_ids:
        certified_panel_ids.add(panel_id)
        if panel_id not in registry_panels:
            errors.append(f"{route}: unknown panel_id {panel_id}")
            continue
        registry_route = str(registry_panels[panel_id].get("route", ""))
        if registry_route != route:
            errors.append(
                f"{panel_id}: rollout route {route} does not match registry route "
                f"{registry_route}"
            )
    return certified_panel_ids


def _validate_certified_route_groups(
    *,
    errors: list[str],
    certified_route_groups: list[Any],
    registry_panels: dict[str, dict[str, Any]],
) -> set[str]:
    if not certified_route_groups:
        errors.append("certified_route_groups must be non-empty")
    certified_panel_ids: set[str] = set()
    for index, group in enumerate(certified_route_groups):
        route_group = _route_group_mapping(errors=errors, group=group, index=index)
        if route_group is None:
            continue
        route = str(route_group.get("route", ""))
        panel_ids = _route_group_panel_ids(route_group)
        _validate_route_group_status(errors=errors, route=route, group=route_group)
        _validate_route_group_evidence(
            errors=errors,
            route=route,
            group=route_group,
            panel_ids=panel_ids,
        )
        certified_panel_ids.update(
            _validate_route_group_panel_routes(
                errors=errors,
                route=route,
                panel_ids=panel_ids,
                registry_panels=registry_panels,
            )
        )
    return certified_panel_ids


def _validate_evidence_required_panels(
    *,
    errors: list[str],
    registry_panels: dict[str, dict[str, Any]],
    certified_panel_ids: set[str],
) -> None:
    registry_evidence_panels = {
        panel_id
        for panel_id, panel in registry_panels.items()
        if panel.get("evidence_required") is True
    }
    missing_certified_panels = sorted(registry_evidence_panels - certified_panel_ids)
    if missing_certified_panels:
        errors.append(
            "certified_route_groups missing evidence-required panels: "
            f"{missing_certified_panels}"
        )


def _validate_rollout_checklist(*, errors: list[str], checklist: list[Any]) -> None:
    required_checklist_terms = {
        "panel registry",
        "sensitive-content",
        "supported-features",
        "dashboard",
        "browser proof",
        "residual",
    }
    checklist_text = " ".join(
        f"{item.get('step', '')} {item.get('required_evidence', '')}".lower()
        for item in checklist
        if isinstance(item, dict)
    )
    for term in required_checklist_terms:
        if term not in checklist_text:
            errors.append(f"rollout_checklist must cover {term}")


def _validate_validator_proof_cases(
    *, errors: list[str], validator_proof_cases: list[Any]
) -> None:
    proof_types = {
        str(case.get("proof_type"))
        for case in validator_proof_cases
        if isinstance(case, dict)
    }
    if "forbidden-label" not in proof_types:
        errors.append("validator_proof_cases must include forbidden-label proof")
    if "unimplemented-metric-reference" not in proof_types:
        errors.append(
            "validator_proof_cases must include unimplemented-metric-reference proof"
        )
    for case in validator_proof_cases:
        if not case.get("test_name") or not case.get("expected_failure"):
            errors.append("validator_proof_cases require test_name and expected_failure")


def _feature_status_map(observability_contract: dict[str, Any]) -> dict[str, str]:
    return {
        str(feature.get("feature_key")): str(feature.get("status"))
        for feature in observability_contract.get("supported_feature_keys", [])
        if isinstance(feature, dict)
    }


def _validate_rollout_feature_status(
    *, errors: list[str], feature_status: dict[str, str]
) -> None:
    rollout_feature_status = feature_status.get(
        "platform.analytics.observability.rollout_readiness"
    )
    if rollout_feature_status != "implemented":
        errors.append(
            "platform.analytics.observability.rollout_readiness must be implemented"
        )


def _validate_residual_scope(
    *,
    errors: list[str],
    residual_scope: list[Any],
    feature_status: dict[str, str],
) -> None:
    for residual in residual_scope:
        feature_key = str(residual.get("feature_key", ""))
        if residual.get("status") != "planned":
            errors.append(f"{feature_key}: residual status must remain planned")
        if feature_status.get(feature_key) != "planned":
            errors.append(
                f"{feature_key}: residual feature must exist in supported features "
                "with planned status"
            )
        for required_field in ("owner_repo", "blocker", "next_action"):
            if not residual.get(required_field):
                errors.append(f"{feature_key}: {required_field} is required")


def validate_rollout_readiness(
    *,
    observability_contract: dict[str, Any],
    rollout_contract: dict[str, Any],
    panel_registry: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    _validate_contract_identity(errors=errors, rollout_contract=rollout_contract)

    source_proof = rollout_contract.get("source_proof", {})
    _validate_source_proof(errors=errors, source_proof=source_proof)

    registry_panels = _registry_panels(panel_registry)
    certified_route_groups = rollout_contract.get("certified_route_groups", [])
    certified_panel_ids = _validate_certified_route_groups(
        errors=errors,
        certified_route_groups=certified_route_groups,
        registry_panels=registry_panels,
    )
    _validate_evidence_required_panels(
        errors=errors,
        registry_panels=registry_panels,
        certified_panel_ids=certified_panel_ids,
    )

    checklist = rollout_contract.get("rollout_checklist", [])
    _validate_rollout_checklist(errors=errors, checklist=checklist)

    _validate_validator_proof_cases(
        errors=errors,
        validator_proof_cases=rollout_contract.get("validator_proof_cases", []),
    )

    feature_status = _feature_status_map(observability_contract)
    _validate_rollout_feature_status(errors=errors, feature_status=feature_status)
    _validate_residual_scope(
        errors=errors,
        residual_scope=rollout_contract.get("residual_scope", []),
        feature_status=feature_status,
    )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate RFC-0108 analytics UI rollout readiness contract."
    )
    parser.add_argument(
        "--observability-contract",
        type=Path,
        default=DEFAULT_OBSERVABILITY_CONTRACT_PATH,
    )
    parser.add_argument(
        "--rollout-contract", type=Path, default=DEFAULT_ROLLOUT_CONTRACT_PATH
    )
    parser.add_argument("--panel-registry", type=Path, default=DEFAULT_PANEL_REGISTRY_PATH)
    args = parser.parse_args()

    errors = validate_rollout_readiness(
        observability_contract=_load_json(args.observability_contract),
        rollout_contract=_load_json(args.rollout_contract),
        panel_registry=_load_json(args.panel_registry),
    )
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Analytics UI rollout readiness validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
