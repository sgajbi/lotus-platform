# RFC-0081 Slice 3: Shell, Navigation, and Design-System Foundation Evidence

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Slice: `Slice 3: Shell, Navigation, and Design-System Foundation`
- Date: 2026-04-12
- Status: Completed and reviewed

## Scope of the assessment

Slice 3 reviewed the current `lotus-workbench` shell, navigation, typography, token ownership, and
shared UI foundation to define the implementation target for the shell uplift.

The slice focused on:

1. shell frame and app switcher behavior,
2. route and navigation vocabulary,
3. shared text and typography primitives,
4. design tokens and theme ownership,
5. shell-related CSS topology,
6. dead or duplicate shell styling patterns that should be retired.

The goal of the slice was to lock the foundation model before route-level UI implementation starts.

## Files and surfaces reviewed

Reviewed directly in `lotus-workbench`:

1. `src/shell/app-shell.tsx`
2. `src/shell/app-registry.ts`
3. `src/shell/app-switcher-nav.tsx`
4. `src/design-system/theme/tokens.ts`
5. `src/design-system/theme/mui-theme.ts`
6. `src/design-system/components/text.tsx`
7. `src/design-system/components/app-page-shell.tsx`
8. `src/design-system/components/workbench-page-header.tsx`
9. `src/design-system/components/page-toolbar.tsx`
10. `src/design-system/components/workspace-layout.tsx`
11. `src/app/globals.css`

## Current-state findings

### 1. The current shell frame is usable, but still too thin for the target enterprise product shell

Evidence:

1. `src/shell/app-shell.tsx` currently provides:
   - Lotus identity,
   - a top bar,
   - `AppSwitcherNav`,
   - page body slot
2. it does not yet provide:
   - shell search,
   - banker context,
   - notification center,
   - command surface,
   - shell-level status or freshness affordances.

Assessment:

1. keep the shell-root pattern,
2. replace the current shell frame with a richer enterprise shell composition,
3. avoid adding more page-local substitutes for shell concerns.

### 2. The current shell navigation model is transitional and does not match the target topology

Evidence:

1. `src/shell/app-registry.ts` still defines:
   - `Overview`,
   - `Relationship Book`,
   - `Portfolio`,
   - `Performance`,
   - `Reporting`,
   - `Operations`
2. `src/shell/app-switcher-nav.tsx` renders this as app-switcher navigation backed by fallback
   platform capabilities.

Assessment:

1. keep the registry-driven navigation concept,
2. replace the current vocabulary with the governed front-office workspaces:
   - `Portfolio`
   - `Performance`
   - `Risk`
   - `Proposal`
   - `Advisory`
3. retire ambiguous or transitional shell labels such as `Overview` and `Operations` once their
   governed replacements exist.

Current gap:

1. shell navigation still reflects implementation history rather than product topology.

### 3. The typography and token direction is strong, but ownership is split across too many layers

Evidence:

1. `src/design-system/theme/tokens.ts` already defines:
   - colors,
   - spacing,
   - radius,
   - typography variants,
   - layout tokens,
   - table density tokens
2. `src/design-system/components/text.tsx` already maps a governed set of text variants,
3. `src/design-system/theme/mui-theme.ts` uses tokens for MUI surfaces.

Assessment:

1. keep the design-token investment,
2. keep the governed `Text` primitive,
3. replace the current split ownership model where too much shell and typography behavior still
   lives in global CSS instead of token-governed component styling.

Current gap:

1. token intent exists, but runtime ownership is not yet tight enough for a large uplift.

### 4. `src/app/globals.css` is carrying too much shell and shared-component responsibility

Evidence:

1. `globals.css` imports fonts, defines root variables, shell layout rules, typography classes,
   shell navigation styles, responsive rules, workbench card rules, chart rules, toolbar rules,
   and many product-area styles in one very large file,
2. shell styles such as:
   - `.shell-topbar`
   - `.shell-nav`
   - `.shell-nav-link`
   - `.shell-brand`
   coexist in the same file as many route-specific or module-era styles.

Assessment:

1. keep only truly global reset and root-token wiring in global CSS,
2. replace monolithic global styling with clearer ownership:
   - shell styles,
   - navigation styles,
   - typography primitives,
   - shared layout primitives,
   - workspace-specific styles
3. retire shell styling that remains trapped in page-era global CSS once migrated to design-system
   or shell-owned files.

Current gap:

1. the current CSS topology will create more drift if later slices keep adding shell and workspace
   logic into one global stylesheet.

### 5. Shared layout primitives are promising, but naming and layering still need tightening

Evidence:

1. `workspace-layout.tsx` provides reusable composition primitives:
   - `WorkstationPage`
   - `WorkspaceLayout`
   - `WorkspaceRail`
   - `WorkspaceMain`
   - `WorkspaceSide`
   - `WorkstationShell`
2. `app-page-shell.tsx`, `workbench-page-header.tsx`, and `page-toolbar.tsx` provide foundational
   wrappers for page structure.

Assessment:

1. keep these shared layout primitives,
2. keep layout composition in reusable components rather than page-local wrappers,
3. replace naming and layering that still mixes:
   - `app`,
   - `workbench`,
   - `workspace`,
   - `workstation`
   without a final governed hierarchy.

Current gap:

1. naming and ownership are close, but not yet clean enough for a long-lived shell and
   micro-frontend host.

### 6. The current visual language already trends institutional, but it still overuses soft gradients and shell chrome

Evidence:

1. `globals.css` still uses shell gradients, sticky chrome, and multiple shadow rules,
2. the RFC target is more restrained:
   - neutral surfaces,
   - disciplined hierarchy,
   - low shadow,
   - strong typography,
   - action-first rails.

Assessment:

1. keep the current premium/institutional direction,
2. replace remaining decorative shell treatment that does not add decision value,
3. remove shell visual flourishes that make the product feel more transitional than enterprise.

### 7. Shell performance expectations need to be explicit before implementation

Evidence:

1. current shell pieces are small, but later slices will add search, notifications, advisory
   workflow rails, AI assist entry points, and more module composition,
2. no explicit shell performance budget is attached to the current shell foundations.

Assessment:

1. the shell should define first-paint, nav-switch, and command-surface expectations now,
2. later slices should not be allowed to grow shell complexity without budget and measurement.

## Keep / replace / retire decisions

### Keep

1. shell-root composition in `app-shell.tsx`,
2. registry-driven navigation,
3. token foundation in `tokens.ts`,
4. `Text` primitive as the typography contract,
5. shared layout primitives in `workspace-layout.tsx`,
6. MUI token integration in `mui-theme.ts`.

### Replace

1. transitional shell vocabulary in `app-registry.ts`,
2. app-switcher posture with a governed workspace shell navigation model,
3. split shell/token ownership between `tokens.ts`, MUI theme overrides, and broad global CSS,
4. shell styling that depends on one very large `globals.css`,
5. mixed `app` / `workbench` / `workspace` / `workstation` ownership language where a clearer
   hierarchy is needed.

### Retire

1. hidden and transitional shell entries once governed workspace entries exist,
2. decorative shell gradients and shadow treatment that add chrome rather than clarity,
3. shell-local CSS trapped inside monolithic global styling once moved to shell- or design-system-
   owned modules,
4. duplicate shell naming patterns that obscure ownership.

## Target shell and design-system foundation confirmed by slice 3

Slice 3 confirms this foundation model for RFC-0081 implementation.

### 1. Shell structure

The shell should evolve into one governed front-office frame with:

1. brand and entity context,
2. workspace navigation,
3. command/search entry,
4. shell actions and notifications,
5. optional assist/AI entry,
6. stable content frame for workspace pages.

### 2. Navigation model

Shell navigation should become workspace-first, not implementation-first.

The governed top-level workspace set is:

1. `Portfolio`
2. `Performance`
3. `Risk`
4. `Proposal`
5. `Advisory`

Hidden or compatibility-era shell entries should not remain part of the long-term model.

### 3. Typography and token ownership

Typography, spacing, radius, color, and layout standards should be governed from token-owned design
system sources first, with global CSS only providing:

1. reset,
2. root custom-property wiring,
3. truly global app behavior.

Page and shell styling should not continue to accumulate in a single global stylesheet.

### 4. Component ownership model

Shared ownership should follow this order:

1. design tokens,
2. shared text and typography primitives,
3. shell and navigation primitives,
4. shared layout primitives,
5. workspace-level composition,
6. page- and module-level domain rendering.

This prevents route-level code from re-owning shell and typography behavior.

### 5. Shell performance posture

The shell should adopt explicit performance expectations:

1. lightweight first paint,
2. low-cost workspace switching,
3. non-blocking command/search surface initialization,
4. deferred loading for non-critical shell adjuncts,
5. no workspace-local duplication of shell dependencies.

## Review of slice 3

### What was improved by the review

The review tightened several foundation decisions that would otherwise stay vague:

1. token direction is good enough to keep,
2. global CSS ownership is too broad and must be reduced,
3. shell naming and route vocabulary cleanup is mandatory,
4. shell performance expectations must be treated as architecture, not later optimization.

### What was consciously not changed in slice 3

1. no `lotus-workbench` code was changed yet,
2. no shell components were renamed yet,
3. no global CSS was split yet,
4. no tokens were changed yet.

This is correct for slice 3. The slice exists to lock the target shell and foundation model before
implementation code starts in later slices.

### Guidance and context decision

No immediate frontend skill or onboarding guidance update is required before implementation begins.

Reason:

1. the problem identified here is implementation topology, not missing agent routing guidance,
2. guidance updates will be more valuable once slices 4 through 6 establish the actual shell,
   naming, and module ownership changes.

This is a conscious no-change decision.

### Follow-up implications for slice 4

Slice 4 should now proceed from a clearer baseline:

1. naming cleanup is not just wording work, it is ownership cleanup,
2. typography standards must map directly onto the shared token model,
3. route and workspace terminology should align with the governed shell before deeper UI work
   begins.

## Conclusion

Slice 3 is complete.

It produced a code-grounded shell and design-system foundation assessment, explicit
keep/replace/retire decisions, and a defensible target model for later shell implementation slices.
