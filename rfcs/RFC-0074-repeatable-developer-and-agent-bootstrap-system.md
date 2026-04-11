# RFC-0074: Repeatable Developer and Agent Bootstrap System

- Status: Draft
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

Without a governed bootstrap system, RFC-0073 depends too much on a machine that has already been curated by prior work.

That is not sufficient for a banking-grade platform.

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

## Non-Goals

1. Replacing RFC-0073 context documents.
2. Replacing RFC-0072 CI and validation governance.
3. Running full platform E2E validation on every onboarding check.
4. Encoding secrets in documentation or automation.
5. Replacing repository-local setup details where local truth belongs in the repository.
6. Creating a new package manager or monorepo orchestration layer.

## Decision

Lotus will create a platform-owned onboarding and bootstrap system with four layers:

1. a human-readable onboarding guide,
2. repeatable local bootstrap automation,
3. governed Codex skill and agent-contract synchronization,
4. a context-loading and first-prompt standard.

The system will live centrally in `lotus-platform` because this is cross-repository platform infrastructure.

## Target State

### Central onboarding guide

Create:

1. `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`
2. `docs/onboarding/LOTUS-AGENT-RAMP-UP.md`

The developer onboarding guide owns machine and repository setup.

The agent ramp-up guide owns new-chat context loading, first prompt, skill selection, and context-window discipline.

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

### Skill distribution

Lotus-specific Codex skills must be versioned as platform artifacts.

Target location:

1. `codex/skills/`

Bootstrap automation should synchronize these skills into the local Codex skill directory, normally:

1. `C:\Users\<user>\.codex\skills`

The source of truth must be the platform repository, not one developer's local profile.

### Agent operating contract synchronization

RFC-0073 already introduced `context/AGENTS-OPERATING-CONTRACT.md` and synchronization automation.

RFC-0074 extends this into onboarding:

1. new-machine setup must validate whether deployed `AGENTS.md` matches the governed source,
2. bootstrap must offer a safe synchronization path,
3. onboarding docs must explain when to update the governed source versus the deployed global file.

### New chat first prompt standard

The agent ramp-up guide must publish the standard first prompt.

Approved baseline prompt:

```text
Read the Lotus context entrypoint at C:\Users\Sandeep\projects\lotus-platform\context\LOTUS-QUICKSTART-CONTEXT.md, then the context reference map, then the target repository's REPOSITORY-ENGINEERING-CONTEXT.md if present. Load only the RFC, skill, playbook, or standard needed for this task. Summarize the repo, branch, task intent, applicable standards, and validation lane before making changes. Keep context lean, use GitHub asynchronously for long-running checks, and update durable context docs when platform or repo reality changes.
```

The guide may provide a path-agnostic template for other machines:

```text
Read <lotus-platform>/context/LOTUS-QUICKSTART-CONTEXT.md, then <lotus-platform>/context/CONTEXT-REFERENCE-MAP.md, then the target repository's REPOSITORY-ENGINEERING-CONTEXT.md if present. Load only the RFC, skill, playbook, or standard needed for this task. Summarize the repo, branch, task intent, applicable standards, and validation lane before making changes. Keep context lean, use GitHub asynchronously for long-running checks, and update durable context docs when platform or repo reality changes.
```

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

### Validate mode

Purpose:

1. prove the machine is ready for normal Lotus development,
2. validate repo presence, toolchain, GitHub auth, Docker, ingress, DSN posture, and context integrity,
3. avoid full E2E unless explicitly requested.

## Secrets And Environment Rules

Bootstrap automation must never print secrets.

It may validate that required environment variables exist, but output must redact values.

DSN validation must be posture-based unless the user explicitly requests a connectivity check:

1. present or missing,
2. expected variable name,
3. target class such as local Docker PostgreSQL,
4. redacted preview only if necessary.

## Developer Experience Rules

The bootstrap system must not make everyday development slower.

Required rules:

1. default checks must be fast,
2. heavy stack bring-up is opt-in,
3. full platform E2E is opt-in,
4. checks must produce actionable output,
5. repeated runs must be idempotent,
6. automation must explain exactly what it changed.

## Relationship To RFC-0072

RFC-0072 governs CI lanes and release confidence.

RFC-0074 governs local and agent bootstrap.

The relationship is:

1. onboarding must explain how to use RFC-0072 lanes correctly,
2. bootstrap should run only fast local readiness checks by default,
3. long-running validation should be delegated to GitHub or explicit platform validation flows,
4. PR-loop guidance should teach asynchronous monitoring and fix-forward patterns.

## Relationship To RFC-0073

RFC-0073 governs durable engineering context.

RFC-0074 governs how a new machine or new developer obtains and uses that context repeatably.

RFC-0074 must not duplicate RFC-0073 content. It should link to it and automate access to it.

## Implementation Slices

### Slice 1: Onboarding RFC approval and documentation skeleton

Outcome:

1. RFC-0074 is approved,
2. onboarding document names and ownership are locked,
3. implementation checklist exists.

Acceptance criteria:

1. this RFC is reviewed and approved,
2. no bootstrap automation is implemented before approval,
3. the checklist defines the delivery order.

### Slice 2: Developer onboarding guide

Outcome:

1. a new developer can follow one guide after `git pull`,
2. prerequisites and repo setup are explicit,
3. local development and demo-readiness paths are separated.

Acceptance criteria:

1. `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md` exists,
2. it covers prerequisites, repo layout, GitHub auth, Docker, ingress, DSN posture, skill sync, and validation depth,
3. it links to RFC-0071, RFC-0072, RFC-0073, local development runbook, and context docs.

### Slice 3: Agent ramp-up guide and first-prompt standard

Outcome:

1. a new chat window has a standard ramp-up prompt,
2. context-loading depth is governed,
3. skill selection and pattern-promotion rules are explicit.

Acceptance criteria:

1. `docs/onboarding/LOTUS-AGENT-RAMP-UP.md` exists,
2. it includes the path-specific and path-agnostic first prompt templates,
3. it defines the small-context-first loading model,
4. it links to RFC-0073 context artifacts and procedural memory.

### Slice 4: Skill distribution and synchronization design

Outcome:

1. Lotus-specific skills have a platform-owned source location,
2. bootstrap can validate and synchronize them without relying on one machine's local state.

Acceptance criteria:

1. `codex/skills/` exists or a clearly named equivalent is approved,
2. Lotus skills are copied or referenced from the governed source,
3. docs explain source-of-truth ownership and sync behavior,
4. no secret or machine-specific path is committed as authoritative.

### Slice 5: Bootstrap and validation automation

Outcome:

1. a new machine can run a repeatable readiness check,
2. bootstrap can sync safe local context artifacts,
3. output is actionable and redacted.

Acceptance criteria:

1. `automation/Bootstrap-LotusDeveloperEnvironment.ps1` exists,
2. `automation/Validate-LotusDeveloperEnvironment.ps1` exists,
3. scripts support inspect, sync, and validate behavior,
4. scripts validate GitHub auth, Docker, Python, Node, repository presence, context docs, skill sync, AGENTS sync, ingress, and DSN posture,
5. scripts are idempotent and safe.

### Slice 6: Validation coverage and drift control

Outcome:

1. onboarding artifacts are protected from silent drift,
2. bootstrap behavior has meaningful tests.

Acceptance criteria:

1. platform tests validate onboarding docs and cross-links,
2. script tests validate report structure and safe redaction behavior,
3. existing context validators are updated to include onboarding entrypoints where appropriate.

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
6. context-loading depth is governed and efficient,
7. no secrets are printed or committed,
8. onboarding artifacts are covered by drift checks or tests,
9. repository-local docs link to central onboarding without duplicating it.

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
