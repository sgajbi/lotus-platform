# RFC-0081 Implementation Checklist

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Status: Proposed
- Last updated: 2026-04-12

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

- [ ] Establish module boundaries and shell registration rules.
- [ ] Define shared state, entitlement, and observability contracts.
- [ ] Define code-organization and file-structure standards for the modular UI topology.
- [ ] Remove page-local composition hacks and dead frontend patterns exposed by the new model.
- [ ] Define cleanup and retirement rules for replaced routes and components.
- [ ] Define how new module routes and panels are incorporated into governed automation.
- [ ] Review whether module architecture requires new validator or onboarding guidance.

## Slice 9: AI Surface Governance and Assistive Workflow Controls

- [ ] Implement AI provenance and feedback patterns.
- [ ] Define audit, telemetry, and review semantics for AI-assisted actions.
- [ ] Keep AI-assisted surfaces distinct from authoritative workflow state.
- [ ] Review whether AI routing or context guidance must be updated.

## Slice 10: AI Search, Command Surfaces, and Agentic Extension Model

- [ ] Define architecture and UX standards for AI search and command-driven discovery surfaces.
- [ ] Define agentic AI extension standards for future workflow-native assist surfaces.
- [ ] Define command-driven discovery and workflow-entry patterns.
- [ ] Ensure search and assist surfaces remain subordinate to shell governance and audit rules.

## Slice 11: Performance, Accessibility, and Operability Hardening

- [ ] Define and enforce route, shell, and module performance budgets.
- [ ] Validate accessibility and keyboard ergonomics across shell and workspace patterns.
- [ ] Validate observability, audit, and entitlement behavior across modular surfaces.
- [ ] Define usage telemetry, workflow analytics, logging, and tracing standards for front-office behavior.
- [ ] Validate caching, prefetch, and invalidation behavior across shell and workflow-critical surfaces.
- [ ] Remove stale implementation paths that undermine operability or maintainability.
- [ ] Extend automation coverage so all newly introduced front-office surfaces are validated through the governed runtime path.

## Slice 12: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

- [ ] Update shell, design-system, and workspace documentation.
- [ ] Update agent guidance if the shell and module model materially changes runtime or routing behavior.
- [ ] Remove stale frontend guidance and obsolete patterns exposed by the uplift.
- [ ] Document conscious no-change decisions explicitly.
- [ ] Complete branch hygiene, PR evidence hygiene, and cross-repo reference cleanup before closure.

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
