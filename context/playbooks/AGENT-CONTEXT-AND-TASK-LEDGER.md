# Agent Context And Task Ledger Playbook

Use this playbook for long-running agent sessions, RFC implementation programs, async validation,
delegated work, and recovery after context compaction.

Governed sources:

1. `rfcs/RFC-0093-lotus-context-assembly-and-compaction-hardening-for-agentic-development.md`
2. `rfcs/RFC-0094-durable-background-engineering-task-ledger-and-governed-delegation-model.md`
3. `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json`
4. `automation/Start-Background-Run.ps1`
5. `automation/Check-Background-Runs.ps1`

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

When delegating or resuming delegated work, record:

1. problem statement,
2. expected output,
3. read scope,
4. task mode,
5. explicit write scope when edits are allowed.

Delegated code changes must return changed files and an outcome summary. Delegated workers must not
revert unrelated work.

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
