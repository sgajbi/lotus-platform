from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ALLOWED_CLASSIFICATIONS = {
    "IMPLEMENTATION_BACKED",
    "BACKEND_BACKED_UI_PENDING",
    "DEGRADED_SUPPORTED",
    "PLANNED_RFC",
    "UNSUPPORTED",
}
CLIENT_FACING_MATERIALS = {
    "DEMO_SCRIPT",
    "SCREENSHOT",
    "RFP_PACK",
    "SECURITY_PACK",
    "ONE_PAGER",
    "ARCHITECTURE_DECK",
    "ROI_STORY",
    "LINKEDIN_DRAFT",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _issue(issues: list[str], path: Path, message: str) -> None:
    issues.append(f"{path}: {message}")


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _validate_register_header(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
) -> None:
    if payload.get("contract_id") != "supported-claim-register":
        _issue(issues, path, "contract_id must be 'supported-claim-register'")
    if not re.fullmatch(
        r"^[0-9]+\.[0-9]+\.[0-9]+$", str(payload.get("contract_version") or "")
    ):
        _issue(issues, path, "contract_version must be semver")
    if not re.fullmatch(r"^RFC-[0-9]{4}$", str(payload.get("governed_by_rfc") or "")):
        _issue(issues, path, "governed_by_rfc must use RFC-0000 format")
    if not re.fullmatch(
        r"^lotus-[a-z0-9-]+$", str(payload.get("owner_repository") or "")
    ):
        _issue(issues, path, "owner_repository must be a lotus repository name")
    if not _non_empty_string(payload.get("scenario_id")):
        _issue(issues, path, "scenario_id must be a non-empty string")
    if not _non_empty_string(payload.get("primary_portfolio_id")):
        _issue(issues, path, "primary_portfolio_id must be a non-empty string")
    if not _non_empty_string(payload.get("proof_marker")):
        _issue(issues, path, "proof_marker must be a non-empty string")

    taxonomy = set(_string_list(payload.get("claim_taxonomy")))
    if taxonomy != ALLOWED_CLASSIFICATIONS:
        _issue(
            issues,
            path,
            "claim_taxonomy must include every supported classification exactly once",
        )


def _validate_register_front_office_policy(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
) -> None:
    front_office = payload.get("front_office_validation")
    if not isinstance(front_office, dict):
        _issue(issues, path, "front_office_validation must be an object")
    else:
        markers = _string_list(front_office.get("required_evidence_markers"))
        if payload.get("proof_marker") not in markers:
            _issue(
                issues, path, "proof_marker must appear in required_evidence_markers"
            )
        if front_office.get("requires_browser_validation") is True and not _string_list(
            front_office.get("required_panels")
        ):
            _issue(
                issues, path, "browser validation requires at least one required panel"
            )


def _validate_register_artifact_policy(
    issues: list[str],
    path: Path,
    payload: dict[str, Any],
) -> None:
    artifact_policy = payload.get("artifact_policy")
    if not isinstance(artifact_policy, dict):
        _issue(issues, path, "artifact_policy must be an object")
    else:
        if not _string_list(artifact_policy.get("commit_allowed_artifacts")):
            _issue(
                issues,
                path,
                "commit_allowed_artifacts must be a non-empty string array",
            )
        if not _string_list(artifact_policy.get("local_only_artifacts")):
            _issue(
                issues, path, "local_only_artifacts must be a non-empty string array"
            )
        sensitive_rules = " ".join(
            _string_list(artifact_policy.get("sensitive_artifact_rules"))
        )
        for forbidden_word in ("secret", "token", "prompt"):
            if forbidden_word not in sensitive_rules.lower():
                _issue(
                    issues,
                    path,
                    f"sensitive_artifact_rules must mention {forbidden_word}",
                )


def _validate_claim(
    issues: list[str],
    path: Path,
    *,
    index: int,
    claim: dict[str, Any],
    claim_ids: set[str],
) -> None:
    claim_id = str(claim.get("claim_id") or "")
    if not re.fullmatch(r"^[a-z][a-z0-9_]+$", claim_id):
        _issue(issues, path, f"claims[{index}].claim_id must be snake_case")
    elif claim_id in claim_ids:
        _issue(issues, path, f"claims[{index}].claim_id duplicates {claim_id}")
    claim_ids.add(claim_id)

    classification = str(claim.get("classification") or "")
    if classification not in ALLOWED_CLASSIFICATIONS:
        _issue(issues, path, f"claims[{index}].classification is not supported")

    evidence_refs = _string_list(claim.get("evidence_refs"))
    proof_requirements = _string_list(claim.get("proof_requirements"))
    allowed_materials = set(_string_list(claim.get("allowed_materials")))
    wording_rules = _string_list(claim.get("wording_rules"))

    if not wording_rules:
        _issue(issues, path, f"claims[{index}].wording_rules must be non-empty")
    if classification == "IMPLEMENTATION_BACKED" and (
        not evidence_refs or not proof_requirements
    ):
        _issue(
            issues,
            path,
            f"claims[{index}] implementation-backed claims require evidence and proof",
        )
    if classification in {"PLANNED_RFC", "UNSUPPORTED"} and (
        allowed_materials & CLIENT_FACING_MATERIALS
    ):
        _issue(
            issues,
            path,
            f"claims[{index}] planned/unsupported claims cannot use client-facing materials",
        )
    if (
        classification == "BACKEND_BACKED_UI_PENDING"
        and "SCREENSHOT" in allowed_materials
    ):
        _issue(
            issues,
            path,
            f"claims[{index}] backend-only claims cannot be used for screenshots",
        )
    if not _non_empty_string(claim.get("promotion_gate")):
        _issue(issues, path, f"claims[{index}].promotion_gate must be non-empty")


def _validate_claims(
    issues: list[str],
    path: Path,
    claims: object,
) -> None:
    if not isinstance(claims, list) or not claims:
        _issue(issues, path, "claims must be a non-empty array")
        return

    claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            _issue(issues, path, f"claims[{index}] must be an object")
            continue
        _validate_claim(
            issues,
            path,
            index=index,
            claim=claim,
            claim_ids=claim_ids,
        )


def validate_supported_claim_register(path: Path, payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    _validate_register_header(issues, path, payload)
    _validate_register_front_office_policy(issues, path, payload)
    _validate_register_artifact_policy(issues, path, payload)
    _validate_claims(issues, path, payload.get("claims"))

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Lotus supported-claim register."
    )
    parser.add_argument("--path", required=True, type=Path)
    args = parser.parse_args(argv)

    issues = validate_supported_claim_register(args.path, _load_json(args.path))
    if issues:
        for issue in issues:
            print(issue)
        return 1
    print(f"Supported-claim register validation passed: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
