# RFC-0081 Slice 8: Micro-Frontend Composition and Extension Model Evidence

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Slice: `Slice 8: Micro-Frontend Composition and Extension Model`
- Date: 2026-04-12
- Status: Completed and reviewed

## Scope of the assessment

Slice 8 reviewed the current shell, route, and shared-frontend composition model in
`lotus-workbench` to define the module-boundary and extension rules required for RFC-0081.

The slice focused on:

1. shell registry and navigation ownership,
2. route topology versus app-module topology,
3. shared dependency and platform-runtime boundaries,
4. design-system naming and ownership that affect modular composition,
5. cleanup and retirement rules for legacy route and module patterns,
6. expectations for incorporating new panels and module routes into governed automation later.

The goal of the slice was to make the future micro-frontend model concrete enough that
`Portfolio`, `Performance`, `Risk`, `Proposal`, and `Advisory` can evolve as first-class shell
modules without fragmenting the product.

## Files and surfaces reviewed

Reviewed directly in `lotus-workbench`:

1. `src/shell/app-registry.ts`
2. `src/shell/app-shell.tsx`
3. `src/shell/app-switcher-nav.tsx`
4. `src/shell/workspace-capabilities.ts`
5. route inventory under `src/app/*`
6. app-module inventory under `src/apps/*`
7. `src/design-system/index.ts`
8. `src/design-system/components/workspace-layout.tsx`
9. `src/features/platform-runtime/query-policy.ts`
10. `src/features/platform-runtime/service-addressing.ts`

Observed topology:

1. `src/app` currently includes transitional route families such as:
   - `intake`
   - `portfolios`
   - `recommendations`
   - `suite`
   - `workbench`
2. `src/apps` currently includes:
   - `home`
   - `performance`
   - `portfolio`
   - `recommendations`
3. the shell registry still exposes transitional labels and capability keys such as:
   - `Overview`
   - `Relationship Book`
   - `Operations`
   - `command_center`
   - `analytics_studio`
   - `decision_console`

## Current-state findings

### 1. Workbench already has route-to-module delegation, but module registration is not yet governed strongly enough

Evidence:

1. `src/app` and `src/apps` already separate route handling from some module ownership,
2. `portfolio-experience-page.tsx` and `performance-analytics-page.tsx` show a clean route-to-app
   delegation pattern,
3. `src/shell/app-registry.ts` still hardcodes the shell app inventory in a transitional shape.

Assessment:

1. keep route-to-module delegation where it is already clean,
2. keep a central registry for shell-managed workspace visibility,
3. replace transitional registry vocabulary and weak ownership semantics,
4. require module registration to be governed by business workspace identity rather than historical
   shell labels.

Current gap:

1. the shell has a registry, but not yet a clear long-term contract for how modules register,
   declare readiness, and participate in shared shell behavior.

### 2. The shell itself is too thin to be the only composition boundary, and too transitional to be the long-term shell vocabulary owner

Evidence:

1. `src/shell/app-shell.tsx` is intentionally small and useful, but only provides:
   - brand,
   - nav,
   - shell body,
2. `app-switcher-nav.tsx` still reads fallback capability navigation directly and exposes
   transitional shell naming,
3. `workspace-capabilities.ts` provides good supportability primitives but does not yet define
   module-registration or shell-composition contracts.

Assessment:

1. keep the shell thin enough to remain stable,
2. keep supportability-state primitives,
3. replace the idea that the current shell files alone define the future module system,
4. require a clearer separation between:
   - shell chrome,
   - shell registry,
   - shell-to-module composition contracts,
   - workspace supportability contracts,
   - shared runtime dependencies.

Current gap:

1. shell composition is happening, but the architectural ownership lines are still too implicit.

### 3. Shared design-system naming still exposes historical `Workbench` and `Workstation` vocabulary that will make modular ownership harder to reason about

Evidence:

1. `src/design-system/index.ts` exports a mix of:
   - `AppPageShell`
   - `WorkbenchPageFrame`
   - `WorkspaceLayout`
   - `WorkstationPage`
   - `WorkstationShell`
2. `workspace-layout.tsx` still encodes `Workstation` naming at a shared-layout layer,
3. slice 4 already established that shared naming should indicate:
   - shell,
   - layout,
   - workspace,
   - module,
   - domain.

Assessment:

1. keep the shared primitives and layout intent,
2. replace mixed historical naming with clearer ownership-aligned names over time,
3. avoid designing the module system on top of ambiguous `workbench` versus `workstation` naming,
4. treat naming cleanup as part of micro-frontend clarity, not only design polish.

Current gap:

1. shared primitives are usable, but their naming still blurs the layer boundaries that a modular
   shell needs.

### 4. Platform-runtime boundaries exist, but they are too small and too implicit for a future shell with many modules

Evidence:

1. `src/features/platform-runtime` currently contains:
   - `query-policy.ts`
   - `service-addressing.ts`
2. `app-switcher-nav.tsx` consumes fallback platform capabilities directly,
3. performance and proposal features still rely on feature-local data wiring rather than a more
   governed shell-runtime contract family.

Assessment:

1. keep a shared platform-runtime layer,
2. replace ad hoc or feature-local shell dependency wiring with a more explicit runtime boundary,
3. require the future module model to depend on:
   - gateway-backed shell bootstrap,
   - shared query policy,
   - shared service addressing,
   - shared entitlement and supportability semantics,
   - shared observability hooks.

Current gap:

1. the runtime foundation exists, but it is not yet broad or explicit enough to host many governed
   shell modules cleanly.

### 5. Legacy routes and app families will create drift unless the retirement rules are explicit

Evidence:

1. route families such as `suite`, `workbench`, `intake`, and `recommendations` still exist,
2. app families still include `home` and `recommendations`,
3. slice 7 confirmed that recommendation-era posture is not the long-term advisory model.

Assessment:

1. keep compatibility routes only where they are needed for migration,
2. replace legacy route and app families with governed shell workspace registration once the target
   modules are ready,
3. require every replacement to include an explicit retirement path,
4. define cleanup as part of the module program, not as an afterthought.

Current gap:

1. the route tree still reveals too much historical migration state, and that will undermine a
   future micro-frontend story if it remains indefinite.

## Keep / replace / retire decisions

### Keep

1. route-to-module delegation where it already exists,
2. central shell registry concept,
3. shared platform-runtime layer,
4. workspace supportability primitives,
5. shared design-system and shell primitives as the foundation for module reuse.

### Replace

1. transitional shell registry vocabulary and capability-key dependence,
2. weakly defined module-registration posture,
3. mixed historical shared-layout naming,
4. feature-local shell dependency wiring that should become part of a governed runtime contract,
5. indefinite coexistence of migration-era route families alongside governed shell workspaces.

### Retire

1. long-term shell labels such as `Overview` and `Operations`,
2. recommendation-era topology as a future advisory module model,
3. workbench-era or workstation-era names at shared architectural boundaries where shell, layout,
   workspace, and module ownership are now clearer,
4. any future module addition that bypasses the governed shell registry and runtime boundaries.

## Target micro-frontend composition model confirmed by slice 8

Slice 8 confirms the module and extension posture required for RFC-0081 implementation.

### 1. Shell-owned module registration model

The shell should own a governed module registry that defines:

1. business workspace identity,
2. route entry,
3. module visibility and entitlement,
4. supportability posture,
5. shell navigation participation,
6. automation participation,
7. deprecation and replacement metadata.

This registry should use governed shell vocabulary:

1. `Portfolio`
2. `Performance`
3. `Risk`
4. `Proposal`
5. `Advisory`

### 2. Module-boundary model

Each shell module should own:

1. domain presentation,
2. module-local composition,
3. route-safe workspace bootstrapping,
4. module-specific interaction flows,
5. module-level tests.

Each shell module should not own:

1. shell chrome,
2. global navigation,
3. shared runtime addressing,
4. global query policy,
5. shared supportability-state primitives,
6. duplicated workflow-truth logic already owned by gateway and domain services.

### 3. Shared runtime and dependency model

The modular shell requires a clearer shared runtime layer for:

1. gateway bootstrap and service addressing,
2. query policy and data-fetch posture,
3. entitlement and visibility semantics,
4. supportability-state interpretation,
5. observability and event emission,
6. cache and revalidation hooks,
7. module-registration consumption.

This runtime layer should become the stable composition boundary between the shell and the modules.

### 4. Cleanup and retirement model

Every migration from a legacy route or module family must include:

1. a replacement module owner,
2. route transition behavior,
3. automation update requirements,
4. validation coverage,
5. final retirement conditions.

Legacy route and app families such as `recommendations`, `suite`, and `workbench` should not remain
indefinitely once governed replacements are proven.

### 5. Automation and extension rule

Future module additions must not be treated as purely frontend work.

Each new shell module or major panel family must declare:

1. route ownership,
2. gateway bootstrap contract,
3. supportability model,
4. screenshot and validation coverage requirements,
5. telemetry and audit expectations.

This is required so the micro-frontend direction remains governed rather than becoming a new source
of shell drift.

## Review of slice 8

### What was improved by the review

The review tightened several important points:

1. it made clear that a central registry already exists, but its vocabulary and ownership model are
   still transitional,
2. it clarified that shell thinness is not the problem; implicit composition boundaries are,
3. it tied design-system naming cleanup directly to module-boundary clarity,
4. it elevated route retirement and automation participation into first-class module-governance
   rules,
5. it prevented the future micro-frontend model from being defined only as "many apps under one
   shell" without strong runtime and registration contracts.

### What was consciously not changed in slice 8

1. no `lotus-workbench` shell or registry code was changed yet,
2. no route families were retired yet,
3. no module-registration contract files were introduced yet,
4. no runtime layer was expanded yet,
5. no automation guidance was updated yet.

This is correct for slice 8. The slice exists to lock the module-boundary and extension model
before implementation begins reworking shell registration, runtime composition, and route cleanup.

### Guidance and context decision

No immediate validator or onboarding guidance update is required before implementation begins.

Reason:

1. the module and extension model is now clear, but the governed runtime and onboarding guidance
   should be updated only after shell registration and route cleanup become operational reality,
2. updating guidance now would document future module behavior that is not yet implemented.

This is a conscious no-change decision.

### Follow-up implications for slice 9

Slice 9 should proceed with these tighter assumptions:

1. AI-assisted surfaces must plug into the governed module and shell model rather than bypassing it,
2. AI disclosure, feedback, and audit controls should be designed as shared shell-module behavior
   rather than page-local widgets,
3. future AI search and command surfaces must follow the same runtime and registration discipline as
   other modules.

## Conclusion

Slice 8 is complete.

It produced a code-grounded micro-frontend composition assessment, explicit keep/replace/retire
decisions, and a defensible shell-module, runtime, retirement, and extension model for the later
implementation slices.
