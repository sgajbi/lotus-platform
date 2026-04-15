# RFC-0077 Slice 5 Evidence: Attribution Panel Readiness Alignment

- RFC: `RFC-0077-workbench-panel-registry-and-evidence-contract.md`
- Date: `2026-04-15`
- Scope:
  - `lotus-platform`
  - `lotus-workbench`
  - `lotus-gateway`
  - `lotus-performance`

## What changed

The governed panel registry now classifies `performance.analysis.attribution` as `ready`.

This updates the registry to match current runtime truth: the canonical gateway performance details
contract reports benchmark-relative attribution detail as supported and returns populated attribution
rows for `PB_SG_GLOBAL_BAL_001`.

Updated artifacts:

1. `context/contracts/workbench-panel-registry.json`
2. `tests/unit/test_rfc_0077_panel_registry_contract.py`
3. `rfcs/RFC-0077-slice-5-attribution-panel-readiness-evidence.md`

## Runtime Evidence

The canonical validation lane reached the browser validator and failed because the panel registry
still required `performance.analysis.attribution = partial` while the current runtime reported the
panel as `ready`.

Direct gateway probe:

```text
GET /api/v1/workbench/PB_SG_GLOBAL_BAL_001/performance/details?period=YTD&chart_frequency=monthly&detail_basis=NET&contribution_dimension=asset_class&attribution_dimension=asset_class&benchmark_code=BMK_PB_GLOBAL_BALANCED_60_40
```

Observed attribution capability:

```json
{
  "state": "supported",
  "reason": "Benchmark-relative attribution detail is available.",
  "coverage_level": "detail",
  "supported_dimensions": ["asset_class", "sector", "country", "currency"],
  "supported_frequencies": ["monthly", "quarterly"]
}
```

Observed attribution row count: `4`.

## Supportability Decision

`performance.analysis.attribution` is no longer intentionally partial for the canonical dataset.
The former limitation, "benchmark-relative attribution may remain partial until full source-backed
detail is available", is removed from the registry.

`performance.evidence` remains intentionally `unavailable` until the gateway evidence and lineage
contract is implemented under `RFC-0079`.

## Validation

Minimum validation for this slice:

```text
python -m pytest tests/unit/test_rfc_0077_panel_registry_contract.py -q
```

The full acceptance check is the canonical Workbench live validation lane:

```text
npm run live:validate
```
