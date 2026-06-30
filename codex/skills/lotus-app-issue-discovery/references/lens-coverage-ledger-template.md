# Lens Coverage Ledger Template

Use this template for long-running issue-discovery campaigns. Keep it concise and evidence-backed.
The preferred durable location is one GitHub issue per Lotus app named `<app> Issue Discovery
Ledger`, especially when implementation branches are active or multiple agents need shared state.
The ledger is a navigation aid, not a substitute for code inspection or duplicate checks.

## Status Model

- `Not Started`: no meaningful inspection yet.
- `In Review`: active inspection has started, but findings are not resolved into issues or explicit no-issue decisions.
- `Issues Raised`: one or more GitHub issues were filed or reused for this lens; residual review may remain.
- `Blocked By Active Fix`: another agent has local or PR work that may change the finding; recheck after that work lands.
- `Needs Recheck`: issue overlap, code changes, or stale evidence means the lens should be revisited.
- `Covered For Now`: representative inspection and duplicate checks are complete for the current campaign depth; remaining risk is recorded.

## Ledger Table

| Lens | Label | Status | Issues | Code Areas Inspected | Remaining Questions / Residual Risk | Last Reviewed |
| --- | --- | --- | --- | --- | --- | --- |
| Architecture boundaries | `lens/architecture-boundaries` | Not Started | - | - | - | - |
| Runtime composition | `lens/runtime-composition` | Not Started | - | - | - | - |
| API design and governance | `lens/api-design-governance` | Not Started | - | - | - | - |
| HTTP boundary controls | `lens/http-boundary-controls` | Not Started | - | - | - | - |
| Application layer | `lens/application-layer` | Not Started | - | - | - | - |
| Domain layer | `lens/domain-layer` | Not Started | - | - | - | - |
| Ports and adapters | `lens/ports-adapters` | Not Started | - | - | - | - |
| Infrastructure | `lens/infrastructure` | Not Started | - | - | - | - |
| Configuration and secrets | `lens/configuration-secrets` | Not Started | - | - | - | - |
| Downstream integration | `lens/downstream-integration` | Not Started | - | - | - | - |
| Mapping and anti-corruption | `lens/mapping-anti-corruption` | Not Started | - | - | - | - |
| Unit of work and transactions | `lens/unit-of-work-transactions` | Not Started | - | - | - | - |
| Event and outbox contracts | `lens/event-outbox-contracts` | Not Started | - | - | - | - |
| Data product and trust telemetry contracts | `lens/data-product-trust-telemetry` | Not Started | - | - | - | - |
| Source contract and dependency semantics | `lens/source-contract-dependency-semantics` | Not Started | - | - | - | - |
| Database operations | `lens/database-operations` | Not Started | - | - | - | - |
| Data model quality | `lens/data-model-quality` | Not Started | - | - | - | - |
| Transaction lifecycle | `lens/transaction-lifecycle` | Not Started | - | - | - | - |
| Position lifecycle | `lens/position-lifecycle` | Not Started | - | - | - | - |
| Calculations and methodology | `lens/calculations-methodology` | Not Started | - | - | - | - |
| Domain vocabulary | `lens/domain-vocabulary` | Not Started | - | - | - | - |
| Validation and idempotency | `lens/validation-idempotency` | Not Started | - | - | - | - |
| Auditability and lineage | `lens/auditability-lineage` | Not Started | - | - | - | - |
| Observability | `lens/observability` | Not Started | - | - | - | - |
| Security and privacy | `lens/security-privacy` | Not Started | - | - | - | - |
| Resilience | `lens/resilience` | Not Started | - | - | - | - |
| Performance and scalability | `lens/performance-scalability` | Not Started | - | - | - | - |
| Testing quality | `lens/testing-quality` | Not Started | - | - | - | - |
| CI and release evidence | `lens/ci-release-evidence` | Not Started | - | - | - | - |
| Documentation and runbooks | `lens/documentation-runbooks` | Not Started | - | - | - | - |
| Operational supportability | `lens/operational-supportability` | Not Started | - | - | - | - |

## Per-Lens Note Shape

```markdown
### <Lens>

- Status: <status>
- Label: `lens/<canonical-lens-label>`
- Issues: #<number>, #<number>
- Existing related issues reused: #<number>
- Code inspected:
  - `<path>`: <symbol/route/workflow>
- Duplicate searches:
  - `<query>`: <result>
- Residual risk:
  - <specific remaining question or next inspection area>
- Last reviewed: YYYY-MM-DD
```
