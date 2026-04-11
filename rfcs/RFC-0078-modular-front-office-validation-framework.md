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
product surfaces. RFC-0076 then governed the seeded dataset, and RFC-0077 governed the panel
surface. The current live validator now carries meaningful value, but too much responsibility still
resides in one large script.

Lotus should treat front-office validation as governed product infrastructure rather than an
organically growing script. This RFC proposes a modular validation framework with stable operator
commands, clear internal boundaries, registry-aware panel classification, and deterministic
machine-readable evidence.

## Problem

The current validation flow works, but it is not yet at the correct architectural standard.

Current risks:

1. one script owns argument parsing, DNS checks, gateway probes, analytics checks, panel
   classification, browser flow, screenshot capture, and artifact writing,
2. new panel or route coverage increases complexity in one place,
3. calculation validation and browser validation are not cleanly separated,
4. failures are harder to attribute to infrastructure, contract, dataset, analytics, or UI layers,
5. reuse across future Lotus product surfaces is limited,
6. future agents are more likely to patch a monolith than extend governed reusable modules,
7. dead helper code and route-local assumptions are more likely to survive inside a large script.

This is manageable in the short term but is the wrong long-term pattern for a governed banking-grade
validation system.

## Decision

Lotus will refactor the current front-office validator into a modular framework while preserving the
existing operator-facing commands and governed runtime path.

The framework will:

1. keep `lotus-workbench` as the runtime owner for front-office live validation,
2. preserve current command entrypoints so operators and automation do not relearn the flow,
3. split infrastructure, API, analytics, panel, browser, screenshot, and evidence responsibilities
   into explicit modules,
4. consume the RFC-0076 canonical data contract and the RFC-0077 panel registry as durable
   metadata authorities,
5. produce deterministic machine-readable outputs that clearly attribute failures to the correct
   validation layer.

## Goals

1. Break the canonical front-office validator into small, composable modules.
2. Preserve the current operator-facing commands and documentation entrypoints.
3. Separate infrastructure, API, analytics, panel, browser, and evidence concerns.
4. Keep validation output deterministic and machine-readable.
5. Make panel classification consume RFC-0077 registry concepts rather than route-local drift.
6. Make failure ownership explicit.
7. Improve testability and maintainability.
8. Prepare the framework for additional Lotus product surfaces beyond the current Workbench flow.

## Non-Goals

1. Replacing Playwright or browser automation.
2. Replacing repo-local unit or integration tests.
3. Building a generic framework disconnected from Lotus domain needs.
4. Moving runtime ownership away from `lotus-workbench`.
5. Making screenshot generation optional for demo-validation runs.
6. Rewriting the canonical runtime flow or seed contract owned by RFC-0076.

## Scope

This RFC governs the validation framework behind the existing canonical runtime flow:

```text
lotus-workbench/scripts/live/Start-LotusFrontOfficeCanonical.ps1
lotus-workbench/scripts/live/Validate-LotusFrontOfficeCanonical.ps1
lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1
```

The first implementation scope is the current governed front-office Workbench surface:

1. portfolio summary,
2. portfolio detailed,
3. performance summary,
4. performance analysis,
5. performance advisor brief,
6. performance risk,
7. performance evidence.

## Operator Stability Rule

The operator interface is part of the product contract.

The following must remain stable unless an explicitly approved migration is documented:

1. `npm run live:stack:up`
2. `npm run live:validate`
3. `npm run live:stack:down`
4. `powershell -ExecutionPolicy Bypass -File scripts/live/Validate-LotusFrontOfficeCanonical.ps1`
5. `powershell -ExecutionPolicy Bypass -File lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1`

Internal module refactors must not force operators, demos, or platform automation to change their
entrypoint usage unless there is a justified and documented benefit.

## Proposed Architecture

The Node validation layer should be refactored into small modules under a governed validation
package, for example:

```text
lotus-workbench/scripts/live/validation/
  args.mjs
  contract-metadata.mjs
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

The final module layout may differ slightly, but module boundaries should remain consistent with the
responsibilities defined below.

## Module Responsibilities

### `args.mjs`

1. parse CLI flags,
2. validate required inputs,
3. normalize output directories and runtime options.

### `contract-metadata.mjs`

1. load RFC-0076 canonical contract metadata,
2. load RFC-0077 panel registry metadata,
3. provide deterministic fallback behavior when platform artifacts are unavailable,
4. keep contract loading separate from browser and API logic.

### `dns-checks.mjs`

1. validate canonical hostnames,
2. validate ingress reachability,
3. return explicit infrastructure readiness results.

### `endpoint-probes.mjs`

1. probe health and readiness endpoints,
2. enforce timeout and retry policy,
3. return normalized service availability evidence.

### `gateway-api-checks.mjs`

1. validate core gateway portfolio metadata,
2. validate benchmark linkage,
3. validate supported product contracts for Workbench routes.

### `performance-calculation-checks.mjs`

1. validate summary availability,
2. validate analysis route readiness,
3. validate advisor brief support,
4. validate evidence route contract posture.

### `risk-calculation-checks.mjs`

1. validate risk snapshot support,
2. validate drawdown,
3. validate concentration,
4. validate rolling risk,
5. validate historical risk attribution.

### `panel-classification.mjs`

1. map backend and browser evidence into RFC-0077 registry-driven panel states,
2. assign `ready`, `partial`, `empty`, `unavailable`, `error`, or other governed states,
3. attach rationale and owner metadata,
4. fail on supportability drift between runtime evidence and registry expectations.

### `browser-panel-checks.mjs`

1. navigate routes,
2. assert visible panel surfaces,
3. validate panel-specific UI evidence against the registry,
4. return structured browser observations rather than free-form strings.

### `screenshot-capture.mjs`

1. create deterministic screenshot file names,
2. attach route and panel metadata,
3. preserve current artifact naming unless a documented migration is approved,
4. support future alternative capture modes without changing validation semantics.

### `evidence-summary-writer.mjs`

1. write `live-validation-summary.json`,
2. write `SHOT-INDEX.md`,
3. emit a stable schema for downstream tooling and demo packaging.

### `validation-runner.mjs`

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
7. Refactoring must reduce complexity, not redistribute it.
8. Dead code should be removed as modules are extracted; do not preserve obsolete helpers in the
   name of “safety”.

## Proposed Output Model

The summary schema should distinguish:

1. environment readiness,
2. service reachability,
3. dataset readiness,
4. route readiness,
5. panel readiness,
6. screenshot artifacts,
7. validation failures,
8. known partial or unavailable states,
9. contract provenance.

This should allow operators and future agents to answer:

1. Did the stack come up correctly?
2. Is the canonical portfolio ready?
3. Which route failed?
4. Which panel failed?
5. Is the issue infrastructure, contract, data, analytics, or UI?
6. Which screenshot corresponds to which route or panel?
7. Which governed contract version backed the run?

## Ownership and Boundary Rules

1. `lotus-workbench` owns the live validation runtime implementation and browser proof path.
2. `lotus-platform` owns cross-repo governance, operator automation, and the contract expectations
   around validation evidence.
3. `lotus-gateway` owns truthful route and contract composition.
4. `lotus-core`, `lotus-performance`, and `lotus-risk` own whether the underlying dataset and
   analytics can support `ready` states.
5. Modules must not hide ownership drift by collapsing all failures into generic validation errors.

## Testing Requirements

The refactor must increase test quality, not just move code around.

Required testing layers:

1. unit tests for each module,
2. contract tests for summary schema and screenshot metadata,
3. integration tests for registry-driven panel classification,
4. smoke tests proving operator commands still work unchanged,
5. regression tests for known degraded-state behavior such as `performance.evidence`.

The implementation should add tests before or alongside extraction work so the refactor remains
truthful and safe.

## Documentation Requirements

The following docs should be updated only where the modular framework materially improves guidance:

1. `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`
2. `lotus-platform/automation/README.md`
3. `lotus-platform/docs/onboarding/LOTUS-AGENT-RAMP-UP.md`
4. relevant skills or agent guidance only if the modular validator changes routing decisions or
   operational commands.

## Proposed Implementation Slices

### Slice 1: Extract Core Validation Types and Result Models

1. define shared result models,
2. extract argument handling and summary-writing contracts,
3. add unit tests for the shared contract layer,
4. document the contract boundary and review whether any extracted helper is still too coupled.

### Slice 2: Extract Infrastructure and Gateway Validation

1. move DNS, ingress, service readiness, and gateway probes into dedicated modules,
2. preserve exact validation semantics,
3. add targeted unit and integration tests,
4. remove obsolete helpers and duplicated fetch/timeout logic.

### Slice 3: Extract Performance and Risk Calculation Validation

1. isolate analytics validation from browser checks,
2. define clear outputs for downstream panel classification,
3. add regression tests around canonical portfolio expectations,
4. review module boundaries so domain logic does not leak back into the runner.

### Slice 4: Extract Browser Validation and Screenshot Capture

1. move browser route checks into route-aware modules,
2. separate screenshot metadata generation from route navigation,
3. keep artifact naming stable or provide a documented migration,
4. remove stale route-local screenshot metadata made obsolete by the extracted modules.

### Slice 5: Registry-Driven Panel Classification

1. align validation with RFC-0077 registry concepts,
2. remove avoidable hardcoded panel-state logic,
3. add contract tests for state classification,
4. fail when registry expectations and runtime supportability diverge.

### Slice 6: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

1. remove obsolete helpers and dead code,
2. tighten naming and module boundaries,
3. update documentation, examples, and front-office runtime guidance,
4. review whether existing skills need explicit references to the modular validator or should stay
   linked through runbooks only,
5. document conscious no-change decisions where skill or context updates are not needed,
6. prove the framework with the canonical runtime flow,
7. complete branch hygiene, PR evidence hygiene, and cross-repo reference cleanup before closure.

## Acceptance Criteria

1. The canonical validation commands remain operator-stable.
2. The live validator is split into small, readable modules with clear ownership.
3. Validation output remains truthful and machine-readable.
4. Test coverage materially improves for validation logic.
5. Browser and calculation validation are clearly separated.
6. The framework is registry-aware and ready for future panel growth.
7. Dead code from the prior monolith is removed.
8. Final docs and skills reflect the new modular runtime only where materially useful.

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

### Risk: Modules become thin wrappers around unchanged monolith logic

Mitigation:

1. require dead-code removal and helper consolidation in each slice,
2. review readability after every slice,
3. fail the slice if extraction only relocates complexity without clarifying ownership.

## Skills, Context, and Documentation Implications

Potential updates during the final slice:

1. update front-office runtime guidance if the internal modular validator changes how operators or
   agents inspect failures,
2. update only the skills that materially benefit from knowing the new module structure,
3. avoid copying internal module inventories into multiple docs when the runbook already points to
   the implementation,
4. document any conscious no-change decision for skills or context.

## Approval Request

Approve this RFC if Lotus should treat front-office validation as governed product infrastructure
with modular internal boundaries rather than allowing the current validator to keep growing as an
organically evolving script.
