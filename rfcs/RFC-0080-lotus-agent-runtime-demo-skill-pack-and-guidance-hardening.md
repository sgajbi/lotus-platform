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

RFC-0073 and RFC-0074 improved Lotus engineering context and repeatable bootstrap guidance. RFC-0075
then established the governed front-office runtime path. The next step is to harden Lotus agent
skills and guidance so future sessions consistently choose the governed runtime, validation, PR, and
evidence paths without rediscovering them.

This RFC proposes:

1. a new Lotus front-office runtime and demo skill,
2. tighter routing across existing Lotus skills,
3. removal of obsolete or overlapping skill guidance,
4. stronger agent instructions for asynchronous GitHub use, screenshot evidence, and truthful panel
   validation.

## Problem

Even with better docs, future agents can still make avoidable mistakes:

1. bringing up stale platform-stack paths instead of the governed Workbench runtime,
2. treating screenshots as proof without runtime validation,
3. blocking on long GitHub checks instead of using asynchronous PR loops,
4. failing to distinguish platform QA from front-office product-surface QA,
5. rediscovering the canonical portfolio and screenshot flow from scratch,
6. keeping obsolete or overlapping skill guidance that creates routing ambiguity.

This creates ramp-up cost and inconsistent execution quality.

## Goals

1. Add a dedicated Lotus front-office runtime skill.
2. Route demo, screenshot, seeded-data, and populated-panel tasks to the governed runtime path.
3. Harden Lotus skills around asynchronous GitHub execution and fix-forward workflows.
4. Remove stale or overlapping Lotus skill guidance.
5. Keep central docs, AGENTS guidance, and skills aligned.
6. Make future agent behavior more deterministic and higher quality.

## Non-Goals

1. Replacing the broader engineering context system from RFC-0073.
2. Replacing repo-local runbooks.
3. Teaching generic Git or UI concepts outside Lotus needs.
4. Embedding large volumes of repo content directly in skill files.

## Proposed New Skill

Add a new skill, for example:

```text
lotus-front-office-runtime
```

### Trigger Conditions

The skill should trigger when tasks mention concepts such as:

1. front-office runtime,
2. Workbench screenshots,
3. populated UI panels,
4. canonical UI proof,
5. demo screenshots,
6. seeded Workbench validation,
7. `PB_SG_GLOBAL_BAL_001`,
8. `lotus-risk-module-shots`,
9. "bring up all UI-related stack",
10. "validate all panels are loaded".

### Required Skill Behavior

The skill should route the agent to the governed path:

1. `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`
2. `lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1`
3. the canonical screenshot output contract,
4. the canonical portfolio and benchmark,
5. the Workbench-owned runtime path rather than stale platform-stack assumptions.

The skill must instruct the agent to:

1. validate before claiming success,
2. capture machine-readable evidence with screenshots,
3. avoid stale demo portfolios such as timestamped smoke portfolios when the canonical dataset is
   required,
4. classify `ready`, `partial`, `empty`, and `unavailable` states truthfully,
5. use targeted local checks and GitHub for heavyweight CI where appropriate.

## Existing Skill Hardening

### `lotus-qa-platform-validator`

Improve this skill so it clearly distinguishes:

1. platform/infrastructure validation,
2. canonical front-office product-surface validation,
3. backend-only service validation.

It should defer front-office populated-panel work to the new skill.

### `lotus-pr-premerge-gate`

Add explicit guidance to:

1. avoid blocking on long-running GitHub checks,
2. push, enable auto-merge when appropriate, and continue useful work,
3. poll asynchronously instead of idling,
4. keep PR evidence truthful and current.

### `lotus-backend-delivery-governance` and `lotus-frontend-delivery-governance`

Add clearer references to:

1. canonical runtime contracts,
2. panel registry expectations,
3. evidence-backed UI requirements,
4. no fake or unsupported UI states.

## Documentation Hardening

The following guidance should be aligned:

1. `C:\\Users\\Sandeep\\.codex\\AGENTS.md`
2. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
3. `lotus-platform/context/AGENTS-OPERATING-CONTRACT.md`
4. `lotus-platform/docs/onboarding/LOTUS-AGENT-RAMP-UP.md`
5. `lotus-platform/docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`

These documents should:

1. cross-link the governed runtime path,
2. explicitly discourage stale stack paths,
3. instruct future maintainers to keep the docs synchronized as the platform evolves.

## Skill Inventory Review

As part of this RFC, the Lotus skill inventory should be reviewed for:

1. duplicate responsibilities,
2. outdated references,
3. stale commands,
4. missing cross-links,
5. opportunities to simplify skill routing.

Skills that are obsolete or overlapping should be removed or tightened rather than preserved by
default.

## Proposed Implementation Slices

### Slice 1: Skill Inventory Review and Routing Map

1. review current Lotus skills,
2. identify overlap, gaps, and stale guidance,
3. define the target routing map.

### Slice 2: New Front-Office Runtime Skill

1. add the new skill,
2. document trigger phrases and governed paths,
3. keep the skill concise and directive.

### Slice 3: Hardening Existing Skills

1. update QA, PR, frontend, and backend skills,
2. align them with RFC-0075 runtime behavior,
3. remove ambiguous or stale wording.

### Slice 4: AGENTS and Context Sync

1. update global AGENTS guidance,
2. update Lotus context docs,
3. add durable cross-links and maintenance expectations.

### Slice 5: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

1. remove dead or obsolete Lotus skill content,
2. validate that the guidance is internally consistent,
3. document any conscious decisions to leave specific skills or docs unchanged,
4. prove that a new agent can follow the governed runtime path with minimal ambiguity,
5. complete branch hygiene, PR evidence hygiene, and cross-repo reference cleanup before closure.

## Acceptance Criteria

1. A dedicated skill exists for the governed front-office runtime and demo path.
2. Existing Lotus skills route tasks more cleanly and avoid overlap.
3. AGENTS and Lotus context docs explicitly point to the governed runtime path.
4. Future sessions are less likely to choose stale startup or validation paths.
5. Obsolete skill guidance is removed.

## Risks and Mitigations

### Risk: Too much guidance creates context overload

Mitigation:

1. keep skills short and directive,
2. store durable detail in linked docs,
3. avoid duplicating full runbooks in multiple places.

### Risk: Skills drift from runtime reality

Mitigation:

1. cross-link to governed runbooks,
2. add explicit maintenance expectations in AGENTS and onboarding docs,
3. review skills whenever the runtime path changes materially.

## Approval Request

Approve this RFC if Lotus should explicitly harden agent skills and operating guidance around the
governed front-office runtime, validation, and asynchronous delivery patterns.
