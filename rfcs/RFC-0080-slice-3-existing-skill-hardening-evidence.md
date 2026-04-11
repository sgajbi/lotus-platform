# RFC-0080 Slice 3 Evidence: Existing Skill Hardening

- RFC: `RFC-0080-lotus-agent-runtime-demo-skill-pack-and-guidance-hardening.md`
- Date: `2026-04-11`
- Scope:
  - `lotus-platform`

## What changed

Slice 3 hardens the existing Lotus skills that were identified as routing-overlap candidates in
Slice 1.

Artifacts updated:

1. `codex/skills/lotus-qa-platform-validator/SKILL.md`
2. `codex/skills/lotus-pr-premerge-gate/SKILL.md`
3. `codex/skills/lotus-frontend-delivery-governance/SKILL.md`
4. `codex/skills/lotus-backend-delivery-governance/SKILL.md`
5. `codex/skills/lotus-validation-resolution-lifecycle/SKILL.md`
6. `rfcs/RFC-0080-slice-3-existing-skill-hardening-evidence.md`

## Hardening outcomes

### `lotus-qa-platform-validator`

This skill now explicitly distinguishes:

1. backend and infrastructure QA,
2. platform validation,
3. governed front-office runtime proof.

It now defers populated Workbench demo-proof tasks to `lotus-front-office-runtime`.

### `lotus-pr-premerge-gate`

This skill now makes asynchronous GitHub behavior explicit:

1. prefer `gh pr checks <PR_NUMBER> --watch=false`,
2. enable auto-merge when appropriate,
3. continue useful work while heavy lanes run,
4. require machine-readable evidence for governed front-office screenshot-proof work.

### `lotus-frontend-delivery-governance`

This skill now clearly treats `lotus-front-office-runtime` as the primary route for:

1. canonical runtime tasks,
2. populated Workbench panel proof,
3. screenshot-backed front-office validation.

It also references RFC-0076 and RFC-0077 expectations for governed Workbench surfaces.

### `lotus-backend-delivery-governance`

This skill now explicitly distinguishes:

1. backend proof,
2. product-surface proof.

It prevents backend-only success from being presented as front-office readiness when the slice
affects canonical product flows.

### `lotus-validation-resolution-lifecycle`

This skill now composes correctly with the new front-office runtime skill and explicitly adopts the
async GitHub posture for heavy PR checks.

## Why this slice is in the right shape

This slice does not rewrite every skill. It only tightens the boundaries that create routing drift.

That is the correct scope:

1. narrow enough to stay readable,
2. broad enough to remove the key overlaps found in Slice 1,
3. explicit about async GitHub behavior,
4. explicit about screenshot-plus-evidence proof.

## Verification

```text
python -m pytest tests\unit\test_rfc_0080_agent_runtime_guidance_contract.py tests\unit\test_engineering_context_system_contract.py -q
```

## Review outcome

Slice 3 is complete and does not need broader churn before moving on.

The conscious no-change decision in this slice is:

1. keep specialized skills such as `lotus-rfc-review-loop` and `lotus-methodology-doc-v3`
   unchanged because they do not create routing ambiguity for front-office runtime work.
