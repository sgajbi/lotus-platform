# RFC-0081 Slice 7: Advisory and Proposal Workspace Integration Evidence

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Slice: `Slice 7: Advisory and Proposal Workspace Integration`
- Date: 2026-04-12
- Status: Completed and reviewed

## Scope of the assessment

Slice 7 reviewed the current proposal and advisory lifecycle surfaces across `lotus-workbench`,
`lotus-gateway`, and `lotus-advise` to define what must happen for `Proposal` and `Advisory` to
become first-class shell workspaces under RFC-0081.

The slice focused on:

1. current workbench proposal and recommendation surfaces,
2. current gateway proposal contract posture,
3. lifecycle depth already implemented in `lotus-advise`,
4. workflow-truth, artifact, consent, approval, and execution-readiness requirements,
5. structural cleanup needed to avoid turning proposal work into another isolated UI island.

The goal of the slice was to confirm which parts of the advisory lifecycle are already real and
which parts are still underrepresented in the shell.

## Files and surfaces reviewed

Reviewed directly in `lotus-workbench`:

1. `src/features/proposals/components/proposal-list-view.tsx`
2. `src/features/proposals/components/proposal-detail-view.tsx`
3. `src/features/proposals/api.ts`
4. `src/features/proposals/types.ts`
5. `src/apps/recommendations/page.tsx`
6. `src/app/proposals/page.tsx`
7. `src/app/proposals/[proposalId]/page.tsx`
8. `src/app/proposals/simulate/page.tsx`
9. `src/apps/performance/components/performance-advisor-brief-mode.tsx`
10. `src/apps/performance/advisor-brief-view-model.ts`

Reviewed directly in `lotus-gateway`:

1. `src/app/contracts/proposals.py`
2. `src/app/services/proposal_service.py`
3. `src/app/routers/proposals.py`
4. `src/app/services/advisor_brief_service.py`
5. `src/app/contracts/advisor_brief.py`

Reviewed directly in `lotus-advise`:

1. `src/api/proposals/routes_lifecycle.py`
2. `src/api/proposals/routes_delivery.py`
3. `src/api/proposals/routes_async.py`
4. `src/core/proposals/service.py`
5. `src/core/advisory/artifact.py`
6. `src/core/common/workflow_gates.py`
7. lifecycle and artifact RFC/demo references under:
   - `docs/rfcs/RFC-0011-proposal-artifact.md`
   - `docs/rfcs/RFC-0012-advisory-workflow-gates.md`
   - `docs/rfcs/RFC-0013-proposal-persistence-workflow-lifecycle.md`
   - `docs/demo/19_advisory_proposal_artifact.json`
   - `docs/demo/20_advisory_proposal_persist_create.json`
   - `docs/demo/23_advisory_proposal_approval_client_consent.json`
   - `docs/demo/24_advisory_proposal_approval_compliance.json`
   - `docs/demo/25_advisory_proposal_transition_executed.json`

## Current-state findings

### 1. Workbench already has proposal entry points, but they still feel transitional rather than shell-native

Evidence:

1. `proposal-list-view.tsx` presents a workflow queue grouped by stage,
2. `proposal-detail-view.tsx` exposes workflow progress, approvals, versioning, lineage, and
   evidence metadata,
3. `apps/recommendations/page.tsx` still exists as a transitional route family,
4. proposal UI currently sits under feature-level pages rather than a fully governed shell workspace
   model.

Assessment:

1. keep the real workflow concepts already expressed in the proposal screens,
2. keep proposal queue, detail, versioning, and approval visibility,
3. replace transitional route and workspace posture with shell-native `Proposal` and `Advisory`
   workspaces,
4. avoid preserving recommendation-era naming as the long-term advisory shell model.

Current gap:

1. the workbench proposal surfaces prove useful backend-backed behavior, but they are not yet
   represented with the same product seriousness as the analytical workspaces.

### 2. Gateway already exposes proposal workflow operations, but the shell-facing contract remains too transport-oriented

Evidence:

1. `src/app/contracts/proposals.py` still wraps raw payloads as broad envelope contracts,
2. `proposal_service.py` already supports:
   - proposal create,
   - list,
   - detail,
   - version create,
   - submit,
   - risk approval,
   - compliance approval,
   - client consent,
   - workflow events,
   - approvals,
3. gateway forwards authoritative workflow behavior rather than inventing local UI state.

Assessment:

1. keep gateway ownership of proposal workflow access,
2. keep proposal lifecycle operations and idempotency-aware actions,
3. replace raw-envelope shell consumption with a richer workspace-bootstrap posture in later
   implementation,
4. require proposal and advisory shell surfaces to be backed by workflow-truth contracts rather than
   ad hoc UI stitching.

Current gap:

1. gateway is functionally rich, but shell-facing composition still needs the governed workspace
   model defined in slice 5.

### 3. `lotus-advise` already contains far more lifecycle depth than workbench currently surfaces

Evidence:

1. `routes_lifecycle.py` exposes create, list, detail, version, transition, and approval behavior,
2. `lotus-advise` has dedicated lifecycle, artifact, workflow-gate, delivery, and async routes,
3. demo and RFC artifacts already describe:
   - artifact generation,
   - workflow gates,
   - approval and consent,
   - execution transition,
4. the service and core layers show proposal persistence and lifecycle as first-class domain
   behavior rather than demo-only functionality.

Assessment:

1. keep `lotus-advise` as the authoritative lifecycle owner,
2. keep the existing lifecycle depth and workflow gate logic,
3. replace thin workbench exposure with a richer shell-native representation of the same domain
   truth,
4. make proposal and advisory UI an operating surface for real workflow, not a front-end wrapper
   around scattered lifecycle calls.

Current gap:

1. the backend lifecycle is more mature than the current UI representation.

### 4. Advisor brief is a useful bridge, but it is not a substitute for a real proposal workspace

Evidence:

1. `performance-advisor-brief-mode.tsx` and `advisor-brief-view-model.ts` surface supportability,
   synopsis, evidence, and talking points,
2. the advisor brief already carries a banker-oriented narrative layer,
3. the advisor brief currently lives inside the performance workspace rather than as part of a
   first-class advisory operating model.

Assessment:

1. keep the advisor brief as a valuable supporting surface,
2. replace any assumption that advisor brief alone equals advisory workspace coverage,
3. position advisor brief as one module or bridge into the broader `Advisory` and `Proposal`
   workspaces,
4. avoid forcing proposal lifecycle UX to stay embedded inside analytical modes.

Current gap:

1. banker narrative exists, but the workflow workspace around it is still underdeveloped in the
   shell.

### 5. Proposal and advisory UX must inherit the same structural quality rules as analytical surfaces

Evidence:

1. current proposal detail already includes:
   - workflow progress,
   - action availability,
   - version management,
   - lineage explorer,
   - evidence and auditability,
   - workflow timeline,
   - approvals,
2. current list and detail views are useful but still more utilitarian than the target product
   references require,
3. RFC-0081 target screens already call for:
   - workflow rails,
   - before or after context,
   - artifact preview,
   - approval pack,
   - client consent,
   - execution handoff.

Assessment:

1. keep the real workflow-bearing content already present,
2. replace the current utilitarian presentation with shell-native, banker-grade workspace
   structures,
3. require proposal and advisory surfaces to inherit:
   - summary first,
   - decision rails,
   - truthful supportability,
   - drill-down behavior,
   - explicit blockers and next actions,
4. ensure artifact preview and client-consent surfaces are first-class rather than buried under
   generic detail pages.

Current gap:

1. the content exists, but the product grammar is not yet at the same level as the target shell.

## Keep / replace / retire decisions

### Keep

1. gateway-backed proposal lifecycle access,
2. `lotus-advise` ownership of workflow truth, persistence, gates, and artifacts,
3. proposal queue, detail, version, approval, and evidence concepts already present in workbench,
4. advisor brief as a bridge between analytics and advisory decision-making,
5. idempotent and state-aware workflow operations.

### Replace

1. recommendation-era route and page posture as the long-term advisory surface,
2. thin proposal pages that are not yet integrated into the governed shell workspace model,
3. shell consumption of proposal data as broad envelopes without richer workspace composition,
4. the assumption that advisory capability can remain split between isolated pages and analytical
   modes.

### Retire

1. long-term dependence on `recommendations` as the product vocabulary,
2. proposal screens that look like utility pages instead of banker workspaces,
3. fragmented approval, consent, artifact, and execution-ready semantics scattered across unrelated
   pages,
4. any UI treatment that renders proposal lifecycle state without backend-backed workflow truth.

## Target proposal and advisory workspace model confirmed by slice 7

Slice 7 confirms the proposal and advisory posture required for RFC-0081 implementation.

### 1. Proposal workspace model

The `Proposal` workspace should become the primary banker workspace for:

1. proposal queue and stage management,
2. proposal context and intent ladder,
3. before or after allocation and risk posture,
4. workflow gates and blockers,
5. artifact preview and delivery actions,
6. consent and execution-handoff readiness.

### 2. Advisory workspace model

The `Advisory` workspace should become the broader relationship-facing operating surface for:

1. advisory objective context,
2. rationale and talking points,
3. suitability and supportability synthesis,
4. next-best proposal and review actions,
5. bridge surfaces from analytics into proposal creation and refinement.

The advisor brief should remain a supporting module, not the full advisory workspace.

### 3. Workflow-truth model

All proposal and advisory pages must remain backed by authoritative workflow truth for:

1. draft,
2. review submission,
3. risk review,
4. compliance review,
5. client consent,
6. execution readiness,
7. execution handoff,
8. version and lineage state,
9. artifact readiness and evidence posture.

### 4. Artifact and consent model

Proposal artifact and client-consent behavior should be first-class product surfaces:

1. artifact preview should be a real workspace view,
2. included sections and artifact identity should be explicit,
3. consent state should be visible and actionable,
4. audit and evidence metadata should remain accessible,
5. execution should remain visibly blocked until the authoritative lifecycle clears it.

### 5. Structural cleanup model

Later implementation should:

1. converge `recommendations` and proposal-era route drift into governed `Proposal` and `Advisory`
   surfaces,
2. prevent proposal UI from accreting into another set of large page-local files,
3. reuse the strongest existing shell, rail, drawer, and supportability patterns,
4. keep backend lifecycle ownership in `lotus-advise` and gateway composition ownership in
   `lotus-gateway`,
5. avoid duplicating lifecycle logic in the frontend.

## Review of slice 7

### What was improved by the review

The review tightened several important points:

1. it made explicit that proposal and advisory work are not greenfield problems; the lifecycle depth
   already exists in `lotus-advise`,
2. it clarified that the main deficit is shell-native product representation rather than backend
   workflow capability,
3. it confirmed that advisor brief is useful but insufficient as the full advisory operating model,
4. it locked artifact, approval, consent, and execution handoff into the target shell model rather
   than leaving them as optional later enhancements,
5. it reduced the risk that implementation would preserve recommendation-era topology by inertia.

### What was consciously not changed in slice 7

1. no `lotus-workbench` proposal or advisory code was changed yet,
2. no `lotus-gateway` proposal contracts were changed yet,
3. no `lotus-advise` lifecycle routes were changed yet,
4. no proposal or advisory route consolidation has happened yet,
5. no panel registry or runtime guidance was updated yet.

This is correct for slice 7. The slice exists to define the target workspace and ownership model
before implementation begins changing routes, shell navigation, and gateway composition.

### Guidance and context decision

No immediate context or skill update is required before implementation begins.

Reason:

1. the target proposal and advisory workspace model is now clear, but operational guidance should be
   updated only after the shell and route model actually adopt those workspaces,
2. updating context now would over-document a target operating model that is not yet live.

This is a conscious no-change decision.

### Follow-up implications for slice 8

Slice 8 should proceed with these tighter assumptions:

1. micro-frontend boundaries must support proposal and advisory modules as first-class shell
   citizens,
2. module registration and shell composition rules must be strong enough to host workflow-bearing
   pages without duplicating lifecycle logic,
3. the future module model must preserve stronger contract and audit posture for proposal surfaces
   than for purely analytical read-only modules.

## Conclusion

Slice 7 is complete.

It produced a code-grounded advisory and proposal integration assessment, explicit
keep/replace/retire decisions, and a defensible workspace and ownership model for bringing the full
`lotus-advise` lifecycle into the governed front-office shell.
