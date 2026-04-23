# RFC-0107: Enterprise Reporting Production Certification

- Status: Proposed
- Date: 2026-04-23
- Owners:
  - lotus-platform governance
  - `lotus-report` owners
  - `lotus-render` owners
  - `lotus-archive` owners
  - `lotus-gateway` owners
  - `lotus-workbench` owners
  - upstream domain service owners
- Target repositories:
  - `lotus-platform`
  - `lotus-report`
  - `lotus-render`
  - `lotus-archive`
  - `lotus-gateway`
  - `lotus-workbench`
  - `lotus-core`
  - `lotus-performance`
  - `lotus-risk`
  - `lotus-advise`
  - `lotus-manage`
- Depends on:
  - `RFC-0099-enterprise-reporting-and-document-archive-target-architecture.md`
  - `RFC-0100` through `RFC-0106`
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
  - `RFC-0091-enterprise-data-mesh-maturity-and-production-readiness.md`

## Summary

This RFC defines the final production certification gate for the enterprise reporting architecture.
It proves that gateway initiation, report ledger, lineage, rendering, archive, batch, observability,
security, documentation, wiki, context, and supported-features posture work end to end.

## Problem

Even if each earlier RFC is individually implemented, the platform is not production-ready until the
complete reporting flow is certified across repositories, services, failure modes, and operational
support paths.

## Target Scope

In scope:

1. end-to-end certification scenarios,
2. canonical portfolio review ad hoc generation,
3. batch production certification,
4. rerender/regenerate/reissue/supersession certification,
5. archive retrieval and access audit certification,
6. observability and trace completeness,
7. security and entitlement certification,
8. non-functional performance and recovery tests,
9. docs/wiki/context/supported-features closure,
10. branch hygiene and wiki publication.

Out of scope:

1. new business report types not introduced by earlier RFCs,
2. unrelated upstream domain feature work,
3. broad platform release certification outside enterprise reporting.

## Certification Scenarios

Required first-wave scenarios:

1. ad hoc portfolio review JSON generation through gateway,
2. ad hoc portfolio review PDF generation through gateway/report/render/archive,
3. document metadata and download through gateway,
4. explicit portfolio-list batch,
5. failed upstream data collection,
6. render failure,
7. archive failure,
8. retry failed batch item,
9. rerender from stored snapshot,
10. regenerate from latest upstream data,
11. corrected/reissued/superseded document,
12. unauthorized report generation denied,
13. unauthorized document retrieval denied,
14. trace from Workbench/gateway to archive.

## Implementation Slices

### Slice 0: Cleanup And Structure

1. Review all reporting RFC docs, README content, wiki source, and context.
2. Remove duplicate architecture or operator guidance.
3. Consolidate long-lived production operation guidance into wiki source.
4. Ensure supported-features lists are implementation-backed.

### Slice 1: Certification Harness

1. Add platform-owned certification runner or workflow.
2. Define service bring-up requirements.
3. Add evidence artifact schema.
4. Add canonical scenario fixtures.

### Slice 2: End-To-End Functional Certification

1. Certify ad hoc JSON and PDF flows.
2. Certify archive retrieval.
3. Certify batch generation.
4. Certify rerender/regenerate/reissue/supersession.

### Slice 3: Failure And Recovery Certification

1. Certify upstream failure behavior.
2. Certify render failure behavior.
3. Certify archive failure behavior.
4. Certify retry, resume, and stuck-job handling.

### Slice 4: Security And Observability Certification

1. Certify authorization negative paths.
2. Certify access audit.
3. Certify trace and metric completeness.
4. Certify sensitive logging posture.

### Slice 5: Non-Functional Certification

1. Run ad hoc latency tests.
2. Run batch throughput tests.
3. Run concurrency/back-pressure tests.
4. Run archive storage/retrieval recovery tests.

### Second-Last Slice: Hardening, Review, And Certification

1. Review all implementation evidence.
2. Verify API certification, platform governance, data mesh standards, docs, and supportability.
3. Fix loose ends before final closure.

### Final Slice: Closure

1. Update docs, wiki, supported-features, context, skills/guidance, and PR evidence.
2. Publish wiki after merge if changed.
3. Leave all branches clean or explicitly close follow-up branches.

## Acceptance Criteria

1. Enterprise reporting works end to end for first-wave ad hoc and batch scenarios.
2. Every generated document has lineage, render evidence, archive metadata, and access audit.
3. Rerender, regenerate, correction, reissue, and supersession are certified.
4. Failure modes are diagnosable and recoverable.
5. Observability and security checks pass.
6. Supported-features material reflects only delivered behavior.
7. Wiki and context are published and usable.

## Risks

| Risk | Mitigation |
| --- | --- |
| Individual RFCs pass but end-to-end flow fails | Platform-owned certification scenarios |
| Non-functional gaps appear late | Dedicated non-functional certification slice |
| Docs overstate readiness | Supported-features and wiki review in closure |
| Cross-repo ownership is unclear | Certification evidence names repo, branch, PR, and owner |

## Validation

Required validation:

1. Repo-native gates for every touched repository.
2. Platform certification runner.
3. Cross-repo GitHub check evidence.
4. Manual or automated review of generated PDF and archive metadata evidence.
5. Security and observability certification evidence.

## Supported Features

This RFC is the only RFC in the sequence allowed to certify the complete enterprise reporting
platform as production-ready. It must not mark the platform production-ready until all required
scenarios, documentation, wiki, context, and supported-features evidence are complete.

