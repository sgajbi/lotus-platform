# RFC-0075: Canonical Front-Office Portfolio Seed and Demo Validation System

- Status: Proposed
- Date: 2026-04-11
- Owners: lotus-platform governance
- Requires Approval From:
  - lotus-platform maintainers
  - lotus-core maintainers
  - lotus-performance maintainers
  - lotus-risk maintainers
  - lotus-gateway maintainers
  - lotus-workbench maintainers
  - lotus-advise maintainers
  - lotus-manage maintainers
  - lotus-report maintainers
  - lotus-ai maintainers
- Related:
  - `RFC-0057-test-pyramid-and-meaningful-coverage-governance.md`
  - `RFC-0063-performance-analytics-input-contracts-and-stateful-computation.md`
  - `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`
  - `RFC-0070-gold-standard-product-experience-foundation-and-ownership-model.md`
  - `RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
  - `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`
  - `RFC-0074-repeatable-developer-and-agent-bootstrap-system.md`

## Summary

Lotus needs one governed, canonical front-office portfolio seed that can reliably bring up the full platform, populate all supported workbench panels, validate calculations, and produce clean demo screenshots without stale Docker state, stale data, or ad hoc local fixes.

This RFC proposes a platform-owned canonical seed and validation system centered on `PB_SG_GLOBAL_BAL_001`.

The goal is not merely to make one screen look populated. The goal is to create a realistic, auditable front-office scenario that exercises the full Lotus analytics stack:

1. portfolio master data,
2. instruments across meaningful asset classes,
3. cash accounts and multi-currency cash,
4. a broad transaction lifecycle,
5. market prices and FX rates through the demo as-of date,
6. benchmark definition, composition, and return history,
7. portfolio, position, performance, risk, advisory, manage, report, gateway, and workbench behavior,
8. canonical ingress and DSN configuration,
9. automated smoke and panel-level validation,
10. screenshot capture with proof that UI panels are backed by real data.

## Problem

The current front-office demo flow has shown avoidable failure modes:

1. stale Docker containers and volumes can be mistaken for current platform truth,
2. historical smoke scripts created repeated `PORT_SMOKE_*` data that polluted portfolio lookup screens,
3. seed verification could pass before all downstream derived state was complete,
4. portfolio-level and position-level timeseries could become inconsistent during asynchronous reprocessing,
5. UI panels could appear empty even though an upstream service had partial data,
6. canonical hostnames could be confused with stale local stack instances,
7. benchmark-relative detail could degrade without the seed tool failing fast,
8. DSN-backed optional services such as `lotus-manage` could surface partial failures during demos,
9. screenshots could be captured before data readiness was proven.

This is not acceptable for a banking-grade platform. Demo data is also test data. If it is weak, it hides defects and encourages superficial UI work.

## Goals

1. Define `PB_SG_GLOBAL_BAL_001` as the canonical front-office portfolio for local demos and full-stack QA.
2. Make the seed economically coherent and domain-realistic.
3. Ensure every supported workbench screen and sub-panel is populated by real backend functionality.
4. Make benchmark linkage and benchmark data complete for performance and risk analytics.
5. Ensure asynchronous core processing reaches a deterministic ready state before validation passes.
6. Make Docker cleanup, startup, seed, validation, and screenshot capture repeatable.
7. Remove stale smoke data patterns and stale startup paths.
8. Add meaningful tests where the seed and validation tooling previously relied on manual observation.
9. Use canonical endpoints end to end.
10. Document the governed path so future agents do not recreate ad hoc tooling.

## Non-Goals

1. Creating synthetic UI-only fixtures that bypass backend contracts.
2. Replacing production portfolio ingestion with a demo-specific pipeline.
3. Optimizing every analytics engine as part of this RFC.
4. Making screenshots the primary validation mechanism.
5. Adding unsupported product features solely to make a demo look richer.
6. Treating partial or unavailable capabilities as populated if the backend contract does not support them.

## Design Principles

1. Backend truth before UI polish.
2. Canonical ingress before localhost shortcuts.
3. Deterministic seed IDs before timestamped smoke artifacts.
4. Readiness gates before screenshots.
5. Domain-correct economics before convenient mock data.
6. Summary first, detail on demand in the UI.
7. All panels must handle ready, empty, partial, loading, and error states truthfully.
8. Tooling must be idempotent and safe to rerun.
9. Validation must assert business facts, not only HTTP 200 responses.
10. Every durable pattern must be captured in docs, context, or automation.

## Decision

Lotus will create a governed canonical front-office demo seed and validation system owned by `lotus-platform`, with data ownership and calculation correctness implemented in the relevant domain repositories.

The canonical portfolio will remain:

```text
PB_SG_GLOBAL_BAL_001
```

The canonical benchmark will remain:

```text
BMK_PB_GLOBAL_BALANCED_60_40
```

The canonical local access path will use ingress hostnames, not random localhost endpoints, except where service-local diagnostics explicitly require direct calls.

## Target State

### Canonical data profile

`PB_SG_GLOBAL_BAL_001` must represent a realistic Singapore-booked private banking balanced mandate:

1. base currency USD,
2. Singapore booking center,
3. discretionary balanced mandate,
4. long-term growth and income objective,
5. multi-currency cash,
6. equity, fixed income, fund, ETF, private credit, and cash exposure,
7. realistic issuer, sector, country, liquidity tier, rating, maturity, and currency attributes,
8. enough observations to support return, risk, concentration, drawdown, rolling risk, contribution, attribution, and advisor/reporting surfaces.

### Required transaction coverage

The seed must include a broad but coherent transaction lifecycle:

1. initial cash funding,
2. multi-currency deposits,
3. equity buys and partial sells,
4. fixed income buys,
5. fund and ETF buys,
6. private credit subscription,
7. dividends,
8. bond interest,
9. advisory fees,
10. planned withdrawals,
11. cash legs linked to securities transactions where required,
12. FX-relevant movements where the portfolio economics require them.

The transaction model must not create negative or nonsensical portfolio economics unless the scenario explicitly documents leverage or short exposure.

### Required market and reference data coverage

The seed must include complete data coverage through the configured demo as-of date:

1. business calendar points,
2. market prices for every non-cash instrument,
3. cash prices,
4. EUR/USD and USD/EUR FX rates,
5. benchmark definitions,
6. benchmark compositions,
7. benchmark return series,
8. benchmark assignment,
9. risk-free series for risk and performance analytics,
10. classification data required by supported groupings.

### Required derived state readiness

The seed flow must not pass until downstream state is complete enough for the canonical UI:

1. positions are available and valued,
2. position timeseries covers the required analytics window,
3. portfolio timeseries covers the required analytics window,
4. portfolio analytics reference resolves a current `performance_end_date`,
5. benchmark assignment resolves through the query control plane,
6. performance workspace summary returns contribution rows,
7. performance workspace summary returns attribution rows or a truthful documented fallback,
8. risk summary, rolling risk, drawdown, concentration, and historical attribution return non-empty supported results,
9. manage/advisory/report optional panels either return ready data or explicitly documented partial states that are acceptable for the demo.

## Automation Target State

The canonical flow should be executable through one platform-governed path:

1. clean Docker state,
2. start all required Lotus services,
3. configure ingress,
4. configure DSNs and local environment,
5. seed `PB_SG_GLOBAL_BAL_001`,
6. wait for asynchronous core processing,
7. validate backend endpoints,
8. validate workbench panels,
9. capture screenshots,
10. write a machine-readable run summary.

The flow must support:

1. `-Clean` or equivalent cleanup mode,
2. `-BuildImages` or equivalent rebuild mode,
3. `-SeedOnly`,
4. `-ValidateOnly`,
5. `-ScreenshotOnly`,
6. configurable output directory,
7. deterministic portfolio and benchmark IDs,
8. clear failure messages with owning service attribution.

## Validation Requirements

Validation must go beyond simple health checks.

### Backend validation

Required backend checks:

1. core portfolio lookup returns the canonical portfolio only once,
2. no `PORT_SMOKE_%` portfolios remain after a clean seed,
3. positions count meets the seed expectation,
4. valued positions count meets the seed expectation,
5. transaction count meets the seed expectation,
6. cash accounts are present,
7. portfolio timeseries max date reaches the target ready date,
8. position timeseries max date reaches the target ready date,
9. portfolio analytics reference `performance_end_date` is not stale,
10. benchmark assignment returns `BMK_PB_GLOBAL_BALANCED_60_40`,
11. benchmark return series covers the requested window,
12. performance workspace summary returns non-empty contribution detail,
13. performance workspace summary returns non-empty attribution detail where contract-supported,
14. risk rolling metrics returns windows and rows,
15. risk drawdown returns a supported result,
16. risk concentration returns scale and top exposure data,
17. historical risk attribution returns grouped contributors,
18. manage/advisory/report backend checks either pass or report a known governed partial state.

### UI validation

Required workbench checks:

1. portfolio summary loads with the canonical portfolio,
2. performance summary loads,
3. performance analysis loads,
4. advisor brief loads,
5. risk summary loads,
6. risk sub-panels load,
7. evidence surface is truthful and not visually broken,
8. no expected panel is blank without an explicit empty or partial state,
9. screenshots are captured only after validation passes.

### Screenshot validation

Screenshots must be stored in a caller-provided directory, with the demo default:

```text
C:\Users\Sandeep\AppData\Local\Temp\lotus-risk-module-shots
```

Screenshot file names must be descriptive and stable, for example:

1. `workbench-portfolio-summary.png`,
2. `workbench-performance-summary.png`,
3. `workbench-performance-analysis.png`,
4. `workbench-performance-risk.png`,
5. `workbench-performance-advisor-brief.png`,
6. `workbench-performance-evidence.png`.

## Repository Responsibilities

### `lotus-platform`

Owns:

1. canonical runbook,
2. cross-repo orchestration entrypoint,
3. ingress and DSN setup documentation,
4. validation profile definitions,
5. agent context updates,
6. demo evidence artifact conventions.

### `lotus-core`

Owns:

1. canonical portfolio seed bundle,
2. cleanup semantics,
3. deterministic smoke seed behavior,
4. transaction and reference data correctness,
5. derived state readiness checks,
6. tests for seed completeness and stale data cleanup.

### `lotus-performance`

Owns:

1. performance workspace correctness,
2. contribution and attribution calculation readiness,
3. benchmark-linked behavior,
4. error reporting when seed economics are invalid.

### `lotus-risk`

Owns:

1. risk snapshot,
2. drawdown,
3. concentration,
4. rolling risk,
5. historical risk attribution,
6. validation evidence that canonical seed data supports supported risk panels.

### `lotus-gateway`

Owns:

1. canonical workbench contracts,
2. partial failure attribution,
3. correct mapping from backend analytics to UI-facing response contracts,
4. no stale report windows when current backend data is available.

### `lotus-workbench`

Owns:

1. canonical UI startup and validation scripts,
2. panel readiness checks,
3. screenshot capture,
4. no visual empty panels for supported populated contracts,
5. truthful partial and unavailable states.

### `lotus-advise`, `lotus-manage`, `lotus-report`, `lotus-ai`

Own:

1. startup participation in the canonical stack,
2. health and readiness checks,
3. DSN or local data configuration,
4. truthful behavior in workbench-facing surfaces or documented non-participation.

## Implementation Slices

### Slice 1: RFC approval and baseline diagnostics

1. Approve this RFC.
2. Record current endpoint and panel failures.
3. Confirm canonical portfolio and benchmark IDs.
4. Confirm required demo as-of date and date window.
5. Confirm which panels are supported versus intentionally partial.

Exit criteria:

1. approved scope,
2. baseline failure list,
3. no cross-repo implementation started before approval.

### Slice 2: Canonical Docker and ingress cleanup path

1. Standardize clean Docker teardown.
2. Remove stale stack and volume ambiguity.
3. Ensure canonical ingress hostnames route only to the active stack.
4. Document cleanup modes and safe rerun behavior.

Exit criteria:

1. no stale containers,
2. no stale Lotus volumes in clean mode,
3. canonical hostnames validated after startup.

### Slice 3: Core seed economics and deterministic smoke data

1. Rebuild `PB_SG_GLOBAL_BAL_001` seed economics.
2. Ensure prices, FX, transactions, and benchmark data cover the demo window.
3. Remove timestamped smoke pollution.
4. Add tests for seed bundle completeness and cleanup behavior.

Exit criteria:

1. no `PORT_SMOKE_%` pollution,
2. seed bundle has coherent transaction and reference coverage,
3. core unit tests cover seed completeness and cleanup.

### Slice 4: Core derived state readiness

1. Make seed verification wait for portfolio and position derived state.
2. Ensure portfolio analytics reference resolves to the intended ready date.
3. Detect slow or stuck asynchronous processing with actionable diagnostics.

Exit criteria:

1. portfolio and position timeseries reach the ready date,
2. analytics reference is current,
3. verification fails fast with useful service attribution when not ready.

### Slice 5: Performance and risk calculation validation

1. Validate performance workspace summary, contribution, and attribution.
2. Validate benchmark-relative behavior.
3. Validate risk snapshot, drawdown, concentration, rolling risk, and historical attribution.
4. Add focused tests where calculations or mappings are weak.

Exit criteria:

1. non-empty supported performance detail rows,
2. non-empty supported risk panel rows,
3. no silent partial state for a supported populated seed.

### Slice 6: Gateway and workbench panel validation

1. Ensure gateway maps current backend data to UI contracts.
2. Ensure all workbench screens and sub-panels show ready, partial, empty, or error states truthfully.
3. Tighten panel smoke automation to catch blank panels.

Exit criteria:

1. workbench validation fails on unsupported blank panels,
2. screenshots are blocked until validation passes,
3. gateway partial failures identify owning services correctly.

### Slice 7: Demo screenshot automation

1. Standardize screenshot file names.
2. Capture all relevant product surfaces.
3. Store artifacts in the requested output directory.
4. Write a run summary with endpoint and panel validation evidence.

Exit criteria:

1. screenshots are clean and populated,
2. run summary records the seed ID, benchmark ID, routes, and validation status.

### Slice 8: Documentation, agent context, and branch hygiene

1. Update runbooks and onboarding docs.
2. Update agent context with the governed path.
3. Remove stale scripts and stale references.
4. Keep commits small and meaningful.
5. Open PRs only after each repository has truthful local evidence.

Exit criteria:

1. future agents know the governed path,
2. stale paths are removed,
3. PR evidence lists real commands and real outcomes.

## Acceptance Criteria

This RFC is complete only when:

1. a clean Docker run can start the canonical stack from zero local state,
2. `PB_SG_GLOBAL_BAL_001` is seeded deterministically,
3. the canonical benchmark is linked and fully usable for the demo window,
4. backend validation passes for all required services,
5. workbench panel validation passes,
6. screenshots are captured after readiness is proven,
7. no stale smoke portfolios are created,
8. documentation and agent context point to the governed path,
9. all changed repositories have meaningful tests,
10. CI and PR evidence are truthful.

## Risks and Mitigations

1. Risk: the seed becomes too large and slow.
   Mitigation: keep one canonical balanced portfolio with enough coverage, not a full production dataset.

2. Risk: UI screenshots become the goal instead of backend correctness.
   Mitigation: block screenshots until backend and panel validation pass.

3. Risk: demo-specific behavior pollutes production code.
   Mitigation: keep demo seed tooling explicit and isolated; do not add UI-only fake behavior.

4. Risk: async core processing makes readiness nondeterministic.
   Mitigation: add explicit derived-state readiness checks and diagnostics.

5. Risk: optional services cause noisy partial failures.
   Mitigation: standardize DSN/local backend configuration or document governed partial behavior.

## Open Questions

1. Should the canonical demo as-of date be fixed at a stable date or derived from the current local date?
2. Should `lotus-manage` use a local SQL DSN in the canonical demo flow or an in-memory supportability backend?
3. Which evidence surfaces are currently contract-supported versus future product scope?
4. Should screenshots include only workbench product surfaces, or also service health/observability surfaces for demo preparation?

## Approval Request

Approval is requested to pause ad hoc seed and screenshot fixes and implement this systematically as the next governed platform workstream.

After approval, implementation should proceed slice by slice. Each slice must be reviewed before moving to the next slice.
