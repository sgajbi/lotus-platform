# Lotus App Issue Discovery Lens Catalog

Use this catalog to plan review batches. Pick one lens or a coherent group; inspect code before
raising issues.

## Canonical Lens Labels

Use these labels when filing or updating GitHub issues from this skill. Create missing labels in the
target repository before filing the issue. Keep the `lens/` prefix stable across Lotus apps.

| Lens | Canonical Label |
| --- | --- |
| Architecture boundaries | `lens/architecture-boundaries` |
| Runtime composition | `lens/runtime-composition` |
| API design and governance | `lens/api-design-governance` |
| HTTP boundary controls | `lens/http-boundary-controls` |
| Application layer | `lens/application-layer` |
| Domain layer | `lens/domain-layer` |
| Ports and adapters | `lens/ports-adapters` |
| Infrastructure | `lens/infrastructure` |
| Configuration and secrets | `lens/configuration-secrets` |
| Downstream integration | `lens/downstream-integration` |
| Mapping and anti-corruption | `lens/mapping-anti-corruption` |
| Unit of work and transactions | `lens/unit-of-work-transactions` |
| Event and outbox contracts | `lens/event-outbox-contracts` |
| Data product and trust telemetry contracts | `lens/data-product-trust-telemetry` |
| Source contract and dependency semantics | `lens/source-contract-dependency-semantics` |
| Database operations | `lens/database-operations` |
| Data model quality | `lens/data-model-quality` |
| Transaction lifecycle | `lens/transaction-lifecycle` |
| Position lifecycle | `lens/position-lifecycle` |
| Calculations and methodology | `lens/calculations-methodology` |
| Domain vocabulary | `lens/domain-vocabulary` |
| Validation and idempotency | `lens/validation-idempotency` |
| Auditability and lineage | `lens/auditability-lineage` |
| Observability | `lens/observability` |
| Security and privacy | `lens/security-privacy` |
| Resilience | `lens/resilience` |
| Performance and scalability | `lens/performance-scalability` |
| Testing quality | `lens/testing-quality` |
| CI and release evidence | `lens/ci-release-evidence` |
| Documentation and runbooks | `lens/documentation-runbooks` |
| Operational supportability | `lens/operational-supportability` |

Use these cross-cutting labels when useful:

| Label | Use |
| --- | --- |
| `issue-discovery` | Every issue created from this skill. |
| `impact/correctness` | Defects that can produce wrong business, calculation, lifecycle, or API behavior. |
| `impact/security` | Security, privacy, authorization, secret-handling, or abuse-protection risk. |
| `impact/operability` | Observability, readiness, diagnostics, recovery, or supportability risk. |
| `impact/performance` | Latency, scalability, batching, pagination, query, or resource-efficiency risk. |
| `impact/architecture` | Boundary, dependency, modularity, contract, or ownership risk. |

## Core Lens Groups

| Lens | What To Inspect | Typical High-Value Findings |
| --- | --- | --- |
| Architecture boundaries | package layout, dependency direction, router/service/repository imports, runtime composition | business logic in delivery layers, infrastructure leaking inward, unclear in-process module boundaries |
| Runtime composition | app factory, dependency container, startup/shutdown hooks, runtime package, adapter wiring, worker wiring | app startup hides business policy, runtime imports API/domain in both directions, no deterministic dependency override for tests |
| API design and governance | routes, DTOs, OpenAPI, versioning, pagination, filtering, sorting, errors | inconsistent route naming, missing problem details, weak examples, unbounded list APIs, missing deprecation posture |
| HTTP boundary controls | app middleware, CORS, trusted hosts, secure headers, body-size limits, content-type checks, abuse protection | relying only on gateway controls, missing secure response headers, unbounded request bodies, unsafe CORS defaults |
| Application layer | use cases, orchestration, commands/results, idempotency/audit workflows | API DTOs passed into use cases, framework objects in application services, missing application error taxonomy |
| Domain layer | business models, value objects, policies, calculations, lifecycle state transitions | Pydantic/API/ORM leakage into domain logic, scattered status strings, weak private-banking vocabulary |
| Ports and adapters | repository/client/event/audit/idempotency interfaces, concrete adapter wiring | concrete dependencies in application logic, broad repositories, missing publisher/client ports |
| Infrastructure | repositories, DB access, HTTP/Kafka/Redis/storage clients, configuration | commit/rollback outside unit of work, raw downstream errors, missing typed infrastructure errors |
| Configuration and secrets | settings models, environment profiles, secret loading, defaults, config validation, test fixtures | permissive production defaults, secrets in examples/logs, weak required-settings validation, test config drifting into runtime |
| Downstream integration | HTTP clients, source API clients, gateway/core/performance/risk/advisory/report/archive/render/AI clients, adapter tests | no timeout budget, raw downstream errors, source-owned semantics lost, retry storms, missing unavailable/degraded mapping |
| Mapping and anti-corruption | API DTO <-> command/result, ORM/read row <-> record, event payload <-> model, response assembly | inline event serialization, untyped row mapping, source-data builders mixing mapping and policy |
| Unit of work and transactions | DB session lifecycle, repository commits, multi-write workflows | partial commits, inconsistent rollback behavior, race-prone claim/update/write flows |
| Event and outbox contracts | events, topics, schema versions, DLQ, replay, idempotency, outbox emission | schema drift, direct Kafka publishing, weak poison-message handling, missing duplicate-delivery tests |
| Data product and trust telemetry contracts | domain data-product declarations, trust telemetry snapshots, producer/consumer declarations, platform catalog validators | governed product declarations without runtime trust proof, missing freshness/lineage/blocking evidence, stale approved-consumer truth |
| Source contract and dependency semantics | upstream source products consumed by the app, required trust metadata, source lifecycle identity, restatement/version/correction semantics | consumer contracts missing source-event identity, lifecycle/correction fields lost during normalization, fail-open dependency posture |
| Database operations | migrations, repository query shape, indexes, unique constraints, lock/lease flows, connection/session lifecycle, query tests | unbounded scans, N+1 reads, no uniqueness for idempotency, unsafe update races, missing index for hot filter/sort paths |
| Data model quality | ORM models, migrations, indexes, identifiers, temporal fields, lineage fields | missing unique constraints, weak temporal semantics, overloaded identifiers, no lineage/audit fields |
| Transaction lifecycle | booking states, trade/settlement dates, cancellations, corrections, reversals, corporate actions | missing linked legs, weak correction model, incomplete cash/product-side linkage |
| Position lifecycle | holdings, tax lots, availability, pledge/margin/collateral, corporate-action restatements | missing lot lineage, weak position type, no availability state, incorrect cash/security separation |
| Calculations and methodology | cost basis, accrued interest, valuation, FX, cashflows, income, P&L, tax, performance inputs | Decimal precision gaps, product-specific calculation assumptions, missing methodology examples/tests |
| Domain vocabulary | names in APIs, models, fields, docs, metrics, tests | ambiguous `client_id`, generic status names, non-standard transaction/instrument terms |
| Validation and idempotency | request validation, duplicate handling, idempotency keys, conflict semantics | same key/different payload not rejected, weak replay/correction validation, missing bounded error codes |
| Auditability and lineage | audit records, source batch, correlation IDs, evidence fingerprints | missing source identity, raw payload retention, no correlation chain across event/API/DB |
| Observability | structured logs, metrics, traces, health/readiness, diagnostics | raw logging, sensitive labels, missing route templates, health not dependency-aware |
| Security and privacy | authn/authz, CORS, headers, secrets, sensitive data, API abuse controls | missing authorization boundaries, unsafe CORS, secret leakage, raw exception exposure |
| Resilience | timeouts, retries, backoff, circuit breaking, graceful degradation | unbounded retries, no timeout budget, inconsistent downstream error mapping |
| Performance and scalability | indexes, query shape, batching, pagination, caching, connection pooling | N+1 queries, unbounded scans, missing indexes, repeated expensive processing |
| Testing quality | unit, integration, contract, API, security, regression, e2e, test taxonomy | mock-only tests, missing contract tests, no edge cases, weak mapper/lifecycle/calculation golden tests |
| CI and release evidence | Make/NPM targets, GitHub Actions lanes, security scans, coverage, Docker/runtime proof, release evidence, branch hygiene | workflows bypass repo-native targets, soft-failed critical gates, no main releasability evidence, stale wiki/context truth |
| Documentation and runbooks | README, repo context, architecture docs, API catalog, RFCs, wiki, supported features | docs claim unsupported behavior, stale commands, missing operator diagnostics, unlinked issues |
| Operational supportability | runbooks, dashboards, alerts, replay/recovery, support APIs | no safe operator view, weak stuck-state diagnostics, missing replay evidence |

## Baseline Lens Queue

Use this order when the user asks for broad defect discovery without naming a lens. Do not force the
order when a repo has an active incident, ongoing fix branch, or user-prioritized topic.

1. Existing issues, active branches, repository context, and ledger posture.
2. Architecture boundaries, runtime composition, API/application/domain/ports/infrastructure layers.
3. API design, HTTP boundary controls, validation, idempotency, auditability, and lineage.
4. Data model, database operations, source contracts, data products, downstream integration.
5. Product/domain lenses: vocabulary, calculations, methodology, transaction lifecycle, position lifecycle.
6. Reliability lenses: events/outbox, resilience, performance/scalability, observability, operational supportability.
7. Security/privacy, configuration/secrets, testing quality, CI/release evidence, documentation/runbooks.

For every lens, record whether the pass was code-backed, docs-backed, duplicate-checked, and ledgered.

## User Prompt To Canonical Lens Map

Use this map when the user describes a review angle in natural language. Pick one primary label for
each issue, then mention secondary lenses in the issue body when helpful.

| User wording or review intent | Primary labels to consider | Evidence to gather |
| --- | --- | --- |
| "architecture issues", "service boundaries", "dependency flow", "separation of concerns" | `lens/architecture-boundaries`, `lens/runtime-composition`, `lens/ports-adapters` | package imports, runtime wiring, dependency overrides, module ownership docs, tests that enforce boundaries |
| "design modularity before runtime modularity" | `lens/architecture-boundaries`, `lens/runtime-composition` | in-process modules, ports, application services, runtime composition, evidence for or against process splits |
| "business logic out of routers/controllers/middleware" | `lens/api-design-governance`, `lens/application-layer`, `lens/domain-layer` | route handlers, DTO mapping, use-case orchestration, domain policies/calculations, API tests |
| "application layer responsibilities" | `lens/application-layer` | command/result types, orchestration services, idempotency/audit workflows, framework leakage |
| "infrastructure responsibilities" | `lens/infrastructure`, `lens/ports-adapters` | repositories, clients, producers/consumers, persistence DTO mapping, adapter error mapping |
| "ports" | `lens/ports-adapters` | repository/client/event/audit/idempotency/clock/UUID interfaces, concrete dependency usage in application logic |
| "domain layer" | `lens/domain-layer`, `lens/domain-vocabulary`, `lens/calculations-methodology` | business models, value objects, policies, calculations, state transitions, private banking terms |
| "logic testable without FastAPI, DB, Kafka, Redis, cloud, downstream APIs" | `lens/domain-layer`, `lens/application-layer`, `lens/ports-adapters`, `lens/testing-quality` | direct framework imports, repository/client dependencies, pure unit tests, fake ports, contract tests |
| "API design, versioning, routing, pagination, filtering, sorting, errors" | `lens/api-design-governance` | routers, OpenAPI, DTOs, list APIs, problem details, examples, response models |
| "HTTP boundary controls" | `lens/http-boundary-controls`, `lens/security-privacy` | CORS, trusted hosts, secure headers, request size limits, content-type checks, abuse protection |
| "validation, idempotency, correlation IDs, auditability, lineage, traceability" | `lens/validation-idempotency`, `lens/auditability-lineage`, `lens/observability` | idempotency store, duplicate conflict semantics, correlation propagation, audit/evidence records |
| "race conditions" | `lens/unit-of-work-transactions`, `lens/database-operations`, `lens/event-outbox-contracts` | claim/lease flows, uniqueness constraints, row locks, transaction scopes, outbox delivery tests |
| "unnecessary data processing", "lack of correct logic", "batching/caching" | `lens/performance-scalability`, `lens/database-operations` | repeated full scans, N+1 reads, missing filters/indexes, pagination, cache invalidation, batch APIs |
| "logging, tracing, monitoring" | `lens/observability`, `lens/operational-supportability` | structured logs, metrics, trace propagation, route templates, health/readiness, runbooks |
| "security, vulnerabilities, auth, CORS, headers, secrets" | `lens/security-privacy`, `lens/configuration-secrets`, `lens/http-boundary-controls` | authn/authz, secret handling, config defaults, sensitive data exposure, abuse controls |
| "database operations, indexes, performance" | `lens/database-operations`, `lens/performance-scalability`, `lens/data-model-quality` | migrations, query paths, indexes/constraints, hot filters/sorts, pooling/timeouts |
| "domain modeling and private banking vocabulary" | `lens/domain-vocabulary`, `lens/domain-layer`, `lens/data-model-quality` | API/model/field names, status/state terms, docs vocabulary, product taxonomy alignment |
| "transactions, lifecycle handling, positions" | `lens/transaction-lifecycle`, `lens/position-lifecycle`, `lens/data-model-quality` | linked legs, cash/security side, corrections/reversals, settlements, corporate actions, lots, availability |
| "calculations" | `lens/calculations-methodology` | methodology docs, Decimal/rounding, FX, accrued interest, cost basis, income, cashflow, golden tests |
| "CI, quality gates, release evidence" | `lens/ci-release-evidence`, `lens/testing-quality` | Make targets, workflows, continue-on-error, timeout-minutes, coverage, security scans, main release proof |
| "README, wiki, architecture docs, API catalog, runbooks" | `lens/documentation-runbooks`, `lens/operational-supportability` | current-state claims, commands, operator docs, API catalog, RFC closure, wiki source |

## Finding Decision Tree

Use this decision tree before filing:

1. Is the evidence in the target repository current source, tests, contracts, migrations, workflows,
   docs, or runtime output? If not, do not file.
2. Is the expected behavior grounded in docs KB, Lotus platform standards, repo context, a public
   standard, or accepted private-banking/domain practice? If not, ledger-only.
3. Does an open or closed GitHub issue already cover the same root cause and acceptance criteria?
   If yes, reuse or comment instead of filing.
4. Is the issue small enough for one implementation agent to start without re-discovering the whole
   repo? If not, split it or turn it into ledger residual risk.
5. Can acceptance criteria include tests, contract checks, docs/context updates, or validation
   proof? If not, keep gathering evidence.

## Evidence Strength Rubric

| Strength | Meaning | Action |
| --- | --- | --- |
| Strong | Concrete code path plus matching missing/weak test or contract, with docs/platform standard support | File an issue |
| Medium | Concrete code path and plausible risk, but standard or blast radius needs more proof | Inspect one more path or ledger as residual risk |
| Weak | Search hit only, stale docs only, style preference, or future-state idea | Do not file |
| Active fix | Same root cause is on an active branch or PR | Comment on existing issue/PR or mark ledger `Blocked By Active Fix` |

## Required Issue Anchors By Lens Family

Use these anchors to make issues practical:

| Lens family | Minimum anchor |
| --- | --- |
| Layering and boundaries | import path or function showing cross-layer leakage, plus target direction |
| API | route, DTO, OpenAPI behavior, error model, or missing pagination/filter contract |
| Data/model/lifecycle | model/migration/DTO field, state transition, linked-leg behavior, or missing lineage |
| Database/performance | query path, migration/index/constraint, hot access pattern, or batch/pagination gap |
| Security/config | concrete auth/config/header/secret/sensitive-data path and expected safe behavior |
| Observability/support | log/metric/trace/health/readiness/runbook path and missing diagnostic outcome |
| Testing/CI | exact test family, Make target, workflow, gate, or release-evidence path |
| Documentation | current-state claim, missing operator instruction, stale RFC/wiki/API catalog link |

## Lens-Specific Search Starters

Use these as starting points, not as proof by themselves.

### Layering

```powershell
rg -n "from fastapi|Request|Depends|Session|AsyncSession|Kafka|Redis|requests|httpx|model_dump\\(|model_validate\\(" src --glob "*.py"
```

### API Contracts

```powershell
rg -n "APIRouter|@router\\.|response_model|HTTPException|status_code|operation_id|Query\\(|Path\\(" src --glob "*.py"
```

### Runtime Composition And HTTP Boundary

```powershell
rg -n "FastAPI\\(|add_middleware|include_router|startup|shutdown|lifespan|Depends\\(|CORSMiddleware|TrustedHostMiddleware|Strict-Transport|X-Content-Type|X-Frame|Content-Security|Referrer-Policy|Permissions-Policy|Content-Length|payload|request size|rate limit|throttle" src tests docs --glob "*.py" --glob "*.md"
```

### Events And Outbox

```powershell
rg -n "Kafka|publish_message|create_outbox_event|model_dump\\(mode=\"json\"\\)|json\\.loads|DLQ|schema_version|event_type" src --glob "*.py"
```

### Data Products And Source Contracts

```powershell
rg -n "domain-data-product|trust-telemetry|producer_repository|consumer_repository|required_trust_metadata|freshness_policy|lineage_policy|approved_consumers|source_event|source_snapshot|restatement|correction|reversal" contracts docs tests src --glob "*.json" --glob "*.md" --glob "*.py"
```

### Data Model And Queries

```powershell
rg -n "Index\\(|UniqueConstraint|ForeignKey|relationship\\(|select\\(|join\\(|order_by\\(|limit\\(|offset\\(" src --glob "*.py"
```

### Database Operations

```powershell
rg -n "create_engine|sessionmaker|Session|AsyncSession|BEGIN|COMMIT|ROLLBACK|FOR UPDATE|SKIP LOCKED|insert\\(|update\\(|delete\\(|bulk|executemany|pool_size|max_overflow|statement_timeout|lock_timeout" src tests migrations --glob "*.py" --glob "*.sql"
```

### Configuration And Downstream Clients

```powershell
rg -n "BaseSettings|Settings|os\\.environ|getenv|Secret|password|token|api_key|timeout|retry|backoff|httpx|requests|AsyncClient|Client\\(" src tests docs --glob "*.py" --glob "*.md"
```

### Lifecycle And Transactions

```powershell
rg -n "transaction_type|settlement|correction|reversal|cancel|corporate|split|dividend|transfer|redemption|maturity|coupon|cashflow|position|lot" src tests docs --glob "*.py" --glob "*.md"
```

### Observability And Security

```powershell
rg -n "logging|getLogger|print\\(|metrics|Counter|Histogram|trace|correlation|CORS|secret|token|Authorization|auth|password|headers" src tests --glob "*.py"
```

### Resilience And Performance

```powershell
rg -n "timeout|retry|backoff|sleep|while True|gather|Semaphore|pool|cache|batch|page_size|limit|offset" src tests --glob "*.py"
```

### CI And Release Evidence

```powershell
rg -n "pytest|make |npm run|continue-on-error|timeout-minutes|permissions:|pull_request_target|coverage|docker|trivy|bandit|pip-audit|main-releasability|merge gate" .github Makefile package.json pyproject.toml docs wiki --glob "*.yml" --glob "*.yaml" --glob "*.md" --glob "Makefile" --glob "*.toml" --glob "*.json"
```

## Duplicate Check Keywords

Search GitHub with both broad and specific terms:

- broad lens terms: `architecture`, `mapping`, `outbox`, `idempotency`, `pagination`
- concrete symbols: function/class/route/topic/table names
- issue-family terms: `boundary`, `contract`, `lifecycle`, `supportability`, `lineage`

## Severity Calibration

Prefer issues that are one of:

- correctness defect,
- production supportability gap,
- security/privacy risk,
- architecture boundary causing repeated drift,
- contract issue that can break consumers,
- missing tests around high-value behavior,
- performance/concurrency risk on hot paths.

Defer or avoid:

- taste-only refactors,
- large rewrites without a fix path,
- findings that are already covered by a broader active issue,
- future product ideas not grounded in current code or accepted standards.

