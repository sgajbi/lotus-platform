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
2. app-wide demo readiness certification,
3. no-code issue-discovery campaigns that should inspect and raise GitHub issues without editing implementation code,
4. platform or backend validation,
5. CI-enforcement and quality-gate design,
6. skill/context inventory and reusable agent-governance maintenance,
7. repo-local frontend or backend delivery governance,
8. PR merge and CI fix-forward workflows,
9. RFC/governance/documentation-only workflows.

This prevents broad generic skills from intercepting more specific governed runtime tasks.

For combined issue-backed discovery and implementation requests, this precedence is sequential,
not exclusive: finish the no-code evidence, duplicate-check, issue create/reuse, and ledger
checkpoint first; then switch to the repo delivery skill before the first source mutation.

## Skill Routing Table

| Task Intent | Primary Skill | Secondary Skills | Governed Source of Truth |
| --- | --- | --- | --- |
| Bring up canonical Workbench runtime, validate populated panels, generate governed demo screenshots, or prove default `lotus-idea` canonical QA readiness/teardown | `lotus-front-office-runtime` | `lotus-frontend-delivery-governance`, `lotus-pr-premerge-gate` | `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`, `lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1` |
| Certify an app is demo-ready across all supported APIs, calculations, product features, seeded data, capability publication, observability/supportability, reviewed evidence, or client-facing demo pack/process | `lotus-demo-readiness-certification` | app delivery governance skill, `lotus-front-office-runtime` for canonical Workbench proof, `lotus-qa-platform-validator`, `lotus-ci-enforcement-governance` when promoting gates, `lotus-readme-wiki-governance` when demo docs/wiki change, `lotus-pr-premerge-gate` | app repo-native demo/API certification command, supported-feature or capability registry, seed automation, generated evidence under app-local `output/`, `docs/demo/client-demo-operating-process.md`, `docs/demo/client-demo-pack-template.md`, and repo docs/scorecards/ledgers |
| Validate service runtime, API, observability, and platform QA posture | `lotus-qa-platform-validator` | `lotus-validation-resolution-lifecycle` | `lotus-platform/automation/Invoke-Platform-QA.ps1` |
| Run or fix RFC-0089/RFC-0090/RFC-0091/RFC-0092 mesh certification, enterprise maturity, and production operating-report failures across telemetry, SLO, access, lifecycle, evidence, drift trend, escalation ownership, GitHub cross-repo checkout, gateway publication, and Workbench discovery consumption | `lotus-backend-delivery-governance` | `lotus-pr-premerge-gate`, `github:gh-fix-ci`, `lotus-rfc-review-loop`, `lotus-qa-platform-validator` | `lotus-platform/automation/mesh_certification_gate.py`, `lotus-platform/automation/mesh_maturity_scope.py`, `lotus-platform/automation/generate_enterprise_mesh_operating_report.py`, `lotus-platform/.github/workflows/mesh-certification-gate.yml`, `lotus-platform/docs/operations/mesh-certification-gate-runbook.md` |
| Certify Lotus API endpoints one by one across every option, output figure, OpenAPI docs, upstream/downstream consumers, GitHub issues, duplicate endpoint posture, and live canonical evidence | `lotus-endpoint-certification-loop` | repo delivery governance skill, `lotus-qa-platform-validator`, `lotus-pr-premerge-gate` | endpoint code/tests/docs plus repo-local engineering context |
| Bring up app, raise defects, implement fixes, revalidate until stable | `lotus-validation-resolution-lifecycle` | `lotus-qa-platform-validator`, `lotus-pr-premerge-gate` | `context/playbooks/VALIDATION-PLAYBOOK.md`, `context/playbooks/PR-LOOP-PLAYBOOK.md` |
| Discover evidence-backed issues and then implement the selected fixes with issue-first traceability | `lotus-app-issue-discovery` for the no-code evidence, duplicate check, issue create/reuse, and ledger checkpoint; then the repo frontend or backend delivery governance skill before mutation | `lotus-codebase-review-ledger` for durable review findings, `lotus-pr-premerge-gate` for PR/merge closure | target repo issue and discovery ledger, repo-local engineering context, `codex/skills/lotus-app-issue-discovery/SKILL.md`, and the applicable repo delivery skill |
| Assess bank readiness, procurement evidence, bank-hosted deployment posture, or a bounded `BR-NNN` control slice | `lotus-app-issue-discovery` for applicability, evidence classification, duplicate search, and issue handoff; then the applicable app delivery skill for selected fixes | `lotus-ci-enforcement-governance` for measured gate promotion, `lotus-skill-context-governance` only when reusable routing changes, `lotus-pr-premerge-gate` for closure | bank-ready implementation playbook, `platform-contracts/bank-readiness/bank-ready-control-catalog.v1.json`, target repo context and evidence; load applicable controls only and do not copy the catalog into skills/context/docs |
| Design or promote high-signal CI enforcement, convert report-only inventories into blocking gates, prevent agent-driven quality degradation, design agentic coding eval loops, decide whether repeated agent failures require skill/context/scaffold updates, enforce test-family or proof-breadth floors, cap uncategorized-test drift, or update quality scorecards and gate placement | `lotus-ci-enforcement-governance` | repo delivery governance skill, `lotus-pr-premerge-gate`, `lotus-codebase-review-ledger` | repo-native quality inventories, Make/NPM targets, GitHub Actions lanes, quality scorecards, review ledgers, platform-owned skill source under `codex/skills`, and `context/playbooks/AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md` |
| Maintain, audit, create, split, merge, or review Lotus skills, agent context, skill manifests, routing maps, deployed-skill sync, AGENTS guidance, procedural memory, or reusable agent guardrails across the Lotus skill inventory | `lotus-skill-context-governance` | `lotus-ci-enforcement-governance` when the lesson should become a CI gate, scaffold, validator, or quality scorecard; `lotus-readme-wiki-governance` when README/wiki source changes | `codex/skills/`, `codex/skills/README.md`, `codex/skills/lotus-skill-manifest.json`, `context/LOTUS-SKILL-ROUTING-MAP.md`, `automation/validate_lotus_skill_alignment.py`, `automation/Bootstrap-LotusDeveloperEnvironment.ps1`, and `codex/skills/lotus-skill-context-governance/scripts/audit_lotus_skills.py` |
| Improve Lotus skills, agent context, operating guidance, or reusable guardrails after a repeated agent-quality, CI, documentation, wiki, closure, architecture, API, or test-quality failure | `lotus-skill-context-governance` | `lotus-ci-enforcement-governance` when the lesson should become a quality gate, scaffold, validator, or scorecard; `lotus-readme-wiki-governance` when README/wiki professionalism is the surfaced failure, repo delivery governance skill for app-specific lessons, `lotus-pr-premerge-gate` before merge | `codex/skills/`, `codex/skills/README.md`, `codex/skills/lotus-skill-manifest.json`, `context/LOTUS-SKILL-ROUTING-MAP.md`, `context/playbooks/AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md`, `context/platform-engineering-ledger.md`, and `automation/Bootstrap-LotusDeveloperEnvironment.ps1` |
| Start or continue an enterprise backend refactor baseline, before/after scorecard, report-only quality measurement, or quality gate promotion in `lotus-platform` | `lotus-ci-enforcement-governance` | `lotus-backend-delivery-governance`, `lotus-readme-wiki-governance`, `lotus-codebase-review-ledger` | `context/playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md`, `automation/generate_enterprise_backend_quality_baseline.py`, `quality/baseline_report.md`, `quality/quality_scorecard.md`, `quality/refactor_health_report.md` |
| Implement or review frontend code in Lotus product surfaces | `lotus-frontend-delivery-governance` | `lotus-pr-premerge-gate` | repo-local engineering context and `RFC-0072` |
| Implement or review backend code in Lotus service repositories | `lotus-backend-delivery-governance` | `lotus-pr-premerge-gate` | repo-local engineering context and `RFC-0072` |
| Implement a business-application RFC slice with domain ownership, API/error-model polish, proof artifacts, data-mesh posture, supported-feature promotion discipline, or blocker-clearing evidence classification | `lotus-backend-delivery-governance` | `lotus-rfc-review-loop` for slice ledger, blocker semantics, and required-vs-actual evidence class recording; `lotus-ci-enforcement-governance` when adding gates, `lotus-pr-premerge-gate` before push/merge | app RFC suite, repo-local engineering context, `LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`, bounded proof artifacts, and `lotus-backend-delivery-governance/references/evidence-classification.md` |
| Define or change a cross-app signed authority, key-discovery, or producer-certification contract | `lotus-backend-delivery-governance` | `lotus-ci-enforcement-governance` for blocking semantic validation, `lotus-skill-context-governance` only when routing lessons change, `lotus-pr-premerge-gate` | `platform-contracts/lifecycle-authority/`, owning app verification code, bank authority boundary, and production certification evidence |
| Standardize, refresh, or professionally polish repository README and wiki documentation across Lotus repos, including weak wiki formatting, reader navigation, business-application feature material, diagrams, implementation-backed demo readiness, current functional/non-functional posture, or restored durable documentation truth | `lotus-readme-wiki-governance` | repo delivery governance skill, `lotus-rfc-review-loop`, `lotus-pr-premerge-gate` for stranded-truth checks | repo-local engineering context, existing public-doc regression tests when present, `docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md`, `context/TASK-ROUTING-GUIDE.md`, and repo-local `wiki/` as the authored source when publishing |
| Prepare, monitor, or merge a PR with Lotus CI discipline, including RFC/docs/wiki/context branch hygiene | `lotus-pr-premerge-gate` | `gh-fix-ci`, `async-task-runner`, `lotus-rfc-review-loop` when durable RFC truth may be stranded | `context/playbooks/PR-LOOP-PLAYBOOK.md` plus stranded-truth reconciliation for governance-bearing branches |
| Launch or monitor detached platform automation profiles, validated repository-native targets, local background runs, RFC-0095 heartbeat attention artifacts, or RFC-0096 governed delegation evidence | `platform-automation-ops` | `async-task-runner`, `lotus-pr-premerge-gate`, `platform-pulse-monitor` | `context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md`, `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json`, `platform-contracts/agent-engineering/delegation-policy-contract.v1.json`, `platform-contracts/heartbeat/heartbeat-status.schema.json`, `automation/Start-Background-Run.ps1`, `automation/repository_background_task.py`, `automation/Check-Background-Runs.ps1`, `automation/Run-Heartbeat.ps1` |
| Refresh only changed or explicitly selected local Lotus Docker services, keep the platform running, avoid full-stack restarts, or run changed-files-based service refresh after implementation | `targeted-service-refresh` | `lotus-qa-platform-validator`, `lotus-front-office-runtime` when canonical Workbench proof is required after refresh | `lotus-platform/automation/Service-Refresh.ps1`, repo-local compose/Dockerfiles, changed-files evidence, and service mapping references |
| Fix failing GitHub Actions checks | `gh-fix-ci` | `lotus-pr-premerge-gate` | GitHub run logs plus repository-native local gates |
| Review, standardize, or create Lotus RFCs and governance docs, including pre-implementation gold-standard hardening, source maps, work-to-be-done ledgers, supported-feature ledgers, branch-graph reconciliation, mandatory slices, and enterprise/data-mesh baselines | `lotus-rfc-review-loop` | `lotus-readme-wiki-governance` when README/wiki product material changes, `lotus-pr-premerge-gate` before merge | RFC file, central platform context, and unmerged-branch stranded-truth evidence |
| Review a Lotus app lens by lens to identify high-value evidence-backed GitHub issues without editing code, including architecture, runtime composition, API design, API documentation/standards, duplicate or unclear APIs, HTTP boundary controls, application/domain/ports/infrastructure layering, downstream integration, database operations, lifecycle, mapping, data model, calculations, security, monitoring/observability, performance, resilience, testing, CI/release evidence, data mesh, repo organization, remote repo hygiene, stale remote feature branches, repo description correctness, agents/context organization, docs/wiki/README, operational supportability, enterprise readiness, tenant isolation, regulatory/records posture, deployment parity, disaster recovery, SLO/capacity/cost, rollout compatibility, operator controls, data privacy lifecycle, licensing/IP, localization, customer-impact failure modes, support escalation, vendor risk, accessibility/usability, client communication suitability, data quality/reconciliation, migration/backfill readiness, SBOM/provenance, API consumer experience, mobile responsiveness, AI model governance, AI data boundaries, AI evaluation quality, AI explainability/audit, AI safety/abuse controls, AI human oversight, AI cost/latency/reliability, AI agent tool governance, shared issue-discovery ledgers, and canonical lens labels | `lotus-app-issue-discovery` | repo delivery governance skill for app type, `lotus-codebase-review-ledger` when durable review ledgers are updated, `lotus-ci-enforcement-governance` when findings should become reusable gates or skills | target repo code/docs/tests, existing GitHub issues, `ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md`, `LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`, `codex/skills/lotus-app-issue-discovery/references/review-lenses.md`, and `codex/skills/lotus-app-issue-discovery/references/campaign-playbook.md` |
| Review codebase patterns, dead code, duplication, or modularity debt | `lotus-codebase-review-ledger` | repo delivery governance skill | review ledger plus repo-local code evidence |
| Upgrade methodology documents to auditable standard | `lotus-methodology-doc-v3` | repo delivery governance skill | methodology docs plus domain source material |
| Draft, review, publish-status update, or maintain Sandeep's private-banking LinkedIn thought-leadership content ledger and post pipeline | `lotus-linkedin-thought-leadership` | `lotus-readme-wiki-governance` only when platform documentation truth changes | `thought-leadership/linkedin/content-ledger.md`, `themes.md`, `voice-and-style-guide.md`, and existing `drafts/`, `reviewed/`, and `posted/` files |

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

### `lotus-app-issue-discovery`

Use when the task is about:

1. reviewing a Lotus repository only to find and raise GitHub issues,
2. continuing a lens-by-lens issue-discovery campaign,
3. finding the next set of high-value defects or improvement opportunities,
4. applying functional or technical knowledge to inspect code before filing issues,
5. reviewing repo organization, agent/context organization, data mesh, monitoring, documentation,
   wiki, or README truth as first-class issue-discovery lenses,
6. reviewing enterprise readiness, accessibility/usability, tenant isolation, compliance, DR,
   rollout, support escalation, data privacy, vendor risk, mobile responsiveness, or AI governance,
   evaluation, safety, oversight, cost, and tool-control posture as issue-discovery lenses,
7. avoiding duplicate GitHub issues while producing evidence-backed acceptance criteria,
8. completing the no-code issue and ledger checkpoint before handing a selected fix to frontend or
   backend delivery.
9. assessing bank readiness or procurement evidence by selecting applicable controls from the
   versioned catalog without embedding those control definitions in the skill or context layer.

### `lotus-demo-readiness-certification`

Use when the task is about:

1. validating every supported demo API, feature, workflow, or calculation for an app,
2. creating or running one repeatable demo-readiness command,
3. seeding deterministic demo data for repeatable validation,
4. reviewing generated evidence and fixing failed or weak proof before a demo,
5. creating or updating client-facing demo packs, demo operating process, talk-track boundaries, or
   follow-up discipline,
6. keeping capability or supported-feature publication aligned with implemented surfaces.

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
6. duplicate, stale, or dead endpoint migration decisions,
7. named-success contract closure for multi-shape caller/source endpoint families.

### `lotus-linkedin-thought-leadership`

Use when the task is about:

1. drafting or reviewing Sandeep's LinkedIn posts,
2. planning the thought-leadership posting cadence,
3. updating the thought-leadership content ledger,
4. moving drafts through reviewed or posted states,
5. preserving employer-safe, non-confidential framing for public content.

### `lotus-ci-enforcement-governance`

Use when the task is about:

1. improving CI enforcement or quality gates,
2. promoting report-only quality inventories to blocking checks,
3. preventing agent-driven code-quality regression,
4. adding or changing repo-native quality commands,
5. updating CI lane placement, scorecards, or enforcement evidence,
6. syncing skill or agent-context guidance for a repeatable enforcement pattern.
7. establishing or updating enterprise backend refactor baseline artifacts under `quality/`.
8. updating scaffold-level anti-drift gates such as `make ci-contract-gate`,
   `make maintainability-gate`, `make documentation-contract-gate`,
   `make quality-scorecard-gate`, `make operation-metric-contract-gate`, or
   `make implementation-truth-gate`.
9. enforcing stable API/runtime, contract/governance, observability/security, or methodology
   test-family breadth instead of relying only on total test count.
10. deciding whether a repeated agent failure should become a skill change, context update,
    scaffold improvement, deterministic gate, report-only inventory, or advisory evaluator case.
11. improving Lotus skills, agent context, operating guidance, or reusable guardrails after a
    repeated quality, documentation, wiki, closure, architecture, API, or test-quality failure.
12. enforcing the universal `Continuous Skill Improvement` section across platform-owned skills so
    future agents promote repeatable lessons into skills, routing, context, validators, scaffolds,
    gates, or an explicit no-change decision.

### `lotus-skill-context-governance`

Use when the task is about:

1. reviewing all Lotus skills or the governed skill inventory,
2. deciding whether a new skill is needed,
3. creating, splitting, merging, or retiring a Lotus skill,
4. maintaining `codex/skills/lotus-skill-manifest.json`,
5. maintaining `context/LOTUS-SKILL-ROUTING-MAP.md`,
6. auditing deployed-skill sync or source-to-local parity,
7. updating AGENTS/context/procedural-memory guidance for future agents,
8. running or improving cross-skill audit validators.

### `lotus-rfc-review-loop`

Use alongside the repo delivery skill when the task is about:

1. implementing an RFC slice from current `main`,
2. preventing many partial slices from accumulating,
3. mapping blocker codes to exact proof artifacts,
4. recording required versus actual evidence classes for blocker-clearing proofs,
5. preserving supported-feature and client-publication boundaries,
6. deciding whether design modularity is enough or a runtime service split is justified.

### `targeted-service-refresh`

Use when the task is about:

1. rebuilding or restarting only impacted local services,
2. keeping the broader Lotus platform running during a focused fix,
3. changed-files-based Docker refresh,
4. avoiding a full stack restart after a bounded implementation change,
5. refreshing services before runtime or canonical evidence that would otherwise use stale containers.

## Keep, Tighten, Add, Remove Decisions

### Add

1. `lotus-front-office-runtime`
2. `lotus-ci-enforcement-governance`
3. `lotus-skill-context-governance`

Reason:

The governed front-office runtime path is important enough to need its own routing surface rather
than being inferred from generic QA or frontend skills.

CI-enforcement design now has enough repeated cross-repository behavior to need a focused routing
surface. It should prevent broad backend, frontend, or PR workflow skills from adding noisy checks
without first proving a measured, deterministic, high-signal gate.

Skill and agent-context governance now has enough repeated platform behavior to need a focused
stewardship surface. It should prevent broad CI or delivery skills from owning whole-inventory
skill audits, manifest changes, deployed-skill sync posture, AGENTS/context routing, and
cross-skill validation decisions.

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
