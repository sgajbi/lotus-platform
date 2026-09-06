# RFC-0081 Slice 6: Portfolio, Performance, and Risk Surface Uplift Evidence

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Slice: `Slice 6: Portfolio, Performance, and Risk Surface Uplift`
- Date: 2026-04-13
- Status: Partial implementation and active review

## Scope of the slice

Slice 6 started as the analytical-surface assessment for `Portfolio`, `Performance`, and `Risk`,
then became the main implementation track for the first serious product-surface uplift under the
new shell, gateway, and naming model established by slices 3 through 5.

The implemented slice has focused on:

1. portfolio workspace organization, density, and modularization,
2. shell-bootstrap consumption inside the workbench rather than fallback-led shell ownership,
3. performance summary information hierarchy, chart structure, support-state truthfulness, and
   repeated-label reduction,
4. first-pass risk workspace uplift and analytical zoning,
5. code cleanup needed to stop analytical pages from remaining monolithic and page-local.

The slice is not closed. The portfolio surface is materially uplifted, performance summary has been
substantially improved but is still under active refinement, and risk has completed a first uplift
pass but still needs final cross-surface consistency review.

## Repositories and active branches

### `lotus-workbench`

1. Repo: `<workspace-root>/lotus-workbench`
2. Branch: `codex/rfc-0081-slice-1-portfolio-foundation`
3. PR: `#83`

### `lotus-platform`

1. Repo: `<workspace-root>/lotus-platform`
2. Branch: `codex/rfc-0081-ui-uplift-hardening-20260411`
3. This document and `RFC-0081-implementation-checklist.md` carry the implementation ledger.

## Assessment findings that still govern the implementation

The original slice-6 assessment remains valid and still governs the implementation:

1. `Portfolio`, `Performance`, and `Risk` were already directionally summary-first and
   supportability-aware.
2. Risk remained product-important but structurally subordinate to performance.
3. Supportability, methodology, evidence, and truthful unavailable-state handling were strong and
   had to be preserved.
4. `portfolio-workspace.tsx` and parts of the performance surface had clear monolithic hotspots.
5. Chart, drawer, table, and rail ownership was uneven and had to be tightened rather than
   multiplied.

The important correction is that slice 6 did not stop at assessment. Those findings have already
driven real implementation and review-fix work.

## What has been implemented so far

### 1. Portfolio analytical surface

Portfolio is the strongest completed portion of slice 6.

Implemented work includes:

1. analytical main-column extraction from the original coarse `portfolio-workspace.tsx` ownership,
2. section decomposition into insights, changes, and drilldown boundaries,
3. drawer-builder decomposition into metric, exception, and record-specific ownership,
4. right-rail detail-card and definition-list standardization,
5. allocation, top-holdings, summary, and support-state hierarchy refinement,
6. shell-bootstrap consumption so portfolio analytical surfaces are no longer tied to duplicated
   shell ownership assumptions.

Material slice-6 portfolio commits:

1. `cc8c851` `Refine portfolio analytical surface density`
2. `2002cc3` `Stack cramped portfolio insight modules`
3. `08e52a0` `Wire shell bootstrap into portfolio analytics surface`
4. `455658a` `Strengthen portfolio analytical workspace`
5. `fc74bd4` `Refine portfolio analytical ownership and flow`
6. `809c89a` `Fix portfolio analytical review issues`

Assessment:

1. portfolio is materially improved,
2. ownership is clearer,
3. duplicate or mixed-responsibility patterns have been reduced,
4. the surface is acceptable for the current RFC scope,
5. there is still CSS concentration in `globals.css`, but the product surface itself is no longer
   the main slice-6 risk.

### 2. Shell/bootstrap consumption on the analytical surfaces

Slice 6 also completed an important ownership correction:

1. workbench shell tabs are now contract-led from gateway-backed `shellBootstrap`,
2. `app-registry.ts` is reduced to route-activation logic rather than being a second shell source
   of truth,
3. first render is no longer visibly fallback-led in the app switcher,
4. disabled-workspace reasons are governed product copy rather than raw contract leakage.

This is part of slice 6 because the analytical surfaces were still being rendered under the old
fallback-led shell posture even after slices 3 and 5 were documented.

Key commits:

1. `08e52a0` `Wire shell bootstrap into portfolio analytics surface`
2. `455658a` `Strengthen portfolio analytical workspace`
3. `fc74bd4` `Refine portfolio analytical ownership and flow`

### 3. Performance summary surface

Performance summary has seen the largest volume of slice-6 follow-on work and remains the area that
is still open.

Implemented work includes:

1. initial performance and risk analytical-surface uplift,
2. return-path chart structure refactors,
3. tooltip contract extraction and hardening,
4. repeated label and support-layer reduction,
5. unavailable and loading state cleanup,
6. horizon comparison refactors,
7. contributor/drivers cleanup,
8. control-bar compaction,
9. trust-strip hierarchy softening,
10. summary-copy and comparison-density refinement.

Major performance summary commits:

1. `b2cf9ee` `Uplift performance and risk analytical surfaces`
2. `3b4ed4d` `Uplift performance analytics visuals`
3. `f8a5439` `Refine performance hierarchy and unavailable states`
4. `e26b4ef` `Polish performance return path chart styling`
5. `57eb45b` `Simplify performance chart information hierarchy`
6. `cf00f33` `Condense performance economics strip`
7. `920b192` `Sharpen performance return path annotations`
8. `06f6d05` `Tighten horizon comparison information density`
9. `b6b753a` `Simplify performance contributor detail table`
10. `db7b95a` `Refactor performance return path chart option`
11. `0e16bbd` `Compact performance unavailable states`
12. `670ea63` `Refine performance loading state`
13. `5ba55ba` `Compact performance unavailable module framing`
14. `0c3b0cd` `Reduce repeated performance comparison labels`
15. `3da8f8c` `Compact performance analysis control chrome`
16. `dc33cba` `Rebalance performance chart information hierarchy`
17. `be3e048` `Tighten performance chart tooltip evidence`
18. `da1d38e` `Refactor performance horizon comparison module`
19. `bf20bbe` `Refactor performance analysis detail sections`
20. `ea340fe` `Simplify performance return path support layer`
21. `5e8e9e0` `Refactor performance return path panel composition`
22. `78fb7a4` `Extract performance return path tooltip contract`
23. `ae73bd0` `Rebalance performance return path layout`
24. `28ded71` `Strengthen performance return path chart styling`
25. `5eab1c7` `Condense performance horizon comparison matrix`
26. `3eceb88` `Simplify performance return path summary copy`
27. `e5a8980` `Compress performance analysis control bar`
28. `5b2e9fa` `Soften performance trust strip hierarchy`

Assessment:

1. the code is materially cleaner than the original performance-summary path,
2. responsibility is better split,
3. tooltip behavior is more reliable,
4. repeated comparison information has been reduced,
5. loading and unavailable states are more truthful and less noisy,
6. but the surface is still not visually accepted as final PB-grade analytics UI.

The remaining problem is no longer only code quality. It is final analytical presentation quality.

### 4. Risk surface

Risk received its first slice-6 uplift pass, mainly through `b2cf9ee`.

Implemented work includes:

1. clearer analytical zoning,
2. better framing of primary and secondary risk areas,
3. improved concentration scale legibility,
4. stronger alignment to the shared analytical system.

Assessment:

1. risk is improved,
2. risk is no longer the weakest analytical surface structurally,
3. but it still needs final cross-surface review against portfolio and performance so the product
   feels governed rather than independently polished.

### 5. Slice-6 continuation: cross-mode consistency and advisor refresh behavior

The latest continuation of slice 6 has started tightening the non-summary performance modes as one
governed analytical workspace rather than three adjacent implementations.

Implemented continuation changes include:

1. a shared mode-intro seam for `Analysis`, `Advisor Brief`, and `Risk`,
2. explicit in-place advisor brief refresh behavior instead of relying on re-selecting the active
   mode,
3. centralized performance-workspace mode registry so labels, titles, subtitles, and mode-intro
   copy no longer drift across route entry, mode switching, and advisor drilldown surfaces,
4. extraction of advisor-brief request logic into a dedicated hook,
5. breakup of the prior advisor-brief view-model monolith into dedicated fallback-builder,
   gateway-normalization, and types modules,
6. focused integration and unit assertions that the three modes expose the intended slice-6 framing,
   advisor refresh behavior, and shared mode metadata,
7. compaction of the shared mode-intro presentation so non-summary surfaces read as governed
   analytical stages instead of page-local banners,
8. explicit degraded-state treatment for risk drawdown and rolling panels so partial upstream
   contracts do not leave visually blank analytical regions,
9. breakup of the advisor brief into a denser decision surface by removing duplicate drilldowns,
   compressing the overview/header chrome, and moving narrative, workflow, and exception cards into
   tighter side-by-side presentation where screen width allows,
10. early Gateway advisor-brief fetch behavior so the narrative path no longer waits for unrelated
    detail hydration before starting the backend-backed brief request,
11. supportability normalization so a partial backend advisor-brief contract renders as `Partial`
    instead of misleading `Generating`,
12. acceptance of the human-readable `mode=advisor-brief` route alias so direct links and review
    captures resolve to the governed `advisor` mode instead of silently falling back to summary,
13. further risk-shell compaction across context and executive posture bands so the top-of-screen
    review area is denser without dropping backend-backed content,
14. a new analysis decision-summary band built from live active return, attribution reconciliation,
    contribution coverage, and capability-backed evidence posture,
15. a compact risk supportability panel that summarizes ready-module count, outstanding review
    items, and non-ready contract reasons instead of repeating every ready module in a tall list.

The latest continuation is currently represented on `lotus-workbench` by commit:

1. `411ab3b` `Continue RFC-0081 slice 6 performance surface uplift`

Assessment:

1. this does not close slice 6,
2. it does reduce one of the remaining consistency gaps called out in this document,
3. it also fixes a real interaction weakness in the advisor brief workflow instead of only polishing
   copy or styling,
4. and it makes the live `PB_SG_GLOBAL_BAL_001` risk surface more truthful under partial backend
   conditions by replacing dead space with explicit partial-state guidance.

## Complexity and maintainability gains already achieved

Slice 6 has already reduced complexity in meaningful ways.

### Portfolio

1. coarse workspace composition was split into named analytical sections,
2. drawer logic was split by subject instead of mixed in one builder file,
3. right-rail primitives were standardized,
4. tests were moved toward role- and behavior-based assertions.

### Performance

1. return-path chart responsibilities were separated into smaller units,
2. tooltip contract was extracted and hardened,
3. horizon comparison ownership was tightened,
4. unavailable-state rendering became reusable and more intentional,
5. repeated copy and header clutter were reduced,
6. control-bar and trust-strip hierarchy became more compact and easier to reason about.

### Shell/bootstrap

1. duplicate shell ownership was reduced,
2. the gateway contract is now more honestly consumed by workbench,
3. app switcher behavior is more deterministic.

## High-value evidence collected so far

### Portfolio evidence folders

1. `lotus-workbench/output/playwright/rfc-0081-slice-6a-review`
2. `lotus-workbench/output/playwright/rfc-0081-slice-6b-review`
3. `lotus-workbench/output/playwright/rfc-0081-slice-6c-review`
4. `lotus-workbench/output/playwright/rfc-0081-slice-6c-review-fix`

### Performance and risk evidence folders

1. `lotus-workbench/output/playwright/rfc-0081-slice-6d-current-state`
2. `lotus-workbench/output/playwright/rfc-0081-slice-6d-review`
3. `lotus-workbench/output/playwright/rfc-0081-slice-6e-current-state`
4. `lotus-workbench/output/playwright/rfc-0081-slice-6e-review`
5. `lotus-workbench/output/playwright/rfc-0081-slice-6f-current-state`
6. `lotus-workbench/output/playwright/rfc-0081-slice-6f-review`
7. `lotus-workbench/output/playwright/rfc-0081-performance-current-review`
8. `lotus-workbench/output/playwright/rfc-0081-performance-chart-visual-review`
9. `lotus-workbench/output/playwright/rfc-0081-performance-chart-annotation-review`
10. `lotus-workbench/output/playwright/rfc-0081-performance-economics-review`
11. `lotus-workbench/output/playwright/rfc-0081-performance-hierarchy-review`
12. `lotus-workbench/output/playwright/rfc-0081-performance-analysis-summary-refactor`
13. `lotus-workbench/output/playwright/rfc-0081-performance-chart-readout-review`
14. `lotus-workbench/output/playwright/rfc-0081-performance-return-path-layout`
15. `lotus-workbench/output/playwright/rfc-0081-performance-control-bar-review`
16. `lotus-workbench/output/playwright/rfc-0081-performance-trust-strip-review`
17. `lotus-workbench/output/playwright/rfc-0081-slice-6g-review`
18. `lotus-workbench/output/playwright/rfc-0081-slice-6h-review`
19. `lotus-workbench/output/playwright/rfc-0081-slice-6i-review`
20. `lotus-workbench/output/playwright/rfc-0081-slice-6j-review`
21. `lotus-workbench/output/playwright/rfc-0081-slice-6k-review`
22. `lotus-workbench/output/playwright/rfc-0081-slice-6l-review`

## Validation posture

The implemented slice has not relied on screenshots alone.

Repeated validation has included:

1. focused `vitest` lanes for portfolio, shell, performance, and risk surfaces,
2. `npm run lint`,
3. `npm run typecheck`,
4. `git diff --check`,
5. browser review against the governed workbench runtime,
6. PR `#83` GitHub checks.

Latest focused local proof for the cross-mode continuation:

1. `npx vitest run tests/unit/performance-advisor-brief-mode.test.tsx`
2. `npx vitest run tests/unit/performance-workspace-modes.test.ts`
3. `npx vitest run tests/unit/performance-advisor-brief-view-model.test.ts`
4. `npx vitest run tests/unit/performance-risk-mode.test.tsx`
5. `npx vitest run tests/integration/performance-analytics-page.test.tsx`
6. `npm run lint`
7. `npm run typecheck`

Important runtime truth:

1. some performance browser validation has been limited by governed data/runtime issues,
2. canonical populated performance proof has not been continuously stable,
3. that instability is one reason slice 6 remains partial rather than closed.

## What was consciously not changed

1. no fake performance, risk, or contribution data was introduced to make screenshots look better,
2. no unsupported workflow actions were added,
3. no backend contract was changed inside this evidence update,
4. no claim is being made that risk is already a fully standalone top-level app implementation,
5. no claim is being made that performance summary has reached final PB-grade visual quality,
6. no claim is being made that slice 6 is complete.

## Pending work before slice 6 can be closed

Slice 6 is still open because the remaining work is real, not cosmetic.

### 1. Performance summary final acceptance

Still required:

1. stronger PB-grade chart presentation,
2. final cleanup of repeated comparison information in populated states,
3. sharper analytical hierarchy across return path, horizon comparison, and drivers,
4. final browser validation against stable canonical populated data.

### 2. Risk consistency review

Still required:

1. final review against the shared analytical system,
2. consistency checks with the improved performance surface,
3. decision on whether any remaining risk layout or density issues still fall inside slice 6.

### 3. Advisor brief completion pass

Still required:

1. final advisor-brief parity review against the improved performance summary and analysis modes,
2. removal of any remaining duplicate workflow, exception, or narrative framing,
3. confirmation that advisor refresh, supportability, and drilldown behavior meet the same gold
   standard as the other performance modes.

### 4. Cross-surface consistency pass

Still required:

1. final comparison of portfolio, performance, risk, and advisor surfaces as one governed product,
2. verification that shared analytical primitives are visibly consistent,
3. final review of CSS ownership and any remaining page-local drift.

### 5. Runtime and evidence closeout

Still required:

1. stable canonical browser proof for populated performance states,
2. final review-fix pass if new defects are found during that runtime validation,
3. truthful closure of slice 6 in the implementation checklist only after those gates pass.

## Conclusion

Slice 6 is not complete.

It has already delivered substantial implementation:

1. portfolio analytical uplift is materially real and acceptable for the current RFC scope,
2. shell/bootstrap ownership is materially cleaner,
3. performance summary has been significantly refactored and improved,
4. risk has a first meaningful uplift pass,
5. advisor brief has meaningful slice-6 continuity work but is not yet at final acceptance.

But the slice remains partial because the final quality bar for performance, risk, advisor brief,
and cross-surface consistency has not yet been met. This document now records the actual
implementation state rather than the earlier assessment-only posture.
