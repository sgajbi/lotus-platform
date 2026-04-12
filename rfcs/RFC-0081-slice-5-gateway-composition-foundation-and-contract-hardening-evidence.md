# RFC-0081 Slice 5: Gateway Composition Foundation and Contract Hardening Evidence

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Slice: `Slice 5: Gateway Composition Foundation and Contract Hardening`
- Date: 2026-04-12
- Status: Completed and reviewed

## Scope of the assessment

Slice 5 reviewed the current `lotus-gateway` contract posture to define the minimum governed
experience-contract model required for an enterprise-grade front-office shell.

The slice focused on:

1. shell-entry and workspace-bootstrap contract ownership,
2. supportability, freshness, evidence, and partial-state delivery,
3. versioning and rollout posture for modular UI contracts,
4. naming alignment between shell vocabulary and gateway contract vocabulary,
5. caching, revalidation, and invalidation rules for workflow-bearing and analytical surfaces.

The goal of the slice was to confirm what the current gateway gets right, what must be evolved, and
what must not be weakened when the shell and module model become more sophisticated.

## Files and surfaces reviewed

Reviewed directly in `lotus-gateway`:

1. `src/app/services/platform_capabilities_service.py`
2. `src/app/contracts/platform_capabilities.py`
3. `docs/standards/scalability-availability.md`
4. `docs/standards/durability-consistency.md`

Reviewed indirectly from prior RFC context:

1. implemented and proposed workbench and proposal contracts already referenced in RFC-0081,
2. slice 2 findings covering current gateway experience-contract drift,
3. slice 4 findings covering governed shell vocabulary and route topology.

## Current-state findings

### 1. The current gateway already has a useful composition posture, but `platform/capabilities` is too coarse to become the shell bootstrap contract

Evidence:

1. `src/app/services/platform_capabilities_service.py` already composes multiple upstream capability
   sources into one response,
2. the service exposes normalized fields for:
   - navigation,
   - workflow flags,
   - input modes,
   - module health,
   - policy diagnostics,
3. `src/app/contracts/platform_capabilities.py` formalizes those fields into a stable contract.

Assessment:

1. keep the capability aggregation pattern,
2. keep normalized module-health and workflow-flag semantics,
3. replace the assumption that `platform/capabilities` can directly become the final shell entry
   model,
4. add governed shell-bootstrap and workspace-bootstrap contract families above this coarse
   capability layer.

Current gap:

1. the current contract answers "what modules exist and are healthy" better than it answers "what
   does the shell need to render a banker-ready workspace with truthful state and freshness."

### 2. Supportability and partial-failure posture is one of the strongest gateway foundations and should be extended, not replaced

Evidence:

1. `platform_capabilities_service.py` preserves per-source errors and partial-failure behavior,
2. module health is normalized into `available`, `unavailable`, and `unknown`,
3. policy diagnostics preserve availability and warning state instead of masking missing data.

Assessment:

1. keep explicit partial-state behavior,
2. keep source-owned diagnostics and warning propagation,
3. extend the same posture to shell-bootstrap and workspace-bootstrap contracts,
4. require every workspace bootstrap to expose:
   - readiness,
   - partial state,
   - evidence posture,
   - freshness posture,
   - blocker or fallback semantics.

Current gap:

1. supportability semantics are strong at the capability layer but are not yet expressed as the
   shell's primary runtime truth for each workspace.

### 3. Workflow-bearing surfaces need stronger freshness and consistency semantics than generic analytical composition

Evidence:

1. `docs/standards/durability-consistency.md` classifies:
   - proposal create or submit or approval or consent orchestration as strong consistency,
   - analytical dashboards and read-side composition as eventual consistency,
2. the same document requires idempotency propagation and conflict visibility for critical proposal
   writes,
3. current capability composition does not carry separate freshness classes for shell, analytics,
   workflow truth, and future AI surfaces.

Assessment:

1. keep strong-consistency posture for proposal and consent workflow truth,
2. keep eventual-consistency posture for analytical read composition,
3. replace generic freshness treatment with explicit contract-level freshness classes,
4. require UI-facing bootstrap contracts to distinguish:
   - shell navigation freshness,
   - analytical summary freshness,
   - workflow truth freshness,
   - AI task or assist freshness.

Current gap:

1. without explicit freshness classes, the UI will either over-refresh everything or treat workflow
   state too casually.

### 4. Caching policy is correctly conservative, but the shell uplift needs a more explicit revalidation model

Evidence:

1. `docs/standards/scalability-availability.md` states that:
   - gateway does not own correctness-critical caches for financial calculations,
   - stale-read tolerance is limited to UI convenience views,
   - any cache addition requires TTL, invalidation owner, and stale-read behavior,
2. the current posture is strong enough to prevent unsafe financial caching,
3. RFC-0081 now requires a faster shell, modular workspaces, and future AI-assisted search and
   command surfaces.

Assessment:

1. keep the no-correctness-critical-cache rule,
2. keep invalidation ownership with the upstream domain owner,
3. replace implicit TTL-only thinking with explicit cache classes and revalidation rules,
4. require cache lifecycle rules per contract family:
   - shell bootstrap can be short-lived and aggressively revalidated,
   - analytical summary can use bounded freshness windows,
   - workflow truth must prefer authoritative reads and targeted invalidation,
   - AI search and assist results must carry provenance-aware freshness and no silent reuse of stale
     workflow state.

Current gap:

1. the current standard is directionally correct, but the shell uplift needs more operationally
   useful cache and revalidation guidance.

### 5. Naming is still technical at the contract layer and needs a shell-facing vocabulary boundary

Evidence:

1. `platform_capabilities.py` uses highly technical names such as:
   - `navigation`,
   - `workflowFlags`,
   - `inputModesBySource`,
   - `moduleHealth`,
   - `policyVersionsBySource`,
2. slice 4 locked shell business vocabulary to:
   - `Portfolio`,
   - `Performance`,
   - `Risk`,
   - `Proposal`,
   - `Advisory`,
3. `platform_capabilities_service.py` still maps navigation to transitional product labels such as:
   - `command_center`,
   - `analytics_studio`,
   - `decision_console`,
   - `reporting_hub`.

Assessment:

1. keep technical capability vocabulary behind gateway composition boundaries,
2. replace shell-facing dependency on transitional or implementation-colored labels,
3. require shell-bootstrap and workspace-bootstrap contracts to use governed business-domain names,
4. permit technical capability and policy vocabulary to remain internal to lower-level capability
   contracts.

Current gap:

1. gateway is close to the right posture, but shell-facing composition cannot continue to inherit
   transitional product names.

## Keep / replace / retire decisions

### Keep

1. multi-source capability aggregation in gateway,
2. explicit partial-failure and source-error propagation,
3. normalized module-health and workflow-flag posture,
4. strong-consistency posture for workflow-bearing proposal surfaces,
5. conservative cache ownership rules that keep financial correctness upstream.

### Replace

1. direct use of `platform/capabilities` as the shell's final bootstrap truth,
2. transitional navigation labels such as `analytics_studio` and `decision_console` at the
   shell-facing layer,
3. one-size-fits-all freshness semantics across analytics, workflow truth, and future AI surfaces,
4. purely TTL-flavored cache posture for shell-bearing and workflow-bearing contracts.

### Retire

1. the idea that coarse capability discovery alone is enough for banker-ready workspace composition,
2. shell-facing dependence on technical gateway area names,
3. any future cache design that treats workflow-truth reads as UI convenience caches,
4. rollout models that change shell bootstrap semantics without versioned contract boundaries.

## Target gateway composition model confirmed by slice 5

Slice 5 confirms the gateway contract-hardening model required for RFC-0081 implementation.

### 1. Shell entry contract family

The shell requires a governed shell-entry contract that provides:

1. active workspace inventory using governed business names,
2. shell navigation structure,
3. entity-context bootstrap data where appropriate,
4. notification and supportability summary,
5. shell-level freshness and contract version metadata,
6. feature and entitlement posture needed to safely render the shell.

This shell-entry contract should sit above technical capability aggregation and should not expose
historical workbench-era naming directly to the product shell.

### 2. Workspace bootstrap contract family

Each governed workspace requires a bootstrap contract family:

1. `Portfolio`
2. `Performance`
3. `Risk`
4. `Proposal`
5. `Advisory`

Each workspace bootstrap contract should provide:

1. workspace identity,
2. summary-first module data,
3. supportability state,
4. freshness metadata,
5. evidence posture,
6. blocking and fallback semantics,
7. route-safe module registration data where modular composition applies.

### 3. Supportability, evidence, and partial-state model

The shell and all workspaces should inherit the same truthful supportability posture:

1. `ready`,
2. `partial`,
3. `unavailable`,
4. `blocked`,
5. `review required` where workflow-bearing surfaces need explicit human action.

Each bootstrap contract should also expose:

1. data readiness,
2. evidence completeness,
3. known degradation reasons,
4. recommended fallback behavior for the UI.

### 4. Freshness and consistency model

Gateway contracts must classify freshness explicitly:

1. shell bootstrap freshness,
2. analytical summary freshness,
3. workflow-truth freshness,
4. AI-task or assist freshness.

Consistency expectations must remain:

1. strong consistency for proposal, approval, consent, and execution-handoff truth,
2. eventual consistency for read-side analytical composition,
3. explicit conflict and idempotency visibility for workflow writes.

### 5. Versioning and rollout posture

Modular UI contracts require explicit versioning and rollout discipline:

1. shell-entry and workspace-bootstrap contracts must be versioned independently from lower-level
   upstream service capability payloads,
2. rollout must preserve backward compatibility during shell migration,
3. shell-facing vocabulary changes require deliberate versioned adoption rather than silent payload
   drift,
4. contract deprecation must be documented before route and workspace retirement.

### 6. Caching, revalidation, and invalidation model

The cache and revalidation model should follow these rules:

1. gateway does not own correctness-critical financial caches,
2. shell bootstrap may use short-lived cache windows with explicit revalidation,
3. analytical summary payloads may use bounded freshness windows and visible stale-state handling,
4. workflow-truth surfaces should prefer authoritative reads and targeted invalidation over passive
   TTL reuse,
5. AI search and assist payloads must carry provenance-aware freshness and must not silently reuse
   stale workflow state,
6. every cache class must define:
   - invalidation owner,
   - stale-read tolerance,
   - revalidation trigger,
   - UI fallback behavior.

## Review of slice 5

### What was improved by the review

The review tightened several important areas:

1. it made clear that the gateway is not weak; it already has the right supportability and
   composition instincts,
2. it clarified that the missing piece is not "more capability flags" but a clearer shell-entry and
   workspace-bootstrap contract family,
3. it locked workflow-bearing freshness and consistency into the RFC instead of leaving them to
   ad hoc UI implementation,
4. it translated the cache standards into UI-relevant contract rules,
5. it established that shell-facing naming must move to governed business vocabulary even if
   lower-level capability contracts remain technical.

### What was consciously not changed in slice 5

1. no gateway code was changed yet,
2. no capability contracts were renamed yet,
3. no shell-entry or workspace-bootstrap contract files were introduced yet,
4. no cache implementation behavior was changed yet.

This is correct for slice 5. The slice exists to define the contract-hardening target model before
implementation begins changing gateway APIs and shell consumers.

### Guidance and context decision

No immediate agent skill or onboarding guidance update is required before implementation begins.

Reason:

1. this slice defines the gateway target posture, but runtime guidance should be updated only after
   the shell-entry and workspace-bootstrap contracts become real operational paths,
2. updating context now would document a contract family that does not yet exist in code.

This is a conscious no-change decision.

### Follow-up implications for slice 6

Slice 6 should proceed with these tighter assumptions:

1. portfolio, performance, and risk surfaces should be designed against governed workspace-bootstrap
   semantics rather than raw capability discovery,
2. supportability, evidence, and freshness must remain truthful and visible,
3. analytical page uplift should not introduce UI-side cache behavior that conflicts with gateway
   invalidation ownership,
4. later proposal and advisory slices must preserve stronger workflow-consistency requirements than
   analytical slices.

## Conclusion

Slice 5 is complete.

It produced a code-grounded gateway composition and contract-hardening assessment, explicit
keep/replace/retire decisions, and a defensible shell-entry, workspace-bootstrap, freshness,
versioning, and caching model for the later implementation slices.
