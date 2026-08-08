from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = ROOT / "automation" / "validate_technology_governance_policy.py"
POLICY_PATH = (
    ROOT
    / "platform-contracts"
    / "technology-governance"
    / "lotus-technology-governance-policy.v1.json"
)
VULNERABILITY_EXCEPTION_EXAMPLE_PATH = (
    ROOT
    / "platform-contracts"
    / "vulnerability-exceptions"
    / "examples"
    / "lotus-platform-vulnerability-exception-register.valid.json"
)


def _validator():
    spec = importlib.util.spec_from_file_location(
        "validate_technology_governance_policy",
        VALIDATOR_PATH,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def _exception_register() -> dict:
    return json.loads(VULNERABILITY_EXCEPTION_EXAMPLE_PATH.read_text(encoding="utf-8"))


def test_technology_governance_policy_accepts_canonical_contract() -> None:
    validator = _validator()

    errors = validator.validate_policy_path(as_of_date=validator.date(2026, 8, 8))

    assert errors == []


def test_schema_rejects_unknown_policy_fields() -> None:
    validator = _validator()
    policy = _policy()
    policy["temporary_note"] = "not governed"

    errors = validator.validate_policy(policy, as_of_date=validator.date(2026, 8, 8))

    assert any("Additional properties are not allowed" in error for error in errors)


def test_approved_default_rejects_missing_ga_and_beta_exclusion() -> None:
    validator = _validator()
    policy = _policy()
    posture = policy["default_technology_posture"]
    posture["required_criteria"].remove("general_availability")
    posture["excluded_by_default"].remove("beta")

    errors = validator.validate_policy(policy, as_of_date=validator.date(2026, 8, 8))

    assert any("missing required values: general_availability" in error for error in errors)
    assert any("missing required values: beta" in error for error in errors)


def test_restricted_and_prohibited_states_cannot_allow_default_production_use() -> None:
    validator = _validator()
    policy = _policy()
    states = {entry["state"]: entry for entry in policy["technology_states"]}
    states["restricted_exception"]["production_use_allowed"] = True
    states["prohibited"]["requires_exception"] = True

    errors = validator.validate_policy(policy, as_of_date=validator.date(2026, 8, 8))

    assert any("restricted_exception technology must require an exception" in error for error in errors)
    assert any("prohibited technology must not allow production use" in error for error in errors)


def test_dependency_evidence_requires_locked_inventory_sbom_and_scan() -> None:
    validator = _validator()
    policy = _policy()
    artifacts = policy["dependency_evidence_policy"]["required_artifacts"]
    artifacts.remove("locked_manifest")
    artifacts.remove("runtime_sbom")
    artifacts.remove("vulnerability_scan")

    errors = validator.validate_policy(policy, as_of_date=validator.date(2026, 8, 8))

    assert any("locked_manifest" in error for error in errors)
    assert any("runtime_sbom" in error for error in errors)
    assert any("vulnerability_scan" in error for error in errors)


def test_container_image_evidence_requires_digest_sbom_signature_and_fresh_scan() -> None:
    validator = _validator()
    policy = _policy()
    image_policy = policy["container_image_evidence_policy"]
    image_policy["required_identity_fields"].remove("image_digest")
    image_policy["required_artifacts"].remove("image_sbom")
    image_policy["required_artifacts"].remove("signature")
    image_policy["max_scan_age_days"] = 45

    errors = validator.validate_policy(policy, as_of_date=validator.date(2026, 8, 8))

    assert any("image_digest" in error for error in errors)
    assert any("image_sbom" in error for error in errors)
    assert any("signature" in error for error in errors)
    assert any("max_scan_age_days must be <= 30" in error for error in errors)


def test_known_exploited_vulnerability_policy_cannot_be_exception_based() -> None:
    validator = _validator()
    policy = _policy()
    known_exploited = next(
        entry
        for entry in policy["vulnerability_severity_policy"]
        if entry["class"] == "known_exploited"
    )
    known_exploited["exception_allowed"] = True

    errors = validator.validate_policy(policy, as_of_date=validator.date(2026, 8, 8))

    assert any("known_exploited vulnerability policy must not allow exceptions" in error for error in errors)


def test_exception_policy_fails_closed_without_scanner_truth() -> None:
    validator = _validator()
    policy = _policy()
    policy["exception_policy"]["fail_closed_when_scan_unavailable"] = False
    policy["exception_policy"]["permanent_suppressions_allowed"] = True

    errors = validator.validate_policy(policy, as_of_date=validator.date(2026, 8, 8))

    assert any("fail_closed_when_scan_unavailable must be true" in error for error in errors)
    assert any("permanent_suppressions_allowed must be false" in error for error in errors)


def test_lens_routing_must_cover_dependency_image_vulnerability_and_rollout_lenses() -> None:
    validator = _validator()
    policy = _policy()
    policy["lens_routing"] = [
        entry
        for entry in policy["lens_routing"]
        if entry["lens"] != "lens/vulnerability-management"
    ]

    errors = validator.validate_policy(policy, as_of_date=validator.date(2026, 8, 8))

    assert any("lens/vulnerability-management" in error for error in errors)


def test_rollout_must_include_platform_and_core_pilots() -> None:
    validator = _validator()
    policy = _policy()
    policy["rollout"]["pilot_repositories"] = ["lotus-platform"]

    errors = validator.validate_policy(policy, as_of_date=validator.date(2026, 8, 8))

    assert any("rollout.pilot_repositories missing lotus-core" in error for error in errors)


def test_expired_vulnerability_exception_register_blocks_policy_validation(tmp_path: Path) -> None:
    validator = _validator()
    register = _exception_register()
    register["exceptions"][0]["expiry_date"] = "2026-07-01"
    register_path = tmp_path / "expired-exception-register.json"
    register_path.write_text(json.dumps(register), encoding="utf-8")

    errors = validator.validate_policy_path(
        exception_register_paths=[register_path],
        as_of_date=validator.date(2026, 8, 8),
    )

    assert any("approved exception expired on 2026-07-01" in error for error in errors)


def test_report_only_cli_suppresses_non_zero_exit_for_policy_findings(tmp_path: Path) -> None:
    validator = _validator()
    policy = _policy()
    policy["container_image_evidence_policy"]["max_scan_age_days"] = 45
    policy_path = tmp_path / "stale-scan-policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")

    exit_code = validator.main(
        [
            "--policy",
            str(policy_path),
            "--as-of-date",
            "2026-08-08",
            "--report-only",
        ]
    )

    assert exit_code == 0


def test_cli_returns_failure_for_policy_findings(tmp_path: Path) -> None:
    validator = _validator()
    policy = _policy()
    policy["container_image_evidence_policy"]["max_scan_age_days"] = 45
    policy_path = tmp_path / "stale-scan-policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")

    exit_code = validator.main(
        [
            "--policy",
            str(policy_path),
            "--as-of-date",
            "2026-08-08",
        ]
    )

    assert exit_code == 1
