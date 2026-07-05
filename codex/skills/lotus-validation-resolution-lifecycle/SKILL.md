---
name: lotus-validation-resolution-lifecycle
description: End-to-end Lotus application validation and issue-resolution lifecycle skill. Use when the user asks to bring up and test an app, validate against lotus-platform standards, open and track defects with evidence, implement and verify fixes, raise/merge PRs, and revalidate until the service is stable and production-ready.
---

# Lotus Validation Resolution Lifecycle

Before substantial lifecycle work, read:

1. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
2. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md`
3. the target repo `REPOSITORY-ENGINEERING-CONTEXT.md`

Use:

1. `lotus-platform/context/playbooks/VALIDATION-PLAYBOOK.md` for validation-depth choices,
2. `lotus-platform/context/playbooks/PR-LOOP-PLAYBOOK.md` for PR progression and merge hygiene,
3. `lotus-platform/context/playbooks/FIX-FORWARD-PATTERNS.md` when failures recur.

If the lifecycle task is specifically about canonical front-office populated-panel proof or demo
screenshots, compose this skill with `lotus-front-office-runtime` instead of relying on generic QA
validation alone.

Run this lifecycle:
1. Bring up application and run API/observability/platform checks.
2. Raise or reuse detailed defects in the target repository.
3. Implement fixes and open PRs with `Fixes #<issue>` links.
4. Monitor PR merge status.
5. Revalidate post-merge and update/close issues based on evidence.
6. Repeat until no blocking findings remain.

Async rule:

1. use truthful local proof first,
2. let GitHub run heavy PR checks where possible,
3. continue implementation or analysis while checks run,
4. return to fix-forward work only when a real failure log exists.

## Core Commands

Validate and sync issue statuses:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\run-lifecycle.ps1 -RepoAlias lotus-risk -RepoSlug sgajbi/lotus-risk -Phase fullcycle -BringUp -AutoCloseResolved
```

Monitor merged PR then auto-revalidate:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\run-lifecycle.ps1 -RepoAlias lotus-risk -RepoSlug sgajbi/lotus-risk -Phase monitorpr -PrNumber 123 -BringUp -AutoCloseResolved
```

Validate only:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\run-lifecycle.ps1 -RepoAlias lotus-risk -RepoSlug sgajbi/lotus-risk -Phase validate -BringUp
```

## Issue Quality Requirements

For each defect issue, include:
- evidence path(s)
- reproduction steps
- expected vs actual
- root-cause hypothesis (when identifiable)
- why existing tests missed it
- recommended regression coverage

## PR and Merge Rules

- Open PRs with issue linkage (`Fixes #<issue>`).
- Do not merge if required checks fail.
- After merge, re-run lifecycle validation.
- Close issues only when QA evidence confirms fix.
- For GitHub-visible lifecycle tracking, use the `gh-issue-fix-qa-loop` status label vocabulary:
  `status/in-progress`, `status/fixed-local`, `status/pr-open`, `status/merged-main`, and `status/blocked`.
  Move labels when state changes; do not rely on chat summaries for issue status visibility.

Use [Lifecycle-Map](references/lifecycle-map.md) and [Defect-Quality-Bar](references/defect-quality-bar.md) for expected behavior.
## Continuous Skill Improvement

At the end of any meaningful use of this skill, decide whether the work exposed a repeatable failure
mode, missing step, weak trigger, validation gap, or context-routing gap. If yes, update the
platform-owned skill source under `lotus-platform/codex/skills/<skill-name>` or its relevant
reference/script in the same delivery slice when the improvement is small and safe. For broader
learning, create a focused follow-up issue or PR instead of relying on chat memory.

Use this decision order:

1. tighten this skill when future agents need different behavior;
2. update `context/LOTUS-SKILL-ROUTING-MAP.md` when routing or overlap changed;
3. update central or repo-local context when source-of-truth changed;
4. add or adjust validators, scaffolds, or gates when deterministic enforcement is better than prose;
5. record an explicit no-change decision in PR evidence, the review ledger, or the task ledger when no durable update is justified.


