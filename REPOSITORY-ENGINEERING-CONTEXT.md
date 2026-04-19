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
   RFC-0084 domain-data-product governance, including first-wave producer and consumer declarations
   for `lotus-core`, `lotus-performance`, and `lotus-risk`, plus the governed identifier and
   temporal semantics registry used by those declarations.
4. `platform-stack/`
   Shared runtime assets, ingress stack material, and environment-level infrastructure definitions.
5. `rfcs/`
   Platform and ecosystem RFCs.
6. `context/`
   The central context system introduced by RFC-0073.
7. `tests/unit/`
   Contract tests for platform validators, automation, standards, and documentation governance.
8. `wiki/`
   canonical authored source for GitHub wiki publication and platform-level onboarding summaries.
9. `docs/documentation/`
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
