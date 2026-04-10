# Continuous Integration, Validation, and Release Governance Standard

- Version: 1.0.0
- Status: Draft Pending RFC-0072 Approval
- Scope: all Lotus repositories
- Change control: changes to mandatory controls require RFC in `lotus-platform/rfcs`

## Purpose

Define the mandatory Lotus engineering process for:

1. local quality execution,
2. remote feature-branch validation,
3. pull-request merge governance,
4. `main` releasability validation,
5. platform end-to-end canonical validation,
6. enterprise-quality security and evidence controls.

This standard is the operational policy that implements `RFC-0072`.

## 1. Mandatory Lane Model

Every Lotus repository must map its workflows to four lanes.

### 1.1 Remote Feature Lane

Purpose:

1. fast developer feedback,
2. low-latency breakage detection,
3. fast branch hygiene.

Must include, as applicable:

1. Workflow lint
2. Dependency integrity
3. Lint
4. Typecheck
5. Fast unit tests
6. Fast contract or schema checks

Must not be the only release-trust signal.

### 1.2 Pull Request Merge Gate

Purpose:

1. block unsafe merges,
2. enforce repository and platform policy,
3. provide auditable PR evidence.

Must include, as applicable:

1. all Feature Lane checks,
2. integration tests,
3. coverage gate,
4. security audit,
5. contract governance gates,
6. Docker build validation,
7. local parity or equivalent repo-native parity run,
8. browser smoke for UI repositories.

### 1.3 Main Releasability Gate

Purpose:

1. keep `main` deployable,
2. produce release-grade evidence.

Must include, as applicable:

1. PR-grade gate rerun or stricter equivalent,
2. release artifact generation,
3. retained evidence outputs,
4. failure treated as a mainline incident.

### 1.4 Platform End-to-End Validation Lane

Purpose:

1. validate the Lotus ecosystem as one platform,
2. validate canonical ingress, DNS, startup, seeding, and product surfaces,
3. provide demo-readiness and release-readiness evidence.

Must include, as applicable:

1. canonical host resolution checks,
2. service readiness checks,
3. canonical stack bring-up,
4. seed-data validation,
5. gateway and upstream API validation,
6. browser validation for screens, sub-screens, and panels,
7. evidence artifact generation.

## 2. Repository-Native Command Policy

Each repository must expose repository-native commands for:

1. install,
2. lint,
3. typecheck,
4. unit tests,
5. integration tests where applicable,
6. e2e tests where applicable,
7. coverage gate,
8. local parity or equivalent CI parity.

CI workflows must call repository-native commands rather than re-implement repository logic in workflow YAML wherever practical.

## 3. Canonical Check Vocabulary

The following check names are the platform standard vocabulary:

1. `Workflow Lint`
2. `Dependency Integrity`
3. `Security Audit`
4. `Lint`
5. `Typecheck`
6. `OpenAPI Gate`
7. `API Vocabulary Gate`
8. `No-Alias Contract Guard`
9. `Migration Contract Smoke`
10. `Unit Tests`
11. `Integration Tests`
12. `E2E Tests`
13. `Coverage Gate`
14. `Validate Docker Build`
15. `CI Local Parity`
16. `Canonical End-to-End Validation`

Repositories may add domain-specific checks, but they should not invent avoidable synonyms for the standard check families.

## 4. Branch Protection and Merge Governance

Mandatory `main` protections:

1. pull requests required,
2. required checks required,
3. direct push blocked except explicitly governed emergency paths,
4. stale branch protection or update-before-merge enabled where supported,
5. merge only after all required checks are green.

Auto-merge:

1. allowed when all required checks are green,
2. must not bypass required reviews,
3. must not bypass required checks.

Merge strategy:

1. merge commits are allowed,
2. squash merges are repository-specific preference,
3. this standard does not require squash-by-default.

## 5. Enterprise Security Baseline

Mandatory current baseline:

1. dependency vulnerability audit,
2. lint and type safety enforcement,
3. OpenAPI and contract governance where applicable,
4. security audit as part of PR merge gate,
5. Docker build validation where containers are part of runtime,
6. documented remediation ownership for failing security findings.

Progressive rollout baseline:

1. secret scanning,
2. container vulnerability scanning,
3. SBOM generation,
4. artifact provenance and signing where platform maturity allows,
5. policy checks for privileged workflow changes.

## 6. Artifact Retention and Audit Evidence

CI and validation lanes must retain useful artifacts where applicable:

1. coverage reports,
2. browser failure artifacts,
3. validation summaries,
4. OpenAPI and vocabulary outputs,
5. system validation screenshots,
6. logs required for root-cause analysis.

Artifacts should be machine-readable when practical.

## 7. Platform End-to-End Validation Standard

The canonical platform validation workflow must be able to:

1. bring the platform up through canonical ingress,
2. validate canonical DNS or hosts mappings,
3. validate seed data exists,
4. validate all major product screens,
5. validate sub-screens and panel-level data presence,
6. validate gateway routes against upstream readiness,
7. publish a consolidated summary.

Current portfolio baseline for front-office validation:

1. `PB_SG_GLOBAL_BAL_001`

## 8. Repository Profile Expectations

### 8.1 UI Product Repositories

Examples:

1. `lotus-workbench`

Must include:

1. build validation,
2. browser smoke in PR lane,
3. canonical UI validation in Platform E2E lane.

### 8.2 Experience API Repositories

Examples:

1. `lotus-gateway`

Must include:

1. contract governance,
2. upstream compatibility validation,
3. integration and coverage gates,
4. Docker validation.

### 8.3 Domain API Repositories

Examples:

1. `lotus-core`
2. `lotus-performance`
3. `lotus-risk`
4. `lotus-advise`
5. `lotus-manage`
6. `lotus-report`

Must include:

1. contract and vocabulary quality where applicable,
2. migration smoke where applicable,
3. unit, integration, and e2e partitioning where applicable,
4. coverage gate,
5. Docker validation.

### 8.4 Platform Governance Repository

Examples:

1. `lotus-platform`

Must include:

1. standards conformance tooling,
2. ingress and DNS validation,
3. platform validation orchestration,
4. workflow and automation hardening.

## 9. Documentation Requirements

Each repository must document:

1. local quality commands,
2. local parity command if distinct,
3. workflow lane mapping,
4. any canonical live-validation command it owns.

`lotus-platform` must document:

1. the cross-repository CI standard,
2. the canonical local runtime and validation runbook,
3. the rollout checklist and conformance status.

## 10. Definition of Done

This standard is considered adopted when:

1. each repository maps its CI workflows to the lane model,
2. required checks are protected on `main`,
3. repository-native commands are aligned with CI,
4. platform end-to-end validation is documented and repeatable,
5. enterprise baseline controls are present and governed.
