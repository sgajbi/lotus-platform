# RFC-0075 Implementation Checklist

- RFC: `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
- Status: Pending approval
- Last updated: 2026-04-11

## Approval Gate

- [ ] RFC reviewed by platform owner.
- [ ] RFC approved for implementation.
- [ ] Canonical portfolio ID confirmed as `PB_SG_GLOBAL_BAL_001`.
- [ ] Canonical benchmark ID confirmed as `BMK_PB_GLOBAL_BALANCED_60_40`.
- [ ] Demo as-of date policy confirmed.
- [ ] Supported versus intentionally partial panels confirmed.

## Slice 1: Baseline Diagnostics

- [ ] Capture current backend endpoint status.
- [ ] Capture current workbench panel status.
- [ ] Record stale Docker and stale data failure modes.
- [ ] Record calculation failures separately from UI mapping failures.
- [ ] Identify owning repository for each failure.

## Slice 2: Docker, Ingress, and Startup

- [ ] Standardize clean Docker teardown.
- [ ] Remove stale volume ambiguity.
- [ ] Ensure canonical ingress routes only to the active stack.
- [ ] Validate DSN and environment setup for all participating services.
- [ ] Update governed startup runbook.
- [ ] Add or update tests for startup automation where practical.

## Slice 3: Core Seed Data

- [ ] Rebuild canonical transaction economics.
- [ ] Ensure no nonsensical negative economics unless explicitly documented.
- [ ] Ensure market prices cover every instrument through the ready date.
- [ ] Ensure FX rates cover every required currency pair through the ready date.
- [ ] Ensure benchmark definition, composition, return series, and assignment are complete.
- [ ] Ensure risk-free series covers performance and risk windows.
- [ ] Remove timestamped smoke portfolio pollution.
- [ ] Add unit tests for seed completeness and cleanup.

## Slice 4: Derived State Readiness

- [ ] Validate positions and valued positions.
- [ ] Validate transaction and cash account counts.
- [ ] Validate position timeseries reaches ready date.
- [ ] Validate portfolio timeseries reaches ready date.
- [ ] Validate analytics reference `performance_end_date` is current.
- [ ] Add actionable diagnostics for stuck async processing.
- [ ] Add focused tests for readiness checks.

## Slice 5: Performance and Risk Calculations

- [ ] Validate performance workspace summary.
- [ ] Validate contribution detail rows.
- [ ] Validate attribution detail rows or governed fallback.
- [ ] Validate benchmark-relative return behavior.
- [ ] Validate risk snapshot.
- [ ] Validate drawdown.
- [ ] Validate concentration.
- [ ] Validate rolling risk.
- [ ] Validate historical risk attribution.
- [ ] Add meaningful tests for calculation and contract gaps found.

## Slice 6: Gateway and Workbench Panels

- [ ] Validate gateway mappings for performance details.
- [ ] Validate gateway mappings for risk details.
- [ ] Validate advisor brief mappings.
- [ ] Validate manage/report partial behavior or DSN-backed readiness.
- [ ] Tighten workbench panel checks to fail on unsupported blank panels.
- [ ] Ensure all UI states are truthful: ready, loading, empty, partial, error.

## Slice 7: Screenshot Automation

- [ ] Capture portfolio summary screenshot.
- [ ] Capture performance summary screenshot.
- [ ] Capture performance analysis screenshot.
- [ ] Capture advisor brief screenshot.
- [ ] Capture risk screenshot.
- [ ] Capture evidence screenshot if contract-supported or truthfully degraded.
- [ ] Store screenshots in caller-provided output directory.
- [ ] Write machine-readable run summary.

## Slice 8: Documentation and Agent Context

- [ ] Update platform runbook.
- [ ] Update onboarding docs.
- [ ] Update agent context with governed demo path.
- [ ] Remove stale scripts and stale references.
- [ ] Update skills if a reusable pattern emerges.
- [ ] Confirm repo-local engineering context references the governed path where relevant.

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
