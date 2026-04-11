# RFC-0075 Implementation Checklist

- RFC: `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
- Status: Slice 4 complete
- Last updated: 2026-04-11

## Approval Gate

- [x] RFC reviewed by platform owner.
- [x] RFC approved for Slice 1 implementation.
- [x] Canonical portfolio ID confirmed as `PB_SG_GLOBAL_BAL_001`.
- [x] Canonical benchmark ID confirmed as `BMK_PB_GLOBAL_BALANCED_60_40`.
- [x] Fixed demo as-of date policy recorded.
- [x] Proposed demo as-of date `2026-04-10` recorded for final confirmation during implementation.
- [x] Supported versus intentionally partial panel categories recorded.
- [x] Docker cleanup scope recorded as explicit clean mode.
- [x] Optional service DSN policy recorded as a Slice 2 decision item.
- [x] Diagnostic screenshot policy confirmed.

## Slice 1: Baseline Diagnostics

- [x] Capture current backend endpoint status.
- [x] Capture current workbench panel status.
- [x] Record stale Docker and stale data failure modes.
- [x] Record calculation failures separately from UI mapping failures.
- [x] Identify owning repository for each failure.
- [x] Record `PORT_SMOKE_%` pollution status.
- [x] Record canonical portfolio analytics reference date status.
- [x] Record gateway/workbench mapping gaps separately from upstream calculation gaps.
- [x] Record manage/advisory/report/AI partial states.

## Slice 2: Docker, Ingress, and Startup

- [x] Standardize clean Docker teardown.
- [x] Remove stale volume ambiguity.
- [x] Remove stale local Lotus image ambiguity when full clean mode is selected.
- [x] Ensure canonical ingress routes only to the active stack.
- [x] Validate DSN and environment setup for all participating services.
- [x] Update governed startup runbook.
- [x] Add or update tests for startup automation where practical.
- [x] Emit a run summary with cleanup scope and service startup evidence.

## Slice 3: Core Seed Data

- [x] Rebuild canonical transaction economics.
- [x] Ensure no nonsensical negative economics unless explicitly documented.
- [x] Validate buy, sell, income, fee, withdrawal, and cash-leg sign conventions.
- [x] Validate deterministic transaction, source record, and economic event IDs.
- [x] Ensure market prices cover every instrument through the ready date.
- [x] Ensure FX rates cover every required currency pair through the ready date.
- [x] Ensure benchmark definition, composition, return series, and assignment are complete.
- [x] Ensure risk-free series covers performance and risk windows.
- [x] Remove timestamped smoke portfolio pollution.
- [x] Add unit tests for seed completeness and cleanup.
- [x] Add tests for portfolio economic sanity and date coverage.

## Slice 4: Derived State Readiness

- [x] Validate positions and valued positions.
- [x] Validate transaction and cash account counts.
- [x] Validate position timeseries reaches ready date.
- [x] Validate portfolio timeseries reaches ready date.
- [x] Validate analytics reference `performance_end_date` is current.
- [x] Add actionable diagnostics for stuck async processing.
- [x] Add focused tests for readiness checks.
- [x] Persist readiness evidence in a machine-readable run summary.

## Slice 5: Performance and Risk Calculations

- [ ] Validate performance workspace summary.
- [ ] Validate contribution detail rows.
- [ ] Validate attribution detail rows or governed fallback.
- [ ] Validate benchmark-relative return behavior.
- [ ] Validate performance numeric sanity ranges.
- [ ] Validate risk snapshot.
- [ ] Validate drawdown.
- [ ] Validate concentration.
- [ ] Validate rolling risk.
- [ ] Validate historical risk attribution.
- [ ] Validate risk row/window/contributor counts.
- [ ] Add meaningful tests for calculation and contract gaps found.

## Slice 6: Gateway and Workbench Panels

- [ ] Validate gateway mappings for performance details.
- [ ] Validate gateway mappings for risk details.
- [ ] Validate advisor brief mappings.
- [ ] Validate manage/report partial behavior or DSN-backed readiness.
- [ ] Tighten workbench panel checks to fail on unsupported blank panels.
- [ ] Ensure all UI states are truthful: ready, loading, empty, partial, error.
- [ ] Classify each panel as supported, intentionally empty, partial, unavailable, or out of scope.
- [ ] Block demo-ready screenshot capture when required panels fail validation.

## Slice 7: Screenshot Automation

- [ ] Capture portfolio summary screenshot.
- [ ] Capture performance summary screenshot.
- [ ] Capture performance analysis screenshot.
- [ ] Capture advisor brief screenshot.
- [ ] Capture risk screenshot.
- [ ] Capture evidence screenshot if contract-supported or truthfully degraded.
- [ ] Store screenshots in caller-provided output directory.
- [ ] Write machine-readable run summary.
- [ ] Prefix pre-validation screenshots with `diagnostic-`.
- [ ] Record route, panel, portfolio ID, benchmark ID, and as-of date for each screenshot.

## Slice 8: Documentation and Agent Context

- [ ] Update platform runbook.
- [ ] Update onboarding docs.
- [ ] Update agent context with governed demo path.
- [ ] Remove stale scripts and stale references.
- [ ] Update skills if a reusable pattern emerges.
- [ ] Confirm repo-local engineering context references the governed path where relevant.
- [ ] Document the exact first command for clean demo bring-up after implementation.
- [ ] Document how to troubleshoot each validation failure category.

## Final Acceptance

- [ ] Clean Docker start from zero state succeeds.
- [ ] Canonical seed is deterministic.
- [ ] Backend endpoint validation passes.
- [ ] Workbench panel validation passes.
- [ ] Screenshots are populated and clean.
- [ ] No `PORT_SMOKE_%` portfolio pollution remains.
- [ ] All changed repositories have meaningful tests.
- [ ] CI evidence is truthful.
- [ ] PRs are raised with small meaningful commits.
- [ ] Machine-readable validation summary is produced.
- [ ] Remaining partial/unavailable panels have explicit ownership and rationale.
