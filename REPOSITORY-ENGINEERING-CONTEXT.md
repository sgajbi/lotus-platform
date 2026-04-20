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
4. `generated/`
   Platform-generated discovery artifacts, including the RFC-0088 domain-product catalog and
   dependency graph derived from governed domain-data-product declarations.
5. `platform-stack/`
   Shared runtime assets, ingress stack material, and environment-level infrastructure definitions.
6. `rfcs/`
   Platform and ecosystem RFCs.
7. `context/`
   The central context system introduced by RFC-0073.
8. `tests/unit/`
   Contract tests for platform validators, automation, standards, and documentation governance.
9. `wiki/`
   canonical authored source for GitHub wiki publication and platform-level onboarding summaries.
10. `docs/documentation/`
   deep documentation governance and layering guidance for Lotus documentation surfaces.

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
5. targeted unit contract tests
   `python -m pytest tests/unit -q`
6. domain-product discovery artifact generation
   `python automation/generate_domain_product_discovery.py --generated-at-utc 2026-04-19T00:00:00Z`
7. domain-product discovery self-serve query
   `python automation/query_domain_product_discovery.py list-products --approved-consumer lotus-risk`
8. domain-product trust certification artifact generation
   `python automation/generate_domain_product_certification.py --generated-at-utc 2026-04-19T00:00:00Z`
9. trust telemetry snapshot validation
   `python automation/validate_trust_telemetry.py <snapshot-file-or-directory>`
10. live trust certification generation
   `python automation/generate_live_trust_certification.py <snapshot-file-or-directory> --generated-at-utc <UTC timestamp>`
11. mesh certification gate, platform-only advisory smoke
   `python automation/mesh_certification_gate.py --mode advisory --generated-at-utc 2026-04-20T00:00:00Z --skip-publication-checks`
12. mesh certification gate, local blocking proof with sibling repos
   `python automation/mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos`
13. GitHub cross-repo mesh certification gate
   `.github/workflows/mesh-certification-gate.yml`

## Validation And CI Expectations

`lotus-platform` uses explicit CI lanes:

1. `Remote Feature Lane`
2. `Pull Request Merge Gate`
3. `Main Releasability Gate`
4. `Platform End-to-End Validation`

The platform repo checks entrypoint is the local truth for most repository validation. Keep it aligned with workflow reality.

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
4. [Continuous Integration, Validation, and Release Governance Standard](./Continuous%20Integration%2C%20Validation%20and%20Release%20Governance%20Standard.md)
5. [Platform Integration Architecture Bible](./Platform%20Integration%20Architecture%20Bible.md)

## Known Constraints And Implementation Notes

1. This repository often references or validates other repositories, so stale repository inventory is a real drift risk.
2. Standards-only changes are not complete unless scaffold, validator, or runbook impact is considered.
3. Avoid duplicating platform-wide policy across many files; prefer one central source of truth plus contract tests.
4. Use GitHub for the expensive validation matrix when practical, and use targeted local proof for faster fix-forward work.
5. when harvesting legacy strategy or wiki material, reclassify it against current Lotus ownership
   boundaries before reusing it in `lotus-platform`; old ecosystem narrative can still help, but
   repo docs must speak in current Lotus vocabulary and current architecture.

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
