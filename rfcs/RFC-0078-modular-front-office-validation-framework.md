# RFC-0078: Modular Front-Office Validation Framework

- Status: Proposed
- Date: 2026-04-11
- Owners: lotus-platform governance
- Requires Approval From:
  - lotus-platform maintainers
  - lotus-workbench maintainers
  - lotus-gateway maintainers
  - lotus-core maintainers
  - lotus-performance maintainers
  - lotus-risk maintainers
- Related:
  - `RFC-0057-test-pyramid-and-meaningful-coverage-governance.md`
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
  - `RFC-0074-repeatable-developer-and-agent-bootstrap-system.md`
  - `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
  - `RFC-0076-canonical-front-office-demo-data-contract.md`
  - `RFC-0077-workbench-panel-registry-and-evidence-contract.md`

## Summary

RFC-0075 established a live validation flow for the canonical front-office runtime and Workbench
product surfaces. The current validator is high-value, but too much responsibility now sits in one
script.

This RFC proposes a modular front-office validation framework with stable operator commands and
clear internal boundaries for DNS checks, service readiness, API validation, analytics validation,
panel classification, browser verification, screenshot capture, and evidence writing.

## Problem

The current validation flow is useful but not yet gold standard:

1. one script is responsible for argument parsing, API checks, browser checks, screenshot capture,
   summary classification, and artifact writing,
2. new panels and checks increase complexity in one place,
3. calculation validation and browser validation are not cleanly separated,
4. reuse across other UIs or future panel sets is limited,
5. failures are harder to attribute to the owning validation layer,
6. future agents are more likely to patch the monolith than extend reusable modules.

This is manageable today, but it is the wrong long-term pattern for a governed validation system.

## Goals

1. Break the canonical front-office validator into small, composable modules.
2. Preserve the current operator-facing commands and documentation entrypoints.
3. Separate infrastructure, API, analytics, panel, and browser concerns.
4. Make validation output deterministic and machine-readable.
5. Enable registry-driven validation where possible.
6. Make failure ownership explicit.
7. Improve testability and maintainability.
8. Prepare the framework for additional Lotus product surfaces beyond the current Workbench flow.

## Non-Goals

1. Replacing Playwright or browser automation.
2. Replacing repo-local unit or integration tests.
3. Building a generic framework disconnected from Lotus domain needs.
4. Moving runtime ownership from `lotus-workbench`.
5. Making screenshot generation optional for demo-validation runs.

## Proposed Architecture

The existing runtime entrypoints remain stable:

```text
lotus-workbench/scripts/live/Start-LotusFrontOfficeCanonical.ps1
lotus-workbench/scripts/live/Validate-LotusFrontOfficeCanonical.ps1
lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1
```

The Node validation layer should be refactored into modules, for example:

```text
lotus-workbench/scripts/live/validation/
  args.mjs
  dns-checks.mjs
  endpoint-probes.mjs
  gateway-api-checks.mjs
  performance-calculation-checks.mjs
  risk-calculation-checks.mjs
  panel-classification.mjs
  browser-panel-checks.mjs
  screenshot-capture.mjs
  evidence-summary-writer.mjs
  validation-runner.mjs
```

### Module Responsibilities

#### `args.mjs`

1. parse CLI flags,
2. validate required inputs,
3. normalize output directories and runtime options.

#### `dns-checks.mjs`

1. validate canonical hostnames,
2. validate ingress reachability,
3. return explicit infrastructure readiness results.

#### `endpoint-probes.mjs`

1. probe health and readiness endpoints,
2. enforce timeout and retry policy,
3. return normalized service availability evidence.

#### `gateway-api-checks.mjs`

1. validate core gateway portfolio metadata,
2. validate benchmark linkage,
3. validate supported product contracts for Workbench routes.

#### `performance-calculation-checks.mjs`

1. validate summary availability,
2. validate analysis route readiness,
3. validate advisor brief support,
4. validate evidence route contract state.

#### `risk-calculation-checks.mjs`

1. validate risk snapshot support,
2. validate drawdown,
3. validate concentration,
4. validate rolling risk,
5. validate historical risk attribution.

#### `panel-classification.mjs`

1. map backend and browser evidence into registry-driven panel states,
2. assign `ready`, `partial`, `empty`, `unavailable`, `error`, or other governed states,
3. attach rationale and owner metadata.

#### `browser-panel-checks.mjs`

1. navigate routes,
2. assert visible panel surfaces,
3. validate panel-specific UI evidence against the registry,
4. return structured browser observations instead of free-form strings.

#### `screenshot-capture.mjs`

1. create deterministic screenshot file names,
2. attach route and panel metadata,
3. support future alternative capture modes without changing validation semantics.

#### `evidence-summary-writer.mjs`

1. write `live-validation-summary.json`,
2. write `SHOT-INDEX.md`,
3. emit a stable schema for downstream tooling and demo packaging.

#### `validation-runner.mjs`

1. orchestrate the validation flow,
2. aggregate module output,
3. determine overall pass/fail state,
4. avoid embedding business logic that belongs in lower layers.

## Design Principles

1. Operator commands stay stable.
2. Validation layers are composable and independently testable.
3. Module outputs are typed and machine-readable.
4. Browser checks consume panel registry definitions rather than route-local hardcoding where
   possible.
5. Failures must point to the correct owner domain.
6. Shared helpers must stay domain-aware; this is a Lotus validator, not a generic framework.

## Proposed Output Model

The summary schema should distinguish:

1. environment readiness,
2. service reachability,
3. dataset readiness,
4. route readiness,
5. panel readiness,
6. screenshot artifacts,
7. validation failures,
8. known partial states.

This should allow operators and future agents to answer:

1. Did the stack come up correctly?
2. Is the canonical portfolio ready?
3. Which route failed?
4. Which panel failed?
5. Is the issue infrastructure, contract, data, or UI?
6. Which screenshot corresponds to which route or panel?

## Testing Requirements

The refactor must increase test quality, not just move code around.

Required testing layers:

1. unit tests for each module,
2. contract tests for summary schema and screenshot metadata,
3. integration tests for registry-driven panel classification,
4. smoke tests proving operator commands still work unchanged,
5. regression tests for known partial-state behavior such as `performance.evidence`.

## Documentation Requirements

The following docs must be updated:

1. `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`
2. `lotus-platform/automation/README.md`
3. `lotus-platform/docs/onboarding/LOTUS-AGENT-RAMP-UP.md`
4. any skill or agent guidance that references the governed runtime and validation path.

## Proposed Implementation Slices

### Slice 1: Extract Core Validation Types and Result Models

1. define shared result models,
2. extract argument handling and summary-writing contracts,
3. add unit tests for the shared contract layer.

### Slice 2: Extract Infrastructure and Gateway Validation

1. move DNS, ingress, service readiness, and gateway probes into dedicated modules,
2. preserve exact validation semantics,
3. add targeted unit and integration tests.

### Slice 3: Extract Performance and Risk Calculation Validation

1. isolate analytics validation from browser checks,
2. define clear outputs for downstream panel classification,
3. add regression tests around canonical portfolio expectations.

### Slice 4: Extract Browser Validation and Screenshot Capture

1. move browser route checks into route-aware modules,
2. separate screenshot metadata generation from route navigation,
3. keep artifact naming stable or provide documented migration.

### Slice 5: Registry-Driven Panel Classification

1. align validation with RFC-0077 registry concepts,
2. remove avoidable hardcoded panel-state logic,
3. add contract tests for state classification.

### Slice 6: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

1. remove obsolete helpers and dead code,
2. tighten naming and module boundaries,
3. update documentation, examples, and front-office runtime guidance,
4. review whether existing skills need explicit references to the modular validator or should stay
   linked through runbooks only,
5. prove the framework with the canonical runtime flow,
6. complete branch hygiene, PR evidence hygiene, and cross-repo reference cleanup before closure.

## Acceptance Criteria

1. The canonical validation commands remain operator-stable.
2. The live validator is split into small, readable modules with clear ownership.
3. Validation output remains truthful and machine-readable.
4. Test coverage materially improves for validation logic.
5. Browser and calculation validation are clearly separated.
6. The framework is ready for registry-driven panel validation.
7. Dead code from the prior monolith is removed.

## Risks and Mitigations

### Risk: Refactor introduces validation regressions

Mitigation:

1. keep commands stable,
2. add contract tests before larger internal changes,
3. validate against the current canonical stack before merge.

### Risk: Over-engineering

Mitigation:

1. optimize for Lotus product needs,
2. avoid generic abstractions without current use,
3. maintain direct ownership and readable module boundaries.

## Approval Request

Approve this RFC if Lotus should treat front-office validation as governed product infrastructure
rather than an organically growing script.
