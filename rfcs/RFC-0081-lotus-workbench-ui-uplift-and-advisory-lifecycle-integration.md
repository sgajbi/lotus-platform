# RFC-0081: Lotus Workbench UI Uplift and Advisory Lifecycle Integration

- Status: Proposed
- Date: 2026-04-11
- Owners: lotus-platform governance
- Requires Approval From:
  - lotus-workbench maintainers
  - lotus-gateway maintainers
  - lotus-advise maintainers
  - lotus-manage maintainers
  - lotus-report maintainers
  - lotus-ai maintainers
- Related:
  - `RFC-0066-lotus-advise-to-lotus-advise-and-lotus-manage-split.md`
  - `RFC-0070-gold-standard-product-experience-foundation-and-ownership-model.md`
  - `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
  - `RFC-0076-canonical-front-office-demo-data-contract.md`
  - `RFC-0077-workbench-panel-registry-and-evidence-contract.md`
  - `RFC-0078-modular-front-office-validation-framework.md`
  - `RFC-0079-gateway-evidence-and-lineage-contract.md`

## Summary

Lotus needs a product-quality UI uplift that does more than restyle cards.

The target state is a dense, modular, banking-grade front-office platform where:

1. portfolio analytics,
2. risk and performance review,
3. advisory proposal construction,
4. proposal approval and consent,
5. execution handoff,
6. future manage, report, and AI-assisted workflows

all feel like one coherent product rather than separately designed screens.

This RFC proposes:

1. a governed UI uplift program for the Lotus shell and core workspaces,
2. first-class `lotus-advise` integration into the UI,
3. a micro-frontend composition model for long-term scalability,
4. a uniform design system and interaction model for portfolio, performance, risk, proposal, and advisory surfaces,
5. explicit UI support for AI-generated content disclosure and feedback,
6. a cleanup and modernization program focused on UI speed, navigability, architectural quality, and dead-code removal.

## Decision

Lotus will evolve the front-office UI into a modular multi-workspace shell centered on `lotus-workbench`.

Specifically:

1. `lotus-workbench` will become the governed front-office shell for portfolio, performance, risk, proposal, and advisory workflows,
2. advisory proposal creation and lifecycle management from `lotus-advise` will be surfaced as first-class product capabilities, not secondary utilities,
3. `lotus-gateway` will evolve into the governed experience-composition layer for shell bootstrap,
   workspace modules, workflow truth, and future agentic AI assist surfaces,
4. the UI architecture will move toward a governed micro-frontend model with shared shell, navigation, design tokens, and contract-backed module boundaries,
5. visual uplift will be treated as a product architecture program, not a one-off redesign,
6. AI-assisted features must expose provenance, disclosure, and user feedback affordances from day one.

The decision also includes these non-negotiable implementation rules:

1. no workspace may adopt a new visual language outside the shared shell and design system,
2. no proposal or advisory surface may present lifecycle readiness without contract-backed workflow truth,
3. no shell or module boundary may be introduced without a clear `lotus-gateway` ownership model
   for experience composition,
4. no AI-assisted surface may render without explicit provenance and feedback affordances,
5. no micro-frontend split is acceptable if it weakens shell consistency, observability, or accessibility,
6. the shell, gateway composition layer, module boundaries, and design system are treated as
   product infrastructure, not optional frontend convenience.

## Scope

This RFC governs:

1. the target shell experience for `lotus-workbench`,
2. the visual and interaction system for portfolio, performance, risk, proposal, and advisory workspaces,
3. first-class UI integration of `lotus-advise` proposal and lifecycle capabilities,
4. the `lotus-gateway` composition and experience-contract requirements needed to support the shell
   and micro-frontend model,
5. the module composition model for current and future Lotus front-office workspaces,
6. AI-assisted disclosure and feedback behavior in front-office UI surfaces,
7. the technical architecture expectations required to support a modern banking-grade frontend.

This RFC does not govern:

1. the detailed backend business logic of advisory, performance, risk, or reporting services,
2. the exact gateway payload schema for every future workspace,
3. a full visual design spec for every page state,
4. a single-release migration of all Lotus product surfaces,
5. replacement of prior RFCs covering canonical data, panel registry, validation framework, or gateway evidence contracts.

## Governed Source Of Truth

Implementation under this RFC must align to these governed sources:

1. `lotus-workbench` as the primary front-office shell,
2. `lotus-gateway` as the experience API and UI composition contract owner,
3. `RFC-0076` for canonical front-office dataset and seeded runtime truth,
4. `RFC-0077` for panel ownership, supportability, and screenshot governance,
5. `RFC-0078` for modular front-office validation and live browser proof,
6. `RFC-0079` for gateway evidence and lineage posture,
7. `RFC-0080` for agent routing, runtime guidance, and async GitHub delivery behavior.

## Problem

The current Lotus UI direction is improving, but the next product bar is higher.

The issues are:

1. some current and historical surfaces look like individually styled screens rather than a unified institutional platform,
2. advisory workflows are not yet represented as a first-class operating model in the UI,
3. proposal lifecycle stages from idea to consent to execution are still fragmented,
4. the system needs a scalable frontend architecture before more workflows from `lotus-manage`, `lotus-report`, and `lotus-ai` arrive,
5. the UI needs denser decision support without becoming visually noisy or dashboard-generic,
6. AI-generated outputs need explicit disclosure and feedback handling to be credible in a banking-grade context,
7. some current routes and frontend patterns still carry avoidable navigation cost, performance weight, or stale implementation debt.

## Reference Review

The shared reference images show several useful patterns and several anti-patterns.

### What is worth carrying forward

1. summary-first portfolio headers with immediate commercial context,
2. dense but readable table layouts for holdings and allocation review,
3. lateral navigation and nested workspace patterns that support drill-down without losing context,
4. before/after proposal comparison views,
5. client-artifact workflows that tie proposal content to approval and delivery,
6. integrated news, signals, and workflow side rails where they directly support advisory action.

### What should not be copied directly

1. older admin-template tab bars and dated chart chrome,
2. over-fragmented secondary nav that forces too many stacked tab systems,
3. low-hierarchy chart pages with excessive white space,
4. inconsistent card density and table rhythm,
5. UI patterns that feel retail-fintech or legacy desktop rather than private-banking institutional.

### What the references imply for Lotus

The strongest target is:

1. Bloomberg-adjacent clarity,
2. private-banking polish,
3. dense front-office review ergonomics,
4. proposal and workflow state represented as first-class product surfaces,
5. charts, tables, and workflow rails designed to support decisions, not decoration.

## Visual and Interaction Patterns Derived From The References

The references imply a specific product grammar that Lotus should adopt deliberately.

### Pattern 1: Entity-anchored shell header

The strongest portfolio screens all start with a stable entity header that keeps the banker oriented.

Lotus should use a consistent top-of-workspace structure:

1. breadcrumb and relationship hierarchy,
2. entity title such as household, portfolio, proposal, or client artifact,
3. compact KPI strip with the most decision-relevant measures,
4. top-right action rail for the primary workflow actions,
5. a secondary workspace tab bar below the header.

This pattern should be reused across:

1. portfolio overview,
2. performance review,
3. risk review,
4. proposal workspace,
5. proposal approval and consent,
6. artifact preview.

### Pattern 2: Summary rail before deep content

The references consistently perform better when they show:

1. the top-level commercial state,
2. the immediate workflow or analytical posture,
3. the primary actions,

before the user sees dense tables or charts.

Lotus should therefore standardize a summary-first page archetype:

1. header band,
2. status or KPI rail,
3. primary analytical or workflow modules,
4. detail tables and drill-down content.

### Pattern 3: Workspace-within-workspace navigation

The most useful references support drill-down without forcing a full route change.

Lotus should standardize three navigation layers:

1. shell workspace navigation:
   - `Portfolio`
   - `Performance`
   - `Risk`
   - `Proposal`
   - `Advisory`
2. page-local sub-navigation:
   - tab or segment bar for the active workspace
3. in-panel drill-down:
   - drawers, side panels, segmented toggles, or sub-tabs

This should replace ad hoc stacks of inconsistent tabs.

Navigation should optimize for:

1. low click depth,
2. preserved user orientation,
3. fast movement between review and action,
4. consistent return paths during deep drill-down flows.

### Pattern 4: Comparison as a first-class representation

Proposal screens are strongest when they show before/after context directly rather than burying it in
narrative.

Lotus should treat comparison as a first-class pattern:

1. current vs proposed allocation,
2. current vs proposed return path,
3. current vs proposed risk posture,
4. current vs proposed funding or FX path,
5. current vs proposed client artifact language where relevant.

Comparison should be represented through:

1. paired cards,
2. mirrored bars,
3. twin chart series,
4. delta badges,
5. explicit "why this changed" notes.

### Pattern 5: Decision rail and workflow rail

The strongest advisory references combine analytics with workflow.

Lotus should use a persistent right-side or upper-right decision rail for workflow-bearing screens.

The decision rail should contain:

1. supportability,
2. suitability,
3. compliance,
4. evidence posture,
5. client consent,
6. execution readiness,
7. next required action.

This gives the banker a constant view of what blocks progress.

### Pattern 6: Dense analytical table core

The holdings and attribution references show that front-office users accept density when:

1. hierarchy is clear,
2. numeric alignment is excellent,
3. row rhythm is stable,
4. drill state is obvious.

Lotus tables should therefore support:

1. row grouping and expand-collapse,
2. right-aligned numeric columns,
3. sticky headers,
4. subtle row separators instead of box-heavy grids,
5. totals or benchmark rows with stronger hierarchy,
6. compact filter and sort controls above the table rather than inside every cell.

### Pattern 7: Chart as analytical evidence, not decoration

The references show several chart types that matter in private banking contexts:

1. growth and hypothetical return paths,
2. benchmark-relative return comparison,
3. drawdown and recovery views,
4. attribution over time,
5. allocation donuts or bars,
6. target-vs-actual policy or IPS comparison.

Lotus should adopt chart rules:

1. charts always answer a business question,
2. every chart has explicit comparison context where relevant,
3. legends, benchmarks, and period controls sit in stable positions,
4. tooltips use domain language and exact values,
5. charts never appear without a supporting summary or drill-down action.

### Pattern 8: Client artifact as product surface, not export button

The references make it clear that proposal output is not just a file-generation side effect.

Lotus should model client artifacts as a product surface with:

1. a preview workspace,
2. version identity,
3. included sections,
4. delivery actions,
5. consent state,
6. audit footer,
7. clear distinction between internal rationale and client-facing copy.

## Target UI Representation Model

### Shell composition

The shell should be visually and structurally composed as:

1. top global shell bar:
   - Lotus identity,
   - global search,
   - notifications,
   - user context,
   - shell-wide command entry
2. primary workspace tabs:
   - `Portfolio`
   - `Performance`
   - `Risk`
   - `Proposal`
   - `Advisory`
3. entity context header:
   - relationship or client hierarchy,
   - active portfolio or proposal identity,
   - as-of date and benchmark context where relevant
4. workspace body:
   - left/main analytical region,
   - optional decision rail,
   - optional drawer/detail panel

### Page archetypes

Lotus should standardize page archetypes instead of designing each page from scratch.

Required archetypes:

1. `Overview Workspace`
   - header
   - KPI/status rail
   - 3 to 6 primary modules
   - detail follow-through row
2. `Analytical Deep Dive`
   - header
   - parameter controls
   - large chart or analytical canvas
   - supporting table
   - drill drawer
3. `Workflow Workspace`
   - header
   - workflow gate rail
   - timeline or intent queue
   - decision rail
   - action footer or action cluster
4. `Artifact Preview`
   - artifact summary
   - content preview
   - delivery controls
   - compliance and consent context
5. `Intent Detail`
   - queue on the left,
   - selected intent in the center,
   - review, suitability, and action rail on the right

### Portfolio and analytics page representation

Portfolio, performance, and risk screens should use:

1. compact header KPIs rather than oversized hero cards,
2. a single controlled tab row for the active analytical domain,
3. modular analytical cards with the same metric style,
4. integrated chart-plus-table layouts,
5. drill drawers for methodology, evidence, and detail.

### Proposal and advisory page representation

Proposal and advisory screens should use:

1. lifecycle cards across the top,
2. timeline or intent-ladder views for the core proposal flow,
3. before/after modules for allocation and risk posture,
4. a right-side decision rail for readiness and blockers,
5. embedded artifact and consent actions rather than burying them in separate screens.

## Detailed Visual Standards

### Typography hierarchy

The visual examples imply a strong hierarchy rather than large decorative cards.

Lotus should standardize:

1. page title:
   - large, sharp, high-contrast
2. section title:
   - strong but compact
3. card title:
   - concise, medium-emphasis
4. labels:
   - muted and compact
5. KPI values:
   - tabular, bold, visually stable
6. workflow status text:
   - compact, high-clarity, color-assisted

### Typography and font standards

Lotus should use a disciplined institutional typography system rather than ad hoc page-level font
choices.

Required standards:

1. one governed primary UI type family for shell, cards, tables, and controls,
2. one governed mono or tabular-numeral-capable companion for dense financial values where needed,
3. explicit font-size and line-height scales for:
   - page titles,
   - workspace titles,
   - section headers,
   - card titles,
   - body text,
   - table text,
   - labels,
   - microcopy,
4. tabular numerals by default for financial values, holdings counts, dates, and workflow identifiers,
5. professional, conservative weight usage that avoids consumer-style oversized bold treatments,
6. typography tokens owned by the shared design system rather than page-local CSS overrides.

The target should feel:

1. premium,
2. disciplined,
3. private-banking appropriate,
4. highly readable during long analytical sessions.

### Spacing and density

The target should feel dense but breathable.

Use:

1. consistent 8px spacing steps,
2. tighter vertical rhythm in analytical cards,
3. larger gutters only between major workspace zones,
4. denser tables than cards,
5. compact controls above charts and tables.

### Cards and surfaces

Shared surface rules should be:

1. restrained neutral page background,
2. white or near-white work surfaces,
3. thin neutral borders,
4. controlled rounding,
5. almost no heavy shadow,
6. status tint only where business state matters.

### Status representation

Workflow and supportability states should use a governed palette:

1. `ready`
   muted green,
2. `review required`
   muted amber,
3. `pending`
   warm neutral or amber,
4. `blocked`
   restrained red,
5. `partial`
   amber-neutral blend,
6. `ai-assisted`
   neutral blue-gray with explicit label.

Status should appear in:

1. badges,
2. workflow gate cards,
3. row-level indicators,
4. decision-rail modules,
5. artifact and approval modules.

## Chart Representation Standards

### Core chart families to support

The references imply Lotus should standardize these chart families:

1. line and area return series,
2. hypothetical growth curves,
3. drawdown series,
4. stacked or grouped attribution bars,
5. grouped return comparison bars,
6. donut and bar allocation comparisons,
7. IPS target or min-max band comparisons,
8. contributor and detractor bar views.

### Chart interaction rules

1. period selectors should sit in a stable header row above the chart,
2. benchmark toggles should be explicit,
3. tooltip language should use portfolio and benchmark business terminology,
4. legends should be consistent across workspaces,
5. export and methodology access should be available without cluttering the chart body.

### Chart layout rules

1. avoid oversized blank canvases,
2. pair each major chart with either:
   - summary metrics,
   - a drill table,
   - or explanatory notes,
3. charts must preserve comparability across modules by using shared color and axis rules.

## Table Representation Standards

### Holdings and analytics tables

Lotus should standardize:

1. expandable grouped rows,
2. numeric precision rules,
3. right-aligned values,
4. support for sticky controls and sticky headers,
5. visible totals and summary rows,
6. direct drill actions on important rows.

### Proposal action tables

Proposal tables should add:

1. intent order,
2. instrument or pair,
3. notional,
4. purpose,
5. funding dependency,
6. execution readiness,
7. supportability or exception state.

## Proposal and Advisory Representation Standards

### Proposal workspace

The proposal workspace should visually combine:

1. proposal context header,
2. workflow lifecycle rail,
3. intent ladder,
4. before/after comparison module,
5. funding and FX module,
6. decision rail,
7. client artifact action module.

### Proposal detail page

The proposal detail page should visually combine:

1. intent queue on the left,
2. selected intent and business rationale in the center,
3. decision, compliance, and action modules on the right,
4. execution payload preview below,
5. explicit dependencies and funding trace.

### Artifact preview page

The artifact preview page should represent:

1. client-facing narrative summary,
2. before/after allocation visuals,
3. proposed action summary,
4. delivery actions,
5. artifact versioning,
6. consent posture,
7. compliance footer.

### Approval and consent page

The approval page should represent:

1. workflow timeline,
2. approval pack,
3. client consent controls,
4. exceptions and notes,
5. execution blocking reason,
6. reminder and follow-up actions.

## AI-Assisted Representation Standards

AI-assisted surfaces should use a consistent representation model.

They should visibly show:

1. `AI-assisted` or `AI-generated` provenance,
2. whether human review has occurred,
3. whether the content is draft, recommended, or approved,
4. a feedback entry point adjacent to the AI surface,
5. the underlying workflow context the AI content belongs to.

AI-generated rationale, summaries, or proposal language should appear inside bounded modules that
cannot be confused with authoritative workflow status.

## Explicit Anti-Patterns To Avoid

The references also make clear what Lotus should not do.

Avoid:

1. stacked tab bars with no clear hierarchy,
2. giant low-information hero regions,
3. equal visual emphasis across all sections,
4. noisy gradients and decorative illustrations,
5. dashboard cards with no action or drill-down value,
6. export-first proposal UX without workspace context,
7. chart pages with detached tables and no explanation,
8. proposal pages that look like static reports instead of operational workspaces,
9. AI-generated content that appears unlabelled,
10. micro-frontend splits that produce visual fragmentation.

## Goals

1. Create a fresh, uniform, premium UI language for Lotus front-office work.
2. Make advisory proposal workflows from `lotus-advise` first-class in the product shell.
3. Support the full advisory lifecycle:
   - idea,
   - rationale,
   - proposal construction,
   - supportability and suitability review,
   - client artifact generation,
   - consent,
   - execution handoff,
   - audit and follow-through.
4. Define a micro-frontend architecture that can scale across current and future Lotus apps.
5. Keep the UI dense, interactive, modular, and extendable without page-local hacks.
6. Standardize state handling for loading, empty, partial, ready, error, blocked, and pending workflow states.
7. Add governed AI disclosure and quality-feedback patterns for AI-assisted features.
8. Make the UI materially faster and easier to navigate for front-office users.
9. Improve architecture quality by replacing weak frontend seams with governed shared patterns.
10. Remove dead code, duplicated frontend structures, and stale UI implementation patterns exposed by the uplift.

## Non-Goals

1. Replacing domain ownership boundaries in backend services.
2. Creating a separate consumer-style design language.
3. Shipping decorative concept mocks without backend support planning.
4. Treating proposal UI as a static PDF-export tool only.
5. Rebuilding the whole UI in one unsafe big-bang release.

## Product Principles

The uplift must follow these principles:

1. summary first, detail on demand,
2. exceptions before raw data,
3. business language over technical language,
4. every widget supports an action, drill-down, or decision,
5. empty portfolios and empty proposals still feel useful,
6. no decorative UI without decision value,
7. reusable patterns over one-off implementations,
8. modular architecture over page-local hacks,
9. every data module handles loading, empty, partial, ready, error,
10. front-office trust, speed, and clarity over novelty,
11. navigation efficiency over unnecessary route churn,
12. dead code and stale patterns should be removed, not preserved for convenience.

## Delivery And Governance Rules

This RFC must be implemented with the same governance posture used for the recent Lotus platform RFCs.

That means:

1. slice-by-slice delivery only,
2. each slice reviewed before moving to the next,
3. dead code and duplicate patterns removed when touched,
4. meaningful tests added as part of the slice rather than deferred,
5. small, truthful commits,
6. GitHub used asynchronously for heavier checks rather than blocking on local reruns,
7. a final slice covering documentation, agent context, skill alignment, and branch hygiene.

## Target Product Model

### Primary workspaces

The front-office shell should support governed primary workspaces:

1. `Portfolio`
   relationship, holdings, exposures, operational context, cash and booking context.
2. `Performance`
   returns, attribution, benchmarking, performance evidence, review notes.
3. `Risk`
   risk snapshot, drawdown, concentration, rolling risk, attribution, evidence.
4. `Proposal`
   proposal workspace, intent ladder, before/after allocation, suitability and execution readiness.
5. `Advisory`
   pipeline, opportunity queue, signals, review tasks, lifecycle oversight, client engagement state.

Future workspaces should fit the same shell:

1. `Manage`
2. `Reporting`
3. `AI`

### Proposal lifecycle representation

The proposal experience should not be a single page.

It should include:

1. proposal workspace overview,
2. intent-by-intent detail,
3. before/after portfolio context,
4. funding and FX path,
5. rationale and suitability notes,
6. supportability and evidence state,
7. client artifact preview,
8. consent and approval workflow,
9. execution handoff status,
10. audit trail and exceptions.

### Advisory lifecycle representation

`lotus-advise` should surface:

1. opportunity intake,
2. advisor rationale,
3. proposal drafting,
4. collaboration and review,
5. client communication state,
6. approval and consent,
7. execution readiness,
8. post-implementation follow-through.

This should feel operational, not merely analytical.

## UX and Visual Direction

### Visual posture

The UI should feel:

1. premium enterprise SaaS,
2. institutional wealth platform,
3. modern but conservative,
4. dense and credible,
5. polished enough for client-facing and banker-facing workflows.

### Visual rules

1. restrained neutral backgrounds,
2. white or near-white work cards,
3. sharp typography hierarchy,
4. strong table and metric rhythm,
5. subtle emphasis through spacing, border, and tone rather than decorative color,
6. status color used intentionally for readiness, blockers, exceptions, and workflow gating,
7. tabular numerals for money and metrics,
8. consistent chart styling across workspaces,
9. shared action toolbar patterns,
10. one shell language across all modules.

### Density rules

The product should be denser than generic SaaS dashboards while remaining calm.

That means:

1. fewer oversized empty cards,
2. more split panels, drawers, side rails, and tabbed analytical views,
3. compact but readable KPI bands,
4. strong table ergonomics,
5. rich context panels for workflow and decision support.

## Micro-Frontend Architecture Direction

### Shell and module model

Lotus should move toward a governed shell-plus-module architecture.

The shell should own:

1. global navigation,
2. workspace switching,
3. route identity,
4. breadcrumb and entity context,
5. top-level search and command access,
6. notifications,
7. permissions and workspace entitlements,
8. shared design tokens and UI primitives,
9. common evidence, state, and AI disclosure patterns.

Independently owned modules should own:

1. workspace-specific screens,
2. contract-backed data modules,
3. domain-specific interactions,
4. module-local tests and validation,
5. clearly defined extension points.

### Ownership expectations

Likely ownership model:

1. `lotus-workbench`
   shell, shared UI framework, route composition, canonical front-office experience.
2. `lotus-gateway`
   UI composition contracts and experience APIs.
3. `lotus-performance`
   authoritative performance module data and evidence.
4. `lotus-risk`
   authoritative risk module data and evidence.
5. `lotus-advise`
   advisory proposal and lifecycle domain contract.
6. `lotus-manage`
   operational implementation and account-management workflows.
7. `lotus-report`
   governed artifact generation and reporting surfaces.
8. `lotus-ai`
   AI-assisted insight, drafting, summarization, and recommendation capabilities.

### Technical direction

This RFC does not lock the exact frontend framework mechanics, but it does require:

1. module boundaries that are explicit,
2. shared shell contracts,
3. versioned module interfaces,
4. route-level lazy loading,
5. reusable shared component packages,
6. strict avoidance of cross-module styling drift and duplicated local primitives.

## Architecture and Technology Review

The UI uplift will fail if it is treated as visual polish on top of weak frontend architecture.

The product direction in this RFC requires a modern UI foundation with explicit decisions across:

1. shell composition,
2. module boundaries,
3. state and data flow,
4. design-system ownership,
5. performance,
6. observability,
7. accessibility,
8. security and auditability,
9. rollout and compatibility.

### What a modern banking-grade UI requires

Lotus should treat the UI as product infrastructure.

That means the frontend architecture must support:

1. modular delivery without visual fragmentation,
2. contract-backed rendering rather than page-local data shaping,
3. consistent state management across analytical and workflow-heavy surfaces,
4. predictable performance under dense tables and chart-heavy workloads,
5. strong auditability for workflow state and AI-assisted actions,
6. accessibility and keyboard-first usability suitable for power users,
7. controlled rollout and backward compatibility as modules evolve.

### Recommended shell architecture

The shell should be a persistent application frame in `lotus-workbench` with:

1. route orchestration,
2. navigation and entity context,
3. shared command bar and search,
4. notification center,
5. common access to evidence, workflow state, and AI provenance,
6. layout primitives for:
   - header bands,
   - KPI rails,
   - decision rails,
   - drawers,
   - comparison panels,
   - artifact previews.

The shell should not directly own domain business logic.

It should also reduce interaction cost by:

1. preserving entity context across workspace transitions,
2. avoiding unnecessary remounting of heavy analytical surfaces,
3. supporting predictable keyboard and command-driven navigation,
4. keeping common actions reachable without forcing users through repeated route resets.

### Recommended module architecture

Each workspace module should be independently evolvable, but governed.

Modules should be designed around:

1. route-level boundaries,
2. explicit registration into the shell,
3. clear contract dependencies,
4. local composition of cards, charts, tables, and workflows,
5. shared primitive reuse rather than local component forks.

The preferred module shape is:

1. shell-owned route registration,
2. gateway-backed data adapters,
3. module-local presentation components,
4. module-local tests,
5. shared design tokens and shared UI primitives imported from a common layer.

### Micro-frontend recommendation

Lotus should use a pragmatic micro-frontend model, not an over-engineered one.

The recommendation is:

1. one governed shell application,
2. route-level workspace modules,
3. shared UI foundation package,
4. shared contract and types package where appropriate,
5. controlled lazy loading of workspace modules,
6. versioned module registration and compatibility rules.

Lotus should avoid:

1. independently styled micro-apps,
2. duplicated routing stacks,
3. duplicated design tokens,
4. duplicated state libraries or conflicting runtime assumptions,
5. runtime composition mechanisms that make debugging and supportability opaque.

### Gateway-first data composition

The RFC should remain aligned with Lotus gateway-first architecture.

For modern UI delivery, this means:

1. modules consume page-entry and panel-entry contracts primarily through `lotus-gateway`,
2. modules do not fan out directly to multiple backend services from the browser without an explicit exception,
3. workflow state, evidence, freshness, and supportability should arrive with the payload,
4. UI-local derived presentation state should be kept separate from authoritative workflow and analytical truth.

### Gateway requirements for shell and modular UI composition

`lotus-gateway` must explicitly support the uplift rather than acting as a thin pass-through.

Required gateway responsibilities:

1. shell-entry contracts for workspace bootstrap and entity context,
2. workspace-level composition contracts for portfolio, performance, risk, proposal, and advisory,
3. workflow and lifecycle truth for proposal, approval, consent, and execution handoff,
4. supportability, evidence, freshness, and partial-state metadata delivered with module payloads,
5. contract versioning that supports phased workspace rollout and micro-frontend evolution,
6. agentic AI context packaging for future assist surfaces where applicable,
7. stable identifiers and telemetry correlation fields that support shell observability and audit.

The target gateway posture is:

1. experience-oriented,
2. composition-aware,
3. module-friendly,
4. version-governed,
5. supportive of progressive rollout and partial capability states.

### Frontend state model

The frontend should standardize state at three levels:

1. shell state:
   - route,
   - active entity,
   - workspace selection,
   - command surfaces,
   - notifications,
   - user/session context
2. module query state:
   - filters,
   - periods,
   - benchmark toggles,
   - selected intent,
   - selected tab,
   - drawer state
3. workflow state:
   - proposal lifecycle,
   - approvals,
   - consent,
   - execution readiness,
   - AI review status

The architecture should explicitly prevent workflow truth from being represented only as local UI state.

### Design-system ownership model

The design system should be a governed shared layer, not a set of copied components.

It should include:

1. tokens:
   - color,
   - spacing,
   - typography,
   - radius,
   - border,
   - elevation,
   - chart palette
2. primitives:
   - buttons,
   - badges,
   - tabs,
   - cards,
   - drawers,
   - data tables,
   - segmented controls,
   - timeline,
   - decision rail modules,
   - form controls
3. complex patterns:
   - KPI strip,
   - before/after comparison,
   - workflow gate rail,
   - artifact preview,
   - AI provenance block

### Performance requirements

The target UI is dense. Performance has to be engineered, not assumed.

The architecture should support:

1. route-level code splitting,
2. lazy loading of heavy analytical modules,
3. virtualization for large tables,
4. efficient chart rendering for long time series,
5. memoization or derived-state control only where justified,
6. prefetching of likely next-step workflow routes,
7. performance budgets for initial route load and panel hydration.

The uplift should explicitly optimize:

1. initial shell load,
2. workspace switch latency,
3. table interaction latency,
4. chart interaction latency,
5. proposal workflow step transition latency.

### Navigation and information architecture requirements

The UI uplift must materially improve navigability.

Required standards:

1. one clear primary workspace navigation model,
2. one clear page-local secondary navigation model,
3. no stacked secondary tab systems without explicit business justification,
4. drawers, detail rails, and contextual drill-downs preferred over unnecessary full-page context switches,
5. entity identity, workflow state, and location context preserved during deep review and approval flows.

### Codebase cleanup and dead-code expectations

RFC-0081 is also a cleanup program.

Implementation must:

1. remove dead page-local styling and layout patterns when shared replacements exist,
2. remove duplicate components that should become shared primitives,
3. retire stale navigation patterns that conflict with the shell model,
4. collapse one-off analytical implementations into governed reusable modules where appropriate,
5. retire obsolete routes and components once replacement surfaces are validated and adopted.

### Accessibility and power-user ergonomics

A modern banking-grade UI must work for keyboard-heavy expert users.

Required standards:

1. keyboard navigation across shell, tabs, drawers, and tables,
2. visible focus management,
3. accessible chart summaries and non-visual equivalents where needed,
4. semantic structure for screen readers,
5. contrast and state clarity that do not rely on color alone,
6. shortcut-friendly interaction for frequent banker workflows.

### Observability and supportability

The UI architecture should support operational debugging and product trust.

Frontend observability should include:

1. route and module identity,
2. panel load timing,
3. failed contract fetch visibility,
4. partial-state and degraded-state telemetry,
5. user action traces for proposal and approval workflows,
6. AI interaction and feedback telemetry,
7. correlation with gateway request identifiers where appropriate.

### Security, entitlements, and audit

The modern UI model must handle banking-grade controls explicitly.

Requirements:

1. module and action visibility driven by entitlements,
2. no hidden client-side-only authorization assumptions,
3. proposal and approval actions must be auditable,
4. client artifact delivery and consent interactions must preserve audit context,
5. AI-assisted actions must preserve provenance and user interaction history.

### Configuration and rollout model

The architecture should support phased rollout without destabilizing the shell.

It should use:

1. feature flags for new workspace modules,
2. route-level enablement by environment and entitlement,
3. compatibility-safe module registration,
4. version-aware gateway contracts where needed,
5. safe fallback behavior when a module is unavailable or partially supported.

### Testing strategy for a modern UI platform

The UI platform should follow a layered testing model:

1. shared primitive unit tests,
2. module component tests,
3. contract tests against gateway-facing payload shapes,
4. visual regression tests for key archetypes,
5. browser workflow tests for advisory and proposal lifecycles,
6. shell integration tests across modules,
7. governed live validation through the canonical front-office runtime.

### Migration strategy implications

A modern UI uplift should be incremental.

The recommended migration posture is:

1. establish the shared shell and design-system layer first,
2. migrate one workspace at a time,
3. keep legacy routes functional until replacement workspaces are proven,
4. remove dead page-local patterns only after shared replacements exist,
5. use validation and screenshot evidence to prove real user-facing improvement.

### Architecture review conclusion

The UI uplift requires:

1. a governed shell,
2. route-level modular composition,
3. gateway-first data contracts,
4. a shared design system,
5. workflow-grade state management,
6. performance and accessibility standards,
7. observability and audit support,
8. phased rollout controls.

Without these, the product may look more modern temporarily but will not scale cleanly as Lotus
adds more workspaces and ecosystem capabilities.

## Technical Decision Summary

To avoid ambiguity, the technical target state for this RFC is:

1. one persistent `lotus-workbench` shell,
2. route-level workspace modules rather than unrelated page bundles,
3. gateway-first contract delivery for analytical and workflow surfaces,
4. shared design-system ownership rather than per-workspace styling,
5. explicit shell, module, and workflow state boundaries,
6. observability, accessibility, entitlement, and audit support built in from the start,
7. feature-flagged incremental rollout rather than a big-bang cutover.

## Naming and Domain Language Standards

The uplift should use banking-grade naming throughout the UI, frontend architecture, and route
model.

Required standards:

1. workspace names, page names, component names, and route names should use business language over
   generic UI wording,
2. `Portfolio`, `Performance`, `Risk`, `Proposal`, and `Advisory` should remain the primary shell
   vocabulary unless a governed domain decision replaces them,
3. workflow states should use domain-correct terms such as:
   - `Suitability Review`,
   - `Client Consent`,
   - `Execution Readiness`,
   - `Approval Pack`,
   - `Artifact Preview`,
4. component and module names should reflect business purpose rather than presentational structure,
5. APIs and UI contracts should use consistent domain terminology across gateway, frontend, and
   documentation,
6. low-signal or generic names such as `widget`, `box`, `panel2`, `temp`, `misc`, or
   `data-card-new` are not acceptable in the target state.

Naming should reinforce:

1. private banking context,
2. portfolio construction and review language,
3. advisory and workflow decision semantics,
4. operational clarity for future agents and developers.

## Frontend Topology and Code-Organization Standards

RFC-0081 is not only a visual uplift. It also defines the right frontend topology for long-term
growth.

Required standards:

1. shell-level code must live separately from workspace module code,
2. shared primitives, tokens, and layout patterns must live in governed shared layers,
3. route-level workspace modules should own only their domain presentation and interaction logic,
4. page-local implementations must not duplicate shell, chart, table, status, or workflow
   primitives,
5. large monolithic frontend files should be broken into:
   - route orchestration,
   - data adapters,
   - presentation components,
   - state hooks,
   - workflow components,
   - tests,
6. file and folder naming should make ownership obvious at a glance,
7. obsolete components, route fragments, style files, and transitional wrappers should be removed
   once replacement paths are validated.

The right topology is:

1. shared shell,
2. shared design system,
3. shared domain-aware UI patterns,
4. route-level workspace modules,
5. gateway-backed adapters,
6. feature-flagged composition boundaries,
7. clean retirement paths for replaced code.

This topology is required so future modules from `lotus-advise`, `lotus-manage`, `lotus-report`,
and `lotus-ai` can be added without creating another cycle of duplicated styling, fragmented
navigation, or page-local architectural debt.

## Agentic AI Product Readiness

The UI and frontend architecture should be designed for future agentic AI capabilities, not merely
for static AI-generated text blocks.

The target state should support agentic AI features such as:

1. guided proposal assembly,
2. AI-assisted rationale drafting,
3. next-best-action recommendations,
4. workflow-aware exception summarization,
5. execution preparation assistance,
6. cross-workspace research and portfolio insight copilots,
7. explainability and review surfaces tied to banker decision flow,
8. AI search and semantic discovery across portfolios, proposals, artifacts, and workflow evidence,
9. command-driven modern product features such as unified search, contextual recommendations, and
   workflow-aware assist entry points.

### Agentic AI design requirements

Agentic AI should appear as a governed collaborator inside the workflow, not as an isolated chat
widget bolted onto the shell.

Required patterns:

1. contextual assist panels bound to the active portfolio, proposal, approval, or review task,
2. explicit task framing so the user understands what the agent is helping with,
3. visible separation between:
   - AI suggestion,
   - human decision,
   - authoritative workflow state,
4. review, accept, reject, and revise actions attached to AI-assisted outputs,
5. feedback capture tied to specific agent outputs and business tasks,
6. traceable links from AI outputs back to source context, evidence, and workflow stage.

AI search should follow the same rules:

1. search results must preserve entity and workflow context,
2. semantic retrieval must distinguish authoritative records from AI-generated summaries,
3. search results should support direct navigation into governed workspaces rather than detached
   result pages,
4. AI-assisted search explanations must be reviewable and attributable.

### Agentic AI architecture requirements

The frontend architecture should preserve room for agentic capabilities without destabilizing the
shell.

Required technical posture:

1. agentic surfaces plug into the governed shell and route model rather than bypassing it,
2. AI modules consume contract-backed context from gateway-facing composition layers,
3. long-running AI tasks support progressive states such as queued, generating, review-required,
   failed, and approved,
4. streaming or staged AI responses must not break layout stability or keyboard usability,
5. AI actions must emit telemetry, audit metadata, and user feedback events,
6. agentic interactions must support entitlement and workflow gating rules,
7. AI-specific UI components should be shared primitives rather than one-off page widgets.

The architecture should also support:

8. shell-level federated search entry points,
9. hybrid keyword and semantic search result models,
10. extensible command surfaces for future AI-assisted navigation and task execution,
11. modular result renderers for portfolios, positions, proposals, approvals, artifacts, and AI
    insights.

### Agentic AI technology and extension implications

Technology choices under this RFC should avoid boxing Lotus into a static page model that becomes
hard to evolve when agentic workflows arrive.

Implementation should therefore prefer:

1. modular route composition,
2. asynchronous task-aware UI state models,
3. event-friendly observability hooks,
4. reusable side-panel, drawer, and decision-rail patterns,
5. shell-level affordances that can host future AI assist experiences without visual drift,
6. search-friendly information architecture and stable entity identifiers,
7. composition patterns that can support AI search, command palettes, and modern assist layers
   without reworking the shell.

Agentic AI support should remain workflow-native, auditable, and subordinate to banker control.

### Modern feature readiness requirements

The shell and module architecture should be chosen so Lotus can add modern front-office features
without another foundational rewrite.

This includes support for:

1. AI search,
2. command palette or command center navigation,
3. cross-workspace saved views and deep links,
4. workspace-level notifications and recommendations,
5. contextual side-panel assistance,
6. future report and manage modules that plug into the same shell,
7. progressive enhancement of AI-assisted workflow controls over time.

Technology and architectural choices should therefore optimize for:

1. extensible shell primitives,
2. contract-backed cross-workspace discovery,
3. route and entity stability,
4. modular rendering of heterogeneous search and workflow results,
5. performance under always-available search and assist surfaces.

## Data Module Standards

Every major UI module must support:

1. loading,
2. empty,
3. partial,
4. ready,
5. error,
6. blocked or pending workflow state where applicable.

Each module should declare:

1. owning service,
2. primary gateway contract,
3. supportability state,
4. refresh or staleness behavior,
5. evidence requirements,
6. action affordances,
7. downstream workflow implications.

Modules should also declare:

8. layout archetype,
9. performance sensitivity,
10. entitlement sensitivity,
11. AI-provenance requirements if applicable.

## Advisory and Proposal Integration Requirements

### Minimum advisory capabilities to surface

1. proposal list and pipeline state,
2. proposal draft and edit workflow,
3. rationale capture,
4. before/after allocation comparison,
5. intent ladder and funding path,
6. suitability review state,
7. supportability review state,
8. client artifact generation and preview,
9. consent capture,
10. execution handoff.

### Proposal workspace requirements

The proposal workspace should show:

1. portfolio context,
2. client context,
3. advisory objective,
4. target risk or income posture,
5. current-state vs proposed-state allocation,
6. intent-by-intent action list,
7. expected risk and performance shifts,
8. workflow gate state,
9. artifact readiness,
10. exceptions and required approvals.

## AI Disclosure and Feedback Requirements

Any AI-assisted surface must make three things explicit:

1. that the content is AI-generated or AI-assisted,
2. what the human approval status is,
3. how the user can provide quality feedback.

### Required AI UI elements

1. AI-generated badge or provenance label,
2. generation timestamp,
3. generating capability or source label where appropriate,
4. human-reviewed or not-reviewed state,
5. structured feedback controls:
   - useful,
   - not useful,
   - requires correction,
   - explain issue,
6. audit-friendly storage of feedback and revision history.

### AI restrictions

1. AI-generated text must not be visually indistinguishable from authoritative workflow state,
2. AI suggestions must not bypass suitability, compliance, or approval steps,
3. AI content must be traceable to its generating workflow and source context.

## Design System and Interaction Standards

The uplift should formalize:

1. shell navigation,
2. workspace tabs,
3. decision rails,
4. timeline components,
5. compact KPI strips,
6. comparison cards,
7. analytical chart containers,
8. dense institutional tables,
9. workflow gate cards,
10. AI provenance and feedback components.

This should be implemented as shared primitives and patterns, not duplicated page-local design.

The design system should explicitly encode the representation patterns described above so future
modules from `lotus-manage`, `lotus-report`, and `lotus-ai` inherit the same shell language rather
than inventing new page archetypes.

## Testing and Validation Requirements

Required validation should include:

1. design-system unit and visual tests,
2. module contract tests,
3. route-level browser validation,
4. panel and workflow-state validation,
5. proposal lifecycle validation from draft through approval handoff,
6. AI disclosure and feedback interaction tests where AI-assisted UI exists,
7. cross-module regression tests for shell consistency.

The implementation should also define:

1. shell performance budgets,
2. accessibility acceptance checks,
3. module registration contract tests,
4. rollback and feature-flag test coverage for newly introduced modules.

Demo screenshots must remain truthful and follow the governed front-office validation path.

## Documentation Requirements

The following should be created or updated during implementation:

1. a shell architecture document,
2. a frontend module ownership map,
3. a design-system token and component contract,
4. proposal workflow UI documentation,
5. advisory lifecycle UI documentation,
6. AI disclosure and feedback UI standards,
7. agent and onboarding guidance where the new shell and module model materially change routing.

## Skills, Context, and Documentation Implications

Implementation of this RFC must include a conscious review of:

1. whether frontend delivery guidance should route UI uplift and shell work differently,
2. whether `lotus-front-office-runtime` should explicitly reference new workspace archetypes,
3. whether onboarding and engineering context docs need updated shell and workspace terminology,
4. whether any old frontend guidance becomes stale once the new shell and module model is introduced.

If no skill or context changes are required for a given slice, that must be documented explicitly in
the slice evidence rather than left implicit.

## Proposed Implementation Slices

### Slice 1: Current-State Assessment and UI Target Model

1. audit the current Lotus shell and major workspaces,
2. map reuse opportunities and major drift areas,
3. define the target workspace model and interaction architecture,
4. document which current patterns are kept, replaced, or retired.

### Slice 2: Gateway Experience-Contract Assessment and Target Model

1. audit current `lotus-gateway` support for shell bootstrap, workspace composition, workflow state,
   and evidence delivery,
2. identify missing gateway capabilities needed for the uplift and modular shell,
3. define the target experience-contract model for current and future workspaces,
4. record which existing gateway patterns are retained, replaced, or deprecated.

### Slice 3: Shell, Navigation, and Design-System Foundation

1. define the upgraded shell,
2. standardize workspace navigation and entity context patterns,
3. formalize shared visual tokens and primitives,
4. remove obvious dead or duplicate shell styling patterns,
5. define shell and navigation performance expectations.

### Slice 4: Gateway Composition Foundation and Contract Hardening

1. define gateway contracts for shell entry, workspace bootstrap, and workflow-bearing surfaces,
2. standardize supportability, freshness, evidence, and partial-state delivery expectations,
3. define contract versioning and rollout posture for modular UI delivery,
4. align naming and domain vocabulary across gateway and shell-facing contracts.

### Slice 5: Portfolio, Performance, and Risk Surface Uplift

1. align the analytical workspaces to one shared system,
2. improve density, hierarchy, tables, charts, and decision rails,
3. ensure supportability, evidence, and empty-state handling stay truthful,
4. remove stale analytical layout patterns and duplicate page-local implementations.

### Slice 6: Advisory and Proposal Workspace Integration

1. bring `lotus-advise` lifecycle capabilities into the shell,
2. implement proposal workspace, proposal detail, artifact preview, and approval surfaces,
3. ensure workflow gates and handoff states are contract-backed.

### Slice 7: Micro-Frontend Composition and Extension Model

1. establish module boundaries and shared shell contracts,
2. define module registration, shared dependencies, and runtime composition rules,
3. define the shared state, entitlement, and observability contracts required for modules,
4. remove page-local composition hacks and dead patterns exposed by the new model,
5. define cleanup and retirement rules for replaced routes and components.

### Slice 8: AI Surface Governance and Agentic Extension Model

1. implement AI-generated content disclosure patterns,
2. add quality feedback controls,
3. define how AI-assisted content interacts with advisory and reporting flows,
4. ensure AI affordances are clearly separated from authoritative workflow state,
5. define audit, telemetry, and review semantics for AI-assisted UI actions,
6. define agentic extension points for future workflow-native AI assist surfaces.

### Slice 9: Performance, Accessibility, and Operability Hardening

1. define and enforce route, shell, and module performance budgets,
2. validate accessibility and keyboard ergonomics across shell and workspace patterns,
3. validate observability, audit, and entitlement behavior across modular surfaces,
4. remove stale implementation paths that undermine operability or maintainability.

### Slice 10: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

1. update shell, design-system, and workspace documentation,
2. update agent guidance if the new shell and workflow model changes routing or runtime expectations,
3. remove dead frontend guidance and stale UI patterns exposed by the uplift,
4. document conscious no-change decisions explicitly,
5. complete branch hygiene, PR evidence hygiene, and cross-repo reference cleanup before closure.

## Acceptance Criteria

1. Lotus has a coherent institutional front-office shell rather than separately styled screens.
2. Portfolio, performance, risk, proposal, and advisory surfaces share one visual and interaction system.
3. `lotus-advise` proposal lifecycle capabilities are represented as first-class UI workflows.
4. `lotus-gateway` is explicitly positioned as the experience-composition layer needed to support
   the shell, workspace modules, and workflow-bearing UI.
5. The UI architecture supports a governed micro-frontend extension model.
6. Shared design primitives replace page-local duplication and poor frontend patterns.
7. AI-generated content is clearly disclosed and feedbackable.
8. The product feels dense, modular, modern, and banking-grade without becoming visually noisy.
9. The RFC defines explicit page archetypes, shell patterns, chart rules, table rules, and proposal
   workflow representations rather than leaving the uplift to subjective interpretation.
10. The RFC defines the technical architecture, state, observability, performance, accessibility,
   entitlement, and rollout requirements needed for a modern banking-grade UI.
11. The RFC defines a governed implementation and closure model, including the final slice for
    documentation, agent context, skill alignment, and branch hygiene.
12. The uplift explicitly improves navigation speed, perceived responsiveness, architecture quality,
    and dead-code removal as part of the program rather than as optional cleanup.
13. The slice model is granular enough to allow structured cross-repo delivery across shell,
    gateway, advisory, AI, performance, and documentation work without turning the RFC into one
    undifferentiated implementation stream.

## Risks and Mitigations

### Risk: Visual redesign outruns backend truth

Mitigation:

1. keep gateway and domain contracts authoritative,
2. require contract-backed module states,
3. do not ship decorative proposal or advisory flows without backend supportability.

### Risk: Micro-frontends create fragmented UX

Mitigation:

1. keep the shell, tokens, and core primitives centralized,
2. use strict module interface contracts,
3. validate shell consistency across modules.

### Risk: Proposal UX becomes presentation-only

Mitigation:

1. tie every proposal screen to lifecycle state and workflow gates,
2. integrate advisory, consent, and execution handoff contracts,
3. ensure proposal artifacts derive from authoritative workflow context.

### Risk: AI features reduce trust

Mitigation:

1. disclose AI provenance clearly,
2. keep human approval state explicit,
3. capture user feedback and audit trail,
4. prevent AI from masquerading as authoritative operational state.

## Approval Request

Approve this RFC if Lotus should proceed with a governed UI uplift and first-class advisory
lifecycle integration program, using `lotus-workbench` as the front-office shell and a modular
micro-frontend direction for future ecosystem growth.
