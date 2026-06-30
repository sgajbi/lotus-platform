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

Use `Y/N` proof flags:

- `Code`: source/tests/contracts/workflows were inspected.
- `Docs`: relevant docs KB, platform standard, repo context, RFC, README, wiki, or runbook was inspected.
- `Dup`: GitHub duplicate searches were run with lens and symbol terms.
- `Labels`: canonical labels were ensured/applied.
- `Ledger`: the pass was recorded in this ledger.

| Lens | Label | Status | Issues | Proof Flags | Code Areas Inspected | Remaining Questions / Residual Risk | Last Reviewed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Architecture boundaries | `lens/architecture-boundaries` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Runtime composition | `lens/runtime-composition` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| API design and governance | `lens/api-design-governance` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| HTTP boundary controls | `lens/http-boundary-controls` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Application layer | `lens/application-layer` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Domain layer | `lens/domain-layer` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Ports and adapters | `lens/ports-adapters` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Infrastructure | `lens/infrastructure` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Configuration and secrets | `lens/configuration-secrets` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Downstream integration | `lens/downstream-integration` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Mapping and anti-corruption | `lens/mapping-anti-corruption` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Unit of work and transactions | `lens/unit-of-work-transactions` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Event and outbox contracts | `lens/event-outbox-contracts` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Data product and trust telemetry contracts | `lens/data-product-trust-telemetry` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Source contract and dependency semantics | `lens/source-contract-dependency-semantics` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Database operations | `lens/database-operations` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Data model quality | `lens/data-model-quality` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Transaction lifecycle | `lens/transaction-lifecycle` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Position lifecycle | `lens/position-lifecycle` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Calculations and methodology | `lens/calculations-methodology` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Domain vocabulary | `lens/domain-vocabulary` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Validation and idempotency | `lens/validation-idempotency` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Auditability and lineage | `lens/auditability-lineage` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Observability | `lens/observability` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Security and privacy | `lens/security-privacy` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Resilience | `lens/resilience` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Performance and scalability | `lens/performance-scalability` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Testing quality | `lens/testing-quality` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| CI and release evidence | `lens/ci-release-evidence` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Documentation and runbooks | `lens/documentation-runbooks` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Operational supportability | `lens/operational-supportability` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |

## Per-Lens Note Shape

```markdown
### <Lens>

- Status: <status>
- Label: `lens/<canonical-lens-label>`
- Issues: #<number>, #<number>
- Existing related issues reused: #<number>
- Proof flags: Code:Y/N Docs:Y/N Dup:Y/N Labels:Y/N Ledger:Y/N
- Code inspected:
  - `<path>`: <symbol/route/workflow>
- Standards/docs consulted:
  - `<path or standard>`: <why it mattered>
- Duplicate searches:
  - `<query>`: <result>
- Labels:
  - Ensured/applied: `issue-discovery`, `lens/<label>`, `impact/<label>`
- Residual risk:
  - <specific remaining question or next inspection area>
- Next suggested lens:
  - <lens name and reason>
- Last reviewed: YYYY-MM-DD
```
