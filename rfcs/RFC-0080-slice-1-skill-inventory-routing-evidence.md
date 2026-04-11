# RFC-0080 Slice 1 Evidence: Skill Inventory Review and Routing Map

- RFC: `RFC-0080-lotus-agent-runtime-demo-skill-pack-and-guidance-hardening.md`
- Date: `2026-04-11`
- Scope:
  - `lotus-platform`

## What changed

Slice 1 establishes the routing baseline for RFC-0080 before any skill content is changed.

Artifacts added:

1. `context/LOTUS-SKILL-ROUTING-MAP.md`
2. `rfcs/RFC-0080-implementation-checklist.md`
3. `tests/unit/test_rfc_0080_agent_runtime_guidance_contract.py`
4. `rfcs/RFC-0080-slice-1-skill-inventory-routing-evidence.md`

The RFC itself was also tightened so the implementation program is governed by an explicit decision,
scope boundary, routing rule, and final-slice posture.

## Inventory review outcome

The current Lotus skill inventory contains ten Lotus-specific skills.

Slice 1 classified them into four groups.

### Add

1. `lotus-front-office-runtime`

Reason:

The governed front-office runtime path introduced by RFC-0075 through RFC-0078 is important enough
to require a dedicated skill rather than being inferred from generic platform QA.

### Tighten

1. `lotus-qa-platform-validator`
2. `lotus-pr-premerge-gate`
3. `lotus-frontend-delivery-governance`
4. `lotus-backend-delivery-governance`
5. `lotus-validation-resolution-lifecycle`

Reason:

These skills remain valid, but their routing boundaries are not yet explicit enough for the
canonical front-office runtime, async GitHub, and screenshot-plus-evidence posture.

### Keep

1. `lotus-rfc-review-loop`
2. `lotus-codebase-review-ledger`
3. `lotus-methodology-doc-v3`
4. `lotus-rfc0067-rollout`
5. `lotus-transaction-rfc-loop`

Reason:

These skills remain specialized and do not currently conflict with the governed runtime path.

### Remove or merge candidates

None in Slice 1.

Reason:

The inventory review found ambiguity, but execution-level removal should wait until replacement
guidance is implemented and validated in later slices.

## Routing decisions

The routing precedence recorded in `context/LOTUS-SKILL-ROUTING-MAP.md` is:

1. front-office runtime and populated product-surface proof,
2. platform or backend validation,
3. repo-local frontend or backend delivery governance,
4. PR merge and CI fix-forward workflows,
5. RFC and governance workflows.

This is the key design choice of Slice 1.

It prevents broad validator or governance skills from intercepting tasks that should route directly
to the governed Workbench runtime.

## Why this slice is in the right shape

This slice avoids two weak patterns:

1. changing many skills immediately without first defining the routing baseline,
2. treating the RFC itself as the only place where routing intent is recorded.

The current shape is stronger:

1. the RFC defines the governed posture,
2. the checklist defines the slice program,
3. the routing map is a durable operational artifact,
4. tests guard the strengthened RFC structure and key routing expectations.

## Verification

```text
python -m pytest tests\unit\test_rfc_0080_agent_runtime_guidance_contract.py -q
3 passed
```

## Review outcome

Slice 1 is complete and does not need more structural tightening before moving to skill
implementation.

The conscious decision for this slice is:

1. add a new front-office runtime skill,
2. tighten overlapping operational skills,
3. defer actual skill removal until replacement paths are proven.
