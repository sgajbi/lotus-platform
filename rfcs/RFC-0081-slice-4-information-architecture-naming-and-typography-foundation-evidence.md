# RFC-0081 Slice 4: Shared Information Architecture, Naming, and Typography Foundation Evidence

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Slice: `Slice 4: Shared Information Architecture, Naming, and Typography Foundation`
- Date: 2026-04-12
- Status: Completed and reviewed

## Scope of the assessment

Slice 4 reviewed current route, module, shell, and typography naming across `lotus-workbench` and
the related gateway-facing vocabulary to define the governed language and topology for RFC-0081.

The slice focused on:

1. top-level workspace naming,
2. route and module topology naming,
3. transitional vocabulary that should be retired,
4. typography naming and ownership expectations,
5. alignment between frontend workspace language and gateway experience-contract language.

The goal of the slice was to remove ambiguity before later implementation starts renaming or
recomposing code.

## Files and surfaces reviewed

Reviewed directly in `lotus-workbench`:

1. `src/shell/app-registry.ts`
2. `src/shell/app-switcher-nav.tsx`
3. `src/shell/workspace-capabilities.ts`
4. `src/features/platform-capabilities/api.ts`
5. `src/design-system/index.ts`
6. `src/app/layout.tsx`
7. route inventory under `src/app/*`
8. module inventory under `src/apps/*`
9. token and typography surfaces already reviewed in slice 3

Reviewed directly in `lotus-gateway`:

1. `src/app/main.py`
2. `docs/documentation/experience-api-foundation-blueprint.md`
3. implemented and proposed gateway RFC references for:
   - foundation,
   - proposal,
   - platform capabilities,
   - workbench contracts

## Current-state findings

### 1. Top-level shell vocabulary is still inconsistent with the governed product model

Evidence:

1. `src/shell/app-registry.ts` currently uses:
   - `Overview`
   - `Relationship Book`
   - `Portfolio`
   - `Performance`
   - `Reporting`
   - `Operations`
2. RFC-0081 target shell vocabulary is:
   - `Portfolio`
   - `Performance`
   - `Risk`
   - `Proposal`
   - `Advisory`

Assessment:

1. keep `Portfolio` and `Performance`,
2. replace `Overview`, `Relationship Book`, `Reporting`, and `Operations` as top-level shell
   language,
3. promote `Risk`, `Proposal`, and `Advisory` into the governed shell vocabulary.

Current gap:

1. shell naming still reflects transitional implementation history rather than product ownership.

### 2. Route topology is carrying both migration-era and target-era names at the same time

Evidence:

1. current `src/app` route directories include:
   - `intake`
   - `performance`
   - `portfolio`
   - `portfolios`
   - `proposals`
   - `recommendations`
   - `suite`
   - `workbench`
2. current `src/apps` module directories include:
   - `home`
   - `performance`
   - `portfolio`
   - `recommendations`
3. `src/app/portfolio/page.tsx` is already a clean domain route that delegates to
   `@/apps/portfolio/page`.

Assessment:

1. keep route-to-app delegation where it is already clean,
2. keep `portfolio` and `performance` as the current business-domain routes,
3. replace or retire migration-era directories such as:
   - `workbench`
   - `suite`
   - `intake`
   - `recommendations`
   where they no longer represent the long-term product topology,
4. avoid keeping both singular and plural product-route families without a governed reason.

Current gap:

1. the route tree still exposes too much transitional history to future implementers.

### 3. Naming across the design system is too mixed between generic, workspace, workbench, and workstation language

Evidence:

1. `src/design-system/index.ts` exports a mixture of names including:
   - `AppPageShell`
   - `WorkbenchPageHeader`
   - `WorkspaceHeader`
   - `WorkstationPage`
   - `WorkstationShell`
   - `WorkspaceLayout`
   - `WorkbenchStatusStrip`
   - `WorkspaceStatusPanel`
2. `src/design-system/components/workspace-layout.tsx` mixes:
   - `Workspace*`
   - `Workstation*`
3. CSS class names in `globals.css` also mix:
   - `workbench-*`
   - `workspace-*`
   - `workstation-*`

Assessment:

1. keep reusable shared primitives,
2. replace mixed naming with a governed hierarchy,
3. make naming indicate ownership:
   - shell,
   - layout,
   - workspace,
   - module,
   - domain.

Current gap:

1. component names are reusable, but ownership is not obvious enough for a large modular shell.

### 4. Platform-capability and workspace-capability language is good, but the product-facing business language is still too implementation-colored

Evidence:

1. `workspace-capabilities.ts` has clean state vocabulary:
   - `supported`
   - `partial`
   - `unavailable`
   - `hidden`
2. `features/platform-capabilities/api.ts` still exposes a frontend-facing fetch contract for
   `platform/capabilities`,
3. gateway docs still use a mix of:
   - `workspace`
   - `foundation`
   - `workbench`
   - `proposal`
   - `platform capabilities`

Assessment:

1. keep supportability-state vocabulary,
2. keep `platform capabilities` for cross-service feature negotiation,
3. replace product-facing language that forces frontend ownership to stay coupled to historical
   gateway area names such as `foundation` or `workbench` when a business workspace name is now
   clearer.

Current gap:

1. product language should be business-first, while technical capability language can remain
   technical behind the shell boundary.

### 5. Typography direction is good, but the naming standard needs to become explicit and bank-grade

Evidence:

1. tokens and text variants already exist,
2. typography classes and token names still mix implementation and historical workbench language,
3. RFC-0081 now requires a professional, conservative, institutional tone.

Assessment:

1. keep the existing typography scale direction,
2. formalize naming around business and design semantics rather than local page usage,
3. require typography naming to stay stable and reusable:
   - page title,
   - workspace title,
   - section title,
   - card title,
   - label,
   - metadata,
   - metric value.

Current gap:

1. the current scale is strong enough, but the final naming contract is not yet explicit enough for
   long-lived governance.

## Keep / replace / retire decisions

### Keep

1. business-domain routes such as `portfolio` and `performance`,
2. route-to-app delegation pattern,
3. supportability-state vocabulary in `workspace-capabilities.ts`,
4. token-driven typography direction,
5. modular app ownership under `src/apps/*` where the domain is already clear.

### Replace

1. top-level shell labels that do not match the target product model,
2. mixed singular/plural and migration-era route naming without governed purpose,
3. mixed `workbench` / `workspace` / `workstation` / `app` naming across shared primitives,
4. product-facing terminology that still exposes historic gateway area names where business domain
   names are clearer.

### Retire

1. `Overview` and `Operations` as long-term shell entries,
2. compatibility-era route labels such as `suite` where they no longer describe the product,
3. duplicate or ambiguous route families such as `portfolio` and `portfolios` unless one remains a
   technical redirect only,
4. shared-component names that preserve historical branding rather than stable architectural
   ownership.

## Target information architecture and naming model confirmed by slice 4

Slice 4 confirms the governed naming and topology model for RFC-0081 implementation.

### 1. Top-level shell vocabulary

The governed top-level shell vocabulary is:

1. `Portfolio`
2. `Performance`
3. `Risk`
4. `Proposal`
5. `Advisory`

This is the business vocabulary for the front-office shell.

### 2. Route topology model

The route model should converge toward:

1. business-domain route families at the shell level,
2. route-to-app delegation,
3. technical compatibility redirects only where unavoidable,
4. retirement of migration-era route families once replacements are proven.

The shell should not expose historical topology such as `suite` or `workbench` as enduring
business route names.

### 3. Shared naming hierarchy

Shared frontend naming should indicate ownership in this order:

1. `Shell`
2. `Layout`
3. `Workspace`
4. `Module`
5. domain-specific artifact names

This means future implementation should reduce mixed use of:

1. `Workbench*`
2. `Workspace*`
3. `Workstation*`

where they describe the same ownership layer.

### 4. Business language rule

Frontend product surfaces should prefer business-domain language over technical implementation
labels.

Examples:

1. `Proposal` instead of generic recommendation-era naming,
2. `Advisory` instead of operationally vague shell labels,
3. `Risk` as a first-class workspace rather than a hidden analytical mode,
4. `Client artifact` and `approval pack` where those are banker-facing concepts,
5. technical terms such as `platform capabilities` or `foundation` remain behind composition and
   contract boundaries, not in product navigation.

### 5. Typography naming rule

Typography naming should be governed by stable semantic roles, not page-local context.

Required stable roles include:

1. page title,
2. workspace title,
3. section title,
4. card title,
5. body,
6. metadata,
7. label,
8. KPI or metric value.

These should remain the owned language across tokens, components, and CSS.

## Review of slice 4

### What was improved by the review

The review tightened several issues that were previously easy to understate:

1. naming cleanup is a structural issue, not documentation-only cleanup,
2. route topology cleanup is part of ownership cleanup,
3. business language should be the public shell language even if gateway internals retain
   technical-area names,
4. typography governance needs stable semantic roles rather than page-era naming.

### What was consciously not changed in slice 4

1. no routes were renamed yet,
2. no shell registry entries were changed yet,
3. no design-system components were renamed yet,
4. no gateway docs or contracts were changed yet.

This is correct for slice 4. The slice exists to define the governed language and topology before
the implementation slices begin making naming and route changes.

### Guidance and context decision

No immediate agent skill or onboarding guidance update is required before implementation begins.

Reason:

1. this slice defines naming and topology decisions, but runtime and routing guidance will become
   more valuable after later slices land actual shell and route changes,
2. updating context now would risk documenting a target-state vocabulary before any repo has adopted
   it operationally.

This is a conscious no-change decision.

### Follow-up implications for slice 5

Slice 5 should now proceed with a tighter contract-language assumption:

1. gateway shell and workspace bootstrap contracts should align to the governed shell vocabulary,
2. technical capability and supportability metadata should remain explicit but should not drive
   product navigation naming,
3. contract naming should anticipate the future shell topology instead of preserving workbench-era
   seams.

## Conclusion

Slice 4 is complete.

It produced a code-grounded naming, topology, and typography-governance assessment, explicit
keep/replace/retire decisions, and a defensible language model for later shell and gateway
implementation slices.
