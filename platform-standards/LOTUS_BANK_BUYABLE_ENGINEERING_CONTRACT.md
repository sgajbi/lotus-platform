# Lotus Bank-Buyable Engineering Contract

This is the standing non-degradation contract for Lotus software that a bank technology buyer may
evaluate. It applies across product UIs, gateways, domain services, shared capabilities, AI-enabled
workflows, and platform governance.

It is an engineering standard, not a regulatory, security, production-readiness, procurement, or
bank-acceptance claim. Do not fake compliance. Unsupported posture remains
`Unknown - requires owner review` or is recorded as planned work.

## Authority And Boundaries

Use this contract for durable outcomes and non-negotiable delivery behavior. Use the
[implementation playbook](./LOTUS_BANK_READY_ENGINEERING_IMPLEMENTATION_PLAYBOOK.md) for the
assessment workflow, maturity and evidence rules, environment responsibilities, and progressive
enforcement. Use the
[versioned control catalog](../platform-contracts/bank-readiness/bank-ready-control-catalog.v1.json)
for stable `BR-NNN` definitions, repository applicability, owner roles, issue-discovery lenses, and
machine validation.

Detailed implementation standards remain authoritative in their own domains:

1. `docs/standards/Enterprise Readiness Standard.md`
2. `docs/standards/Testing Pyramid and Coverage Standard.md`
3. `docs/standards/Dependency Hygiene and Security Standard.md`
4. `docs/standards/Scalability and Availability Standard.md`
5. `docs/standards/Platform Observability Standards.md`
6. `docs/standards/Continuous Integration, Validation, and Release Governance Standard.md`
7. `platform-standards/Development-Workflow-and-CI-Strategy-Standard.md`
8. `platform-standards/Repository-CI-Lane-Mapping-Baseline.md`
9. `platform-standards/Workflow-Security-and-Permissions-Standard.md`
10. `platform-standards/Workflow-Action-Runtime-and-Version-Baseline.md`
11. `platform-standards/Release-Evidence-and-SBOM-Foundation-Standard.md`

Do not copy this contract or the catalog into app repositories. App-local documentation should
record applicability, implementation truth, evidence, exceptions, and residual gaps.

## Required Outcomes

Lotus work must move applicable controls toward these outcomes:

1. Architecture and ownership are explicit; domain logic is testable and separated from transport,
   persistence, and framework adapters.
2. APIs, events, files, calculations, and data changes are deterministic, compatible, bounded,
   domain-correct, and observable.
3. Identity, authorization, secrets, sensitive data, audit, dependencies, artifacts, containers,
   and deployment paths fail closed at the appropriate boundary.
4. Tests prove material positive and negative behavior; contracts and migrations are executable
   evidence rather than prose claims.
5. Logs, metrics, traces, health, alerts, runbooks, recovery, reconciliation, performance, and
   capacity evidence make supported operations diagnosable.
6. Release artifacts map to reviewed source through enforced CI, SBOM/provenance evidence, controlled
   promotion, rollback, and exact-main validation.
7. Documentation is audience-aware and implementation-backed, with unsupported boundaries stated
   plainly and duplication removed.
8. AI, ML, or RAG assistance is advisory unless deterministic evidence, source authority,
   entitlements, model-risk controls, prompt/output governance, auditability, and human review are
   implemented and tested.
9. Product UIs expose truthful ready, loading, empty, partial, stale, degraded, permission-blocked,
   unavailable, and error states backed by governed backend contracts.

## Delivery Non-Negotiables

Every governed slice must:

1. preserve behavior and compatibility unless change is intentional, tested, documented, and
   downstream-safe;
2. state the objective, measurable improvement, compatibility impact, applicable controls, and
   evidence boundary;
3. Complete one implementation-backed slice before opening the next;
4. add meaningful regression and negative-path proof, then search the agreed scope for the same
   defect pattern;
5. reduce dead code, duplication, stale aliases, accidental compatibility paths, and unclear
   ownership encountered in scope;
6. use synthetic or explicitly approved test data and keep secrets, client identifiers, and
   sensitive payloads out of source, logs, evidence, and screenshots;
7. update code, tests, contracts, OpenAPI, migrations, context, docs, wiki, scorecards, and issues
   only where truth changed, recording explicit no-change decisions elsewhere;
8. keep actionable residual work in deduplicated GitHub issues rather than chat or local notes;
9. use small signed commits, fix review and CI findings forward, and preserve meaningful history
   through the repository-approved linear merge path;
10. treat merged-to-main and validated as the definition of done, including issue evidence, wiki
    publication when applicable, and verified branch/worktree reconciliation;
11. Separate design modularity from runtime modularity: prefer clear in-process ownership and
    contract seams until independent scaling, deployment, resilience, data, and operational needs
    justify another service.

## Quality And Enforcement Rules

The Lotus lane model is the shared delivery evidence structure:

1. `Remote Feature Lane` proves fast branch-qualified quality.
2. `Pull Request Merge Gate` proves merge-grade integration and release checks.
3. `Main Releasability Gate` proves the exact merged mainline state.
4. `Platform End-to-End Validation` proves affected cross-app and canonical flows.

Repository-native commands own the checks; workflows orchestrate them. Blocking gates must be
deterministic, actionable, locally reproducible, low-noise, covered by pass/fail tests, and paired
with an explicit exception posture.

Test-family breadth is measured where API/runtime, contract/governance, security, observability, or
domain-methodology evidence matters; aggregate test count alone is not quality proof.

Report-only quality inventories should be promoted to regression-blocking gates only after their
baseline, failure mode, deterministic command, lane placement, exception policy, focused tests, and
scorecard evidence are explicit.

When one scanner supports both report generation and blocking enforcement, keep the
artifact-refresh command separate from the worktree-clean gate command.

Use the agentic coding quality evaluation loop when repeated CI, review, QA, documentation, or
agent-authored failures reveal a reusable evaluator, scaffold, skill, context, or gate improvement.

## Evidence And Readiness

An assessment records control ID, applicability, status, maturity, evidence class, exact evidence,
owner, residual gap, and recheck trigger. The catalog governs the allowed vocabulary.

Evidence must not be promoted across boundaries:

- source design is not local execution;
- local execution is not CI enforcement;
- CI enforcement is not deployment proof;
- deployment proof is not production operation;
- production operation is not independent certification or bank acceptance.

Every quantitative PR claim must be remeasured at the final PR head against the current base after
the last rebase, force-push, or scope correction, using a reproducible command and exact refs.

## Repository Responsibilities

Each app owns its implementation, tests, API and data contracts, migrations, runbooks, scorecards,
repository context, and wiki source. `lotus-platform` owns cross-repository standards, stable control
IDs, validators, scaffolds, routing, and aggregated evidence. It must not duplicate app-local runtime
truth or claim that a source contract proves bank operation.

The target repository profile in the catalog selects applicable controls. A bounded slice may focus
on a coherent subset; it must not claim all 25 controls merely because the catalog exists.

## Maintenance

Update this contract only when the platform-wide non-degradation bar changes. Update the playbook
when execution practice changes, and version the catalog when machine-readable controls or mappings
change. App-specific exceptions belong in the owning repository with an accountable owner and
expiry/recheck condition.

When any layer changes, validate references and behavior, update context and wiki navigation only
where discoverability changed, and preserve the distinction between authored source, generated
evidence, and published wiki state.
