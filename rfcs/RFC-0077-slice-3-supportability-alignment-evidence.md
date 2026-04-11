# RFC-0077 Slice 3 Evidence: Gateway and Panel Supportability Alignment

- RFC: `RFC-0077-workbench-panel-registry-and-evidence-contract.md`
- Date: `2026-04-11`
- Scope:
  - `lotus-platform`
  - `lotus-workbench`

## What changed

Slice 3 tightened the registry from "structured metadata" into a supportability contract that can
fail when runtime truth drifts.

Updated artifacts:

1. `lotus-platform/context/contracts/workbench-panel-registry.json`
2. `lotus-platform/tests/unit/test_rfc_0077_panel_registry_contract.py`
3. `lotus-workbench/scripts/live/validate-canonical-workbench-live.mjs`
4. `lotus-workbench/tests/unit/live-canonical-validation-script.test.ts`
5. `lotus-platform/rfcs/RFC-0077-implementation-checklist.md`
6. `lotus-platform/rfcs/RFC-0077-slice-3-supportability-alignment-evidence.md`

## Runtime and contract alignment

### Endpoint alignment

The platform registry test now asserts the exact gateway endpoint mapping for every governed panel.
This makes endpoint drift a contract failure rather than a review-time discovery.

### Ownership alignment

The Workbench validator now fails if a panel classification reports an owner that disagrees with the
registry. This corrected a real drift case where several performance panels were being classified as
`lotus-gateway` instead of `lotus-performance`.

### Support-state alignment

The validator now fails if a classified panel state differs from the registry's
`required_support_state`.

Current governed posture:

1. `performance.analysis.attribution` remains intentionally `partial`
2. `performance.evidence` is intentionally `unavailable`

`performance.evidence` was revised from the earlier provisional partial posture because the current
gateway contract does not expose evidence support through a materially useful backend surface yet.
That limitation remains explicitly linked to `RFC-0079`.

## Why this slice is in the right shape

This slice avoids two bad patterns:

1. a registry that documents intent but does not police runtime truth,
2. a validator that still carries hidden ownership assumptions outside the registry.

The current implementation is narrower and stronger:

1. contract tests pin endpoint mappings,
2. runtime validation pins owner and support state,
3. intentionally degraded panels remain explicit and auditable.

## Verification

```text
python -m pytest tests/unit/test_rfc_0077_panel_registry_contract.py -q
3 passed

npm test -- --runInBand tests/unit/live-canonical-validation-script.test.ts
9 passed
```

## Review outcome

Slice 3 is complete. No additional simplification is required before moving to the final
documentation, context, skill, and branch-hygiene slice. The remaining intentionally degraded panel
surface is explicit and governed instead of being left as implicit product behavior.
