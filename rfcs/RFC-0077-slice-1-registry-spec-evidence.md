# RFC-0077 Slice 1 Evidence: Registry Specification and Testable Contract

- RFC: `RFC-0077-workbench-panel-registry-and-evidence-contract.md`
- Date: `2026-04-11`
- Scope:
  - `lotus-platform`

## What changed

Slice 1 establishes the machine-readable contract surface for governed Workbench panel ownership and
evidence posture before any downstream consumer starts depending on it.

Artifacts added:

1. `context/contracts/workbench-panel-registry.schema.json`
2. `context/contracts/workbench-panel-registry.json`
3. `rfcs/RFC-0077-implementation-checklist.md`
4. `tests/unit/test_rfc_0077_panel_registry_contract.py`
5. `rfcs/RFC-0077-slice-1-registry-spec-evidence.md`

The initial registry inventory covers the current governed front-office Workbench surface introduced
by RFC-0075 and tied to the canonical RFC-0076 dataset.

## Design choices

### Root contract model

The registry is a contract artifact, not a loose JSON list. The root object therefore records:

1. `contract_id`
2. `contract_version`
3. `governed_by_rfc`
4. `related_rfcs`
5. `canonical_data_contract`
6. `panels`

This keeps the registry versioned and traceable in the same way as the RFC-0076 contract artifacts.

### Panel granularity

The initial inventory includes 12 governed panel entries:

1. `portfolio.summary`
2. `portfolio.detailed`
3. `performance.summary`
4. `performance.analysis.contribution`
5. `performance.analysis.attribution`
6. `performance.advisor_brief`
7. `performance.risk.snapshot`
8. `performance.risk.drawdown`
9. `performance.risk.concentration`
10. `performance.risk.rolling`
11. `performance.risk.historical_attribution`
12. `performance.evidence`

This is intentionally narrow. It matches the already-governed front-office validation surface rather
than speculating about panels that are not yet under live validation.

### State posture

The schema allows only governed states:

1. `ready`
2. `loading`
3. `empty`
4. `partial`
5. `unavailable`
6. `error`
7. `out_of_scope`

`supported_blank` is explicitly disallowed. That is the key drift-prevention rule introduced by
RFC-0075 and formalized by RFC-0077.

### `performance.evidence`

`performance.evidence` is intentionally modeled with `required_support_state = partial`.
The registry makes that partial posture explicit and links it forward to `RFC-0079` instead of
pretending the evidence panel is fully supported today.

## Why this slice is in the right shape

This slice avoids two common mistakes:

1. under-modeling, where the registry would be too weak to drive anything meaningful,
2. over-modeling, where the registry would attempt to encode browser interaction flow or domain
   calculations that belong elsewhere.

The current shape is appropriate:

1. the registry owns durable panel metadata,
2. the schema governs structure and state vocabulary,
3. downstream scripts can consume it without carrying duplicated metadata,
4. imperative browser flow remains in code where it is still clearer.

## Verification

```text
python -m pytest tests\unit\test_rfc_0077_panel_registry_contract.py -q
2 passed
```

## Review outcome

Slice 1 is complete and does not need more structural tightening before moving to Workbench
adoption. The next slice should focus on consuming this metadata in `lotus-workbench` and removing
duplicated panel metadata there.
