# RFC-0081 Implementation Checklist

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Status: Proposed
- Last updated: 2026-04-11

## Approval Gate

- [x] RFC reviewed and tightened before implementation.
- [x] Architecture, visual model, and module model made explicit.
- [ ] RFC approved for slice implementation.

## Slice 1: Current-State Assessment and UI Target Model

- [ ] Audit current Lotus shell and workspace drift.
- [ ] Record keep, replace, retire decisions for major patterns.
- [ ] Define target page archetypes and workspace structure.
- [ ] Review whether current frontend guidance needs early updates before implementation begins.

## Slice 2: Gateway Experience-Contract Assessment and Target Model

- [ ] Audit current `lotus-gateway` support for shell bootstrap, workspace composition, workflow state, and evidence delivery.
- [ ] Identify missing gateway capabilities needed for the shell and modular UI model.
- [ ] Define target experience-contract expectations for current and future workspaces.
- [ ] Review whether current gateway guidance or RFC cross-links need updates before implementation begins.

## Slice 3: Shell, Navigation, and Design-System Foundation

- [ ] Define upgraded shell structure.
- [ ] Define shared navigation, entity context, and toolbar patterns.
- [ ] Define shared tokens and primitives.
- [ ] Define professional typography, sizing, and naming standards for the shell and shared UI layer.
- [ ] Remove obvious dead or duplicate shell styling patterns.
- [ ] Define shell and navigation performance expectations.

## Slice 4: Gateway Composition Foundation and Contract Hardening

- [ ] Define gateway contracts for shell entry and workspace bootstrap.
- [ ] Standardize supportability, freshness, evidence, and partial-state delivery expectations.
- [ ] Define versioning and rollout posture for modular UI contracts.
- [ ] Align gateway-facing naming and domain vocabulary with the shell model.

## Slice 5: Portfolio, Performance, and Risk Surface Uplift

- [ ] Align analytical workspaces to the shared system.
- [ ] Standardize chart, table, and summary-rail patterns.
- [ ] Preserve truthful supportability, evidence, and empty-state behavior.
- [ ] Remove stale analytical layout patterns and duplicate page-local implementations.
- [ ] Review whether the panel registry or runtime guidance needs updates.

## Slice 6: Advisory and Proposal Workspace Integration

- [ ] Bring `lotus-advise` proposal lifecycle into the shell.
- [ ] Implement proposal workspace, intent detail, artifact preview, and approval surfaces.
- [ ] Ensure workflow gates and lifecycle readiness are contract-backed.
- [ ] Review whether proposal and advisory guidance requires new context or skill updates.

## Slice 7: Micro-Frontend Composition and Extension Model

- [ ] Establish module boundaries and shell registration rules.
- [ ] Define shared state, entitlement, and observability contracts.
- [ ] Define code-organization and file-structure standards for the modular UI topology.
- [ ] Remove page-local composition hacks and dead frontend patterns exposed by the new model.
- [ ] Define cleanup and retirement rules for replaced routes and components.
- [ ] Review whether module architecture requires new validator or onboarding guidance.

## Slice 8: AI Surface Governance and Agentic Extension Model

- [ ] Implement AI provenance and feedback patterns.
- [ ] Define audit, telemetry, and review semantics for AI-assisted actions.
- [ ] Keep AI-assisted surfaces distinct from authoritative workflow state.
- [ ] Define agentic AI extension standards for future workflow-native assist surfaces.
- [ ] Define architecture and UX standards for AI search and command-driven discovery surfaces.
- [ ] Review whether AI routing or context guidance must be updated.

## Slice 9: Performance, Accessibility, and Operability Hardening

- [ ] Define and enforce route, shell, and module performance budgets.
- [ ] Validate accessibility and keyboard ergonomics across shell and workspace patterns.
- [ ] Validate observability, audit, and entitlement behavior across modular surfaces.
- [ ] Remove stale implementation paths that undermine operability or maintainability.

## Slice 10: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

- [ ] Update shell, design-system, and workspace documentation.
- [ ] Update agent guidance if the shell and module model materially changes runtime or routing behavior.
- [ ] Remove stale frontend guidance and obsolete patterns exposed by the uplift.
- [ ] Document conscious no-change decisions explicitly.
- [ ] Complete branch hygiene, PR evidence hygiene, and cross-repo reference cleanup before closure.

## Final Acceptance

- [ ] Lotus has a coherent institutional front-office shell.
- [ ] Portfolio, performance, risk, proposal, and advisory surfaces share one interaction and visual system.
- [ ] `lotus-advise` lifecycle capabilities are first-class UI workflows.
- [ ] `lotus-gateway` is explicitly upgraded to support shell composition and modular workspace contracts.
- [ ] The UI architecture supports governed modular extension without shell drift.
- [ ] The uplift materially improves navigation speed and route clarity.
- [ ] Dead code and obsolete frontend patterns exposed by the uplift are removed.
- [ ] Banking-grade naming, typography, and code organization are standardized across the uplift.
- [ ] The shell and module model remain compatible with future agentic AI workflow surfaces.
- [ ] The shell and gateway model remain compatible with future AI search and modern discovery features.
- [ ] AI-generated content is clearly disclosed and feedbackable.
- [ ] CI evidence is truthful and branch hygiene is complete.
