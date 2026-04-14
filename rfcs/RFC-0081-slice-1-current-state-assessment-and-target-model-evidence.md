# RFC-0081 Slice 1: Current-State Assessment and UI Target Model Evidence

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Slice: `Slice 1: Current-State Assessment and UI Target Model`
- Date: 2026-04-12
- Status: Completed and reviewed

## Scope of the assessment

Slice 1 reviewed the current front-office UI posture across:

1. `lotus-workbench` shell, route, and module topology,
2. `lotus-gateway` experience-composition posture,
3. current documentation and capability-contract guidance,
4. current automation posture as it relates to front-office screens and panels.

The goal of the slice was not implementation. The goal was to establish a code-grounded target
model and explicit keep/replace/retire decisions so later slices can change the product
deliberately.

## Files and surfaces reviewed

### `lotus-workbench`

Reviewed directly:

1. `src/shell/app-shell.tsx`
2. `src/shell/app-registry.ts`
3. `src/app/layout.tsx`
4. `docs/architecture/workbench-ui-gateway-capability-contract.md`
5. route inventory under `src/app/*`
6. design-system and workspace module topology under:
   - `src/design-system/*`
   - `src/apps/*`
   - `src/features/*`
7. canonical live-validation scripts under `scripts/live/*`

### `lotus-gateway`

Reviewed directly:

1. `src/app/main.py`
2. `src/app/routers/workbench.py`
3. `src/app/services/workbench_service.py`
4. `src/app/services/async_ttl_cache.py`
5. router/service/contract inventory under `src/app/*`

### `lotus-platform`

Reviewed directly:

1. RFC-0081
2. RFC-0081 implementation checklist
3. current PR state for RFC-0081 hardening

## Current-state findings

### 1. `lotus-workbench` already has the beginnings of the right shell, but it is still too thin

Evidence:

1. `src/shell/app-shell.tsx` is a very small persistent frame with:
   - Lotus brand,
   - app switcher navigation,
   - page body slot
2. `src/app/layout.tsx` consistently mounts the shell.

Assessment:

1. keep the shell-as-root pattern,
2. replace the current shell implementation with a materially richer enterprise shell,
3. add missing shell concerns rather than proliferating page-local substitutes.

Current gaps:

1. no governed global search,
2. no notification center,
3. no command surface,
4. no persistent banker context or entity context model,
5. no explicit shell-level observability or route identity model.

### 2. Navigation vocabulary and route topology do not yet match the target product model

Evidence:

1. `src/shell/app-registry.ts` currently defines:
   - `Overview` (hidden),
   - `Relationship Book` (unavailable),
   - `Portfolio`,
   - `Performance`,
   - `Reporting` (unavailable),
   - `Operations` (hidden)
2. route inventory includes:
   - `/portfolio`
   - `/performance`
   - `/proposals`
   - `/portfolios`
   - `/workbench`
   - `/suite`
   - `/intake`
   - `/recommendations`

Assessment:

1. keep the registry concept,
2. replace current shell vocabulary with the governed target vocabulary,
3. retire ambiguous or legacy route labels such as `Operations` where they obscure business intent,
4. converge toward a route model that reflects front-office business domains rather than historical
   implementation seams.

Current gaps:

1. `Proposal` and `Advisory` are not first-class shell workspaces yet,
2. route names and shell names are partially mismatched,
3. hidden entries indicate transitional architecture rather than final product intent,
4. page structure still reflects historic slices rather than one governed product topology.

### 3. The workbench codebase already has reusable primitives, but overlap and layering are still high

Evidence:

1. `src/design-system/components/*` contains a substantial shared component layer,
2. `src/apps/portfolio/*` and `src/apps/performance/*` contain route-local and module-local
   structures,
3. `src/features/workbench/*` still contains a separate legacy-oriented feature area.

Assessment:

1. keep the shared design-system investment,
2. keep the route-level module posture in `src/apps/*`,
3. replace overlapping page-local and feature-local presentation layers with clearer ownership,
4. retire transitional components once route-local modules are stabilized.

Current gaps:

1. multiple component families overlap in responsibility,
2. there is still visible legacy naming around `workbench` vs domain-specific route modules,
3. design-system and page-module boundaries are not yet strict enough for long-term micro-frontend
   growth,
4. page-local composition debt still exists.

### 4. `lotus-gateway` already acts as a BFF, but not yet as a full experience-composition layer

Evidence:

1. `src/app/main.py` shows clear router separation and enterprise middleware,
2. `src/app/routers/workbench.py` exposes split performance and risk routes plus legacy compatibility,
3. `src/app/services/workbench_service.py` still performs multi-service orchestration inside a
   service named around `workbench`,
4. `src/app/services/async_ttl_cache.py` provides generic async TTL caching without richer
   freshness/invalidation governance.

Assessment:

1. keep gateway-first UI composition,
2. keep router/service/contract separation,
3. replace route naming and service naming that are still anchored to historical UI seams,
4. evolve gateway toward workspace bootstrap and composition ownership rather than only endpoint
   pass-through plus aggregation.

Current gaps:

1. no explicit shell bootstrap contract,
2. no governed workspace-entry contract model for all target domains,
3. caching exists but is too primitive for workflow-bearing freshness rules,
4. observability and composition metadata are not yet expressed as part of the future shell model,
5. legacy monolithic compatibility paths still exist.

### 5. Capability-contract thinking is present and should be preserved

Evidence:

1. `docs/architecture/workbench-ui-gateway-capability-contract.md` already defines:
   - `supported`
   - `partial`
   - `unavailable`
   - `hidden`
2. the document already records keep-or-retire decisions and live gateway-backed usage.

Assessment:

1. keep the capability-state vocabulary,
2. keep explicit supportability and partial-state handling,
3. extend this model to all new UI surfaces created under RFC-0081,
4. do not regress to implicit `if data exists` rendering logic.

### 6. Automation is strong for current canonical runtime validation, but not yet broad enough for the uplift

Evidence:

1. `lotus-workbench/scripts/live/*` provides governed browser/runtime validation,
2. automation is currently optimized around existing front-office routes and panels,
3. RFC-0081 introduces many new surfaces:
   - proposal workspace,
   - proposal detail,
   - artifact preview,
   - approval and consent,
   - advisory lifecycle,
   - AI search and assist surfaces.

Assessment:

1. keep the governed runtime validation path,
2. replace legacy fixed-surface assumptions with an extensible surface inventory,
3. require every new route/panel/workflow surface to be automation-addressable.

### 7. The current state is strong enough to avoid a rewrite, but not strong enough to avoid a governed program

The repos already contain useful foundations:

1. persistent app shell,
2. growing design-system layer,
3. route-level app modules,
4. gateway-first composition,
5. capability-state thinking,
6. canonical runtime validation.

But they do not yet add up to a final enterprise-grade front-office product platform.

The uplift should therefore be an evolutionary architecture program, not a greenfield rewrite and
not a cosmetic pass.

## Keep / replace / retire decisions

### Keep

1. `lotus-workbench` as the front-office shell host,
2. gateway-first composition through `lotus-gateway`,
3. route-level app modules in `src/apps/*`,
4. the design-system investment in `src/design-system/*`,
5. capability-state vocabulary and partial-state truthfulness,
6. canonical runtime validation and screenshot evidence posture.

### Replace

1. current shell navigation vocabulary and hidden transitional app model,
2. legacy `workbench`-centric naming where business-domain naming should be primary,
3. page-local or feature-local duplication where shared primitives should own the pattern,
4. thin TTL caching assumptions with a governed freshness and invalidation model,
5. compatibility-driven gateway seams where richer workspace bootstrap contracts are needed.

### Retire

1. obsolete hidden shell routes and labels once governed replacements exist,
2. legacy monolithic performance compatibility paths after external dependency verification,
3. duplicate page-local composition layers displaced by shared shell and module primitives,
4. stale navigation, layout, and style fragments that conflict with the target shell model.

## Target model confirmed by slice 1

Slice 1 confirms that RFC-0081 should implement toward this target:

1. one governed `lotus-workbench` shell,
2. one governed `lotus-gateway` experience-composition layer,
3. route-level workspace modules for:
   - Portfolio,
   - Performance,
   - Risk,
   - Proposal,
   - Advisory,
4. shared design-system primitives and business-domain patterns,
5. explicit workflow truth and partial-state handling,
6. governed automation for every new route, panel, drawer, and workflow surface,
7. enterprise-grade observability, caching, and usage analytics,
8. architecture that can host future AI search, AI assist, and agentic workflow modules.

## Review of slice 1

### What was improved by the review

The review tightened three points that were too implicit in the RFC alone:

1. gateway uplift is mandatory, not optional,
2. route topology and naming cleanup are core work, not cosmetic follow-up,
3. the existing repos contain enough reusable architecture that a controlled evolution is preferable
   to a rewrite.

### What was consciously not changed in slice 1

1. no code changes were made in `lotus-workbench` or `lotus-gateway`,
2. no route names were changed yet,
3. no shell UI changes were started,
4. no gateway contracts were changed yet.

This is correct for slice 1. The slice exists to prevent premature implementation without a grounded
target model.

### Follow-up implications for slice 2

Slice 2 should start from a much clearer gateway question:

1. what is the shell bootstrap contract,
2. what belongs in workspace entry contracts,
3. what must be versioned,
4. what existing endpoints become compatibility-only or retirement candidates.

## Conclusion

Slice 1 is complete.

It produced a code-grounded assessment, explicit keep/replace/retire decisions, and a defensible
target model for the next implementation slices.
