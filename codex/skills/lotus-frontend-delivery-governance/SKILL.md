---
name: lotus-frontend-delivery-governance
description: "Use when implementing or reviewing frontend work in Lotus product surfaces such as lotus-workbench or other Lotus UIs. Apply the Lotus platform CI lane model, canonical gateway-first integration rules, browser validation expectations, platform end-to-end evidence requirements, and truthful PR process defined by RFC-0072."
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

## Frontend Gold-Standard Checklist

1. The screen is backed by supported backend functionality.
2. Canonical endpoints are used end to end.
3. Browser validation covers the impacted screen or panel.
4. Screenshot or artifact evidence exists when visually important behavior changed.
5. Copy, state handling, and layout do not drift from the shared system without explicit reason.
6. PR evidence names the real commands and the real routes or panels validated.

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
