# Lotus App Issue Discovery Lens Catalog

Use this catalog to plan review batches. Pick one lens or a coherent group; inspect code before
raising issues.

## Core Lens Groups

| Lens | What To Inspect | Typical High-Value Findings |
| --- | --- | --- |
| Architecture boundaries | package layout, dependency direction, router/service/repository imports, runtime composition | business logic in delivery layers, infrastructure leaking inward, unclear in-process module boundaries |
| API design and governance | routes, DTOs, OpenAPI, versioning, pagination, filtering, sorting, errors | inconsistent route naming, missing problem details, weak examples, unbounded list APIs, missing deprecation posture |
| Application layer | use cases, orchestration, commands/results, idempotency/audit workflows | API DTOs passed into use cases, framework objects in application services, missing application error taxonomy |
| Domain layer | business models, value objects, policies, calculations, lifecycle state transitions | Pydantic/API/ORM leakage into domain logic, scattered status strings, weak private-banking vocabulary |
| Ports and adapters | repository/client/event/audit/idempotency interfaces, concrete adapter wiring | concrete dependencies in application logic, broad repositories, missing publisher/client ports |
| Infrastructure | repositories, DB access, HTTP/Kafka/Redis/storage clients, configuration | commit/rollback outside unit of work, raw downstream errors, missing typed infrastructure errors |
| Mapping and anti-corruption | API DTO <-> command/result, ORM/read row <-> record, event payload <-> model, response assembly | inline event serialization, untyped row mapping, source-data builders mixing mapping and policy |
| Unit of work and transactions | DB session lifecycle, repository commits, multi-write workflows | partial commits, inconsistent rollback behavior, race-prone claim/update/write flows |
| Event and outbox contracts | events, topics, schema versions, DLQ, replay, idempotency, outbox emission | schema drift, direct Kafka publishing, weak poison-message handling, missing duplicate-delivery tests |
| Data product and trust telemetry contracts | domain data-product declarations, trust telemetry snapshots, producer/consumer declarations, platform catalog validators | governed product declarations without runtime trust proof, missing freshness/lineage/blocking evidence, stale approved-consumer truth |
| Source contract and dependency semantics | upstream source products consumed by the app, required trust metadata, source lifecycle identity, restatement/version/correction semantics | consumer contracts missing source-event identity, lifecycle/correction fields lost during normalization, fail-open dependency posture |
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
| Documentation and runbooks | README, repo context, architecture docs, API catalog, RFCs, wiki, supported features | docs claim unsupported behavior, stale commands, missing operator diagnostics, unlinked issues |
| Operational supportability | runbooks, dashboards, alerts, replay/recovery, support APIs | no safe operator view, weak stuck-state diagnostics, missing replay evidence |

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

