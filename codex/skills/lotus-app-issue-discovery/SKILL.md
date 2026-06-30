---
name: lotus-app-issue-discovery
description: Use when reviewing Lotus applications lens by lens to find high-value, evidence-backed GitHub issues without editing code. Applies when the user asks to inspect a Lotus repo for architecture, API, domain, lifecycle, mapping, data model, calculations, security, observability, performance, resilience, testing, documentation, operational supportability, or bank-buyable readiness issues; when they want defects raised for another implementation agent; or when a reusable issue-discovery campaign should avoid duplicates and cite concrete code evidence.
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

## Required Context

Load the smallest correct context set:

1. target repo `AGENTS.md`
2. `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`
3. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
4. target repo `REPOSITORY-ENGINEERING-CONTEXT.md`
5. `lotus-platform/context/LOTUS-SKILL-ROUTING-MAP.md`
6. `lotus-platform/context/playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md` for backend issue lenses
7. `lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`
8. app-specific RFCs, standards, methodology docs, or docs repo knowledge only when the lens needs them

For the lens catalog, read `references/review-lenses.md`. For a reusable campaign ledger shape,
read `references/lens-coverage-ledger-template.md` when starting or resuming a multi-lens defect
discovery campaign.

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

For a multi-turn or multi-lens campaign, create or update a lens coverage ledger before filing more
issues. Prefer one GitHub issue per Lotus app named `<app> Issue Discovery Ledger` when multiple
agents are working, implementation branches are active, or the user wants shared campaign state.
Use a repo-local ledger only when the review campaign itself is part of a committed documentation
slice. Use a temp note only as a short-lived draft before creating or updating the GitHub ledger
issue. Track:

- lens name,
- status: `Not Started`, `In Review`, `Issues Raised`, `Blocked By Active Fix`, `Needs Recheck`,
  or `Covered For Now`,
- issue numbers raised or existing issues reused,
- code areas inspected,
- remaining questions,
- last review date.

Do not mark a lens `Covered For Now` just because issues were filed. Use that status only when
duplicate checks, representative code inspection, and residual-risk notes are complete for the
current campaign depth.

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

### 6. Verify And Summarize

After filing:

1. list the created issue numbers,
2. re-check `git status --short --branch`,
3. state whether files were edited,
4. update the app's GitHub issue-discovery ledger issue or state why no durable ledger update was
   made,
5. summarize the lens covered and remaining logical next lens.

## Issue Body Template

```markdown
## Lens
<lens name>

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

