---
name: lotus-app-issue-discovery
description: Use when reviewing Lotus applications lens by lens to find high-value, evidence-backed GitHub issues, and as the mandatory first phase when a combined request asks to discover issues and then implement fixes. Applies to architecture, API, domain, lifecycle, data, calculations, security, observability, performance, resilience, testing, CI, docs, repo hygiene, operational supportability, enterprise readiness, regulatory/compliance, tenant isolation, DR, rollout, privacy, accessibility/usability, data quality, migration, SBOM/provenance, API consumer experience, mobile readiness, and AI governance/evaluation/safety/tool-control issue discovery. Use when defects need duplicate checks, a GitHub ledger, canonical lens labels, concrete file evidence, acceptance criteria, and an issue-backed handoff before source mutation.
---

# Lotus App Issue Discovery

## Purpose

Use this skill to run a disciplined no-code issue-discovery campaign across a Lotus app. Inspect
current implementation truth first, avoid duplicate GitHub issues, and file only high-value defects
that another agent can implement from the issue body and ledger.

Use this skill with the relevant delivery skill:

- backend services: `lotus-backend-delivery-governance`
- frontend product surfaces: `lotus-frontend-delivery-governance`
- runtime validation or service QA: `lotus-qa-platform-validator`
- CI or quality-gate findings: `lotus-ci-enforcement-governance`
- durable review-ledger campaigns: `lotus-codebase-review-ledger`

Do not edit code unless the user explicitly asks for fixes.
Before raising issues, search GitHub for duplicates with both broad lens terms and concrete symbols.
For the lens catalog, read `references/review-lenses.md`.

## Load Order

For substantial review work, load the smallest correct context set in this order:

1. target repo `AGENTS.md`
2. `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`
3. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
4. target repo `REPOSITORY-ENGINEERING-CONTEXT.md`
5. `lotus-platform/context/CONTEXT-REFERENCE-MAP.md`
6. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md` for multi-turn or resumed campaigns
7. `lotus-platform/context/LOTUS-SKILL-ROUTING-MAP.md`
8. `lotus-platform/context/playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md` for backend lenses
9. `lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`
10. relevant sibling `docs` repo knowledge-base pages, target repo RFCs, README, wiki source,
    supported-feature material, OpenAPI output, contracts, tests, or runtime evidence for the lens

Use repo-local truth for ownership. Use platform standards and the docs knowledge base for the
expected banking-grade posture. If a required docs source is absent, record that context gap in the
ledger and do not claim a docs-backed review.
Treat the sibling docs repo knowledge base as the reusable Lotus product, domain, and technical
standard library when it is present in the workspace.

## Required References

Read these bundled references as needed:

- `references/review-lenses.md`: canonical lenses, labels, extension-lens acceptance criteria,
  evaluation conditions, user-prompt mapping, search starters, duplicate keywords, and severity
  calibration.
- `references/campaign-playbook.md`: start/resume procedure, autopilot rules, evidence packets,
  active-fix handling, issue filing, ledger updates, time boxes, move-app decisions, and skill/KB
  improvement routing.
- `references/lens-coverage-ledger-template.md`: ledger status model, issue-ledger table shape,
  proof flags, per-lens notes, and campaign summary.

Use `scripts/ensure_issue_discovery_labels.py` before filing or relabeling issues. Use
`scripts/validate_issue_discovery_skill.py` after changing the lens catalog, labels, or ledger
template. Use `scripts/plan_issue_discovery_campaign.py` to generate a repeatable repo/profile
campaign plan before broad reviews or app handoffs.

## Discovery-To-Delivery Handoff

When the user asks to discover issues and then implement fixes, treat discovery and delivery as two
sequential phases. Before the first source mutation:

1. complete the evidence packet and duplicate search,
2. create or reuse the focused implementation issue,
3. update the campaign ledger when one exists,
4. record the issue number in the working plan, branch, commit, and PR evidence,
5. then load the repo delivery skill and begin implementation.

Do not create the implementation issue retroactively after code editing has started. Keep a shared
campaign ledger open unless the ledger itself is the implementation target.

## Operating Contract

Act like a senior Lotus review lead, not a bug-title generator.

For every issue, prove five things before filing:

1. **Current truth**: current source, tests, docs, contracts, migrations, workflows, generated
   contract output, or runtime evidence proves the behavior.
2. **Expected truth**: a Lotus standard, docs KB source, repo context, RFC/contract, or accepted
   domain/technical practice explains the expected posture.
3. **Owner truth**: the target repo owns the fix, or its publication/consumer contract makes the
   issue actionable there.
4. **Duplicate truth**: open and closed GitHub issues were searched using broad lens terms plus
   concrete symbols, routes, tables, files, or likely fix terms.
5. **Fixability truth**: the issue is one coherent implementation slice with concrete acceptance
   criteria and an evaluation condition.

Prefer fewer, stronger issues. If a finding is speculative, stale, duplicate, active-fix dependent,
or below the bank-buyable bar, record it in the ledger as residual risk instead of filing noise.

Use these campaign outcomes:

- `file`: create one new issue for a distinct root cause.
- `reuse`: link, relabel, or comment on an existing issue that already covers the root cause.
- `block`: mark the lens blocked when active local work, a branch, or a PR is changing the same
  evidence.
- `ledger-only`: record useful but not-yet-actionable residual risk.
- `covered`: mark the lens covered for current campaign depth after representative inspection,
  duplicate searches, and ledger evidence.
- `not applicable`: record why repo context proves the lens is outside the app boundary.

## Autopilot Algorithm

Use this sequence for "continue", "next issues", "check this lens", time-boxed review, or resumed
campaign work:

1. Resolve target repo, GitHub `owner/repo`, branch, dirty worktree, open PRs, and whether the task
   is no-code review only.
2. Find or create the `<repo> Issue Discovery Ledger`; read its latest comments before selecting a
   lens.
3. For broad or resumed campaigns, generate a starting plan with
   `python <skill-dir>\scripts\plan_issue_discovery_campaign.py --repository <owner>/<repo>`;
   then select one primary lens from the user's request, ledger gaps, the baseline queue, or a
   recent high-value adjacent defect.
4. Load `references/review-lenses.md` and `references/campaign-playbook.md`; load the ledger
   template only when creating or repairing a ledger.
5. Inspect code with `rg` first, then read representative source plus at least one counterpart
   artifact: test, contract, migration, workflow, README/wiki source, generated OpenAPI, or runtime
   proof.
6. Compare evidence to platform, repo, docs KB, RFC, contract, or accepted domain practice.
7. Search GitHub duplicates with at least one broad lens query and one concrete symbol/file/query
   term across open and closed issues.
8. Classify each candidate as `new issue`, `existing issue`, `active-fix feedback`,
   `ledger-only residual risk`, `no issue`, or `not applicable`.
9. Ensure labels, then file or reuse one issue per root cause only when the evidence packet is
   complete.
10. Update the ledger after every pass with status, proof flags, inspected paths, standards,
    duplicate searches, issue numbers, active blockers, residual risk, recommendation, and next lens.
11. Report the lens covered, issues filed or reused, no-issue decisions, current worktree state, and
    the next useful recommendation.

Do not stop after state discovery unless the repository target, GitHub access, or required
ownership context is blocked.

## Evidence Packet

Assemble this packet before creating or updating an issue:

- `Lens`: one primary canonical `lens/*` label; mention secondary lenses in the body.
- `Standard`: the exact platform, docs KB, repo, RFC, contract, public standard, or domain rule.
- `Evidence`: concrete files, symbols, routes, contracts, migrations, workflows, tests, or runtime
  output.
- `Impact`: correctness, security, operability, performance, architecture, compliance,
  customer-experience, or supportability consequence.
- `Duplicate searches`: exact queries and result summary.
- `Owner boundary`: why this repo owns the fix, or which publication/consumer boundary makes it
  actionable here.
- `Expected direction`: smallest implementation direction without over-prescribing a brittle design.
- `Acceptance criteria`: tests, contracts, docs/context updates, runtime proof, or gate evidence.
- `Evaluation condition`: the concrete check or operator proof that closes the finding.
- `Non-goals`: adjacent rewrites, service splits, or product decisions not required for the first
  fix.
- `Recheck trigger`: PR, branch, issue, or runtime evidence that should revisit the lens.

For stateful behavior, also include authoritative identity, lifecycle state, persistence owner,
idempotency, conflict, replay, retry, audit, lineage, retention, restart, scale-out, concurrency,
and recovery posture where applicable.

For capability, evidence, or supported-feature claims, also include what is claimed, where it is
published, which runtime/API/data/test evidence supports or contradicts it, and what must be
downgraded or implemented if the claim is not true.

## Issue Rules

Create issues only when they materially improve at least one bank-buyable control:

- architecture or module boundaries
- API and contract quality
- domain correctness or methodology
- transaction, position, lifecycle, data quality, or reconciliation correctness
- data lineage, auditability, records, privacy, or compliance
- security, abuse prevention, entitlement, or tenant isolation
- observability, supportability, resilience, recovery, SLO, capacity, or cost
- meaningful tests, CI, release evidence, rollout, deployment parity, or provenance
- documentation, API consumer experience, operational truth, accessibility, or client suitability
- AI model, data, evaluation, explainability, safety, oversight, reliability, or tool governance

Do not file issues for taste-only cleanup, broad future-state preferences, duplicate root causes,
product ideas without an accepted target, or findings with only search-hit evidence.

Issue bodies must include:

- `Lens`
- `Standard`
- `Finding`
- concrete evidence
- duplicate searches
- owner boundary
- `Why This Matters`
- `Expected Direction`
- `Acceptance Criteria`
- `Evaluation Condition`
- related issues or non-goals when relevant

Apply labels:

1. `issue-discovery`
2. exactly one primary `lens/*`
3. at most one primary `impact/*`, unless the target repo has a stricter convention

## Ledger Rules

Use a GitHub issue named `<repo> Issue Discovery Ledger` for multi-lens campaigns. Keep the ledger
in the target app repository unless the campaign is platform-wide.

Use these statuses consistently:

- `Not Started`
- `In Review`
- `Issues Raised`
- `Blocked By Active Fix`
- `Needs Recheck`
- `Covered For Now`
- `Not Applicable`

Never mark `Covered For Now` from memory, label existence, or GitHub search alone. A covered lens
needs representative source inspection, standard comparison, duplicate searches, labels, and a
ledger update. A `Not Applicable` lens needs a repo-context or ownership-boundary note.

Use the ledger, not chat memory, to answer whether to continue, pause for implementation, recheck
after merge, or move apps.

## Docs Knowledge Routing

Use the sibling docs repository at `<workspace-root>/docs` as a knowledge base:

- product/domain lenses: `docs/docs/products/`
- backend/API/data/CI/infrastructure/observability/security/performance/testing/docs/SRE lenses:
  `docs/docs/technical/`
- wealth-platform architecture, strategy, and operating-model lenses: `docs/docs/reference/`
- reusable prompt or agent-workflow lenses: `docs/docs/prompts/`

Update the docs KB in a separate maintenance slice when a reusable product, domain, technical, API,
security, observability, testing, CI, or operating-model standard is missing or stale across apps.
Keep app-specific bug evidence in the app issue, ledger, RFC, repo context, README, wiki, tests, or
implementation proof.

## Skill Maintenance

When the user asks to strengthen this skill, or a review pass exposes repeatable process weakness,
edit the platform-owned source under `lotus-platform/codex/skills/lotus-app-issue-discovery`.
Do not hand-edit the deployed local skill copy as source truth.

Choose the smallest durable artifact:

- `SKILL.md`: mandatory trigger-time behavior and no-code review contract
- `references/review-lenses.md`: lenses, labels, search, evidence anchors, acceptance criteria, and
  evaluation conditions
- `references/campaign-playbook.md`: start/resume, active-fix, issue-count, time-box, handoff, and
  self-improvement procedure
- `references/lens-coverage-ledger-template.md`: ledger shape and campaign-state visibility
- `scripts/ensure_issue_discovery_labels.py`: deterministic GitHub label creation
- `scripts/validate_issue_discovery_skill.py`: drift checks across catalog, label script, and ledger
- `scripts/plan_issue_discovery_campaign.py`: repeatable repo/profile campaign planning and
  high-signal CI-hardening candidate hints

For skill-maintenance slices, run:

```powershell
python -m py_compile codex\skills\lotus-app-issue-discovery\scripts\ensure_issue_discovery_labels.py
python -m py_compile codex\skills\lotus-app-issue-discovery\scripts\validate_issue_discovery_skill.py
python -m py_compile codex\skills\lotus-app-issue-discovery\scripts\plan_issue_discovery_campaign.py
python codex\skills\lotus-app-issue-discovery\scripts\validate_issue_discovery_skill.py
python <skill-creator>\scripts\quick_validate.py codex\skills\lotus-app-issue-discovery
python automation\validate_lotus_skill_alignment.py
powershell -ExecutionPolicy Bypass -File automation\Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast -ValidateAfterSync
```

Record an explicit no-wiki-change decision unless wiki source changed.

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

## Guardrails

- Do not edit app code during issue-discovery-only tasks.
- Do not create duplicate, vague, or count-driven issues.
- Do not expose secrets, tokens, private client data, raw sensitive payloads, or unsafe diagnostic
  content in issue bodies.
- Do not overstate severity; use evidence-based language.
- Do not create wrong-owner capability-publication issues.
- Do not treat active fix branches as stable truth without noting recheck posture.
- Do not create runtime service-split issues before in-process modularity has been evaluated.
- Do not use docs KB pages as decoration; cite them only when they define or clarify the standard.
- Do not let a broad architecture issue hide a concrete defect that needs its own fixable issue.
