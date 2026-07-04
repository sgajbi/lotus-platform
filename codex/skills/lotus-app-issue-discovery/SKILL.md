---
name: lotus-app-issue-discovery
description: Use when reviewing Lotus applications lens by lens to find high-value, evidence-backed GitHub issues without editing code. Applies when the user asks to inspect a Lotus repo for architecture, runtime composition, API, HTTP boundary controls, domain, lifecycle, mapping, data model, database operations, calculations, security, observability/monitoring, performance, resilience, testing, CI/release evidence, data mesh, repo organization, agents/context organization, documentation/wiki/README, operational supportability, or bank-buyable readiness issues; when they want defects raised for another implementation agent; or when a reusable issue-discovery campaign should avoid duplicates, maintain a GitHub ledger, apply canonical lens labels, cite code evidence, and use docs repo knowledge plus Lotus platform standards as the review baseline.
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

Execute as if the next implementation agent will only see the GitHub issue and the ledger. Preserve
the reasoning that normally lives in chat: what was inspected, what standard was applied, why the
target repo owns the issue, what duplicate searches were run, and what would prove the fix complete.

Default to execution. When the user asks to continue a campaign, strengthen the skill, find issues,
check a lens, or decide whether to move apps, do not stop at a plan. Rebuild state from durable
sources, inspect evidence, file or decline issues, update the ledger, and report the next useful
decision.

Your job is to make another implementation agent successful. A good issue-discovery pass leaves
behind:

1. a clear lens decision,
2. code-backed evidence,
3. the standard or domain rule used to judge the evidence,
4. duplicate-search proof,
5. a GitHub issue that is small enough to implement,
6. a ledger update that tells the user what has been covered and what remains.

For every issue, prove four things before filing:

1. the repository evidence exists,
2. the expected behavior is grounded in Lotus standards, the docs knowledge base, repo context, or
   accepted industry/domain practice,
3. the finding is not already covered by an open, closed, or actively fixed issue,
4. the issue is fixable as a coherent implementation slice with clear acceptance criteria.

Run the gold gate for high-impact findings before filing:

1. **Truth gate**: prove the claim against current source plus one counterpart artifact such as a
   test, migration, contract, RFC, wiki source, capability catalog, OpenAPI output, workflow, or
   generated evidence file.
2. **State gate**: for stateful workflows, prove whether state, idempotency, audit, lineage,
   replay, and recovery are durable, transactional, and safe across restart and scale-out.
3. **Ownership gate**: prove the target repository owns the failing behavior or the publication
   contract that makes it actionable there.
4. **Runtime gate**: when a finding affects production behavior, check startup/runtime wiring,
   dependency injection, configuration, health/readiness, observability, and operator diagnostics.
5. **Implementation gate**: make the expected direction specific enough that a fixing agent can
   start without rediscovering the repo, but avoid prescribing a brittle design when multiple good
   fixes exist.

Prefer fewer, stronger issues. If a finding is speculative, stale, duplicate, or below the
bank-buyable bar, record it in the ledger as residual risk instead of filing noise.

Think in campaign outcomes:

1. `file`: a new, fixable, evidence-backed issue is needed;
2. `reuse`: an existing issue already covers the root cause, so link or comment there;
3. `block`: an active branch or PR is changing the same evidence, so mark the lens blocked or
   needs recheck;
4. `ledger-only`: the observation is useful but not issue-worthy yet;
5. `covered`: the lens has enough representative proof for the current campaign depth.

Never optimize for issue count. Optimize for campaign truth: complete lens passes,
implementation-ready defects, clear labels, and a ledger that lets the user decide whether to keep
reviewing, wait for fixes, recheck after merges, or move to another app.

## Autonomous Campaign Contract

When the user says "continue", "next issues", "check this lens", "make the skill do what you do",
or otherwise expects ongoing review, run the campaign without asking for more instructions unless
the target repository or GitHub issue target is genuinely ambiguous.

Assume future agents may have no useful chat history. Reconstruct campaign state from durable
sources, not memory:

1. the target repository branch and worktree,
2. the app's GitHub issue-discovery ledger,
3. current open issue-discovery issues and active PRs,
4. repo/platform/docs context for the selected lens,
5. current code, tests, contracts, workflows, docs, and runtime evidence.

Use this default behavior:

1. infer the target repository from the current working directory, explicit repo name, or latest
   active campaign ledger;
2. inspect `git status --short --branch` and never edit or revert unrelated local changes;
3. find or create the app ledger issue named `<repo> Issue Discovery Ledger`;
4. choose the next lens from the ledger status and the baseline lens queue;
5. read the smallest context and docs KB set that makes the lens judgment defensible;
6. inspect code, tests, docs, contracts, migrations, workflows, and runtime wiring before making
   claims;
7. duplicate-check GitHub issues using both lens keywords and concrete symbols;
8. create missing labels before filing issues;
9. file only high-value issues with one root cause, concrete evidence, expected direction, and
   acceptance criteria;
10. update the ledger after every pass, including no-issue decisions and blocked-by-active-fix
    states.
11. answer "are we done?" and "should we move apps?" from ledger coverage, active-fix blockers,
    open issue posture, and remaining high-value lenses, not from the number of issues raised.

If the user gives a time box, optimize for complete lens passes over issue count. If a finding needs
more proof than the time box allows, record it as residual risk and continue with the next most
provable candidate.

When the user asks to strengthen this skill, preserve this autonomous contract. The skill should
teach the next agent what to do without relying on prior chat: context loading, lens selection,
evidence standard, duplicate searches, GitHub labels, ledger updates, active-fix handling, and app
handoff decisions all belong in the durable skill or its references.

## Agent Execution Algorithm

Use this algorithm when a future agent has only the skill and the user's latest request:

1. **Resolve target**: identify the repository, GitHub owner/name, active branch, and whether the
   request is issue-discovery only. If code edits were not requested, do not edit app code.
2. **Protect local work**: run `git status --short --branch`; treat all dirty files as user or
   active-agent work unless you created them in this turn.
3. **Load standards**: read the mandatory context, the repo engineering context, the refactoring
   playbook, the bank-buyable engineering contract, and the relevant docs KB pages for the lens.
4. **Open the ledger**: find or create `<repo> Issue Discovery Ledger`; use it to determine covered,
   blocked, remaining, and needs-recheck lenses.
5. **Select one lens**: prefer the user's lens, then ledger gaps, then the baseline queue. Do not
   jump across unrelated lenses to inflate issue count.
6. **Inspect source**: use `rg` first, then read representative source, tests, docs/contracts,
   migrations/workflows, and runtime wiring. Gather line-level or symbol-level evidence.
7. **Compare to standard**: decide whether behavior violates repo responsibility, Lotus platform
   standards, docs KB, domain practice, or public technical standards.
8. **Search duplicates**: search open and closed GitHub issues with broad lens terms, concrete
   symbols, route/table/event names, and likely fix terms.
9. **Classify candidates**: `new issue`, `existing issue`, `active-fix feedback`, `ledger-only
   residual risk`, or `no issue`.
10. **File or decline**: create labels, file one issue per root cause only when evidence and
    duplicate checks are complete, or record why nothing met the bar.
11. **Update ledger**: add a compact comment with status, proof flags, inspected paths, duplicate
    searches, issue numbers, active blockers, residual risk, and next lens.
12. **Maintain the skill**: when the pass reveals a repeatable review failure, update the
    platform-owned skill source, validate, sync, and PR the skill improvement instead of relying on
    chat memory.
13. **Improve the knowledge base**: when the pass reveals a reusable domain or technical standard
    gap, update the docs knowledge base in a separate KB-maintenance slice instead of burying the
    lesson in an app issue or chat memory.
14. **Report**: tell the user which lens was covered, what was filed or declined, current worktree
    state, and the recommended next lens or app handoff point.

If any step cannot be completed, record the reason in the ledger and continue with the next
defensible action. Do not silently skip duplicate searches, standards lookup, or ledger updates.

### Senior Reviewer Decision Loop

For every candidate, walk this loop before creating an issue:

1. **Current truth**: prove the behavior in current source, tests, docs, contracts, workflow,
   migrations, generated contract output, or runtime evidence. Do not rely on old chat or stale
   memory.
2. **Expected truth**: tie the expected behavior to target repo context, platform context, the
   refactoring playbook, bank-buyable contract, docs KB, RFC/contract, or a recognized domain or
   technical standard.
3. **Owner truth**: state why this repo owns the fix or why this repo's publication/consumer
   contract makes the issue actionable here.
4. **Duplicate truth**: search open and closed GitHub issues with lens terms and concrete symbols.
   Reuse, comment, or link instead of filing when the root cause is already covered.
5. **Fixability truth**: make the implementation slice small enough to start and acceptance
   criteria testable enough to finish.
6. **Campaign truth**: update the ledger whether the outcome is new issue, reused issue, blocked
   active fix, residual risk, or no issue.

If any truth is missing, inspect one more bounded path or ledger the gap. Do not file a weak issue
just because the user asked for a count.

### Fast Autopilot Checklist

Run this checklist for ordinary "continue", "next issues", and "check this lens" turns:

1. `git status --short --branch` in the target repo.
2. `gh pr list` and open `issue-discovery` issues for the target repo.
3. Find or create the `<repo> Issue Discovery Ledger`.
4. Read the latest ledger comments before choosing a lens.
5. Read `references/review-lenses.md` and `references/campaign-playbook.md`.
6. Load only the repo/platform/docs KB files required for the chosen lens.
7. Inspect source plus a test/doc/contract/workflow counterpart.
8. Duplicate-search GitHub with at least one broad lens query and one concrete symbol query.
9. Ensure labels, then create or reuse one issue per root cause.
10. Comment on the ledger with status, proof flags, inspected paths, searches, issues, blockers,
    residual risk, and next recommendation.
11. If the pass exposes a repeatable review-process weakness, update this platform-owned skill in a
    separate skill-maintenance slice and sync the local deployed copy after validation.
12. If the pass exposes missing reusable product, domain, technical, API, security, observability,
    testing, or operating-model knowledge, update the docs knowledge base in a separate
    KB-maintenance slice and reference it from future issue standards.

If a step produces "nothing to file", still update the ledger so campaign coverage remains visible.

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
review. Also use the target repository's own README, wiki source, RFCs, architecture docs, API
catalog, supported-feature material, and tests as implementation truth. Do not treat local code
convention as sufficient when it contradicts those sources. If the docs repo is absent from the
workspace, record that context gap in the ledger and do not claim a docs-backed review for that
lens.

For the lens catalog, read `references/review-lenses.md`. Also use that file for canonical GitHub
label names, the baseline lens queue, and search starters. For a reusable campaign ledger shape,
read `references/lens-coverage-ledger-template.md` when starting or resuming a multi-lens defect
discovery campaign.

For a multi-turn review, a time-boxed defect-discovery run, or a request to "work like you", read
`references/campaign-playbook.md` before inspecting code. That playbook is the operational runbook
for start/resume decisions, lens sequencing, issue filing, ledger updates, active-fix handling,
user status updates, and skill self-improvement.

When the request asks to make this skill stronger, use `skill-creator` and
`lotus-ci-enforcement-governance`, update the canonical source under
`lotus-platform/codex/skills/lotus-app-issue-discovery`, run the skill validation and Lotus skill
alignment/sync checks, open a PR, and sync the local deployed skill from platform source. Do not
hand-edit the local deployed skill as the source of truth.

Use `references/review-lenses.md` to translate user wording into canonical labels. For example,
"business logic out of routers" maps to `lens/api-design-governance`, `lens/application-layer`,
`lens/domain-layer`, and `lens/infrastructure` depending on the evidence; "logic testable without
FastAPI/database/Kafka/Redis/cloud" maps primarily to `lens/domain-layer`, `lens/application-layer`,
`lens/ports-adapters`, and `lens/testing-quality`; "race conditions and unnecessary processing"
maps to `lens/unit-of-work-transactions`, `lens/database-operations`,
`lens/performance-scalability`, and `lens/resilience`; "supported feature truth", "Workbench
publication", "Gateway capability", or "what the app claims it supports" maps to
`lens/capability-publication`; "proof artifacts", "certification evidence", "scorecards", or
"implementation proof" maps to `lens/evidence-proof-contracts`.
For "dead code", "duplicate logic", "stale code paths", or "cleanup that affects maintainability",
use `lens/dead-code-duplication` only when the evidence has behavioral, supportability, test,
security, or ownership impact; do not file taste-only cleanup issues. For dependency, package,
scanner, lockfile, vulnerable transitive dependency, or supply-chain posture, use
`lens/dependency-hygiene` unless the concrete issue is primarily runtime security behavior.
For "repo organization", "repository layout", "cleanup", "generated artifacts", "script
organization", or "repository hygiene", use `lens/repo-organization`. For "agents", "agent
context", `AGENTS.md`, "skill routing", "procedural memory", "context organization", or "future
agents should know what to read", use `lens/agents-context-organization`. For "data mesh",
"catalog", "data-product publication", "producer/consumer declaration", or "trust telemetry", use
`lens/data-product-trust-telemetry`. For "monitoring", "alerts", "dashboards", "metrics", "SLO",
or "runbook-backed operations", use `lens/observability` or `lens/operational-supportability`
based on whether the root cause is telemetry instrumentation or operator workflow. For
"documentation", "wiki", "README", "API catalog", "runbook", or "docs truth", use
`lens/documentation-runbooks`.

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

Use this review-standard stack in order:

1. target repo source, tests, contracts, migrations, workflows, README, wiki source, RFCs, and
   generated OpenAPI or published capability artifacts;
2. target repo `REPOSITORY-ENGINEERING-CONTEXT.md`, especially ownership and non-ownership
   boundaries;
3. Lotus platform context, bank-buyable engineering contract, refactoring playbook, skill routing
   map, and current platform standards;
4. docs repo knowledge base for product/domain/technical standards;
5. public industry or framework standards only when repo and platform standards do not answer the
   question.

If these sources conflict, prefer implementation truth for what exists now and platform/repo/docs
truth for what the behavior must become. Record the conflict explicitly in the issue or ledger.

When repo source and docs disagree, do not silently choose the more convenient source. File a
capability-publication, documentation-runbooks, evidence-proof-contracts, or implementation issue
based on ownership and impact, and name the truth conflict in the issue body.

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

If the user asks whether the campaign is done or whether to move to another app, answer from the
ledger, not memory. Report lenses covered, lenses remaining, active-fix blockers, highest-value
remaining risk, and whether the current repository has reached a sensible handoff point.

When the user asks for "N issues", interpret `N` as an upper bound, not a quota. Stop early when the
remaining candidates are weak, duplicate, blocked by active fixes, or too broad for one agent.

When maintaining a ledger, keep it usable for human campaign steering. The ledger should let the
user see:

1. which lenses were actually inspected,
2. which issue labels were applied,
3. which open issues are waiting for implementation,
4. which lenses are blocked by active fixes,
5. which high-value lenses remain,
6. whether it is sensible to keep reviewing this app or move to another app.

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

### 1B. Evidence Packet

Before creating an issue, assemble a compact evidence packet. The issue body should be a polished
version of this packet:

1. `Lens`: the current lens and canonical label.
2. `Standard`: exact platform/doc/repo source that explains the expected posture.
3. `Evidence`: file path, line or symbol, and the observed behavior.
4. `Impact`: what can go wrong in correctness, operability, performance, security, architecture, or
   supportability terms.
5. `Duplicate search`: exact GitHub searches and result summary.
6. `Fix direction`: the smallest implementation direction that addresses the root cause.
7. `Tests`: the meaningful unit, integration, contract, API, security, regression, or E2E tests
   expected from the fix.
8. `Non-goals`: adjacent rewrites, service splits, or product decisions that are not required for
   the first fix, when the finding could otherwise become too broad.
9. `Recheck trigger`: branch, PR, issue, or runtime evidence that should cause the lens to be
   revisited.

Do not file from a packet that is missing either `Evidence` or `Duplicate search`.

Add `Owner boundary` whenever the issue touches cross-app behavior. State why the target repository
owns the fix, or whether it is a publication, Gateway, Workbench, source-contract, or consumer
integration issue. This prevents wrong-owner defects in a distributed Lotus review.

For active capability, evidence, or supported-feature claims, add `Truth boundary`:

1. what is claimed as supported,
2. where the claim is published,
3. which runtime/API/data/test evidence supports or contradicts it,
4. what must be downgraded or implemented if the claim is not currently true.

For stateful behavior, add `State boundary`:

1. authoritative identity and lifecycle state,
2. persistence owner and migration/table/collection evidence,
3. idempotency, conflict, replay, and retry semantics,
4. audit, lineage, correlation, and evidence references,
5. restart, scale-out, concurrency, and recovery behavior,
6. retention or archival posture where the state is regulated or client-relevant.

### 1C. Lens Completion Rules

Use these ledger outcomes consistently:

1. `Issues Raised`: at least one new or reused issue exists, but residual review may remain.
2. `Covered For Now`: representative code inspection, docs/context comparison, duplicate searches,
   and residual-risk notes are complete for the current campaign depth.
3. `Blocked By Active Fix`: a branch or PR is actively changing the same area; record the branch,
   PR, or issue and recheck after merge.
4. `Needs Recheck`: evidence is stale, a broad issue landed, or adjacent code changed.

Never mark a lens complete just because labels exist or because a search found no obvious hits.

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

If the active fix is in the same lens but the root cause is distinct, file a new issue and link the
active issue or PR. If it is the same root cause, comment on the existing issue or PR instead of
creating a duplicate.

If a duplicate exists but lacks the current lens label, add the canonical label only when the issue
clearly maps to that lens and the repository uses the shared taxonomy. If the existing issue is too
broad, create a focused child issue only when it names a distinct implementation slice and links
back to the parent.

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

### 3A. Source Inspection Depth

A strong pass usually reads at least:

1. one delivery or runtime entry point,
2. one application or domain path,
3. one adapter, repository, client, or workflow path when relevant,
4. one test path or the absence of a test path,
5. one contract, migration, README/wiki, OpenAPI, workflow, or docs path when the lens touches
   durable truth.

Use `rg --files` and targeted `rg -n` before opening files. Prefer source-owned evidence over
generated artifacts unless the generated artifact is the actual contract consumers use.

For high-risk backend lenses, add a second pass over tests and contracts before filing. Typical
examples are lifecycle/corporate-action behavior, idempotency, transactionality, security,
operational diagnostics, proof/capability publication, and public API shape.

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

When in doubt, ask whether the issue would change a future implementation agent's actual work. If
the answer is "no", keep it in the ledger as residual risk.

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

Prefer one canonical `lens/*` label per issue. When a finding crosses several lenses, choose the
root-cause lens and mention the secondary lenses in the body. Example: missing idempotency storage
that also hurts auditability should usually use `lens/validation-idempotency`; the issue body can
state that it also affects `lens/auditability-lineage`.

### 6. Verify And Summarize

After filing:

1. list the created issue numbers,
2. re-check `git status --short --branch`,
3. state whether files were edited,
4. confirm which lens and impact labels were applied,
5. update the app's GitHub issue-discovery ledger issue or state why no durable ledger update was
   made,
6. summarize the lens covered and remaining logical next lens.

If no issue was filed, still update the ledger with:

1. the lens,
2. inspected paths,
3. duplicate searches,
4. why no issue met the bar,
5. residual risk or next recheck trigger.

If the review exposes a repeatable review weakness, update the skill source, routing map, or Lotus
context in `lotus-platform` rather than relying on memory. Examples:

- a new lens or label is repeatedly needed,
- the ledger needs a stronger status or field,
- duplicate checking failed because the skill lacked a symbol-search step,
- agents repeatedly file broad issues without acceptance criteria,
- a docs KB source should become a required anchor for a lens.

For skill updates, edit the platform-owned source under `lotus-platform/codex/skills`, validate it,
commit, raise a PR, sync the local skill after merge, and return the repo to clean `main`.

When strengthening this skill, update the smallest durable artifact that will change future agent
behavior: `SKILL.md` for mandatory workflow, `references/review-lenses.md` for lens/label/search
coverage, `references/lens-coverage-ledger-template.md` for ledger shape, `references/campaign-playbook.md`
for operating procedure, and scripts for deterministic GitHub or validation behavior.

When issue discovery exposes a reusable knowledge gap, update the sibling docs repository rather
than overloading the skill. Use the docs KB for durable product/domain/technical knowledge that
engineers should learn from across apps; use this skill for the process of finding, filing, and
ledgering defects. Keep app-specific facts in the app repository issue, ledger, README, wiki, RFC,
or repo context.

KB updates are appropriate when:

1. multiple apps need the same standard or review rule;
2. a product, lifecycle, transaction, position, calculation, architecture, API, security,
   observability, testing, CI, or operations concept is missing or ambiguous in the docs repo;
3. a repeated issue-discovery finding would be prevented by a clearer reusable reference;
4. the docs KB contains stale, duplicate, or weak guidance that future issues are citing;
5. a new review lens needs a learning page, worked example, or checklist to make future agents and
   engineers faster.

KB updates are not appropriate for one-off app bugs, speculative future features, confidential
client data, or implementation details that belong only in the target app's issue, RFC, README,
wiki, or repository context.

### 7. GitHub Issue Ledger Procedure

Use this exact pattern for app-ledger issues:

1. find existing ledger:
   `gh issue list --repo <owner>/<repo> --state open --search "\"Issue Discovery Ledger\"" --json number,title,url`
2. create it if missing with the template from `references/lens-coverage-ledger-template.md`;
3. after each pass, add a compact comment instead of rewriting history unless the user asks for a
   fully refreshed table;
4. mention issue numbers, labels, inspected paths, duplicate searches, and next lens;
5. keep the ledger in the target app repository, not in `lotus-platform`, unless the campaign is
   platform-wide.

Ledger comments should help the user answer: "Which lenses are done, which are remaining, and when
is it sensible to move to another app?"

## Issue Body Template

```markdown
## Lens
<lens name>

Labels: `issue-discovery`, `lens/<canonical-lens-label>`, `impact/<optional-impact>`

## Standard
- `<doc/platform/repo source>`: <expected behavior this issue uses>

## Finding
<specific finding in current implementation>

Concrete evidence:
- `<path>:<line or function>` <what it does>
- `<path>:<line or function>` <what it does>

Related but not duplicate of: #<issue>, #<issue>

Duplicate searches:
- `<query>`: <result summary>

Owner boundary:
- <why this repo owns the issue or which integration/publication boundary makes it actionable here>

## Why This Matters
<business, engineering, operational, security, or domain consequence>

## Expected Direction
<target design or behavior, preserving existing behavior unless intentionally changed>

Non-goals:
- <adjacent rewrite, runtime split, or product decision not required for the first fix>

## Acceptance Criteria
- <testable condition>
- <testable condition>
- <docs/context/gate update if truth changes>

Recheck trigger:
- <PR/branch/runtime evidence/issue that should cause this lens to be revisited>
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
- Do not file issues to satisfy an issue-count target when the next candidate is weak or duplicate.
- Do not mark a ledger lens complete from memory; inspect current code and GitHub issue state first.
- Do not create capability-publication issues against the wrong owner; verify the app owns the
  published feature or that the problem is the app's contract/publication surface.

## Bundled Resources

- `references/review-lenses.md`: canonical lenses, label taxonomy, search starters, and severity calibration.
- `references/lens-coverage-ledger-template.md`: durable issue-ledger structure and per-lens note shape.
- `references/campaign-playbook.md`: start/resume, lens execution, issue filing, ledger,
  active-fix, time-box, and self-improvement operating procedure.
- `scripts/ensure_issue_discovery_labels.py`: creates or updates the canonical `issue-discovery`,
  `lens/*`, and `impact/*` labels in a target GitHub repository.
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


