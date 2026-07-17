---
name: lotus-frontend-delivery-governance
description: "Use when implementing or reviewing frontend work in Lotus product surfaces such as lotus-workbench or other Lotus UIs, including private banking analytics dashboards, Workbench panels, forms, tables, charts, and UI polish. Apply the Lotus platform CI lane model, canonical gateway-first integration rules, browser validation expectations, platform end-to-end evidence requirements, enterprise private-banking UI quality guidance, non-degradation guardrails against unsupported or low-quality UI code, and truthful PR process defined by RFC-0072."
---

# Lotus Frontend Delivery Governance

Use this skill for Lotus frontend implementation, UI hardening, validation, and PR preparation.

Apply it in line with:

1. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
2. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md`
3. the target repo `REPOSITORY-ENGINEERING-CONTEXT.md`
4. `lotus-platform/rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
5. `lotus-platform/docs/standards/Continuous Integration, Validation, and Release Governance Standard.md`
6. `lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`
7. Lotus UI and gateway ownership rules already established in platform RFCs

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

## Traceability Before Mutation

When the user, an issue-discovery campaign, or a governing workflow requires issue-backed delivery,
complete this checkpoint before the first source mutation:

1. duplicate-check open and closed issues using the failure pattern and concrete symbols,
2. create or reuse one focused issue with evidence, acceptance criteria, and an evaluation
   condition,
3. update the campaign ledger when one exists,
4. carry the issue number through the working plan, branch, commits, PR, merge, and recheck evidence.

Then implement under this delivery skill. Do not create the owning issue retroactively after code
editing has started. This checkpoint does not require an issue for every routine edit when neither
the user nor the governing workflow requires issue-backed delivery.

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

Before editing product UI code, inspect the existing implementation enough to name:

1. the existing component, route, hook, client, view-model, and test patterns in the touched area,
2. the current source of backend truth and whether it is canonical, fixture-only, or unsupported,
3. the existing loading, empty, partial, ready, error, and permission states,
4. the closest meaningful tests and browser/runtime proof commands,
5. the quality signal the slice will improve or preserve.

If you cannot name those items, keep reading before writing code.

Before editing frontend code, produce a short quality intake from the actual product surface:

1. name the canonical gateway endpoint, shared client, or deterministic fixture boundary that owns
   the data,
2. identify the current loading, empty, partial, ready, error, and permission behavior for the
   touched screen or panel,
3. identify the nearest browser/runtime proof command and the viewport or governed panel that must
   be validated,
4. inspect duplicate view-model logic, copied calculations, stale mocks, unsupported feature text,
   and accessibility/layout signals that can regress,
5. state the narrow quality signal the slice will improve or preserve.

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

## Bank-Buyable Default Bar

Treat the Lotus Bank-Buyable Engineering Contract as the default quality posture for frontend work,
even when the user asks for a narrow UI change.

Every meaningful product-surface slice should improve or preserve at least one bank-buyable control:

1. gateway-backed implementation truth,
2. complete state handling for loading, empty, partial, ready, error, stale, degraded, and
   permission-blocked states,
3. accessibility, layout stability, and browser-validated user workflow,
4. safe observability with bounded labels and no sensitive client or portfolio data,
5. meaningful tests and canonical runtime evidence where applicable,
6. implementation-backed README, wiki, route, and panel documentation.

If a UI change reveals unsupported feature text, decorative trust state, stale mocks, duplicated
calculations, or weak browser proof in the touched surface, fix it in the same slice when safe or
record a concrete follow-up in the scorecard, review ledger, or PR evidence.

## Frontend Non-Degradation Bar

Frontend work must leave the product surface at least as truthful, usable, accessible, observable,
and maintainable as it was before the change.

Before editing, identify the quality signals that can regress in the touched UI:

1. gateway/API contract truth and supported backend capability,
2. loading, empty, partial, ready, error, and permission states,
3. layout stability across desktop and mobile viewports,
4. table, chart, filter, drill-down, and action ergonomics for advisor workflows,
5. accessibility semantics, keyboard reachability, focus behavior, and color contrast,
6. duplicate view-model logic, page-local data shaping, and stale mock fixtures,
7. browser validation, screenshot evidence, and canonical runtime proof when visually important.

During implementation:

1. prefer existing components, design tokens, view-model helpers, route conventions, and gateway
   clients before adding local one-off code,
2. keep UI state backed by real contracts or clearly isolated deterministic fixtures for tests,
3. remove stale mock-only or page-local assumptions when the slice safely reaches them,
4. preserve user-facing behavior unless the behavior change is intentional, tested, and documented,
5. use browser or screenshot proof for visual/layout changes, not just unit tests.

Do not claim frontend progress from:

1. decorative polish that hides unsupported backend behavior,
2. screenshots captured before canonical API and panel validation pass,
3. copy-pasted panels with duplicated business calculations,
4. tests that only assert component rendering while ignoring state, data, or interactions,
5. text that describes missing functionality instead of implementing supported workflow behavior.

Reject agent-produced UI that only looks plausible. A Lotus frontend change is low quality if it:

1. introduces a page-local data contract when a gateway or shared client already exists,
2. duplicates calculations, status mapping, table shaping, or chart data transformations already
   owned by a helper or backend contract,
3. renders business-critical values without units, as-of date, source posture, or supportability
   context where the surrounding surface expects them,
4. handles only the happy path while silently weakening existing loading, empty, partial, error, or
   permission behavior,
5. ships layout changes without browser validation for the impacted viewport or governed runtime
   proof when the screen participates in canonical Workbench evidence.

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
9. The diff preserves or improves contract truth, state handling, accessibility, layout stability,
   duplicate view-model posture, and browser-validated behavior.

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


