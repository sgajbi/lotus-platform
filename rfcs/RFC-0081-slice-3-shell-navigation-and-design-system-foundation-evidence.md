# RFC-0081 Slice 3: Shell, Navigation, and Design-System Foundation Evidence

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Slice: `Slice 3: Shell, Navigation, and Design-System Foundation`
- Date: 2026-04-12
- Status: Implemented

## Outcome

Slice 3 moved the shared shell and navigation foundation from assessment into implementation across
`lotus-workbench` and `lotus-gateway`.

The implemented foundation now provides:

1. one shared shell top bar plus workspace tab bar structure in `lotus-workbench`,
2. one governed workspace tab set:
   - `Portfolio`
   - `Performance`
   - `Risk`
   - `Proposal`
   - `Advisory`
3. shared design-system primitives for workspace tabs and toolbar groups,
4. explicit gateway navigation flags for the new workspace shell composition contract,
5. removal of stale duplicate shell nav CSS selectors that no longer match runtime markup.

## Repositories Changed

### `lotus-workbench`

Implemented shell and design-system foundation changes in:

1. `src/shell/app-registry.ts`
2. `src/shell/app-switcher-nav.tsx`
3. `src/shell/app-shell.tsx`
4. `src/design-system/components/workspace-tab-nav.tsx`
5. `src/design-system/components/workbench-toolbar-group.tsx`
6. `src/design-system/components/workspace-header.tsx`
7. `src/design-system/index.ts`
8. `src/features/platform-capabilities/types.ts`
9. `src/apps/portfolio/components/portfolio-workspace-toolbar.tsx`
10. `src/app/globals.css`
11. `tests/unit/app-shell.test.tsx`
12. `tests/integration/top-nav-capabilities.test.tsx`
13. `tests/unit/design-system-components.test.tsx`
14. `tests/unit/portfolio-workspace-toolbar.test.tsx`

### `lotus-gateway`

Aligned normalized capabilities to the shell composition contract in:

1. `src/app/services/platform_capabilities_service.py`
2. `tests/unit/test_platform_capabilities_service.py`
3. `tests/integration/test_platform_capabilities_router.py`
4. `tests/contract/test_platform_capabilities_contract.py`

## What Changed

### 1. Shell structure

`lotus-workbench` now uses a clearer shared shell structure:

1. shell brand row in `AppShell`,
2. dedicated shell workspace bar below the brand row,
3. shared workspace tab navigation component for shell tabs instead of page-local nav markup.

This normalized the shell frame so route surfaces can share one top-level navigation structure.

### 2. Navigation foundation

The shell app registry was standardized to the governed workspace set:

1. `Portfolio`
2. `Performance`
3. `Risk`
4. `Proposal`
5. `Advisory`

Implementation detail:

1. `Risk` is backed by the existing supported route `/performance?mode=risk`,
2. `Proposal` and `Advisory` remain visible but disabled because the shell routes are not yet
   backed by a stable supported workspace contract in this slice,
3. hidden transitional shell labels such as `Relationship Book`, `Reporting`, and `Operations`
   were removed from the runtime shell registry.

### 3. Shared primitives

The slice added or upgraded shared primitives for reuse:

1. `WorkspaceTabNav` for governed shell/workspace tab sets,
2. `WorkbenchToolbarGroup` for labeled toolbar groups,
3. `WorkspaceHeader` now composes through `WorkbenchPageHeader` so page header structure is shared
   instead of locally re-owned.

The portfolio toolbar now uses `WorkbenchToolbarGroup` instead of bespoke group markup, which gives
the shell and page-control foundation a shared component contract.

### 4. Gateway experience composition alignment

`lotus-gateway` now returns explicit normalized workspace navigation flags:

1. `portfolio_workspace`
2. `performance_workspace`
3. `risk_workspace`
4. `proposal_workspace`
5. `advisory_workspace`

These were added without removing legacy navigation keys so existing consumers stay compatible while
the shell begins moving to the governed workspace vocabulary.

### 5. Dead or duplicate styling removed

The slice removed stale duplicate shell nav CSS ownership by retiring unused `.shell-nav` and
`.shell-nav-link*` selector usage in favor of the new shared `.workspace-tab-nav*` contract.

## Validation

### `lotus-workbench`

Commands run:

1. `npx vitest run tests/unit/app-shell.test.tsx tests/integration/top-nav-capabilities.test.tsx tests/unit/design-system-components.test.tsx tests/unit/portfolio-workspace-toolbar.test.tsx`
2. `npm run lint`
3. `npm run typecheck`
4. `git diff --check`

Result:

1. focused shell/design-system tests passed,
2. lint passed,
3. typecheck passed,
4. diff check passed.

### `lotus-gateway`

Commands run:

1. `python -m pytest tests/unit/test_platform_capabilities_service.py tests/integration/test_platform_capabilities_router.py tests/contract/test_platform_capabilities_contract.py`
2. `python -m ruff check .`
3. `python -m ruff format --check .`
4. `python scripts/check_monetary_float_usage.py`
5. `python -m mypy src`
6. `git diff --check`

Result:

1. focused gateway tests passed,
2. ruff check passed,
3. ruff format check passed after formatting the touched files,
4. monetary float guard passed,
5. mypy passed,
6. diff check passed.

## Screenshot Evidence

Shell top bar and workspace tab evidence was captured from the canonical populated workbench using
`PB_SG_GLOBAL_BAL_001` under:

`C:\Users\Sandeep\projects\lotus-workbench\output\playwright\rfc-0081-slice-3-review`

Files:

1. `portfolio-shell-tabs.png`
2. `performance-shell-tabs.png`
3. `risk-shell-tabs.png`

## Consciously Not Changed

Slice 3 did not:

1. add new business actions,
2. change backend business behavior,
3. enable unsupported Proposal or Advisory workflows,
4. redesign portfolio modules beyond moving the portfolio toolbar onto the shared toolbar-group
   primitive,
5. change stable existing routes except exposing `Risk` through the already-supported
   `/performance?mode=risk` workspace mode.

## Follow-Up Notes For Slice 4

Slice 4 can now build on a real shared shell/navigation contract instead of page-local markup.

Recommended next focus:

1. move additional shared shell/layout styling out of `globals.css` where practical,
2. extend the shared header and card primitives only where they replace duplication,
3. keep Proposal and Advisory disabled until backed by supported workspace routes and data.
