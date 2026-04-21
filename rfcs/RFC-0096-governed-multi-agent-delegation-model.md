# RFC-0096: Governed Multi-Agent Delegation Model

- Status: Draft
- Date: 2026-04-21
- Owners:
  - lotus-platform governance
  - Codex/agent operating-contract maintainers
- Target repositories:
  - `lotus-platform`
- Depends on:
  - `RFC-0093-lotus-context-assembly-and-compaction-hardening-for-agentic-development.md`
  - `RFC-0094-durable-background-engineering-task-ledger-and-governed-delegation-model.md`
  - `RFC-0095-heartbeat-driven-monitoring-and-attention-surfacing.md`

## Summary

Lotus should use parallel agent work only under explicit governance. This RFC defines bounded
delegation profiles, task ownership, write scopes, evidence-return requirements, review rules, and
failure semantics for multi-agent engineering work.

The goal is not to maximize parallelism. The goal is to make parallel work safe, auditable, and
useful without losing ownership, reverting unrelated changes, or weakening review discipline.

## Problem

Large Lotus RFCs often span multiple repositories, long-running CI, documentation, wiki publication,
and post-merge hygiene. Parallel agents can help with exploration, validation, and bounded
implementation slices, but unmanaged delegation creates risks:

1. overlapping writes,
2. unclear ownership,
3. stale or incomplete findings,
4. duplicate analysis,
5. unreviewed generated changes,
6. hidden task state after context compaction,
7. weak evidence when sub-work returns.

RFC-0094 introduced delegation contract foundations. This RFC turns those foundations into an
operating model.

## Goals

1. Define approved delegation profiles.
2. Require explicit read and write scopes.
3. Require durable task identity and evidence refs for delegated work.
4. Define when delegation is allowed and when work must remain local.
5. Define subtask output requirements.
6. Add validation and context guidance so future agents follow the model.
7. Preserve human-readable review discipline after every delegated slice.

## Non-Goals

1. Creating unrestricted nested agent trees.
2. Allowing agents to edit overlapping write scopes without coordination.
3. Replacing code review with delegation output.
4. Delegating immediate blockers when the main task cannot progress without the result.
5. Creating a new hidden memory store for delegated work.

## Delegation Profiles

| Profile | Purpose | Write permission |
| --- | --- | --- |
| `exploration` | answer a bounded codebase or docs question | none |
| `implementation` | implement a narrow slice in a declared file/module set | explicit write scope required |
| `validation` | run checks, inspect failures, summarize evidence | none unless approved |
| `review-support` | inspect diff for risks, missing tests, stale docs | none |
| `documentation` | update a bounded docs/wiki/context scope | explicit write scope required |

## Required Delegation Input

Every delegated task must include:

1. problem statement,
2. expected output,
3. repository and branch,
4. read scope,
5. write scope or explicit no-write statement,
6. task mode,
7. evidence requirements,
8. reminder not to revert unrelated work,
9. expected return shape.

## Required Delegation Output

Delegated work must return:

1. outcome summary,
2. files changed, if any,
3. tests or checks run,
4. evidence refs,
5. blockers or assumptions,
6. remaining risks,
7. whether follow-up is required.

## Implementation Plan

### Slice 1: Delegation Policy Contract

1. Extend or add a platform contract for delegation profiles.
2. Align it with RFC-0094 `delegation_contract`.
3. Add validator and focused tests.

Review gate:

1. ensure profile names are bounded,
2. ensure write-scope rules are explicit,
3. avoid duplicating RFC-0094 task identity fields.

### Slice 2: Agent Operating Guidance

1. Update AGENTS operating contract.
2. Update context playbooks.
3. Update skill routing guidance if needed.
4. Add examples of good delegation prompts and bad delegation prompts.

Review gate:

1. confirm the guidance discourages delegation of immediate blockers,
2. confirm subagent output is evidence-bearing,
3. confirm no new agent mode conflicts with existing Codex instructions.

### Slice 3: Task Ledger Integration

1. Record delegated tasks through RFC-0094-compatible task fields.
2. Define how delegated task status maps to main task status.
3. Add support for superseded or abandoned delegated tasks.

Review gate:

1. verify GitHub truth and local automation truth are not redefined,
2. verify `LOST` delegated work is visible and not treated as success,
3. add tests for terminal and abandoned states.

### Slice 4: Review And Merge Discipline

1. Define the main-agent review obligations after delegated code changes.
2. Require conflict checks before accepting delegated edits.
3. Require focused tests after integration.
4. Add docs for rejecting low-quality delegated output.

Review gate:

1. confirm the model preserves one accountable owner,
2. confirm delegated changes cannot bypass PR checks,
3. confirm evidence hierarchy is preserved.

### Slice 5: Heartbeat Integration

1. Feed stale delegated task posture into RFC-0095 heartbeat attention items.
2. Surface missing evidence, stale running state, or unresolved delegated blockers.
3. Add tests using synthetic ledger records.

Review gate:

1. ensure heartbeat reads task truth without redefining it,
2. ensure duplicate stale-task alerts are deduplicated,
3. ensure no alert is raised for intentionally closed tasks.

### Slice 6: Code Review, API Certification, And Governance Tightening

Second-last mandatory slice.

1. Review delegation contracts, docs, context, and tests for duplication.
2. Confirm machine-readable artifacts follow the certification pattern.
3. Confirm no dead or stale agent guidance remains.
4. Tighten examples to repo-native Lotus workflows.

### Slice 7: Documentation, Context, Wiki, Skills, And Branch Hygiene

Final mandatory slice.

1. Update documentation and central agent context.
2. Update wiki source if operator or agent-facing behavior changed enough for publication.
3. Assess whether a new skill is needed or existing skills should be tightened.
4. Run wiki sync checks and publish after merge if needed.
5. Record final evidence and branch cleanup.

## Acceptance Criteria

1. Delegation profiles are machine-readable or otherwise validator-protected.
2. AGENTS/context guidance tells future agents when and how to delegate.
3. Delegated code changes require explicit write scope and main-agent review.
4. Stale, failed, lost, and superseded delegated tasks have clear status semantics.
5. Heartbeat integration can surface stale delegated work.
6. Final docs/context/wiki/skills/branch hygiene is complete.

## Initial Priority

Implement second. Heartbeat monitoring should land first so delegated tasks can be observed.
