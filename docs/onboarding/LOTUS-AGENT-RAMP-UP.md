# Lotus Agent Ramp-Up

Use this guide at the start of a new coding-agent chat.

This is the agent-facing companion to [Lotus Developer Onboarding](./LOTUS-DEVELOPER-ONBOARDING.md). It assumes the workspace exists and focuses on loading the right context, selecting the right skills, and avoiding context-window waste.

This guide is governed by:

1. [RFC-0073](../../rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md)
2. [RFC-0074](../../rfcs/RFC-0074-repeatable-developer-and-agent-bootstrap-system.md)
3. [Lotus Quickstart Context](../../context/LOTUS-QUICKSTART-CONTEXT.md)
4. [Lotus Engineering Context](../../context/LOTUS-ENGINEERING-CONTEXT.md)
5. [Context Reference Map](../../context/CONTEXT-REFERENCE-MAP.md)
6. [Procedural Memory Index](../../context/PROCEDURAL-MEMORY-INDEX.md)
7. [AGENTS Operating Contract](../../context/AGENTS-OPERATING-CONTRACT.md)
8. [Lotus Skill Routing Map](../../context/LOTUS-SKILL-ROUTING-MAP.md)

## Purpose

A new chat should become useful quickly without relying on prior conversation memory.

The agent should:

1. load the smallest correct context set,
2. identify the target repository and branch,
3. identify the governing RFC, standard, or playbook,
4. select the right skill for the task,
5. choose the right validation lane before making changes,
6. use GitHub asynchronously for long-running checks,
7. update durable context docs when platform or repository truth changes.

The agent should not load every Lotus document by default.

## First Prompt Template

Use this path-agnostic prompt on a new machine:

```text
Read <lotus-platform>/context/LOTUS-QUICKSTART-CONTEXT.md, then <lotus-platform>/context/CONTEXT-REFERENCE-MAP.md, then the target repository's REPOSITORY-ENGINEERING-CONTEXT.md if present. Load only the RFC, skill, playbook, or standard needed for this task. Summarize the repo, branch, task intent, applicable standards, and validation lane before making changes. Keep context lean, use GitHub asynchronously for long-running checks, and update durable context docs when platform or repo reality changes.
```

Use this workspace-root prompt when the Lotus workspace path is known:

```text
Read <workspace-root>/lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md, then <workspace-root>/lotus-platform/context/CONTEXT-REFERENCE-MAP.md, then the target repository's REPOSITORY-ENGINEERING-CONTEXT.md if present. Load only the RFC, skill, playbook, or standard needed for this task. Summarize the repo, branch, task intent, applicable standards, and validation lane before making changes. Keep context lean, use GitHub asynchronously for long-running checks, and update durable context docs when platform or repo reality changes.
```

## First-Turn Checklist

Before editing files, the agent should identify:

1. target repository,
2. current branch,
3. task intent,
4. applicable RFC or standard,
5. required Lotus skill or workflow,
6. smallest local validation lane,
7. GitHub checks or PRs to monitor asynchronously,
8. whether durable context or repository-local documentation may need an update.
9. whether the task is actually a front-office runtime or UI-proof task that must use the governed `lotus-workbench` live runtime path.
10. whether the task should be routed through `LOTUS-SKILL-ROUTING-MAP.md` before loading broader skills.

If any of these are unclear, inspect the repository and context map before implementing.

## Context Budget Tiers

### Tier 1: Startup Context

Default for most tasks.

Load:

1. [Lotus Quickstart Context](../../context/LOTUS-QUICKSTART-CONTEXT.md)
2. [Context Reference Map](../../context/CONTEXT-REFERENCE-MAP.md)
3. the target repository's `REPOSITORY-ENGINEERING-CONTEXT.md`
4. task-specific skill instructions when a skill matches the work

Use Tier 1 for:

1. small code changes,
2. targeted bug fixes,
3. focused documentation updates,
4. straightforward PR follow-up,
5. narrow UI or backend tasks with clear ownership.

For focused documentation updates, also load
[Lotus Documentation Layering](../documentation/LOTUS-DOCUMENTATION-LAYERING.md) before editing
README, wiki, or deep-doc structure.

### Tier 2: Governance Context

Use when the task affects standards, CI, runtime, cross-repository contracts, or platform architecture.

Load:

1. Tier 1,
2. the active RFC for the work,
3. the relevant platform standard,
4. a procedural playbook from [Procedural Memory Index](../../context/PROCEDURAL-MEMORY-INDEX.md)

Use Tier 2 for:

1. RFC-driven slice implementation,
2. CI lane or workflow changes,
3. API vocabulary or contract governance,
4. cross-app integration changes,
5. repository context or platform standards updates.

### Tier 3: Deep Context

Use only when broad reasoning is required.

Load:

1. Tier 2,
2. [Lotus Engineering Context](../../context/LOTUS-ENGINEERING-CONTEXT.md)
3. [Recent Architectural Decisions Digest](../../context/recent-architectural-decisions-digest.md)
4. [Platform Engineering Ledger](../../context/platform-engineering-ledger.md)
5. specific historical RFCs or runbooks referenced by the context map

Use Tier 3 for:

1. cross-repo incident resolution,
2. broad architecture changes,
3. large refactors,
4. ambiguous ownership decisions,
5. repeated failures where the underlying pattern must be codified.

Do not start with Tier 3 by default.

## Skill Selection

Use skills when the task matches their scope.

Common Lotus skill routes:

| Task | Skill Or Workflow |
| --- | --- |
| canonical populated Workbench runtime, demo screenshots, panel validation | `lotus-front-office-runtime` |
| backend implementation or review | `lotus-backend-delivery-governance` |
| frontend implementation or review | `lotus-frontend-delivery-governance` |
| PR merge or pre-merge checks | `lotus-pr-premerge-gate` |
| GitHub CI failure fix-forward | `gh-fix-ci` or GitHub plugin CI skill |
| platform validation and QA | `lotus-qa-platform-validator` |
| RFC quality and review loop | `lotus-rfc-review-loop` |
| async automation monitoring | `async-task-runner` or `platform-pulse-monitor` |

If no skill fits, use the repository context, task routing guide, and procedural playbooks before inventing a new process.

When multiple skills seem to fit, resolve the overlap through
[Lotus Skill Routing Map](../../context/LOTUS-SKILL-ROUTING-MAP.md) instead of guessing from
descriptions alone.

## Validation Lane Selection

Select validation before implementation.

| Work Type | Default Local Validation | GitHub / Async Validation |
| --- | --- | --- |
| documentation-only | targeted doc tests, context validator | Feature Lane, PR Merge Gate |
| backend logic | touched unit tests, lint/typecheck for changed scope | PR Merge Gate, Docker/E2E if relevant |
| frontend UI | lint/typecheck/unit tests, targeted browser proof when needed | PR Merge Gate and platform UI validation if cross-app |
| CI or platform automation | script tests, validator tests, dry-run/inspect mode | platform PR checks |
| runtime or ingress | targeted platform scripts, no hidden restarts | platform validation lane when required |

Prefer targeted local checks and GitHub-backed heavy execution. Do not repeatedly run full local CI when GitHub can run the expensive matrix while the agent continues useful work.

## Front-Office Runtime Routing

When the task is about:

1. Workbench demo readiness,
2. populated screens or panels,
3. screenshot capture,
4. canonical UI proof,
5. front-office seeded runtime validation,

route to the governed `lotus-workbench` runtime first:

1. `../../../lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`
2. `npm run live:stack:up`
3. `npm run live:validate`
4. `npm run live:stack:down`
5. `powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory <path>` from `lotus-platform` when the task requires a platform-owned run summary and caller-directed screenshot pack.
6. `../../context/contracts/canonical-front-office-demo-data-contract.json`
7. `../../context/contracts/canonical-front-office-demo-data-invariants.json`
8. `../../context/contracts/workbench-panel-registry.json`

Use `PB_SG_GLOBAL_BAL_001` unless the task explicitly requires another portfolio.
Use the RFC-0076 contract files when you need the governed as-of date, benchmark identity, minimum
supportability thresholds, or machine-readable canonical dataset truth.
Use the RFC-0077 panel registry when the task changes a governed Workbench screen, sub-screen,
panel classification, screenshot ownership, or support-state posture.

Do not default to `lotus-platform/platform-stack` as the primary front-office product bring-up path. That path owns shared infrastructure assets and ingress support, but the governed populated product-surface flow lives in `lotus-workbench`.

Treat `lotus-front-office-runtime` as the primary skill route for these tasks. Use broader frontend,
QA, or PR skills only as supporting guidance once the runtime path is selected.

Demo-ready screenshots are valid only after canonical endpoint, calculation, and panel validation passes. Keep diagnostic captures separate with a `diagnostic-` prefix.

## Async GitHub Monitoring

When checks are already running in GitHub:

1. keep implementation moving on non-conflicting work,
2. poll with `gh pr checks <pr-number> --watch=false`,
3. inspect failures with `gh run view <run-id> --log-failed`,
4. fix-forward in the same branch,
5. rerun only targeted local checks for the fix,
6. push and let GitHub rerun full gates.

Use:

1. [PR Loop Playbook](../../context/playbooks/PR-LOOP-PLAYBOOK.md)
2. [Validation Playbook](../../context/playbooks/VALIDATION-PLAYBOOK.md)
3. [Fix-Forward Patterns](../../context/playbooks/FIX-FORWARD-PATTERNS.md)

## Context Maintenance Rule

Update durable context when the task changes durable truth.

Update central context when:

1. platform architecture changes,
2. validation lane policy changes,
3. skill or agent workflow expectations change,
4. cross-repository ownership changes,
5. a repeatable pattern becomes durable platform guidance.

Update repository-local context when:

1. repo-native commands change,
2. local module ownership changes,
3. repo-specific runtime setup changes,
4. repo-specific constraints or pitfalls change.

Do not update durable context for transient CI state unless it becomes a repeatable pattern.

## Anti-Patterns

Avoid:

1. loading every RFC before understanding the task,
2. treating prior chat memory as source of truth,
3. implementing UI-only features without backend capability,
4. running full local CI after every small fix,
5. overwriting global `AGENTS.md` or local skills without explicit sync semantics,
6. duplicating platform policy prose into repository-local docs,
7. ignoring GitHub failures because local checks passed,
8. marking a slice complete without tests or context links.
9. treating `lotus-platform/platform-stack` as the canonical populated front-office runtime when `lotus-workbench` already owns that governed flow.
10. treating `PB_SG_GLOBAL_BAL_001` as a generic smoke fixture rather than a governed contract-backed dataset.

## Current RFC-0074 Boundary

RFC-0074 is implemented and governed.

Current bootstrap support includes:

1. platform-owned Lotus skills under `lotus-platform/codex/skills`,
2. read-only developer-environment inspection through `automation/Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast`,
3. governed Lotus skill and `AGENTS.md` synchronization through `automation/Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast`,
4. redacted readiness reports at `output/developer-environment-readiness.json` and `output/developer-environment-readiness.md`,
5. drift controls through `automation/validate_engineering_context_system.py` and `tests/unit/test_developer_environment_bootstrap.py`,
6. repository-local context links back to the central onboarding and agent ramp-up guides.

Do not duplicate this guide into repository-local context documents. Keep local repository context focused on repo-specific commands, boundaries, and constraints, and link back here for agent ramp-up behavior.
