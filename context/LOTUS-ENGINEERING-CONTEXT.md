# Lotus Engineering Context

This is the canonical ecosystem context for Lotus engineering work.

Use this file after the [Lotus Quickstart Context](./LOTUS-QUICKSTART-CONTEXT.md). Use the repository-local `REPOSITORY-ENGINEERING-CONTEXT.md` for implementation truth inside a specific repository.

## Purpose

Lotus is a governed private banking technology ecosystem. It is not a loose collection of apps.

The ecosystem is designed to support:

1. portfolio management,
2. performance analytics,
3. risk analytics,
4. advisory workflows,
5. reporting and evidence production,
6. platform-grade runtime, validation, CI, ingress, and governance.

The engineering goal is a premium, production-critical, banking-grade platform where architecture clarity, operational rigor, and domain correctness are non-negotiable.

## Application Roles

### Product and experience layer

1. `lotus-workbench`
   The primary product UI. It should present a coherent banking-grade user experience and consume the unified contract from `lotus-gateway`.

2. `lotus-gateway`
   The experience API and composition layer. It provides the governed client contract for UI experiences and mediates access to domain services.

### Domain-authoritative services

1. `lotus-core`
   Authoritative for portfolio, booking, account, holding, mandate, and transaction domain data.

2. `lotus-performance`
   Authoritative for performance metrics, period analytics, and related review data.

3. `lotus-risk`
   Authoritative for drawdown, attribution, concentration, rolling risk, and related analytics.

4. `lotus-advise`
   Advisory workflow and recommendation capability.

5. `lotus-manage`
   Portfolio-management and operational workflow capability.

6. `lotus-report`
   Reporting and document generation capability.

7. `lotus-render`
   Deterministic document rendering capability for governed reporting flows.

8. `lotus-archive`
   Generated-document archive, retrieval, retention, legal hold, access-audit, and lifecycle capability.

9. `lotus-ai`
   Shared AI capability service used behind governed product and platform flows.

### Platform and governance

1. `lotus-platform`
   Owner of shared automation, ingress, standards, validation, CI governance, and environment-level operational guidance.

## Architectural Relationships

The canonical relationship model is:

1. `lotus-workbench` consumes `lotus-gateway`,
2. `lotus-gateway` consumes or aggregates domain-authoritative services,
3. domain services remain authoritative for their business domain,
4. `lotus-report` may orchestrate reporting flows across upstream domain services and `lotus-render`,
5. `lotus-archive` owns durable generated-document archive records and retrieval governance after document generation,
6. `lotus-platform` governs how the ecosystem is run, validated, and standardized.

### Boundary rules

1. UI features must not be superficially invented at the presentation layer.
2. Experience composition belongs in `lotus-gateway`, not scattered into direct UI-to-service coupling.
3. Domain-specific business logic belongs in the authoritative service or a governed view-model layer, not as uncontrolled UI logic.
4. Standards, validators, and platform automation are part of the architecture and should be maintained with the same discipline as product code.

## Domain Data Product Governance

For cross-domain governed data products:

1. domain repositories remain authoritative for product truth,
2. `lotus-platform/platform-contracts/domain-data-products/` is the platform-owned contract family
   for producer and consumer declarations introduced by RFC-0084,
3. `lotus-platform/platform-contracts/domain-vocabulary/domain-data-product-semantics.v1.json`
   is the governed identifier, temporal-semantic, and trust-vocabulary registry that those
   declarations must reference,
4. `lotus-platform/platform-contracts/domain-vocabulary/domain-data-product-trust-metadata.v1.json`
   is the governed trust metadata field registry, evidence-class registry, and lineage-bundle
   registry for those declarations,
5. `lotus-gateway` may publish and compose APIs around those products, but it does not become the
   product authority or product registry,
6. the current RFC-0086 included repo-native rollout set is `lotus-core`, `lotus-performance`,
   `lotus-risk`, `lotus-advise`, `lotus-report`, and `lotus-manage`,
7. current governed producer repositories are `lotus-core`, `lotus-performance`, `lotus-risk`, and
   `lotus-advise`; `lotus-report` and `lotus-manage` are current consumer-declaration
   participants,
8. `lotus-ai` is not a first-wave domain-product producer or consumer declaration participant until
   it owns a stable governed product or catalog-consuming capability,
9. producer and consumer declarations should stay explicit, version-aware, registry-backed, and
   validator-backed.

## Domain Vocabulary Governance

For analytics period naming:

1. `lotus-platform/platform-contracts/domain-vocabulary/canonical-performance-periods.v1.json`
   is the platform-owned vocabulary for performance, risk, reporting, and front-office period
   values,
2. new or materially changed APIs should expose canonical period codes such as `YTD`, `1Y`, `3Y`,
   `5Y`, `SI`, `YEAR`, and `EXPLICIT`,
3. legacy service values such as `ONE_YEAR`, `THREE_YEAR`, `FIVE_YEAR`, and `ITD` may be accepted
   only when listed as aliases in the platform contract and normalized internally,
4. Swagger/OpenAPI examples should use canonical period codes unless they are explicitly
   documenting a legacy compatibility path,
5. services should not introduce local period enum values without first updating the platform
   vocabulary with semantics, required fields, ownership, and migration posture.

For RFC-0087 live trust telemetry:

1. `platform-contracts/trust-telemetry/` owns the governed telemetry snapshot contract,
2. `automation/validate_trust_telemetry.py` validates snapshots against the generated catalog and
   trust vocabulary,
3. first-wave producer snapshots live in `lotus-core`, `lotus-performance`, `lotus-risk`, and
   `lotus-advise` under `contracts/trust-telemetry/`,
4. `automation/generate_live_trust_certification.py` creates derived live-trust certification
   artifacts from validated snapshots,
5. gateway and Workbench must consume certified trust posture through governed APIs rather than
   inventing decorative trust state.

For the RFC-0085/RFC-0088 first-wave publication and discovery path:

1. `lotus-gateway` is the API publication face for generated domain-product discovery and trust
   evidence; it must not become a product registry or domain-product authority,
2. gateway exposes read-only domain-product catalog, detail, dependency graph, and trust
   certification APIs under `/api/v1/domain-products`,
3. gateway reads platform-generated discovery and live-trust artifacts and returns explicit
   unavailable or degraded posture when certified platform evidence is absent,
4. `lotus-workbench` exposes the first-wave self-serve discovery UI at `/data-products`,
5. Workbench discovery must consume gateway through the BFF only and must not read platform files
   directly or invent decorative trust state,
6. RFC-0085, RFC-0087, and RFC-0088 are implemented and merged for the first-wave mesh surface:
   platform PR #149 closed platform evidence, gateway PR #136 merged the publication/trust API
   surface, and Workbench PR #97 merged the `/data-products` discovery UI.
7. RFC-0089 is implemented for first-wave mesh certification enforcement:
   `automation/mesh_certification_gate.py` composes the domain-product catalog, source manifest,
   RFC-0087 telemetry validation, live trust certification, gateway publication drift checks, and
   Workbench gateway/BFF-only consumption checks. Platform CI runs an advisory gate smoke through
   `automation/Invoke-PlatformRepoChecks.ps1`; local blocking proof with sibling repositories uses
   `python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos`.
8. RFC-0090 is implemented for GitHub cross-repo mesh certification enforcement:
   `.github/workflows/mesh-certification-gate.yml` checks out first-wave producer repositories,
   `lotus-gateway`, and `lotus-workbench` next to `lotus-platform`, runs the RFC-0089 gate in
   blocking mode, uploads mesh-certification artifacts, and keeps product authority in producer
   repositories and platform-generated evidence rather than gateway or Workbench.
9. RFC-0091 is implemented for enterprise mesh maturity. Slice 0 provides the generated maturity
   matrix, Slice 1 provides `automation/generate_domain_product_onboarding.py` for
   scaffold-and-check onboarding bundles, Slice 2 provides
   `automation/collect_trust_telemetry.py` for runtime-preferred telemetry collection, Slice 3
   provides `platform-contracts/mesh-slo/` plus `automation/validate_mesh_slo_policies.py`, and
   Slice 4 provides `platform-contracts/mesh-access/` plus
   `automation/validate_mesh_access_policies.py`. Slice 5 provides
   `platform-contracts/mesh-evidence/` plus `automation/generate_mesh_evidence_pack.py` for
   certification-history and evidence-pack manifests. Slice 6 promotes
   `lotus-report:ClientReportEvidencePack:v1` and
   `lotus-manage:PortfolioActionRegister:v1` into the enterprise maturity wave.
   Slice 7 turns mesh certification into an enterprise maturity gate with operator-facing
   telemetry, SLO, access, lifecycle, evidence, catalog, gateway, and Workbench check families,
   evidence-policy validation, lifecycle drift validation, and RFC-0091 `enterprise-mesh-*`
   artifacts. Slice 8 centralizes the six-product maturity-wave scope in
   `automation/mesh_maturity_scope.py`; new platform mesh automation should import that module
   instead of copying product lists. Slice 9 completed the final documentation, context, wiki,
   skills-routing, and branch-hygiene readiness updates.
   Generated onboarding bundles are starter artifacts for owning repositories; they are not
   platform-owned product truth until the owner replaces placeholders, adds repo-native tests,
   emits telemetry, and passes certification. Static telemetry fixtures remain explicit fallback
   evidence and must not masquerade as runtime telemetry. Mesh SLO, access-policy, and
   evidence-pack drift are certification evidence and must not be handled as separate decorative
   reports. Public customer evidence packs must not expose restricted telemetry paths, source
   artifacts, or consumer entitlement details.
10. RFC-0104 is implemented for first-wave batch reporting scope. Slice 0 strengthens
   `automation/New-Lotus-Service.ps1` so newly scaffolded FastAPI services include
   Swagger-quality health, liveness, readiness, and metadata endpoints plus a generated OpenAPI
   quality gate that checks summaries, descriptions, tags, response descriptions, 2xx responses,
   and success examples. Slice 1 adds the `lotus-report` `report_batch_orchestrator` module
   boundary and planned selector/frequency vocabulary while keeping
   `BATCH_RUNTIME_SUPPORTED = False`. Slice 2 adds internal durable `report_batch` and
   `report_batch_item` materialization for explicit portfolio lists and selected subsets, with
   source-backed validation and idempotent duplicate prevention. Slice 3 adds deterministic
   schedule-cycle materialization and scheduled idempotency identity for monthly, quarterly,
   semi-annual, yearly, and explicit cycles. Later slices add certified materialization/status/
   control APIs, dispatch/lease/back-pressure, retry/recovery controls, internal item execution
   through report-job/snapshot/render/archive handoff, bounded run-once, bounded runtime-pass,
   daemonized worker-process execution, config-backed internal scheduler-process materialization
   with explicit/all-active/inline-manifest scheduler selectors, gateway-facing batch
   materialization/status/control/operator-run APIs, gateway-facing scheduler administration, and
   Workbench gateway/BFF-backed explicit single-portfolio batch operation. RFC-0105
   dashboards/replay, RFC-0106 security certification, and RFC-0107 production certification remain
   pending later work.
11. RFC-0105 implementation has started with Slice 0 platform scaffold hardening after RFC-0104
    closure. It may consume RFC-0104 durable batch, gateway, Workbench, and scheduler-administration
    identifiers as source-backed observability inputs. The platform scaffold now defaults future
    FastAPI services to correlation-id plus trace-id propagation. The next implementation wave
    should continue with observability contracts, trace/log/operator lookup, and data-protection
    proof before mutating rerender, regenerate, or replay commands.
12. The current RFC-0091 maturity-wave required product set is six products: core portfolio state,
    performance returns, risk metrics, advisory proposal lifecycle, report evidence pack, and
    management action register.
13. RFC-0092 is implemented for production mesh operations. The mesh certification gate now writes
    `enterprise-mesh-operating-report.json` and `.md` alongside certification status artifacts.
    The operating report consumes current certification status and optional certification-history
    records, then reports operating state, limited-history posture, drift trend, regression since
    prior certified posture, product operating posture, escalation ownership, and operator guidance.
    It is operational evidence, not product truth and not customer evidence export.
14. The durable mesh completion handoff is
    `docs/operations/enterprise-mesh-completion-handoff.md`, with machine-readable closure evidence
    in `generated/enterprise-mesh-closure-ledger.json` and published human status in
    `wiki/Enterprise-Mesh-Status.md`. Use those artifacts instead of old chat history when
    continuing mesh expansion or briefing a new agent.

For RFC governance:

1. new and reopened implementation-bearing RFCs must include a second-last code review,
   loose-end-tightening, API certification, and platform-governance slice,
2. they must also include a final documentation, agent context, wiki, skills/guidance assessment,
   and branch-hygiene slice,
3. legacy RFCs are not rewritten only for formatting, but must be upgraded when reopened.

For RFC-0093/RFC-0094 agent engineering governance:

1. use `context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md` when resuming long-running work,
   delegating bounded subtasks, monitoring detached checks, or recovering after context compaction,
2. preserve operational identifiers exactly in handoffs and summaries: repository, branch, PR
   number, commit SHA, check name, RFC id, file path, endpoint, contract name, portfolio id, and
   task status,
3. use `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json` as the
   contract for detached engineering task identity, lifecycle, cleanup, evidence, delegation, and
   context-preservation fields,
4. treat `output/background-runs.json` as local automation evidence for background runs and GitHub
   Actions as the source of truth for GitHub check status,
5. use `automation/Run-Heartbeat.ps1` when a governed advisory attention snapshot is needed across
   background-run, mesh, context, workflow-pack, wiki, or PR-monitor evidence,
6. treat heartbeat output under `output/heartbeat/` as derived advisory evidence only; it does not
   replace GitHub, local background-run ledgers, mesh certification, wiki source, context
   validators, or `lotus-ai` runtime APIs as source truth,
7. use `platform-contracts/agent-engineering/delegation-policy-contract.v1.json` for governed
   RFC-0096 delegation profiles, input envelopes, output envelopes, write-scope rules, and
   heartbeat attention identifiers,
8. keep delegated implementation work accountable to the main agent: returned patches are evidence,
   not review, and require main-agent diff review plus focused tests before integration,
9. do not delegate immediate critical-path blockers, broad repo cleanup, overlapping write scopes,
   PR merge, or wiki publication without explicit main-agent ownership and review,
10. promote durable lessons into governed docs, context, wiki source, skills, validators, or RFC
   follow-ups instead of relying on chat history.

## Front-Office Runtime Governance

For local front-office product bring-up, demo readiness, UI screenshots, and populated panel validation:

1. prefer the `lotus-front-office-runtime` skill when choosing agent routing for these tasks,
2. use the governed canonical runtime in `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`,
2. use `lotus-workbench` live commands such as `npm run live:stack:up`, `npm run live:validate`, and `npm run live:stack:down`,
3. treat `PB_SG_GLOBAL_BAL_001` as the governed seeded reference portfolio unless a task explicitly requires another portfolio,
4. treat `lotus-platform/context/contracts/canonical-front-office-demo-data-contract.json` and `lotus-platform/context/contracts/canonical-front-office-demo-data-invariants.json` as the source of truth for canonical front-office dataset governance,
5. treat `lotus-platform/context/contracts/workbench-panel-registry.json` as the source of truth for governed Workbench panel identifiers, owners, support states, and screenshot ownership,
6. use `lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory <path>` when a platform-owned run summary and caller-directed demo screenshot pack are required,
7. treat `lotus-platform/platform-stack` as shared ingress and infrastructure support, not as the canonical front-office product bring-up path.

Do not improvise a parallel front-office stack sequence from `lotus-platform/platform-stack` when the governed `lotus-workbench` runtime already covers the required UI surfaces and seeded-data validation flow.

Demo-ready screenshots must be captured only after canonical API, calculation, and panel validation passes. Pre-validation captures are diagnostic artifacts and must not be presented as demo-ready evidence.
Machine-readable runtime evidence should preserve canonical contract identity and version, not just portfolio and route parameters.
This runtime and dataset posture is governed by `RFC-0076` and the governed panel-surface posture by `RFC-0077`.

## Engineering Standards

Lotus engineering is expected to be:

1. clean,
2. modular,
3. readable,
4. domain-correct,
5. reliable,
6. scalable,
7. observable,
8. production-ready.

### Required delivery posture

Always:

1. look for opportunities to reduce complexity,
2. make the codebase cleaner, more readable, more maintainable, and more modular,
3. make code and test improvements that materially improve reliability and maintainability,
4. add or update documentation wherever necessary,
5. leave the codebase cleaner than you found it,
6. write meaningful, high-value tests and avoid superficial coverage,
7. keep making small, meaningful commits,
8. remove dead code, duplication, and non-standard legacy handling when encountered,
9. ensure every UI feature is genuinely backed by supported backend functionality.

### Clean code principles

1. prefer explicit, well-scoped responsibilities over convenience coupling,
2. avoid duplicated policy or logic across repositories and layers,
3. prefer shared reusable patterns over page-local or file-local hacks,
4. make naming precise, domain-correct, and stable,
5. remove stale abstractions when the product direction changes,
6. keep public contracts intentional and documented.

### Modular design principles

1. separate platform truth from repository-local truth,
2. separate domain authority from composition and presentation,
3. prefer well-defined modules and validators over ad hoc scripts,
4. treat automation and runbooks as product-quality operational code,
5. push repeatable patterns into standards, templates, skills, or validators once they recur.

## Testing Standards And Validation Model

Lotus follows the test pyramid and meaningful coverage posture defined by platform standards.

Expected validation layers include:

1. fast unit tests for local logic,
2. contract and integration tests for domain boundaries,
3. browser or end-to-end validation where product experience matters,
4. platform validation for canonical stack bring-up, ingress, seeded data, and cross-app flows,
5. CI lane validation with fast feature gates, PR merge gates, main releasability gates, and platform end-to-end validation where applicable.

### Test quality rules

1. test business and contract behavior, not just implementation trivia,
2. add regression tests for every real defect you fix,
3. prefer deterministic, minimal, high-signal tests,
4. remove stale assertions that no longer reflect the product contract,
5. keep repo-native commands truthful to the actual CI contract.

## Documentation Quality Standards

Documentation in Lotus is part of the delivery artifact.

Update docs when:

1. architecture changes,
2. commands change,
3. runtime or validation flow changes,
4. standards or CI rules change,
5. a repeatable pattern is worth codifying,
6. a repository’s current-state reality materially changes.

Central docs own platform truth.

Repository-local docs own repo truth.

When a repository uses a GitHub wiki, the repo-local `wiki/` directory should be treated as the
canonical authored source and the `*.wiki.git` repository should be treated as publication
transport only. PR validation now runs
`automation/Sync-RepoWikis.ps1 -CheckOnly -Repository lotus-platform` for platform wiki drift, and
agents should run the same command with the target repository name before merging wiki-affecting
changes. After merge, publish with `automation/Sync-RepoWikis.ps1 -Publish -Repository <repo-name>`;
use `-AllRepositories` for coordinated platform-wide audits or publication sweeps.

Do not duplicate central policy prose into every repo unless repo-local interpretation is required.

## API Quality And UI Alignment

Lotus APIs and product surfaces are expected to be:

1. clear,
2. consistent,
3. domain-correct,
4. fully modeled,
5. documented,
6. aligned with authoritative ownership boundaries.

### API and UI rules

1. use business-language contracts rather than generic field naming,
2. keep gateway contracts governed and explicit,
3. do not ship UI flows that are not supported by backend capability,
4. do not mask backend gaps with decorative UI or fabricated content,
5. keep empty, partial, loading, ready, and error states explicit for data modules.

## Performance, Reliability, And Production Readiness

Lotus delivery should optimize for:

1. front-office trust,
2. operational clarity,
3. performance and low latency,
4. strong reliability,
5. maintainable observability,
6. stable production posture.

This means:

1. avoid unnecessary runtime cost and repeated work,
2. treat latency and performance regressions as product quality issues,
3. keep Docker, ingress, runtime, and validation paths repeatable,
4. provide evidence for readiness through CI artifacts, validation summaries, and truthful checks.

## Naming And Vocabulary Standards

Naming should reflect banking and investment domain reality.

Preferred vocabulary should come from:

1. private banking,
2. portfolio management,
3. performance analytics,
4. risk analytics,
5. advisory workflows,
6. reporting and investment-review language.

### Naming rules

1. file names should describe stable responsibility,
2. functions and objects should use domain-correct verbs and nouns,
3. APIs should prefer explicit business meaning over generic placeholders,
4. avoid generic labels such as `widget`, `thing`, `item`, or `stats` when a domain term exists,
5. use domain-correct terms such as `portfolio`, `benchmark`, `mandate`, `allocation`, `attribution`, `drawdown`, `exposure`, `supportability`, `readiness`, `booking`, `holding`, `proposal`, and `evidence` where appropriate.

## Agent Operating Expectations

Agents working in Lotus are expected to operate like disciplined banking-grade engineers.

### Mandatory posture

1. choose the smallest correct working set of context,
2. use standards, skills, validators, and runbooks before improvising a new local pattern,
3. prefer async GitHub-backed heavy execution when it is more efficient than repeated heavyweight local reruns,
4. promote repeatable patterns into durable guidance,
5. keep repo and platform context current when reality changes.

### Skills and working methods

Use the right skill or workflow for the task:

1. `lotus-front-office-runtime` for canonical populated Workbench runtime, demo screenshots, and panel-proof tasks,
2. backend delivery governance for backend repos,
3. frontend delivery governance for UI work,
4. PR pre-merge governance for merge preparation,
5. QA or platform validator skills for stack and platform validation,
6. RFC or documentation skills for governance work.

When a repeatable pattern emerges:

1. update the relevant context document,
2. update an existing skill,
3. add a new skill if the pattern is durable and recurring,
4. add a validator or scaffold rule if executable enforcement is valuable.

## Human-Maintained Memory

The central curated memory layer is:

1. [Platform Engineering Ledger](./platform-engineering-ledger.md)
2. [Recent Architectural Decisions Digest](./recent-architectural-decisions-digest.md)

These files exist to preserve high-value practical guidance and recent platform reality across sessions.

## Structured Reusable Context

The machine-readable ecosystem map is:

1. [lotus-context-manifest.json](./lotus-context-manifest.json)

Use the manifest for:

1. ecosystem inventory,
2. repo roles,
3. canonical commands,
4. dependency and authority lookups,
5. context-path discovery.

## Procedural Memory

The governed procedural-memory layer lives in:

1. [Procedural Memory Index](./PROCEDURAL-MEMORY-INDEX.md)

Use it when you need durable guidance for:

1. change execution,
2. PR loops and async monitoring,
3. validation depth selection,
4. fix-forward response patterns.

## Related References

Use the [Context Reference Map](./CONTEXT-REFERENCE-MAP.md) to find:

1. active standards,
2. active RFCs,
3. runbooks,
4. domain references,
5. repository-local context documents.

## Task Routing Guidance

Use the [Task Routing Guide](./TASK-ROUTING-GUIDE.md) when you want the smallest correct reading path for:

1. frontend and product-surface work,
2. backend API and domain-service work,
3. cross-app integration and platform validation work,
4. standards, RFC, and governance work.

Use the [Lotus Skill Routing Map](./LOTUS-SKILL-ROUTING-MAP.md) when you need the smallest correct
skill boundary for:

1. canonical front-office runtime work,
2. platform QA vs product-surface proof,
3. delivery governance vs PR governance,
4. async GitHub-heavy execution posture.

Use [Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md) when you need a human-readable view of:

1. application roles and categories,
2. domain authority ownership,
3. standards currently in force,
4. active RFCs that still materially govern the ecosystem.
