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

Use [Lifecycle-Map](references/lifecycle-map.md) and [Defect-Quality-Bar](references/defect-quality-bar.md) for expected behavior.
