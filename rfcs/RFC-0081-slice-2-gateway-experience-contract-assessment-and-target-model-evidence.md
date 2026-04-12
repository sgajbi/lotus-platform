# RFC-0081 Slice 2: Gateway Experience-Contract Assessment and Target Model Evidence

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Slice: `Slice 2: Gateway Experience-Contract Assessment and Target Model`
- Date: 2026-04-12
- Status: Completed and reviewed

## Scope of the assessment

Slice 2 reviewed whether `lotus-gateway` is already capable of serving as the experience-composition
layer required by RFC-0081.

The assessment focused on:

1. shell bootstrap readiness,
2. workspace bootstrap and route topology,
3. workflow-bearing proposal and advisory surfaces,
4. evidence, supportability, and freshness delivery,
5. caching and composition posture,
6. current gateway architecture that should be retained, replaced, or retired.

The goal of the slice was to define the target gateway experience-contract model before code changes
begin in later slices.

## Files and surfaces reviewed

Reviewed directly in `lotus-gateway`:

1. `src/app/routers/workbench.py`
2. `src/app/routers/portfolio.py`
3. `src/app/routers/proposals.py`
4. `src/app/routers/platform.py`
5. `src/app/services/workbench_service.py`
6. `src/app/services/async_ttl_cache.py`
7. `docs/documentation/experience-api-foundation-blueprint.md`
8. gateway RFC inventory and standards references under:
   - `docs/rfcs/*`
   - `docs/standards/*`

Reviewed indirectly through repository inventory:

1. router topology under `src/app/routers/*`
2. service references for supportability, workspace, and cache semantics

## Current-state findings

### 1. Gateway intent is already correct, but the active runtime surface is still fragmented

Evidence:

1. `docs/documentation/experience-api-foundation-blueprint.md` already states the right long-term
   direction:
   - workspace-oriented contracts,
   - shared response-envelope and partial-failure patterns,
   - product-area orchestration modules,
   - supportability and evidence access for product surfaces
2. router topology is organized by product area:
   - `foundation.py`
   - `portfolio.py`
   - `proposals.py`
   - `reporting.py`
   - `workbench.py`

Assessment:

1. keep the gateway-as-experience-API direction,
2. keep product-area routing,
3. replace historical runtime fragmentation where shell composition is split across route families
   without one governed shell/bootstrap model.

Current gap:

1. the architecture document is ahead of the runtime contract model,
2. there is still no single shell bootstrap payload for the enterprise front-office shell.

### 2. Existing workspace contracts prove the gateway can shape product-facing responses

Evidence:

1. `src/app/routers/portfolio.py` already exposes workspace-oriented routes such as:
   - `/portfolios/{portfolio_id}/workspace`
   - `/readiness`
   - `/insights`
   - `/workflow`
   - `/book`
   - `/allocations`
   - `/positions`
   - `/performance-snapshot`
2. `src/app/routers/workbench.py` already exposes split contracts for:
   - performance summary,
   - performance details,
   - horizon comparison,
   - attribution trend,
   - risk summary,
   - concentration,
   - drawdown,
   - rolling,
   - attribution
3. `src/app/routers/proposals.py` already exposes workflow-bearing proposal routes.

Assessment:

1. keep workspace-oriented contract shaping,
2. keep split contracts for first paint vs heavier detail where the domain justifies it,
3. replace inconsistent shell-entry semantics and historically named route families that still make
   UI composition depend on route-by-route knowledge.

Current gap:

1. gateway has many useful workspace fragments but no explicit workspace bootstrap family that the
   shell can rely on uniformly.

### 3. Proposal workflow truth exists, but proposal surfaces are still API-family oriented rather than shell-oriented

Evidence:

1. `src/app/routers/proposals.py` already supports:
   - proposal creation,
   - proposal versioning,
   - submit,
   - approvals,
   - client consent,
   - workflow events
2. this is enough to show that the gateway already owns key proposal lifecycle seams.

Assessment:

1. keep proposal lifecycle APIs,
2. keep gateway ownership of workflow-bearing proposal actions,
3. replace purely endpoint-centric proposal composition with shell-facing proposal workspace and
   proposal detail bootstrap contracts.

Current gap:

1. the future `Proposal` and `Advisory` shell workspaces should not have to independently assemble
   lifecycle cards, timeline rails, artifact readiness, and approval posture from many unrelated
   endpoints.

### 4. Platform capability aggregation is useful but too coarse to be the shell bootstrap model

Evidence:

1. `src/app/routers/platform.py` exposes `GET /api/v1/platform/capabilities`,
2. the existing contract is good for cross-service readiness and feature negotiation,
3. the platform capability pattern is already referenced by implemented gateway RFCs.

Assessment:

1. keep platform capability aggregation,
2. keep it as a coarse feature and readiness source,
3. do not treat it as the final shell bootstrap contract.

Current gap:

1. shell bootstrap needs more than service capability flags:
   - workspace registration,
   - route identity,
   - entitlement visibility,
   - default entity context,
   - observability metadata,
   - freshness posture,
   - AI-assist entry capability.

### 5. Runtime composition is still too dependent on router-local service assembly and historical naming

Evidence:

1. `src/app/routers/workbench.py` constructs multiple services in one router module,
2. `src/app/routers/portfolio.py` rebuilds `WorkbenchService` and
   `PerformanceWorkspaceService` locally,
3. `src/app/services/workbench_service.py` still acts as a historically named orchestration
   surface spanning portfolio, snapshot, analytics, sandbox, and policy feedback concerns.

Assessment:

1. keep router/service/client separation,
2. replace duplicated router-local service construction,
3. replace historical `workbench` service naming with domain- or composition-oriented ownership as
   later implementation slices proceed.

Current gap:

1. without a clearer composition layer, future shell bootstrap, proposal workspace composition, AI
   search bootstrap, and module registration will create more duplication instead of less.

### 6. Supportability and partial-state posture is a strength that should be extended

Evidence:

1. `workbench.py` and risk/performance contracts already shape partial and compatibility states,
2. gateway documentation explicitly calls out supportability and evidence access,
3. implemented RFCs in `docs/rfcs/*` already frame gateway responsibilities around UI experience
   rather than pure upstream parity.

Assessment:

1. keep partial-failure and supportability patterns,
2. extend them into shell bootstrap and workspace bootstrap contracts,
3. require supportability, evidence posture, and freshness metadata to be first-class in future
   shell-facing contracts.

Current gap:

1. supportability is still uneven across route families,
2. shell-level composition metadata is not yet standardized.

### 7. Current cache posture is useful for latency, but not yet governed enough for workflow-bearing UI

Evidence:

1. `src/app/services/async_ttl_cache.py` provides basic TTL caching with in-flight de-duplication,
2. config already defines route-specific TTLs for:
   - portfolio upstream data,
   - advisor brief,
   - risk BFF
3. gateway standards already state that cache additions require explicit TTL, invalidation owner,
   and stale-read behavior.

Assessment:

1. keep lightweight async caching as an implementation primitive,
2. replace ad hoc TTL-only cache posture with a governed freshness model for shell and workflow
   contracts,
3. do not allow caching to obscure approval state, consent state, execution readiness, or AI task
   status.

Current gap:

1. gateway does not yet expose cache/freshness semantics in a way the future shell can use
   consistently,
2. there is no shared distinction between:
   - shell bootstrap freshness,
   - analytical workspace freshness,
   - workflow truth freshness,
   - AI task freshness.

## Keep / replace / retire decisions

### Keep

1. gateway-first experience composition,
2. product-area routers,
3. platform capability aggregation,
4. workspace-oriented route families already present in portfolio and workbench,
5. proposal workflow action ownership in gateway,
6. partial-failure and supportability posture,
7. lightweight async cache primitive as a building block.

### Replace

1. router-local service assembly duplication,
2. shell composition that depends on route-by-route frontend knowledge,
3. historically named orchestration surfaces such as `WorkbenchService` as the main long-term
   composition seam,
4. TTL-only cache thinking for workflow-bearing UI state,
5. compatibility-driven monolithic endpoint posture where split contracts are already the cleaner
   active model.

### Retire

1. deprecated monolithic performance workspace compatibility route once downstream migration is
   complete,
2. route naming and runtime coupling that force the shell to understand implementation-era seams
   rather than business workspaces,
3. duplicated composition patterns in routers once a governed shell/workspace bootstrap layer is in
   place.

## Target gateway experience-contract model confirmed by slice 2

Slice 2 confirms that RFC-0081 should implement toward this target gateway contract family.

### 1. Shell bootstrap contract

Gateway should expose one shell bootstrap contract that gives the frontend:

1. workspace registry,
2. workspace visibility and entitlement state,
3. route identity and default route targets,
4. shell-wide capability posture,
5. command/search capability registration,
6. notification and assist-entry availability,
7. freshness and composition metadata needed for observability.

This contract should be shell-oriented, not service-oriented.

### 2. Workspace bootstrap contracts

Each top-level workspace should have a governed bootstrap contract:

1. `Portfolio`
2. `Performance`
3. `Risk`
4. `Proposal`
5. `Advisory`

Each workspace bootstrap should provide:

1. entity context,
2. summary rail or KPI context,
3. workflow posture where relevant,
4. supportability and freshness posture,
5. child-module registration where the page uses modular composition,
6. links to detail contracts for drill-down.

### 3. Workflow-truth contracts

Workflow-bearing surfaces should use explicit contracts for:

1. proposal lifecycle,
2. approvals,
3. consent,
4. execution readiness,
5. AI review state where later slices introduce AI-assisted surfaces.

These contracts should carry authoritative state, blockers, next actions, and freshness posture.

### 4. Evidence and supportability metadata

All shell-facing and workflow-bearing contracts should converge on explicit metadata for:

1. supportability state,
2. evidence availability,
3. freshness posture,
4. partial-state reason,
5. upstream provenance,
6. audit/correlation identity.

### 5. Cache and freshness model

Gateway should distinguish at least four freshness classes:

1. shell bootstrap and navigation metadata,
2. analytical summary/detail data,
3. workflow-bearing proposal and approval truth,
4. AI-assisted task or search result state.

These classes need different cache and invalidation rules.

## Review of slice 2

### What was improved by the review

The review tightened several points that were too easy to leave vague:

1. platform capabilities are useful, but they are not the shell bootstrap model,
2. proposal lifecycle routes prove gateway can own workflow truth, but the UI still needs
   workspace-facing bootstrap contracts,
3. caching cannot remain TTL-only once workflow truth and AI-assisted surfaces become first-class,
4. router-local service construction is already a maintainability smell that later slices should
   remove rather than normalize.

### What was consciously not changed in slice 2

1. no gateway code was changed yet,
2. no router names were changed yet,
3. no gateway doc was edited in `lotus-gateway` during this slice,
4. no gateway contracts were added yet.

This is correct for slice 2. The slice exists to define the required gateway target model before
shell and contract implementation starts.

### Guidance and cross-link decision

No immediate gateway guidance change is required before implementation begins.

Reason:

1. `docs/documentation/experience-api-foundation-blueprint.md` already points in the correct
   direction,
2. the main problem is runtime implementation drift rather than missing conceptual guidance,
3. targeted gateway documentation updates should land when slice 5 changes the actual contract and
   composition model.

This is a conscious no-change decision, not an omission.

### Follow-up implications for slice 3

Slice 3 should now proceed with a tighter shell assumption:

1. the UI shell must be designed to consume one governed shell bootstrap contract,
2. workspace navigation and entity context should not depend on hardcoded route families,
3. shell-level assist, search, telemetry, and freshness behavior must align to the future gateway
   model from the start.

## Conclusion

Slice 2 is complete.

It produced a code-grounded gateway assessment, explicit keep/replace/retire decisions, and a
defensible target experience-contract model for later shell and gateway implementation slices.
