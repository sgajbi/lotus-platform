# RFC-0072: Platform-Wide Multi-Lane CI, Validation, and Release Governance

- Status: Proposed
- Date: 2026-04-10
- Owners: lotus-platform governance
- Requires Approval From:
  - lotus-platform maintainers
  - lotus-workbench maintainers
  - lotus-gateway maintainers
  - lotus-core maintainers
  - lotus-performance maintainers
  - lotus-risk maintainers
  - lotus-advise maintainers
  - lotus-manage maintainers
  - lotus-report maintainers
  - lotus-ai maintainers
- Related:
  - `RFC-0005-engineering-baseline-and-delivery-standards.md`
  - `RFC-0048-shared-automation-and-agent-toolkit.md`
  - `RFC-0057-test-pyramid-and-meaningful-coverage-governance.md`
  - `RFC-0060-phase-2-shared-standards-and-automated-conformance.md`
  - `RFC-0061-openapi-contract-quality-and-conformance-automation.md`
  - `RFC-0062-domain-vocabulary-conformance-automation.md`
  - `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`
  - `RFC-0070-gold-standard-product-experience-foundation-and-ownership-model.md`
  - `RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`

## Summary

Lotus needs one platform-wide CI and release model that is:

1. fast enough for daily development,
2. strict enough for merge governance,
3. complete enough for enterprise and banking-grade release trust,
4. explicit about which checks run on feature branches, pull requests, `main`, and scheduled platform validation,
5. grounded in real cross-repository end-to-end evidence rather than repository-local optimism.

This RFC establishes a mandatory multi-lane quality model for all Lotus repositories.

The target model has four lanes:

1. `Remote Feature Lane`
2. `Pull Request Merge Gate`
3. `Main Releasability Gate`
4. `Platform End-to-End Validation Lane`

Each lane has a distinct purpose, cost profile, and required evidence contract.

This RFC also formalizes the banking-grade controls that must be part of Lotus CI:

1. security scanning,
2. contract governance,
3. dependency hygiene,
4. OpenAPI and domain vocabulary quality,
5. Docker/runtime parity,
6. cross-repository canonical environment validation,
7. artifact retention suitable for audit and operator review.

## Problem

Lotus quality gates have improved materially, but the current CI posture is still not governed as one platform system.

Current issues:

1. repositories have strong local gates, but lane intent is not standardized platform-wide,
2. some checks are only discoverable by reading individual workflow files,
3. local CI commands and GitHub workflow behavior are close, but not yet governed as one development standard,
4. end-to-end platform validation exists, but is not yet expressed as the mandatory system-level trust lane for demo and release readiness,
5. security posture is present in parts of the estate, but not yet codified as one required enterprise-quality CI baseline,
6. branch protection and required-check policy are not yet expressed as a single Lotus operating rule,
7. documentation is split across repo READMEs, runbooks, and individual workflows instead of one clear platform policy.

This creates risk:

1. engineers may over-run expensive checks on feature branches or under-run required checks on merge paths,
2. different repositories may drift toward different definitions of "green",
3. main-branch stability may depend on convention instead of platform policy,
4. demos and release candidates may still rely on manual operator judgment rather than canonical validation evidence,
5. security and compliance expectations may be applied unevenly.

## Goals

1. Establish one mandatory CI lane model for all Lotus applications.
2. Standardize which checks are expected on feature branches, PRs, `main`, and scheduled/manual platform validation.
3. Make repository-native commands the source of truth for local and CI execution.
4. Ensure security, contract quality, dependency hygiene, and release evidence are part of the mandatory engineering baseline.
5. Make canonical end-to-end validation part of the governed platform release and demo-readiness story.
6. Reduce workflow drift by documenting a shared naming, ownership, and check taxonomy.
7. Keep the developer experience efficient by separating fast feedback from heavy system validation.
8. Ensure every newly scaffolded Lotus application receives the approved CI lane model and baseline governance by default.

## Non-Goals

1. Replacing all repository workflows in one immediate change.
2. Forcing all repositories onto identical implementation technology.
3. Mandating that every feature branch run full-system Docker and browser validation.
4. Defining production deployment orchestration in this RFC.
5. Replacing domain-specific quality requirements already governed by repo RFCs.

## Why This RFC Is Needed Now

Lotus has already crossed the point where repository-local quality is not enough.

The platform now depends on:

1. `lotus-workbench` consuming `lotus-gateway`,
2. `lotus-gateway` brokering multiple domain authorities,
3. canonical ingress and environment-scoped service identity,
4. seeded demo and front-office validation flows,
5. platform-owned standards and automation as release-critical infrastructure.

At that stage, an informal or partially documented CI philosophy is a platform risk.

Without this RFC:

1. different repositories will continue to define incompatible meanings of "green",
2. platform validation will remain useful but not mandatory,
3. feature-branch speed and PR rigor will continue to be tuned ad hoc,
4. security and enterprise controls will remain unevenly enforced,
5. release and demo readiness will still depend too much on operator memory.

## Decision

Lotus will adopt a four-lane CI and validation model.

This model is mandatory for both:

1. existing repositories through phased convergence,
2. newly scaffolded repositories and applications by default at creation time.

### Lane 1: Remote Feature Lane

Purpose:

1. protect developers from pushing obviously broken code,
2. keep feedback fast,
3. stop drift from accumulating before PR review.

Mandatory characteristics:

1. runs on branch push,
2. must finish quickly relative to the repo,
3. must be deterministic and low-flake,
4. must use repository-native commands.

Required controls by default:

1. Workflow lint
2. Dependency install sanity
3. Lint
4. Typecheck
5. Fast unit tests
6. Fast contract or schema governance checks
7. Changed-scope smoke checks where relevant

Definition of green:

1. the repository installs cleanly,
2. static quality is green,
3. fast tests are green,
4. no blocking governance check in the changed scope is red.

Must not be relied on for:

1. full integration confidence,
2. full browser or cross-app trust,
3. final release readiness.

### Lane 2: Pull Request Merge Gate

Purpose:

1. prove the branch is safe to merge,
2. enforce platform and repository governance,
3. provide auditable merge evidence.

Mandatory characteristics:

1. runs on every PR,
2. is required by branch protection,
3. blocks merge until all required checks pass,
4. must remain mapped to repository-native commands.

Required controls by default:

1. all Feature Lane checks,
2. integration tests,
3. coverage gate,
4. OpenAPI quality and documentation gate where applicable,
5. domain vocabulary or no-alias governance where applicable,
6. migration or contract smoke where applicable,
7. security audit,
8. Docker build validation,
9. local-CI parity or equivalent repo-native parity target,
10. UI browser smoke for UI repositories.

Definition of green:

1. all required PR checks pass,
2. no required security, contract, or coverage gate is red,
3. the PR description includes accurate validation evidence,
4. no known flaky required check is being ignored or bypassed.

### Lane 3: Main Releasability Gate

Purpose:

1. ensure `main` remains releasable,
2. ensure merge success was not branch-specific luck,
3. produce durable release evidence.

Mandatory characteristics:

1. runs on every push to `main`,
2. reruns the PR-grade gate or a stricter equivalent,
3. publishes retained artifacts that support release and audit review.

Required controls by default:

1. rerun PR-grade quality gate,
2. build release-grade container artifacts where applicable,
3. publish coverage reports,
4. publish OpenAPI and vocabulary artifacts where applicable,
5. publish workflow summaries and validation outputs where produced,
6. fail loudly if `main` is no longer releasable.

Definition of green:

1. `main` passes the releasability gate without manual exception,
2. release artifacts and evidence are produced successfully,
3. there is no regression from the branch-protected PR contract.

### Lane 4: Platform End-to-End Validation Lane

Purpose:

1. prove the Lotus ecosystem works as a system,
2. validate canonical ingress, DNS, startup, data seeding, and product surfaces,
3. provide demo-readiness and release-readiness evidence.

Mandatory characteristics:

1. owned centrally from `lotus-platform` and cooperating repos,
2. runnable on demand,
3. runnable on schedule,
4. based on canonical environment-scoped service addressing,
5. based on live stack bring-up and seeded data,
6. produces machine-readable and human-readable evidence.

Required controls by default:

1. canonical host resolution validation,
2. ingress readiness validation,
3. stack bring-up validation,
4. seed-data readiness validation,
5. gateway and upstream API readiness validation,
6. browser-level validation for major screens, sub-screens, and panels,
7. cross-app payload validation where gateway is expected to faithfully represent upstream domain truth,
8. screenshot and summary artifact generation.

Definition of green:

1. canonical DNS or hosts resolution is correct,
2. required services are healthy,
3. required seed data is present,
4. major screens, sub-screens, and panels render populated states,
5. gateway-facing and upstream-facing checks agree where comparison is expected,
6. evidence artifacts are published.

## Required Check Taxonomy

The following names are the canonical check vocabulary for Lotus CI:

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

Repositories may add domain-specific checks, but they must not rename these canonical categories arbitrarily.

## Scaffolding-by-Default Requirement

The Lotus scaffolding baseline must include this CI model by default.

This means any new Lotus application scaffold created after RFC approval must start with:

1. a Feature Lane workflow,
2. a Pull Request Merge Gate workflow,
3. a Main Releasability Gate workflow,
4. repository-native quality commands wired into those workflows,
5. baseline security and dependency checks,
6. Docker build validation where containerized runtime is expected,
7. documentation that explains the local quality command and lane mapping.

### Source of truth

`lotus-platform` must own the scaffold templates, examples, or generation assets that make this possible.

That source of truth must cover:

1. workflow templates,
2. repository command conventions,
3. baseline branch-protection expectations,
4. baseline README and runbook language,
5. standard check naming.

### Non-negotiable scaffolding rule

No new Lotus repository or application should be introduced with:

1. missing CI lanes,
2. ad hoc workflow naming,
3. no security baseline,
4. no documented local quality command,
5. no path to main-branch releasability evidence.

If a new app cannot yet support the full target model, it must still be scaffolded with:

1. the required lane placeholders,
2. explicit TODO markers,
3. tracked deviations and owners,
4. a documented adoption plan.

## Non-Negotiable Operating Rules

1. CI lane purpose must remain explicit. Fast lanes must stay fast; heavy lanes must stay purposeful.
2. Repository-native commands are the source of truth for local and CI execution.
3. A repository is not considered "green" if required checks are only passing locally but not in GitHub.
4. A platform surface is not considered "green" if APIs pass but canonical UI validation fails.
5. No required check may be bypassed through documentation-only approval or operator convention.
6. Flaky checks are governance defects. They must be stabilized, demoted from required status with explicit approval, or replaced.
7. Platform validation evidence must be reproducible, not narrative-only.

## Enterprise and Banking-Grade Mandatory Controls

Every Lotus repository must be mapped to the enterprise-quality controls below.

### Security baseline

Minimum required controls:

1. dependency vulnerability audit,
2. static lint/type safety enforcement,
3. secrets hygiene in committed source and workflow design,
4. container build validation where containers are part of the runtime,
5. branch protection, required-check enforcement, and conversation-resolution enforcement,
6. auditability of merge evidence through retained workflow records.

Planned platform baseline for progressive rollout:

1. SCA for dependency vulnerabilities,
2. secret scanning,
3. Docker image vulnerability scanning,
4. SBOM generation for release-grade services,
5. policy checks for high-risk workflow changes,
6. signed or provenance-backed release artifacts where platform maturity allows.

### Contract and integration baseline

Minimum required controls:

1. OpenAPI contract quality gates where APIs exist,
2. vocabulary governance where public APIs exist,
3. migration contract smoke where persistence exists,
4. cross-app validation for integration boundaries,
5. canonical environment URL discipline for cross-app validation.

### Operational baseline

Minimum required controls:

1. local bring-up and local parity commands must exist,
2. CI must call repository-native commands rather than duplicate ad hoc shell logic,
3. failure artifacts must be retained for diagnosis,
4. runbooks must be current and match the implemented workflow.

## Ownership Model

### `lotus-platform`

Owns:

1. lane policy,
2. canonical check vocabulary,
3. standards documentation,
4. implementation checklist and conformance reporting,
5. canonical end-to-end validation orchestration.

### Individual application repositories

Own:

1. repository-native local quality commands,
2. workflow implementation aligned to the lane policy,
3. repository-specific contract, security, and coverage gates,
4. remediation of failing checks in their own scope.

### `lotus-gateway` and `lotus-workbench`

Carry additional responsibility for:

1. product-surface validation,
2. browser and experience-contract validation,
3. upstream-comparison evidence where UI-facing aggregation is involved.

## Repository Classifications

Repositories will be classified into quality profiles:

1. `UI Product`
2. `Experience API`
3. `Domain API`
4. `Platform Governance / Automation`
5. `Shared Capability Service`

### UI Product profile

Example:

1. `lotus-workbench`

Expected lane additions:

1. browser smoke in PR and `main`,
2. build validation,
3. canonical screen and panel validation in Platform E2E lane.

### Experience API profile

Example:

1. `lotus-gateway`

Expected lane additions:

1. contract governance,
2. upstream live compatibility checks,
3. canonical UI-facing route validation,
4. partial-failure and contract-shaping validation.

### Domain API profile

Examples:

1. `lotus-core`
2. `lotus-performance`
3. `lotus-risk`
4. `lotus-advise`
5. `lotus-manage`
6. `lotus-report`

Expected lane additions:

1. strict contract quality gates,
2. migration smoke,
3. integration and e2e suite partitioning,
4. enterprise coverage gate,
5. Docker build validation.

### Platform Governance / Automation profile

Example:

1. `lotus-platform`

Expected lane additions:

1. validation of ingress, DNS, automation, and standards tooling,
2. cross-app orchestration ownership,
3. artifact production for system validation.

### Shared Capability Service profile

Example:

1. `lotus-ai`

Expected lane additions:

1. capability contract validation,
2. governance checks for AI integration boundaries,
3. gateway-mediated end-to-end validation where the capability is consumed through the product.

## Branch Protection and Merge Governance

The platform standard is:

1. `main` must be protected in all Lotus repositories,
2. direct pushes to `main` are not allowed except explicitly governed emergency paths,
3. PRs are required before merge,
4. required PR checks must be green before merge,
5. required approving review count is `0` in the single-developer operating model,
6. unresolved conversations or explicitly blocking review comments must be resolved,
7. auto-merge is allowed only when all required checks are green,
8. merge queue or equivalent serialized merge discipline is preferred where repository throughput warrants it.

Human approval reviews are optional in the single-developer operating model because there is no independent second reviewer account. The control objective is retained through mandatory PRs, strict required checks, protected `main`, conversation resolution, truthful PR evidence, and GitHub audit history. Multi-developer or regulated-team operation can raise required approving review count above `0` without changing the rest of this model.

Merge strategy:

1. merge commits are allowed,
2. squash merge may be allowed where the owning repo explicitly prefers it,
3. rebase merge is optional,
4. the platform standard does not require squash-by-default.

## Exception and Deviation Governance

Allowed deviations are limited to:

1. temporary repository-specific constraints,
2. staged rollout where a required control is not yet implemented,
3. explicitly approved demotion of a flaky or non-actionable check.

Every deviation must have:

1. an owning repository,
2. a written rationale,
3. an expiry or review date,
4. a replacement or remediation plan,
5. a platform-visible tracking record.

Acceptable vehicles:

1. ADR in the owning repository,
2. implementation checklist status in `lotus-platform`,
3. follow-on RFC where the deviation is cross-cutting.

## Artifact and Evidence Policy

Required retained artifacts where applicable:

1. coverage outputs,
2. Playwright or browser failure artifacts,
3. validation summaries,
4. generated OpenAPI or contract quality reports,
5. cross-app validation JSON or markdown summaries,
6. screenshots for canonical platform validation.

Evidence outputs must be machine-readable where practical.

## Required Evidence by Lane

### Remote Feature Lane

Required evidence:

1. workflow logs,
2. failing test or lint output when red.

### Pull Request Merge Gate

Required evidence:

1. check run history,
2. PR validation summary,
3. retained test and coverage artifacts where applicable.

### Main Releasability Gate

Required evidence:

1. release-grade workflow record,
2. retained coverage or contract artifacts,
3. build artifact or container build record where applicable.

### Platform End-to-End Validation Lane

Required evidence:

1. canonical validation summary JSON,
2. canonical validation summary markdown where practical,
3. screenshots or browser artifacts,
4. endpoint comparison evidence where upstream comparison is required.

## Documentation and Developer Process Standard

Every repository must document:

1. the repository-native local quality command,
2. the repository-native local parity command if distinct,
3. any canonical stack or live-validation command relevant to that repository,
4. the workflow names that correspond to the Feature Lane, PR Merge Gate, and Main Releasability Gate.

`lotus-platform` must maintain:

1. the cross-repository CI and validation standard,
2. the canonical local bring-up and validation runbook for the platform workflow,
3. the implementation checklist and conformance tracking.

## Implementation Phases

### Slice 1: Governance and documentation foundation

Outcome:

1. this RFC is approved,
2. the standard document is published,
3. the lane model is documented and adopted as platform policy.

Acceptance criteria:

1. `lotus-platform` contains the RFC and the associated standard,
2. repositories can map their current workflows to the lane model,
3. branch-protection expectations are documented.

### Slice 1A: Scaffold baseline definition

Outcome:

1. the platform defines what a compliant newly scaffolded Lotus app must contain,
2. future repositories can inherit CI and governance defaults without reinvention.

Acceptance criteria:

1. the RFC and standard explicitly define scaffolding requirements,
2. `lotus-platform` identifies the template or scaffold source of truth,
3. future implementation work includes updating the scaffold assets.

### Slice 2: Repository workflow classification and gap audit

Outcome:

1. every Lotus repository is classified by profile,
2. each repo has a current-state versus target-state CI matrix,
3. missing checks and stale workflow names are enumerated.

Acceptance criteria:

1. one platform-owned rollout document exists,
2. each repo has explicit target lanes and required checks,
3. missing enterprise/security checks are enumerated.

### Slice 3: Standardized workflow convergence

Outcome:

1. repositories converge toward the shared lane model,
2. workflow names and required checks are standardized,
3. local commands and CI commands are aligned.

Acceptance criteria:

1. every in-scope repo has explicit Feature Lane, PR Merge Gate, and Main Releasability Gate workflows,
2. repo-native command parity is enforced,
3. required checks are configured in branch protection.

### Slice 3A: Skill and developer-process alignment

Outcome:

1. Codex-operable skills reflect the lane model,
2. backend, frontend, and PR workflows are aligned to the platform standard,
3. future implementation work inherits the policy by default.

Acceptance criteria:

1. reusable skills exist or are updated for backend delivery, frontend delivery, and PR pre-merge flow,
2. those skills reference the platform standard and RFC,
3. the skills direct agents toward the required lane-specific validation behavior.

### Slice 3B: Scaffold and template convergence

Outcome:

1. scaffold assets produce compliant repositories by default,
2. future app creation no longer starts below platform quality expectations.

Acceptance criteria:

1. shared scaffold templates or generation assets exist,
2. generated repositories include the required lane model and baseline docs,
3. new-app bootstrap no longer requires manual CI invention.

### Slice 4: Platform end-to-end lane hardening

Outcome:

1. `lotus-platform` owns the canonical full-stack validation path,
2. stack bring-up, seeding, and panel-level validation are repeatable and auditable,
3. the platform can demonstrate demo-readiness and release-readiness evidence.

Acceptance criteria:

1. canonical E2E validation runs on demand,
2. scheduled validation exists,
3. validation covers major screens, sub-screens, and panels with real data,
4. artifacts are generated and retained.

### Slice 5: Advanced enterprise controls

Outcome:

1. container scanning, SBOM, secret scanning, and additional security governance are phased in,
2. release evidence quality increases without collapsing developer productivity.

Acceptance criteria:

1. advanced controls are implemented with clear ownership,
2. false-positive and developer-friction handling is documented,
3. governance remains practical and enforceable.

## Risks and Trade-Offs

1. Overloading Feature Lane checks will slow developers down and produce queue fatigue.
2. Under-investing in Platform E2E validation will preserve false confidence.
3. Over-standardizing implementation details too early may create repo-local friction.
4. Adding security checks without ownership and remediation discipline will create noisy, ignored failures.

Mitigations:

1. keep lane purposes distinct,
2. use repository-native commands,
3. phase advanced controls progressively,
4. keep required checks explicit and minimal for the purpose of each lane.

## Alternatives Considered

### Alternative 1: One uniform heavyweight pipeline for every event

Rejected.

Reason:

1. too slow for feature development,
2. causes developers to bypass discipline,
3. mixes fast feedback with expensive system validation.

### Alternative 2: Let each repo define its own CI philosophy

Rejected.

Reason:

1. incompatible definitions of "green" would persist,
2. cross-repository release trust would remain weak.

### Alternative 3: Rely only on repo-local PR checks and skip platform validation

Rejected.

Reason:

1. Lotus is a platform system,
2. repo-local success does not prove canonical end-to-end behavior.

## Acceptance Criteria

This RFC is complete when:

1. the Lotus ecosystem adopts the four-lane CI and validation model,
2. a platform-owned standard document exists and is current,
3. every in-scope repository is mapped to a lane profile,
4. branch protection and required checks reflect the documented merge-governance rules,
5. platform-level canonical end-to-end validation is formalized as a governed lane,
6. enterprise and security controls are incorporated into the baseline and phased roadmap.
7. deviation handling and evidence requirements are explicit and enforceable.

## Approval Requested

Approve this RFC if the team agrees that:

1. Lotus should operate one platform-wide multi-lane CI model rather than repo-by-repo convention,
2. Feature Lane, PR Merge Gate, Main Releasability Gate, and Platform End-to-End Validation must be explicit and mandatory,
3. security, contract quality, dependency hygiene, and release evidence are part of the engineering baseline,
4. `lotus-platform` should own the cross-repository CI and validation standard and rollout governance,
5. implementation should proceed only after approval through a staged, repo-by-repo convergence program.
