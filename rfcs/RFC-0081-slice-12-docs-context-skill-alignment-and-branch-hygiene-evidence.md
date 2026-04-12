# RFC-0081 Slice 12: Documentation, Agent Context, Skill Alignment, and Branch Hygiene Evidence

## Scope of this slice

Slice 12 reviewed whether RFC-0081 requires immediate updates to:

1. engineering documentation,
2. agent context,
3. skill routing guidance,
4. branch and PR hygiene posture,
5. stale frontend guidance.

Because RFC-0081 is still pre-implementation, this slice is intentionally explicit about what
should change now versus later.

## Current-state findings

### The RFC itself is now implementation-grade

RFC-0081 and its slice evidence now cover:

1. visual and interaction grammar,
2. gateway composition posture,
3. shell and naming standards,
4. advisory and proposal integration,
5. micro-frontend composition,
6. AI disclosure and governance,
7. AI search and command posture,
8. performance, accessibility, observability, caching, and automation expectations.

That means the RFC set itself is already a meaningful documentation asset.

### Runtime and agent guidance should not be changed prematurely

The current governed runtime guidance from RFC-0076 through RFC-0080 is still correct.

RFC-0081 has not yet changed:

1. the actual supported shell routes,
2. the canonical runtime bring-up path,
3. the validator execution entry point,
4. the active skill-routing behavior for current day-to-day work.

So immediate changes to AGENTS, onboarding, or runtime docs would be speculative.

### Branch hygiene is not yet closure-complete

Branch hygiene for RFC-0081 cannot be considered complete yet because:

1. implementation has not started,
2. PR [#135](https://github.com/sgajbi/lotus-platform/pull/135) is still open,
3. this branch remains the active RFC working branch.

That is correct posture for now.

## Keep / replace / retire decisions

### Keep

1. current RFC-0076 through RFC-0080 runtime and routing guidance,
2. current `lotus-front-office-runtime` governed path,
3. current AGENTS and onboarding posture for the canonical runtime,
4. current async PR and GitHub-first working method.

### Replace

1. implicit “no docs change required” posture with explicit no-change evidence,
2. future stale shell guidance once RFC-0081 implementation lands,
3. future ambiguous skill routing once the new shell, proposal, and AI discovery surfaces become supported product flows.

### Retire

1. any old shell/workspace guidance that still points to transitional route families once implementation is complete,
2. any future onboarding note that describes deprecated shell vocabulary,
3. any future skill instruction that routes proposal, advisory, or AI search work through obsolete UI topology assumptions.

## Documentation and context decision for this slice

### 1. No immediate agent-context change is required before implementation begins

This is a conscious decision.

Reason:

1. RFC-0081 has established target-state governance,
2. it has not yet changed the live runtime contract or supported product flow,
3. changing AGENTS or onboarding now would create speculative guidance rather than accurate guidance.

### 2. Documentation updates must happen during implementation, not ahead of it

When RFC-0081 starts changing real product topology, the following docs should be reviewed and
updated:

1. `context/LOTUS-ENGINEERING-CONTEXT.md`,
2. `context/AGENTS-OPERATING-CONTRACT.md`,
3. `docs/onboarding/LOTUS-AGENT-RAMP-UP.md`,
4. runtime and validation runbooks affected by shell changes,
5. any skill docs that encode obsolete shell or module assumptions.

### 3. Skills should only change when product routing changes materially

Potential later updates may be needed for:

1. `lotus-front-office-runtime`,
2. `lotus-frontend-delivery-governance`,
3. `lotus-qa-platform-validator`,
4. any future skill that references shell route families or validated screen inventory.

No skill change is justified yet because no live runtime behavior has changed.

### 4. Branch hygiene decision

The correct branch-hygiene posture for this slice is:

1. keep working on `codex/rfc-0081-ui-uplift-hardening-20260411`,
2. keep PR #135 open while RFC evidence continues,
3. only perform final branch cleanup after:
   - RFC evidence is complete,
   - PR is merged,
   - any follow-up working branches are no longer needed.

## Stale-guidance review

No stale guidance was removed in this slice because implementation has not yet landed.

However, this slice confirms that the following guidance areas must be reviewed later:

1. any route vocabulary that still points to `suite`, `recommendations`, or other transitional shell surfaces,
2. any runtime guidance that does not mention proposal, advisory, and AI-bearing shell modules once they become supported,
3. any automation guidance that does not include new panels and discovery surfaces once implemented.

## Review of slice 12

Slice 12 is complete.

The most important outcome is that the RFC closure is explicit rather than implicit:

1. no premature AGENTS or onboarding changes were made,
2. that no-change decision is documented consciously,
3. the future documentation and skill update points are clearly listed,
4. branch hygiene is correctly deferred until PR merge rather than claimed early.

Slice 12 is complete.
