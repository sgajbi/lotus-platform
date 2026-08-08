from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "platform-contracts" / "technology-governance"
POLICY_PATH = CONTRACT_DIR / "lotus-technology-governance-policy.v1.json"
SCHEMA_PATH = CONTRACT_DIR / "technology-governance-policy.schema.json"
VULNERABILITY_EXCEPTION_EXAMPLES = (
    ROOT / "platform-contracts" / "vulnerability-exceptions" / "examples"
)

if str(ROOT / "automation") not in sys.path:
    sys.path.insert(0, str(ROOT / "automation"))

from json_contract_validation import validate_json_schema_subset_document  # noqa: E402
from validate_vulnerability_exception_register import (  # noqa: E402
    validate_register_paths as validate_vulnerability_exception_register_paths,
)


REQUIRED_STATES = {"approved_default", "restricted_exception", "prohibited"}
EXCLUDED_RELEASE_PHASES = {
    "alpha",
    "beta",
    "preview",
    "release_candidate",
    "experimental",
    "incubating",
    "end_of_life",
    "novelty_driven_major_upgrade",
}
REQUIRED_DEFAULT_CRITERIA = {
    "general_availability",
    "active_maintenance",
    "broad_adoption",
    "credible_security_patch_channel",
    "well_documented",
    "broad_training_and_tooling_support",
    "license_compatible",
}
REQUIRED_DEPENDENCY_ARTIFACTS = {
    "direct_dependency_manifest",
    "locked_manifest",
    "transitive_dependency_inventory",
    "runtime_sbom",
    "license_inventory",
    "vulnerability_scan",
}
REQUIRED_CONTAINER_IDENTITY_FIELDS = {
    "image_repository",
    "image_digest",
    "git_sha",
    "source_repository",
    "build_pipeline",
    "build_timestamp",
    "architecture",
}
REQUIRED_CONTAINER_ARTIFACTS = {
    "oci_labels",
    "image_sbom",
    "signature",
    "provenance_attestation",
    "scan_receipt",
    "base_image_support_evidence",
    "runtime_smoke_receipt",
}
REQUIRED_SEVERITY_CLASSES = {"known_exploited", "critical", "high", "medium", "low"}
REQUIRED_LENSES = {
    "lens/dependency-hygiene",
    "lens/environment-supply-chain-provenance",
    "lens/vulnerability-management",
    "lens/release-rollout-compatibility",
}


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: policy must be a JSON object")
    return payload


def validate_policy_path(
    path: Path = POLICY_PATH,
    *,
    exception_register_paths: list[Path] | None = None,
    as_of_date: date | None = None,
) -> list[str]:
    try:
        policy = load_policy(path)
    except (json.JSONDecodeError, ValueError) as exc:
        return [f"{path}: {exc}"]
    return validate_policy(
        policy,
        document_name=str(path),
        exception_register_paths=exception_register_paths,
        as_of_date=as_of_date,
    )


def validate_policy(
    policy: dict[str, Any],
    *,
    document_name: str = "policy",
    exception_register_paths: list[Path] | None = None,
    as_of_date: date | None = None,
) -> list[str]:
    errors = validate_json_schema_subset_document(
        SCHEMA_PATH,
        policy,
        document_name=document_name,
    )

    try:
        _validate_default_posture(policy, errors)
        _validate_technology_states(policy, errors)
        _validate_dependency_evidence(policy, errors)
        _validate_container_image_evidence(policy, errors)
        _validate_vulnerability_policy(policy, errors)
        _validate_exception_policy(policy, errors)
        _validate_lens_routing(policy, errors)
        _validate_rollout(policy, errors)
    except (KeyError, TypeError) as exc:
        errors.append(
            f"{document_name}: semantic validation could not complete after schema findings: {exc}"
        )

    exception_paths = exception_register_paths
    if exception_paths is None:
        exception_paths = sorted(VULNERABILITY_EXCEPTION_EXAMPLES.glob("*.json"))
    errors.extend(
        validate_vulnerability_exception_register_paths(
            exception_paths,
            as_of_date=as_of_date,
        )
    )
    return errors


def _validate_default_posture(policy: dict[str, Any], errors: list[str]) -> None:
    posture = policy["default_technology_posture"]
    criteria = set(posture["required_criteria"])
    excluded = set(posture["excluded_by_default"])
    missing_criteria = REQUIRED_DEFAULT_CRITERIA - criteria
    missing_exclusions = EXCLUDED_RELEASE_PHASES - excluded
    if missing_criteria:
        errors.append(
            "default_technology_posture.required_criteria missing required values: "
            + ", ".join(sorted(missing_criteria))
        )
    if missing_exclusions:
        errors.append(
            "default_technology_posture.excluded_by_default missing required values: "
            + ", ".join(sorted(missing_exclusions))
        )


def _validate_technology_states(policy: dict[str, Any], errors: list[str]) -> None:
    states = {state["state"]: state for state in policy["technology_states"]}
    missing_states = REQUIRED_STATES - set(states)
    if missing_states:
        errors.append(
            "technology_states missing required states: "
            + ", ".join(sorted(missing_states))
        )
        return

    approved = states["approved_default"]
    restricted = states["restricted_exception"]
    prohibited = states["prohibited"]
    if approved["requires_exception"] or not approved["production_use_allowed"]:
        errors.append(
            "approved_default technology must allow production use without an exception"
        )
    if not restricted["requires_exception"] or restricted["production_use_allowed"]:
        errors.append(
            "restricted_exception technology must require an exception and remain non-production by default"
        )
    if prohibited["requires_exception"] or prohibited["production_use_allowed"]:
        errors.append(
            "prohibited technology must not allow production use or exception-based promotion"
        )


def _validate_dependency_evidence(policy: dict[str, Any], errors: list[str]) -> None:
    evidence = policy["dependency_evidence_policy"]
    artifacts = set(evidence["required_artifacts"])
    missing = REQUIRED_DEPENDENCY_ARTIFACTS - artifacts
    if missing:
        errors.append(
            "dependency_evidence_policy.required_artifacts missing required values: "
            + ", ".join(sorted(missing))
        )
    if evidence["inventory_source"] != "locked_manifests":
        errors.append("dependency_evidence_policy.inventory_source must be locked_manifests")


def _validate_container_image_evidence(policy: dict[str, Any], errors: list[str]) -> None:
    evidence = policy["container_image_evidence_policy"]
    identity_fields = set(evidence["required_identity_fields"])
    artifacts = set(evidence["required_artifacts"])
    missing_identity = REQUIRED_CONTAINER_IDENTITY_FIELDS - identity_fields
    missing_artifacts = REQUIRED_CONTAINER_ARTIFACTS - artifacts
    if evidence["identity_source"] != "immutable_digest":
        errors.append("container_image_evidence_policy.identity_source must be immutable_digest")
    if evidence["mutable_tag_posture"] != "non_certifying":
        errors.append("container_image_evidence_policy.mutable_tag_posture must be non_certifying")
    if evidence["max_scan_age_days"] > 30:
        errors.append("container_image_evidence_policy.max_scan_age_days must be <= 30")
    if missing_identity:
        errors.append(
            "container_image_evidence_policy.required_identity_fields missing required values: "
            + ", ".join(sorted(missing_identity))
        )
    if missing_artifacts:
        errors.append(
            "container_image_evidence_policy.required_artifacts missing required values: "
            + ", ".join(sorted(missing_artifacts))
        )


def _validate_vulnerability_policy(policy: dict[str, Any], errors: list[str]) -> None:
    severities = {entry["class"]: entry for entry in policy["vulnerability_severity_policy"]}
    missing = REQUIRED_SEVERITY_CLASSES - set(severities)
    if missing:
        errors.append(
            "vulnerability_severity_policy missing required classes: "
            + ", ".join(sorted(missing))
        )
        return

    known_exploited = severities["known_exploited"]
    critical = severities["critical"]
    high = severities["high"]
    if known_exploited["exception_allowed"]:
        errors.append("known_exploited vulnerability policy must not allow exceptions")
    if "block_release" not in known_exploited["release_behavior"]:
        errors.append("known_exploited vulnerability policy must block release")
    for severity_name, entry in (("critical", critical), ("high", high)):
        if not entry["exception_allowed"]:
            errors.append(f"{severity_name} vulnerability policy must allow approved exceptions")
        if "block_release" not in entry["release_behavior"]:
            errors.append(f"{severity_name} vulnerability policy must block release without proof")


def _validate_exception_policy(policy: dict[str, Any], errors: list[str]) -> None:
    exception_policy = policy["exception_policy"]
    if not exception_policy["fail_closed_when_scan_unavailable"]:
        errors.append("exception_policy.fail_closed_when_scan_unavailable must be true")
    if exception_policy["permanent_suppressions_allowed"]:
        errors.append("exception_policy.permanent_suppressions_allowed must be false")
    required = set(exception_policy["required_fields"])
    for field in (
        "canonical_github_issue",
        "accountable_owner",
        "component_identity",
        "version_or_digest",
        "severity",
        "runtime_exposure",
        "exploitability",
        "expiry_date",
        "planned_fix",
        "approval_evidence",
        "removal_proof",
    ):
        if field not in required:
            errors.append(f"exception_policy.required_fields missing {field}")


def _validate_lens_routing(policy: dict[str, Any], errors: list[str]) -> None:
    lenses = {entry["lens"] for entry in policy["lens_routing"]}
    missing = REQUIRED_LENSES - lenses
    if missing:
        errors.append(
            "lens_routing missing required lenses: " + ", ".join(sorted(missing))
        )


def _validate_rollout(policy: dict[str, Any], errors: list[str]) -> None:
    rollout = policy["rollout"]
    pilot_repositories = set(rollout["pilot_repositories"])
    for repository in ("lotus-platform", "lotus-core"):
        if repository not in pilot_repositories:
            errors.append(f"rollout.pilot_repositories missing {repository}")
    if rollout["lane_posture"] == "blocking":
        promotion = rollout["promotion_requirement"].lower()
        for term in ("baseline", "exception", "exact-sha"):
            if term not in promotion:
                errors.append(
                    f"rollout.promotion_requirement must cite {term} before blocking promotion"
                )


def _parse_as_of_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be YYYY-MM-DD") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Lotus technology maturity and vulnerability posture policy."
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=POLICY_PATH,
        help="Technology-governance policy JSON file to validate.",
    )
    parser.add_argument(
        "--exception-register",
        action="append",
        type=Path,
        dest="exception_registers",
        help="Vulnerability exception register JSON file to validate with the policy. Defaults to checked-in examples.",
    )
    parser.add_argument(
        "--as-of-date",
        type=_parse_as_of_date,
        default=date.today(),
        help="As-of date for exception expiry checks, in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Print findings but return success so repositories can measure before lane promotion.",
    )
    args = parser.parse_args(argv)

    errors = validate_policy_path(
        args.policy,
        exception_register_paths=args.exception_registers,
        as_of_date=args.as_of_date,
    )
    if errors:
        print("Technology governance policy findings:")
        for error in errors:
            print(f"- {error}")
        if args.report_only:
            print("Result: report-only findings emitted; exit code suppressed.")
            return 0
        return 1

    print(f"Technology governance policy validation passed: {args.policy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
