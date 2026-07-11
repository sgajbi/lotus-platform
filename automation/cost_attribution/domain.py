from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import re


COST_CATEGORIES = (
    "compute",
    "memory",
    "database",
    "network",
    "storage",
    "observability",
    "shared_platform",
)
MONEY_PATTERN = re.compile(r"^-?(?:0|[1-9][0-9]*)\.[0-9]{2}$")


def parse_money(value: object, *, field: str) -> Decimal:
    if not isinstance(value, str) or not MONEY_PATTERN.fullmatch(value):
        raise ValueError(f"{field} must be a canonical two-decimal monetary string")
    return Decimal(value)


@dataclass(frozen=True)
class BillingExport:
    authority: str
    export_type: str
    export_version: str
    export_digest_sha256: str
    exported_at_utc: datetime
    billing_period_start: date
    billing_period_end: date
    currency: str
    category_costs: dict[str, Decimal]
    source_total: Decimal
    completeness_status: str
    freshness_status: str
    partial_period: bool
    late_adjustment: bool

    def __post_init__(self) -> None:
        if (
            self.exported_at_utc.tzinfo is None
            or self.exported_at_utc.utcoffset() is None
        ):
            raise ValueError("exported_at_utc must be timezone-aware")
        if self.billing_period_end < self.billing_period_start:
            raise ValueError("billing period end must not precede start")
        if not re.fullmatch(r"[A-Z]{3}", self.currency):
            raise ValueError("currency must be an uppercase ISO 4217 code")
        if set(self.category_costs) != set(COST_CATEGORIES):
            raise ValueError(
                "billing export must contain every governed cost category exactly once"
            )
        if sum(self.category_costs.values(), Decimal("0.00")) != self.source_total:
            raise ValueError(
                "billing export category costs must reconcile to source total"
            )
        if self.completeness_status not in {"complete", "partial", "missing"}:
            raise ValueError("unsupported completeness status")
        if self.freshness_status not in {"current", "stale"}:
            raise ValueError("unsupported freshness status")
        if len(self.export_digest_sha256) != 64 or any(
            character not in "0123456789abcdef"
            for character in self.export_digest_sha256
        ):
            raise ValueError("export digest must be lowercase SHA-256")


@dataclass(frozen=True)
class ServiceAllocationRequest:
    repository: str
    service_id: str
    environment: str
    region: str
    source_commit_sha: str
    source_ref: str
    pipeline_run_id: str
    resource_observation_schema_version: str
    resource_observation_sha256: str
    resource_observation_run_id: str
    shared_cost_numerator: Decimal
    shared_cost_denominator: Decimal

    def __post_init__(self) -> None:
        for name in (
            "repository",
            "service_id",
            "environment",
            "region",
            "source_commit_sha",
            "source_ref",
            "pipeline_run_id",
            "resource_observation_schema_version",
            "resource_observation_run_id",
        ):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be blank")
        if (
            not self.shared_cost_denominator.is_finite()
            or self.shared_cost_denominator <= 0
        ):
            raise ValueError("shared cost denominator must be positive")
        if not self.shared_cost_numerator.is_finite() or not (
            Decimal("0") <= self.shared_cost_numerator <= self.shared_cost_denominator
        ):
            raise ValueError(
                "shared cost numerator must be between zero and denominator"
            )
        if len(self.resource_observation_sha256) != 64 or any(
            character not in "0123456789abcdef"
            for character in self.resource_observation_sha256
        ):
            raise ValueError("resource observation digest must be lowercase SHA-256")
