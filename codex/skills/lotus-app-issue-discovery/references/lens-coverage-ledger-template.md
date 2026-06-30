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

| Lens | Status | Issues | Code Areas Inspected | Remaining Questions / Residual Risk | Last Reviewed |
| --- | --- | --- | --- | --- | --- |
| Architecture boundaries | Not Started | - | - | - | - |
| API design and governance | Not Started | - | - | - | - |
| Application layer | Not Started | - | - | - | - |
| Domain layer | Not Started | - | - | - | - |
| Ports and adapters | Not Started | - | - | - | - |
| Infrastructure | Not Started | - | - | - | - |
| Mapping and anti-corruption | Not Started | - | - | - | - |
| Unit of work and transactions | Not Started | - | - | - | - |
| Event and outbox contracts | Not Started | - | - | - | - |
| Data model quality | Not Started | - | - | - | - |
| Transaction lifecycle | Not Started | - | - | - | - |
| Position lifecycle | Not Started | - | - | - | - |
| Calculations and methodology | Not Started | - | - | - | - |
| Domain vocabulary | Not Started | - | - | - | - |
| Validation and idempotency | Not Started | - | - | - | - |
| Auditability and lineage | Not Started | - | - | - | - |
| Observability | Not Started | - | - | - | - |
| Security and privacy | Not Started | - | - | - | - |
| Resilience | Not Started | - | - | - | - |
| Performance and scalability | Not Started | - | - | - | - |
| Testing quality | Not Started | - | - | - | - |
| Documentation and runbooks | Not Started | - | - | - | - |
| Operational supportability | Not Started | - | - | - | - |

## Per-Lens Note Shape

```markdown
### <Lens>

- Status: <status>
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
