# Lotus App Issue Discovery Lens Catalog

Use this catalog to plan review batches. Pick one lens or a coherent group; inspect code before
raising issues.

## Contents

1. [Canonical Lens Labels](#canonical-lens-labels)
2. [Core Lens Groups](#core-lens-groups)
3. [Enterprise Readiness Extension Lenses](#enterprise-readiness-extension-lenses)
4. [Baseline Lens Queue](#baseline-lens-queue)
5. [Repository Review Profiles](#repository-review-profiles)
6. [Lens Definition Of Done](#lens-definition-of-done)
7. [Campaign Coverage Model](#campaign-coverage-model)
8. [User Prompt To Canonical Lens Map](#user-prompt-to-canonical-lens-map)
9. [Finding Decision Tree](#finding-decision-tree)
10. [Evidence Strength Rubric](#evidence-strength-rubric)
11. [Required Issue Anchors By Lens Family](#required-issue-anchors-by-lens-family)
12. [Lens-Specific Search Starters](#lens-specific-search-starters)
13. [Duplicate Check Keywords](#duplicate-check-keywords)
14. [Severity Calibration](#severity-calibration)

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
| Secure development lifecycle and threat modeling | `lens/secure-development-threat-modeling` |
| Identity, authentication, and authorization | `lens/identity-access-management` |
| Container and workload runtime hardening | `lens/container-runtime-hardening` |
| Vulnerability management and penetration-test readiness | `lens/vulnerability-management` |
| Incident response | `lens/incident-response` |
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
| Entitlements and tenant isolation | `lens/entitlements-tenant-isolation` |
| Regulatory compliance and records | `lens/regulatory-compliance-records` |
| Deployment and environment parity | `lens/deployment-environment-parity` |
| Business continuity and disaster recovery | `lens/business-continuity-disaster-recovery` |
| SLO, capacity, and cost management | `lens/slo-capacity-cost-management` |
| Release rollout and compatibility | `lens/release-rollout-compatibility` |
| Operator control plane | `lens/operator-control-plane` |
| Data governance and privacy lifecycle | `lens/data-governance-privacy-lifecycle` |
| License and IP compliance | `lens/license-ip-compliance` |
| Localization and market conventions | `lens/localization-market-conventions` |
| Customer-impact failure modes | `lens/customer-impact-failure-modes` |
| Change-management audit | `lens/change-management-audit` |
| Support escalation workflows | `lens/support-escalation-workflows` |
| Third-party vendor risk | `lens/third-party-vendor-risk` |
| Accessibility and inclusive design | `lens/accessibility-inclusive-design` |
| Product workflow usability | `lens/product-workflow-usability` |
| Client communication suitability | `lens/client-communication-suitability` |
| Data quality and reconciliation | `lens/data-quality-reconciliation` |
| Migration and backfill readiness | `lens/migration-backfill-readiness` |
| Environment supply-chain provenance | `lens/environment-supply-chain-provenance` |
| API consumer experience | `lens/api-consumer-experience` |
| Mobile and responsive device readiness | `lens/mobile-responsive-device-readiness` |
| AI model governance | `lens/ai-model-governance` |
| AI data boundaries | `lens/ai-data-boundaries` |
| AI evaluation quality | `lens/ai-evaluation-quality` |
| AI explainability and audit | `lens/ai-explainability-audit` |
| AI safety and abuse controls | `lens/ai-safety-abuse-controls` |
| AI human oversight | `lens/ai-human-oversight` |
| AI cost, latency, and reliability | `lens/ai-cost-latency-reliability` |
| AI agent tool governance | `lens/ai-agent-tool-governance` |

Use these cross-cutting labels when useful:

| Label | Use |
| --- | --- |
| `issue-discovery` | Every issue created from this skill. |
| `impact/correctness` | Defects that can produce wrong business, calculation, lifecycle, or API behavior. |
| `impact/security` | Security, privacy, authorization, secret-handling, or abuse-protection risk. |
| `impact/operability` | Observability, readiness, diagnostics, recovery, or supportability risk. |
| `impact/performance` | Latency, scalability, batching, pagination, query, or resource-efficiency risk. |
| `impact/architecture` | Boundary, dependency, modularity, contract, or ownership risk. |
| `impact/compliance` | Regulatory, records, audit, legal, licensing, or policy-adherence risk. |
| `impact/customer-experience` | User workflow, accessibility, client communication, or customer-impact risk. |

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
| Event and outbox contracts | events, logical and physical topic identity, schema versions, DLQ, replay, idempotency, outbox emission | schema drift, logical/physical routing mismatch, direct Kafka publishing, broad replay success checks, weak poison-message handling, missing duplicate-delivery tests |
| Data mesh, data product, and trust telemetry contracts | domain data-product declarations, trust telemetry snapshots, producer/consumer declarations, platform catalog validators, mesh catalog publication, SLO/access/evidence policies | governed product declarations without runtime trust proof, missing freshness/lineage/blocking evidence, stale approved-consumer truth, mesh catalog entries not backed by runtime evidence |
| Capability and supported-feature publication | supported-feature ledgers, capability registries, Gateway publication, Workbench consumption, README/wiki feature claims, demo/publication contracts | published features without implemented or certified endpoints, stale Workbench/Gateway capability truth, UI-visible claims backed by unsupported behavior |
| Evidence and proof contracts | implementation proofs, certification artifacts, scorecards, validation outputs, generated evidence packs, proof schemas, evidence lineage | proof artifacts not reproducible from current code, unbounded/manual evidence, stale scorecards, missing evidence fingerprints or contract provenance |
| Source contract and dependency semantics | upstream source products consumed by the app, required trust metadata, source lifecycle identity, restatement/version/correction semantics | consumer contracts missing source-event identity, lifecycle/correction fields lost during normalization, fail-open dependency posture |
| Database operations | migrations, relationship inventory, destructive cleanup/reseed, repository query shape, indexes, unique constraints, lock/lease flows, connection/session lifecycle, query tests | hand-maintained cleanup omits durable children, cleanup is non-atomic, unbounded scans, N+1 reads, no uniqueness for idempotency, unsafe update races, missing index for hot filter/sort paths |
| Data model quality | ORM models, migrations, indexes, identifiers, temporal fields, lineage fields | missing unique constraints, weak temporal semantics, overloaded identifiers, no lineage/audit fields |
| Transaction lifecycle | booking states, trade/settlement dates, cancellations, corrections, reversals, corporate actions | missing linked legs, weak correction model, incomplete cash/product-side linkage |
| Position lifecycle | holdings, tax lots, availability, pledge/margin/collateral, corporate-action restatements | missing lot lineage, weak position type, no availability state, incorrect cash/security separation |
| Calculations and methodology | cost basis, accrued interest, valuation, FX, cashflows, income, P&L, tax, performance inputs | Decimal precision gaps, product-specific calculation assumptions, missing methodology examples/tests |
| Domain vocabulary | names in APIs, models, fields, docs, metrics, tests | ambiguous `client_id`, generic status names, non-standard transaction/instrument terms |
| Validation and idempotency | request validation, exact governed resource/work identity, duplicate handling, idempotency keys, conflict semantics | unrelated row/page/aggregate satisfies readiness, same key/different payload not rejected, logical/physical idempotency mismatch, weak replay/correction validation, missing bounded error codes |
| Auditability and lineage | audit records, source batch, correlation IDs, evidence fingerprints | missing source identity, raw payload retention, no correlation chain across event/API/DB |
| Monitoring and observability | structured logs, metrics, traces, health/readiness, diagnostics, alert rules, dashboards, SLO/error-budget evidence | raw logging, sensitive labels, missing route templates, health not dependency-aware, no alert/dashboard path for critical failures |
| Security and privacy | authn/authz, CORS, headers, secrets, sensitive data, API abuse controls | missing authorization boundaries, unsafe CORS, secret leakage, raw exception exposure |
| Secure development lifecycle and threat modeling | threat models, data flows, trust boundaries, abuse cases, security acceptance criteria, negative tests, expiring exceptions | material feature has no threat review, trust boundary is undocumented, abuse case lacks a mitigation/test, exception has no owner or expiry |
| Identity, authentication, and authorization | identity architecture, OIDC/OAuth/workload identity, server-side policies, object/tenant/portfolio scope, privileged action audit | UI-only authorization, production-enablable local bypass, wrong-scope access, shared long-lived service credentials, unaudited privilege change |
| Container and workload runtime hardening | production Docker stage, base image, runtime user, capabilities, filesystem, resource limits, network/egress, built-image entrypoint/assets | root runtime, mutable or bloated image, leaked build secret, missing worker asset, broad privilege, absent shutdown/health smoke |
| Vulnerability management and penetration-test readiness | SAST/SCA/container findings, SBOM-to-version mapping, severity policy, exception expiry, disclosure path, external-test scope and retest evidence | scanner installed but unenforced, finding lacks owner/version, permanent suppression, pen-test claim without scope/retest evidence |
| Incident response | severity and escalation model, alerts, containment, rollback, credential rotation, evidence preservation, reconciliation, post-incident actions | alert has no owner/runbook, no containment or reconciliation path, unsafe diagnostic collection, corrective actions remain chat-only |
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

## Enterprise Readiness Extension Lenses

Use these lenses when the app is production-deployed, externally exposed, regulated, multi-tenant,
client-demo/publication relevant, AI-backed, agentic, or otherwise expected to be enterprise-ready.
Do not require every extension lens for every scaffold or internal prototype; record `not
applicable` in the ledger when the repo context proves the lens is outside the app boundary.

Each extension-lens issue should include:

1. **Acceptance criteria**: the implementation evidence that must exist before the finding can be
   closed.
2. **Evaluation condition**: the concrete check, runtime proof, contract test, doc/runbook review,
   or operator exercise that proves the acceptance criteria.

| Lens | Applies when | What to inspect | Typical high-value findings | Acceptance criteria | Evaluation condition |
| --- | --- | --- | --- | --- | --- |
| Entitlements and tenant isolation | APIs, UIs, data products, or workers handle user, portfolio, client, mandate, tenant, advisor, or service-scoped access | auth policies, caller context, tenant filters, row/object guards, denial tests, audit logs, Gateway/BFF propagation | cross-tenant reads, missing object-level authorization, UI-only entitlements, service tokens with broad scope, missing denial audit | authorization is enforced at the owning backend boundary; tenant/portfolio/client scope is carried through APIs, queries, events, logs, and audit; allow and deny paths are tested | focused tests prove allowed, denied, wrong-tenant, missing-scope, and service-to-service cases; logs/audit show support-safe denial evidence |
| Regulatory compliance and records | records, reports, legal hold, client communication, suitability, retention, audit, or regulated evidence is stored or published | retention rules, legal hold, audit trails, records classification, evidentiary snapshots, data residency, change history | missing retention/hold controls, mutable records without versioning, weak audit chain, unsupported client-record claims | regulated records have immutable identity/versioning, retention/hold policy, audit history, owner, and support-safe retrieval semantics | migration/contract tests, records lifecycle tests, and runbook checks prove create/read/update/correction/hold/purge behavior |
| Deployment and environment parity | the app has Docker, compose, Kubernetes, environment-specific settings, CI runtime, or deployed service manifests | Dockerfiles, compose, Helm/K8s/IaC, env templates, config validation, readiness/liveness, startup imports | local works but container import fails, prod defaults differ from CI, probes are shallow, secrets/config missing validation | local, CI, and deployment manifests run the same service entrypoint and required settings; health/readiness reflect real dependencies | Docker/import smoke, config validation tests, and readiness checks run through repo-native commands or deployment pipeline |
| Business continuity and disaster recovery | the app owns durable state, files, queues, evidence, or critical workflows | backups, restore docs, idempotency, replay/recovery, RTO/RPO docs, object-store/database recovery, migration rollback | no restore path, untested backup, no replay after partial failure, recovery docs missing exact commands | durable data has backup/restore, replay, and recovery procedures with declared RTO/RPO or explicit non-production boundary | restore/replay drill, migration rollback proof, or operator runbook exercise with recorded evidence |
| SLO, capacity, and cost management | production readiness, high-volume traffic, latency-sensitive UI/API paths, or AI/token-heavy flows exist | SLOs, latency/error metrics, rate limits, load tests, capacity assumptions, resource budgets, token/cost budgets | no SLO, unbounded fan-out, missing saturation metrics, expensive AI calls without budget, no capacity evidence | SLOs or readiness targets are documented; capacity/cost risks have limits, metrics, alerts, and tests where practical | load/performance smoke, dashboard/alert contract, budget test, or capacity worksheet tied to repo truth |
| Release rollout and compatibility | public/internal APIs, DB migrations, events, data products, UI contracts, or downstream consumers can break | versioning, migrations, feature flags, deprecation docs, rollback, blue/green/canary posture, compatibility tests | breaking change without versioning, irreversible migration, no rollback, silent event/schema incompatibility | changes are backward-compatible or explicitly versioned/deprecated; rollout and rollback paths are documented and tested | migration forward/backward proof, contract compatibility tests, deprecation docs, and release evidence |
| Operator control plane | operators need support-safe status, retry, replay, drain, pause, unblock, or diagnostic actions | admin/support APIs, control commands, RBAC, audit, dry-run, safeguards, runbooks | unsafe retry/replay, no stuck-state controls, admin actions lack audit, break-glass path uncontrolled | operator actions are scoped, authorized, audited, idempotent or guarded, and documented with safe next steps | operator API tests, audit assertions, runbook exercise, and negative authorization tests |
| Data governance and privacy lifecycle | the app stores or emits personal, client, portfolio, document, prompt, telemetry, or restricted data | classification, minimization, masking, retention, erasure/anonymization, approved consumers, lineage, logs/metrics | raw PII in logs/events, missing data classification, no retention/erasure boundary, broad data exports | data fields are classified; sensitive data is minimized, masked, retained, deleted, and shared according to policy | static sensitive-content scans, schema/contract checks, retention tests, and log/metric redaction tests |
| License and IP compliance | dependencies, generated artifacts, third-party data, templates, market data, or AI-generated assets are used | license manifests, package metadata, attribution, generated content provenance, data-use terms, binary/image assets | incompatible license, missing attribution, unclear generated-content ownership, third-party data copied into repo | license/IP obligations are identified, approved, documented, and enforced for dependencies and artifacts | license scanner, dependency manifest review, artifact provenance checks, and docs/NOTICE validation |
| Localization and market conventions | user-visible dates, currencies, markets, jurisdictions, calendars, statements, or reporting periods exist | time zones, business calendars, settlement calendars, currencies, formats, language, tax/jurisdiction flags | UTC/local confusion, wrong currency rounding, weekend business days, hard-coded SG/US assumptions, non-localized reports | market conventions are explicit, tested, and configurable or bounded to the documented jurisdiction | golden tests for dates/currency/business days/time zones plus docs naming supported markets |
| Customer-impact failure modes | UI/API/workflow failures can affect advisor, PM, client, operations, or downstream consumers | degraded states, partial data, dependency failures, empty/stale states, user messages, retry behavior, status pages | blank UI, misleading success, partial data not marked, retries duplicate actions, client-facing error leaks internals | failure states are explicit, support-safe, actionable, and do not overstate success or completeness | dependency-failure tests, UI/API degraded-state proof, and runbook/customer-impact classification |
| Change-management audit | production or governed changes affect data, APIs, workflows, model prompts, configuration, or supported-feature truth | release approvals, change records, migration plans, audit trail, PR evidence, feature flags, rollback owners | no trace from change to issue/PR/proof, unapproved config changes, unsupported docs updated without implementation | changes have owner, approval/evidence trail, rollout/rollback plan, and implementation-backed docs | PR/release evidence checklist, change log, migration proof, and post-release verification |
| Support escalation workflows | support teams need L1/L2/L3 routing, diagnostics, incident response, or client-impact triage | runbooks, escalation owners, diagnostic bundles, support-safe identifiers, alert routing, incident templates | no escalation owner, support cannot correlate IDs, diagnostic steps expose sensitive data, L1 must inspect DB | support path names owners, severity, inputs, diagnostic commands, safe identifiers, and escalation criteria | runbook review plus dry-run incident exercise or diagnostic API evidence |
| Third-party vendor risk | external APIs, SaaS, cloud providers, data vendors, model providers, or managed services are used | SLAs, timeouts, data sharing, vendor security posture, outage behavior, contract boundaries, fallback | hidden vendor dependency, no timeout/SLA, sensitive data sent without policy, vendor outage breaks core path | vendor dependency, data classes, timeout/retry/SLA, outage mode, and owner are documented and tested | adapter tests, vendor-failure simulation, data-sharing review, and runbook evidence |
| Accessibility and inclusive design | user-facing UI, dashboards, PDFs, reports, email content, or generated documents exist | semantic HTML, keyboard nav, focus, contrast, ARIA, PDF tagging, captions, error messaging | inaccessible controls, missing keyboard path, poor contrast, untagged PDFs, charts without text alternatives | supported surfaces meet the declared accessibility baseline and do not block keyboard/screen-reader workflows | axe/Playwright checks, keyboard walkthrough, PDF accessibility proof, and manual residual-risk notes |
| Product workflow usability | users perform repeated, high-value operational, advisory, PM, support, or client-service workflows | task flows, navigation, state persistence, error recovery, defaults, bulk actions, confirmation copy | workflows require excessive clicks, destructive action unclear, status hidden, users cannot recover from common errors | core workflows are efficient, clear, reversible or safely confirmed, and backed by real APIs | task-based walkthrough evidence, UX regression tests, screenshots/video where useful, and API support proof |
| Client communication suitability | client-ready or advisor-use communications, reports, recommendations, AI text, disclaimers, or approvals exist | disclaimers, approval state, suitability gates, audience classification, publication controls, client/advisor split | advisor-only content exposed to clients, missing disclaimer, unsupported recommendation, no approval lineage | communications carry audience, approval/suitability status, disclaimer, source evidence, and publication boundary | content contract tests, approval workflow tests, generated-document proof, and supported-feature docs |
| Data quality and reconciliation | source data, analytics, reports, data products, positions, transactions, or evidence packs depend on quality thresholds | freshness, completeness, reconciliation, trust scores, breaks, source corrections, restatements, exception handling | stale data marked ready, reconciliation breaks hidden, source corrections not propagated, no trust telemetry | quality dimensions are measured, surfaced, and block or degrade outputs according to policy | data-quality tests, reconciliation fixtures, trust telemetry/evidence checks, and degraded-state proof |
| Migration and backfill readiness | schemas, historical data, event replay, new derived fields, or cutover flows change | migration scripts, backfill jobs, checkpointing, idempotency, validation totals, rollback/cutover plan | one-shot backfill cannot resume, no row-count/hash proof, migration ignores historical edge cases | migrations/backfills are resumable or explicitly bounded, validated, observable, and rollback-aware | dry-run/backfill tests, row-count/hash reconciliation, checkpoint proof, and rollback/cutover docs |
| Environment supply-chain provenance | build artifacts, containers, deployment packages, SBOM, signing, or runtime images matter | SBOM, artifact signing, pinned base images, immutable image tags, OCI image labels, version/build metadata endpoint, build provenance, vulnerability scan, reproducible builds, CI run metadata, image digest capture, Kubernetes manifests, build secret handling | mutable image tags, unpinned image, no SBOM, unsigned release artifact, build uses mutable dependency source, missing OCI revision/source/created labels, missing Git branch or CI run ID, image digest not captured, version endpoint drifts from image labels, deploy manifests use mutable tags, build secrets leak through ARG/ENV | artifacts have provenance, dependency locks, vulnerability posture, signing/SBOM policy, digest-based deployment, same-image promotion, and the deployable-image checklist below where required | SBOM/scanner output, `docker image inspect` or registry OCI label proof, image digest checks, release-manifest proof, CI artifact/build-log digest proof, signature and provenance attestation verification, Kubernetes manifest check, version endpoint contract test comparing runtime metadata to image/build metadata, build provenance evidence, and secret-leak scan |
| API consumer experience | APIs are consumed by Gateway, Workbench, SDKs, external tools, support scripts, or partner services | examples, SDK/client helpers, error taxonomy, pagination, versioning, mock/server fixtures, changelog | API technically works but consumers cannot integrate safely, poor errors, no examples, unstable operation IDs | API has stable docs, examples, error model, compatibility posture, and consumer tests | generated OpenAPI/client checks, consumer contract tests, examples, and Gateway/Workbench integration proof |
| Mobile and responsive device readiness | UI/product surfaces may be used on laptops, tablets, mobile, or constrained viewports | responsive layout, touch targets, table behavior, modal overflow, real device/browser viewport tests | desktop-only layout, clipped controls, tiny touch targets, horizontal scroll hiding critical action | supported viewport/device classes are named and tested; unsupported classes are documented truthfully | Playwright viewport screenshots, interaction tests, and visual review evidence |
| AI model governance | an app uses LLMs, embeddings, classifiers, recommenders, model providers, or model-assisted workflows | model inventory, approved models, versioning, ownership, fallback, eval gate, model-change audit | unknown model, untracked version, no fallback, model change bypasses review, unsupported live-provider claim | model/provider/version/owner/purpose are declared; model changes are gated by eval and rollback posture | model registry or config contract, eval run, fallback test, and PR/release evidence |
| AI data boundaries | prompts, retrieval, embeddings, model inputs/outputs, feedback, traces, or tool context include client/platform data | PII handling, prompt construction, retrieval corpus, embedding store, provider data-use policy, retention | client data sent to unapproved provider, prompt logs leak PII, retrieval corpus lacks access control | AI inputs/outputs/traces are classified, minimized, access-controlled, retained, and provider-governed | prompt/log redaction tests, retrieval entitlement tests, data-use docs, and no-training/retention evidence |
| AI evaluation quality | AI outputs affect decisions, recommendations, summaries, classifications, or client/advisor workflows | golden datasets, domain assertions, hallucination checks, adversarial tests, regression thresholds, eval artifacts | demo-only prompts, no regression eval, hallucinated sources, weak domain correctness proof | eval suites cover normal, edge, adversarial, and domain-critical outputs with thresholds and owners | deterministic eval command, generated eval report, failing-case fixtures, and CI/report-only placement |
| AI explainability and audit | AI output must be explainable, cited, reviewed, or used as evidence | citations, source trace, prompt/version audit, decision log, confidence, review status | no source attribution, output cannot be reproduced, no prompt/model trace, decision audit missing | AI decisions/outputs carry enough source, prompt/model, reviewer, and evidence metadata for support | trace/audit tests, citation verification, reviewer workflow proof, and support-safe evidence pack |
| AI safety and abuse controls | AI can receive user text, external content, retrieved docs, tool results, or generate actions/content | prompt injection defenses, content filters, tool constraints, unsafe output handling, jailbreak/adversarial tests | prompt injection can override policy, unsafe content emitted, retrieved text controls tool calls | AI flows enforce input/output safety, policy hierarchy, injection resistance, and safe refusal/degradation | adversarial tests, prompt-injection fixtures, policy checks, and unsafe-output regression tests |
| AI human oversight | AI supports advice, recommendations, publication, workflow actions, or material decisions | approval gates, confidence thresholds, escalation, reviewer role, client/advisor boundary, override audit | autonomous client-impact action, no review threshold, recommendations lack suitability approval | human review/approval is required where policy demands it; thresholds and escalation are explicit and audited | workflow tests for approve/reject/escalate/override plus audit evidence |
| AI cost, latency, and reliability | AI calls are in user paths, batch workflows, or expensive/high-volume operations | token budgets, timeouts, retries, caching, batching, provider fallback, rate limits, circuit breakers | no timeout, runaway token use, provider outage blocks core app, no cost visibility | AI calls have budgets, limits, timeout/fallback/degraded behavior, and cost/latency telemetry | load/latency tests, budget guard tests, provider-failure simulation, and dashboard/metric evidence |
| AI agent tool governance | AI agents can call tools, write data, trigger workflows, access files/APIs, or delegate work | tool registry, permissions, scoped credentials, approval, dry-run, action logs, rollback, sandbox | agent has broad write token, no approval for destructive action, tool calls unaudited | tools are explicitly registered, least-privilege, audited, bounded by read/write scope, and reversible or approval-gated | tool-permission tests, action-log proof, denial tests, dry-run/rollback evidence |

### Canonical Backend Layer Flow

Use this flow as the default expected dependency direction when reviewing backend architecture,
application, domain, port, adapter, API, and mapping lenses:

1. External consumer.
2. API, controller, or route.
3. Request DTO mapper.
4. Application use case.
5. Domain model plus domain service.
6. Port or interface.
7. Infrastructure adapter.
8. Database, cache, queue, or external API.

Issue-discovery findings should flag inversions where DTOs, framework objects, ORM rows,
infrastructure clients, queue payloads, cache concerns, or external API semantics leak upward into
application/domain code, or where routes bypass request DTO mappers, use cases, ports, or adapters.
The expected fix direction should normally move mapping to boundary mappers, orchestration to
application use cases, business rules to domain models/services, and side effects behind ports and
infrastructure adapters.

### Environment Supply-Chain Provenance Checklist

When a Lotus repository builds or deploys a container image, review the image and deployment path
against this checklist:

1. The image is tagged with the Git commit SHA.
2. OCI labels include commit, Git branch/ref, repository URL, version, build time, and CI
   pipeline/run ID.
3. Release images are built and pushed by CI only, not from developer workstations.
4. The pushed image digest is captured in a release manifest or equivalent immutable evidence.
5. An SBOM is generated for the image.
6. Vulnerability scanning passes or records an approved, time-bounded exception.
7. The image is signed.
8. A provenance attestation is generated.
9. Kubernetes, Helm, or deployment manifests deploy by digest, not mutable tags.
10. The `/version` or version/build metadata endpoint exposes the same commit, Git branch/ref,
    repository, version, build time, pipeline/run ID, and image digest metadata.
11. The same immutable image is promoted across environments; later environments do not rebuild from
    source.
12. Build secrets do not leak through Dockerfile `ARG`, Dockerfile `ENV`, image history, logs, OCI
    labels, or runtime version metadata.

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
   When bank readiness is in scope, include threat modeling, identity/access, container runtime,
   vulnerability lifecycle, and incident response as distinct review families.
8. Repo organization, remote repository hygiene, and agents/context organization where layout,
   generated-artifact policy, remote branch/repo metadata, agent onboarding, or skill-routing
   discoverability affects future implementation quality.
9. Dead-code/duplication and dependency-hygiene passes when prior lenses reveal stale paths,
   repeated logic, vulnerable dependencies, or cleanup work with real behavioral or supportability
   impact.
10. Enterprise readiness extension lenses when the app is production-deployed, externally exposed,
    regulated, multi-tenant, client-demo/publication relevant, AI-backed, agentic, or expected to be
    bank-buyable from all angles. Do not force AI lenses on repos with no AI surface; record them as
    not applicable when repo context proves they are outside scope.

For every lens, record whether the pass was code-backed, docs-backed, duplicate-checked, and ledgered.

Use `scripts/plan_issue_discovery_campaign.py --repository <owner>/<repo>` to generate a
repo/profile-specific first-pass plan from this queue. The plan is a starting point only; ledger
state, active PRs, and user priority still govern the actual next lens.

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
| AI capability service or AI-backed app surface such as `lotus-ai` or any app using LLMs, embeddings, retrieval, classification, recommendations, or agentic tools | AI model governance, AI data boundaries, AI evaluation quality, AI explainability/audit, AI safety/abuse controls, AI human oversight, AI cost/latency/reliability, AI agent tool governance, entitlements/tenant isolation, data governance/privacy lifecycle |
| Platform/governance repository such as `lotus-platform` | CI/release evidence, standards/contracts, scaffold drift, repo organization, skill/context routing, agents/context organization, validation automation, docs/wiki truth |

For bank-ready or procurement-oriented campaigns, generate the control-aware queue with
`scripts/plan_issue_discovery_campaign.py --repository <owner>/<repo> --include-bank-readiness`.
The queue maps stable `BR-001` through `BR-025` controls to the selected repository profile. Use the
control ID in the ledger and issue body, but still file one issue per root cause rather than one
issue per checklist row.

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
7. bank-ready findings also record the stable `BR-NNN` control, environment layer (`local`, `ci`,
   `production`, or `recovery`), actual evidence class, status, maturity, and owner without implying
   certification from lower-class evidence.

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
| "secure development lifecycle", "threat model", "trust boundary", "abuse case", "security acceptance criteria" | `lens/secure-development-threat-modeling`, `lens/security-privacy` | threat model, data flow, assets, actors, boundaries, abuse cases, mitigations, negative tests, exception expiry |
| "identity", "authentication", "OIDC", "OAuth", "workload identity", "production auth bypass" | `lens/identity-access-management`, `lens/entitlements-tenant-isolation` | identity architecture, policy enforcement, local-bypass isolation, role/scope matrix, allow/deny/expiry tests, privileged audit |
| "container hardening", "non-root", "read-only filesystem", "capabilities", "pod security", "runtime image" | `lens/container-runtime-hardening`, `lens/environment-supply-chain-provenance`, `lens/deployment-environment-parity` | final image user/assets, security context, capabilities, filesystem, resources, egress, image scan, startup/shutdown smoke |
| "vulnerability management", "penetration test", "security finding", "remediation SLA", "exception expiry" | `lens/vulnerability-management`, `lens/dependency-hygiene`, `lens/security-privacy` | finding/version mapping, severity/exploitability, owner/due date, exception expiry, external-test scope, retest evidence |
| "incident response", "containment", "post incident", "root cause analysis", "evidence preservation" | `lens/incident-response`, `lens/support-escalation-workflows`, `lens/operational-supportability` | severity model, alert/runbook, contacts, containment/rollback/rotation, reconciliation, evidence, corrective-action tracker |
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
| "entitlements", "tenant isolation", "RBAC", "ABAC", "row-level authorization", "multi-tenant" | `lens/entitlements-tenant-isolation`, `lens/security-privacy`, `lens/auditability-lineage` | caller context, policy modules, query filters, object guards, allow/deny tests, audit logs |
| "regulatory", "records", "legal hold", "retention", "data residency", "compliance" | `lens/regulatory-compliance-records`, `lens/data-governance-privacy-lifecycle`, `lens/auditability-lineage` | retention/hold rules, record versioning, audit trails, classification, residency docs, lifecycle tests |
| "deployment parity", "Kubernetes", "Docker", "environment parity", "runtime config", "readiness probes" | `lens/deployment-environment-parity`, `lens/configuration-secrets`, `lens/runtime-composition` | Docker/compose/K8s/IaC, env templates, startup imports, config validation, health/readiness |
| "DR", "disaster recovery", "backup", "restore", "RTO", "RPO", "business continuity" | `lens/business-continuity-disaster-recovery`, `lens/operational-supportability`, `lens/resilience` | backup/restore docs, replay/recovery commands, durable state, restore drills, runbooks |
| "SLO", "capacity", "cost", "load", "resource budget", "error budget" | `lens/slo-capacity-cost-management`, `lens/performance-scalability`, `lens/observability` | SLO docs, dashboards, alerts, load tests, rate limits, capacity assumptions, cost/token budgets |
| "rollout", "backward compatibility", "deprecation", "feature flag", "rollback", "zero downtime" | `lens/release-rollout-compatibility`, `lens/api-design-governance`, `lens/database-operations` | versioning, migrations, compatibility tests, feature flags, rollback docs, consumer contracts |
| "operator control", "admin actions", "replay controls", "retry controls", "pause", "drain", "break glass" | `lens/operator-control-plane`, `lens/operational-supportability`, `lens/auditability-lineage` | support/admin APIs, permissions, audit logs, dry-run, idempotency, safeguards, runbooks |
| "data privacy lifecycle", "masking", "erasure", "anonymization", "data classification" | `lens/data-governance-privacy-lifecycle`, `lens/security-privacy`, `lens/regulatory-compliance-records` | schemas, logs, metrics, retention, deletion, masking, approved consumers, lineage |
| "license", "IP", "third-party content", "attribution", "NOTICE", "generated assets" | `lens/license-ip-compliance`, `lens/dependency-hygiene` | package licenses, NOTICE/attribution, generated assets, data-use terms, dependency manifests |
| "timezone", "currency", "calendar", "locale", "business day", "market convention", "jurisdiction" | `lens/localization-market-conventions`, `lens/calculations-methodology`, `lens/domain-vocabulary` | currency/date formatting, business calendars, rounding, market support docs, golden tests |
| "customer impact", "degraded mode", "partial data", "empty state", "stale state", "failure mode UX" | `lens/customer-impact-failure-modes`, `lens/product-workflow-usability`, `lens/operational-supportability` | dependency failures, stale/empty/error states, user messages, retries, runbook/customer-impact classification |
| "change management", "release approval", "change audit", "production change", "config change" | `lens/change-management-audit`, `lens/ci-release-evidence`, `lens/documentation-runbooks` | PR evidence, release notes, approvals, migration plans, config history, post-release verification |
| "support escalation", "L1", "L2", "L3", "incident handoff", "diagnostic bundle" | `lens/support-escalation-workflows`, `lens/operational-supportability`, `lens/observability` | runbooks, owners, severity taxonomy, safe identifiers, diagnostic APIs, alert routing |
| "vendor risk", "external API", "SaaS dependency", "model provider", "market data provider", "SLA" | `lens/third-party-vendor-risk`, `lens/downstream-integration`, `lens/security-privacy` | vendor clients, timeouts, SLAs, data-sharing docs, outage handling, adapter tests |
| "accessibility", "a11y", "inclusive design", "keyboard", "screen reader", "PDF accessibility" | `lens/accessibility-inclusive-design`, `lens/product-workflow-usability` | UI components, semantic HTML, keyboard path, contrast, ARIA, PDF tagging, accessibility tests |
| "usability", "workflow ergonomics", "user journey", "task flow", "bulk action", "confirmation" | `lens/product-workflow-usability`, `lens/api-consumer-experience`, `lens/customer-impact-failure-modes` | task flows, navigation, state persistence, confirmations, undo/recovery, API support |
| "client communication", "advisor use", "client-ready", "suitability", "disclaimer", "approval gate" | `lens/client-communication-suitability`, `lens/regulatory-compliance-records`, `lens/capability-publication` | audience classification, approval state, disclaimers, suitability evidence, publication controls |
| "data quality", "reconciliation", "freshness", "completeness", "trust score", "source correction" | `lens/data-quality-reconciliation`, `lens/data-product-trust-telemetry`, `lens/source-contract-dependency-semantics` | freshness/completeness checks, reconciliation breaks, trust telemetry, source correction handling |
| "migration", "backfill", "historical replay", "cutover", "data migration" | `lens/migration-backfill-readiness`, `lens/database-operations`, `lens/validation-idempotency` | migration/backfill scripts, checkpoints, dry runs, row-count/hash proof, rollback/cutover docs |
| "SBOM", "artifact signing", "build provenance", "image digest", "container hardening", "OCI labels", "version endpoint", "build metadata", "image signed", "provenance attestation", "deploy by digest", "same image promoted", "build secrets" | `lens/environment-supply-chain-provenance`, `lens/dependency-hygiene`, `lens/ci-release-evidence` | SBOM, image pins/digests, OCI labels, Git SHA/branch/source/build timestamp metadata, CI run ID, version endpoint parity, signing/provenance attestation evidence, scanner output, release manifest, Kubernetes digest deploys, same-image promotion evidence, build secret leak checks |
| "developer experience", "API consumer experience", "SDK", "examples", "client ergonomics" | `lens/api-consumer-experience`, `lens/api-documentation-standards`, `lens/downstream-integration` | OpenAPI, examples, SDK/client helpers, error taxonomy, operation IDs, consumer tests |
| "mobile", "responsive", "tablet", "device readiness", "viewport" | `lens/mobile-responsive-device-readiness`, `lens/accessibility-inclusive-design`, `lens/product-workflow-usability` | responsive layouts, viewport tests, touch targets, table/modals, screenshots |
| "AI", "LLM", "model", "embedding", "retrieval", "RAG", "agent", "prompt", "eval" | AI extension lenses: `lens/ai-model-governance`, `lens/ai-data-boundaries`, `lens/ai-evaluation-quality`, `lens/ai-explainability-audit`, `lens/ai-safety-abuse-controls`, `lens/ai-human-oversight`, `lens/ai-cost-latency-reliability`, `lens/ai-agent-tool-governance` | model inventory, prompt/data boundaries, retrieval corpus, eval suites, traces, safety tests, oversight workflows, token/cost budgets, tool permissions |
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
| Enterprise readiness | entitlement policy, regulated-record control, deployment manifest, DR/runbook proof, SLO/capacity/cost evidence, rollout/rollback contract, operator control, privacy lifecycle, license/IP evidence, market-convention tests, support escalation, vendor-risk contract, accessibility/usability proof, data-quality/reconciliation proof, migration/backfill proof, SBOM/provenance evidence, OCI image metadata/version endpoint parity proof, or API/mobile consumer proof |
| Bank-readiness control | stable `BR-NNN` identifier, applicable repository profile, local/CI/production or recovery gap, actual evidence class, status, maturity, owner, and non-certification boundary |
| AI readiness | model registry/config, prompt/retrieval data path, eval artifact, source/citation trace, safety/adversarial test, human approval workflow, cost/latency budget, or tool permission/action-log proof |

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

### Bank-Readiness Control System

```powershell
python <lotus-platform>\automation\validate_bank_readiness_control_catalog.py
python <skill-dir>\scripts\plan_issue_discovery_campaign.py --repository <owner>/<repo> --include-bank-readiness
rg -n "threat model|trust boundary|OIDC|OAuth|workload identity|non-root|read-only|capabilities|penetration|vulnerability|incident|containment|RPO|RTO|SBOM|provenance|rollback" README.md docs wiki src tests contracts deploy .github Dockerfile* --glob "*.md" --glob "*.py" --glob "*.json" --glob "*.yml" --glob "*.yaml"
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

### Enterprise Readiness

```powershell
rg -n "tenant|entitlement|permission|role|RBAC|ABAC|legal hold|retention|record|regulatory|compliance|data residency|backup|restore|RTO|RPO|SLO|error budget|capacity|cost|rollback|deprecation|feature flag|operator|admin|break glass|data classification|mask|erasure|license|NOTICE|timezone|currency|calendar|business day|degraded|partial|stale|support escalation|vendor|SLA|accessibility|ARIA|keyboard|client-ready|advisor-use|suitability|reconciliation|freshness|backfill|migration|SBOM|provenance|attestation|cosign|slsa|signing|org.opencontainers.image|OCI label|commit_sha|git_sha|branch|build timestamp|build_timestamp|repo URL|repository URL|GITHUB_RUN_ID|CI_PIPELINE|run ID|image digest|image_digest|release manifest|deploy by digest|image tag|/version|version endpoint|build metadata|ARG |ENV |secret|same image|promote|promotion|SDK|responsive|viewport" README.md docs wiki src tests contracts .github Makefile package.json pyproject.toml Dockerfile* --glob "*.md" --glob "*.py" --glob "*.json" --glob "*.yml" --glob "*.yaml" --glob "Makefile" --glob "*.toml"
```

### AI Readiness

```powershell
rg -n "AI|LLM|model|embedding|retrieval|RAG|prompt|completion|provider|OpenAI|AzureOpenAI|eval|evaluation|golden dataset|hallucination|citation|source trace|confidence|human review|approval|jailbreak|prompt injection|tool call|agent|token budget|rate limit|fallback|no training|PII" README.md docs wiki src tests contracts prompts output .github --glob "*.md" --glob "*.py" --glob "*.json" --glob "*.yml" --glob "*.yaml" --glob "*.ts" --glob "*.tsx"
```

## Duplicate Check Keywords

Search GitHub with both broad and specific terms:

- broad lens terms: `architecture`, `mapping`, `outbox`, `idempotency`, `pagination`,
  `OpenAPI`, `Swagger`, `duplicate endpoint`, `stale branch`, `repo description`, `tenant`,
  `DR`, `SLO`, `rollback`, `threat model`, `workload identity`, `container hardening`,
  `vulnerability management`, `incident response`, `accessibility`, `AI evaluation`,
  `prompt injection`, `model governance`
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

