# RFC-0080: Lotus Agent Runtime, Demo Skill Pack, and Guidance Hardening

- Status: Proposed
- Date: 2026-04-11
- Owners: lotus-platform governance
- Requires Approval From:
  - lotus-platform maintainers
  - repository maintainers for all affected Lotus repos
- Related:
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
  - `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`
  - `RFC-0074-repeatable-developer-and-agent-bootstrap-system.md`
  - `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
  - `RFC-0076-canonical-front-office-demo-data-contract.md`
  - `RFC-0077-workbench-panel-registry-and-evidence-contract.md`
  - `RFC-0078-modular-front-office-validation-framework.md`
  - `RFC-0079-gateway-evidence-and-lineage-contract.md`

## Summary

RFC-0073 and RFC-0074 improved Lotus engineering context and repeatable bootstrap guidance.
RFC-0075, RFC-0076, RFC-0077, and RFC-0078 then established the governed front-office runtime,
canonical data contract, panel registry, and modular validation path.

The next gap is not product runtime capability. It is agent routing quality.

Future sessions can still waste time by:

1. choosing stale startup paths,
2. treating screenshots as proof without governed validation,
3. idling on long GitHub checks instead of using asynchronous PR loops,
4. mixing platform QA with front-office product-surface QA,
5. rediscovering the canonical portfolio, screenshot path, and evidence model from scratch,
6. following overlapping or outdated Lotus skill guidance.

This RFC proposes a governed Lotus agent runtime skill pack and guidance hardening program so future
Codex sessions use the correct runtime, validation, PR, and evidence paths by default.

## Decision

Lotus will treat agent routing and skill guidance as governed platform infrastructure rather than
informal convenience notes.

Specifically:

1. a dedicated Lotus front-office runtime skill will be introduced,
2. existing Lotus skills will be tightened to route to the governed runtime and validation path,
3. stale or overlapping skill guidance will be removed rather than preserved,
4. AGENTS and central context documents will explicitly reinforce the governed runtime, async GitHub
   workflow, and evidence-backed validation posture,
5. every implementation slice under this RFC must end with an explicit review of whether context,
   skills, or documentation should be updated, left unchanged consciously, or simplified,
6. no subsequent slice should begin until that review is complete and the review outcome is recorded
   truthfully.

## Problem

Lotus now has a governed runtime path, but agents can still miss it because the routing layer is not
yet first-class.

The current failure modes are:

1. stale platform-stack assumptions instead of the governed Workbench runtime,
2. screenshot-only success criteria rather than screenshot-plus-machine-readable validation,
3. long blocking waits on GitHub checks instead of fix-forward asynchronous execution,
4. blurred boundaries between platform QA, backend service validation, and populated product-surface
   validation,
5. stale skill inventory items that no longer reflect the current target operating model,
6. central docs and AGENTS guidance that mention the right concepts but do not always drive the
   agent decisively to the correct path.

This is not a documentation-only problem. It is a routing and operating-contract problem.

## Goals

1. Add a dedicated Lotus front-office runtime skill for governed local demo/runtime work.
2. Route demo, screenshot, seeded-data, and populated-panel tasks to the governed runtime path by
   default.
3. Harden Lotus skills around asynchronous GitHub execution and fix-forward workflows.
4. Remove stale or overlapping Lotus skill guidance.
5. Keep AGENTS, central context, onboarding docs, and skills aligned.
6. Reduce ramp-up cost and increase determinism of future agent behavior.
7. Ensure guidance remains concise, actionable, and linked to governed source documents instead of
   becoming a duplicated prose layer.

## Non-Goals

1. Replacing the broader engineering context system introduced by RFC-0073.
2. Replacing repo-local runbooks with skill content.
3. Embedding large operational runbooks directly into skill files.
4. Teaching generic Git, browser, or UI concepts outside Lotus needs.
5. Replacing product or service contracts with agent guidance.

## Scope

This RFC governs:

1. Lotus skill routing and trigger design,
2. Lotus agent guidance for front-office runtime and evidence-backed demo work,
3. async PR and GitHub execution guidance in Lotus skills,
4. AGENTS and central context references that shape future Codex behavior,
5. cleanup of stale, duplicate, or misleading Lotus skill guidance.

This RFC does not govern:

1. the canonical dataset itself, which remains owned by RFC-0076,
2. the panel registry contract, which remains owned by RFC-0077,
3. the validation framework runtime code, which remains owned by RFC-0078,
4. evidence and lineage payloads, which remain owned by RFC-0079.

## Mandatory Slice Review Gate

Every completed slice under this RFC must be reviewed before work starts on the next slice.

That review must explicitly check:

1. whether complexity can be reduced further,
2. whether code, tests, docs, and automation can be made cleaner, more readable, more maintainable,
   and more modular,
3. whether dead code, stale guidance, duplicated logic, or oversized files should be removed,
   simplified, or split,
4. whether tests are meaningful and high-value rather than superficial,
5. whether documentation and governed context were updated wherever repository or platform truth
   changed,
6. whether any conscious no-change decisions should be recorded explicitly.

The slice review is not complete unless it records:

1. improvements made in the same slice,
2. opportunities intentionally deferred,
3. justification for anything left unchanged when a reasonable reviewer could expect it to change.

## Agent Routing Rule

Lotus guidance must route tasks according to operational intent, not vague keyword overlap.

The routing order must be:

1. front-office demo/runtime and populated-panel proof,
2. platform QA or backend/runtime QA,
3. repo-local development or service delivery governance,
4. PR merge and CI fix-forward workflows.

If a task includes terms such as:

1. `PB_SG_GLOBAL_BAL_001`,
2. demo screenshots,
3. populated Workbench panels,
4. `lotus-risk-module-shots`,
5. canonical UI proof,
6. front-office runtime,
7. "all panels loaded",
8. "bring up all UI-related stack",

the new front-office runtime skill must take precedence over more generic platform validator skills.

## Governed Source of Truth

The new runtime skill and related guidance must point to the following governed sources of truth:

1. `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`
2. `lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1`
3. RFC-0076 contract artifacts under `lotus-platform/context/contracts/`
4. RFC-0077 panel registry artifacts under `lotus-platform/context/contracts/`
5. screenshot evidence and validation summary outputs produced by the governed validator

The skill layer must not restate large sections of those runbooks. It must route to them decisively.

## Proposed Skill Changes

### New Skill: `lotus-front-office-runtime`

Add a dedicated skill:

```text
lotus-front-office-runtime
```

This skill must:

1. route the agent to the governed Workbench-owned runtime path,
2. identify the canonical portfolio and benchmark,
3. instruct the agent to validate before claiming success,
4. require screenshot evidence plus machine-readable validation evidence,
5. reject stale demo portfolios such as timestamped smoke portfolios when canonical data is
   required,
6. classify `ready`, `partial`, `empty`, `unavailable`, and `error` states truthfully,
7. prefer targeted local checks and GitHub for heavyweight CI,
8. instruct the agent to keep working asynchronously while GitHub executes long lanes.

### Existing Skill Hardening

#### `lotus-qa-platform-validator`

This skill must distinguish:

1. platform or infrastructure validation,
2. canonical front-office populated product-surface validation,
3. backend-only service validation.

It should explicitly defer front-office populated-panel work to `lotus-front-office-runtime`.

#### `lotus-pr-premerge-gate`

This skill must explicitly instruct the agent to:

1. avoid blocking on long-running GitHub checks,
2. push, enable auto-merge when appropriate, and continue useful work,
3. poll asynchronously rather than idling,
4. keep PR evidence truthful and current,
5. complete branch hygiene after merge rather than leaving repos in a drifting state.

#### `lotus-backend-delivery-governance` and `lotus-frontend-delivery-governance`

These skills must clearly reference:

1. canonical runtime contracts,
2. panel registry and evidence expectations where relevant,
3. evidence-backed UI requirements,
4. the rule that unsupported UI states must be surfaced truthfully, not cosmetically.

## Documentation and Context Hardening

The following guidance must be reviewed and aligned:

1. repo-root `AGENTS.md` in affected Lotus repositories
2. `C:\\Users\\Sandeep\\.codex\\AGENTS.md`
3. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
4. `lotus-platform/context/AGENTS-OPERATING-CONTRACT.md`
5. `lotus-platform/docs/onboarding/LOTUS-AGENT-RAMP-UP.md`
6. `lotus-platform/docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`

These documents must:

1. cross-link the governed runtime path,
2. explicitly discourage stale stack paths,
3. instruct maintainers to keep docs synchronized when the runtime path changes materially,
4. reinforce async GitHub usage and fix-forward execution as the default for long CI loops,
5. make it explicit that screenshots without validation evidence are not sufficient proof,
6. keep repo-root and deployed AGENTS entrypoints synchronized when routing guidance changes.

This RFC does not authorize repo-specific routing forks inside repo-root `AGENTS.md`. Routing policy
continues to be authored centrally and synchronized outward.

## Skill Inventory Review Rule

As part of this RFC, the Lotus skill inventory must be reviewed for:

1. duplicate responsibilities,
2. outdated references,
3. stale commands,
4. missing cross-links,
5. opportunities to simplify routing and reduce ambiguity.

Skills that are obsolete or overlapping should be removed or tightened rather than preserved by
default.

Dead guidance should be removed, not merely marked as historical, unless it is required for audit or
RFC evidence.

## Implementation Slices

### Slice 1: Skill Inventory Review and Routing Map

1. review current Lotus skills,
2. identify overlap, gaps, stale guidance, and dead guidance,
3. define the target routing map,
4. record explicit keep, tighten, remove, and add decisions,
5. complete and record the mandatory slice review gate before moving to Slice 2.

### Slice 2: New Front-Office Runtime Skill

1. add `lotus-front-office-runtime`,
2. document trigger phrases and governed paths,
3. keep the skill concise, directive, and linked to source-of-truth runbooks,
4. prove that the skill routes to validation-plus-evidence rather than screenshots-only success,
5. complete and record the mandatory slice review gate before moving to Slice 3.

### Slice 3: Hardening Existing Skills

1. update QA, PR, frontend, and backend Lotus skills,
2. align them with RFC-0075 through RFC-0079 runtime behavior,
3. remove stale or ambiguous wording,
4. prove that front-office tasks no longer route through weaker generic skill paths,
5. complete and record the mandatory slice review gate before moving to Slice 4.

### Slice 4: AGENTS and Context Synchronization

1. update global AGENTS guidance,
2. update Lotus context docs and onboarding docs,
3. add durable cross-links and maintenance expectations,
4. keep context concise and avoid duplicating runbooks,
5. complete and record the mandatory slice review gate before moving to Slice 5.

### Slice 5: Validation of Agent Routing Behavior

1. prove that a new agent can select the governed runtime path with minimal ambiguity,
2. prove that async GitHub behavior is reflected in the updated skills,
3. prove that stale startup or screenshot-only behaviors are no longer encouraged,
4. add tests or contract guards for key guidance artifacts where appropriate,
5. complete and record the mandatory slice review gate before moving to Slice 6.

### Slice 6: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

1. remove dead or obsolete Lotus skill content,
2. validate that the guidance is internally consistent,
3. document any conscious decisions to leave specific skills or docs unchanged,
4. complete branch hygiene, PR evidence hygiene, and cross-repo reference cleanup before closure,
5. complete and record the final mandatory slice review gate before RFC closure.

## Acceptance Criteria

1. A dedicated skill exists for the governed front-office runtime and demo path.
2. Existing Lotus skills route tasks more cleanly and avoid overlap.
3. AGENTS and Lotus context docs explicitly point to the governed runtime path.
4. Repo-root and deployed AGENTS entrypoints stay synchronized when routing posture changes.
5. Async GitHub execution and fix-forward behavior are explicitly reinforced in the relevant skills.
6. Screenshot-only success patterns are explicitly rejected.
7. Obsolete skill guidance is removed.
8. The final slice records any conscious no-change decisions for skills or docs.

## Risks and Mitigations

### Risk: Too much guidance creates context overload

Mitigation:

1. keep skills short and directive,
2. store durable detail in linked docs,
3. avoid duplicating full runbooks in multiple places,
4. prefer routing clarity over prose volume.

### Risk: Skills drift from runtime reality

Mitigation:

1. cross-link to governed runbooks and contracts,
2. add explicit maintenance expectations in AGENTS and onboarding docs,
3. review skills whenever the runtime path changes materially,
4. add lightweight governance tests for critical RFC structure and guidance contracts.

### Risk: Guidance cleanup leaves hidden gaps

Mitigation:

1. inventory skills before removal,
2. require explicit keep/remove/tighten decisions,
3. fail the slice if guidance is removed without a replacement routing path where one is needed.

## Skills, Context, and Documentation Implications

This RFC is expected to change:

1. Lotus skill inventory structure,
2. AGENTS guidance and cross-links,
3. Lotus onboarding and agent ramp-up documents,
4. the default routing posture for demo/runtime and async PR work.

This RFC must also include a conscious review of what should not change.

If a skill or context document already reflects the required behavior, the slice evidence should say
so explicitly rather than changing it for appearance only.

## Approval Request

Approve this RFC if Lotus should treat agent runtime routing, demo guidance, and async delivery
behavior as governed platform infrastructure rather than informal operational memory.
