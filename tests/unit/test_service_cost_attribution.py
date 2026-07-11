from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
import json
from pathlib import Path

import pytest

from automation.cost_attribution.application import build_service_cost_attribution
from automation.cost_attribution.domain import ServiceAllocationRequest
from automation.cost_attribution.infrastructure import JsonBillingExportAdapter


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _export_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "authority": "governed-finops-export",
        "exportType": "normalized_service_billing_export",
        "exportVersion": "2026-07",
        "exportedAtUtc": "2026-07-11T08:00:00Z",
        "billingPeriodStart": "2026-07-01",
        "billingPeriodEnd": "2026-07-31",
        "currency": "USD",
        "categoryCosts": {
            "compute": "100.00",
            "memory": "50.00",
            "database": "75.00",
            "network": "10.00",
            "storage": "20.00",
            "observability": "15.00",
            "shared_platform": "30.00",
        },
        "sourceTotal": "300.00",
        "completenessStatus": "complete",
        "freshnessStatus": "current",
        "partialPeriod": False,
        "lateAdjustment": False,
    }
    payload.update(overrides)
    return payload


def _adapter(tmp_path: Path, payload: dict[str, object]) -> JsonBillingExportAdapter:
    path = tmp_path / "normalized-export.json"
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return JsonBillingExportAdapter(path)


def _request(**overrides: object) -> ServiceAllocationRequest:
    values: dict[str, object] = {
        "repository": "lotus-idea",
        "service_id": "lotus-idea-api",
        "environment": "production-like",
        "region": "ap-southeast-1",
        "source_commit_sha": "a" * 40,
        "source_ref": "refs/heads/main",
        "pipeline_run_id": "run-123",
        "resource_observation_schema_version": "lotus-idea.service-resource-baseline.v1",
        "resource_observation_sha256": "b" * 64,
        "resource_observation_run_id": "resource-run-123",
        "shared_cost_numerator": Decimal("1"),
        "shared_cost_denominator": Decimal("3"),
    }
    values.update(overrides)
    return ServiceAllocationRequest(**values)  # type: ignore[arg-type]


def test_build_reconciles_rounding_residual_without_promoting_product_support(
    tmp_path: Path,
) -> None:
    artifact = build_service_cost_attribution(
        billing_export_port=_adapter(tmp_path, _export_payload()),
        request=_request(),
        generated_at_utc=datetime(2026, 7, 11, 9, 0, tzinfo=UTC),
    )

    assert artifact["schemaVersion"] == "lotus-platform.service-cost-attribution.v1"
    assert artifact["reconciliation"]["allocatedTotal"] == "100.00"
    assert artifact["reconciliation"]["expectedWeightedTotal"] == "100.00"
    assert artifact["reconciliation"]["variance"] == "0.00"
    assert (
        artifact["sharedCostAllocation"]["residualHandling"]
        == "assign_to_shared_platform"
    )
    assert artifact["costAttributionReconciled"] is True
    assert artifact["costAttributionCertified"] is False
    assert artifact["certificationBlockers"] == ["artifact_attestation_missing"]
    assert artifact["supportedFeaturePromoted"] is False
    serialized = json.dumps(artifact)
    for forbidden in (
        "tenant",
        "client",
        "portfolio",
        "candidate",
        "account",
        "credential",
    ):
        assert forbidden not in serialized.lower()


@pytest.mark.parametrize(
    ("overrides", "blocker"),
    [
        ({"completenessStatus": "partial"}, "billing_export_incomplete"),
        ({"freshnessStatus": "stale"}, "billing_export_stale"),
        ({"partialPeriod": True}, "partial_billing_period"),
    ],
)
def test_incomplete_stale_or_partial_export_remains_blocked(
    tmp_path: Path, overrides: dict[str, object], blocker: str
) -> None:
    artifact = build_service_cost_attribution(
        billing_export_port=_adapter(tmp_path, _export_payload(**overrides)),
        request=_request(),
        generated_at_utc=datetime(2026, 7, 11, 9, 0, tzinfo=UTC),
    )

    assert artifact["costAttributionCertified"] is False
    assert blocker in artifact["certificationBlockers"]
    assert artifact["claimPosture"] == "reconciliation_blocked"


def test_negative_credit_is_reconciled_with_decimal_arithmetic(tmp_path: Path) -> None:
    payload = _export_payload(
        categoryCosts={
            "compute": "100.00",
            "memory": "50.00",
            "database": "75.00",
            "network": "10.00",
            "storage": "20.00",
            "observability": "15.00",
            "shared_platform": "-20.00",
        },
        sourceTotal="250.00",
    )
    artifact = build_service_cost_attribution(
        billing_export_port=_adapter(tmp_path, payload),
        request=_request(
            shared_cost_numerator=Decimal("1"), shared_cost_denominator=Decimal("1")
        ),
        generated_at_utc=datetime(2026, 7, 11, 9, 0, tzinfo=UTC),
    )

    assert artifact["reconciliation"]["allocatedTotal"] == "250.00"
    shared = next(
        item
        for item in artifact["allocations"]
        if item["category"] == "shared_platform"
    )
    assert shared["amount"] == "-20.00"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"sourceTotal": 300.0}, "canonical two-decimal"),
        ({"currency": "usd"}, "uppercase ISO 4217"),
        ({"partialPeriod": "false"}, "must be a boolean"),
        ({"accountId": "forbidden"}, "closed normalized envelope"),
    ],
)
def test_adapter_rejects_ambiguous_or_sensitive_export_shapes(
    tmp_path: Path, mutation: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        _adapter(tmp_path, _export_payload(**mutation)).load()


def test_adapter_rejects_duplicate_json_fields(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text('{"authority":"one","authority":"two"}', encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate JSON field"):
        JsonBillingExportAdapter(path).load()


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"shared_cost_denominator": Decimal("0")}, "denominator must be positive"),
        ({"shared_cost_numerator": Decimal("-1")}, "numerator must be between"),
        ({"shared_cost_numerator": Decimal("4")}, "numerator must be between"),
        ({"shared_cost_numerator": Decimal("NaN")}, "numerator must be between"),
        ({"resource_observation_sha256": "bad"}, "digest must be lowercase SHA-256"),
    ],
)
def test_allocation_request_rejects_invalid_weight_or_provenance(
    overrides: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        _request(**overrides)


def test_schema_is_closed_and_preserves_uncertified_generation_posture() -> None:
    schema = json.loads(
        (
            REPOSITORY_ROOT
            / "platform-contracts"
            / "cost-attribution"
            / "service-cost-attribution.schema.json"
        ).read_text(encoding="utf-8")
    )

    assert schema["additionalProperties"] is False
    assert schema["properties"]["costAttributionCertified"] == {"const": False}
    assert schema["properties"]["supportedFeaturePromoted"] == {"const": False}
    assert schema["properties"]["allocations"]["minItems"] == 7
    assert schema["properties"]["allocations"]["maxItems"] == 7
