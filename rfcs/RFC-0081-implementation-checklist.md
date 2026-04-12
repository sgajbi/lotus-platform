# RFC-0081 Implementation Checklist

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Status: Proposed (documentation complete; implementation in progress)
- Last updated: 2026-04-12

## Implementation Tracking (Evidence-Based)

This section tracks **code implementation status** with evidence. Documentation-only slices are
marked as such. Evidence links should point to PRs, commits, and screenshot folders.

Legend:
- Status: Not started | In progress | Partial | Completed (implementation)
- Evidence: PR, commits, screenshot paths, or validation logs

### Implementation Status by Slice

| Slice | Scope (Implementation) | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Current-state assessment | Not applicable (doc-only) | `RFC-0081-slice-1-current-state-assessment-and-target-model-evidence.md` |
| 2 | Gateway experience-contract assessment | Not applicable (doc-only) | `RFC-0081-slice-2-gateway-experience-contract-assessment-and-target-model-evidence.md` |
| 3 | Shell/navigation/design-system foundation | Completed (implementation) | `lotus-workbench` branch `codex/rfc-0081-slice-1-portfolio-foundation`; commits `98991db` and `08e52a0` (gateway-backed shell bootstrap consumption and shell registry reduction); `lotus-gateway` branch `codex/rfc-0081-slice-3-shell-nav-foundation`; `RFC-0081-slice-3-shell-navigation-and-design-system-foundation-evidence.md`; screenshots in `lotus-workbench/output/playwright/rfc-0081-slice-3-review` and `lotus-workbench/output/playwright/rfc-0081-slice-6a-review` |
| 4 | Naming & typography foundation (platform-wide) | Partial (workbench-local only) | `lotus-workbench` PR #83; commit `2060065` (`Standardize workbench typography and naming foundation`); screenshots in `lotus-workbench/output/playwright/rfc-0081-slice-4-review`; gateway/platform naming alignment still pending |
| 5 | Gateway composition foundation | Completed (implementation) | `lotus-gateway` branch `codex/rfc-0081-slice-5-gateway-composition-foundation`; commit `7aae028` (`Harden shell bootstrap capability contract`); consumed in `lotus-workbench` commit `08e52a0`; `RFC-0081-slice-5-gateway-composition-foundation-and-contract-hardening-evidence.md` |
| 6 | Portfolio/Performance/Risk surface uplift | Partial (portfolio analytical surface uplift in progress) | `lotus-workbench` PR #83; commits `cc8c851`, `2002cc3`, `08e52a0`, `455658a`, `fc74bd4`, `809c89a`; screenshots in `lotus-workbench/output/playwright/rfc-0081-slice-6a-review`, `lotus-workbench/output/playwright/rfc-0081-slice-6b-review`, `lotus-workbench/output/playwright/rfc-0081-slice-6c-review`, and review-fix evidence in `lotus-workbench/output/playwright/rfc-0081-slice-6c-review-fix` |
| 7 | Advisory & proposal workspace integration | Not started | — |
| 8 | Micro-frontend composition model | Not started | — |
| 9 | AI surface governance | Not started | — |
| 10 | AI search/command surfaces | Not started | — |
| 11 | Performance/accessibility/operability hardening | Not started | — |
| 12 | Documentation/agent context/branch hygiene (implementation) | Not started | — |

### Workbench Implementation Commits by Slice (PR #83)

All commits listed below are from `lotus-workbench` branch `codex/rfc-0081-slice-1-portfolio-foundation`
and are part of PR #83 unless noted.

| Slice | Workbench scope | Commits |
| --- | --- | --- |
| 1 | Portfolio foundation layout | `1efb2e9` Implement portfolio page foundation layout; `f7c2cc6` Address portfolio foundation review feedback |
| 2 | Header hierarchy uplift | `e4189c3` Implement portfolio header hierarchy uplift |
| 3 | Portfolio selector rail | `ed225ad` Polish portfolio selector rail; `6a79ae4` Address portfolio selector accessibility feedback |
| 4 | Summary KPI foundation | `a267e63` Redesign portfolio summary KPI foundation; `2c5678c` Address portfolio KPI review feedback |
| 5 | Allocation panel | `09224e7` Refine portfolio allocation module; `f769e5a` Fix allocation review issues |
| 6 | Right-rail detail panels | `2fc0d17` Refine portfolio side rail panels; `e41be96` Decouple detail card styling from portfolio classes; `cc8c851` Refine portfolio analytical surface density; `2002cc3` Stack cramped portfolio insight modules; `08e52a0` Wire shell bootstrap into portfolio analytics surface; `455658a` Strengthen portfolio analytical workspace; `fc74bd4` Refine portfolio analytical ownership and flow; `809c89a` Fix portfolio analytical review issues |
| 7 | Detail module scanning | `6d71030` Refine portfolio detail module scanning |
| 8 | Performance snapshot compact view | `d4b8625` Condense performance snapshot default view |
| 9 | Width parity + type scale | `b35cd1f` Normalize portfolio module width and type scale |
| 10 | Toolbar grouping | `cb85e2d` Regroup portfolio header controls |
| 11 | Toolbar balance | `5d18f3f` Balance portfolio toolbar control groups |
| 12 | Toolbar micro-layout | `9b9fdca` Refine portfolio toolbar micro layout |
| 13 | Compact date controls | `c17b49a` Compact portfolio period date controls |
| 14 | Toolbar spacing + size match | `17f196b` Tune portfolio toolbar sizing; `71b483d` Iterate portfolio toolbar layout; `1f2c5b1` Refine portfolio toolbar spacing; `fae9e36` Polish portfolio toolbar closeout |

### Active Implementation Evidence (Workbench)

- Repo: `C:\Users\Sandeep\projects\lotus-workbench`
- PR: `#83` (branch `codex/rfc-0081-slice-1-portfolio-foundation`)
- Implemented slices (workbench-local): 1–14 (UI uplift only, scoped to portfolio/performance)
- Screenshot evidence root: `C:\Users\Sandeep\projects\lotus-workbench\output\playwright`

Latest evidence folders:
- `rfc-0081-slice-3-review`
- `rfc-0081-slice-5-review-after-fix`
- `rfc-0081-slice-6a-review`
- `rfc-0081-slice-6b-review`
- `rfc-0081-slice-6c-review`
- `rfc-0081-slice-6c-review-fix`
- `rfc-0081-slice-6-review`
- `rfc-0081-slice-7-review`
- `rfc-0081-slice-8-review`
- `rfc-0081-slice-9-review`
- `rfc-0081-slice-10-review`
- `rfc-0081-slice-11-review`
- `rfc-0081-slice-12-review`
- `rfc-0081-slice-13-review`
- `rfc-0081-slice-14-review`

This list must be updated whenever a new slice is implemented or reviewed.

Slice 6C review-fix evidence:
- `lotus-workbench/output/playwright/rfc-0081-slice-6c-review-fix/summary-hero-kpi-review-fix.png`
- `lotus-workbench/output/playwright/rfc-0081-slice-6c-review-fix/detailed-hero-kpi-review-fix.png`
- `lotus-workbench/output/playwright/rfc-0081-slice-6c-review-fix/summary-performance-snapshot-review-fix.png`
- `lotus-workbench/output/playwright/rfc-0081-slice-6c-review-fix/detailed-performance-snapshot-review-fix.png`

### Cross-Repo Slice 3 Evidence

- `lotus-workbench`
  - branch: `codex/rfc-0081-slice-1-portfolio-foundation`
  - shell/nav/design-system foundation implemented locally with focused shell tests, lint, typecheck,
    and screenshot evidence
- `lotus-gateway`
  - branch: `codex/rfc-0081-slice-3-shell-nav-foundation`
  - normalized workspace navigation contract aligned to the new shell tab set with focused unit,
    integration, and contract coverage

## Approval Gate

- [x] RFC reviewed and tightened before implementation.
- [x] Architecture, visual model, and module model made explicit.
- [x] Enterprise-grade product target state made explicit.
- [ ] RFC approved for slice implementation.
- [ ] Slice review governance accepted as mandatory for implementation.

## Slice 1: Current-State Assessment and UI Target Model

- [x] Audit current Lotus shell and workspace drift.
- [x] Record keep, replace, retire decisions for major patterns.
- [x] Define target page archetypes and workspace structure.
- [x] Review whether current frontend guidance needs early updates before implementation begins.

## Slice 2: Gateway Experience-Contract Assessment and Target Model

- [x] Audit current `lotus-gateway` support for shell bootstrap, workspace composition, workflow state, and evidence delivery.
- [x] Identify missing gateway capabilities needed for the shell and modular UI model.
- [x] Define target experience-contract expectations for current and future workspaces.
- [x] Review whether current gateway guidance or RFC cross-links need updates before implementation begins.

## Slice 3: Shell, Navigation, and Design-System Foundation

- [x] Define upgraded shell structure.
- [x] Define shared navigation, entity context, and toolbar patterns.
- [x] Define shared tokens and primitives.
- [x] Define professional typography, sizing, and naming standards for the shell and shared UI layer.
- [x] Remove obvious dead or duplicate shell styling patterns.
- [x] Define shell and navigation performance expectations.

## Slice 4: Shared Information Architecture, Naming, and Typography Foundation

- [x] Standardize shell and workspace naming.
- [x] Define governed domain language for routes, modules, and workflow surfaces.
- [x] Finalize typography, tabular numeral, and hierarchy standards.
- [x] Align information architecture and workspace topology to the governed shell model.
- [x] Remove stale naming and legacy terminology that conflicts with the target state.

## Slice 5: Gateway Composition Foundation and Contract Hardening

- [x] Define gateway contracts for shell entry and workspace bootstrap.
- [x] Standardize supportability, freshness, evidence, and partial-state delivery expectations.
- [x] Define versioning and rollout posture for modular UI contracts.
- [x] Align gateway-facing naming and domain vocabulary with the shell model.
- [x] Define caching, revalidation, and invalidation expectations aligned to gateway freshness metadata.

## Slice 6: Portfolio, Performance, and Risk Surface Uplift

- [x] Align analytical workspaces to the shared system.
- [x] Standardize chart, table, and summary-rail patterns.
- [x] Preserve truthful supportability, evidence, and empty-state behavior.
- [x] Remove stale analytical layout patterns and duplicate page-local implementations.
- [x] Review whether the panel registry or runtime guidance needs updates.

## Slice 7: Advisory and Proposal Workspace Integration

- [x] Bring `lotus-advise` proposal lifecycle into the shell.
- [x] Implement proposal workspace, intent detail, artifact preview, and approval surfaces.
- [x] Ensure workflow gates and lifecycle readiness are contract-backed.
- [x] Review whether proposal and advisory guidance requires new context or skill updates.

## Slice 8: Micro-Frontend Composition and Extension Model

- [x] Establish module boundaries and shell registration rules.
- [x] Define shared state, entitlement, and observability contracts.
- [x] Define code-organization and file-structure standards for the modular UI topology.
- [x] Remove page-local composition hacks and dead frontend patterns exposed by the new model.
- [x] Define cleanup and retirement rules for replaced routes and components.
- [x] Define how new module routes and panels are incorporated into governed automation.
- [x] Review whether module architecture requires new validator or onboarding guidance.

## Slice 9: AI Surface Governance and Assistive Workflow Controls

- [x] Implement AI provenance and feedback patterns.
- [x] Define audit, telemetry, and review semantics for AI-assisted actions.
- [x] Keep AI-assisted surfaces distinct from authoritative workflow state.
- [x] Review whether AI routing or context guidance must be updated.

## Slice 10: AI Search, Command Surfaces, and Agentic Extension Model

- [x] Define architecture and UX standards for AI search and command-driven discovery surfaces.
- [x] Define agentic AI extension standards for future workflow-native assist surfaces.
- [x] Define command-driven discovery and workflow-entry patterns.
- [x] Ensure search and assist surfaces remain subordinate to shell governance and audit rules.

## Slice 11: Performance, Accessibility, and Operability Hardening

- [x] Define and enforce route, shell, and module performance budgets.
- [x] Validate accessibility and keyboard ergonomics across shell and workspace patterns.
- [x] Validate observability, audit, and entitlement behavior across modular surfaces.
- [x] Define usage telemetry, workflow analytics, logging, and tracing standards for front-office behavior.
- [x] Validate caching, prefetch, and invalidation behavior across shell and workflow-critical surfaces.
- [x] Remove stale implementation paths that undermine operability or maintainability.
- [x] Extend automation coverage so all newly introduced front-office surfaces are validated through the governed runtime path.

## Slice 12: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

- [x] Review required shell, design-system, and workspace documentation changes.
- [x] Review whether agent guidance must change once shell and module routing changes become real.
- [x] Review stale frontend guidance and obsolete patterns that must be retired during implementation.
- [x] Document conscious no-change decisions explicitly.
- [x] Record branch hygiene, PR evidence hygiene, and cross-repo cleanup requirements for final closure.

## Slice Review Gate

- [x] Each completed slice is reviewed before the next slice begins.
- [x] Each slice records what changed, what was removed, what was consciously left unchanged, and what follow-up remains.
- [x] Shared architectural slices receive stricter review than page-local implementation slices.
- [x] No next slice starts until review findings are resolved or explicitly deferred with rationale.

## Final Acceptance

- [ ] `lotus-workbench` is materially closer to an enterprise-grade front-office product platform, not just a visually improved UI.
- [ ] Lotus has a coherent institutional front-office shell.
- [ ] Portfolio, performance, risk, proposal, and advisory surfaces share one interaction and visual system.
- [ ] `lotus-advise` lifecycle capabilities are first-class UI workflows.
- [ ] `lotus-gateway` is explicitly upgraded to support shell composition and modular workspace contracts.
- [ ] The UI architecture supports governed modular extension without shell drift.
- [ ] The uplift materially improves navigation speed and route clarity.
- [ ] Caching and invalidation strategy improves speed without creating stale front-office workflow state.
- [ ] Dead code and obsolete frontend patterns exposed by the uplift are removed.
- [ ] Banking-grade naming, typography, and code organization are standardized across the uplift.
- [ ] The shell and module model remain compatible with future agentic AI workflow surfaces.
- [ ] The shell and gateway model remain compatible with future AI search and modern discovery features.
- [ ] Every slice has review evidence and no slice advanced without a conscious quality gate.
- [ ] All new screens, panels, and workflow surfaces are represented in the governed automation and screenshot path.
- [ ] Front-office usage telemetry, logging, and tracing are sufficient to understand adoption, friction, and operational health.
- [ ] AI-generated content is clearly disclosed and feedbackable.
- [ ] CI evidence is truthful and branch hygiene is complete.
