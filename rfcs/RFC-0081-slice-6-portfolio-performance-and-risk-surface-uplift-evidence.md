# RFC-0081 Slice 6: Portfolio, Performance, and Risk Surface Uplift Evidence

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Slice: `Slice 6: Portfolio, Performance, and Risk Surface Uplift`
- Date: 2026-04-12
- Status: Completed and reviewed

## Scope of the assessment

Slice 6 reviewed the current analytical surfaces in `lotus-workbench` to define how portfolio,
performance, and risk should be uplifted under the governed shell, gateway, and naming model
already established by slices 1 through 5.

The slice focused on:

1. current workspace ownership for `Portfolio`, `Performance`, and `Risk`,
2. summary-first and detail-on-demand quality of the analytical pages,
3. supportability, evidence, empty-state, and methodology behavior,
4. chart, table, rail, and drawer consistency,
5. structural hotspots where page-local or monolithic code will undermine the uplift if left
   unaddressed.

The goal of the slice was to decide what analytical patterns are already strong enough to keep and
where later implementation must tighten layout, ownership, and code organization.

## Files and surfaces reviewed

Reviewed directly in `lotus-workbench`:

1. `src/apps/portfolio/portfolio-experience-page.tsx`
2. `src/apps/portfolio/components/portfolio-workspace.tsx`
3. `src/apps/portfolio/capabilities.ts`
4. `src/apps/portfolio/view-model.ts`
5. `src/apps/performance/performance-analytics-page.tsx`
6. `src/apps/performance/components/performance-workspace-view.tsx`
7. `src/apps/performance/workspace-assembler.ts`
8. `src/apps/performance/view-model.ts`
9. `src/apps/performance/advisor-brief-view-model.ts`
10. `src/apps/performance/components/risk/*`

Additional structure checks:

1. `portfolio-workspace.tsx` is approximately `1856` lines,
2. `advisor-brief-view-model.ts` is approximately `776` lines,
3. `performance-view-model.ts` is approximately `301` lines,
4. `risk` currently lives inside the performance workspace rather than as a standalone top-level
   app.

## Current-state findings

### 1. The analytical surfaces already follow summary-first discipline better than many legacy wealth UIs

Evidence:

1. `portfolio-experience-page.tsx` is intentionally thin and delegates to a workspace client,
2. `performance-analytics-page.tsx` renders summary-first and explicitly defers deep detail on
   first paint,
3. `performance-workspace-view.tsx` keeps analysis and evidence deferred behind mode selection,
4. portfolio and performance surfaces already use:
   - rail structures,
   - summary frames,
   - deferred modules,
   - supportability-aware states.

Assessment:

1. keep the summary-first and detail-on-demand discipline,
2. keep deferred loading for heavier analytical and evidence surfaces,
3. keep capability-aware rendering and explicit degraded-state messaging,
4. treat these as governed analytical patterns rather than incidental implementation choices.

Current gap:

1. the interaction model is directionally right, but the surfaces are not yet visually and
   structurally unified enough to feel like one enterprise-grade front-office product.

### 2. Risk is product-important but still structurally subordinate to the performance workspace

Evidence:

1. there is no standalone `src/apps/risk`,
2. `risk` exists as a mode inside the performance workspace,
3. there is a substantial dedicated risk component family under
   `src/apps/performance/components/risk/*`,
4. slice 4 locked `Risk` as a first-class shell workspace.

Assessment:

1. keep the existing risk analytical primitives and supportability behavior,
2. replace the long-term assumption that risk remains only a performance sub-mode,
3. require later implementation to make risk first-class in shell topology while preserving shared
   analytical components where reuse is real,
4. avoid duplicating risk modules just to create a new route.

Current gap:

1. the product language says `Risk` is first-class, but the app topology still treats it as a
   nested performance specialization.

### 3. Supportability, methodology access, and truthful empty-state behavior are already strong and must be preserved

Evidence:

1. `src/apps/portfolio/capabilities.ts` has explicit `partial`, `unavailable`, and hidden-state
   logic,
2. `portfolio/view-model.ts` and `performance/advisor-brief-view-model.ts` preserve partial and
   unavailable reasoning,
3. the risk component family includes methodology and coverage access, detail drawers, and explicit
   empty-state copy,
4. `performance-workspace-view.tsx` already renders degraded-state messaging rather than pretending
   the workspace is ready.

Assessment:

1. keep supportability-state truthfulness,
2. keep methodology and evidence access as first-class analytical behavior,
3. keep empty, partial, and unavailable states explicit and professionally worded,
4. do not trade these truthful states away for cleaner screenshots or simpler layouts.

Current gap:

1. the behavioral model is strong, but the final UI uplift must standardize how these states look
   and where they appear across all analytical surfaces.

### 4. Portfolio and advisory-brief surfaces still contain monolithic hotspots that will slow down the uplift if left untouched

Evidence:

1. `src/apps/portfolio/components/portfolio-workspace.tsx` is approximately `1856` lines,
2. the same file mixes:
   - workspace composition,
   - drawer state,
   - section behavior,
   - metric-detail builders,
   - exception-detail builders,
   - drilldown logic,
   - formatting-oriented rendering helpers,
3. `src/apps/performance/advisor-brief-view-model.ts` is approximately `776` lines and concentrates
   significant supportability, evidence, and narrative logic in one file.

Assessment:

1. keep the underlying domain behavior and business logic,
2. replace monolithic file concentration with clearer boundaries,
3. require later implementation to split:
   - route orchestration,
   - workspace composition,
   - drilldown or drawer builders,
   - analytical modules,
   - state hooks,
   - copy maps,
   - tests,
4. avoid page-local accretion while performing the visual uplift.

Current gap:

1. the code quality risk is not that the product surfaces are weak; it is that some of the strongest
   surfaces are held in files that are already too large for the next wave of product change.

### 5. Charts, tables, rails, and drawers are rich, but pattern ownership is still uneven

Evidence:

1. portfolio uses dedicated holdings, liquidity, projected cashflow, paired analytics, and rail
   modules,
2. performance uses summary, analysis, advisor, risk, and evidence modes with dedicated module
   families,
3. risk has a disciplined drawer and analytical-table family,
4. some analytical interaction patterns are still local to one workspace rather than clearly owned
   as shared enterprise primitives.

Assessment:

1. keep the strong reusable patterns already extracted,
2. replace page-local or workspace-local duplicates where shared ownership is now obvious,
3. require table, drawer, chart, and rail patterns to become more visibly governed by the shared
   system,
4. keep domain-specific content local while promoting generic analytical scaffolding upward.

Current gap:

1. the uplift will create avoidable drift if it adds new page-local table or drawer variants instead
   of consolidating the existing strong patterns.

## Keep / replace / retire decisions

### Keep

1. summary-first analytical framing,
2. deferred loading for heavy analytical and evidence modes,
3. truthful supportability, empty, partial, and unavailable states,
4. methodology and coverage access patterns,
5. rich risk analytical components and drill-down behavior,
6. route-to-workspace delegation where already clean.

### Replace

1. the long-term assumption that `Risk` stays a permanent sub-mode under `Performance`,
2. monolithic portfolio and advisor-brief file concentration,
3. workspace-local ownership of patterns that are now clearly shared analytical primitives,
4. any visual uplift approach that standardizes appearance but leaves structural hotspots untouched.

### Retire

1. new analytical page work that adds more behavior into `portfolio-workspace.tsx`,
2. duplicate chart, drawer, or table scaffolding introduced for one workspace only,
3. hidden topology where product-important surfaces exist only as nested modes without clear shell
   ownership,
4. decorative analytical UI that does not preserve supportability, evidence, or drill-down value.

## Target analytical surface model confirmed by slice 6

Slice 6 confirms the analytical-surface posture for RFC-0081 implementation.

### 1. Portfolio workspace model

The `Portfolio` workspace should remain:

1. summary-first,
2. decision-support focused,
3. rail-aware,
4. drilldown capable,
5. operationally truthful.

Later implementation should tighten:

1. code organization,
2. module boundaries,
3. visual consistency,
4. empty-state and action presentation,
5. layout rhythm across summary and detailed sections.

### 2. Performance workspace model

The `Performance` workspace should remain:

1. summary-first on entry,
2. mode-driven for deep analysis,
3. evidence-aware,
4. benchmark and control-strip friendly,
5. defer-heavy for analysis and evidence.

Later implementation should tighten:

1. visual hierarchy,
2. shared analytical table and chart ownership,
3. shell vocabulary alignment,
4. cleaner boundary between shared analytical primitives and mode-specific content.

### 3. Risk workspace model

The `Risk` workspace should become first-class in the shell while preserving reuse of the existing
risk analytical components.

That means:

1. risk remains analytically dense and evidence-aware,
2. methodology and coverage access remain integral,
3. drawers and deep drilldowns remain first-class,
4. the shell and route model should stop treating risk as merely a nested analytical mode.

### 4. Analytical state and evidence model

All three analytical workspaces must preserve:

1. ready,
2. partial,
3. unavailable,
4. empty,
5. degraded or blocked where workflow truth or source availability requires it.

These states must remain:

1. explicit,
2. business-readable,
3. contract-backed,
4. visually consistent across portfolio, performance, and risk.

### 5. Structural cleanup model

Later implementation should use the uplift to reduce concentration and improve maintainability:

1. split large page-local files,
2. move reusable analytical scaffolding upward,
3. keep domain-specific view-model logic where it belongs,
4. avoid introducing new local helper piles during visual polish,
5. retire duplicated scaffolding once replacements are proven.

## Review of slice 6

### What was improved by the review

The review tightened several important points:

1. it made explicit that current analytical quality is better than the shell-level product posture,
2. it identified risk topology, not analytical depth, as the key structural gap,
3. it confirmed that supportability and methodology access are assets to preserve, not cleanup
   targets,
4. it identified clear monolithic hotspots that later implementation must reduce rather than accept,
5. it clarified that code organization is part of the analytical uplift, not a later optional
   refactor.

### What was consciously not changed in slice 6

1. no `lotus-workbench` code was changed yet,
2. no portfolio, performance, or risk routes were moved yet,
3. no component families were renamed yet,
4. no analytical modules were split yet,
5. no panel registry or runtime guidance was updated yet.

This is correct for slice 6. The slice exists to lock the analytical target model and cleanup
priorities before code changes start.

### Guidance and context decision

No immediate panel-registry or runtime-guidance update is required before implementation begins.

Reason:

1. the current slice defines analytical uplift and cleanup priorities, but the governed runtime and
   panel registry should only be updated after the analytical surfaces and topology actually change,
2. updating validation guidance now would risk documenting target surfaces that are not yet adopted
   in the product runtime.

This is a conscious no-change decision.

### Follow-up implications for slice 7

Slice 7 should proceed with these tighter assumptions:

1. proposal and advisory workspaces must reach the same supportability and drilldown quality as the
   analytical surfaces,
2. workflow-bearing proposal pages should borrow the strongest summary-first and drawer patterns
   already present in analytical pages,
3. proposal surfaces must avoid creating new monoliths similar to the largest current analytical
   files,
4. workflow truth must remain stricter than analytical read-side freshness and supportability.

## Conclusion

Slice 6 is complete.

It produced a code-grounded analytical-surface assessment, explicit keep/replace/retire decisions,
and a defensible uplift model for portfolio, performance, and risk that preserves existing strengths
while forcing structural cleanup where the next stage of enterprise product work would otherwise
create more drift and code concentration.
