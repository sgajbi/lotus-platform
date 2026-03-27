# RFC-0070: Gold-Standard Product Experience Foundation and Ownership Model

- Status: Proposed
- Date: 2026-03-26
- Owners: lotus-platform governance
- Requires Approval From:
  - lotus-platform maintainers
  - lotus-workbench maintainers
  - lotus-gateway maintainers
  - lotus-core maintainers
  - lotus-performance maintainers
  - lotus-risk maintainers
  - lotus-advise maintainers
  - lotus-manage maintainers
  - lotus-report maintainers
  - lotus-ai maintainers

## Summary

Lotus now has the right service topology to become a world-class product ecosystem:

1. `lotus-core` as canonical portfolio and ledger truth,
2. `lotus-performance` as advanced performance analytics authority,
3. `lotus-risk` as advanced risk analytics authority,
4. `lotus-advise` as advisory workflow authority,
5. `lotus-manage` as discretionary lifecycle and automation authority,
6. `lotus-report` as reporting authority,
7. `lotus-gateway` as the UI-facing experience API,
8. `lotus-workbench` as the primary product surface,
9. `lotus-ai` as the shared governed AI capability plane,
10. `lotus-platform` as the governance and standards authority.

That topology is necessary, but not sufficient.

The current risk is not lack of functionality alone. The deeper risk is experience fragmentation:

1. screen-by-screen growth instead of product-system design,
2. gateway-level patching of upstream problems,
3. inconsistent ownership of UI-facing quality,
4. AI introduced as novelty instead of as governed product capability,
5. standards applied unevenly across applications,
6. teams optimizing local convenience instead of ecosystem quality.

This RFC defines the first and most important product-experience foundation for the next phase:

1. `lotus-workbench` becomes the primary application shell for the Lotus ecosystem,
2. `lotus-gateway` evolves into a `v2` experience API organized around journeys and workspaces,
3. upstream application teams remain responsible for fixing their own domain contract and rendering-input issues,
4. platform standards from `lotus-platform` remain mandatory across the experience stack,
5. AI capabilities enter the product through `lotus-ai` under explicit ownership and governance rather than ad hoc UI embedding.

This RFC is intentionally first in a broader product-experience sequence.

It does not attempt to solve every workflow, app, visual system, or AI capability in one move.
It establishes the operating model and sequencing needed so that later RFCs can deepen the product
without creating architectural debt.

## Why This Is First

Lotus can only reach a gold-standard product outcome if the ecosystem agrees on:

1. where the primary user experience lives,
2. what the gateway owns versus what upstream apps own,
3. how standards propagate across the platform,
4. how AI is introduced without collapsing boundaries,
5. how improvements are routed to the right repository instead of being papered over centrally.

Without this RFC:

1. `lotus-workbench` risks becoming a collection of disconnected screens,
2. `lotus-gateway` risks becoming a dumping ground for fixes that belong upstream,
3. UI quality issues caused by weak upstream contracts will be masked instead of corrected,
4. `lotus-ai` adoption could become flashy but structurally unsound,
5. the ecosystem could become harder to evolve precisely when ambitions rise.

This is therefore the highest-priority foundation RFC because it sets the product-system
ownership model before large new implementation waves begin.

## Problem Statement

The current platform has strong momentum, but the product-experience architecture is still in a
transitional state.

Current issues:

1. `lotus-workbench` is still closer to a set of feature slices than to a premium app shell.
2. `lotus-gateway` still reflects incremental aggregation more than a full experience-API model.
3. Several Lotus apps expose backend-oriented contracts that are good enough for integration but not
   yet ideal as polished product rendering inputs.
4. There is no single governing RFC yet that says how world-class UI quality, ownership discipline,
   and future AI product capabilities should work together across the whole Lotus estate.
5. The platform has standards, but it still needs a product-facing operating rule that those
   standards must shape the experience architecture, not only backend engineering hygiene.

The platform therefore needs:

1. one clear product shell strategy,
2. one clear experience-API strategy,
3. one clear ownership rule for where fixes belong,
4. one clear sequencing rule for AI-enabled product capability,
5. one explicit program structure for follow-on RFCs.

## Goals

1. Make `lotus-workbench` the primary product workspace for the Lotus ecosystem.
2. Make `lotus-gateway` the primary experience API for that workspace.
3. Establish that upstream application teams own the quality of domain truth and rendering inputs.
4. Keep `lotus-platform` as the mandatory standards and governance authority.
5. Define how `lotus-ai` will enter the ecosystem as a governed capability plane rather than a
   source of UI or domain ownership drift.
6. Prioritize the first implementation waves so the platform moves toward a premium product
   architecture without a reckless big-bang rewrite.

## Non-Goals

1. Defining the full visual design system in this RFC.
2. Defining every `lotus-workbench` screen and route.
3. Defining every `lotus-gateway` `v2` endpoint.
4. Migrating every current page or endpoint immediately.
5. Making `lotus-gateway` the owner of domain-specific data cleanup or domain semantics.
6. Allowing `lotus-ai` to become the source of truth for business logic or workflow decisions.
7. Solving every UX defect across the estate in one document.

## Decision

The Lotus ecosystem will adopt the following operating model.

### 1. `lotus-workbench` is the primary product shell

`lotus-workbench` will evolve from route-level slices into a cohesive application shell with
domain applications inside it.

Target app categories:

1. Foundation
2. Performance
3. Risk
4. Proposal
5. Manage
6. Reporting
7. Platform

### 2. `lotus-gateway` is the experience API, not the source of truth

`lotus-gateway` will evolve into a `v2` experience API organized around:

1. workspaces,
2. page-entry payloads,
3. task and activity surfaces,
4. action-oriented UI workflows,
5. supportability and evidence retrieval for product surfaces.

It may:

1. aggregate,
2. normalize,
3. enrich,
4. parallelize,
5. degrade gracefully under partial failure.

It may not become:

1. a replacement domain service,
2. a permanent band-aid for upstream contract defects,
3. the owner of business semantics that belong in domain apps.

### 3. Fix issues at the right layer

This RFC establishes a non-negotiable ownership rule:

1. `lotus-workbench` owns presentation composition and interaction quality.
2. `lotus-gateway` owns experience orchestration and UI-facing aggregation contracts.
3. Each domain application owns the correctness and quality of the data, workflow semantics, and
   rendering inputs that originate from that domain.
4. `lotus-ai` owns shared AI capabilities and their governance.
5. `lotus-platform` owns cross-app standards and architecture governance.

When a UX or UI problem is caused by weak or missing domain-owned inputs, the fix should be made in
the owning application repository.

If the issue is discovered while building `lotus-workbench` or `lotus-gateway`:

1. raise a GitHub issue in the owning repository,
2. describe the product impact,
3. link the needed contract, metadata, or behavior improvement,
4. avoid burying the problem in gateway-only workaround logic unless a temporary mitigation is
   explicitly approved.

### 4. `lotus-platform` standards remain mandatory

This product-experience program must continue to follow platform governance, including:

1. domain boundaries and service ownership,
2. OpenAPI and vocabulary governance,
3. durability, scalability, and observability standards,
4. engineering baseline and CI expectations,
5. migration and data-model ownership rules,
6. centralized shared-infrastructure ownership.

This RFC does not replace those standards. It applies them to the product-experience layer.

### 5. `lotus-ai` enters through governed capability integration

Future AI features are expected to become highly differentiated and product-defining.
That is desired.

But the entry path must be governed:

1. domain apps remain responsible for their business meaning,
2. `lotus-ai` provides bounded reusable AI capabilities,
3. `lotus-workbench` integrates those capabilities as polished product experiences,
4. `lotus-gateway` may broker AI-backed experience contracts where appropriate,
5. no AI feature should bypass platform governance or ownership boundaries.

This means:

1. no direct free-form AI layer stuffed into the shell without app ownership,
2. no gateway-owned pseudo-AI business logic,
3. no UI-only AI features that cannot be traced back to domain-owned context and `lotus-ai`
   capability governance.

## Experience Architecture Direction

### `lotus-workbench`

`lotus-workbench` should move toward:

1. one persistent app shell,
2. portfolio-first and task-aware navigation,
3. shared design-system and interaction primitives,
4. app-level workspaces for each bounded context,
5. premium visual and motion quality,
6. resilient partial-failure handling and operator trust cues.

### `lotus-gateway`

`lotus-gateway` should move toward:

1. `v2` experience endpoints organized by workspace and journey,
2. explicit response-envelope and partial-failure models,
3. per-panel or per-surface source attribution and freshness metadata,
4. bounded caching for read-heavy overview surfaces,
5. screen-oriented orchestration modules rather than thin route mirroring.

### Upstream apps

Upstream apps must increasingly provide:

1. better rendering inputs,
2. stronger metadata for as-of, lineage, freshness, and warnings,
3. UI-usable action and workflow semantics,
4. cleaner ownership of domain explanations and evidence references,
5. more product-ready contracts rather than only backend-composable payloads.

## Follow-On RFC Program

This RFC is the foundation, not the full program.

The intended follow-on sequence should include at least:

### Wave 1: Product shell and experience API foundation

1. `lotus-workbench` shell and design-system foundation
2. `lotus-gateway` `v2` experience-envelope and partial-failure contract
3. Foundation app first-production surface

### Wave 2: Domain app productization

1. Performance workspace
2. Risk workspace
3. Proposal workspace
4. Manage workspace
5. Reporting workspace

### Wave 3: Cross-app product capabilities

1. task inbox and activity model
2. shared search and recent items
3. saved views and collaboration primitives
4. export, reporting, and evidence workflows

### Wave 4: AI-enabled product differentiation

1. AI capability integration model for `lotus-workbench`
2. app-specific AI capability adoption RFCs
3. `lotus-ai` capability-pack rollout into Lotus apps
4. AI trust, evidence, and operator review UX

This ordering is deliberate:

1. shell and ownership first,
2. high-quality app experiences second,
3. shared workflow capabilities third,
4. differentiated AI experiences after the product foundation is sound.

## Delivery Slices

### Slice 1: Foundation governance and target-architecture alignment

Outcome:

1. the ecosystem agrees on the product shell and experience-API model,
2. ownership rules are explicit,
3. the issue-routing rule is formalized,
4. standards and AI posture are anchored.

Acceptance gate:

1. the RFC is approved,
2. the target architecture is documented in `lotus-workbench` and `lotus-gateway`,
3. teams agree that upstream UX/input issues should be fixed in the owning repo.

### Slice 2: `lotus-workbench` shell foundation

Outcome:

1. a new shell foundation exists in `lotus-workbench`,
2. app-oriented packaging starts replacing route-centric packaging,
3. design-system and shell primitives are established.

Acceptance gate:

1. the new shell is real, not only conceptual,
2. app navigation and shared layout primitives exist,
3. future product surfaces can be built on the shell without structural rework.

### Slice 3: `lotus-gateway` `v2` experience API foundation

Outcome:

1. a `v2` namespace exists,
2. shared envelope and partial-failure contracts exist,
3. first workspace-oriented orchestration modules exist.

Acceptance gate:

1. `v1` remains stable,
2. `v2` enables app-by-app migration,
3. the gateway is moving toward journey-shaped contracts rather than upstream mirroring.

### Slice 4: Foundation app first

Outcome:

1. the first production-grade app surface exists,
2. it proves the shell, gateway, and ownership model together,
3. it exposes gaps in upstream contracts early.

Acceptance gate:

1. the app is materially better than the current slice UI,
2. upstream issues discovered are logged in the owning repos where needed,
3. no major gateway-only workaround debt is silently introduced.

### Slice 5: Follow-on app and AI waves

Outcome:

1. the pattern expands to performance, risk, proposal, manage, reporting, and AI-enabled
   experiences,
2. the platform compounds quality instead of fragmenting.

Acceptance gate:

1. later RFCs follow the ownership and sequencing rules set here,
2. AI adoption remains governed through `lotus-ai`,
3. upstream ownership remains clear as the ecosystem grows.

## Risks

1. teams may still choose short-term gateway workarounds instead of fixing upstream issues.
2. the shell may be treated as a branding pass instead of as real architecture.
3. AI enthusiasm may pressure the platform to skip product-foundation work.
4. standards may be cited but not made operational in product delivery.
5. too much scope may be loaded into the first implementation wave if sequencing is ignored.

## Alternatives Considered

### Alternative 1: Let `lotus-workbench` and `lotus-gateway` evolve organically

Rejected.

Reason:

1. that would preserve ambiguity,
2. ambiguity will compound into expensive product debt at ecosystem scale.

### Alternative 2: Put most UI-facing fixes into `lotus-gateway`

Rejected.

Reason:

1. that would make the gateway a masking layer for upstream defects,
2. it would weaken service ownership and long-term product quality.

### Alternative 3: Start with AI-first product differentiation

Deferred.

Reason:

1. differentiated AI features are important,
2. but they will create more value on top of a strong product shell, experience API, and
   ownership model than in place of them.

## Initial Implementation Focus

The first implementation focus after approval should be:

1. `lotus-workbench` shell foundation,
2. `lotus-gateway` `v2` experience-API foundation,
3. Foundation app first-production surface,
4. upstream issue-routing discipline for discovered product-input gaps.

The first AI work should be planned, but not forced into the first build wave unless it directly
fits the governed capability model and does not compromise the foundation sequence.

## Acceptance Criteria

This RFC is complete when:

1. the Lotus ecosystem has one explicit product-experience ownership model,
2. `lotus-workbench` is recognized as the primary shell for the product ecosystem,
3. `lotus-gateway` is recognized as the experience API rather than the owner of domain fixes,
4. teams follow the rule that upstream domain-owned UX/input issues are fixed in the owning repo,
5. `lotus-platform` standards remain the governing baseline across the program,
6. `lotus-ai` is explicitly positioned as the governed AI capability plane for later product
   differentiation,
7. follow-on RFCs can proceed from a clear foundation rather than from local assumptions.

## Approval Requested

Approve this RFC if the team agrees that:

1. product excellence across Lotus requires a platform-level product-experience operating model,
2. `lotus-workbench` should become the primary product shell,
3. `lotus-gateway` should become the `v2` experience API rather than a catch-all workaround layer,
4. UI-facing issues that originate in domain apps should be fixed in those owning apps and tracked
   in their repositories,
5. future AI product capabilities should be integrated through `lotus-ai` under explicit governance,
6. implementation should proceed in the prioritized sequence defined above.
