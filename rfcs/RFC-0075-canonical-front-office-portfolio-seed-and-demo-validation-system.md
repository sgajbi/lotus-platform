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

The proposed target state is a production-grade local proving ground, not a marketing fixture. The seed must be suitable for engineering validation, regression detection, release evidence, and client-facing demos. Any panel that looks populated must be backed by supported backend functionality. Any panel that is not supported must render a truthful partial, unavailable, or empty state with clear service ownership.

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

## Proposed Decisions Requiring Approval

This RFC asks for explicit approval on the following implementation decisions before cross-repo work starts:

1. `PB_SG_GLOBAL_BAL_001` remains the single canonical front-office demo and QA portfolio.
2. `BMK_PB_GLOBAL_BALANCED_60_40` remains the canonical balanced benchmark.
3. The canonical demo as-of date is fixed, not derived from the wall clock. The initial proposed date is `2026-04-10`, the last business day before this RFC date.
4. Clean demo startup is allowed to remove Lotus Docker containers, local Lotus images, and Lotus/PBWM volumes when the operator chooses the explicit clean mode.
5. Screenshot capture is blocked until backend and UI validation pass or until the operator explicitly requests a diagnostic capture.
6. Unsupported panels must not be faked. They must either be implemented through the owning backend contract or rendered as truthful partial/unavailable states.
7. `lotus-manage`, `lotus-report`, `lotus-advise`, and `lotus-ai` participate in startup and backend health checks even if the current workbench route does not consume every capability.

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

## Current Baseline Observations

This RFC was created after a clean-stack investigation found several concrete failure patterns:

1. repeated `PORT_SMOKE_*` portfolios polluted portfolio lookup because smoke data used timestamped IDs instead of deterministic cleanup-aware identifiers,
2. the canonical portfolio could have current position timeseries while portfolio-level analytics reference still resolved to a stale `performance_end_date`,
3. direct performance workspace calls could return contribution and attribution while gateway-facing workbench details still rendered empty rows, which indicates a mapping or window-resolution gap rather than a pure seed absence,
4. `lotus-manage` could contribute a `DPM_SUPPORTABILITY_POSTGRES_DSN_REQUIRED` partial failure during workbench overview loading,
5. stale Docker projects could continue running beside the canonical stack and make route ownership ambiguous.

These observations are baseline evidence. They do not authorize local hacks. Each must be resolved in the owning repository and covered by durable validation.

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

## Quality Bar

The RFC is successful only if it improves platform reliability, not just demo appearance.

Required quality attributes:

1. deterministic from a clean machine and clean Docker state,
2. idempotent when rerun against an existing local environment,
3. explicit about every mutation it performs,
4. auditable through machine-readable validation evidence,
5. backed by meaningful tests in changed repositories,
6. safe for developer machines through opt-in destructive cleanup,
7. domain-correct in portfolio economics and terminology,
8. fast enough for regular developer use with heavier checks available on demand,
9. aligned with RFC-0071 ingress and RFC-0072 validation lanes,
10. maintained as platform infrastructure, not prompt-local tribal knowledge.

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

## Design Constraints

1. The seed may be synthetic, but the calculations must use normal product code paths.
2. The canonical flow must use canonical hostnames for end-to-end validation.
3. Direct service-local calls are allowed only for diagnostics, readiness checks, or owning-repository tests.
4. Data cleanup must be scoped to canonical demo artifacts unless the operator explicitly requests full Docker cleanup.
5. The seed must not create open-ended data drift based on the current date.
6. Every timestamped or random smoke artifact must either be removed or replaced with deterministic identifiers.
7. Any implementation shortcut must be recorded as a gap, not hidden behind a green demo.

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

The canonical seed date policy will be fixed-date by default. This prevents new-machine and future-date drift from turning a deterministic demo into a moving target. If a rolling-date demo is ever required, it must be added as a separate explicit mode with its own validation evidence.

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

The seed must be sized as a compact institutional portfolio, not a toy fixture. It should be large enough to exercise diversification, issuer concentration, benchmark-relative analytics, multi-currency behavior, and cashflow paths without becoming a large production-like dataset that slows every developer run.

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

Transaction economics must observe these invariants:

1. security buys reduce the relevant cash account through linked cash movements or a documented settlement model,
2. security sells increase the relevant cash account,
3. income events increase cash net of withholding or fees where applicable,
4. advisory fees and withdrawals reduce cash,
5. cash balances must remain plausible for the stated mandate unless a documented overdraft or leverage scenario exists,
6. positions must not appear only on acquisition day if the instrument remains held,
7. average and period returns must not be dominated by accidental sign errors in cash or market value handling,
8. transaction IDs, source record IDs, and economic event IDs must be deterministic.

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

Reference data must be complete enough to support the domain vocabulary expected by front-office users:

1. private banking portfolio metadata,
2. issuer and ultimate parent identifiers,
3. asset class, sector, country of risk, currency, liquidity tier, rating, and maturity where relevant,
4. benchmark component asset classes that align with performance and risk groupings,
5. stable display names suitable for screenshots and demos.

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

Readiness must be evaluated against the fixed canonical demo as-of date. A seed run must not pass by silently falling back to a stale earlier performance window if current derived state is missing.

### Panel support policy

Every workbench panel must be classified before implementation as one of:

1. supported and must be populated,
2. supported but legitimately empty for the scenario,
3. partial with a known owning-service limitation,
4. unavailable because no backend contract currently supports it,
5. out of scope for the current demo route.

Only the first two categories are allowed to appear as normal populated or empty product surfaces. Partial and unavailable panels must show explicit capability posture. Out-of-scope panels must not be included in demo success criteria.

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

The run summary must include:

1. command line and mode,
2. Git repository revisions where available,
3. canonical portfolio ID,
4. canonical benchmark ID,
5. demo as-of date,
6. services started,
7. Docker cleanup scope,
8. backend validation results,
9. UI panel validation results,
10. screenshot artifact paths,
11. warnings and governed partial states.

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

Backend validation must also record enough numeric evidence to make regressions visible:

1. total positions,
2. valued positions,
3. total transactions,
4. cash account count,
5. position timeseries min and max date,
6. portfolio timeseries min and max date,
7. benchmark return min and max date,
8. performance contribution row count,
9. performance attribution row count,
10. risk rolling window count,
11. risk historical attribution contributor count.

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

UI validation must check sub-screens and panels, not only the top-level route. A successful page load with empty sub-panels is a failure unless the panel is explicitly classified as intentionally empty, partial, unavailable, or out of scope.

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

Diagnostic screenshots captured before validation passes must use a `diagnostic-` prefix and must not be presented as demo-ready evidence.

## Repository Responsibilities

### `lotus-platform`

Owns:

1. canonical runbook,
2. cross-repo orchestration entrypoint,
3. ingress and DSN setup documentation,
4. validation profile definitions,
5. agent context updates,
6. demo evidence artifact conventions,
7. central registration of this governed demo path in engineering context and onboarding docs after implementation.

### `lotus-core`

Owns:

1. canonical portfolio seed bundle,
2. cleanup semantics,
3. deterministic smoke seed behavior,
4. transaction and reference data correctness,
5. derived state readiness checks,
6. tests for seed completeness and stale data cleanup,
7. protection against stale performance reference dates when current position and portfolio derived state should be available.

### `lotus-performance`

Owns:

1. performance workspace correctness,
2. contribution and attribution calculation readiness,
3. benchmark-linked behavior,
4. error reporting when seed economics are invalid,
5. tests that detect empty contribution or attribution detail for the canonical seed when the contract says it is supported.

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
4. no stale report windows when current backend data is available,
5. panel-level contract tests for canonical performance and risk details.

### `lotus-workbench`

Owns:

1. canonical UI startup and validation scripts,
2. panel readiness checks,
3. screenshot capture,
4. no visual empty panels for supported populated contracts,
5. truthful partial and unavailable states,
6. browser validation that proves sub-panels are populated or truthfully classified.

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
4. Confirm fixed demo as-of date and date window.
5. Confirm which panels are supported versus intentionally partial.
6. Confirm allowed Docker cleanup scope.
7. Confirm DSN policy for optional services.

Exit criteria:

1. approved scope,
2. baseline failure list,
3. explicit implementation decisions recorded,
4. no cross-repo implementation started before approval.

### Slice 2: Canonical Docker and ingress cleanup path

1. Standardize clean Docker teardown.
2. Remove stale stack and volume ambiguity.
3. Ensure canonical ingress hostnames route only to the active stack.
4. Document cleanup modes and safe rerun behavior.
5. Add a post-clean assertion that no stale Lotus containers, images, or volumes remain when full clean mode is selected.

Exit criteria:

1. no stale containers,
2. no stale Lotus volumes in clean mode,
3. no stale local Lotus images in full clean mode,
4. canonical hostnames validated after startup.

### Slice 3: Core seed economics and deterministic smoke data

1. Rebuild `PB_SG_GLOBAL_BAL_001` seed economics.
2. Ensure prices, FX, transactions, and benchmark data cover the demo window.
3. Remove timestamped smoke pollution.
4. Add tests for seed bundle completeness and cleanup behavior.
5. Add data-quality assertions for transaction/cash sign conventions and date coverage.

Exit criteria:

1. no `PORT_SMOKE_%` pollution,
2. seed bundle has coherent transaction and reference coverage,
3. seed bundle has plausible portfolio economics,
4. core unit tests cover seed completeness and cleanup.

### Slice 4: Core derived state readiness

1. Make seed verification wait for portfolio and position derived state.
2. Ensure portfolio analytics reference resolves to the intended ready date.
3. Detect slow or stuck asynchronous processing with actionable diagnostics.
4. Include direct database or canonical API evidence in the run summary.

Exit criteria:

1. portfolio and position timeseries reach the ready date,
2. analytics reference is current,
3. verification fails fast with useful service attribution when not ready,
4. derived-state readiness is covered by focused tests.

### Slice 5: Performance and risk calculation validation

1. Validate performance workspace summary, contribution, and attribution.
2. Validate benchmark-relative behavior.
3. Validate risk snapshot, drawdown, concentration, rolling risk, and historical attribution.
4. Add focused tests where calculations or mappings are weak.
5. Verify numeric sanity ranges and row counts rather than only presence.

Exit criteria:

1. non-empty supported performance detail rows,
2. non-empty supported risk panel rows,
3. no silent partial state for a supported populated seed,
4. calculation validation emits machine-readable evidence.

### Slice 6: Gateway and workbench panel validation

1. Ensure gateway maps current backend data to UI contracts.
2. Ensure all workbench screens and sub-panels show ready, partial, empty, or error states truthfully.
3. Tighten panel smoke automation to catch blank panels.
4. Prevent screenshots from being marked demo-ready if panel validation fails.

Exit criteria:

1. workbench validation fails on unsupported blank panels,
2. screenshots are blocked until validation passes,
3. gateway partial failures identify owning services correctly,
4. browser evidence covers the relevant sub-screens.

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
10. CI and PR evidence are truthful,
11. a clean run produces a machine-readable validation summary,
12. demo-ready screenshots are produced only after validation passes,
13. any remaining partial or unavailable panel has explicit product and service ownership.

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

6. Risk: a fixed demo date eventually feels stale in demos.
   Mitigation: use the fixed date for deterministic validation and add a separately approved rolling-date mode only after the fixed path is stable.

7. Risk: validating every panel makes the developer loop too heavy.
   Mitigation: provide fast backend smoke, panel smoke, and full demo evidence modes as separate lanes.

8. Risk: canonical data becomes a second business domain model.
   Mitigation: keep the seed compact, documented, and owned by normal domain services rather than a parallel fixture framework.

## Open Questions

1. Confirm whether the proposed fixed demo as-of date `2026-04-10` is approved.
2. Confirm whether `lotus-manage` should use a local SQL DSN in the canonical demo flow or an in-memory supportability backend.
3. Confirm which evidence surfaces are currently contract-supported versus future product scope.
4. Confirm whether screenshots should include only workbench product surfaces, or also service health/observability surfaces for demo preparation.
5. Confirm whether full Docker cleanup may remove all local Lotus images by default in clean demo mode, or only when an additional force flag is supplied.

## Approval Request

Approval is requested to pause ad hoc seed and screenshot fixes and implement this systematically as the next governed platform workstream.

After approval, implementation should proceed slice by slice. Each slice must be reviewed before moving to the next slice.
