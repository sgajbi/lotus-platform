# RFC-0094: Durable Background Engineering Task Ledger and Governed Delegation Model

- Status: Draft
- Date: 2026-04-18
- Owners:
  - lotus-platform governance
- Requires Approval From:
  - lotus-platform maintainers
  - maintainers of Lotus repositories whose automation, skill, or validation posture is updated
    under this RFC
- Related:
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
  - `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`
  - `RFC-0074-repeatable-developer-and-agent-bootstrap-system.md`
  - `RFC-0080-lotus-agent-runtime-demo-skill-pack-and-guidance-hardening.md`
  - `RFC-0093-lotus-context-assembly-and-compaction-hardening-for-agentic-development.md`

## Summary

Lotus already expects agents and engineers to use asynchronous execution for expensive work rather
than blocking on long checks.

That posture exists in practice through:

1. GitHub Actions under RFC-0072,
2. platform background-run automation,
3. async skills such as `async-task-runner` and `platform-automation-ops`,
4. emerging agent workflows that keep implementation moving while checks run remotely.

What Lotus still lacks is a governed platform model for:

1. what detached engineering work exists,
2. how it is tracked durably,
3. how ownership and status are communicated,
4. how bounded delegated work should be launched and reported,
5. how agents should avoid polling loops, orphaned runs, and untruthful handoffs.

This RFC defines the next layer:

1. a durable background engineering task ledger,
2. a governed delegation model for bounded parallel agent work,
3. clear ownership, evidence, and lifecycle expectations,
4. updates to automation, skills, context, and validation where needed.

The goal is to make long-running engineering work in Lotus:

1. more reliable,
2. more inspectable,
3. less blocking,
4. more truthful,
5. easier to continue across sessions and PR loops.

## Why This RFC Exists

Lotus is increasingly using agentic development patterns that involve detached work:

1. GitHub checks running after a push,
2. background validation profiles,
3. long QA or runtime bring-up loops,
4. repo-wide scans,
5. delegation to bounded agent subtasks,
6. PR monitoring and merge loops.

These patterns are useful, but without a governed model they create recurring failure modes:

1. the agent forgets which detached jobs are active,
2. the user gets a status answer based on stale assumptions,
3. results are trapped in logs without durable summary or ownership,
4. delegation fans out without clear write boundaries or return contracts,
5. agents waste time polling repeatedly instead of continuing useful work,
6. CI, local async runs, and delegated subtasks all use different implicit status language.

OpenClaw is useful here as a reference, not as a library.

Its background tasks and subagent models show the value of:

1. one task ledger for detached work,
2. explicit task lifecycle,
3. push-oriented completion handling,
4. bounded delegation with allowlists and cleanup semantics.

Lotus should selectively translate those operating ideas into its own platform-owned automation and
agent guidance.

## Problem

Today Lotus has asynchronous execution tools, but not yet one durable operating model for them.

Detached engineering work can currently be spread across:

1. GitHub Actions runs,
2. local platform background-run artifacts,
3. asynchronous validation scripts,
4. branch-local PR loops,
5. delegated agent subtasks.

The missing pieces are:

1. one durable task identity model,
2. one lifecycle vocabulary,
3. one ownership and evidence-return model,
4. one delegation posture that keeps write scope, review scope, and status reporting bounded.

Without this RFC:

1. agents can still idle or over-poll rather than work in parallel,
2. detached work can become hard to reconstruct after interruption or compaction,
3. delegation can become under-specified and conflict-prone,
4. async results can surface late or ambiguously,
5. branch and PR hygiene can drift because background work outlives the context that launched it.

## Goals

1. Define a durable background engineering task ledger model for Lotus.
2. Standardize lifecycle and status semantics for detached engineering work.
3. Define a governed delegation model for bounded agent subtasks.
4. Require explicit ownership, evidence return, and cleanup posture for delegated work.
5. Improve async operating discipline across skills, onboarding, and AGENTS guidance.
6. Keep expensive work running in the background while useful foreground work continues.

## Non-Goals

1. Building a general workflow engine for all Lotus business processes.
2. Replacing GitHub Actions as the CI truth source.
3. Turning delegated agents into unconstrained autonomous workers.
4. Creating a hidden background orchestration layer with no human-visible status surface.
5. Replacing repo-local quality ownership with central platform automation.

## Scope Boundary

This RFC governs:

1. background engineering task identity and lifecycle,
2. bounded delegation of engineering subtasks,
3. result and evidence return expectations,
4. skill and context guidance for asynchronous engineering work,
5. cleanup and branch-hygiene rules for detached work.

This RFC does not govern:

1. product-facing workflow-pack runs,
2. business-domain task management,
3. arbitrary multi-agent conversational systems,
4. replacing the existing CI lane model defined by RFC-0072.

## Decision

Lotus will adopt a durable background engineering task ledger and governed delegation model.

Specifically:

1. detached engineering work should be represented as durable task records rather than only as
   transient terminal output,
2. lifecycle status and ownership must remain explicit,
3. delegated agent work must be bounded by scope, write responsibility, and return expectations,
4. completion handling should be push-oriented where possible, not poll-loop-oriented by default,
5. skills, onboarding, and automation must reinforce this operating posture.

## Implementation Status

Current status: **Draft; Slice 1 contract foundation implemented on the active RFC branch**.

The first implementation slice adds the shared agent-engineering contract foundation used by
RFC-0093 and RFC-0094:

1. `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json`,
2. `automation/validate_agent_engineering_contracts.py`,
3. `tests/unit/test_agent_engineering_contracts.py`.

That contract establishes RFC-0094's task identity, lifecycle, evidence, cleanup, authority, and
delegation requirements in machine-readable form. The broader automation, reporting, context,
skills, wiki, and branch-hygiene adoption slices remain open.

No implementation slice may mark RFC-0094 as fully implemented until the platform can point to:

1. a concrete task-ledger contract or artifact shape,
2. automation, skill, context, or onboarding changes that consume that contract,
3. tests or validators for any machine-readable task-ledger output introduced,
4. explicit review evidence for the second-last tightening slice,
5. final documentation, context, wiki, skills/guidance, and branch-hygiene evidence.

GitHub Actions remains the source of truth for GitHub check status. The RFC-0094 ledger may record
and summarize GitHub status, but it must not become a weaker duplicate of GitHub truth.

## Design Principles

### 1. Detached work is still part of one truthful delivery program

Background tasks, GitHub checks, and delegated agents are not separate universes.

They are extensions of the same implementation slice and should remain tied to:

1. branch,
2. PR,
3. repository,
4. owner,
5. evidence.

### 2. A task ledger is a record, not the scheduler itself

The platform may use GitHub, local scripts, or delegated agents to execute work.

The ledger exists to record:

1. what was launched,
2. what state it is in,
3. who owns it,
4. what evidence it produced.

### 3. Delegation must be bounded, not aspirational

Every delegated task should have:

1. a narrow problem statement,
2. an explicit ownership boundary,
3. a defined output,
4. a clear write scope when code changes are involved.

### 4. Polling should be deliberate, not reflexive

The platform should favor:

1. meaningful foreground work,
2. periodic status reads at useful intervals,
3. push-oriented result capture where possible,
4. explicit escalation when a detached task stalls or fails.

### 5. Detached work must end with evidence or explicit failure

A background or delegated task that cannot produce a durable outcome is operationally weak.

## Background Engineering Task Ledger Model

The task ledger should provide one durable record shape for detached engineering work.

### Task categories

At minimum, it should cover:

1. GitHub check or PR-monitoring tasks,
2. local platform background-run tasks,
3. detached validation or QA runs,
4. delegated agent subtasks,
5. merge/cleanup watcher tasks where the platform owns the loop.

### Minimum task identity

1. `engineering_task_id`
2. `task_kind`
3. `repository`
4. `branch`
5. `pr_number` where applicable
6. `owner`
7. `requested_at`
8. `started_at`
9. `ended_at`
10. `origin`
11. `correlation_ref`

### Minimum task metadata

1. `summary`
2. `status`
3. `runtime`
4. `scope`
5. `write_scope` where applicable
6. `artifacts`
7. `evidence_refs`
8. `error_summary`
9. `cleanup_state`

## Task Lifecycle Model

The engineering task ledger should use one bounded status vocabulary.

Recommended states:

1. `QUEUED`
2. `RUNNING`
3. `SUCCEEDED`
4. `FAILED`
5. `TIMED_OUT`
6. `CANCELLED`
7. `LOST`
8. `SUPERSEDED`

### Meaning

1. `QUEUED`
   the task has been created but work has not started.
2. `RUNNING`
   the task is actively executing or owned by a live external system.
3. `SUCCEEDED`
   the task completed with its expected result or evidence.
4. `FAILED`
   the task ended with a meaningful failure.
5. `TIMED_OUT`
   the task exceeded its allowed runtime.
6. `CANCELLED`
   the task was explicitly stopped.
7. `LOST`
   the authoritative runtime or ownership context disappeared unexpectedly.
8. `SUPERSEDED`
   the task is no longer the authoritative active task because a newer task replaced it.

### Lifecycle invariants

1. every detached task must have one durable owner,
2. terminal tasks must carry either evidence or explicit failure context,
3. `LOST` must be treated as an operational problem, not a silent terminal state,
4. status transitions must remain reconstructable after restart or handoff.

## Delegation Model

Delegation should be governed as one bounded task subtype, not as free-form agent fan-out.

### Delegation requirements

Every delegated task must specify:

1. problem statement,
2. expected output,
3. owner,
4. read scope,
5. write scope if any,
6. whether the task is:
   - exploratory,
   - implementation,
   - validation,
   - documentation,
   - review support.

### Code-change delegation rule

If a delegated task can edit code, it must have:

1. an explicit file or module ownership boundary,
2. a clear statement that other workers may also be active,
3. a requirement not to revert unrelated work,
4. a return contract listing changed files and the outcome.

### Read-only delegation rule

Read-only delegated tasks should still return:

1. what was inspected,
2. what was found,
3. whether the result is final, partial, or blocked,
4. what the next local action should be.

## Result and Evidence Return Model

Detached work should return one bounded outcome shape.

### Required return content

1. final status,
2. concise result summary,
3. evidence references,
4. changed files where applicable,
5. blocker or failure explanation where applicable,
6. cleanup posture.

### Evidence examples

1. GitHub Actions run urls,
2. local output JSON or Markdown artifacts,
3. validation summary files,
4. logs,
5. PR numbers,
6. changed file lists,
7. test names and outcomes.

### Task outcome contract

Every detached engineering task should be able to return, in bounded form:

1. task identity,
2. final or current status,
3. concise human-readable summary,
4. evidence refs,
5. changed files or write impact where applicable,
6. blocker or failure reason where applicable,
7. cleanup posture,
8. recommended next local action.

The outcome contract should be short enough to survive handoff and compaction, but explicit enough
to avoid stale or ambiguous status retelling.

## State Authority and Invariants

This RFC establishes the following authority rules.

1. GitHub remains the source of truth for GitHub Actions status,
2. local platform automation remains the source of truth for locally launched background runs,
3. delegated agent return artifacts and status become durable engineering-task evidence once
   recorded,
4. branch and PR state remain source-of-truth in git and GitHub rather than in task summaries,
5. skills and onboarding docs are operating aids, not the authoritative status source.

The following invariants must hold:

1. detached task state must be attributable to one runtime or system of record,
2. evidence refs must point to durable inspectable artifacts or URLs where possible,
3. delegated tasks must not have ambiguous write ownership when code edits are allowed,
4. cleanup posture must be explicit for detached work that changes branch or session state.

## Async Operating Rules

The platform should adopt the following operating rules.

### 1. Launch once, then continue useful work

When a long-running task is detached:

1. start it once,
2. record or reference its durable identity,
3. continue non-overlapping foreground work,
4. poll only when the result is needed or when the watch interval says it is time.

### 2. Prefer periodic polling over busy waiting

Status checks should happen:

1. on useful intervals,
2. when the next local decision depends on them,
3. when a stall threshold is exceeded,
4. when a human asks for status.

### 3. Escalate stale tasks

Queued or running tasks that overrun their expected time should become explicit findings, not quiet
background clutter.

### 3a. Stale-task escalation contract

Stale-task handling should distinguish:

1. `late but still owned`,
2. `stalled and needs inspection`,
3. `lost ownership context`,
4. `superseded by a newer task`,
5. `safe to keep running while foreground work continues`.

The point is not to interrupt useful work reflexively.

The point is to stop stale detached work from becoming invisible.

### 4. Do not claim completion without evidence

A task is not "done" just because the launching agent moved on.

## OpenClaw Reference Findings

OpenClaw is useful as a reference here because its background task and subagent model is explicit
about:

1. task records as detached-work ledgers,
2. push-oriented completion handling,
3. bounded lifecycle states,
4. delegation with session isolation and depth limits,
5. cleanup and archive semantics.

Lotus should adopt the useful patterns:

1. task records as a ledger,
2. explicit lifecycle and ownership,
3. bounded delegation,
4. push-oriented completion where possible.

Lotus should reject:

1. open-ended agent orchestration,
2. weakly governed delegation scopes,
3. runtime models where delegated work can mutate broad state without explicit ownership.

## Cross-Repository Impact

### `lotus-platform`

High impact:

1. automation scripts and output conventions,
2. background-run status artifacts,
3. skills and onboarding updates,
4. PR-loop and async-run guidance,
5. potential validator updates for documentation and contract coherence.

### All Lotus repositories

Medium impact:

1. branch and PR workflow guidance becomes more consistent,
2. repo-local docs may need to align when they expose async or delegated engineering workflows.

### Skill system

High impact:

1. `async-task-runner`,
2. `platform-automation-ops`,
3. PR and QA related skills,
4. any skill that encourages long-running validation or delegated work.

## Alternatives Considered

### Alternative 1: Keep detached work ad hoc and skill-specific

Rejected because it fragments lifecycle truth, ownership, and return expectations.

### Alternative 2: Let delegation remain purely conversational with no durable status model

Rejected because it is too easy to lose state, duplicate work, and report stale outcomes.

### Alternative 3: Build a heavy central orchestration system before defining the operating contract

Rejected because Lotus first needs a truthful lightweight model aligned with existing GitHub and
platform automation reality.

## Implementation Plan

Every implementation slice must end with:

1. focused validation appropriate to the files changed,
2. a review pass for simplification, stale guidance, duplicate policy, and test quality,
3. a small truthful commit,
4. updated PR evidence,
5. updated shared-memory or handoff state when detached work crosses sessions.

### Slice 1: Engineering Task Ledger Contract

1. define task kinds, lifecycle states, and required identity fields,
2. define evidence and cleanup metadata,
3. align local automation artifact shapes with the contract.

Deliverables:

1. contract documentation,
2. background-run artifact shape updates where needed,
3. validator or contract-test targets if platform truth changes.

### Slice 2: Async Operating Guidance Hardening

1. update AGENTS, onboarding, and async skills to reinforce launch-once, poll-deliberately,
   continue-working posture,
2. define stale-task and escalation guidance,
3. align PR monitoring guidance with the same model.

Deliverables:

1. updated guidance docs,
2. updated skills,
3. cross-links to governed automation scripts.

### Slice 3: Governed Delegation Model

1. define bounded delegation types,
2. define required write-scope and return contracts,
3. define cleanup and ownership rules for delegated code changes.

Deliverables:

1. delegation standard text,
2. skill updates for agent delegation,
3. examples and guardrails for bounded task design.

### Slice 4: Automation and Reporting Alignment

1. align platform background-run and PR-loop automation artifacts with the task-ledger model,
2. make result summaries easier to inspect and hand off,
3. ensure artifacts are durable enough for later session resumption.

Deliverables:

1. updated automation outputs where needed,
2. report-shape guidance,
3. truthful status and evidence conventions.

### Slice 5: Validation and Contract-Test Hardening

1. update validators or tests where durable platform truth changes,
2. add targeted checks for required documentation cross-links and contract references,
3. keep repo-native validation truthful.

Deliverables:

1. validator updates,
2. targeted tests,
3. local and CI evidence expectations.

### Slice 6: Code Review, Loose-End Tightening, API Certification Pattern, and Platform Governance

1. review all RFC-0094 implementation changes for duplicated task-state vocabulary, stale async
   guidance, ambiguous task ownership, missing cleanup semantics, and avoidable complexity,
2. verify any API-like or machine-readable contract introduced under this RFC follows the Lotus API
   certification pattern where applicable:
   - stable identity,
   - explicit schema or contract,
   - source-of-truth ownership,
   - validation evidence,
   - degraded, stale, cancelled, lost, and superseded states,
   - OpenAPI or generated-contract alignment when an HTTP endpoint is involved,
3. verify platform governance requirements:
   - RFC-0072 lane evidence,
   - GitHub remains CI truth,
   - local automation remains local-run truth,
   - AGENTS synchronization when the operating contract changes,
   - no unconstrained autonomous delegation,
   - branch and PR cleanup state is explicit,
4. remove stale or conflicting guidance discovered during implementation,
5. decide whether any remaining work must become a follow-up issue before the final slice.

Deliverables:

1. explicit review findings and fixes,
2. targeted validation rerun after review fixes,
3. platform governance checklist evidence,
4. updated gap or follow-up list if the RFC is not yet fully implemented.

### Slice 7: Documentation, Agent Context, Wiki Update, Skill Update if Needed, and Branch Hygiene

1. update docs that now own durable truth under this RFC,
2. update context artifacts where the async and delegation model changes platform behavior,
3. update wiki-source guidance where operator or onboarding posture changes,
4. explicitly assess whether skills, guidance, documentation, wiki, or context should be updated
   for future agent effectiveness,
5. update skills where the implementation changes durable agent workflow guidance,
6. record a conscious "no change needed" decision when a reviewed skill, guidance file, wiki page,
   or context artifact does not need modification,
7. keep PR evidence, branch cleanup, and implementation status truthful.

Deliverables:

1. updated docs and wiki-source pages,
2. updated context files,
3. updated skills where needed,
4. explicit skills/guidance/context/wiki assessment, including "no change needed" decisions,
5. PR and branch-hygiene evidence,
6. no stale guidance that implies implementation beyond what was actually delivered.

## Requirement Traceability

| Requirement | Primary implementation slice | Required evidence before closure |
| --- | --- | --- |
| Durable background engineering task ledger model | Slice 1 | Contract/artifact shape and validation evidence where machine-readable |
| Shared lifecycle vocabulary | Slice 1 | Task-state documentation plus tests/validators where executable |
| Async operating guidance | Slice 2 | AGENTS/onboarding/skill updates or explicit no-change rationale |
| Governed delegation model | Slice 3 | Delegation rules with write-scope and return-contract evidence |
| Automation/reporting alignment | Slice 4 | Background-run or PR-loop artifact updates with evidence refs |
| Executable governance checks | Slice 5 | Repo-native validator/test evidence and PR lane evidence |
| Review and governance closure | Slice 6 | Review findings, fixes, API-certification/platform-governance checklist evidence |
| Final docs/context/wiki/skills/branch hygiene | Slice 7 | Final documentation/context/wiki/skills assessment and branch cleanup evidence |

### Current Evidence

| Evidence | Status | Notes |
| --- | --- | --- |
| `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json` | Implemented on active branch | Captures task identity, lifecycle, evidence, cleanup, authority, delegation, and context-preservation contract requirements |
| `automation/validate_agent_engineering_contracts.py` | Implemented on active branch | Validates the shared RFC-0093/RFC-0094 contract shape |
| `tests/unit/test_agent_engineering_contracts.py` | Implemented on active branch | Proves the contract preserves required lifecycle states, ownership/evidence fields, cleanup posture, delegation guardrails, and identifier-preservation requirements |

## Risks and Mitigations

### Risk: The ledger becomes a second CI system instead of a status contract

Mitigation:

1. keep GitHub as CI truth,
2. keep the ledger focused on detached engineering work identity, status, and evidence,
3. avoid duplicating CI logic in platform docs or automation.

### Risk: Delegation creates merge conflicts or unclear ownership

Mitigation:

1. require explicit write scope,
2. require changed-file reporting,
3. treat bounded ownership as mandatory rather than optional advice.

### Risk: Agents still fall into polling loops despite the guidance

Mitigation:

1. encode the rule in skills and onboarding,
2. reinforce launch-once and periodic-poll posture,
3. keep result return push-oriented where platform automation supports it.

## Validation Posture

This RFC should drive both governed guidance and executable validation where the signal is strong
enough.

The platform should prefer validation for:

1. required documentation and skill cross-links,
2. required background-run artifact references where implementation adopts the ledger contract,
3. required branch/PR hygiene references in skills or onboarding once implemented,
4. obvious contract-shape checks for durable output artifacts where the platform owns those files.

The platform should prefer governed prose rather than brittle automation for:

1. whether a delegated task was well-scoped in a nuanced case,
2. whether a polling interval was reasonable for one specific situation,
3. whether a human or agent made the best foreground/parallelization tradeoff in context.

## Open Questions

1. How much of the task-ledger contract should be materialized in existing `output/*.json` artifacts
   versus new dedicated summary files?
2. Which delegated-work patterns should be platform-standard first:
   documentation, validation, code implementation, or review support?
3. Should `Close-PR-Loop.ps1` and similar automation become the first concrete task-ledger
   consumers under this RFC?

## Acceptance Criteria

1. Lotus has one documented durable background engineering task ledger model.
2. Lotus has one documented lifecycle vocabulary for detached engineering work.
3. Lotus has one documented governed delegation model with bounded scope and return expectations.
4. The RFC defines clear authority boundaries between:
   1. GitHub truth,
   2. local automation truth,
   3. delegated task evidence,
   4. skill guidance.
5. The implementation plan includes a final slice for documentation, agent context, wiki update,
   skill update if needed, and branch hygiene.
6. The implementation plan includes a second-last review and governance slice covering loose-end
   tightening, API certification pattern checks where applicable, and platform governance
   conformance.
7. The final slice includes an explicit skills, guidance, documentation, wiki, and context
   assessment, including conscious "no change needed" decisions when appropriate.
8. No slice under this RFC creates unconstrained autonomous delegation or ambiguous write ownership.

## Final Position

Lotus already knows that long-running engineering work should not block useful foreground progress.

The next step is to make that operating posture durable and governed.

The correct Lotus answer is:

1. a background engineering task ledger,
2. a bounded lifecycle model,
3. a governed delegation contract,
4. explicit evidence return,
5. aligned skills, onboarding, automation, and branch hygiene.

That is the platform-quality path for reliable async engineering work and bounded agent delegation in
the Lotus ecosystem.
