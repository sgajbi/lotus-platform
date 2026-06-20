# Lotus Bank-Buyable Engineering Contract

This standard defines what "bank-buyable" means for Lotus applications and shared platform
capabilities.

It is a platform-owned engineering contract. It must be used by agents and engineers when bringing
any Lotus app closer to a reusable, maintainable, secure, observable, production-ready posture that a
bank technology buyer could evaluate seriously.

The contract is intentionally evidence-driven. A repository does not become bank-buyable because its
README says so. It becomes more bank-buyable when implementation, tests, CI, runtime behavior,
documentation, and operating evidence line up.

## Scope

This contract applies to:

1. `lotus-workbench`
   Product UI and front-office experience.
2. `lotus-gateway`
   Experience API and governed composition boundary.
3. `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise`, `lotus-manage`, `lotus-report`
   Domain-authoritative or domain workflow services.
4. `lotus-render`, `lotus-archive`, `lotus-ai`
   Shared capability services.
5. `lotus-platform`
   Platform governance, validation, automation, ingress, standards, and cross-repository evidence.

It does not replace repository-local ownership. Platform truth belongs in `lotus-platform`.
Repository-specific implementation truth belongs in the owning repository's
`REPOSITORY-ENGINEERING-CONTEXT.md`, README, docs, contracts, tests, and wiki source.

## Source Of Truth

Canonical copy:

1. `lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`

Related Lotus standards:

1. `docs/standards/Enterprise Readiness Standard.md`
2. `docs/standards/Testing Pyramid and Coverage Standard.md`
3. `docs/standards/Dependency Hygiene and Security Standard.md`
4. `docs/standards/Scalability and Availability Standard.md`
5. `docs/standards/Platform Observability Standards.md`
6. `docs/standards/Continuous Integration, Validation, and Release Governance Standard.md`
7. `platform-standards/Development-Workflow-and-CI-Strategy-Standard.md`
8. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
9. `platform-standards/Workflow-Security-and-Permissions-Standard.md`
10. `platform-standards/Workflow-Action-Runtime-and-Version-Baseline.md`
11. `platform-standards/Release-Evidence-and-SBOM-Foundation-Standard.md`

Agents should link to this standard from app-local docs when adopting it. Do not copy the full text
into every app unless an app-specific adoption document needs a local interpretation.

## Non-Negotiables

Every Lotus app refactoring or readiness slice must follow these rules:

1. Do not fake compliance. Mark unknowns as unknown and create follow-up work.
2. Do not claim a capability is implemented unless executable code, tests, and evidence support it.
3. Preserve behavior unless the behavior change is intentional, tested, and documented.
4. Keep commits small, truthful, and scoped to one improvement area.
5. Keep the app buildable after each slice.
6. Use synthetic or approved demo data only. Do not introduce real client data, account data,
   secrets, credentials, or personally identifiable information into tests or examples.
7. Prefer reusable patterns over local hacks.
8. Remove duplicate logic, dead code, stale aliases, and non-standard handling when encountered
   inside the slice boundary.
9. Update docs, context, runbooks, contracts, and wiki source when platform or repository truth
   changes.
10. Treat merged-to-main and validated as the definition of done for durable truth.

## Status Vocabulary

Use these readiness statuses in control matrices, scorecards, review ledgers, and PR evidence:

| Status | Meaning |
| --- | --- |
| `Implemented` | The capability exists in code, is tested, documented where relevant, and has recent validation evidence. |
| `Partially implemented` | Some implementation exists, but coverage, behavior, documentation, or operational evidence is incomplete. |
| `Planned` | The capability is intentionally future work and must not be presented as current support. |
| `Not applicable` | The control does not apply to this repository type, with a short rationale. |
| `Unknown - requires owner review` | Current state cannot be proven from repo evidence. This is not compliant. |

Avoid softer labels such as "mostly done", "probably ready", "enterprise-grade", or
"production-ready" unless the precise evidence is attached.

## Readiness Levels

These are internal Lotus readiness levels, not external certification claims.

| Level | Name | Required Evidence |
| --- | --- | --- |
| `L0` | Unknown baseline | Repository can be built or inspected, but readiness posture is not yet measured. |
| `L1` | Governed baseline | README, repo context, CI entrypoints, dependency posture, and key ownership boundaries are truthful. |
| `L2` | CI-enforced quality | Feature lane and PR merge gate prove lint, typecheck, tests, security, contracts, and workflow hygiene for the supported scope. |
| `L3` | Operable service or product surface | Health/readiness, observability, safe errors, runbooks, runtime evidence, and supportability states exist for supported flows. |
| `L4` | Procurement-ready evidence pack | Architecture, security, operations, data, audit, release evidence, support model, control matrix, and residual-risk backlog are coherent and current. |

Repositories may progress control by control. Do not block useful refactoring because a repository is
not yet `L4`; instead, improve one measurable control and record the gap honestly.

## App-Type Applicability

### Product UI

Applies primarily to `lotus-workbench`.

Required emphasis:

1. Gateway-first integration.
2. Real backend-backed product behavior.
3. Empty, partial, degraded, stale, permission-blocked, loading, ready, and error states.
4. Browser and canonical runtime proof for promoted product surfaces.
5. No decorative trust, metrics, status, or audit state invented in the UI.

### Experience API

Applies primarily to `lotus-gateway`.

Required emphasis:

1. Stable client contracts.
2. Explicit upstream dependency map.
3. Safe fan-out behavior and bounded degradation.
4. No ownership drift into domain services' business logic.
5. Gateway publication of governed platform or domain evidence without becoming the source of truth.

### Domain Service

Applies to `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise`, `lotus-manage`, and
`lotus-report`.

Required emphasis:

1. Clear domain authority.
2. Thin controllers and strong domain/service modules.
3. Deterministic business calculations.
4. Explicit API contracts and domain vocabulary.
5. Meaningful unit, contract, integration, and migration/runtime checks.

### Shared Capability Service

Applies to `lotus-render`, `lotus-archive`, and `lotus-ai`.

Required emphasis:

1. Capability boundaries and supported use cases.
2. Safe handling of generated documents, prompts, archives, and operational diagnostics.
3. Contracted consumers and caller context.
4. Auditability, retention, access, and fallback posture where applicable.
5. No unsupported provider, AI, archive, or rendering behavior presented as available.

### Platform Governance

Applies to `lotus-platform`.

Required emphasis:

1. Standards, validators, scaffolds, and runbooks as product-quality assets.
2. Cross-repository evidence and drift detection.
3. Accurate context and skill routing.
4. CI lane templates and repository-governance policy.
5. Minimal duplication of app-local truth.

## Architectural Contract

Bank-buyable Lotus applications must have understandable boundaries.

Required controls:

1. Repository responsibility is clear in `REPOSITORY-ENGINEERING-CONTEXT.md`.
2. Public APIs and product surfaces map to an owning domain or composition layer.
3. Controllers, routes, and UI adapters stay thin.
4. Business rules live in named domain, service, policy, or calculation modules.
5. Shared rules are centralized when repeated.
6. Compatibility aliases and legacy paths are documented, tested, and retired when no longer needed.
7. New abstractions reduce complexity or enforce a real contract.

Evidence examples:

1. module map in repo context,
2. code-review ledger entry,
3. architecture doc or ADR,
4. tests proving behavior remains stable through refactor,
5. complexity and maintainability scorecard movement.

## API And Contract Quality

APIs must be explicit, stable, documented, and domain-correct.

Required controls:

1. OpenAPI/Swagger summaries, descriptions, tags, examples, response models, and error responses
   describe current implementation.
2. Request and response names use Lotus domain vocabulary.
3. Error responses are bounded and product-safe.
4. API aliases are governed, not accidental.
5. Breaking changes are intentional, documented, and validated with downstream consumers.
6. Gateway and Workbench contracts do not bypass domain authority.
7. Contract drift is caught by repo-native tests or platform validators where available.

## Data And Methodology Quality

Data and calculations must be explainable and reproducible.

Required controls:

1. Calculations have deterministic inputs and outputs.
2. Methodology docs define variables, formulas, failure behavior, and examples when the domain
   requires calculation trust.
3. Data freshness, lineage, reconciliation, and fallback states are explicit.
4. Test data is synthetic, deterministic, and representative of realistic private-banking cases.
5. No confidential client data or unmanaged local secrets appear in fixtures, docs, logs, or CI.

## Security And Privacy

Security posture is part of implementation quality.

Required controls:

1. No secrets in source, examples, tests, CI logs, or generated artifacts.
2. Authentication and authorization assumptions are explicit.
3. Permission-denied states are product-safe and do not leak raw entitlement failures.
4. Logs, metrics, traces, screenshots, evidence packs, and diagnostics avoid sensitive labels and
   payloads.
5. Dependency and container scans are governed by repo-native or platform-native gates.
6. Write-capable workflows use least privilege and avoid unsafe `pull_request_target` patterns.
7. Customer-facing or externally shareable evidence packs filter restricted telemetry and internal
   source paths.

## Observability And Supportability

Operators must be able to understand supported runtime behavior without reading source code.

Required controls:

1. Health and readiness endpoints reflect real dependencies where applicable.
2. Structured logs carry bounded event names, safe statuses, correlation, and trace context.
3. Metrics use bounded label sets and never include portfolio ids, client names, raw account ids,
   holdings, request bodies, response bodies, or trace ids as labels.
4. Degraded, stale, partial, unavailable, and permission-blocked states are explicit.
5. Runbooks describe common failures, diagnosis commands, escalation owners, and rollback or
   mitigation posture.
6. Dashboard and alert references map to implemented metric families.

## Resilience, Performance, And Scalability

Bank-buyable apps should fail safely and remain operable under load.

Required controls:

1. Timeouts, retries, idempotency, and back-pressure are explicit where the workflow requires them.
2. Long-running work has durable state, replay or recovery posture, and safe operator controls.
3. Performance gates exist for critical APIs or product paths.
4. Expensive computation is cached, batched, bounded, or made asynchronous where appropriate.
5. Docker/runtime evidence proves the service starts in the supported profile.
6. Capacity assumptions and known limits are documented when they materially affect buyers or
   operators.

## Testing Contract

Tests must prove behavior and contracts, not merely count lines.

Required controls:

1. Unit tests cover domain rules and edge cases.
2. Contract tests protect API schemas, vocabulary, aliases, and generated artifacts.
3. Integration tests cover upstream/downstream behavior that cannot be trusted from unit tests.
4. E2E or browser tests cover product surfaces that users evaluate directly.
5. Regression tests accompany bug fixes.
6. Test names describe business behavior.
7. Coverage thresholds are meaningful and ratcheted as the codebase improves.
8. Collection gates or smoke tests catch broken test discovery where useful.

## CI And Release Evidence

Use the Lotus multi-lane validation model.

Required lanes:

1. Remote Feature Lane
   Fast proof for lint, typecheck, unit, contract, workflow, and security basics.
2. Pull Request Merge Gate
   Merge-grade proof for integration, coverage, Docker, API, migration, and release evidence as
   applicable.
3. Main Releasability Gate
   Post-merge release-grade confirmation on `main`.
4. Platform End-to-End Validation
   Required when a change affects canonical product flows, gateway/upstream behavior, seeded demo
   flows, or platform runtime assumptions.

Required controls:

1. CI names are stable and match repository-governance policy.
2. Workflow action versions meet the platform runtime baseline.
3. Workflows use least privilege.
4. Release evidence includes SBOM/provenance where applicable.
5. Artifacts are useful for diagnosis and do not leak restricted data.
6. Heavy checks may run asynchronously in GitHub, but failures must be inspected and fixed forward.

## Documentation And Evidence Pack

Each app should maintain the smallest truthful documentation set for its role.

Minimum app-local evidence pack:

1. `README.md`
   Fast repo truth, commands, scope, and navigation.
2. `REPOSITORY-ENGINEERING-CONTEXT.md`
   Current repo role, boundaries, commands, constraints, and cross-links.
3. Architecture or operations docs where the repository has enough runtime or contract surface to
   justify them.
4. API, methodology, security, observability, and runbook docs where applicable.
5. `quality/` scorecard, review ledger, or equivalent when refactoring readiness is being measured.
6. `wiki/` source when operator-facing or onboarding truth is published to GitHub wiki.

Minimum platform-level references:

1. standards and templates in `platform-standards/`,
2. context routing in `context/`,
3. automation and validators in `automation/`,
4. platform contracts in `platform-contracts/`,
5. RFCs and implementation evidence where the work is RFC-driven.

## Control Matrix Template

Use this matrix shape in app-local bank-readiness docs or quality scorecards.

| Control Area | Current Status | Evidence | Gap | Next Slice |
| --- | --- | --- | --- | --- |
| Architecture | `Unknown - requires owner review` |  |  |  |
| API and contracts | `Unknown - requires owner review` |  |  |  |
| Data and methodology | `Unknown - requires owner review` |  |  |  |
| Security and privacy | `Unknown - requires owner review` |  |  |  |
| Observability and supportability | `Unknown - requires owner review` |  |  |  |
| Resilience and performance | `Unknown - requires owner review` |  |  |  |
| Testing | `Unknown - requires owner review` |  |  |  |
| CI and release evidence | `Unknown - requires owner review` |  |  |  |
| Documentation and operations | `Unknown - requires owner review` |  |  |  |

## Agent Workflow

Before substantial app work:

1. Read `AGENTS.md`.
2. Read `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`.
3. Read `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`.
4. Read the target repository's `REPOSITORY-ENGINEERING-CONTEXT.md`.
5. Read `lotus-platform/context/CONTEXT-REFERENCE-MAP.md`.
6. Read procedural memory when execution process is material.
7. Read this contract when the goal is enterprise readiness, bank-buyability, refactoring,
   production readiness, or cross-app standardization.

During work:

1. Create a feature branch from clean `main`.
2. Run stranded-truth reconciliation for docs, context, contracts, RFCs, wiki, CI, or standards
   changes.
3. Choose one measurable improvement area.
4. Implement the smallest meaningful slice.
5. Add or improve high-value tests.
6. Update scorecards, review ledgers, docs, and wiki source when truth changed.
7. Validate with repo-native commands first.
8. Push regularly and use GitHub CI for heavy lanes.
9. Inspect failures and fix forward.
10. Merge only when evidence is healthy and the PR explains changes, proof, risks, and follow-up
    backlog.
11. After merge, confirm main releasability, local/remote branch hygiene, wiki publication posture,
    and no stranded feature branches or PRs.

## PR Evidence Requirements

Every readiness PR should explain:

1. what changed,
2. which readiness controls improved,
3. what behavior was preserved or intentionally changed,
4. what tests and validation commands ran,
5. which CI lanes passed,
6. what documentation or wiki source changed,
7. what residual risks remain,
8. which follow-up backlog items should be handled next.

## Standard Agent Goal Prompt

Use this prompt shape when asking an agent to bring a Lotus app closer to the standard:

```text
Continue improving <lotus-app> toward the Lotus Bank-Buyable Engineering Contract.

Use the Lotus context reading order, the target repo's REPOSITORY-ENGINEERING-CONTEXT.md, and
lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md.

Work from a new feature branch off clean main. Make small, meaningful commits. Each commit should
improve one clear area: architecture, API quality, tests, security, observability, documentation, or
CI measurement.

Preserve behavior unless an intentional behavior change is tested and documented. Keep the app
buildable after each slice. Update scorecards, docs, context, and wiki source when truth changes.
Push regularly, monitor GitHub CI, inspect failures, and fix forward.

Do not raise or merge a PR until measurable improvement is clear, CI is healthy, docs are updated,
and the PR can explain changes, evidence, risks, and follow-up backlog. Treat merged-to-main and
validated as the definition of done.
```

## Anti-Patterns

Avoid these patterns:

1. adding documents that claim future-state readiness without implementation,
2. adding broad abstractions before a real repeated pattern exists,
3. moving logic without tests that prove behavior survived,
4. lowering gates or expanding allowlists to hide quality problems,
5. copying central standards into app repos without local interpretation,
6. leaving durable docs, contracts, or wiki truth on an unmerged branch,
7. merging a PR before main-releasability and wiki publication posture are understood,
8. treating screenshots, dashboards, or generated reports as proof when the underlying API,
   calculation, or runtime validation has not passed.

## Maintenance

Update this contract when Lotus changes its platform-wide definition of bank-buyable engineering.
Do not update it for a one-off app-local exception. Record app-local exceptions in that repository's
context, scorecard, ADR, or follow-up backlog.

When this standard changes:

1. update `platform-standards/README.md`,
2. update `context/CONTEXT-REFERENCE-MAP.md` and the context manifest when discoverability changes,
3. update generated or rendered registry companions if needed,
4. run targeted documentation and context tests,
5. run the platform wiki check before merge,
6. publish wiki source after merge only if repo-local `wiki/` changed.
