# Repository Engineering Context

This is the repository-local context for `lotus-platform`. It describes current ownership,
boundaries, task routes, and completion evidence. Historical delivery belongs in the
[RFC index](./rfcs/README.md), issue tracker, and generated evidence—not here.

Start with [AGENTS.md](./AGENTS.md), then read the
[Lotus quickstart](./context/LOTUS-QUICKSTART-CONTEXT.md) and this file. Use the
[skill routing map](./context/LOTUS-SKILL-ROUTING-MAP.md) to load specialist procedure only when
the task requires it.

## Repository Role

`lotus-platform` is the shared engineering and operational authority for the Lotus ecosystem. It
owns:

1. platform standards and machine-readable cross-repository contracts;
2. reusable CI, validation, scaffold, governance, and release automation;
3. shared ingress, service addressing, and infrastructure support;
4. central engineering context, onboarding, skill source, and documentation conventions;
5. cross-repository evidence generation and validation.

It does not own business-domain APIs or authoritative portfolio, advisory, performance, risk, or
reporting truth. Those remain with their application repositories.

## Business And Domain Responsibility

Platform makes the independently owned Lotus services operable and governable as one ecosystem.
It provides shared engineering controls and integration foundations without becoming a competing
source of business or financial truth.

## Current-State Summary

- The multi-lane CI model, workflow governance, context system, agent onboarding, platform
  validation, and repository scaffolding are active platform capabilities.
- `platform-stack/` is the shared infrastructure and local integration baseline. The governed,
  populated front-office runtime belongs to `lotus-workbench`; Platform supplies shared ingress,
  validation, and evidence automation around it.
- Platform contracts govern API vocabulary, domain data products, trust telemetry, service
  addressing, technology posture, vulnerability exceptions, agent delegation, and bank-readiness
  controls. Repository-native declarations remain owned by their source repositories.
- Quality artifacts under `quality/` measure the repository and are checked by the repo-native
  lanes. They are engineering evidence, not product capability claims.
- Repo-local `wiki/` is the authored wiki source. Publication to the separate GitHub wiki follows
  the governed synchronization workflow.

Current rollout state and unfinished work live in GitHub issues. Do not copy an execution board or
PR chronology into this document.

## Architecture And Module Map

| Area | Responsibility | Boundary |
| --- | --- | --- |
| `automation/` | Reusable validators, generators, runtime helpers, repo checks, and publication tooling | Automation must preserve producer exit status and fail closed when its claim cannot be proved. |
| `platform-standards/` | Human-readable shared standards and templates | Application-specific policy stays with the owning repository. |
| `platform-contracts/` | Versioned machine-readable ecosystem contracts | Consumers validate or reference these contracts; they do not fork their definitions. |
| `context/` | Central progressive context and task-routing system | Durable platform-wide guidance only; repo-local truth belongs in each repository context. |
| `codex/skills/` | Authoritative Lotus skill source | Deploy only merged central source through governed synchronization. |
| `docs/` | Architecture, operations, onboarding, standards, and documentation governance | [Docs index](./docs/README.md) routes to specialist material. |
| `rfcs/` | Design decisions and bounded delivery specifications | Current implementation claims require code and evidence, not RFC prose alone. |
| `platform-stack/` | Shared local infrastructure and ingress assets | Not the canonical populated front-office product runtime. |
| `generated/` | Reproducible derived discovery and certification artifacts | Generated output cannot redefine source ownership. |
| `quality/` | Measured quality baselines, scorecards, and decision evidence | Baselines must come from healthy collection and must not hide regression. |
| `tests/unit/` | Contract and regression proof for Platform policy and automation | Tests should falsify the protected defect where proportionate. |
| `wiki/` | Authored operator-facing wiki source | Never hand-edit publication-only truth in `*.wiki.git`. |

`thought-leadership/` is non-product personal-brand content. It is not customer evidence, platform
marketing truth, or engineering authority.

## Runtime And Integration Boundaries

1. Define platform-wide policy once in Platform and link to it from applications.
2. Keep repository purpose, architecture, ownership, commands, and constraints in that
   repository's `REPOSITORY-ENGINEERING-CONTEXT.md`.
3. Treat generated catalogs and reports as derived evidence; source contracts remain authoritative.
4. Run cross-repository Python validation in isolated interpreters with each repository's real
   package root. Never combine unrelated generic packages such as `app` in one interpreter.
5. Preserve authenticated ownership and server-owned scope. Platform automation must not bypass a
   domain service's authorization or compensate for missing authoritative data.
6. Keep unverified runtime behavior unclaimed. A thin tool adapter may route to shared guidance,
   but runtime-specific discovery or deployment requires independent executable proof.
7. Synchronize central agent contracts or skills to sibling worktrees only from content present on
   `origin/main`; a feature branch is not durable authority.
8. For long-running work, designate one active branch/worktree owner and record exact revision and
   task identity as required by the
   [agent task ledger](./context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md).
9. Canonical front-office QA also includes `lotus-idea` by default and consumes
   repo-native `lotus-idea` declarations; do not make that evidence path opt-in or replace source
   ownership in Platform.

## Task Routes

Use the [skill routing map](./context/LOTUS-SKILL-ROUTING-MAP.md) first. Common routes are:

| Task | Read next |
| --- | --- |
| Context, skills, AGENTS, or agent onboarding | [Context system](./context/README.md), then `lotus-skill-context-governance` |
| README, docs, or wiki organization | [Documentation layering](./docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md), then `lotus-readme-wiki-governance` |
| CI or quality gates | [CI standard](./docs/standards/Continuous%20Integration%2C%20Validation%2C%20and%20Release%20Governance%20Standard.md), then `lotus-ci-enforcement-governance` |
| Platform runtime or integration | [Integration architecture](./docs/architecture/Platform%20Integration%20Architecture%20Bible.md) |
| Canonical Workbench runtime | [Front-office runtime route](./AGENTS.md#front-office-runtime-routing-rule), then `lotus-front-office-runtime` |
| Backend service scaffold | [Scaffold guide](./docs/onboarding/LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md), then `lotus-backend-delivery-governance` |
| Backend refactor instruction rollout | [Canonical instructions](./context/playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md), then verify app copies with `automation/Sync-EnterpriseBackendRefactoringInstructions.ps1 -CheckOnly` |
| Data-mesh delivery or closure | [Lotus Data Mesh Standard](./docs/standards/Lotus%20Data%20Mesh%20Standard.md), then the [enterprise mesh completion handoff](./docs/operations/enterprise-mesh-completion-handoff.md) and its `enterprise-mesh-closure-ledger.json` evidence |
| Client-demo certification | [Lotus Client Demo Certification Standard](./docs/standards/Lotus%20Client%20Demo%20Certification%20Standard.md), then the [Client Demo Pack Template](./docs/templates/client-demo-pack-template.md) |
| Wiki publication | [Wiki rule](./AGENTS.md#wiki-publication-rule) |
| RFC work | [RFC governance standard](./rfcs/RFC-GOVERNANCE-STANDARD.md), then `lotus-rfc-review-loop` when applicable |

## Repo-Native Commands

Run commands from the `lotus-platform` repository root.

```powershell
# Fast targeted context validation
python automation/validate_engineering_context_system.py

# Feature-lane repository proof
powershell -ExecutionPolicy Bypass -File automation/Invoke-PlatformRepoChecks.ps1 -Lane feature

# Validate the measured quality surface
python automation/generate_enterprise_backend_quality_baseline.py --check

# Regenerate only after a healthy test collection
python automation/generate_enterprise_backend_quality_baseline.py --write --check

# Verify this repository's operating contract without changing it
powershell -ExecutionPolicy Bypass -File automation/Sync-AgentOperatingContract.ps1 -CheckOnly

# Verify the deployed copy under the Codex home, which must be asked for by name
powershell -ExecutionPolicy Bypass -File automation/Sync-AgentOperatingContract.ps1 -CheckOnly -IncludeDeployedTarget
```

For all automation and specialist commands, use the
[automation inventory](./quality/automation_inventory.md) and [docs index](./docs/README.md).
Do not create ad hoc substitutes for an existing repo-native entrypoint.

## Validation And CI Expectations

Platform uses these GitHub lanes:

1. Remote Feature Lane;
2. Pull Request Merge Gate;
3. Main Releasability Gate;
4. Platform End-to-End Validation.

A change is complete only when the evidence matches its claim:

- targeted tests prove the corrected behavior and important failure path;
- the applicable repository lane passes at the exact implementation head;
- required review findings are resolved after that head;
- durable docs, context, contracts, and wiki source are included in the owning PR;
- post-merge wiki publication and strict parity are complete when wiki truth changed;
- exact `origin/main` is validated and the working tree, branches, and worktrees are clean;
- completed or superseded GitHub execution state is reconciled.

The quality baseline must record a successful pytest collection (`returncode: 0`). A collected test
count from a non-zero collection is partial evidence and must never overwrite the accepted
baseline. Small environment-driven count variance may be tolerated only by the existing gate; do
not weaken it to make a run green.

For queued or stalled evidence, use:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Detect-Stalled-PR-Checks.ps1
powershell -ExecutionPolicy Bypass -File automation/Detect-Stalled-Workflow-Runs.ps1
```

A queued protected-runner lane is evidence debt, not a passing result.

## Standards And RFCs That Govern This Repository

The current governing entrypoints are the
[RFC governance standard](./rfcs/RFC-GOVERNANCE-STANDARD.md),
[RFC-0071 service-addressing and ingress governance](./rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md),
[RFC-0072 CI and release governance](./rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md),
and [RFC-0073 context governance](./rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md).
Use the RFC index for deeper or historical decisions.

## Known Constraints And Implementation Notes

- Repository inventory drift changes cross-repo validation scope; update `automation/repos.json`
  deliberately and test the resulting discovery behavior.
- Scaffold changes belong in `automation/New-Lotus-Service.ps1` with generated-output contract
  tests, not hand-copied into applications.
- A standard is not implemented merely because prose exists. Consider its contract, validator,
  scaffold, adoption, and release-evidence boundaries.
- Certified endpoint examples need code-owned runtime parity; schema-only or duplicated literals
  do not prove response truth.
- Stateful PostgreSQL claims require real PostgreSQL evidence when correctness depends on its SQL,
  types, constraints, locking, transaction, or persistence semantics.
- Cleanup and targeted refresh automation must resolve declared resources, preserve the caller
  environment, affect only owned runtime state, and verify final health.
- Avoid repeating shared policy in README, wiki, context, and skills. Keep one authority and route
  readers to it.

## Context Maintenance Rule

Update this file only when Platform's current ownership, architecture, boundaries, task routes,
canonical commands, or completion evidence changes. Put temporary status in GitHub and historical
decisions in RFCs or durable evidence.

## Cross-Links

1. [Lotus Quickstart Context](./context/LOTUS-QUICKSTART-CONTEXT.md)
2. [Lotus Engineering Context](./context/LOTUS-ENGINEERING-CONTEXT.md)
3. [Context Reference Map](./context/CONTEXT-REFERENCE-MAP.md)
4. [Repository Engineering Context Contract](./context/Repository-Engineering-Context-Contract.md)
5. [Procedural Memory Index](./context/PROCEDURAL-MEMORY-INDEX.md)
6. [Lotus Developer Onboarding](./docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
7. [Lotus Agent Ramp-Up](./docs/onboarding/LOTUS-AGENT-RAMP-UP.md)
8. [Documentation Index](./docs/README.md)
