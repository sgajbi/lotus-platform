from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(
    0,
    str(ROOT / "codex" / "skills" / "lotus-ci-enforcement-governance" / "scripts"),
)

from endpoint_example_parity import (  # noqa: E402
    ALLOWED_NORMALIZATION_STRATEGIES,
    CONTRACT_VERSION,
    FAILURE_CODES,
    FORBIDDEN_NORMALIZATION_TOKENS,
    compare_endpoint_examples,
)


CONTRACT_PATH = (
    ROOT
    / "platform-contracts"
    / "api-governance"
    / "endpoint-example-parity-contract.v1.json"
)


def _codes(documented: object, runtime: object, **kwargs: object) -> set[str]:
    return {
        violation.code
        for violation in compare_endpoint_examples(documented, runtime, **kwargs)
    }


def test_machine_readable_contract_matches_comparator_vocabulary() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    assert contract["schemaVersion"] == CONTRACT_VERSION
    assert (ROOT / contract["standard"]).is_file()
    assert (ROOT / contract["referenceImplementation"]).is_file()
    assert set(contract["normalization"]["allowedStrategies"]) == set(
        ALLOWED_NORMALIZATION_STRATEGIES
    )
    assert set(contract["normalization"]["forbiddenFieldTokens"]) == set(
        FORBIDDEN_NORMALIZATION_TOKENS
    )
    assert set(contract["failureCodes"]) == set(FAILURE_CODES)


def test_exact_structural_comparison_ignores_object_key_order() -> None:
    documented = {"status": "blocked", "blockers": ["runtime_missing"]}
    runtime = {"blockers": ["runtime_missing"], "status": "blocked"}

    assert compare_endpoint_examples(documented, runtime) == ()


@pytest.mark.parametrize(
    ("documented", "runtime", "expected_code"),
    [
        (
            {"status": "ready"},
            {"status": "ready", "version": "v1"},
            "missing_documented_field",
        ),
        (
            {"status": "ready", "legacy": True},
            {"status": "ready"},
            "stale_documented_field",
        ),
        ({"ready": True}, {"ready": 1}, "type_mismatch"),
        ({"count": 1}, {"count": 1.0}, "type_mismatch"),
        (
            {"blockers": ["a", "b"]},
            {"blockers": ["b", "a"]},
            "value_mismatch",
        ),
        ({"status": "ready"}, {"status": "blocked"}, "value_mismatch"),
        ({"value": None}, {}, "stale_documented_field"),
    ],
)
def test_contract_drift_fails_with_stable_codes(
    documented: object,
    runtime: object,
    expected_code: str,
) -> None:
    assert expected_code in _codes(documented, runtime)


def test_lotus_idea_ai_readiness_regression_detects_stale_blocker_and_field() -> None:
    documented = {
        "lotusAiRunAttestationAvailable": True,
        "certificationBlockers": ["lotus_ai_run_attestation_mainline_proof_missing"],
    }
    runtime = {
        "lotusAiRunAttestationAvailable": True,
        "metadataEnvelopeVersion": "v1",
        "certificationBlockers": [],
    }

    violations = compare_endpoint_examples(documented, runtime)

    assert (
        "missing_documented_field",
        "/metadataEnvelopeVersion",
    ) in {(violation.code, violation.pointer) for violation in violations}
    assert (
        "array_length_mismatch",
        "/certificationBlockers",
    ) in {(violation.code, violation.pointer) for violation in violations}


def test_dynamic_values_require_valid_explicit_normalization() -> None:
    documented = {
        "generatedAtUtc": datetime(2026, 7, 13, 1, 0, tzinfo=UTC).isoformat(),
        "requestId": "e6ef1f39-ecf0-47ec-a12f-c1b59ba14fa4",
        "status": "blocked",
    }
    runtime = {
        "generatedAtUtc": datetime(2026, 7, 13, 2, 0, tzinfo=UTC).isoformat(),
        "requestId": "16cd8561-f702-48e4-a1ce-e75f3431dad2",
        "status": "blocked",
    }

    violations = compare_endpoint_examples(
        documented,
        runtime,
        normalizations=(
            {"pointer": "/generatedAtUtc", "strategy": "rfc3339"},
            {"pointer": "/requestId", "strategy": "uuid"},
        ),
    )

    assert violations == ()


@pytest.mark.parametrize(
    ("rule", "expected_code"),
    [
        (
            {"pointer": "generatedAtUtc", "strategy": "rfc3339"},
            "invalid_normalization_pointer",
        ),
        (
            {"pointer": "/generated~2AtUtc", "strategy": "rfc3339"},
            "invalid_normalization_pointer",
        ),
        (
            {"pointer": "/generatedAtUtc", "strategy": "anything"},
            "unsupported_normalization_strategy",
        ),
        (
            {"pointer": "/missing", "strategy": "non_empty_string"},
            "normalization_target_missing",
        ),
        (
            {"pointer": "/generatedAtUtc", "strategy": "uuid"},
            "normalization_value_invalid",
        ),
        (
            {"pointer": "/readinessStatus", "strategy": "non_empty_string"},
            "forbidden_governance_normalization",
        ),
        (
            {"pointer": "/certificationBlockers/0", "strategy": "non_empty_string"},
            "forbidden_governance_normalization",
        ),
    ],
)
def test_normalization_policy_fails_closed(
    rule: dict[str, str],
    expected_code: str,
) -> None:
    documented = {
        "generatedAtUtc": "2026-07-13T01:00:00+00:00",
        "readinessStatus": "blocked",
        "certificationBlockers": ["runtime_missing"],
    }
    runtime = {
        "generatedAtUtc": "2026-07-13T02:00:00+00:00",
        "readinessStatus": "blocked",
        "certificationBlockers": ["runtime_missing"],
    }

    assert expected_code in _codes(documented, runtime, normalizations=(rule,))


def test_duplicate_normalization_pointer_is_rejected() -> None:
    payload = {"requestId": "e6ef1f39-ecf0-47ec-a12f-c1b59ba14fa4"}
    rules = (
        {"pointer": "/requestId", "strategy": "uuid"},
        {"pointer": "/requestId", "strategy": "uuid"},
    )

    assert "duplicate_normalization_pointer" in _codes(
        payload,
        payload,
        normalizations=rules,
    )


def test_non_object_normalization_rule_is_rejected_without_raising() -> None:
    payload = {"requestId": "e6ef1f39-ecf0-47ec-a12f-c1b59ba14fa4"}

    assert "invalid_normalization_rule" in _codes(
        payload,
        payload,
        normalizations=("/requestId",),
    )


@pytest.mark.parametrize(
    ("rule", "expected_code"),
    [
        ({"pointer": 7, "strategy": "uuid"}, "invalid_normalization_pointer"),
        (
            {"pointer": "/requestId", "strategy": ["uuid"]},
            "unsupported_normalization_strategy",
        ),
    ],
)
def test_non_string_normalization_fields_are_rejected_without_raising(
    rule: dict[str, object],
    expected_code: str,
) -> None:
    payload = {"requestId": "e6ef1f39-ecf0-47ec-a12f-c1b59ba14fa4"}

    assert expected_code in _codes(payload, payload, normalizations=(rule,))


def test_violation_messages_do_not_echo_values() -> None:
    secret_like_value = "customer-specific-value"

    violations = compare_endpoint_examples(
        {"status": secret_like_value},
        {"status": "other"},
    )

    assert violations
    assert all(secret_like_value not in violation.detail for violation in violations)
