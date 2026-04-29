---
name: lotus-frontend-delivery-governance
description: "Use when implementing or reviewing frontend work in Lotus product surfaces such as lotus-workbench or other Lotus UIs, including private banking analytics dashboards, Workbench panels, forms, tables, charts, and UI polish. Apply the Lotus platform CI lane model, canonical gateway-first integration rules, browser validation expectations, platform end-to-end evidence requirements, enterprise private-banking UI quality guidance, and truthful PR process defined by RFC-0072."
---

# Lotus Frontend Delivery Governance

Use this skill for Lotus frontend implementation, UI hardening, validation, and PR preparation.

Apply it in line with:

1. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
2. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md`
3. the target repo `REPOSITORY-ENGINEERING-CONTEXT.md`
4. `lotus-platform/rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
5. `lotus-platform/Continuous Integration, Validation, and Release Governance Standard.md`
6. Lotus UI and gateway ownership rules already established in platform RFCs

Use `lotus-platform/context/playbooks/CHANGE-PLAYBOOKS.md` for task sequencing, `lotus-platform/context/playbooks/VALIDATION-PLAYBOOK.md` for proof selection, and `lotus-platform/context/playbooks/FIX-FORWARD-PATTERNS.md` when GitHub or runtime evidence surfaces a real defect.

If the task is specifically about the governed canonical front-office runtime, populated Workbench
panels, or screenshot proof for `PB_SG_GLOBAL_BAL_001`, use `lotus-front-office-runtime` as the
primary routing skill and treat this skill as secondary delivery governance.

For Workbench experience design, analytics UI hardening, or private banking product-surface polish,
also read [Private Banking Analytics UI](references/private-banking-analytics-ui.md). That
reference captures reusable enterprise-grade UI guidance adapted from UI UX Pro Max and Lotus
private banking architecture without making generic design-system generation the source of truth.

## Context-First Rule

Before substantive frontend work:

1. load the central engineering context,
2. load the repo-local context,
3. load only the platform RFCs and standards the task actually needs.

## Working Model

Before changing UI:

1. confirm the repo and branch,
2. confirm the product surface and upstream owner,
3. identify the repository-native commands for:
   - lint
   - typecheck
   - unit
   - integration
   - browser smoke
   - build
   - local parity
4. identify the backing API owner:
   - gateway
   - upstream domain app
   - shared capability service

## Frontend Non-Negotiables

1. UI consumes canonical backend contracts, normally through `lotus-gateway`.
2. Do not fake unsupported product behavior in the UI.
3. Business-critical content should come from backend truth or deterministic view-model logic that is justified and documented.
4. Avoid duplicated UI narration and duplicated figures when the value is already visible elsewhere.
5. Every screen, sub-screen, and panel must handle:
   - loading
   - empty
   - partial
   - ready
   - error
6. For governed Workbench panel or screenshot-proof surfaces, follow the RFC-0076 canonical
   contract and RFC-0077 panel registry rather than page-local assumptions.
7. Screenshots alone are not proof for governed front-office surfaces.

## Workbench Experience Model

For private banking analytics surfaces, organize the screen around advisor workflow value:

1. portfolio identity and as-of context,
2. primary decision or exception requiring attention,
3. performance, risk, advisory, reporting, or operational evidence,
4. drill-down path from summary to explanation to source evidence,
5. supported action with its permission, workflow, and audit posture.

Do not organize the interface around service boundaries or chart inventory. The user should see a
coherent advisor workbench, not a stitched set of backend modules.

## Validation Thinking

Map validation to the platform lanes:

1. Feature Lane:
   - lint
   - typecheck
   - focused unit/integration
2. PR Merge Gate:
   - browser smoke
   - build
   - coverage
   - local parity
3. Main Releasability:
   - releasability rerun and artifact retention
4. Platform End-to-End Validation:
   - required when the change affects canonical screens, sub-screens, panels, seeded demo flows, ingress assumptions, or gateway-backed product behavior

For those canonical runtime tasks, the governed source of truth is:

1. `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`
2. `lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1`

## Frontend Gold-Standard Checklist

1. The screen is backed by supported backend functionality.
2. Canonical endpoints are used end to end.
3. Browser validation covers the impacted screen or panel.
4. Screenshot or artifact evidence exists when visually important behavior changed.
5. Copy, state handling, and layout do not drift from the shared system without explicit reason.
6. PR evidence names the real commands and the real routes or panels validated.
7. Panel support posture is truthful and matches the governed registry state.
8. Private banking analytics panels show as-of date, benchmark or mandate context, currency/unit,
   freshness, supportability, and source/evidence posture where applicable.

## Cross-Repo Rule

If the UI issue is caused by weak upstream input or mapping:

1. fix it in the owning repo where possible,
2. avoid burying the issue in page-local hacks,
3. call out the upstream dependency explicitly in the final response.

## Final Response Rule

When closing frontend work, report:

1. what changed,
2. which routes, screens, or panels were validated,
3. which repository-native commands were run,
4. whether platform end-to-end validation was required and completed.
