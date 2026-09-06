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
Read the target repository's AGENTS.md, <lotus-platform>/context/LOTUS-QUICKSTART-CONTEXT.md, the target repository's REPOSITORY-ENGINEERING-CONTEXT.md, and <lotus-platform>/context/LOTUS-SKILL-ROUTING-MAP.md. Load only the task-specific RFC, contract, playbook, or standard selected by those sources. Summarize the repo, branch, task intent, owner, applicable skill, validation lane, and completion evidence before changing files.
```

Use this workspace-root prompt when the Lotus workspace path is known:

```text
Read the target repository's AGENTS.md, <workspace-root>/lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md, the target repository's REPOSITORY-ENGINEERING-CONTEXT.md, and <workspace-root>/lotus-platform/context/LOTUS-SKILL-ROUTING-MAP.md. Load only the task-specific RFC, contract, playbook, or standard selected by those sources. Summarize the repo, branch, task intent, owner, applicable skill, validation lane, and completion evidence before changing files.
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
11. whether new or moved files belong in an existing domain-owned package, a new cohesive
    subpackage, or an explicitly tracked cleanup issue instead of a broad bucket such as `services`,
    `utils`, `helpers`, or `scripts`.

If any of these are unclear, inspect the repository and context map before implementing.

## Context Budget Tiers

### Tier 1: Startup Context

Default for most tasks.

Load:

1. the target repository's `AGENTS.md`,
2. [Lotus Quickstart Context](../../context/LOTUS-QUICKSTART-CONTEXT.md),
3. the target repository's `REPOSITORY-ENGINEERING-CONTEXT.md`,
4. [Lotus Skill Routing Map](../../context/LOTUS-SKILL-ROUTING-MAP.md) and the selected skill.

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
5. repository context or platform standards updates,
6. agentic coding quality evaluation, eval dataset design, or promotion of repeated agent failure
   modes into deterministic gates.

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

## Fresh-Start Walkthrough

Test an onboarding change without prior chat context:

1. Start at the repository README and `AGENTS.md`; identify product purpose and mandatory rules.
2. Follow the quickstart and repository context; identify the owning component and its boundaries.
3. Use the skill-routing map; name the skill and why it applies.
4. Follow one representative task route to its specialist contract or runbook.
5. Find the smallest local validation and the required PR, exact-main, wiki, and hygiene evidence.
6. Repeat without a sibling Platform checkout by using the canonical GitHub links.

Record the paths followed and any tool-specific behavior that was not actually verified. A
successful walkthrough must not depend on a personal directory, remembered issue state, or an
undocumented command.

## Skill Selection

Use skills when the task matches their scope.

Common Lotus skill routes:

| Task | Skill Or Workflow |
| --- | --- |
| canonical populated Workbench runtime, demo screenshots, panel validation | `lotus-front-office-runtime` |
| backend implementation or review | `lotus-backend-delivery-governance` |
| frontend implementation or review | `lotus-frontend-delivery-governance` |
| PR merge or pre-merge checks | `lotus-pr-premerge-gate` |
| GitHub CI failure fix-forward | `gh-fix-ci` from platform-owned skill source; GitHub plugin CI skill may supplement repository metadata |
| GitHub PR review-thread handling | `gh-address-comments` from platform-owned skill source |
| CI quality-gate design or report-only inventory promotion | `lotus-ci-enforcement-governance` |
| agentic coding quality evaluation or anti-slop feedback loops | `lotus-ci-enforcement-governance` plus [Agentic Coding Quality Evaluation Loop](../../context/playbooks/AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md) |
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

## Implementation Non-Degradation Bar

Before implementation, write a short quality intake from the actual codebase. It should name the
existing owner patterns, source of truth, closest meaningful tests, repo-native validation command,
and measurable quality signal the slice will improve or preserve. If the agent cannot name those
items, it should keep reading instead of writing plausible code.

For backend implementation, use `lotus-backend-delivery-governance` as more than a PR checklist.
Before coding, identify which measured quality signals can regress in the touched area: duplicate
implementation, architecture boundaries, security scanner posture, API/OpenAPI truth, vocabulary and
contract validation, complexity/function size, test-family breadth, uncategorized-test growth, and
supportability evidence.

The default acceptable backend slice either improves one of those signals or preserves it while
delivering tested behavior. Do not treat passing tests alone as enough when the diff adds copy-paste,
new boundary drift, weak mocks-only tests, stale allowlists, or optimistic documentation that is not
backed by implementation.

For RFC-driven or proof-driven work, do not move to the next slice until the current slice has a
closure manifest in the PR, RFC ledger, task ledger, or repo-local proof document. It should record
blockers cleared, blockers intentionally preserved, proof artifacts, commands, docs/wiki and
supported-feature decisions, merge method, post-merge validation, and branch cleanup evidence.
Before deleting local or remote branches, verify merge or superseded status with PR state plus
`git log`, `git diff`, or cherry-pick evidence so implementation code and durable truth are not
lost during hygiene.

For CI enforcement work, do not use total test count as the only quality proxy. If a repository has
a deterministic test taxonomy or proof-breadth inventory, check whether API/runtime,
contract/governance, observability/security, or domain-methodology families can regress even when
the total number of tests rises.

For frontend implementation, use `lotus-frontend-delivery-governance` as more than visual polish.
Before coding, identify which product-surface signals can regress: backed API truth, state handling,
accessibility, layout stability, duplicated view-model/business logic, stale fixtures, browser
validation, and canonical runtime proof for governed Workbench surfaces.

The default acceptable frontend slice either improves one of those signals or preserves it while
delivering validated behavior. Do not treat render-only tests or screenshots as enough when the diff
adds unsupported UI behavior, copied calculations, unvalidated layout changes, or text that explains
missing functionality instead of implementing supported workflow behavior.

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
5. `powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory <path>` from `lotus-platform` when the task requires a platform-owned run summary, runtime transcript, and caller-directed screenshot pack.
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
4. [Agentic Coding Quality Evaluation Loop](../../context/playbooks/AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md)
   when repeated agent-authored code, test, documentation, or CI failures should become measured
   gates, scorecards, evaluator cases, skills, or context guidance.

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

When CI enforcement is the repeatable pattern, update the platform-owned skill source and central
skill routing context, then run the developer-environment bootstrap or validation automation so
local agent skill copies and `AGENTS.md` remain synchronized.

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
11. adding copy-pasted backend logic, broad unmeasured rewrites, or mocks-only tests and calling that
    production-grade progress.
12. starting code changes before naming the existing owner pattern, source of truth, closest tests,
    validation command, and measurable quality signal for the slice.
13. deleting branches because they look stale without proving their unique commits and durable
    truth are already merged, cherry-picked, or explicitly superseded.
14. adding source, tests, scripts, workflows, contracts, or docs to a broad folder without first
    naming the owning layer, bounded concern, permanent filename, and any deferred cleanup issue.

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
