# Agent Context And Task Ledger Playbook

Use this playbook for long-running agent sessions, RFC implementation programs, async validation,
delegated work, and recovery after context compaction.

Governed sources:

1. `rfcs/RFC-0093-lotus-context-assembly-and-compaction-hardening-for-agentic-development.md`
2. `rfcs/RFC-0094-durable-background-engineering-task-ledger-and-governed-delegation-model.md`
3. `rfcs/RFC-0096-governed-multi-agent-delegation-model.md`
4. `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json`
5. `platform-contracts/agent-engineering/delegation-policy-contract.v1.json`
6. `automation/Start-Background-Run.ps1`
7. `automation/Check-Background-Runs.ps1`

## Context Assembly

Start with the smallest correct working set:

1. repo-root `AGENTS.md`,
2. central quickstart and engineering context,
3. repo-local engineering context for the repository being changed,
4. the active RFC and directly referenced contracts or runbooks,
5. failing check output or PR comments only when they are part of the current task.

Do not load broad historical chat or unrelated RFCs as default context. Promote durable lessons into
governed artifacts instead of relying on conversation memory.

## Identifier Preservation

When summarizing, compacting, or handing off work, preserve these identifiers exactly when they are
present:

1. repository,
2. branch,
3. PR number,
4. commit SHA,
5. check name,
6. RFC id,
7. file path,
8. endpoint,
9. contract name,
10. portfolio id,
11. task status.

If an identifier is uncertain, state that it is unknown. Do not invent a value to make the handoff
look complete.

## Detached Task Ledger

For background automation launched through platform scripts:

1. `Start-Background-Run.ps1` creates `output/background-runs.json` entries with
   `engineering_task_id`, `task_kind`, ownership, lifecycle, cleanup, and evidence fields,
2. `Check-Background-Runs.ps1` refreshes those entries from process state and result artifacts,
3. GitHub remains the source of truth for GitHub Actions checks,
4. local automation artifacts remain the source of truth for local background runs.

Use the lifecycle vocabulary from the contract:

1. `QUEUED`,
2. `RUNNING`,
3. `SUCCEEDED`,
4. `FAILED`,
5. `TIMED_OUT`,
6. `CANCELLED`,
7. `LOST`,
8. `SUPERSEDED`.

`LOST` is an operational problem, not success. Treat it as a finding that needs cleanup or
rerun evidence.

## Delegated Work

Delegation is allowed only when the delegated task is bounded, reviewable, and not the immediate
critical-path blocker for the main agent.

Use one governed profile from the delegation policy contract:

1. `exploration`,
2. `implementation`,
3. `validation`,
4. `review_support`,
5. `documentation`,
6. `ci_triage`.

Do not use broad helper profiles such as `general_helper`, `best_effort_worker`, or
`do_everything`.

When delegating or resuming delegated work, record the required input envelope:

1. problem statement,
2. expected output,
3. read scope,
4. task mode or delegation profile,
5. explicit write scope when edits are allowed, or `none` for no-write work,
6. forbidden actions,
7. evidence requirements,
8. coordination notes,
9. required return envelope.

Delegated work must return:

1. outcome summary,
2. files changed, if any,
3. tests or checks run,
4. evidence refs,
5. blockers or assumptions,
6. remaining risks,
7. follow-up required or `none`,
8. confirmation that unrelated work was not reverted,
9. patch summary grouped by owned write scope when implementation changed files.

Delegated code changes are evidence, not review. The main agent must review returned diffs, reject
out-of-scope edits, run focused checks after integration, and preserve one accountable owner for PR
posture, wiki publication, merge readiness, and final communication.

Treat overlapping active write scopes as a coordination problem. Pause, cancel, or supersede one
task before integrating conflicting changes. Treat `LOST`, `TIMED_OUT`, and `FAILED` delegated work
as findings that need fix-forward, explicit cancellation, or supersession evidence.

## Promotion Decisions

After each slice, decide whether new knowledge belongs in:

1. repository docs,
2. central context,
3. onboarding docs,
4. wiki source,
5. skill guidance,
6. validator or contract tests,
7. RFC follow-up items.

If no durable artifact should change, record that as a conscious decision in PR evidence or the
slice review notes.
