---
name: lotus-backend-delivery-governance
description: "Use when implementing or reviewing backend work in Lotus repositories such as lotus-core, lotus-performance, lotus-risk, lotus-advise, lotus-manage, lotus-report, lotus-idea, lotus-gateway, or lotus-ai. Apply the Lotus platform CI lane model, enterprise security baseline, contract-governance rules, repository-native command policy, truthful PR evidence process defined by RFC-0072, and non-degradation guardrails that prevent low-quality agent-generated backend code."
---

# Lotus Backend Delivery Governance

Use this skill for Lotus backend feature work, cleanup, validation, and PR preparation.

Apply it in line with:

1. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
2. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md`
3. the target repo `REPOSITORY-ENGINEERING-CONTEXT.md`
4. `lotus-platform/rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
5. `lotus-platform/docs/standards/Continuous Integration, Validation, and Release Governance Standard.md`
6. `lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`
7. repository-local RFCs and standards already in force

Use `lotus-platform/context/playbooks/CHANGE-PLAYBOOKS.md` for task sequencing and `lotus-platform/context/playbooks/VALIDATION-PLAYBOOK.md` when deciding how much proof is required.

Use `lotus-front-office-runtime` as the primary route when the backend change is being validated
through the governed canonical front-office runtime and populated Workbench product surfaces.

Use `lotus-ci-enforcement-governance` as the primary route when the backend task is mainly about
designing, promoting, or hardening CI quality gates, repository-native enforcement targets,
scorecard-backed regression blockers, or agent-development guardrails.

## Context-First Rule

Before substantive backend work:

1. load the central engineering context,
2. load the repo-local context,
3. load only the specific standards or RFCs the task actually needs.

## Working Model

Before changing code:

1. confirm the repo and branch,
2. classify the repo:
   - Experience API
   - Domain API
   - Opportunity Intelligence / Domain Workflow Service
   - Shared Capability Service
   - Platform Governance / Automation
3. identify the repository-native commands for:
   - lint
   - typecheck
   - unit
   - integration
   - e2e
   - coverage
   - local parity
4. identify whether the change affects:
   - OpenAPI
   - vocabulary
   - no-alias rules
   - migrations
   - Docker/runtime behavior
   - cross-app contracts
   - canonical front-office runtime behavior

Before editing backend code, produce a short quality intake from the actual repository:

1. name the existing module, service, repository, model, router, and test patterns in the touched
   area,
2. identify the canonical source of business truth and whether the code path is API-facing,
   operator-facing, batch/runtime, or internal-only,
3. identify the closest meaningful tests and the repo-native command that runs them,
4. inspect the current duplicate-code, complexity/function-size, architecture-boundary, security,
   API/OpenAPI, vocabulary, and contract signals that can regress,
5. state the narrow quality signal the slice will improve or preserve.

If you cannot name those items, keep reading before writing code.

For RFC-driven business-application slices, extend that intake with:

1. the RFC slice or blocker family being targeted,
2. the exact blocker codes this slice will clear,
3. the exact blocker codes this slice will intentionally preserve,
4. the source-authority owner for each consumed portfolio, performance, risk, advisory, suitability,
   compliance, reporting, archive, render, AI, Gateway, or Workbench fact,
5. the API/OpenAPI/error-model, persistence, data-mesh, proof-artifact, docs/wiki, and
   supported-feature surfaces affected,
6. the local gate commands and remote GitHub lanes that must pass before merge,
7. the no-claim boundary that prevents a narrow proof from becoming a demo-ready, production-ready,
   client-publication, supported-feature, data-mesh-certified, or live-provider claim.

## Delivery Rules

1. Use repository-native commands as the source of truth.
2. Keep changes small and auditable.
3. Update docs and runbooks in the same slice when contracts or operator flow change.
4. Keep security and governance checks first-class; do not treat them as optional cleanup.
5. Prefer fixing root-cause quality issues over updating allowlists or suppressions, unless the allowlist is the truthful current state.
6. Treat closure truth as mainline validated truth. A backend RFC or product capability is not
   complete until the implementation and required proof are merged to `main`, required gates have
   passed, local state is synced clean, and RFC docs, source maps, work-to-be-done ledgers, wiki
   source, supported-features, repository context, API contracts, and proof references are not
   stranded on an unmerged side branch.
7. For RFC-driven backend work, run stranded-truth reconciliation before implementation starts,
   before final closure, and before moving to the next RFC.
8. When a quality inventory is clean, deterministic, and already measured, consider whether
   `lotus-ci-enforcement-governance` should promote it to a blocking gate instead of leaving it as
   report-only evidence.

## Bank-Buyable Default Bar

Treat the Lotus Bank-Buyable Engineering Contract as the default quality posture for backend work,
even when the user does not explicitly ask for a refactor.

Every meaningful backend slice should improve or preserve at least one bank-buyable control:

1. architecture and module boundaries,
2. API and contract quality,
3. data, methodology, lineage, and supportability truth,
4. security and privacy,
5. observability and operator diagnostics,
6. resilience, performance, and scalability,
7. meaningful tests and CI/release evidence,
8. documentation, README, wiki, and repo-context truth.

Do not leave low-quality generated code in place just because the requested feature works. If the
slice exposes duplicate logic, unsupported contract claims, unsafe error/logging behavior, weak
tests, or stale docs in the touched area, either fix it in the same slice or record a concrete
follow-up in the repo's scorecard, review ledger, or PR evidence.

## Non-Degradation Bar

Backend work must leave the application at least as maintainable, observable, secure, and contract
truthful as it was before the change.

Before editing, identify the quality signals that can regress in the touched area:

1. duplicate implementation hotspots,
2. architecture-boundary imports and ownership drift,
3. OpenAPI, vocabulary, no-alias, and domain-contract drift,
4. security scanner findings, dependency findings, and unsafe production assertions,
5. complexity, function-size, and low-maintainability hotspots,
6. test coverage quality for the actual behavior being changed,
7. observability, runtime-status, lineage, and supportability evidence when runtime behavior changes.

During implementation:

1. prefer a shared helper, typed model, service boundary, or existing local pattern over copy-paste,
2. avoid broad rewrites unless the user asked for them and the proof plan covers the blast radius,
3. remove stale special cases when the slice safely reaches them,
4. keep public behavior unchanged unless the behavior change is intentional, tested, documented, and
   represented in API or contract truth,
5. treat report-only inventories as planning evidence and blocking gates as minimum standards, not
   as permission to add weak code that barely passes.
6. finish and merge one proof-backed RFC slice before opening the next, unless the user explicitly
   asks for a planning branch and the branch is clearly marked as unmerged planning work.

Do not claim progress from:

1. cosmetic renames, formatting-only churn, or doc-only optimism,
2. tests that only assert mocks were called while ignoring domain output,
3. allowlists or suppressions without a documented reason and follow-up,
4. generated abstractions that hide complexity without reducing duplicated responsibility,
5. PR summaries that overstate readiness beyond the evidence.

Reject agent-produced backend code that only appears plausible. A Lotus backend change is low
quality if it:

1. creates a parallel service, mapper, DTO, status enum, or contract vocabulary when a governed
   helper or schema already exists,
2. adds local branching, coercion, or fallback behavior that bypasses canonical domain rules,
3. copies calculations, serialization envelopes, query shaping, or error mapping instead of
   extracting the shared responsibility,
4. weakens observability, lineage, runtime-status, or supportability evidence for operator-facing
   paths,
5. adds tests that only freeze implementation mechanics while leaving domain output, failure
   behavior, or contract truth unverified.

## Required Validation Thinking

Map validation to the platform lanes:

1. Feature Lane:
   - lint
   - typecheck
   - fast unit
   - fast contract/schema checks
2. PR Merge Gate:
   - integration
   - coverage
   - security audit
   - OpenAPI / vocabulary / no-alias / migration smoke where relevant
   - Docker build validation where relevant
3. Main Releasability:
   - release-grade rerun and artifact posture
4. Platform End-to-End Validation:
   - required when the change affects canonical product flows, gateway/upstream behavior, seeded demo flows, or platform runtime assumptions

Remote workflows should consume repo-native commands rather than reimplementing local validation in
YAML. If a Make/NPM target exists for a test, coverage, contract, security, or quality gate, call
that target from GitHub Actions. Add or repair the target before adding raw workflow-level `pytest`,
coverage, or scanner commands, and update the CI contract gate when workflow drift should become
blocking.

If the backend change affects governed front-office proof:

1. validate the authoritative service locally,
2. use the canonical runtime path for product-surface proof,
3. do not claim UI readiness from backend checks alone.

## Backend Gold-Standard Checklist

1. API contracts are truthful and fully documented.
2. Naming matches Lotus domain vocabulary.
3. Security and dependency checks are green or explicitly governed.
4. Tests are meaningful, domain-aware, and high-value.
5. The diff reduces or preserves measured duplicate-code, complexity, architecture-boundary,
   security, API-governance, and contract posture.
6. PR evidence lists the actual commands run and any quality metrics that moved.
7. Cross-app impacts are validated at the right layer.
8. Front-office truth claims are supported by governed runtime evidence when the slice affects
   product surfaces.
9. Unmerged remote branches containing durable governance artifacts have been classified as
   `must-merge`, `cherry-pick`, `superseded`, `delete`, or `active`.
10. Any restored durable truth is indexed and pinned by tests or explicit governance evidence where
   the repository has a docs/current-state test pack.

## Cross-App Rule

If the change affects a UI-facing workflow through `lotus-gateway`:

1. validate the backend repo locally,
2. validate `lotus-gateway` if contract shape is affected,
3. require platform-level evidence if canonical UI behavior is part of the slice.

## Final Response Rule

When closing backend work, report:

1. what changed,
2. which repository-native commands were run,
3. which lane(s) were satisfied,
4. any remaining gap or governed deviation.
