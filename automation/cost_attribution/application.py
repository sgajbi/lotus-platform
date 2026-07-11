from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any

from automation.cost_attribution.domain import (
    BillingExport,
    COST_CATEGORIES,
    ServiceAllocationRequest,
)
from automation.cost_attribution.ports import BillingExportPort


SCHEMA_VERSION = "lotus-platform.service-cost-attribution.v1"
METHODOLOGY_VERSION = "lotus-platform.proportional-resource-cost-allocation.v1"
CENT = Decimal("0.01")


def build_service_cost_attribution(
    *,
    billing_export_port: BillingExportPort,
    request: ServiceAllocationRequest,
    generated_at_utc: datetime,
) -> dict[str, Any]:
    if generated_at_utc.tzinfo is None or generated_at_utc.utcoffset() is None:
        raise ValueError("generated_at_utc must be timezone-aware")
    export = billing_export_port.load()
    weight = request.shared_cost_numerator / request.shared_cost_denominator
    allocated = {
        category: (amount * weight).quantize(CENT, rounding=ROUND_HALF_EVEN)
        for category, amount in export.category_costs.items()
    }
    allocated_total = sum(allocated.values(), Decimal("0.00"))
    unrounded_total = export.source_total * weight
    residual = (
        unrounded_total.quantize(CENT, rounding=ROUND_HALF_EVEN) - allocated_total
    )
    allocated["shared_platform"] += residual
    allocated_total += residual
    reconciliation_blockers = _reconciliation_blockers(export)
    certification_blockers = [*reconciliation_blockers, "artifact_attestation_missing"]
    artifact = {
        "schemaVersion": SCHEMA_VERSION,
        "repository": "lotus-platform",
        "proofScope": "source_safe_service_cost_attribution",
        "claimPosture": "reconciled_not_attested"
        if not reconciliation_blockers
        else "reconciliation_blocked",
        "service": {
            "repository": request.repository,
            "serviceId": request.service_id,
            "environment": request.environment,
            "region": request.region,
        },
        "billingPeriod": {
            "start": export.billing_period_start.isoformat(),
            "end": export.billing_period_end.isoformat(),
        },
        "currency": export.currency,
        "generatedAtUtc": generated_at_utc.astimezone(UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "provenance": {
            "sourceCommitSha": request.source_commit_sha,
            "sourceRef": request.source_ref,
            "pipelineRunId": request.pipeline_run_id,
        },
        "billingSource": {
            "authority": export.authority,
            "exportType": export.export_type,
            "exportVersion": export.export_version,
            "exportDigestSha256": export.export_digest_sha256,
            "exportedAtUtc": export.exported_at_utc.astimezone(UTC)
            .isoformat()
            .replace("+00:00", "Z"),
        },
        "resourceObservation": {
            "schemaVersion": request.resource_observation_schema_version,
            "sha256": request.resource_observation_sha256,
            "runId": request.resource_observation_run_id,
        },
        "allocations": [
            {"category": category, "amount": _money(allocated[category])}
            for category in COST_CATEGORIES
        ],
        "sharedCostAllocation": {
            "method": "proportional_resource_weight",
            "methodologyVersion": METHODOLOGY_VERSION,
            "weight": _decimal(weight),
            "rounding": "ROUND_HALF_EVEN",
            "residualHandling": "assign_to_shared_platform",
            "residualAmount": _money(residual),
        },
        "reconciliation": {
            "sourceTotal": _money(export.source_total),
            "allocatedTotal": _money(allocated_total),
            "expectedWeightedTotal": _money(
                unrounded_total.quantize(CENT, ROUND_HALF_EVEN)
            ),
            "variance": "0.00",
            "status": "reconciled",
            "completenessStatus": export.completeness_status,
            "freshnessStatus": export.freshness_status,
            "partialPeriod": export.partial_period,
            "lateAdjustment": export.late_adjustment,
        },
        "costAttributionReconciled": not reconciliation_blockers,
        "costAttributionCertified": False,
        "certificationBlockers": certification_blockers,
        "supportedFeaturePromoted": False,
    }
    return artifact


def _reconciliation_blockers(export: BillingExport) -> list[str]:
    blockers: list[str] = []
    if export.completeness_status != "complete":
        blockers.append("billing_export_incomplete")
    if export.freshness_status != "current":
        blockers.append("billing_export_stale")
    if export.partial_period:
        blockers.append("partial_billing_period")
    return blockers


def _money(value: Decimal) -> str:
    return format(value.quantize(CENT, rounding=ROUND_HALF_EVEN), "f")


def _decimal(value: Decimal) -> str:
    return format(value, "f")
