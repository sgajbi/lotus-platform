# Lotus Skill Routing Map

This document defines the target routing map for Lotus agent skills.

It is task-first and should be used to decide which Lotus skill is the smallest correct fit for a
request before loading deeper context or starting implementation.

RFC governance:

1. `RFC-0075` governs the canonical front-office runtime path.
2. `RFC-0076` governs the canonical front-office dataset.
3. `RFC-0077` governs Workbench panel ownership and supportability.
4. `RFC-0078` governs the modular front-office validator.
5. `RFC-0079` governs evidence and lineage contracts.
6. `RFC-0080` governs skill routing and guidance hardening.

## Routing Precedence

When multiple Lotus skills appear relevant, choose in this order:

1. front-office runtime and populated product-surface proof,
2. platform or backend validation,
3. repo-local frontend or backend delivery governance,
4. PR merge and CI fix-forward workflows,
5. RFC/governance/documentation-only workflows.

This prevents broad generic skills from intercepting more specific governed runtime tasks.

## Skill Routing Table

| Task Intent | Primary Skill | Secondary Skills | Governed Source of Truth |
| --- | --- | --- | --- |
| Bring up canonical Workbench runtime, validate populated panels, generate governed demo screenshots | `lotus-front-office-runtime` | `lotus-frontend-delivery-governance`, `lotus-pr-premerge-gate` | `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`, `lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1` |
| Validate service runtime, API, observability, and platform QA posture | `lotus-qa-platform-validator` | `lotus-validation-resolution-lifecycle` | `lotus-platform/automation/Invoke-Platform-QA.ps1` |
| Certify Lotus API endpoints one by one across every option, output figure, OpenAPI docs, upstream/downstream consumers, GitHub issues, duplicate endpoint posture, and live canonical evidence | `lotus-endpoint-certification-loop` | repo delivery governance skill, `lotus-qa-platform-validator`, `lotus-pr-premerge-gate` | endpoint code/tests/docs plus repo-local engineering context |
| Bring up app, raise defects, implement fixes, revalidate until stable | `lotus-validation-resolution-lifecycle` | `lotus-qa-platform-validator`, `lotus-pr-premerge-gate` | `context/playbooks/VALIDATION-PLAYBOOK.md`, `context/playbooks/PR-LOOP-PLAYBOOK.md` |
| Implement or review frontend code in Lotus product surfaces | `lotus-frontend-delivery-governance` | `lotus-pr-premerge-gate` | repo-local engineering context and `RFC-0072` |
| Implement or review backend code in Lotus service repositories | `lotus-backend-delivery-governance` | `lotus-pr-premerge-gate` | repo-local engineering context and `RFC-0072` |
| Standardize or refresh repository README and wiki documentation across Lotus repos | `lotus-readme-wiki-governance` | repo delivery governance skill, `lotus-rfc-review-loop` | repo-local engineering context, existing public-doc regression tests when present, `docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md`, `context/TASK-ROUTING-GUIDE.md`, and repo-local `wiki/` as the authored source when publishing |
| Prepare, monitor, or merge a PR with Lotus CI discipline | `lotus-pr-premerge-gate` | `gh-fix-ci`, `async-task-runner` | `context/playbooks/PR-LOOP-PLAYBOOK.md` |
| Fix failing GitHub Actions checks | `gh-fix-ci` | `lotus-pr-premerge-gate` | GitHub run logs plus repository-native local gates |
| Review or standardize Lotus RFCs and governance docs | `lotus-rfc-review-loop` | none by default | RFC file plus central platform context |
| Review codebase patterns, dead code, duplication, or modularity debt | `lotus-codebase-review-ledger` | repo delivery governance skill | review ledger plus repo-local code evidence |
| Upgrade methodology documents to auditable standard | `lotus-methodology-doc-v3` | repo delivery governance skill | methodology docs plus domain source material |

## Task-Intent Triggers

### `lotus-front-office-runtime`

Use when the task mentions:

1. `PB_SG_GLOBAL_BAL_001`
2. `lotus-risk-module-shots`
3. demo screenshots
4. populated Workbench panels
5. canonical UI proof
6. "all panels loaded"
7. "bring up all UI-related stack"
8. screenshot evidence for the canonical runtime

### `lotus-qa-platform-validator`

Use when the task is about:

1. backend or infrastructure QA,
2. service health, logs, metrics, or observability checks,
3. standards conformance and issue filing,
4. platform QA that does not require populated canonical front-office screenshots.

### `lotus-validation-resolution-lifecycle`

Use when the user wants:

1. validate -> issue -> fix -> PR -> merge -> revalidate loop,
2. defect-driven stabilization,
3. repeated QA and closure until no blockers remain.

### `lotus-endpoint-certification-loop`

Use when the task is about:

1. endpoint-by-endpoint certification,
2. testing all request options and every returned figure,
3. OpenAPI/Swagger completeness,
4. upstream and downstream integration correctness,
5. GitHub issue review for endpoint-specific defects,
6. duplicate, stale, or dead endpoint migration decisions.

## Keep, Tighten, Add, Remove Decisions

### Add

1. `lotus-front-office-runtime`

Reason:

The governed front-office runtime path is important enough to need its own routing surface rather
than being inferred from generic QA or frontend skills.

### Tighten

1. `lotus-qa-platform-validator`
2. `lotus-pr-premerge-gate`
3. `lotus-frontend-delivery-governance`
4. `lotus-backend-delivery-governance`
5. `lotus-validation-resolution-lifecycle`

Reason:

These skills are still useful, but their routing boundaries and async GitHub posture need to be
more explicit.

### Keep

1. `lotus-rfc-review-loop`
2. `lotus-codebase-review-ledger`
3. `lotus-methodology-doc-v3`
4. `lotus-rfc0067-rollout`
5. `lotus-transaction-rfc-loop`

Reason:

These skills remain specialized and do not currently create routing ambiguity for the front-office
runtime path.

### Remove or merge candidates

None are approved for removal in Slice 1.

Reason:

The inventory review identifies routing ambiguity, but removal decisions should only be executed in
later slices once replacement guidance is implemented and validated.

## Routing Rules

1. Do not use screenshot capture alone as proof for canonical product-surface readiness.
2. Do not route canonical Workbench demo work through generic platform QA when populated product
   surfaces are the goal.
3. Do not block on long GitHub checks if truthful local proof is already complete and GitHub can run
   the heavy lanes asynchronously.
4. Do not keep dead or duplicate skill guidance once a stronger governed path exists.
