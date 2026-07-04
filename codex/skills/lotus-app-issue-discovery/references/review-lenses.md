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
| API documentation, standards, and duplicate endpoint posture | `lens/api-documentation-standards` |
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
| Data mesh, data product, and trust telemetry contracts | `lens/data-product-trust-telemetry` |
| Capability and supported-feature publication | `lens/capability-publication` |
| Evidence and proof contracts | `lens/evidence-proof-contracts` |
| Source contract and dependency semantics | `lens/source-contract-dependency-semantics` |
| Database operations | `lens/database-operations` |
| Data model quality | `lens/data-model-quality` |
| Transaction lifecycle | `lens/transaction-lifecycle` |
| Position lifecycle | `lens/position-lifecycle` |
| Calculations and methodology | `lens/calculations-methodology` |
| Domain vocabulary | `lens/domain-vocabulary` |
| Validation and idempotency | `lens/validation-idempotency` |
| Auditability and lineage | `lens/auditability-lineage` |
| Monitoring and observability | `lens/observability` |
| Security and privacy | `lens/security-privacy` |
| Resilience | `lens/resilience` |
| Performance and scalability | `lens/performance-scalability` |
| Testing quality | `lens/testing-quality` |
| CI and release evidence | `lens/ci-release-evidence` |
| Documentation, wiki, README, and runbooks | `lens/documentation-runbooks` |
| Operational supportability | `lens/operational-supportability` |
| Dead code and duplicate logic | `lens/dead-code-duplication` |
| Dependency hygiene and supply chain | `lens/dependency-hygiene` |
| Repo organization | `lens/repo-organization` |
| Remote repository hygiene | `lens/remote-repository-hygiene` |
| Agents/context organization | `lens/agents-context-organization` |

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
| API documentation, standards, and duplicate endpoint posture | generated OpenAPI, endpoint catalogs, route inventories, API certification ledgers, Swagger examples, API vocabulary/no-alias evidence, Gateway/Workbench API maps | endpoint docs missing operation purpose/examples/errors, duplicate or overlapping routes with no owning contract, unclear supported/deprecated APIs, OpenAPI diverging from implementation, route inventory not reconciled with tests or consumers |
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
| Data mesh, data product, and trust telemetry contracts | domain data-product declarations, trust telemetry snapshots, producer/consumer declarations, platform catalog validators, mesh catalog publication, SLO/access/evidence policies | governed product declarations without runtime trust proof, missing freshness/lineage/blocking evidence, stale approved-consumer truth, mesh catalog entries not backed by runtime evidence |
| Capability and supported-feature publication | supported-feature ledgers, capability registries, Gateway publication, Workbench consumption, README/wiki feature claims, demo/publication contracts | published features without implemented or certified endpoints, stale Workbench/Gateway capability truth, UI-visible claims backed by unsupported behavior |
| Evidence and proof contracts | implementation proofs, certification artifacts, scorecards, validation outputs, generated evidence packs, proof schemas, evidence lineage | proof artifacts not reproducible from current code, unbounded/manual evidence, stale scorecards, missing evidence fingerprints or contract provenance |
| Source contract and dependency semantics | upstream source products consumed by the app, required trust metadata, source lifecycle identity, restatement/version/correction semantics | consumer contracts missing source-event identity, lifecycle/correction fields lost during normalization, fail-open dependency posture |
| Database operations | migrations, repository query shape, indexes, unique constraints, lock/lease flows, connection/session lifecycle, query tests | unbounded scans, N+1 reads, no uniqueness for idempotency, unsafe update races, missing index for hot filter/sort paths |
| Data model quality | ORM models, migrations, indexes, identifiers, temporal fields, lineage fields | missing unique constraints, weak temporal semantics, overloaded identifiers, no lineage/audit fields |
| Transaction lifecycle | booking states, trade/settlement dates, cancellations, corrections, reversals, corporate actions | missing linked legs, weak correction model, incomplete cash/product-side linkage |
| Position lifecycle | holdings, tax lots, availability, pledge/margin/collateral, corporate-action restatements | missing lot lineage, weak position type, no availability state, incorrect cash/security separation |
| Calculations and methodology | cost basis, accrued interest, valuation, FX, cashflows, income, P&L, tax, performance inputs | Decimal precision gaps, product-specific calculation assumptions, missing methodology examples/tests |
| Domain vocabulary | names in APIs, models, fields, docs, metrics, tests | ambiguous `client_id`, generic status names, non-standard transaction/instrument terms |
| Validation and idempotency | request validation, duplicate handling, idempotency keys, conflict semantics | same key/different payload not rejected, weak replay/correction validation, missing bounded error codes |
| Auditability and lineage | audit records, source batch, correlation IDs, evidence fingerprints | missing source identity, raw payload retention, no correlation chain across event/API/DB |
| Monitoring and observability | structured logs, metrics, traces, health/readiness, diagnostics, alert rules, dashboards, SLO/error-budget evidence | raw logging, sensitive labels, missing route templates, health not dependency-aware, no alert/dashboard path for critical failures |
| Security and privacy | authn/authz, CORS, headers, secrets, sensitive data, API abuse controls | missing authorization boundaries, unsafe CORS, secret leakage, raw exception exposure |
| Resilience | timeouts, retries, backoff, circuit breaking, graceful degradation | unbounded retries, no timeout budget, inconsistent downstream error mapping |
| Performance and scalability | indexes, query shape, batching, pagination, caching, connection pooling | N+1 queries, unbounded scans, missing indexes, repeated expensive processing |
| Testing quality | unit, integration, contract, API, security, regression, e2e, test taxonomy | mock-only tests, missing contract tests, no edge cases, weak mapper/lifecycle/calculation golden tests |
| CI and release evidence | Make/NPM targets, GitHub Actions lanes, security scans, coverage, Docker/runtime proof, release evidence, branch hygiene | workflows bypass repo-native targets, soft-failed critical gates, no main releasability evidence, stale wiki/context truth |
| Documentation, wiki, README, and runbooks | README, repo context, architecture docs, API catalog, RFCs, wiki, supported features, docs regression tests | docs claim unsupported behavior, stale commands, missing operator diagnostics, unlinked issues, wiki/README truth drifting from implementation |
| Operational supportability | runbooks, dashboards, alerts, replay/recovery, support APIs | no safe operator view, weak stuck-state diagnostics, missing replay evidence |
| Dead code and duplicate logic | stale modules, duplicate builders, unused routes, abandoned tests, repeated policy logic, conflicting helper paths | unsupported behavior still reachable, duplicate rules drifting apart, obsolete code confusing ownership, tests exercising dead paths |
| Dependency hygiene and supply chain | dependency manifests, lockfiles, scanner config, import usage, transitive risk, license posture | vulnerable or unpinned dependencies, unused heavy packages, scanner blind spots, dependency drift across runtime and CI |
| Repo organization | repository layout, source tree, generated artifacts, cleanup scripts, local byproduct policy, repo hygiene gates, script and quality-artifact organization | generated/runtime artifacts not aligned with cleanup policy, source/generated truth mixed, stale or confusing top-level layout, repo hygiene gaps letting agent byproducts become source truth |
| Remote repository hygiene | GitHub repo description, topics, default branch, branch protection posture, stale remote feature branches, merged branch pruning, archived/fork/visibility state, repo URL/readme alignment, remote wiki/source alignment | repo description misstates ownership or product scope, stale remote feature branches carry stranded durable truth, remote settings contradict Lotus standards, default branch or topics make agents choose the wrong repo, GitHub wiki/source publication drift is not discoverable |
| Agents/context organization | `AGENTS.md`, repo context, platform context cross-links, skill routing, procedural memory, agent onboarding paths, local/deployed skill source alignment | mandatory reading order not discoverable, repo context bypasses skill routing, local skill drift, procedural memory missing for repeated work |

## Baseline Lens Queue

Use this order when the user asks for broad defect discovery without naming a lens. Do not force the
order when a repo has an active incident, ongoing fix branch, or user-prioritized topic.

1. Existing issues, active branches, repository context, and ledger posture.
2. Architecture boundaries, runtime composition, API/application/domain/ports/infrastructure layers.
3. API design, API documentation/standards/duplicate endpoint posture, HTTP boundary controls,
   validation, idempotency, auditability, and lineage.
4. Data model, database operations, source contracts, data mesh/data products, capability publication,
   evidence/proof contracts, downstream integration.
5. Product/domain lenses: vocabulary, calculations, methodology, transaction lifecycle, position lifecycle.
6. Reliability lenses: events/outbox, resilience, performance/scalability, monitoring/observability, operational supportability.
7. Security/privacy, configuration/secrets, testing quality, CI/release evidence, documentation/wiki/README/runbooks.
8. Repo organization, remote repository hygiene, and agents/context organization where layout,
   generated-artifact policy, remote branch/repo metadata, agent onboarding, or skill-routing
   discoverability affects future implementation quality.
9. Dead-code/duplication and dependency-hygiene passes when prior lenses reveal stale paths,
   repeated logic, vulnerable dependencies, or cleanup work with real behavioral or supportability
   impact.

For every lens, record whether the pass was code-backed, docs-backed, duplicate-checked, and ledgered.

## Repository Review Profiles

Use these profiles to choose the strongest first lenses for the target app. They are starting
points, not exemptions from the baseline queue.

| Repository Type | First High-Value Lens Group |
| --- | --- |
| Source-owned domain service such as `lotus-core` | data model, transaction/position lifecycle, validation/idempotency, auditability/lineage, database operations, API governance and API documentation/standards |
| Analytics service such as `lotus-performance` or `lotus-risk` | calculations/methodology, source contract semantics, API governance and API documentation/standards, observability/supportability, testing quality, performance/scalability |
| Workflow service such as `lotus-advise`, `lotus-manage`, `lotus-report`, or `lotus-idea` | lifecycle state transitions, idempotency, event/outbox, proof/evidence, operational supportability, capability publication |
| Experience/composition service such as `lotus-gateway` | API governance, downstream integration, mapping/anti-corruption, authorization, fan-out resilience, capability publication |
| Product UI such as `lotus-workbench` | Gateway/BFF consumption, supported-feature truth, entitlement/error states, observability, accessibility/usability defects that hide backend truth |
| Platform/governance repository such as `lotus-platform` | CI/release evidence, standards/contracts, scaffold drift, repo organization, skill/context routing, agents/context organization, validation automation, docs/wiki truth |

For any profile, verify the app's current `REPOSITORY-ENGINEERING-CONTEXT.md` before filing. If the
profile and repo context disagree, use repo context as the ownership boundary and record the
conflict in the ledger.

## Lens Definition Of Done

A lens pass is complete for the current campaign depth only when all of these are true:

1. at least one representative source path and one representative test, docs, contract, workflow, or
   migration path were inspected, or the absence of that path was verified;
2. the expected behavior was compared against repo context, Lotus platform standards, the docs KB,
   an RFC/contract, or accepted industry/domain practice;
3. GitHub duplicate searches covered broad lens terms and concrete symbols from the evidence;
4. labels were ensured or existing labels were confirmed;
5. every candidate was classified as `new issue`, `existing issue`, `active-fix feedback`,
   `ledger-only residual risk`, or `no issue`;
6. the ledger records the status, proof flags, inspected paths, duplicate searches, issues
   raised/reused, residual risk, and next lens.

Do not mark `Covered For Now` when only a search was run, when the current active branch may change
the evidence, or when a broad issue was filed but representative inspection is still incomplete.
Use `Issues Raised` for open findings that need implementation, `Blocked By Active Fix` when the
same files are changing, and `Needs Recheck` when the proof may be stale after a merge.

## Campaign Coverage Model

Use these groups when explaining progress or deciding whether to move to another app:

- `Done enough for now`: lenses marked `Covered For Now`.
- `Implementation waiting`: lenses marked `Issues Raised` with open implementation issues.
- `Blocked`: lenses marked `Blocked By Active Fix` or tied to an open PR.
- `Recheck later`: lenses marked `Needs Recheck`.
- `Remaining`: lenses marked `Not Started` or with weak/no ledger evidence.

The campaign is usually ready to pause or move apps when the first three groups cover the highest
risk areas for that repository's source-owned responsibility and the remaining lenses are either
lower value or depend on fixes/runtime evidence that has not landed.

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
| "API documentation", "API standard", "Swagger", "OpenAPI quality", "duplicate APIs", "unclear APIs", "API improvements" | `lens/api-documentation-standards`, `lens/api-design-governance`, `lens/documentation-runbooks` | generated OpenAPI, route inventory, endpoint catalog, operation IDs, examples, error responses, API certification ledger, duplicate route searches, consumer references |
| "HTTP boundary controls" | `lens/http-boundary-controls`, `lens/security-privacy` | CORS, trusted hosts, secure headers, request size limits, content-type checks, abuse protection |
| "validation, idempotency, correlation IDs, auditability, lineage, traceability" | `lens/validation-idempotency`, `lens/auditability-lineage`, `lens/observability` | idempotency store, duplicate conflict semantics, correlation propagation, audit/evidence records |
| "supported features", "capability publication", "Gateway", "Workbench discovery", "UI backed by backend" | `lens/capability-publication`, `lens/api-design-governance`, `lens/documentation-runbooks` | supported-feature ledgers, capability registries, Gateway routes, Workbench consumers, README/wiki claims, endpoint certification |
| "proof artifacts", "certification evidence", "scorecard", "implementation proof", "evidence pack" | `lens/evidence-proof-contracts`, `lens/ci-release-evidence`, `lens/operational-supportability` | generated evidence files, proof schemas, certification commands, scorecards, evidence fingerprints, reproducibility from current source |
| "race conditions" | `lens/unit-of-work-transactions`, `lens/database-operations`, `lens/event-outbox-contracts` | claim/lease flows, uniqueness constraints, row locks, transaction scopes, outbox delivery tests |
| "unnecessary data processing", "lack of correct logic", "batching/caching" | `lens/performance-scalability`, `lens/database-operations` | repeated full scans, N+1 reads, missing filters/indexes, pagination, cache invalidation, batch APIs |
| "logging, tracing, monitoring" | `lens/observability`, `lens/operational-supportability` | structured logs, metrics, trace propagation, route templates, health/readiness, runbooks |
| "monitoring, alerts, dashboards, metrics, SLOs" | `lens/observability`, `lens/operational-supportability` | metric contracts, alert rules, dashboards, SLO/error-budget evidence, runbooks, health/readiness behavior |
| "security, vulnerabilities, auth, CORS, headers, secrets" | `lens/security-privacy`, `lens/configuration-secrets`, `lens/http-boundary-controls` | authn/authz, secret handling, config defaults, sensitive data exposure, abuse controls |
| "database operations, indexes, performance" | `lens/database-operations`, `lens/performance-scalability`, `lens/data-model-quality` | migrations, query paths, indexes/constraints, hot filters/sorts, pooling/timeouts |
| "domain modeling and private banking vocabulary" | `lens/domain-vocabulary`, `lens/domain-layer`, `lens/data-model-quality` | API/model/field names, status/state terms, docs vocabulary, product taxonomy alignment |
| "transactions, lifecycle handling, positions" | `lens/transaction-lifecycle`, `lens/position-lifecycle`, `lens/data-model-quality` | linked legs, cash/security side, corrections/reversals, settlements, corporate actions, lots, availability |
| "calculations" | `lens/calculations-methodology` | methodology docs, Decimal/rounding, FX, accrued interest, cost basis, income, cashflow, golden tests |
| "CI, quality gates, release evidence" | `lens/ci-release-evidence`, `lens/testing-quality` | Make targets, workflows, continue-on-error, timeout-minutes, coverage, security scans, main release proof |
| "data mesh", "data product", "catalog", "producer/consumer declarations", "trust telemetry" | `lens/data-product-trust-telemetry`, `lens/source-contract-dependency-semantics` | data-product declarations, mesh catalog publication, producer/consumer policy, trust telemetry, freshness/lineage/SLO/access evidence |
| "repo organization", "repository layout", "generated artifacts", "cleanup policy", "script organization", "repository hygiene" | `lens/repo-organization`, `lens/dead-code-duplication`, `lens/ci-release-evidence` | top-level layout, generated-artifact paths, `.gitignore`, `.dockerignore`, clean scripts, Make targets, hygiene gates, source-vs-output boundaries |
| "stale remote feature branches", "repo description", "GitHub description", "remote repo quality", "remote repo hygiene", "repository settings" | `lens/remote-repository-hygiene`, `lens/repo-organization`, `lens/documentation-runbooks` | `gh repo view`, remote branch list, unmerged branch diff summaries for durable paths, branch protection/default branch settings, repo topics/description, open PRs, wiki publication posture |
| "agents", "agent context", "AGENTS.md", "skill routing", "procedural memory", "future agents should know what to read" | `lens/agents-context-organization`, `lens/documentation-runbooks`, `lens/ci-release-evidence` | `AGENTS.md`, repo engineering context, platform context links, skill routing map, procedural memory, local/deployed skill alignment, onboarding docs |
| "README, wiki, architecture docs, API catalog, runbooks", "documentation truth" | `lens/documentation-runbooks`, `lens/operational-supportability` | current-state claims, commands, operator docs, API catalog, RFC closure, wiki source, docs regression tests |
| "dead code", "duplicate logic", "stale code", "obsolete paths", "cleanup with impact" | `lens/dead-code-duplication`, `lens/architecture-boundaries`, `lens/testing-quality` | unused routes/modules/tests, duplicate rules or builders, unreachable adapters, divergent helpers, stale docs or workflows still referencing removed behavior |
| "dependencies", "vulnerable packages", "supply chain", "lockfile", "dependency hygiene" | `lens/dependency-hygiene`, `lens/security-privacy`, `lens/ci-release-evidence` | manifests, lockfiles, scanner workflows, import usage, vulnerability output, dependency policy docs |
| "skill should work like you", "make issue discovery reusable", "future agents should know what to do" | `lens/agents-context-organization`, `lens/ci-release-evidence`, `lens/documentation-runbooks` for the platform skill source, or no app issue when it is a skill-maintenance slice | skill source, routing map, campaign playbook, ledger template, validation/sync commands, PR proof pack |

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
| API | route, DTO, OpenAPI behavior, error model, missing pagination/filter contract, endpoint catalog, duplicate route evidence, or API certification ledger |
| Data/model/lifecycle | model/migration/DTO field, state transition, linked-leg behavior, or missing lineage |
| Capability/publication | supported-feature or capability declaration plus missing runtime/API/test proof or stale consumer publication |
| Evidence/proof | generated proof, scorecard, certification artifact, or evidence contract that cannot be reproduced or traced |
| Database/performance | query path, migration/index/constraint, hot access pattern, or batch/pagination gap |
| Security/config | concrete auth/config/header/secret/sensitive-data path and expected safe behavior |
| Observability/support | log/metric/trace/health/readiness/runbook path and missing diagnostic outcome |
| Testing/CI | exact test family, Make target, workflow, gate, or release-evidence path |
| Documentation | current-state claim, missing operator instruction, stale RFC/wiki/API catalog link |
| Repo organization | layout, generated-artifact, cleanup script, ignore file, Make target, or hygiene-gate path |
| Remote repository hygiene | GitHub repo metadata, branch protection/default branch setting, stale remote branch list, unmerged durable-truth diff, or repo description/topic evidence |
| Agents/context organization | `AGENTS.md`, repo context, skill-routing, procedural-memory, onboarding, or local skill sync path |
| Dead-code/duplication | stale or duplicate path plus evidence that it is still imported, tested, published, or confusing ownership |
| Dependency hygiene | dependency declaration or scanner path plus import/runtime/CI evidence that the dependency posture matters |

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

### API Documentation, Standards, And Duplicate Endpoints

```powershell
rg -n "openapi|swagger|operation_id|api catalog|endpoint catalog|endpoint-certification|API-CERTIFICATION|no-alias|vocabulary|duplicate endpoint|deprecated|supported API|unsupported API" README.md docs wiki contracts src tests output --glob "*.md" --glob "*.json" --glob "*.py" --glob "*.yml" --glob "*.yaml"
rg -n "APIRouter\\(|@router\\.(get|post|put|patch|delete)|include_router|operation_id" src tests --glob "*.py"
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
rg -n "domain-data-product|trust-telemetry|producer_repository|consumer_repository|required_trust_metadata|freshness_policy|lineage_policy|approved_consumers|source_event|source_snapshot|restatement|correction|reversal|supported-feature|supported_feature|capability|Gateway|Workbench|publication|certification|evidence|proof|scorecard" contracts docs tests src wiki --glob "*.json" --glob "*.md" --glob "*.py"
```

### Capability Publication And Proof Evidence

```powershell
rg -n "supported-feature|supported_feature|capability|capabilities|Gateway|Workbench|publication|published|certification|certified|evidence|proof|scorecard|demo-ready|demo ready|api catalog|API catalog" README.md docs wiki contracts src tests output --glob "*.md" --glob "*.json" --glob "*.py" --glob "*.yml" --glob "*.yaml"
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

### Repo Organization And Cleanup

```powershell
rg -n "clean_generated_artifacts|repository-hygiene|output/|artifacts/|lineage_data|generated|source of truth|Makefile|quality/" .gitignore .dockerignore Makefile docs wiki scripts automation quality --glob "*.md" --glob "*.py" --glob "*.ps1" --glob "*.yml" --glob "*.yaml" --glob "Makefile"
rg --files | rg "^(artifacts|output|lineage_data|quality|scripts|automation|docs|wiki|src|tests)/|README.md|AGENTS.md|REPOSITORY-ENGINEERING-CONTEXT.md|Makefile|\\.gitignore|\\.dockerignore"
```

### Remote Repository Hygiene

```powershell
gh repo view <owner>/<repo> --json name,description,homepageUrl,repositoryTopics,defaultBranchRef,isArchived,isFork,visibility,url
git fetch origin --prune
git branch -r --no-merged origin/main
gh pr list --repo <owner>/<repo> --state open --limit 100 --json number,title,headRefName,baseRefName,updatedAt,url
```

### Agents And Context Organization

```powershell
rg -n "AGENTS.md|REPOSITORY-ENGINEERING-CONTEXT|LOTUS-SKILL-ROUTING|PROCEDURAL-MEMORY|mandatory reading|agent|context|skill routing|deployed skill|local skill" AGENTS.md README.md REPOSITORY-ENGINEERING-CONTEXT.md docs wiki .github --glob "*.md" --glob "*.yml" --glob "*.yaml"
```

### Dead Code, Duplicate Logic, And Dependency Hygiene

```powershell
rg -n "TODO|FIXME|deprecated|legacy|unused|duplicate|copy|fallback|compat|temporary|remove after|dead code|not used|pass #|pragma: no cover" src tests docs wiki --glob "*.py" --glob "*.md"
rg --files | rg "requirements|constraints|poetry.lock|uv.lock|package-lock|pnpm-lock|yarn.lock|pyproject.toml|package.json|pip-audit|safety|trivy|bandit|npm audit"
```

## Duplicate Check Keywords

Search GitHub with both broad and specific terms:

- broad lens terms: `architecture`, `mapping`, `outbox`, `idempotency`, `pagination`,
  `OpenAPI`, `Swagger`, `duplicate endpoint`, `stale branch`, `repo description`
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

