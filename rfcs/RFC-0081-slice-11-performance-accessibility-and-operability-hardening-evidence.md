# RFC-0081 Slice 11: Performance, Accessibility, and Operability Hardening Evidence

## Scope of this slice

Slice 11 reviewed the non-visual hardening posture required for RFC-0081.

The review covered:

1. shell and route performance posture,
2. cache and revalidation behavior,
3. accessibility and keyboard posture,
4. telemetry, logging, tracing, and audit posture,
5. automation coverage for current and future screens,
6. stale implementation patterns that would undermine enterprise-grade operation.

## Current-state findings

### Workbench already has some performance discipline, but it is still too coarse

`lotus-workbench/src/features/platform-runtime/query-policy.ts` defines shared query defaults.

That is useful because it centralizes one baseline.

It is not yet sufficient because:

1. all query classes are effectively treated with one stale-time posture,
2. workflow-bearing state, analytical state, and shell bootstrap state are not yet differentiated,
3. many components still use page-local caches in refs rather than one governed freshness model,
4. first-paint and deep-detail loading are partially governed but not yet budgeted consistently.

### Styling and shared layout still carry operational drag

`lotus-workbench/src/app/globals.css` remains very large and still owns too many shared concerns.

That is an operability issue, not just a cleanliness issue, because:

1. shared behavior is harder to reason about,
2. shell and page-local styling remain too interleaved,
3. accessibility and interaction regressions become harder to detect,
4. future module expansion will otherwise compound CSS drift.

### Gateway already provides strong audit posture

`lotus-gateway/src/app/enterprise_readiness.py` shows that write-path authorization and audit
middleware already exist.

That is the correct enterprise posture for UI-bearing workflow systems.

RFC-0081 should build on that by requiring:

1. shell and workflow telemetry to align with backend audit truth,
2. UI usage analytics to remain subordinate to operational governance,
3. workflow-sensitive front-office actions to preserve correlation and audit continuity.

### Canonical QA automation is already a strong base

`lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1` and
`lotus-workbench/scripts/live/validate-canonical-workbench-live.mjs` already provide a meaningful
governed validation path.

That is valuable because:

1. browser validation is tied to real gateway contracts,
2. screenshots are governed by runtime evidence,
3. panel-level validation already exists for key portfolio, performance, risk, and advisor-brief
   surfaces.

The remaining gap is extension coverage:

1. future proposal, advisory, search, and AI screens must be added as first-class validated panels,
2. automation must validate more than “page renders”; it must validate supportability, provenance,
   and truthful degraded states.

## Keep / replace / retire decisions

### Keep

1. shared query-policy baseline,
2. summary-first and deferred-detail loading posture in workbench,
3. gateway audit middleware and correlation continuity,
4. canonical front-office QA wrapper in `lotus-platform`,
5. modular browser-validation structure from RFC-0078.

### Replace

1. one-size-fits-all freshness defaults with differentiated cache classes,
2. page-local cache maps as the long-term primary state strategy,
3. CSS-heavy shared behavior in one global file,
4. implicit accessibility posture with explicit keyboard and focus standards,
5. panel validation that stops at current analytical surfaces once proposal, advisory, and AI
   modules land.

### Retire

1. any future shell module that ships without automation coverage,
2. any route-local cache logic that conflicts with governed freshness classes,
3. any shared style expansion that keeps pushing shell and module behavior back into monolithic
   global CSS,
4. any workflow-bearing screen that emits no usage or operational telemetry,
5. any AI or proposal workflow surface that bypasses audit, trace, or correlation continuity.

## Target operability model confirmed by slice 11

### 1. Performance-budget model

RFC-0081 implementation should define explicit budgets for:

1. shell bootstrap,
2. first workspace paint,
3. route transition latency,
4. deferred analytical detail load,
5. search and command invocation latency,
6. workflow action feedback latency.

The shell should optimize for:

1. summary first,
2. detail on demand,
3. predictable route transitions,
4. limited first-paint payloads,
5. contract-aware progressive loading.

### 2. Freshness and caching model

The shell needs differentiated cache classes rather than a single TTL posture.

The model should distinguish:

1. shell bootstrap and navigation metadata,
2. analytical summary data,
3. analytical detail data,
4. workflow truth and approval state,
5. AI assist and search results,
6. supportability and readiness diagnostics.

Each class should define:

1. default freshness window,
2. revalidation trigger,
3. invalidation trigger,
4. stale-while-revalidate acceptability,
5. whether cached values are permitted across entity changes.

Workflow-bearing and consent-bearing state should be much stricter than analytical history.

### 3. Accessibility and keyboard-ergonomics model

RFC-0081 should treat accessibility as part of enterprise front-office speed and trust.

The target model should require:

1. keyboard-operable shell navigation,
2. predictable focus movement across headers, tabs, rails, drawers, and tables,
3. visible focus states for all interactive primitives,
4. semantic headings and landmarks across workspaces,
5. accessible table and chart summaries where visual density is high,
6. drawer and panel behavior that preserves orientation for keyboard users.

### 4. Observability and usage model

The shell should emit enough telemetry to understand:

1. which workspaces are used most by front office,
2. where users abandon or stall in workflows,
3. which modules most often degrade to partial or unavailable,
4. which AI assists are used, rejected, or revised,
5. which command and search entries are actually adopted.

This should include:

1. structured frontend event logging,
2. correlation IDs carried to gateway-backed actions,
3. route and workflow timing,
4. error and degraded-state counts,
5. bounded usage analytics aligned to enterprise governance.

### 5. Logging, tracing, and audit-continuity model

Frontend interaction should not invent a parallel observability system.

The target model should align frontend traces and events with:

1. gateway audit events,
2. correlation middleware,
3. workflow action identity,
4. AI audit and retrieval posture where applicable.

This is required so operators can trace:

1. user action,
2. shell event,
3. gateway call,
4. workflow change,
5. AI assist or retrieval event,
6. final outcome.

### 6. Automation-coverage model

RFC-0081 implementation should require governed automation coverage for all net-new supported
front-office surfaces.

Coverage should include:

1. portfolio, performance, and risk screens,
2. proposal workspace and proposal detail,
3. artifact preview and consent surfaces,
4. advisory workflow surfaces,
5. AI-bearing surfaces with provenance,
6. shell search and command surfaces once supported.

Automation should validate:

1. ready states,
2. partial states,
3. unavailable states,
4. supportability alignment,
5. evidence and provenance visibility where applicable,
6. screenshot truthfulness.

## Structural implications for implementation

Slice 11 confirms that implementation should:

1. move shared shell and module behavior out of monolithic `globals.css`,
2. introduce governed freshness classes instead of expanding ad hoc local caches,
3. add shell-level instrumentation and route metrics deliberately,
4. extend the canonical validator rather than building separate test harnesses,
5. treat accessibility and keyboard posture as acceptance criteria, not polish.

## Dead code and weak-pattern review

No slice-11-specific dead code was removed in `lotus-platform`, because this slice is governance and
assessment evidence.

The assessment did confirm weak patterns that later implementation should remove:

1. continued growth of monolithic global CSS for shell and module concerns,
2. page-local cache maps as a long-term replacement for governed state policy,
3. implicit keyboard/accessibility behavior without shared testable standards,
4. supported UI modules that are absent from the governed screenshot and browser-validation path.

## Skills, context, and documentation review

No immediate skill or onboarding guidance update is required before implementation begins.

That is a conscious decision for this slice because:

1. the current governed runtime path is still correct,
2. the validator and runtime docs already point to the right execution path,
3. the correct documentation change should happen when new proposal, advisory, search, and AI
   surfaces are actually wired into automation.

What must be reviewed later:

1. whether `lotus-front-office-runtime` should enumerate new validation classes beyond current
   portfolio, performance, and risk screens,
2. whether agent guidance should describe differentiated cache classes and workflow freshness rules,
3. whether automation docs should explicitly call out shell search, proposal, and AI provenance
   coverage once those surfaces are implemented.

## Review of slice 11

Slice 11 is complete.

The strongest conclusion is that Lotus already has a good validation spine and meaningful gateway
audit posture.

The real gaps are:

1. differentiated cache and freshness policy,
2. explicit performance and accessibility budgets,
3. shell-level usage telemetry,
4. guaranteed automation coverage for every new front-office surface,
5. retirement of monolithic styling and route-local cache drift.

Slice 11 is complete.
