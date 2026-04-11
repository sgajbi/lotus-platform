# RFC-0074: Repeatable Developer and Agent Bootstrap System

- Status: Implemented
- Date: 2026-04-11
- Owners: lotus-platform governance
- Requires Approval From:
  - lotus-platform maintainers
  - lotus-core maintainers
  - lotus-performance maintainers
  - lotus-risk maintainers
  - lotus-advise maintainers
  - lotus-manage maintainers
  - lotus-report maintainers
  - lotus-ai maintainers
  - lotus-gateway maintainers
  - lotus-workbench maintainers
- Related:
  - `RFC-0005-engineering-baseline-and-delivery-standards.md`
  - `RFC-0048-shared-automation-and-agent-toolkit.md`
  - `RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
  - `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`

## Summary

RFC-0073 created the governed Lotus engineering context system for agent ramp-up. It solved the durable context problem inside the existing environment, but it did not fully solve new-machine and new-developer repeatability.

This RFC proposes a platform-owned bootstrap system that allows a new developer or a coding agent on a new machine to:

1. clone or pull the Lotus repositories,
2. install or validate required local prerequisites,
3. synchronize Lotus Codex skills and agent guidance,
4. validate that context documents and `AGENTS.md` are discoverable,
5. verify GitHub, Docker, Python, Node, PowerShell, ingress, DSN, and repository readiness,
6. start a new chat with a known high-signal first prompt,
7. load the smallest correct context set without flooding the context window,
8. become productive quickly with a repeatable, auditable, banking-grade setup process.

The target state is not a large onboarding document alone. The target state is a documented and automated bootstrap capability owned by `lotus-platform`.

The system must be safe by default:

1. inspect before mutation,
2. redacted output by default,
3. idempotent sync behavior,
4. no hidden long-running validation,
5. no undocumented local-machine assumptions,
6. clear separation between human onboarding, agent ramp-up, and executable environment validation.

## Problem

Lotus now has strong context guidance, repo-local engineering context, skills, procedural memory, CI governance, and platform validation standards. However, a new machine or new developer still has avoidable ambiguity:

1. where to start after `git pull`,
2. which repositories must exist locally,
3. how Codex skills are distributed and kept current,
4. how global `AGENTS.md` should be synchronized,
5. how much context to load in a new chat,
6. what the first prompt should be,
7. how to validate local prerequisites without manually discovering failures,
8. how to prepare canonical ingress and environment settings,
9. how to avoid stale local state becoming mistaken for platform truth.
10. how to know whether a failure is a missing prerequisite, a local configuration gap, a repo drift issue, or a real product defect.

Without a governed bootstrap system, RFC-0073 depends too much on a machine that has already been curated by prior work.

That is not sufficient for a banking-grade platform.

## Quality Bar

This RFC is successful only if the resulting system materially improves the speed and quality of future work without turning onboarding into a heavy platform run.

Required quality attributes:

1. repeatable across new Windows developer machines,
2. path-aware without hard-coding one user's workspace as the only supported layout,
3. safe to run repeatedly,
4. explicit about what it checks and what it changes,
5. fast by default,
6. redacted by default,
7. capable of producing a useful readiness report for humans and agents,
8. aligned with RFC-0071 ingress, RFC-0072 validation lanes, and RFC-0073 context architecture,
9. covered by meaningful tests for report shape, redaction, idempotency, and context-link integrity.

## Goals

1. Make new-machine and new-developer setup repeatable from `lotus-platform`.
2. Provide one authoritative onboarding guide for human developers and coding agents.
3. Provide bootstrap automation that validates prerequisites and reports actionable gaps.
4. Version and distribute Lotus Codex skills in a repeatable way.
5. Keep global `AGENTS.md` synchronized from the governed platform source.
6. Define the standard first prompt for a new chat window.
7. Define context-loading discipline so agents load neither too much nor too little.
8. Integrate existing RFC-0073 context artifacts instead of duplicating them.
9. Make the bootstrap process useful for both normal development and demo readiness.
10. Keep developer experience efficient by distinguishing required checks from optional heavy validation.
11. Produce a machine-readable readiness report that future agents can consume without re-running discovery.
12. Make common failure remediation explicit so bootstrap output tells the developer what to do next.

## Non-Goals

1. Replacing RFC-0073 context documents.
2. Replacing RFC-0072 CI and validation governance.
3. Running full platform E2E validation on every onboarding check.
4. Encoding secrets in documentation or automation.
5. Replacing repository-local setup details where local truth belongs in the repository.
6. Creating a new package manager or monorepo orchestration layer.
7. Guaranteeing that all application test suites are green on every developer machine during bootstrap.
8. Installing licensed or privileged enterprise tooling without an explicit local operator step.

## Decision

Lotus will create a platform-owned onboarding and bootstrap system with four layers:

1. a human-readable onboarding guide,
2. repeatable local bootstrap automation,
3. governed Codex skill and agent-contract synchronization,
4. a context-loading and first-prompt standard.

The system will live centrally in `lotus-platform` because this is cross-repository platform infrastructure.

The bootstrap system must be designed as an onboarding control plane, not as an implicit replacement for CI or platform E2E validation.

## Source-Of-Truth Model

The source-of-truth model is:

| Artifact | Source Of Truth | Local Copy Or Consumer | Drift Handling |
| --- | --- | --- | --- |
| Platform context | `lotus-platform/context/` | new chat context loading | validated by context-system validator |
| Repository context | `<repo>/REPOSITORY-ENGINEERING-CONTEXT.md` | target repo task execution | validated by repository context contract where available |
| Agent operating contract | `lotus-platform/context/AGENTS-OPERATING-CONTRACT.md` | `C:\Users\<user>\.codex\AGENTS.md` | synchronized by platform automation |
| Lotus Codex skills | `lotus-platform/codex/skills/` | `C:\Users\<user>\.codex\skills\` | inspected and synchronized by bootstrap automation |
| Onboarding docs | `lotus-platform/docs/onboarding/` | human and agent startup workflow | protected by documentation contract tests |
| Runtime prerequisites | local machine | bootstrap readiness report | inspected, never silently installed unless explicitly supported |
| CI and release truth | GitHub Actions and RFC-0072 lanes | PR and main validation | monitored asynchronously, not replaced by bootstrap |

## Target State

### Central onboarding guide

Create:

1. `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`
2. `docs/onboarding/LOTUS-AGENT-RAMP-UP.md`

The developer onboarding guide owns machine and repository setup.

The agent ramp-up guide owns new-chat context loading, first prompt, skill selection, and context-window discipline.

The two guides must cross-link but remain distinct:

1. developer onboarding answers "how do I prepare this machine and workspace?",
2. agent ramp-up answers "how does a new chat load enough context and operate correctly?",
3. neither guide should duplicate the full RFC-0073 context body.

### Bootstrap automation

Create:

1. `automation/Bootstrap-LotusDeveloperEnvironment.ps1`
2. `automation/Validate-LotusDeveloperEnvironment.ps1`

The bootstrap script should be safe to run repeatedly. It should not overwrite local work or secrets.

The validator should produce a clear readiness report.

Required validation areas:

1. Git and GitHub CLI authentication,
2. PowerShell execution capability,
3. Docker availability and daemon status,
4. Python and Node runtime availability,
5. repository presence and branch cleanliness summary,
6. Codex skill directory presence and synchronization status,
7. global `AGENTS.md` synchronization status,
8. platform context document presence and cross-link validation,
9. canonical ingress host mapping status,
10. local environment and DSN configuration status without printing secrets,
11. optional stack bring-up readiness checks.

The scripts must expose a consistent summary with four statuses:

1. `ready`,
2. `warning`,
3. `blocked`,
4. `skipped`.

The output must distinguish:

1. missing prerequisite,
2. stale synchronized artifact,
3. local configuration gap,
4. repository state issue,
5. optional heavy validation not requested,
6. product or CI failure requiring fix-forward work.

### Readiness report contract

The validator must emit both human-readable and machine-readable output.

Required output files:

1. `output/developer-environment-readiness.json`
2. `output/developer-environment-readiness.md`

Required JSON shape:

```json
{
  "status": "ready|warning|blocked",
  "generated_at": "ISO-8601 timestamp",
  "workspace_root": "redacted-or-normalized path",
  "checks": [
    {
      "id": "stable-check-id",
      "category": "toolchain|repository|context|agent|ingress|environment|runtime",
      "status": "ready|warning|blocked|skipped",
      "summary": "human-readable summary",
      "remediation": "actionable next step or null"
    }
  ]
}
```

The JSON report must not include secrets, tokens, DSN passwords, or private credential material.

### Skill distribution

Lotus-specific Codex skills must be versioned as platform artifacts.

Target location:

1. `codex/skills/`

Bootstrap automation should synchronize these skills into the local Codex skill directory, normally:

1. `C:\Users\<user>\.codex\skills`

The source of truth must be the platform repository, not one developer's local profile.

The skill sync mechanism must preserve local non-Lotus skills and must never delete unknown user skills.

The bootstrap system should maintain a small skill manifest for Lotus-owned skills so it can report:

1. skill present,
2. skill missing,
3. skill stale,
4. skill locally modified,
5. source unavailable.

### Agent operating contract synchronization

RFC-0073 already introduced `context/AGENTS-OPERATING-CONTRACT.md` and synchronization automation.

RFC-0074 extends this into onboarding:

1. new-machine setup must validate whether deployed `AGENTS.md` matches the governed source,
2. bootstrap must offer a safe synchronization path,
3. onboarding docs must explain when to update the governed source versus the deployed global file.

If the deployed global file has local modifications, bootstrap must not overwrite it silently. It must either:

1. report drift only,
2. create a timestamped backup before sync,
3. or require an explicit force flag documented in the onboarding guide.

### New chat first prompt standard

The agent ramp-up guide must publish the standard first prompt.

Proposed baseline prompt:

```text
Read the Lotus context entrypoint at C:\Users\Sandeep\projects\lotus-platform\context\LOTUS-QUICKSTART-CONTEXT.md, then the context reference map, then the target repository's REPOSITORY-ENGINEERING-CONTEXT.md if present. Load only the RFC, skill, playbook, or standard needed for this task. Summarize the repo, branch, task intent, applicable standards, and validation lane before making changes. Keep context lean, use GitHub asynchronously for long-running checks, and update durable context docs when platform or repo reality changes.
```

The guide may provide a path-agnostic template for other machines:

```text
Read <lotus-platform>/context/LOTUS-QUICKSTART-CONTEXT.md, then <lotus-platform>/context/CONTEXT-REFERENCE-MAP.md, then the target repository's REPOSITORY-ENGINEERING-CONTEXT.md if present. Load only the RFC, skill, playbook, or standard needed for this task. Summarize the repo, branch, task intent, applicable standards, and validation lane before making changes. Keep context lean, use GitHub asynchronously for long-running checks, and update durable context docs when platform or repo reality changes.
```

The guide must also include a short first-turn checklist for the agent:

1. identify repo and branch,
2. identify applicable RFC or standard,
3. identify required skills,
4. identify smallest validation lane,
5. identify whether GitHub async monitoring is required,
6. identify whether context docs need updates if the task changes durable truth.

### Context-loading standard

Agents should not load every context document by default.

The required loading model is:

1. quickstart context first,
2. reference map second,
3. repository-local context third,
4. task-specific RFC, playbook, skill, or standard only when needed,
5. manifest for structured lookups where it is enough,
6. deeper central engineering context when architectural reasoning or governance interpretation is required.

This prevents both failure modes:

1. too little context, causing low-quality or wrong-layer implementation,
2. too much context, wasting the context window and reducing execution quality.

### Context budget tiers

The agent ramp-up guide must define three context tiers.

#### Tier 1: Startup context

Use for most new tasks:

1. quickstart context,
2. reference map,
3. target repository context,
4. task-specific skill.

#### Tier 2: Governance context

Use when a task affects standards, CI, runtime, cross-repo contracts, or platform architecture:

1. Tier 1,
2. active RFC,
3. relevant standard,
4. procedural playbook.

#### Tier 3: Deep context

Use only when architectural trade-offs, broad refactors, or cross-repo incident resolution require it:

1. Tier 2,
2. engineering context,
3. recent architectural decisions digest,
4. platform engineering ledger,
5. specific historical RFCs or runbooks.

The default must be Tier 1, not Tier 3.

## Placement

Central platform-owned files:

1. `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`
2. `docs/onboarding/LOTUS-AGENT-RAMP-UP.md`
3. `automation/Bootstrap-LotusDeveloperEnvironment.ps1`
4. `automation/Validate-LotusDeveloperEnvironment.ps1`
5. `codex/skills/`

Existing files to link or update during implementation:

1. `context/LOTUS-QUICKSTART-CONTEXT.md`
2. `context/LOTUS-ENGINEERING-CONTEXT.md`
3. `context/CONTEXT-REFERENCE-MAP.md`
4. `context/AGENTS-OPERATING-CONTRACT.md`
5. `context/PROCEDURAL-MEMORY-INDEX.md`
6. `context/playbooks/PR-LOOP-PLAYBOOK.md`
7. `context/playbooks/VALIDATION-PLAYBOOK.md`
8. `automation/README.md`
9. `Local Development Runbook.md`

Repository-local documents should only link to the onboarding guide where repo-specific setup depends on platform bootstrap. They must not duplicate the full onboarding procedure.

## Requirement Traceability

| Requirement | Governing Artifact Or Control | Completion Evidence |
| --- | --- | --- |
| New developer can start from a fresh workspace | `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md` | onboarding doc and prerequisite checks |
| New chat can ramp up without prior memory | `docs/onboarding/LOTUS-AGENT-RAMP-UP.md` | first prompt, context tiers, first-turn checklist |
| Lotus skills are portable across machines | `codex/skills/` and skill manifest | skill inventory and sync validation |
| Global agent contract is consistent | `context/AGENTS-OPERATING-CONTRACT.md` and sync automation | drift check and safe sync behavior |
| Context loading is right-sized | context budget tiers | agent ramp-up guide and context references |
| Local readiness is inspectable | readiness validator | redacted `.json` and `.md` reports |
| Secrets are protected | redaction rules and tests | redaction tests and report review |
| Heavy validation is not accidental | validation profiles | fast, extended, and explicit platform profiles |
| Repo-local truth remains local | repository context cross-links | repo-local documents link centrally without duplicating |

## Prerequisite Classification

The onboarding guide must classify prerequisites into three groups.

### Required

Required items block normal Lotus development if missing:

1. Git,
2. GitHub CLI authentication,
3. PowerShell,
4. Python runtime used by platform automation,
5. Node runtime for frontend repositories,
6. Docker for runtime and platform validation tasks,
7. local repository layout,
8. platform context artifacts.

### Required for full-stack validation

These may not block documentation or small code work, but block stack bring-up and demo validation:

1. canonical ingress host mappings,
2. local DSN posture,
3. Docker daemon health,
4. seeded-data prerequisites,
5. service-specific environment variables.

### Optional

Optional items should be reported but should not block bootstrap:

1. browser automation dependencies unless UI validation is requested,
2. local performance tooling unless performance validation is requested,
3. repo-specific convenience tools.

## Bootstrap Modes

The automation should support at least three modes.

### Inspect mode

Purpose:

1. read-only readiness assessment,
2. safe for any machine,
3. produces a clear report of missing prerequisites and stale context artifacts.

### Sync mode

Purpose:

1. synchronize Lotus Codex skills,
2. synchronize or validate `AGENTS.md`,
3. update derived local guidance artifacts where safe.

Sync mode must not overwrite user-edited files without clear backup or confirmation semantics.

Sync mode must be scoped. A user or agent should be able to run:

1. skills-only sync,
2. `AGENTS.md` sync,
3. context validation only,
4. all safe sync operations.

### Validate mode

Purpose:

1. prove the machine is ready for normal Lotus development,
2. validate repo presence, toolchain, GitHub auth, Docker, ingress, DSN posture, and context integrity,
3. avoid full E2E unless explicitly requested.

Validate mode must be split into fast and extended profiles:

1. fast profile for default readiness,
2. extended profile for Docker, ingress, DSN, and optional stack posture,
3. explicit platform profile for full stack bring-up and panel/data validation.

## Secrets And Environment Rules

Bootstrap automation must never print secrets.

It may validate that required environment variables exist, but output must redact values.

DSN validation must be posture-based unless the user explicitly requests a connectivity check:

1. present or missing,
2. expected variable name,
3. target class such as local Docker PostgreSQL,
4. redacted preview only if necessary.

Redaction must be tested. Any value with credential-like keys such as `password`, `token`, `secret`, `key`, `dsn`, or `connection` must be redacted in human and JSON reports unless the value is a documented non-secret enum.

## Developer Experience Rules

The bootstrap system must not make everyday development slower.

Required rules:

1. default checks must be fast,
2. heavy stack bring-up is opt-in,
3. full platform E2E is opt-in,
4. checks must produce actionable output,
5. repeated runs must be idempotent,
6. automation must explain exactly what it changed,
7. validation failures must include next-step commands where safe,
8. automation must avoid restarting Docker services unless an explicit runtime profile is selected,
9. bootstrap must not modify repositories other than `lotus-platform` unless the selected mode explicitly requires cross-repo context-link rollout.

## Error Handling And Exit Codes

Scripts must have stable exit behavior:

1. exit `0` when status is `ready` or when only informational optional checks are skipped,
2. exit non-zero when required prerequisites are blocked,
3. distinguish validation failure from script failure in the output report,
4. write a partial report even when one check fails unexpectedly,
5. include remediation text for every blocked required check.

## Relationship To RFC-0072

RFC-0072 governs CI lanes and release confidence.

RFC-0074 governs local and agent bootstrap.

The relationship is:

1. onboarding must explain how to use RFC-0072 lanes correctly,
2. bootstrap should run only fast local readiness checks by default,
3. long-running validation should be delegated to GitHub or explicit platform validation flows,
4. PR-loop guidance should teach asynchronous monitoring and fix-forward patterns,
5. bootstrap reports should identify which RFC-0072 validation lane a user should run next instead of blindly running every check.

## Relationship To RFC-0073

RFC-0073 governs durable engineering context.

RFC-0074 governs how a new machine or new developer obtains and uses that context repeatably.

RFC-0074 must not duplicate RFC-0073 content. It should link to it and automate access to it.

## Implementation Governance

Implementation must follow these rules:

1. no automation before RFC approval,
2. one slice at a time,
3. each slice must update tests and docs in the same commit or PR,
4. each script slice must include meaningful tests for the behavior introduced,
5. no script may print secrets,
6. no script may mutate user files without explicit sync mode and documented backup behavior,
7. all generated reports must be deterministic enough for review and automation,
8. every durable new operating pattern must be linked from the RFC-0073 context system.

## Implementation Slices

### Slice 1: Onboarding RFC approval and documentation skeleton

Outcome:

1. RFC-0074 is approved,
2. onboarding document names and ownership are locked,
3. implementation checklist exists.

Acceptance criteria:

1. this RFC is reviewed and approved,
2. no bootstrap automation is implemented before approval,
3. the checklist defines the delivery order,
4. source-of-truth boundaries, context budget tiers, bootstrap modes, report contract, and safety rules are approved.

### Slice 2: Developer onboarding guide

Outcome:

1. a new developer can follow one guide after `git pull`,
2. prerequisites and repo setup are explicit,
3. local development and demo-readiness paths are separated.

Acceptance criteria:

1. `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md` exists,
2. it covers prerequisites, repo layout, GitHub auth, Docker, ingress, DSN posture, skill sync, and validation depth,
3. it classifies prerequisites into required, full-stack, and optional groups,
4. it separates fast local development from demo/full-stack validation,
5. it links to RFC-0071, RFC-0072, RFC-0073, local development runbook, and context docs.

### Slice 3: Agent ramp-up guide and first-prompt standard

Outcome:

1. a new chat window has a standard ramp-up prompt,
2. context-loading depth is governed,
3. skill selection and pattern-promotion rules are explicit.

Acceptance criteria:

1. `docs/onboarding/LOTUS-AGENT-RAMP-UP.md` exists,
2. it includes the path-specific and path-agnostic first prompt templates,
3. it defines the small-context-first loading model,
4. it defines Tier 1, Tier 2, and Tier 3 context-budget guidance,
5. it includes the first-turn checklist for repo, branch, standards, skills, validation lane, and context maintenance,
6. it links to RFC-0073 context artifacts and procedural memory.

### Slice 4: Skill distribution and synchronization design

Outcome:

1. Lotus-specific skills have a platform-owned source location,
2. bootstrap can validate and synchronize them without relying on one machine's local state.

Acceptance criteria:

1. `codex/skills/` exists or a clearly named equivalent is approved,
2. Lotus skills are copied or referenced from the governed source,
3. a skill manifest or equivalent inventory identifies Lotus-owned skills,
4. docs explain source-of-truth ownership and sync behavior,
5. sync preserves local non-Lotus skills and reports missing, stale, locally modified, and source-unavailable states,
6. no secret or machine-specific path is committed as authoritative.

### Slice 5: Bootstrap and validation automation

Outcome:

1. a new machine can run a repeatable readiness check,
2. bootstrap can sync safe local context artifacts,
3. output is actionable and redacted.

Acceptance criteria:

1. `automation/Bootstrap-LotusDeveloperEnvironment.ps1` exists,
2. `automation/Validate-LotusDeveloperEnvironment.ps1` exists,
3. scripts support inspect, sync, and validate behavior,
4. validate mode supports fast, extended, and explicit platform profiles,
5. scripts validate GitHub auth, Docker, Python, Node, repository presence, context docs, skill sync, AGENTS sync, ingress, and DSN posture,
6. scripts emit `output/developer-environment-readiness.json` and `.md`,
7. scripts apply stable statuses and exit semantics,
8. scripts are idempotent and safe.

### Slice 6: Validation coverage and drift control

Outcome:

1. onboarding artifacts are protected from silent drift,
2. bootstrap behavior has meaningful tests.

Acceptance criteria:

1. platform tests validate onboarding docs and cross-links,
2. script tests validate report structure and safe redaction behavior,
3. script tests validate idempotency and scoped sync behavior,
4. existing context validators are updated to include onboarding entrypoints where appropriate.

### Slice 7: Repository-local cross-link rollout

Outcome:

1. each Lotus repository points to the central onboarding guide without duplicating it.

Acceptance criteria:

1. repository-local context documents link to the central onboarding guide where appropriate,
2. local docs retain repo-specific setup truth,
3. no repo duplicates the full platform onboarding guide.

## Acceptance Criteria

RFC-0074 is complete when:

1. a new developer has one documented onboarding path,
2. a new agent has one documented ramp-up path,
3. Lotus-specific Codex skills are versioned and synchronizable from platform-owned artifacts,
4. `AGENTS.md` synchronization is part of onboarding,
5. bootstrap automation validates prerequisites and context readiness,
6. bootstrap automation emits redacted human and JSON readiness reports,
7. context-loading depth is governed and efficient,
8. no secrets are printed or committed,
9. onboarding artifacts are covered by drift checks or tests,
10. repository-local docs link to central onboarding without duplicating it,
11. the process is useful after a fresh `git pull` on a new machine without relying on prior chat history.

## Risks And Mitigations

Risk: onboarding becomes another stale document.

Mitigation: add validator coverage and make onboarding updates part of context-maintenance rules.

Risk: bootstrap scripts become destructive.

Mitigation: default to inspect mode, require explicit sync behavior, and never overwrite local artifacts silently.

Risk: skills drift between platform source and local Codex profile.

Mitigation: make platform-owned skills the source of truth and include sync validation.

Risk: new chat prompts load too much context.

Mitigation: publish a small-context-first loading model and route deeper reading through the reference map.

Risk: local setup checks become too slow.

Mitigation: separate fast readiness checks from explicit heavy platform validation.

## Approval Requested

Approve this RFC if the team agrees that Lotus should treat new-machine and new-agent bootstrap as platform infrastructure, implemented centrally in `lotus-platform`, with safe automation, governed context loading, skill synchronization, and a standard first prompt for future sessions.
