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
3. CI-enforcement and quality-gate design,
4. repo-local frontend or backend delivery governance,
5. PR merge and CI fix-forward workflows,
6. RFC/governance/documentation-only workflows.

This prevents broad generic skills from intercepting more specific governed runtime tasks.

## Skill Routing Table

| Task Intent | Primary Skill | Secondary Skills | Governed Source of Truth |
| --- | --- | --- | --- |
| Bring up canonical Workbench runtime, validate populated panels, generate governed demo screenshots | `lotus-front-office-runtime` | `lotus-frontend-delivery-governance`, `lotus-pr-premerge-gate` | `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`, `lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1` |
| Validate service runtime, API, observability, and platform QA posture | `lotus-qa-platform-validator` | `lotus-validation-resolution-lifecycle` | `lotus-platform/automation/Invoke-Platform-QA.ps1` |
| Run or fix RFC-0089/RFC-0090/RFC-0091/RFC-0092 mesh certification, enterprise maturity, and production operating-report failures across telemetry, SLO, access, lifecycle, evidence, drift trend, escalation ownership, GitHub cross-repo checkout, gateway publication, and Workbench discovery consumption | `lotus-backend-delivery-governance` | `lotus-pr-premerge-gate`, `github:gh-fix-ci`, `lotus-rfc-review-loop`, `lotus-qa-platform-validator` | `lotus-platform/automation/mesh_certification_gate.py`, `lotus-platform/automation/mesh_maturity_scope.py`, `lotus-platform/automation/generate_enterprise_mesh_operating_report.py`, `lotus-platform/.github/workflows/mesh-certification-gate.yml`, `lotus-platform/docs/operations/mesh-certification-gate-runbook.md` |
| Certify Lotus API endpoints one by one across every option, output figure, OpenAPI docs, upstream/downstream consumers, GitHub issues, duplicate endpoint posture, and live canonical evidence | `lotus-endpoint-certification-loop` | repo delivery governance skill, `lotus-qa-platform-validator`, `lotus-pr-premerge-gate` | endpoint code/tests/docs plus repo-local engineering context |
| Bring up app, raise defects, implement fixes, revalidate until stable | `lotus-validation-resolution-lifecycle` | `lotus-qa-platform-validator`, `lotus-pr-premerge-gate` | `context/playbooks/VALIDATION-PLAYBOOK.md`, `context/playbooks/PR-LOOP-PLAYBOOK.md` |
| Design or promote high-signal CI enforcement, convert report-only inventories into blocking gates, prevent agent-driven quality degradation, or update quality scorecards and gate placement | `lotus-ci-enforcement-governance` | repo delivery governance skill, `lotus-pr-premerge-gate`, `lotus-codebase-review-ledger` | repo-native quality inventories, Make/NPM targets, GitHub Actions lanes, quality scorecards, and review ledgers |
| Implement or review frontend code in Lotus product surfaces | `lotus-frontend-delivery-governance` | `lotus-pr-premerge-gate` | repo-local engineering context and `RFC-0072` |
| Implement or review backend code in Lotus service repositories | `lotus-backend-delivery-governance` | `lotus-pr-premerge-gate` | repo-local engineering context and `RFC-0072` |
| Standardize or refresh repository README and wiki documentation across Lotus repos, including business-application feature material, diagrams, implementation-backed demo readiness, current functional/non-functional posture, or restored durable documentation truth | `lotus-readme-wiki-governance` | repo delivery governance skill, `lotus-rfc-review-loop`, `lotus-pr-premerge-gate` for stranded-truth checks | repo-local engineering context, existing public-doc regression tests when present, `docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md`, `context/TASK-ROUTING-GUIDE.md`, and repo-local `wiki/` as the authored source when publishing |
| Prepare, monitor, or merge a PR with Lotus CI discipline, including RFC/docs/wiki/context branch hygiene | `lotus-pr-premerge-gate` | `gh-fix-ci`, `async-task-runner`, `lotus-rfc-review-loop` when durable RFC truth may be stranded | `context/playbooks/PR-LOOP-PLAYBOOK.md` plus stranded-truth reconciliation for governance-bearing branches |
| Launch or monitor detached platform automation profiles, local background runs, RFC-0095 heartbeat attention artifacts, or RFC-0096 governed delegation evidence | `platform-automation-ops` | `async-task-runner`, `lotus-pr-premerge-gate`, `platform-pulse-monitor` | `context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md`, `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json`, `platform-contracts/agent-engineering/delegation-policy-contract.v1.json`, `platform-contracts/heartbeat/heartbeat-status.schema.json`, `automation/Start-Background-Run.ps1`, `automation/Check-Background-Runs.ps1`, `automation/Run-Heartbeat.ps1` |
| Fix failing GitHub Actions checks | `gh-fix-ci` | `lotus-pr-premerge-gate` | GitHub run logs plus repository-native local gates |
| Review, standardize, or create Lotus RFCs and governance docs, including pre-implementation gold-standard hardening, source maps, work-to-be-done ledgers, supported-feature ledgers, branch-graph reconciliation, mandatory slices, and enterprise/data-mesh baselines | `lotus-rfc-review-loop` | `lotus-readme-wiki-governance` when README/wiki product material changes, `lotus-pr-premerge-gate` before merge | RFC file, central platform context, and unmerged-branch stranded-truth evidence |
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

### `lotus-ci-enforcement-governance`

Use when the task is about:

1. improving CI enforcement or quality gates,
2. promoting report-only quality inventories to blocking checks,
3. preventing agent-driven code-quality regression,
4. adding or changing repo-native quality commands,
5. updating CI lane placement, scorecards, or enforcement evidence,
6. syncing skill or agent-context guidance for a repeatable enforcement pattern.

## Keep, Tighten, Add, Remove Decisions

### Add

1. `lotus-front-office-runtime`
2. `lotus-ci-enforcement-governance`

Reason:

The governed front-office runtime path is important enough to need its own routing surface rather
than being inferred from generic QA or frontend skills.

CI-enforcement design now has enough repeated cross-repository behavior to need a focused routing
surface. It should prevent broad backend, frontend, or PR workflow skills from adding noisy checks
without first proving a measured, deterministic, high-signal gate.

### Tighten

1. `lotus-qa-platform-validator`
2. `lotus-pr-premerge-gate`
3. `lotus-frontend-delivery-governance`
4. `lotus-backend-delivery-governance`
5. `lotus-validation-resolution-lifecycle`
6. `lotus-rfc-review-loop`

Reason:

These skills remain the right fit. RFC-0089, RFC-0090, RFC-0091, and RFC-0092 add a more explicit
routing row for mesh certification, enterprise maturity checks, operating-report drift,
evidence-policy/lifecycle drift, escalation ownership, and GitHub cross-repo gate failures. No
dedicated mesh-certification or mesh-operations skill is created yet because the current workflow
is still well covered by backend delivery governance plus pre-merge governance; create one only if
repeated operational failure patterns prove that the current skill set is too broad.

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
5. Do not start or close RFC implementation while unmerged remote branches contain unique durable
   RFC/docs/wiki/context/contract truth. Reconcile those branches first and record the disposition.
