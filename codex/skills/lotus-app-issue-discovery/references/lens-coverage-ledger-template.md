# Lens Coverage Ledger Template

Use this template for long-running issue-discovery campaigns. Keep it concise and evidence-backed.
The preferred durable location is one GitHub issue per Lotus app named `<app> Issue Discovery
Ledger`, especially when implementation branches are active or multiple agents need shared state.
The ledger is a navigation aid, not a substitute for code inspection or duplicate checks.

## Contents

1. [Status Model](#status-model)
2. [Campaign Summary](#campaign-summary)
3. [Ledger Table](#ledger-table)
4. [Per-Lens Note Shape](#per-lens-note-shape)

## Status Model

- `Not Started`: no meaningful inspection yet.
- `In Review`: active inspection has started, but findings are not resolved into issues or explicit no-issue decisions.
- `Issues Raised`: one or more GitHub issues were filed or reused for this lens; residual review may remain.
- `Blocked By Active Fix`: another agent has local or PR work that may change the finding; recheck after that work lands.
- `Needs Recheck`: issue overlap, code changes, or stale evidence means the lens should be revisited.
- `Covered For Now`: representative inspection and duplicate checks are complete for the current campaign depth; remaining risk is recorded.
- `Not Applicable`: repo context or ownership boundaries prove the lens is outside the app's responsibility; record the evidence.

## Campaign Summary

Maintain this summary at the top of a newly created ledger issue, or restate it in periodic comments
when the ledger is managed through comments:

- Target repository: `<owner>/<repo>`
- Local path when known: `<path>`
- Current branch or active PRs: `<branch/PR>`
- Latest campaign recommendation: `<continue | pause for implementation | recheck after merge | move app>`
- Covered for now: `<lens labels or count>`
- Issues raised / implementation waiting: `<issue numbers or count>`
- Blocked by active fixes: `<branches/PRs/issues or none>`
- Needs recheck: `<lens labels or none>`
- Highest-value remaining lenses: `<lens labels>`

The summary is for navigation only. Do not use it as evidence for filing an issue; inspect current
code and GitHub state before every new finding.

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
| API documentation, standards, and duplicate endpoint posture | `lens/api-documentation-standards` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
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
| Data mesh, data product, and trust telemetry contracts | `lens/data-product-trust-telemetry` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Capability and supported-feature publication | `lens/capability-publication` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Evidence and proof contracts | `lens/evidence-proof-contracts` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Source contract and dependency semantics | `lens/source-contract-dependency-semantics` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Database operations | `lens/database-operations` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Data model quality | `lens/data-model-quality` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Transaction lifecycle | `lens/transaction-lifecycle` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Position lifecycle | `lens/position-lifecycle` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Calculations and methodology | `lens/calculations-methodology` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Domain vocabulary | `lens/domain-vocabulary` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Validation and idempotency | `lens/validation-idempotency` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Auditability and lineage | `lens/auditability-lineage` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Monitoring and observability | `lens/observability` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Security and privacy | `lens/security-privacy` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Resilience | `lens/resilience` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Performance and scalability | `lens/performance-scalability` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Testing quality | `lens/testing-quality` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| CI and release evidence | `lens/ci-release-evidence` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Documentation, wiki, README, and runbooks | `lens/documentation-runbooks` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Operational supportability | `lens/operational-supportability` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Dead code and duplicate logic | `lens/dead-code-duplication` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Dependency hygiene and supply chain | `lens/dependency-hygiene` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Repo organization | `lens/repo-organization` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Remote repository hygiene | `lens/remote-repository-hygiene` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Agents/context organization | `lens/agents-context-organization` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Entitlements and tenant isolation | `lens/entitlements-tenant-isolation` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Regulatory compliance and records | `lens/regulatory-compliance-records` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Deployment and environment parity | `lens/deployment-environment-parity` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Business continuity and disaster recovery | `lens/business-continuity-disaster-recovery` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| SLO, capacity, and cost management | `lens/slo-capacity-cost-management` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Release rollout and compatibility | `lens/release-rollout-compatibility` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Operator control plane | `lens/operator-control-plane` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Data governance and privacy lifecycle | `lens/data-governance-privacy-lifecycle` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| License and IP compliance | `lens/license-ip-compliance` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Localization and market conventions | `lens/localization-market-conventions` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Customer-impact failure modes | `lens/customer-impact-failure-modes` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Change-management audit | `lens/change-management-audit` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Support escalation workflows | `lens/support-escalation-workflows` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Third-party vendor risk | `lens/third-party-vendor-risk` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Accessibility and inclusive design | `lens/accessibility-inclusive-design` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Product workflow usability | `lens/product-workflow-usability` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Client communication suitability | `lens/client-communication-suitability` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Data quality and reconciliation | `lens/data-quality-reconciliation` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Migration and backfill readiness | `lens/migration-backfill-readiness` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Environment supply-chain provenance | `lens/environment-supply-chain-provenance` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| API consumer experience | `lens/api-consumer-experience` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| Mobile and responsive device readiness | `lens/mobile-responsive-device-readiness` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| AI model governance | `lens/ai-model-governance` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| AI data boundaries | `lens/ai-data-boundaries` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| AI evaluation quality | `lens/ai-evaluation-quality` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| AI explainability and audit | `lens/ai-explainability-audit` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| AI safety and abuse controls | `lens/ai-safety-abuse-controls` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| AI human oversight | `lens/ai-human-oversight` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| AI cost, latency, and reliability | `lens/ai-cost-latency-reliability` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |
| AI agent tool governance | `lens/ai-agent-tool-governance` | Not Started | - | Code:N Docs:N Dup:N Labels:N Ledger:Y | - | - | - |

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
