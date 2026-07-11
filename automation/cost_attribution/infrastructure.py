from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path

from automation.cost_attribution.domain import (
    BillingExport,
    COST_CATEGORIES,
    parse_money,
)


EXPORT_FIELDS = frozenset(
    {
        "authority",
        "exportType",
        "exportVersion",
        "exportedAtUtc",
        "billingPeriodStart",
        "billingPeriodEnd",
        "currency",
        "categoryCosts",
        "sourceTotal",
        "completenessStatus",
        "freshnessStatus",
        "partialPeriod",
        "lateAdjustment",
    }
)


class JsonBillingExportAdapter:
    """Loads a normalized aggregate export without retaining raw billing rows or credentials."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> BillingExport:
        raw = self._path.read_bytes()
        payload = json.loads(raw, object_pairs_hook=_unique_object)
        if not isinstance(payload, dict):
            raise ValueError("billing export must be a JSON object")
        if set(payload) != EXPORT_FIELDS:
            raise ValueError(
                "billing export fields must match the closed normalized envelope"
            )
        costs = payload.get("categoryCosts")
        if not isinstance(costs, dict):
            raise ValueError("categoryCosts must be an object")
        if set(costs) != set(COST_CATEGORIES):
            raise ValueError(
                "categoryCosts must contain every governed category exactly once"
            )
        return BillingExport(
            authority=_required_text(payload, "authority"),
            export_type=_required_text(payload, "exportType"),
            export_version=_required_text(payload, "exportVersion"),
            export_digest_sha256=hashlib.sha256(raw).hexdigest(),
            exported_at_utc=datetime.fromisoformat(
                _required_text(payload, "exportedAtUtc").replace("Z", "+00:00")
            ),
            billing_period_start=datetime.fromisoformat(
                _required_text(payload, "billingPeriodStart")
            ).date(),
            billing_period_end=datetime.fromisoformat(
                _required_text(payload, "billingPeriodEnd")
            ).date(),
            currency=_required_text(payload, "currency"),
            category_costs={
                category: parse_money(
                    costs.get(category), field=f"categoryCosts.{category}"
                )
                for category in COST_CATEGORIES
            },
            source_total=parse_money(payload.get("sourceTotal"), field="sourceTotal"),
            completeness_status=_required_text(payload, "completenessStatus"),
            freshness_status=_required_text(payload, "freshnessStatus"),
            partial_period=_required_bool(payload, "partialPeriod"),
            late_adjustment=_required_bool(payload, "lateAdjustment"),
        )


def _required_text(payload: dict[str, object], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-blank string")
    return value


def _required_bool(payload: dict[str, object], name: str) -> bool:
    value = payload.get(name)
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean")
    return value


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result
