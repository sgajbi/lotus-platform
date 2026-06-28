# Lotus Enterprise Backend Refactoring Instructions

Use this file as the detailed refactoring instruction pack for any Lotus backend application.

The Codex Goal prompt must name the target application and instruct the agent to follow this file fully.

This instruction pack is application-independent. Apply it to the named target app only.

---

# 0. Required Lotus References

Before substantial refactoring work, load the smallest correct set of references:

- `AGENTS.md`
- `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`
- `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
- the target repository's `REPOSITORY-ENGINEERING-CONTEXT.md`
- `lotus-platform/context/CONTEXT-REFERENCE-MAP.md`
- `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md`
- `lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`
- `lotus-platform/context/LOTUS-SKILL-ROUTING-MAP.md` when skill choice matters
- `lotus-platform/docs/standards/Lotus Data Mesh Standard.md` when data products, trust telemetry, lineage, access policy, SLO policy, or evidence packs are touched
- `lotus-platform/docs/standards/Lotus Client Demo Certification Standard.md` when demo claims, client-facing material, screenshots, or sales/marketing proof are touched
- `lotus-platform/docs/onboarding/LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md` when changing scaffolded service structure, generated gates, or generated docs

Use the right Lotus skill for the task. In particular:

- use `lotus-ci-enforcement-governance` for quality gates, CI lane placement, scaffold guardrails, and anti-slop enforcement,
- use `lotus-backend-delivery-governance` for backend implementation and architecture refactoring,
- use `lotus-readme-wiki-governance` for README, wiki, demo, operator, and audience-aware documentation changes,
- use `lotus-pr-premerge-gate` before push, PR update, merge, or branch cleanup,
- use `lotus-rfc-review-loop` for RFC structure, source maps, implementation ledgers, and closure truth.

Do not create a new skill unless the workflow is durable, recurring, and not already covered by an existing Lotus skill. If a new or changed skill is justified, update the platform-owned skill source, skill manifest, routing map, central context, and bootstrap/sync evidence in the same slice.

---

# 1. Mission

Refactor the target Lotus backend application into a modular, reusable, maintainable, performant, secure, observable, enterprise-grade, production-ready, bank-buyable backend application.

The goal is not cosmetic cleanup.

The goal is to make the application:

- easier to understand
- safer to change
- easier to test
- easier to operate
- easier to support in production
- easier to explain to developers, business users, operations, sales, and enterprise clients
- suitable for enterprise adoption and long-term maintainability

The application must align with:

- Lotus platform governance
- API governance
- data mesh standards
- private banking engineering practices
- production support expectations
- secure software delivery practices
- implementation-backed documentation expectations
- Codex-assisted development safety expectations

Refactoring must preserve existing behavior unless a behavior change is intentional, tested, documented, and clearly explained.

---

# 2. Execution Principles

Work on a feature branch.

Use small, meaningful commits.

Target roughly 40 to 60 well-scoped commits for a large refactor program, unless the repository is
too small or too large for that number to make sense. For RFC implementation programs, complete and
merge one proof-backed slice before starting the next slice.

Preserve normal commit history because the final PR will use a non-squash merge strategy.
When the repository disallows merge commits, use the repository-approved linear merge path such as
rebase merge. Do not retry a rejected merge-commit strategy after repository policy is known, and do
not squash unless policy or the owner explicitly requires it.

Each commit should have a clear purpose and should keep the application buildable and testable as much as practical.

Prefer incremental improvement over large rewrites.

Avoid large mechanical rewrites unless they create clear architectural value and are easy to review.

Do not mix unrelated concerns in one commit.
Do not keep many partial RFC slices open at once. If a foundational change touches several future
slices, classify which blockers it actually clears and leave the remaining slices explicitly
blocked, planned, or unpromoted.

Do not perform broad renaming, formatting, folder moves, and business refactoring in the same commit unless unavoidable.

When behavior changes, document:

- what changed
- why it changed
- who or what is impacted
- what tests prove the new behavior
- whether migration or client communication is required

Use the repository's existing conventions where they are good.

Improve conventions where they are weak, inconsistent, unsafe, or not enterprise-ready.

## 2A. RFC Slice Intake And Closure

For RFC-driven application work, write a short slice intake before editing:

- current branch and mainline commit,
- RFC slice or blocker family being targeted,
- exact blocker codes this slice intends to clear,
- exact blocker codes that must intentionally remain,
- source-authority owner for every consumed fact,
- API, OpenAPI, error-model, persistence, data-mesh, Gateway, Workbench, wiki, and
  supported-feature surfaces affected,
- local commands that prove the slice before PR,
- remote GitHub lanes required before merge,
- no-claim boundary: the product, demo, client-publication, production, AI, data-mesh, or
  supported-feature claims this slice still does not support.

Do not continue into the next RFC slice while the current slice is unmerged, its CI evidence is
unknown, wiki publication is pending, or local/remote branch hygiene is unresolved.

---

# 3. Codex Safety Rules

Codex must not optimize for speed over correctness.

Codex must not hide uncertainty.

Codex must not silently remove behavior.

Codex must not delete code only because it looks unused unless evidence supports removal.

Codex must not introduce new dependencies without clear justification.

Codex must not introduce framework, persistence, infrastructure, or transport leakage into domain/application logic.

Codex must not weaken tests to make CI pass.

Codex must not lower quality thresholds to make CI pass without documenting why.

Codex must not replace meaningful business behavior with placeholders, stubs, fake implementations, or TODO-only code.

Codex must not document capabilities that are not implemented.

Codex must not expose secrets, tokens, credentials, client data, internal stack traces, or sensitive data in logs, docs, examples, tests, or error responses.

Codex must not create a large final PR without progressive commits and measurable evidence.

When in doubt, prefer a smaller, safer change with clear evidence.

---

# 4. Refactoring Focus Areas

Improve the application across these areas:

- remove dead code and unused paths
- split monolithic files into clear modules
- reduce duplication across routers, controllers, services, DTOs, mappers, validators, middleware, clients, repositories, tests, and configuration
- improve domain modeling and private banking vocabulary
- improve API design, versioning, routing, pagination, filtering, sorting, and error handling
- complete OpenAPI with summaries, descriptions, examples, tags, operation IDs, request models, response models, and error models
- keep business logic out of routers, controllers, middleware, infrastructure, persistence models, and downstream adapters
- improve service boundaries, dependency flow, orchestration boundaries, and separation of concerns
- strengthen validation, idempotency, correlation IDs, auditability, lineage, and traceability
- improve structured logging, metrics, tracing hooks, health checks, readiness checks, and operational diagnostics
- optimize latency, batching, pagination, caching, connection pooling, timeout handling, retry behavior, and downstream access patterns
- harden security, authentication, authorization, sensitive-data handling, secrets handling, configuration, CORS, secure headers, and API abuse protection
- improve resilience with timeouts, retries, bounded failure behavior, graceful degradation, and consistent downstream error mapping
- improve tests with meaningful unit, integration, contract, API, middleware, security, regression, and end-to-end coverage
- update README, architecture docs, API catalog, RFCs, operational runbooks, supported-features material, and wiki-ready documentation

Prioritize changes that produce measurable improvement and reduce long-term ownership risk.

---

# 5. Architecture Principles

Use clear layered architecture.

Preferred dependency flow:

```text
api / routers / controllers
    -> application / use_cases / services
        -> domain / models / value_objects / policies
        -> ports / interfaces
            <- infrastructure / adapters / clients / repositories
```

Rules:

- routers/controllers call application services or use cases only
- routers/controllers must not call repositories, database clients, HTTP clients, Kafka clients, Redis clients, file clients, or downstream adapters directly
- middleware must stay thin, reusable, and free of business logic
- domain logic must not depend on FastAPI, framework objects, infrastructure clients, persistence models, API DTOs, transport DTOs, or external service response models
- application logic must not depend on FastAPI, framework request objects, persistence models, concrete infrastructure clients, or transport DTOs
- infrastructure must sit behind ports/adapters
- API DTOs must not leak into domain logic
- persistence models must not leak into API responses or domain logic
- downstream response models must not leak into domain logic
- mappers must be explicit and testable
- downstream errors must map to consistent platform errors
- errors should follow RFC 7807/problem-details style where applicable
- every request must support or propagate correlation ID
- relevant mutations must be auditable
- idempotent operations must define explicit idempotency behavior
- logs must be structured and must not leak sensitive data

The core business logic should be testable without FastAPI, real databases, Kafka, Redis, cloud services, or real downstream APIs.

Design modularity is required before runtime modularity. Use packages, domain modules, ports,
adapters, application services, proof builders, and explicit contracts to make responsibilities
clear inside the service. Create a separate deployable microservice only when independent runtime
scaling, deployment cadence, operational ownership, data persistence, failure isolation, or security
boundary needs are proven. Do not split a service just because a module is conceptually important;
first make the in-process boundary clean and enforce it with tests or architecture gates.

For opportunity-intelligence, advisory-orchestration, reporting-orchestration, and other
cross-domain workflow services, harden source ownership before adding breadth. The service may own
its lifecycle state, orchestration decisions, evidence-pack assembly, readiness posture, and
operator workflow, but it must consume portfolio accounting, performance, risk, suitability,
compliance, reporting, archive, render, gateway, AI, and other source-domain truth through governed
contracts, ports, proof artifacts, or live-source APIs. Do not copy source-domain approval logic,
calculation methods, persistence models, or supportability claims into the orchestrating service.
Name modules, APIs, errors, metrics, and proof artifacts after the business responsibility they
actually own.

---

# 6. Layer Responsibilities

## API Layer

Responsible for:

- route definitions
- HTTP method and path
- request DTOs
- response DTOs
- status codes
- headers
- query parameters
- path parameters
- authentication context extraction
- API-level validation
- mapping API DTOs to application commands
- mapping application results to API responses

Not responsible for:

- business decisions
- database access
- downstream HTTP calls
- Kafka publishing
- Redis access
- file access
- complex orchestration
- domain calculations

## Application Layer

Responsible for:

- use case orchestration
- transaction/workflow coordination
- calling domain logic
- calling ports
- coordinating persistence through repository ports
- coordinating downstream access through client ports
- idempotency workflow
- audit workflow
- application-level error mapping

Not responsible for:

- HTTP details
- API DTOs
- persistence schema details
- concrete client implementation
- framework objects

## Domain Layer

Responsible for:

- business models
- value objects
- policies
- business rules
- calculations
- validations
- state transitions
- private banking vocabulary

Not responsible for:

- FastAPI
- Pydantic API DTOs
- SQLAlchemy/ORM models
- database details
- HTTP clients
- Kafka clients
- Redis clients
- file clients
- cloud clients

## Ports

Responsible for:

- defining external capabilities required by the application
- repository interfaces
- downstream client interfaces
- event publisher interfaces
- audit interfaces
- idempotency store interfaces
- clock/UUID/provider interfaces where useful for testability

## Infrastructure

Responsible for:

- concrete repository implementations
- database access
- downstream HTTP clients
- Kafka/EventHub producers/consumers
- Redis/cache clients
- file/cloud storage clients
- external service DTO mapping
- infrastructure-specific error handling
- configuration of concrete adapters

---

# 7. API Governance

Improve APIs so they are consistent, explainable, and enterprise-ready.

Every endpoint should have:

- clear route naming
- consistent versioning
- summary
- description
- tags
- operation ID
- request model
- response model
- useful request examples
- useful response examples
- standard error responses
- documented validation behavior
- documented correlation ID behavior
- documented idempotency behavior where relevant
- documented pagination/filtering/sorting where relevant
- security/authentication declaration where relevant

Standardize:

- pagination
- filtering
- sorting
- error format
- status codes
- versioning
- deprecation strategy
- internal versus public endpoints
- health endpoint
- readiness endpoint
- liveness endpoint
- metrics endpoint
- OpenAPI tag structure
- API examples

Problem-details responses should be consistent.

Typical error shape should include:

- type
- title
- status
- detail
- instance where applicable
- correlation ID
- application error code where useful
- safe contextual metadata where useful

Do not expose internal exception messages, stack traces, downstream raw errors, secrets, credentials, or sensitive client data.

API and error-model polish is part of the refactor, not a final cleanup task. New or changed
business endpoints should expose stable operation IDs, response models, examples, bounded
problem-details responses, application error codes, correlation context, and source-safe diagnostic
metadata before they are treated as implementation-complete.

For orchestrating services, API errors must distinguish local lifecycle failures from source-owned
unavailable, stale, denied, degraded, or not-certified evidence. Do not collapse upstream source
posture into generic local validation errors, and do not expose raw upstream exception text or
source-sensitive identifiers in problem details.

---

# 8. Observability and Operations

Improve operational readiness.

The application should support:

- structured JSON logging
- correlation ID in request logs
- correlation ID in response headers
- correlation ID propagation to downstream calls
- correlation ID propagation to events/messages where applicable
- safe logging without secrets, tokens, credentials, personal data, or client-sensitive data
- request metrics
- latency metrics
- downstream call metrics
- error metrics
- business-operation metrics where useful
- health checks
- readiness checks
- liveness checks
- tracing hooks where practical
- clear operational diagnostics
- meaningful startup behavior
- meaningful shutdown behavior
- timeout visibility
- retry visibility
- dependency health visibility
- runbook documentation

Logs should be useful for production support but must not leak sensitive information.

Operational documentation should explain:

- how to run locally
- how to configure
- how to diagnose failures
- how to interpret health/readiness
- how to trace a request with correlation ID
- what downstream dependencies exist
- what common failures mean
- what alerts or metrics matter

---

# 9. Security

Harden the application.

Check and improve:

- authentication boundaries
- authorization boundaries
- service-to-service trust boundaries
- secrets handling
- environment-based configuration
- safe defaults
- sensitive-data masking
- secure headers where applicable
- CORS policy
- input validation
- output sanitization where relevant
- dependency vulnerabilities
- insecure Python patterns
- unsafe deserialization
- command execution risks
- path traversal risks
- SQL/NoSQL injection risks
- SSRF risks in downstream calls
- downstream error leakage
- logs for sensitive-data exposure
- negative/security test coverage

Do not expose:

- tokens
- secrets
- credentials
- internal stack traces
- raw downstream errors
- sensitive client data
- personal data
- private account information
- full request/response bodies where they may contain sensitive data

New dependencies must be justified and checked for:

- purpose
- license
- maintenance status
- security vulnerabilities
- overlap with existing dependencies
- runtime/container impact

---

# 10. Resilience and Reliability

Improve production resilience.

Check and improve:

- explicit downstream timeouts
- bounded retries
- retry backoff
- no infinite retry loops
- consistent timeout configuration
- consistent error mapping
- graceful degradation where appropriate
- duplicate message handling
- idempotent mutation behavior
- idempotent event processing where applicable
- transaction boundaries
- partial-failure behavior
- startup dependency behavior
- shutdown behavior
- connection pooling
- resource cleanup
- concurrency safety
- race-condition risks
- poison message handling where applicable
- dead-letter behavior where applicable

For idempotent operations, define and test:

- same idempotency key with same payload
- same idempotency key with different payload
- concurrent requests with same key
- operation in progress
- operation completed
- operation failed
- retention/expiry behavior

---

# 11. Testing Expectations

Improve tests so they protect behavior, architecture, and production readiness.

Add or strengthen:

- unit tests for domain logic
- unit tests for value objects
- unit tests for application services/use cases
- integration tests for infrastructure/adapters where practical
- repository tests where practical
- downstream client tests with mocked responses
- contract/API tests
- router/controller tests
- middleware tests
- error-handling tests
- security tests
- regression tests for existing supported features
- health/readiness/liveness tests
- correlation ID propagation tests
- RFC 7807/problem-details tests
- downstream failure tests
- timeout/retry tests
- sensitive-data masking tests
- idempotency tests where relevant
- audit tests where relevant
- OpenAPI generation tests
- architecture boundary tests
- performance smoke tests where practical

Tests should be meaningful, not coverage fillers.

Do not weaken or delete tests to make refactoring easier.

If a test is obsolete, explain why and replace it with a better test.

Use golden regression tests for business-critical calculations and behavior.

For portfolio, performance, buying-power, advisory, or reporting apps, preserve and expand tests around:

- money and Decimal precision
- FX handling
- date/time boundaries
- timezone behavior
- valuation dates
- cashflow timing
- cost calculation
- TWR/MWR/performance calculations where relevant
- contribution/attribution where relevant
- benchmark behavior where relevant
- buying power and collateral behavior where relevant
- idempotency and duplicate event behavior
- backdated or correction events where relevant

---

# 12. Quality Gates and Measurement

Add measurable quality gates so refactoring progress is tangible in CI and PR evidence.

Before major refactoring, create a baseline report covering:

- code size
- module/package count
- largest files
- largest functions
- complexity
- maintainability
- lint issues
- formatting issues
- type-checking issues
- test count
- test-family breadth, including API/runtime, contract/governance, observability/security, and
  uncategorized tests where a repo-native taxonomy exists
- line coverage
- branch coverage
- diff coverage where available
- dead-code candidates
- dependency issues
- security findings
- dependency vulnerability findings
- OpenAPI gaps
- architecture boundary violations
- router/controller complexity
- middleware complexity
- documentation gaps
- observability gaps
- container/deployment gaps where applicable

Create a before/after scorecard and update it during the refactor.

Recommended files:

- `pyproject.toml`
- CI quality workflow
- `.importlinter`
- `.spectral.yaml`
- `quality/baseline_report.md`
- `quality/refactor_health_report.md`
- `quality/quality_scorecard.md`
- `quality/architecture_rules.md`
- `quality/api_governance_rules.md`
- `quality/ci_quality_gates.md`
- `quality/security_findings.md`
- `quality/refactor_decisions.md`

Recommended tools where applicable:

- `ruff` for linting and formatting
- `mypy` or `pyright` for type checking
- `pytest`, `pytest-cov`, and `coverage.py` for tests and coverage
- `diff-cover` for changed-code coverage
- `radon` for complexity and maintainability reporting
- `xenon` for complexity enforcement
- `vulture` for dead-code detection
- `deptry` for dependency hygiene
- `bandit` for Python security scanning
- `pip-audit` or `osv-scanner` for dependency vulnerability scanning
- `spectral` for OpenAPI governance
- `import-linter` or equivalent for architecture boundaries
- `interrogate` for docstring coverage
- optional: `schemathesis` for OpenAPI/property-based API testing
- optional: `pytest-benchmark` for performance checks
- optional: `locust` or `k6` for load/performance testing
- optional: `hadolint`, `trivy`, `grype`, `syft`, or equivalent for container and supply-chain checks

Use progressive CI gating:

1. baseline/report-only checks
2. fail only on new regressions
3. enforce agreed thresholds
4. enforce strict enterprise-readiness gates

Do not make CI weaker to complete the refactor.

When promoting a report-only inventory, use the `lotus-ci-enforcement-governance` intake. A
promotion is valid only when it names the measured baseline artifact, exact failure mode,
repo-native command, intended CI lane, exception policy, pass/fail tests, and scorecard or ledger
update. Do not promote broad metrics such as maintainability index, dead-code percentage, or public
docstring coverage until false positives and remediation policy are stable.

For test inventories, do not rely only on total collected tests. Stable API/runtime,
contract/governance, observability/security, or domain-methodology family counts can be useful
regression gates. It is acceptable to cap uncategorized-test growth while keeping finer taxonomy
maturity report-only, provided the baseline and exception policy are documented.

## 12A. Agentic Quality Gate Pack

For new or heavily refactored Lotus backend services, use the scaffolded `lotus-idea` quality posture as the minimum bar, then improve it when the target repository justifies stricter controls.

The repo-native local surface should include deterministic blocking gates for:

- CI contract drift
- architecture boundary drift
- maintainability thresholds
- documentation surface contracts
- quality-scorecard truth
- monetary precision
- sensitive-content leakage
- source-safe observability
- operation metric vocabulary
- implementation-truth claims
- supported-feature promotion
- endpoint certification
- OpenAPI quality
- migration contracts when persistence exists
- runtime proof contracts when proof artifacts exist
- repository hygiene and safe cleanup

Use `make lint` or the repository's equivalent fast static command to run the anti-slop pack that prevents weak agent-generated code from passing early. Use `make check` or the repository's equivalent PR-grade command for typecheck, unit/integration tests, coverage, contract gates, security, Docker/runtime proof, and migration/runtime checks as applicable.

GitHub Actions lanes should be consumers of that repo-native command surface, not a parallel
validation implementation. Before editing workflows, map each remote step to the local Make/NPM
target that a developer or agent can run. Do not add raw workflow-level `pytest`, direct Python
runner, coverage, or scanner invocations when a repo-native target exists; add or fix the target
first, then call it from the workflow. When a CI contract gate exists, add pass/fail coverage that
proves the gate rejects workflow shortcuts and missing suite-level coverage targets.

Generated or refactored gates must be:

- repo-native,
- worktree-clean,
- focused on concrete engineering risk,
- covered by pass and fail tests,
- documented in README, repo context, quality docs, and wiki source when truth changes.

Do not hide weak implementation behind allowlists, lowered thresholds, or documentation-only optimism. If a gate cannot be made deterministic and low-noise, keep it report-only and record the follow-up in the scorecard or refactor decision log.

## 12B. Bounded Proof Artifact Pattern

When a refactor introduces cross-repository, runtime, data-mesh, downstream, AI, report/render/archive, broker, or product-surface evidence, use bounded proof artifacts instead of vague readiness prose.

A proof artifact must define:

- schema version,
- owning repository,
- generated timestamp with timezone,
- proof type,
- proof scope,
- required evidence references,
- exact routes, contracts, migrations, dashboards, alerts, or runtime commands being proven,
- exact blockers cleared,
- remaining blockers,
- non-proof boundaries,
- source-safety checks,
- validation command,
- focused tests for valid, invalid, missing-evidence, and sensitive-content cases.

The artifact must clear only the blockers it actually proves. For example, a route-foundation proof must not become execution proof; report materialization proof must not become client-publication proof; data-mesh onboarding proof must not become mesh certification; AI workflow-pack registration proof must not become live-provider proof.

Refactoring agents must keep this distinction explicit in code, tests, README, operations docs, wiki source, supported-feature ledgers, RFCs, and PR evidence. This is a core anti-overclaim control for bank-buyable Lotus work.

For opportunity, advisory, reporting, AI, data-mesh, or product-surface RFCs, treat blocker
semantics as the implementation contract. A proof may clear only the exact blocker codes it
validates and must preserve downstream, client-publication, supported-feature, data-mesh
certification, Workbench/Gateway, or live-provider blockers until runtime evidence exists.

Recommended implementation shape:

- application module for proof payload construction and validation,
- generator script that writes ignored `output/` artifacts,
- contract gate script that can run in CI without live dependencies,
- Make target for the contract gate,
- aggregate readiness integration that consumes the proof only when valid,
- tests proving blocker clearance and remaining blockers,
- documentation section with current truth, proof boundary, non-proof boundary, commands, and evidence refs.

Missing sibling evidence may write an invalid non-proof artifact and exit cleanly only when the command is designed for stable local or CI operation without sibling checkouts. Contract drift in present sibling evidence must fail.

Live API tests are valuable when upstreams are available, but they do not replace the test pyramid.
Keep deterministic unit, contract, and adapter tests at the base; add live or canonical API proof as
an explicit higher lane with source-safe output artifacts, stable seed data, bounded credentials,
and clear skip/failure semantics.

---

# 13. Required Evidence After Each Meaningful Refactoring Step

For each meaningful refactoring commit or small group of commits, record evidence in the commit message, PR notes, or `quality/refactor_health_report.md`.

Evidence should include where applicable:

- tests run
- number of tests passed
- focused test suites run
- Ruff lint result
- Ruff format result
- type-check result
- Radon/Xenon complexity result
- before/after complexity for touched hotspots
- coverage or diff coverage result
- dependency check result
- security check result
- OpenAPI/Spectral result
- architecture boundary check result
- known limitations or deferred work

Example evidence format:

```text
Evidence:
- pytest tests/unit/application/test_create_proposal.py: 18 passed
- ruff check src/app/application src/app/domain: passed
- ruff format --check src/app/application src/app/domain: passed
- pyright: passed
- radon: CreateProposalUseCase.execute improved from C (13) to B (7)
- architecture boundary check: passed
```

Evidence must be specific, not generic.

Avoid statements like "all good" or "quality improved" without proof.

---

# 14. Documentation Expectations

Treat documentation as part of the product.

Update or create:

- `README.md`
- `docs/architecture.md`
- `docs/api-governance.md`
- `docs/observability.md`
- `docs/security.md`
- `docs/operations-runbook.md`
- `docs/supported-features.md`
- `docs/configuration.md`
- `docs/local-development.md`
- RFCs where architectural decisions changed
- wiki-ready diagrams and flow descriptions

Documentation should support:

- developers
- business users
- operations
- sales
- client demos
- client pitches
- future maintainers
- production support

Documentation must be implementation-backed.

Do not document capabilities that the code does not support.

Where the application has limitations, document them honestly.

Where the refactor introduces decisions, document the decision and reasoning.

Documentation must not be a text dump. Use polished, audience-aware structure:

- current-truth table,
- what it proves,
- what it does not prove,
- blocker table,
- response or artifact shape table,
- implementation evidence,
- executable commands,
- diagrams where they clarify architecture, data flow, runtime proof, or audience understanding.

Keep README concise and navigational. Put detailed proof, operations, API, and architecture content in `docs/`. Keep repo-local `wiki/` as the authored source for onboarding, operations, demo, business, sales, marketing, and support navigation. Publish the GitHub wiki after merge when wiki source changes.

When implementation truth changes, update all durable surfaces that depend on it:

- README,
- `REPOSITORY-ENGINEERING-CONTEXT.md`,
- relevant `docs/`,
- repo-local `wiki/`,
- supported-features material,
- quality scorecards or review ledgers,
- RFC source maps and implementation ledgers,
- central platform context when the pattern is platform-wide,
- skills and scaffold docs when the pattern is repeatable.

---

# 15. Suggested Commit Sequence

Use this sequence as guidance, adapting to the repository reality.

Do not force the sequence if the repository needs a different safe order.

1. inspect repository structure and identify application boundaries
2. add or update baseline quality tooling
3. create baseline quality report
4. add CI quality workflow in report-only mode
5. add architecture boundary rules
6. add OpenAPI governance rules
7. add controller/router thinness checks where practical
8. add observability and correlation ID checks
9. add security and dependency scanning
10. add type-checking baseline
11. add or improve coverage reporting
12. split large modules into coherent packages
13. extract application services/use cases
14. extract or refine domain models and value objects
15. move infrastructure concerns behind ports/adapters
16. standardize mappers between API/application/domain/persistence
17. standardize errors and problem-details responses
18. standardize correlation ID propagation
19. standardize idempotency behavior where relevant
20. standardize audit and lineage behavior where relevant
21. improve validation and request models
22. improve response models
23. improve downstream client boundaries
24. improve retry, timeout, and error mapping behavior
25. improve logging and metrics
26. improve health, readiness, and liveness checks
27. improve OpenAPI descriptions and examples
28. add or strengthen unit tests
29. add or strengthen integration tests
30. add or strengthen API/contract tests
31. add or strengthen middleware tests
32. add or strengthen security tests
33. add or strengthen idempotency tests
34. add or strengthen performance smoke tests
35. remove proven dead code
36. remove unused dependencies
37. reduce duplication
38. improve documentation
39. tighten CI from report-only to regression-blocking
40. tighten CI to agreed enterprise-readiness thresholds
41. produce final before/after refactor health report
42. reconcile docs/wiki/context/skills/scaffold updates created by the slice
43. run stranded-truth reconciliation for durable governance paths
44. sync enterprise refactor instructions to app-local copies when this playbook changes
45. publish wiki source after merge when wiki truth changed

---

# 16. PR Requirements

The final PR must include:

- summary of refactoring approach
- before/after quality scorecard
- major architectural improvements
- API improvements
- testing improvements
- security improvements
- observability improvements
- documentation improvements
- dependency changes and justification
- behavior changes, if any
- migration notes, if any
- configuration changes, if any
- known limitations
- follow-up backlog
- review focus areas
- proof-artifact blocker-clearance summary when the slice adds or consumes evidence artifacts
- docs/wiki/context/skill/scaffold sync decision
- stranded-truth reconciliation result for RFC, docs, wiki, context, contract, supported-features, API-governance, migration, and CI-workflow paths

The PR must include concrete evidence, not just a narrative.

Required PR evidence:

- tests executed and result
- coverage result
- lint/format result
- type-check result
- complexity/maintainability result
- dependency hygiene result
- security scan result
- OpenAPI governance result where applicable
- architecture boundary result where applicable
- before/after hotspot summary
- known remaining hotspots
- exact blockers cleared and exact blockers intentionally preserved
- source-safe evidence refs for proof artifacts

---

# 17. Definition of Done

The refactor is complete only when:

- CI passes
- scorecard proves measurable improvement
- architecture boundaries are defined and enforced where practical
- OpenAPI quality is improved where APIs exist
- tests protect important behavior
- changed code is covered by meaningful tests
- security checks pass or documented exceptions exist
- dependency checks pass or documented exceptions exist
- observability behavior is implemented, documented, and tested where practical
- correlation ID behavior is implemented and tested
- error behavior is consistent
- sensitive-data logging risk is reduced
- documentation is implementation-backed
- application behavior is preserved unless changes are explicitly documented
- final PR explains what changed, why it changed, what improved, what risks remain, and what should follow next
- no unsupported feature, client-demo, production, data-mesh, downstream, AI, report/render/archive, or Workbench claim is promoted without implementation-backed proof
- any new proof artifact has a contract gate, focused tests, source-safety checks, documentation, and explicit blocker semantics
- repo-local wiki source is checked when documentation truth changed, and published after merge when required
- central context, skills, scaffold, and app-local deployed copies are synchronized when platform-wide guidance changes
- feature branches and worktrees are cleaned after merge, and durable truth is not stranded outside `main`

---

# 18. Final Agent Instruction

Refactor with discipline.

Prefer small, evidence-backed improvements.

Keep the application working.

Protect behavior with tests.

Make architecture cleaner without over-engineering.

Do not chase cosmetic perfection.

Do not make broad unsafe rewrites.

Do not claim improvement without measurement.

The final outcome should be a backend application that is measurably cleaner, safer, more testable, more observable, more secure, and easier to own in production.
