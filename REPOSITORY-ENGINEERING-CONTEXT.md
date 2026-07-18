# Repository Engineering Context

This file provides repository-local engineering context for `lotus-platform`.

For platform-wide truth, read:

1. [Lotus Quickstart Context](./context/LOTUS-QUICKSTART-CONTEXT.md)
2. [Lotus Engineering Context](./context/LOTUS-ENGINEERING-CONTEXT.md)
3. [Context Reference Map](./context/CONTEXT-REFERENCE-MAP.md)

## Repository Role

`lotus-platform` owns the shared platform layer for the Lotus ecosystem.

It is the source of truth for:

1. shared automation,
2. ingress and service-addressing operations,
3. cross-repository validation,
4. platform standards,
5. governance validators,
6. CI lane templates and repository governance policy.

## Business And Domain Responsibility

This repository does not own a business-domain API. It owns the engineering and operational system that allows the Lotus ecosystem to be run, validated, standardized, and governed as one platform.

## Current-State Summary

Current repository posture:

1. RFC-0072 implementation is active and has standardized CI lane, workflow security, container, validation, and repository-governance foundations.
2. RFC-0073 is implemented and governs the central ecosystem context system.
3. RFC-0074 is implemented and governs developer onboarding, agent ramp-up, and bootstrap synchronization.
4. Platform validation, ingress, and local runtime automation are already in active use for canonical stack bring-up and proof.
5. Front-office product-surface bring-up is governed through `lotus-workbench`; this repository owns the shared ingress and infrastructure support around that flow rather than replacing it.
6. `platform-stack` includes production-like local persistence dependencies for orchestrated
   services where readiness requires them, including `lotus-report-postgres` for `lotus-report`
   report-job and batch ledger readiness.
7. The enterprise backend refactor baseline foundation is active. The report-only generator
   `automation/generate_enterprise_backend_quality_baseline.py` writes measured quality artifacts
   under `quality/`, including `baseline_report.md`, `baseline_report.json`,
   `quality_scorecard.md`, `refactor_health_report.md`, architecture/API/CI/security rule pages,
   and a refactor decision log. `automation/Invoke-PlatformRepoChecks.ps1` validates the quality
   reporting surface through `--check`.
8. New FastAPI service scaffolds created by `automation/New-Lotus-Service.ps1` now include
   bank-buyable quality defaults: service-profile-aware README/repo-context/wiki references,
   `quality/quality_scorecard.md`, architecture rules, CI-quality-gate notes, refactor decisions,
   a layered `src/app/api|application|domain|ports|infrastructure|runtime|observability|security|resilience`
   skeleton, runtime composition boundary protection, caller-context and capability-policy
   primitives, a downstream JSON client resilience template, profile-gated idempotency/audit
   models for write-capable services, demo-claims
   documentation with Lotus status vocabulary, opt-in planned/not-certified mesh placeholders plus
   an optional `data-mesh-contract-gate` for mesh-capable scaffolds,
   report-only `architecture-boundary-report` and `quality-baseline` commands where
   `quality-baseline` depends on architecture evidence, and the
   existing OpenAPI, supported-features, AST-backed monetary-float,
   no-sensitive-content, endpoint-certification with code-owned response-example parity, coverage,
   quality-scorecard truth, observability, health/readiness, and workflow baseline gates. The
   parity control compares every baseline-certified or certified success example with a safe route
   invocation or deterministic callable and permits dynamic values only through explicit
   field-level normalizers. Parseable but stale aliases, blockers, fields, types, or values fail.
   The generated PR auto-merge helper now warns and skips auto-merge when
   `LOTUS_AUTOMERGE_TOKEN` is
   absent, preserving non-`GITHUB_TOKEN` merge semantics without creating a permanent red helper
   check for repositories that require manual/release-actor rebase merge. Generated services also
   include `make monetary-float-guard`, which blocks money-like `float` annotations, literals,
   return annotations, and conversions while allowing operational floats such as timeout seconds.
   Generated services include a tested `scripts/clean_generated_artifacts.py` utility, `make clean`
   wiring, and CI-contract protection so cleanup remains safe, prunes `.git`, `.venv`, and
   `node_modules`, and removes only known local cache/build/coverage artifacts. Generated services
   also include `make source-observability-contract-gate`, which blocks raw
   `print()`, direct Python logging, and low-level `log_event` bypasses in `src/app` while the
   generated request diagnostic helper logs route templates instead of raw URL paths. Generated
   services also include `make operation-metric-contract-gate`, which protects bounded
   `*_operation_events_total` metric vocabulary, safe operation labels, and forbidden sensitive
   operation attribute keys before service-specific business operations are implemented. Detailed
   usage and generated feature documentation lives in
   `docs/onboarding/LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md`. Generated test targets now expose
   `UNIT_TESTS`, `INTEGRATION_TESTS`, and `E2E_TESTS` path overrides so focused fix-forward
   validation can stay on the repo-native Makefile surface instead of falling back to ad hoc
   pytest commands. Generated workflows now consume the same surface with `make test-unit` and
   `make test-${{ matrix.suite }}-coverage`, and the generated CI contract gate rejects raw
   workflow-level `pytest` shortcuts or missing suite coverage targets.
9. `automation/Sync-EnterpriseBackendRefactoringInstructions.ps1` now treats
   `context/playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md` as the canonical source and
   supports `-CheckOnly` drift detection for app-local deployed copies under
   `docs/architecture/ENTERPRISE_BACKEND_REFACTORING_INSTRUCTIONS.md`. Its default backend scope is
   resolved from `automation/repos.json`; use `-Repositories` only for bounded rollout slices.
10. `automation/generate_automation_inventory.py` writes `quality/automation_inventory.*` so cleanup
    work can separate genuinely dead automation from under-documented but maintained scripts.
11. Durable standards, runbooks, architecture notes, reports, onboarding, and archived legacy mirrors
    live under `docs/` with [docs/README.md](./docs/README.md) as the index. Repo-root Markdown is
    intentionally limited to `README.md`, `AGENTS.md`, and `REPOSITORY-ENGINEERING-CONTEXT.md`.
12. Cross-repository Python policy validators must load each application in an isolated interpreter
    using its real package import root. Do not load package modules as synthetic top-level files or
    reuse generic package names such as `app` across repositories in one interpreter.

## Architecture And Module Map

Primary areas:

1. `automation/`
   PowerShell and Python automation for standards validation, platform checks, ingress helpers, governance, and runtime orchestration.
2. `platform-standards/`
   Governing standards, templates, and baseline contracts for repositories and workflows.
3. `platform-contracts/`
   Machine-readable platform contract families including API vocabulary, domain vocabulary, and
   RFC-0084 domain-data-product governance, including the RFC-0086 source manifest for repo-native
   declarations in `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise`,
   `lotus-report`, and `lotus-manage`, plus the governed identifier and temporal semantics registry
   and trust metadata registry used by those declarations.
   This area also owns the cross-service cost-attribution schema and decimal methodology.
   Applications provide bounded resource-observation digests and consume verified evidence; they
   do not own authoritative billing exports, shared-platform allocation, or official FinOps
   reconciliation.
   This area also owns the versioned bank-readiness control catalog. The catalog is the sole
   machine-readable authority for `BR-NNN` definitions and mappings; standards, skills, context,
   generated plans, and wiki pages reference it instead of copying it.
4. `generated/`
   Platform-generated discovery artifacts, including the RFC-0088 domain-product catalog and
   dependency graph derived from governed domain-data-product declarations.
5. `platform-stack/`
   Shared runtime assets, ingress stack material, and environment-level infrastructure definitions.
6. `rfcs/`
   Platform and ecosystem RFCs.
7. `context/`
   The central context system introduced by RFC-0073.
8. `docs/`
   Durable standards, architecture notes, operations runbooks, onboarding, reports, documentation
   governance, and archived legacy mirrors.
9. `tests/unit/`
   Contract tests for platform validators, automation, standards, and documentation governance.
10. `wiki/`
   canonical authored source for GitHub wiki publication and platform-level onboarding summaries.
11. `docs/documentation/`
   deep documentation governance and layering guidance for Lotus documentation surfaces.
12. `thought-leadership/`
   non-product personal-brand content workflows, including LinkedIn thought-leadership drafts,
   ledgers, themes, and voice guidance. This area preserves drafting memory for authentic,
   non-confidential, Lotus-adjacent professional content and must not be treated as product truth,
   customer evidence, or platform marketing material.
13. `quality/`
   enterprise backend refactor baseline, scorecard, quality gate rules, security findings tracker,
   and refactor decision log. This is measured refactor evidence and planning truth, not generated
   product output.

## Runtime And Integration Boundaries

Runtime model:

1. platform automation is executed through Python and PowerShell tooling,
2. local validation and stack control interact with many Lotus repositories,
3. this repository governs but does not replace repository-local quality ownership.

Boundary rules:

1. platform-wide truth belongs here,
2. repository-local truth must remain in the owning repository,
3. cross-repo validation should be encoded once here rather than reimplemented ad hoc elsewhere,
4. `platform-stack` is not the primary front-office product bring-up path when `lotus-workbench` already owns the governed populated UI runtime,
5. cross-domain data-product governance contracts now live under `platform-contracts/` and should be
   treated as platform contract infrastructure rather than repository-local metadata.
6. generated domain-product discovery artifacts are derived platform outputs and should not redefine
   ownership or dependency truth by hand.
7. `platform-contracts/domain-data-products/domain-product-source-manifest.v1.json` records which
   repositories are included from repo-native sibling declarations and which, if any, still need
   temporary platform mirrors.
8. `automation/generate_domain_product_discovery.py` validates the included repo-native declaration
   set as one federated source before writing generated catalog and graph artifacts.
9. `automation/query_domain_product_discovery.py` is the platform-owned self-serve query surface
   for generated catalog and graph artifacts; it must remain read-only and must not replace contract
   validation or gateway-facing discovery APIs.
10. `generated/domain-product-certification-report.json` and `.md` are derived RFC-0087 trust
   certification artifacts over the generated catalog and dependency graph.
11. `platform-contracts/trust-telemetry/` and `automation/validate_trust_telemetry.py` define the
   RFC-0087 runtime telemetry contract that producer and consumer repos should target before their
   telemetry can be certified.
12. `automation/generate_live_trust_certification.py` turns validated RFC-0087 telemetry snapshots
   into deterministic live trust certification artifacts under `output/trust-certification/`.
13. First-wave RFC-0087 producer telemetry snapshots now live in repo-native
   `contracts/trust-telemetry/` directories in `lotus-core`, `lotus-performance`, `lotus-risk`, and
   `lotus-advise`; platform validation accepts those snapshots and combined live trust generation
   certifies all four without issues.
14. RFC-0086 is implemented for the first-wave repo-native rollout. `lotus-ai` is consciously not
   included as a first-wave producer or consumer declaration participant until it owns a stable
   governed product or catalog-consuming capability. Transitional platform mirror declarations are
   retained only as compatibility evidence and must not be active source paths in generated catalog
   artifacts.
15. RFC-0085 is implemented/proven for the first-wave gateway read-only publication path:
   `lotus-gateway` exposes catalog, detail, dependency graph, and live trust certification APIs
   under `/api/v1/domain-products` while reading platform-generated artifacts rather than owning
   product truth.
16. RFC-0088 is implemented/proven for first-wave self-serve discovery:
   `lotus-workbench` exposes `/data-products`, consumes gateway through the BFF only, and renders
   real catalog, dependency, lifecycle, approved-consumer, certification, trust, unavailable,
   loading, empty, stale/attention, and error states.
17. Gateway PR #136 and Workbench PR #97 are merged, so RFC-0085, RFC-0087, and RFC-0088 are now
   implemented and merged for the first-wave mesh surface across platform, gateway, and Workbench.
18. `rfcs/RFC-GOVERNANCE-STANDARD.md` is the durable rule for new and reopened
   implementation-bearing RFCs: include the second-last code-review/governance slice and the final
   documentation/context/wiki/skills/branch-hygiene slice.
19. RFC-0089 is implemented for first-wave mesh certification enforcement. The platform-owned gate
    lives in `automation/mesh_certification_gate.py`, writes operator artifacts to
    `output/mesh-certification/`, runs as an advisory platform repo-check smoke, and supports local
    blocking proof with sibling producer, gateway, and Workbench repositories.
20. RFC-0090 is implemented for GitHub cross-repo mesh certification enforcement. The workflow
    `.github/workflows/mesh-certification-gate.yml` checks out `lotus-platform`, first-wave
    producer repositories, `lotus-gateway`, and `lotus-workbench` in sibling layout, runs
    `automation/mesh_certification_gate.py` in blocking mode, uploads
    `output/mesh-certification/` artifacts, and remains read-only.
21. RFC-0091 is implemented. Slice 0 adds the enterprise mesh maturity matrix generator and
    generated matrix artifacts that classify every Lotus repository, first-wave product,
    candidate expansion product, and explicit non-participant posture before maturity
    implementation continues.
22. RFC-0091 Slice 1 adds `automation/generate_domain_product_onboarding.py`, a self-service
    scaffold-and-check tool for repo-native product onboarding bundles. The tool writes product
    declaration, telemetry, SLO, access, evidence, README, and checklist files to a caller-directed
    output directory; generated bundles are onboarding aids, not platform-owned product truth.
23. RFC-0091 Slice 2 adds `automation/collect_trust_telemetry.py`, a collection step that prefers
    runtime snapshots from sibling repository `output/trust-telemetry/runtime/` directories and
    records static fixture fallback explicitly in `output/trust-telemetry/collection/`.
24. RFC-0091 Slice 3 adds `platform-contracts/mesh-slo/` and
    `automation/validate_mesh_slo_policies.py`; the mesh certification gate now evaluates
    telemetry against first-wave SLO policies and reports policy drift as certification issues.
25. RFC-0091 Slice 4 adds `platform-contracts/mesh-access/` and
    `automation/validate_mesh_access_policies.py`; the mesh certification gate validates access
    policy presence and shape before gateway or Workbench can present entitled discovery.
26. RFC-0091 Slice 5 adds `platform-contracts/mesh-evidence/` and
    `automation/generate_mesh_evidence_pack.py`; certification-history records and evidence-pack
    manifests are generated from derived mesh certification artifacts with audience-based field
    filtering.
27. RFC-0091 Slice 6 promotes `lotus-report:ClientReportEvidencePack:v1` and
    `lotus-manage:PortfolioActionRegister:v1` into the enterprise maturity wave. The later
    DPM source-readiness expansion promotes `lotus-core:DpmSourceReadiness:v1`, so mesh
    certification now treats seven products as required.
28. RFC-0091 Slice 7 extends the mesh certification gate into the enterprise maturity gate. The gate
    now reports operator-facing maturity check families for telemetry, SLO, access, lifecycle,
    evidence, catalog, gateway, and Workbench drift; validates evidence-policy and lifecycle drift;
    and writes both RFC-0089 `mesh-*` artifacts and RFC-0091 `enterprise-mesh-*` artifacts.
29. RFC-0091 Slice 8 centralizes the maturity-wave scope in
    `automation/mesh_maturity_scope.py`; platform automation must import that module rather than
    copying required-product lists into new validators or generators.
30. RFC-0091 Slice 9 completes final documentation, agent context, wiki, skills-routing, and
    branch-hygiene readiness updates. The durable skills decision is to tighten
    `context/LOTUS-SKILL-ROUTING-MAP.md` instead of creating a new dedicated mesh skill.
31. `platform-contracts/lifecycle-authority/` owns the cross-repository signed-decision and key
    discovery interface for bank lifecycle authority integrations. Platform governs schemas and
    producer certification evidence but cannot issue legal, records, privacy, erasure, or purge
    decisions. `automation/validate_lifecycle_authority_contracts.py` blocks semantic drift and
    evidence-free production promotion.
31. RFC-0092 is implemented. `automation/generate_enterprise_mesh_operating_report.py` builds the
    production mesh operating report from current enterprise certification status and optional
    certification-history records. `automation/mesh_certification_gate.py` writes
    `enterprise-mesh-operating-report.json` and `.md` on every gate run so operators can see
    production-ready versus limited-history posture, drift trends, regressions, product operating
    posture, escalation owners, and state-specific guidance.
32. The final durable mesh handoff is `docs/operations/enterprise-mesh-completion-handoff.md`.
    The machine-readable closure ledger is `generated/enterprise-mesh-closure-ledger.json`, and
    the published wiki landing page is `wiki/Enterprise-Mesh-Status.md`.
33. RFC-0095 is implemented for first-wave heartbeat-driven monitoring and attention surfacing.
    `automation/Run-Heartbeat.ps1` and `automation/run_heartbeat.py` generate advisory derived
    heartbeat artifacts under `output/heartbeat/`; `automation/heartbeat_sources.py` consumes
    configured source artifacts for GitHub PR monitor, RFC-0094 background-run ledger, wiki
    publication posture, agent-context validation, enterprise mesh operating posture, and bounded
    `lotus-ai` workflow-pack runtime status; `automation/heartbeat_state.py` preserves first-seen
    posture and explicit non-blocking suppressions. `automation/validate_heartbeat_contracts.py`
    certifies the contract, examples, runner config, and suppression policy in the platform repo
    check lane. Heartbeat output remains advisory and does not replace source truth.
34. RFC-0096 is implemented for governed multi-agent delegation. The platform owns the delegation
    policy contract, delegated task ledger helper, return-envelope and main-agent review discipline,
    optional heartbeat attention adapter for delegated task posture, and future-agent AGENTS/context
    guidance. Delegated work remains evidence for the accountable main agent; it is not review, PR
    approval, wiki publication, or merge authority.
35. RFC-0104 is implemented for first-wave scope. Platform-owned evidence now tracks durable batch
    materialization/status/control, scheduler identity, dispatch/recovery, internal execution,
    bounded worker/runtime/scheduler processes, gateway batch APIs, scheduler selectors, and
    gateway scheduler administration plus Workbench gateway-backed explicit single-portfolio batch
    operation across the sibling repos. RFC-0105 observability/replay, RFC-0106 security
    certification, and RFC-0107 production certification remain pending.
36. RFC-0105 implementation has completed Slice 0 platform scaffold hardening, Slice 1
    `lotus-report` observability structure cleanup, and Slice 2 cross-service trace and structured
    logging proof after RFC-0104 closure. Platform truth now says RFC-0105 may consume RFC-0104
    batch, gateway, Workbench, and scheduler-admin identifiers as source-backed observability
    inputs; future FastAPI service scaffolds now default to correlation-id plus trace-id
    propagation, `lotus-report` now owns runtime correlation, request, trace, structured-log, and
    safe operator lookup vocabulary in `src/app/observability.py`, and gateway/report/render/archive
    now preserve caller correlation and trace identifiers through live batch-to-archive proof while
    suppressing malformed `traceparent` headers for non-W3C trace IDs. The next implementation wave
    must continue with operator status and diagnostics APIs before mutating rerender/regenerate/
    replay commands.
37. `docs/demo/canonical-dpm-demo-story.md` and `wiki/Canonical-DPM-Demo-Story.md` are the
    governed cross-app canonical DPM demo story for `PB_SG_GLOBAL_BAL_001`. They must stay tied to
    the canonical demo-data contract, Workbench panel registry, platform QA wrapper, and merged
    owning-repository evidence; they must not promote external OMS execution, PM scoring,
    client-communication lineage, autonomous AI decisioning, or other unsupported target-state
    claims.
38. The canonical front-office contract and Workbench panel registry now include RFC-0027
    advisory-copilot proof as `advisory.advisory_copilot`, with Gateway-backed route
    `/api/v1/advisory-copilot/actions`, source-owned `lotus-advise` supportability, and explicit
    boundaries from client-ready publication, autonomous advice, external client communication,
    and OMS/order/fill/settlement posture.
39. `docs/standards/Lotus Data Mesh Standard.md` and `wiki/Data-Mesh-Standard.md` are the durable
    platform standard and wiki entry point for Lotus data mesh meaning, ecosystem app roles,
    certification controls, automation, onboarding workflow, and anti-patterns. Future app agents
    should use this standard before promoting a product as mesh certified.
40. `docs/standards/Lotus Client Demo Certification Standard.md` and
    `wiki/Client-Demo-Certification.md` are the durable platform standard and wiki entry point for
    client-demo claim states, evidence requirements, demo pack structure, canonical front-office
    proof, and explicit boundaries. Future client-demo material must distinguish
    implementation-backed, bounded-preview, diagnostic, planned, and unsupported claims.
    `docs/demo/client-demo-pack-template.md` and `wiki/Client-Demo-Pack-Template.md` provide the
    complete client-demo pack structure for the client brief, business story, demo sequence, claim
    table, evidence map, boundary register, rehearsal plan, and follow-up register.
41. Platform repo-contract workflows now checkout and sibling-link `lotus-idea` with the other
    governed source repositories because the domain-product source manifest includes
    repo-native `lotus-idea` declarations. Do not remove that checkout unless the manifest is
    changed at the same time. Canonical front-office QA also includes `lotus-idea` by default; do
    not restore an opt-in flag or skip readiness/teardown evidence as a shortcut.
42. `codex/skills/lotus-endpoint-certification-loop/references/named-success-family-closure.md`
    is the governed workflow for multi-shape caller/source endpoint-family closure. It requires
    goal re-read checkpoints, issue-first ownership, deterministic inventory, application-backed
    and DTO-serialized named examples, source-port-only fakes, non-candidate no-write proof, exact
    OpenAPI/ledger parity, durable context evidence, and PR-to-main release/wiki/branch hygiene.
    Central engineering context, procedural memory, and skill routing link to this source; the
    skill manifest is unchanged because no skill was added, moved, renamed, or reclassified.
43. `automation/Invoke-Canonical-FrontOffice-QA.ps1` uses
    `automation/canonical_docker_ownership.py` to produce a read-only, provenance-bearing cleanup
    plan before mutation. A resource is in scope only when its exact canonical Compose project and
    working-directory labels match the declared runtime roots (or it is the exact direct-ingress
    singleton). Cleanup delegates to repository-scoped Workbench Compose teardown; daemon-wide
    Lotus/PBWM/performance prefix deletion is prohibited. A reused project name from a different
    working directory, including a nested Git worktree under that directory, is a blocking
    ownership conflict. Residual Compose volumes or images without
    a live container that proves the expected working directory are also ambiguous and must block
    mutation. Use `-CleanPlanOnly` to review
    `output/front-office-qa/cleanup-plan-latest.json` without mutation.

## Repo-Native Commands

Use these commands as the primary local contract:

1. feature-lane repo checks
   `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature`
2. PR-merge repo checks
   `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane pr-merge`
3. main-releasability repo checks
   `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane main-releasability`
4. platform validation lane
   `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformValidationLane.ps1 -ValidationProfile core-performance-green-lanes`
5. platform demo-readiness certification, report-only in CI until governance promotion
   `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformDemoReadinessCertification.ps1 -ScenarioMode fresh_seed`
6. targeted unit contract tests
   `python -m pytest tests/unit -q`
7. domain-product discovery artifact generation
   `python automation/generate_domain_product_discovery.py --generated-at-utc 2026-04-19T00:00:00Z`
8. domain-product discovery self-serve query
   `python automation/query_domain_product_discovery.py list-products --approved-consumer lotus-risk`
9. domain-product trust certification artifact generation
   `python automation/generate_domain_product_certification.py --generated-at-utc 2026-04-19T00:00:00Z`
10. trust telemetry snapshot validation
   `python automation/validate_trust_telemetry.py <snapshot-file-or-directory>`
11. live trust certification generation
   `python automation/generate_live_trust_certification.py <snapshot-file-or-directory> --generated-at-utc <UTC timestamp>`
12. mesh certification gate, platform-only advisory smoke
   `python automation/mesh_certification_gate.py --mode advisory --generated-at-utc 2026-04-20T00:00:00Z --skip-publication-checks`
13. mesh certification gate, branch-current repo-native declaration preview
   `python automation/mesh_certification_gate.py --mode advisory --generated-at-utc 2026-04-20T00:00:00Z --catalog-source current-repo-native --skip-publication-checks`
14. mesh certification gate, local blocking proof with sibling repos
   `python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos`
15. GitHub cross-repo mesh certification gate
   `.github/workflows/mesh-certification-gate.yml`
16. enterprise mesh maturity matrix generation
   `python automation/generate_enterprise_mesh_maturity_matrix.py --generated-at-utc 2026-04-20T00:00:00Z`
17. enterprise mesh maturity matrix freshness check
   `python automation/generate_enterprise_mesh_maturity_matrix.py --check --generated-at-utc 2026-04-20T00:00:00Z`
18. domain-product onboarding bundle scaffold
   `python automation/generate_domain_product_onboarding.py --repository lotus-report --product-name ClientReportEvidencePack --product-version v1 --authoritative-domain reporting --product-family client_reporting --output-directory output/domain-product-onboarding/lotus-report-client-report-evidence-pack`
19. domain-product onboarding bundle check
   `python automation/generate_domain_product_onboarding.py --repository lotus-report --product-name ClientReportEvidencePack --product-version v1 --output-directory output/domain-product-onboarding/lotus-report-client-report-evidence-pack --check`
20. trust telemetry collection for RFC-0091 runtime-vs-fixture proof
   `python automation/collect_trust_telemetry.py --generated-at-utc 2026-04-20T00:00:00Z`
21. mesh SLO policy validation
   `python automation/validate_mesh_slo_policies.py`
22. mesh access policy validation
   `python automation/validate_mesh_access_policies.py`
23. mesh evidence pack generation
   `python automation/generate_mesh_evidence_pack.py --generated-at-utc 2026-04-20T00:00:00Z --audience customer-authorized`
24. enterprise mesh operating report generation
   `python automation/generate_enterprise_mesh_operating_report.py --generated-at-utc 2026-04-20T00:00:00Z`
25. agent engineering contract validation
   `python automation/validate_agent_engineering_contracts.py`
26. delegated task ledger create/update/review helper
   `python automation/delegation_task_ledger.py --help`
27. heartbeat contract validation
   `python automation/validate_heartbeat_contracts.py`
28. enterprise backend quality baseline generation and surface validation
   `python automation/generate_enterprise_backend_quality_baseline.py --write --check`
29. enterprise backend refactoring instruction copy drift check
   `powershell -ExecutionPolicy Bypass -File automation/Sync-EnterpriseBackendRefactoringInstructions.ps1 -CheckOnly`
30. automation discoverability inventory generation and surface validation
   `python automation/generate_automation_inventory.py --write --check`
31. supported-claim register validation
   `python automation/validate_supported_claim_register.py --path platform-contracts/supported-claims/examples/rfc0028-advisory-bank-demo-supported-claims.valid.json`
32. digest-based deployment promotion manifest validation
   `python automation/validate_deployment_promotion_manifest.py`
33. rounding governance compliance matrix generation
   `powershell -ExecutionPolicy Bypass -File automation/Validate-Rounding-Governance.ps1`
34. platform mesh and demo standard documentation contract tests
   `python -m pytest tests/unit/test_lotus_platform_standards_docs.py -q`
35. validated repository-native detached task
    `powershell -ExecutionPolicy Bypass -File automation/Start-Background-Run.ps1 -Repository <repo> -TargetType <make|npm|python|powershell> -Target <target> -ExpectedHead <sha> -RequireClean -RequiredArtifact <repo-relative-pattern>`
    with PID plus culture-independent process-start identity reconciliation; PowerShell
    JSON-deserialized timestamps must be normalized by type rather than locale-formatted and parsed
    back.

## Validation And CI Expectations

`lotus-platform` uses explicit CI lanes:

1. `Remote Feature Lane`
2. `Pull Request Merge Gate`
3. `Main Releasability Gate`
4. `Platform End-to-End Validation`

The platform repo checks entrypoint is the local truth for most repository validation. Keep it aligned with workflow reality.

`automation/generate_enterprise_backend_quality_baseline.py --check` is a freshness gate for stable
material quality metrics. After a slice changes source files, Python function count, max
complexity, max function length, or materially changes unit test collection count, regenerate the
accepted baseline with `--write --check` instead of leaving stale report-only evidence checked in.
Exact total source-line count is context-only because it proved too noisy for deterministic
freshness gating. Unit test collection count is checked with a small tolerance because GitHub and
local environments can differ by one or two collected tests due environment-specific collection
behavior.

`automation/validate_auto_merge_releasability.py` validates the registered Lotus repositories'
auto-merge and exact-main releasability workflow posture. It requires `LOTUS_AUTOMERGE_TOKEN`
auto-merge, rebase merge intent, a merged-PR `main-releasability.yml` dispatcher, and
`workflow_dispatch` on Main Releasability. Temporary rollout gaps must be explicit in
`platform-contracts/ci-governance/auto-merge-releasability-exceptions.v1.json` with owner, reason,
issue URL, exact violations, and expiry.

`automation/validate_mainline_commit_provenance.py` validates GitHub or local Git verification for
the exact commit under validation. Mainline releasability must fail on unsigned or otherwise
unverified commits unless
`platform-contracts/ci-governance/mainline-commit-provenance-exceptions.v1.json` contains an exact
repository, commit SHA, verification reason, owner, issue URL, and unexpired exception.

Important documentation expectations:

1. platform README and wiki work is partially governed by unit-level documentation contract tests,
2. central context, onboarding, automation, and standards docs should stay cross-linked rather than
   being rewritten as parallel prose silos,
3. repo-local `wiki/` content should summarize platform role, operator flows, and ecosystem
   boundaries without duplicating the entire RFC or `context/` tree,
4. common targeted documentation contract packs include
   `tests/unit/test_engineering_context_system_contract.py`,
   `tests/unit/test_dev_ingress_status_automation_contract.py`, and
   `tests/unit/test_front_office_runtime_automation_contract.py`.

## Standards And RFCs That Govern This Repository

Most relevant current governance:

1. [RFC-0071](./rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md)
2. [RFC-0072](./rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md)
3. [RFC-0073](./rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md)
4. [Continuous Integration, Validation, and Release Governance Standard](./docs/standards/Continuous%20Integration%2C%20Validation%2C%20and%20Release%20Governance%20Standard.md)
5. [Platform Integration Architecture Bible](./docs/architecture/Platform%20Integration%20Architecture%20Bible.md)

## Known Constraints And Implementation Notes

1. This repository often references or validates other repositories, so stale repository inventory is a real drift risk.
2. Standards-only changes are not complete unless scaffold, validator, or runbook impact is considered.
3. Avoid duplicating platform-wide policy across many files; prefer one central source of truth plus contract tests.
4. Use GitHub for the expensive validation matrix when practical, and use targeted local proof for faster fix-forward work.
5. when harvesting legacy strategy or wiki material, reclassify it against current Lotus ownership
   boundaries before reusing it in `lotus-platform`; old ecosystem narrative can still help, but
   repo docs must speak in current Lotus vocabulary and current architecture.
6. New-service scaffold changes should be centralized in `automation/New-Lotus-Service.ps1` and
   protected by scaffold contract tests rather than copied into individual service repositories.
7. Enterprise refactor quality artifacts under `quality/` must remain synchronized with README,
   wiki, repo context, central context, and skill guidance whenever a quality signal moves from
   report-only to a blocking gate or the baseline measurement scope changes.
8. New-service scaffold changes should keep the bank-buyable defaults current so new Lotus apps do
   not start below the enterprise quality bar.
9. Certified endpoint examples require code-owned runtime parity evidence. A second documentation
   literal or schema-only assertion does not prove current response truth.

## Context Maintenance Rule

Update this document when:

1. platform-owned repository responsibilities change,
2. repo-native commands or lane entrypoints change,
3. validation or ingress automation changes materially,
4. the repository's current RFC rollout posture changes,
5. dominant local patterns or key directories change.
6. documentation layering or publication posture changes materially.

## Cross-Links

1. [Lotus Quickstart Context](./context/LOTUS-QUICKSTART-CONTEXT.md)
2. [Lotus Engineering Context](./context/LOTUS-ENGINEERING-CONTEXT.md)
3. [Context Reference Map](./context/CONTEXT-REFERENCE-MAP.md)
4. [Repository Engineering Context Contract](./context/Repository-Engineering-Context-Contract.md)
5. [Lotus Developer Onboarding](./docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
6. [Lotus Agent Ramp-Up](./docs/onboarding/LOTUS-AGENT-RAMP-UP.md)
