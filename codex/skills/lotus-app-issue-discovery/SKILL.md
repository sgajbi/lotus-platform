---
name: lotus-app-issue-discovery
description: Use when reviewing Lotus applications lens by lens to find high-value, evidence-backed GitHub issues without editing code. Applies when the user asks to inspect a Lotus repo for architecture, runtime composition, API, HTTP boundary controls, domain, lifecycle, mapping, data model, database operations, calculations, security, observability, performance, resilience, testing, CI/release evidence, documentation, operational supportability, or bank-buyable readiness issues; when they want defects raised for another implementation agent; or when a reusable issue-discovery campaign should avoid duplicates, maintain a GitHub ledger, apply canonical lens labels, cite code evidence, and use docs repo knowledge plus Lotus platform standards as the review baseline.
---

# Lotus App Issue Discovery

## Overview

Use this skill to run a disciplined issue-discovery campaign across a Lotus app. Inspect code first,
avoid duplicates, and raise only high-value issues that another agent can triage and fix.

Use this skill with the relevant app delivery governance skill:

- backend services: `lotus-backend-delivery-governance`
- frontend product surfaces: `lotus-frontend-delivery-governance`
- runtime validation or service QA: `lotus-qa-platform-validator`
- CI/gate design: `lotus-ci-enforcement-governance`
- persistent review-ledger work: `lotus-codebase-review-ledger`

Do not edit code unless the user explicitly asks for fixes. This skill is for review and issue
creation.

## Operating Posture

Act like a senior Lotus review lead, not a bug-title generator.

For every issue, prove four things before filing:

1. the repository evidence exists,
2. the expected behavior is grounded in Lotus standards, the docs knowledge base, repo context, or
   accepted industry/domain practice,
3. the finding is not already covered by an open, closed, or actively fixed issue,
4. the issue is fixable as a coherent implementation slice with clear acceptance criteria.

Prefer fewer, stronger issues. If a finding is speculative, stale, duplicate, or below the
bank-buyable bar, record it in the ledger as residual risk instead of filing noise.

## Required Context

Load the smallest correct context set:

1. target repo `AGENTS.md`
2. `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`
3. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
4. target repo `REPOSITORY-ENGINEERING-CONTEXT.md`
5. `lotus-platform/context/CONTEXT-REFERENCE-MAP.md`
6. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md` for long-running campaign execution
7. `lotus-platform/context/LOTUS-SKILL-ROUTING-MAP.md`
8. `lotus-platform/context/playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md` for backend issue lenses
9. `lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`
10. relevant docs knowledge-base pages from the sibling repository `<workspace-root>/docs` when
   present, especially product, technical, data-model, transaction/position lifecycle, methodology,
   API, security, observability, DevOps, and operations references that match the lens
11. app-specific RFCs, standards, methodology docs, or source contracts when the lens needs them

Use the sibling docs repo knowledge base when present, Lotus platform context, repository
engineering context, and `ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md` as the standard for
review. Do not treat local code convention as sufficient when it contradicts those sources. If the
docs repo is absent from the workspace, record that context gap in the ledger and do not claim a
docs-backed review for that lens.

For the lens catalog, read `references/review-lenses.md`. Also use that file for canonical GitHub
label names, the baseline lens queue, and search starters. For a reusable campaign ledger shape,
read `references/lens-coverage-ledger-template.md` when starting or resuming a multi-lens defect
discovery campaign.

## Docs Knowledge Routing

Use the sibling docs repository at `<workspace-root>/docs` as a knowledge base, not as decorative
background. Load only the pages that match the current lens:

- product, lifecycle, transaction, position, cash-flow, instrument-static, source-ownership, and
  calculation lenses: `docs/docs/products/`
- backend boundaries, API contracts, data products, CI/CD, infrastructure, SRE, security,
  performance, testing, documentation, and leadership lenses: `docs/docs/technical/`
- wealth-platform architecture, strategy, operating model, and domain-engineering lenses:
  `docs/docs/reference/`
- reusable prompt or agent-workflow lenses: `docs/docs/prompts/`

High-signal product anchors include:

- `docs/docs/products/cross-product-transaction-position-data-model.md`
- `docs/docs/products/product-lifecycle-cashflow-and-event-guide.md`
- `docs/docs/products/product-calculation-example-catalog.md`
- `docs/docs/products/source-ownership-calculation-reporting-matrix.md`
- `docs/docs/products/product-taxonomy-and-vocabulary-guide.md`

High-signal technical anchors include:

- `docs/docs/technical/backend-service-design/`
- `docs/docs/technical/api-contract-engineering/`
- `docs/docs/technical/data-product-engineering/`
- `docs/docs/technical/cicd-devsecops-release-evidence/`
- `docs/docs/technical/observability-sre-supportability/`
- `docs/docs/technical/security-cyber-resilience/`
- `docs/docs/technical/performance-scalability-resilience-async/`
- `docs/docs/technical/testing-quality-certification/`
- `docs/docs/technical/documentation-knowledge-governance/`

When filing an issue, cite docs or platform standards only when they materially explain why the code
is wrong, incomplete, or risky. Do not turn the issue into a generic essay; keep it tied to the
target repository evidence.

## Workflow

### 1. Establish Scope

Confirm:

- repository and branch,
- app role in the Lotus ecosystem,
- current lens,
- whether the user wants GitHub issues only or code changes too,
- issue target repository,
- existing local worktree changes that must not be touched.

If the user asks for "next N issues", keep the scope to one coherent lens or a named lens group.
If the user asks broadly to "find issues", choose the next highest-value lens from the ledger and
the baseline lens queue in `references/review-lenses.md`.

For a multi-turn or multi-lens campaign, create or update a lens coverage ledger before filing more
issues. Prefer one GitHub issue per Lotus app named `<app> Issue Discovery Ledger` when multiple
agents are working, implementation branches are active, or the user wants shared campaign state.
Use a repo-local ledger only when the review campaign itself is part of a committed documentation
slice. Use a temp note only as a short-lived draft before creating or updating the GitHub ledger
issue. Track:

- lens name,
- canonical lens label,
- status: `Not Started`, `In Review`, `Issues Raised`, `Blocked By Active Fix`, `Needs Recheck`,
  or `Covered For Now`,
- issue numbers raised or existing issues reused,
- code areas inspected,
- remaining questions,
- last review date.

Do not mark a lens `Covered For Now` just because issues were filed. Use that status only when
duplicate checks, representative code inspection, and residual-risk notes are complete for the
current campaign depth.

Ledger issue rules:

1. use a durable GitHub issue when the user wants ongoing app review,
2. update the ledger after every issue-discovery batch,
3. include the lens, inspected paths, duplicate searches, issues raised/reused, active-fix blockers,
   and next suggested lens,
4. keep the ledger factual and compact; it is an operating index, not a second issue body.

For each lens pass, use this loop:

1. read the target repo context and the relevant docs KB/technical standard,
2. inspect representative code, tests, docs, contracts, migrations, and runtime wiring,
3. search open and closed GitHub issues by lens terms and concrete symbols,
4. decide whether the finding is new, duplicate, active-fix feedback, or below the issue bar,
5. create or update labels with `scripts/ensure_issue_discovery_labels.py`,
6. file only evidence-backed issues with canonical labels,
7. update the ledger with inspected areas, duplicate searches, issue numbers, and residual risk.

### 1A. Lens Pass Standard

For each lens, complete this minimum pass before filing:

1. read at least one target repo source path and one matching test/doc/contract path when present,
2. read the relevant docs KB or platform standard when the finding depends on domain or technical
   correctness,
3. search GitHub issues using both broad lens keywords and concrete file/symbol names,
4. classify each candidate as `new issue`, `existing issue`, `active-fix feedback`, `ledger-only
   residual risk`, or `no issue`,
5. ensure canonical labels exist,
6. write one issue per root cause unless separate symptoms require different owners or fix paths.

For implementation-review of another agent's active branch, prefer feedback on the existing issue or
PR when the problem is an unfinished acceptance criterion. File a new issue only for a distinct
root cause.

### 2. Check Existing Issues First

Before raising issues, search GitHub for duplicates and adjacent work:

```powershell
gh issue list --repo <owner>/<repo> --state open --limit 200 --search "<lens keywords>"
```

Also search closed issues when the finding may already have been handled:

```powershell
gh issue list --repo <owner>/<repo> --state all --limit 200 --search "<specific title or file>"
```

Do not file a new issue when an existing issue already covers the same root cause, same acceptance
criteria, and same likely implementation slice. Add a new issue only when it is a distinct root
cause, distinct boundary, or more actionable child of a broad parent issue.

Use multiple duplicate searches:

1. lens words, such as `idempotency`, `pagination`, `security headers`, `outbox`,
2. concrete symbols, such as route names, classes, tables, migrations, event types, or Make targets,
3. expected fix terms, such as `lease`, `problem details`, `retry`, `index`, `operation_id`,
4. closed issue searches when the repository has recent fix activity.

If another agent is actively fixing defects in the target worktree or branch:

1. inspect the current local diff before relying on older findings,
2. run focused tests or contract checks that prove whether the active fix is complete,
3. search for the owning GitHub issue or PR before filing anything new,
4. add concise implementation-review evidence to the existing issue or PR when the finding is a
   gap in that active fix,
5. create a new issue only when the finding is a separate root cause or lens, not an unfinished
   acceptance criterion of the active issue.

Use this posture to avoid noisy duplicate issues while still giving the implementation agent
actionable evidence.

### 3. Inspect Code Before Claims

Use targeted searches, then open representative files:

```powershell
rg -n "<pattern>" src tests docs --glob "*.py" --glob "*.ts" --glob "*.tsx" --glob "*.md"
```

Prefer concrete evidence:

- exact file paths,
- function/class names,
- route names,
- DTO/model names,
- repository/query names,
- event/topic names,
- tests that cover or miss the behavior,
- docs/standards that state the expected behavior.

Do not raise issues from intuition alone.

Use the target app's role to avoid wrong-owner issues. For example:

- `lotus-core` owns portfolio, account, transaction, position, holding, booking, and portfolio
  management source data.
- `lotus-performance` owns performance analytics and methodology outputs, not source booking.
- `lotus-risk` owns risk analytics, drawdown, concentration, stress, and exposure outputs.
- `lotus-advise` owns advisory workflow and proposal lifecycle.
- `lotus-manage` owns discretionary portfolio-management execution and action-register workflows.
- `lotus-report`, `lotus-render`, and `lotus-archive` own report generation, rendering, archive,
  retrieval, retention, and evidence flows.
- `lotus-idea` owns opportunity intelligence and idea lifecycle, not source-owned portfolio,
  performance, risk, reporting, archive, render, gateway, or AI infrastructure truth.
- `lotus-gateway` owns experience composition and publication, not domain authority.
- `lotus-workbench` owns the product UI and must consume supported backend/Gateway capability.

### 4. Calibrate Value

File only issues that materially improve at least one bank-buyable control:

- architecture and module boundaries,
- API and contract quality,
- domain correctness and methodology,
- transaction or lifecycle correctness,
- data lineage and auditability,
- security and privacy,
- observability and supportability,
- resilience, performance, or scalability,
- meaningful tests and CI proof,
- documentation and operational truth.

Avoid low-value issues for cosmetic naming, speculative rewrites, broad "clean up" requests, or
future-state preferences without current evidence.

Raise the issue when at least one of these is true:

- it can produce wrong domain, calculation, lifecycle, security, or API behavior,
- it can hide operational failure or make support unable to diagnose production behavior,
- it erodes source ownership, layer boundaries, or testability in a way likely to recur,
- it leaves unsupported claims in README, wiki, API docs, supported-feature material, or runtime
  evidence,
- it makes the app harder to make bank-buyable because CI, release evidence, observability,
  security, or documentation truth is missing.

Do not raise the issue when:

- the code is simply not aesthetically ideal,
- the finding requires a product decision with no current standard or accepted target,
- the same root cause is already being fixed,
- the only evidence is an isolated search hit with no behavior or contract consequence,
- the issue would be too broad for another agent to start fixing.

### 5. Write Actionable Issues

Each issue should include:

- `Lens`
- `Finding`
- concrete evidence with file paths and behavior
- `Why This Matters`
- `Expected Direction`
- `Acceptance Criteria`
- related issues to avoid duplicate implementation

Keep titles specific and implementation-oriented:

- good: `Move Kafka event payload mapping into explicit event adapters instead of inline consumers and repositories`
- weak: `Improve events`

Apply labels while creating issues:

1. use the canonical lens label from `references/review-lenses.md`, for example
   `lens/api-design-governance` or `lens/security-privacy`,
2. add `issue-discovery` to every issue created by this skill,
3. add one optional impact label only when it materially improves triage, such as
   `impact/correctness`, `impact/security`, `impact/operability`, `impact/performance`, or
   `impact/architecture`,
4. create missing labels in the target repository before issue creation instead of filing unlabeled
   issues,
5. do not invent app-local lens labels when a canonical label exists.

Create or update the canonical labels before issue creation:

```powershell
python <skill-dir>/scripts/ensure_issue_discovery_labels.py --repo <owner>/<repo>
gh issue create --repo <owner>/<repo> --title "<title>" --body-file <body.md> --label "issue-discovery" --label "lens/api-design-governance" --label "impact/operability"
```

When updating existing issues discovered earlier, add the canonical labels if the issue clearly maps
to one lens. Do not relabel unrelated or ambiguous issues in bulk.

Issue quality bar:

1. title names the failing behavior or missing control,
2. body cites concrete files, symbols, routes, contracts, migrations, tests, or docs,
3. expected direction is implementation-oriented but does not over-prescribe a fragile design,
4. acceptance criteria include tests and docs/context updates when truth changes,
5. related issues are listed to prevent duplicate work,
6. labels include `issue-discovery`, exactly one `lens/*`, and at most one primary `impact/*`
   unless the repository already uses a stricter triage convention.

### 6. Verify And Summarize

After filing:

1. list the created issue numbers,
2. re-check `git status --short --branch`,
3. state whether files were edited,
4. confirm which lens and impact labels were applied,
5. update the app's GitHub issue-discovery ledger issue or state why no durable ledger update was
   made,
6. summarize the lens covered and remaining logical next lens.

If the review exposes a repeatable review weakness, update the skill source, routing map, or Lotus
context in `lotus-platform` rather than relying on memory. Examples:

- a new lens or label is repeatedly needed,
- the ledger needs a stronger status or field,
- duplicate checking failed because the skill lacked a symbol-search step,
- agents repeatedly file broad issues without acceptance criteria,
- a docs KB source should become a required anchor for a lens.

For skill updates, edit the platform-owned source under `lotus-platform/codex/skills`, validate it,
commit, raise a PR, sync the local skill after merge, and return the repo to clean `main`.

## Issue Body Template

```markdown
## Lens
<lens name>

Labels: `issue-discovery`, `lens/<canonical-lens-label>`, `impact/<optional-impact>`

## Finding
<specific finding in current implementation>

Concrete evidence:
- `<path>:<line or function>` <what it does>
- `<path>:<line or function>` <what it does>

Related but not duplicate of: #<issue>, #<issue>

## Why This Matters
<business, engineering, operational, security, or domain consequence>

## Expected Direction
<target design or behavior, preserving existing behavior unless intentionally changed>

## Acceptance Criteria
- <testable condition>
- <testable condition>
- <docs/context/gate update if truth changes>
```

## Guardrails

- Do not edit code during issue-discovery-only tasks.
- Do not file duplicate or vague issues.
- Do not overstate severity; use evidence-based language.
- Do not expose secrets, tokens, private client data, or sensitive payloads in issue bodies.
- Do not claim a lens is fully complete unless the current-state evidence proves it.
- Do not let a broad architecture issue hide a concrete defect that needs its own fixable issue.
- Do not create runtime service-split issues before in-process modularity has been evaluated.
- Do not use the docs repo as a decoration; cite it only when it changes the standard or explains
  why the code is materially risky.
- Do not use local active fix diffs as stable evidence without noting that the finding may need
  recheck after merge.

## Bundled Resources

- `references/review-lenses.md`: canonical lenses, label taxonomy, search starters, and severity calibration.
- `references/lens-coverage-ledger-template.md`: durable issue-ledger structure and per-lens note shape.
- `scripts/ensure_issue_discovery_labels.py`: creates or updates the canonical `issue-discovery`,
  `lens/*`, and `impact/*` labels in a target GitHub repository.

