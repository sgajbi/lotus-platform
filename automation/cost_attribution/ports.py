from __future__ import annotations

from typing import Protocol

from automation.cost_attribution.domain import BillingExport


class BillingExportPort(Protocol):
    def load(self) -> BillingExport: ...
