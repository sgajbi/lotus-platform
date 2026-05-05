---
name: lotus-backend-delivery-governance
description: "Use when implementing or reviewing backend work in Lotus repositories such as lotus-core, lotus-performance, lotus-risk, lotus-advise, lotus-manage, lotus-report, lotus-gateway, or lotus-ai. Apply the Lotus platform CI lane model, enterprise security baseline, contract-governance rules, repository-native command policy, and truthful PR evidence process defined by RFC-0072."
---

# Lotus Backend Delivery Governance

Use this skill for Lotus backend feature work, cleanup, validation, and PR preparation.

Apply it in line with:

1. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
2. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md`
3. the target repo `REPOSITORY-ENGINEERING-CONTEXT.md`
4. `lotus-platform/rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
5. `lotus-platform/Continuous Integration, Validation, and Release Governance Standard.md`
6. repository-local RFCs and standards already in force

Use `lotus-platform/context/playbooks/CHANGE-PLAYBOOKS.md` for task sequencing and `lotus-platform/context/playbooks/VALIDATION-PLAYBOOK.md` when deciding how much proof is required.

Use `lotus-front-office-runtime` as the primary route when the backend change is being validated
through the governed canonical front-office runtime and populated Workbench product surfaces.

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

If the backend change affects governed front-office proof:

1. validate the authoritative service locally,
2. use the canonical runtime path for product-surface proof,
3. do not claim UI readiness from backend checks alone.

## Backend Gold-Standard Checklist

1. API contracts are truthful and fully documented.
2. Naming matches Lotus domain vocabulary.
3. Security and dependency checks are green or explicitly governed.
4. Tests are meaningful, domain-aware, and high-value.
5. PR evidence lists the actual commands run.
6. Cross-app impacts are validated at the right layer.
7. Front-office truth claims are supported by governed runtime evidence when the slice affects
   product surfaces.
8. Unmerged remote branches containing durable governance artifacts have been classified as
   `must-merge`, `cherry-pick`, `superseded`, `delete`, or `active`.
9. Any restored durable truth is indexed and pinned by tests or explicit governance evidence where
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
