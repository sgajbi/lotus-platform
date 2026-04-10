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
2. RFC-0073 implementation is active and has established the central ecosystem context system.
3. Platform validation, ingress, and local runtime automation are already in active use for canonical stack bring-up and proof.
4. Repository-local context rollout to the rest of the estate is not complete yet.

## Architecture And Module Map

Primary areas:

1. `automation/`
   PowerShell and Python automation for standards validation, platform checks, ingress helpers, governance, and runtime orchestration.
2. `platform-standards/`
   Governing standards, templates, and baseline contracts for repositories and workflows.
3. `platform-stack/`
   Shared runtime assets, ingress stack material, and environment-level infrastructure definitions.
4. `rfcs/`
   Platform and ecosystem RFCs.
5. `context/`
   The central context system introduced by RFC-0073.
6. `tests/unit/`
   Contract tests for platform validators, automation, standards, and documentation governance.

## Runtime And Integration Boundaries

Runtime model:

1. platform automation is executed through Python and PowerShell tooling,
2. local validation and stack control interact with many Lotus repositories,
3. this repository governs but does not replace repository-local quality ownership.

Boundary rules:

1. platform-wide truth belongs here,
2. repository-local truth must remain in the owning repository,
3. cross-repo validation should be encoded once here rather than reimplemented ad hoc elsewhere.

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

## Cross-Links

1. [Lotus Quickstart Context](./context/LOTUS-QUICKSTART-CONTEXT.md)
2. [Lotus Engineering Context](./context/LOTUS-ENGINEERING-CONTEXT.md)
3. [Context Reference Map](./context/CONTEXT-REFERENCE-MAP.md)
4. [Repository Engineering Context Contract](./context/Repository-Engineering-Context-Contract.md)
