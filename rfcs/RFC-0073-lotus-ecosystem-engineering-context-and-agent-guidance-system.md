# RFC-0073: Lotus Ecosystem Engineering Context and Agent Guidance System

- Status: Proposed
- Date: 2026-04-11
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
  - `RFC-0041-platform-integration-architecture-bible-governance.md`
  - `RFC-0048-shared-automation-and-agent-toolkit.md`
  - `RFC-0057-test-pyramid-and-meaningful-coverage-governance.md`
  - `RFC-0060-phase-2-shared-standards-and-automated-conformance.md`
  - `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`
  - `RFC-0070-gold-standard-product-experience-foundation-and-ownership-model.md`
  - `RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`

## Summary

Lotus needs one governed engineering-context system that allows any future coding agent to start a new chat and quickly become effective across the ecosystem without relying on fragile prior conversation history.

This RFC proposes a platform-owned context architecture with:

1. one central quickstart context document,
2. one central canonical engineering context document,
3. one central reference map,
4. one machine-readable ecosystem context manifest,
5. one repository-local engineering context document per Lotus repository,
6. one revised `AGENTS.md` operating contract that cross-links the governed context set.

The goal is not to create more documentation for its own sake. The goal is to reduce onboarding time, improve agent output quality, reduce repeated explanation, and make Lotus engineering expectations durable, explicit, and reusable.

This RFC treats context as platform infrastructure.

## Problem

Lotus now spans multiple repositories, multiple product surfaces, multiple domain services, multiple engineering standards, and multiple operational workflows.

A new coding agent currently has to infer too much from:

1. partial repository READMEs,
2. RFC history,
3. runbooks,
4. prior chat context,
5. local branch history,
6. scattered `AGENTS.md` instructions,
7. implicit engineering norms discovered only after repeated interaction.

This creates real operational and quality costs:

1. ramp-up is slower than it should be,
2. the same platform explanation is repeated across sessions,
3. agents can miss important standards or architectural boundaries,
4. repo-local truth and platform-wide truth are not clearly separated,
5. reusable delivery patterns remain trapped in chat history instead of being promoted into durable guidance,
6. documentation drift becomes likely when context responsibilities are not clearly defined,
7. `AGENTS.md` risks becoming either too thin to be useful or too large to remain trustworthy.

For a banking-grade platform, this is not acceptable. Context quality is part of engineering quality.

## Goals

1. Provide a governed starting point that gives any future agent immediate Lotus ecosystem context.
2. Separate platform-wide truth from repository-local truth cleanly.
3. Define a maintainable documentation structure that avoids duplication and drift.
4. Turn key ecosystem knowledge into durable, discoverable guidance.
5. Improve Codex efficiency, consistency, and delivery quality in new sessions.
6. Ensure Lotus engineering expectations are explicit, enforceable, and reusable.
7. Make `AGENTS.md` a strong operational entrypoint rather than an overloaded knowledge dump.
8. Support both human engineers and coding agents with the same context architecture.
9. Introduce a machine-readable context layer that can support tooling, automation, and future validation.

## Non-Goals

1. Replacing all READMEs, standards, RFCs, or runbooks with one mega-document.
2. Capturing every implementation detail of every repository in a single file.
3. Making `AGENTS.md` the full knowledge base for the platform.
4. Implementing context-drift automation in the same slice as this approval RFC.
5. Treating undocumented tribal knowledge as acceptable once the system exists.

## Why This RFC Is Needed Now

Lotus has already reached a complexity level where ad hoc onboarding is wasteful and risky.

The ecosystem now includes:

1. multiple backend domain services,
2. one experience API (`lotus-gateway`),
3. one primary product UI (`lotus-workbench`),
4. platform-owned ingress, automation, validation, and CI governance,
5. shared engineering and vocabulary standards,
6. domain-heavy portfolio, advisory, risk, performance, and reporting workflows.

At this stage:

1. context is no longer local to one repository,
2. standards are no longer optional knowledge,
3. new sessions need a trustworthy entrypoint,
4. agents must be able to act like domain-aware, banking-grade engineers from the start.

Without this RFC:

1. each new session will continue to spend avoidable time rebuilding the same mental model,
2. important expectations will remain implicit,
3. repo-local documentation will drift from platform reality,
4. reusable patterns will continue to be discovered repeatedly instead of codified once.

## Decision

Lotus will adopt a layered, platform-owned engineering context system with central and repository-local documents, plus a machine-readable manifest.

### Required context layers

The approved target state is:

1. `AGENTS.md` as the short operational entrypoint,
2. `LOTUS-QUICKSTART-CONTEXT.md` as the fast orientation layer,
3. `LOTUS-ENGINEERING-CONTEXT.md` as the canonical ecosystem context,
4. `CONTEXT-REFERENCE-MAP.md` as the curated navigation layer,
5. `lotus-context-manifest.json` as the machine-readable ecosystem map,
6. `REPOSITORY-ENGINEERING-CONTEXT.md` in each Lotus repository as the repository-local truth.

### Core rule

Platform-wide truth lives centrally in `lotus-platform`.

Repository-specific truth lives in the owning repository.

The system must make this distinction explicit and durable.

## Target State Structure

### 1. `AGENTS.md`

Role:

1. short operational contract,
2. mandatory reading order,
3. mandatory working rules,
4. maintenance obligation for the context system,
5. cross-links to the governed context documents.

`AGENTS.md` must not become the full ecosystem encyclopedia.

It should remain concise, stable, and strict.

### 2. `LOTUS-QUICKSTART-CONTEXT.md`

Role:

1. five-minute orientation layer,
2. high-signal introduction for a new agent or engineer,
3. minimal working set before reading deeper material.

This should explain:

1. what Lotus is,
2. what the major apps are,
3. how the platform is generally structured,
4. how work should be approached safely and correctly,
5. where to read next.

### 3. `LOTUS-ENGINEERING-CONTEXT.md`

Role:

1. canonical ecosystem context,
2. platform-wide engineering expectations,
3. architectural and operational truth for how Lotus is built and maintained.

This is the main durable context document for future sessions.

### 4. `CONTEXT-REFERENCE-MAP.md`

Role:

1. curated navigation to important supporting docs,
2. reduce context search overhead,
3. help agents choose the right reading path for the task type.

This file should not restate the full content of standards or RFCs. It should route to them.

### 5. `lotus-context-manifest.json`

Role:

1. machine-readable representation of the Lotus ecosystem,
2. structured repo and service inventory,
3. consumable by automation and future validators,
4. lightweight context cache for deterministic tooling.

This is a strategic asset. It allows platform tooling and future agents to reason over the estate without scraping prose first.

### 6. `REPOSITORY-ENGINEERING-CONTEXT.md`

Role:

1. repository-local operating truth,
2. app-specific architecture and commands,
3. local testing, CI, and integration reality,
4. local constraints and non-obvious patterns.

Every repository gets one.

## Recommended Placement

### Central documents

Central documents must live in `lotus-platform` because:

1. `lotus-platform` already owns shared automation and standards,
2. platform-wide architecture and governance belong there,
3. the central context is cross-repository by nature,
4. this minimizes duplication and prevents inconsistent platform narratives.

Recommended location:

1. `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`
2. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
3. `lotus-platform/context/CONTEXT-REFERENCE-MAP.md`
4. `lotus-platform/context/lotus-context-manifest.json`

### Repository-local documents

Repository-local context belongs in each repository because:

1. local architecture changes faster than platform principles,
2. repo-native commands and module maps must stay close to the code,
3. local ownership is clearer,
4. platform context should not become a shadow copy of every repository.

Recommended location:

1. `<repo>/REPOSITORY-ENGINEERING-CONTEXT.md`

This should be standardized across the Lotus estate.

## Why This Structure Is Best

### Alternative 1: One central document only

Rejected.

Reason:

1. central-only documentation becomes too abstract for implementation work,
2. it cannot remain accurate for repo-native commands and local module realities,
3. it forces agents to hunt for local truth anyway.

### Alternative 2: One large local document in every repository

Rejected.

Reason:

1. platform-wide information will drift immediately,
2. the same ecosystem explanation will be duplicated everywhere,
3. standards will become inconsistent across repositories.

### Alternative 3: Keep only `AGENTS.md` plus existing docs

Rejected.

Reason:

1. `AGENTS.md` is not the right vehicle for durable multi-layer context,
2. existing docs are too scattered,
3. the next session still pays high ramp-up costs,
4. the system remains dependent on chat memory.

### Chosen approach: Central plus local, with manifest support

Accepted because it gives:

1. one authoritative ecosystem narrative,
2. one authoritative engineering standard posture,
3. one fast-entry orientation layer,
4. one machine-readable map,
5. one local truth document per repository,
6. lower duplication,
7. lower drift risk,
8. better long-term maintainability.

## Content Ownership Rules

### Content that belongs centrally

The central context documents must own:

1. what Lotus is,
2. the role of each application,
3. architectural relationships between applications,
4. platform operating model,
5. engineering and development standards,
6. gold-standard delivery expectations,
7. testing philosophy and test pyramid expectations,
8. API quality and UI/backend alignment expectations,
9. observability, reliability, performance, scalability, and production-readiness expectations,
10. naming and domain vocabulary standards,
11. agent operating expectations,
12. how reusable patterns are promoted into durable guidance,
13. how context documents are maintained and cross-linked.

### Content that belongs locally

Each repository-local context document must own:

1. repository purpose,
2. business and domain responsibility,
3. local architecture and module map,
4. runtime dependencies and upstream/downstream relationships,
5. repo-native commands,
6. CI lane expectations for that repo,
7. local testing expectations,
8. important local standards and RFCs,
9. known implementation constraints,
10. common pitfalls and established patterns for that repo.

### Content that belongs in the manifest

The machine-readable manifest should include:

1. repository name,
2. repository category,
3. business role,
4. primary runtime and language,
5. canonical startup command,
6. canonical quality commands,
7. major upstream and downstream dependencies,
8. key documentation paths,
9. ownership classification,
10. whether browser validation, contract validation, or platform E2E validation applies.

## Required Central Content

The central context system must explain:

1. what Lotus is,
2. the role of each application in the ecosystem,
3. the architectural relationship between the applications,
4. what engineering standards and development standards the ecosystem follows,
5. how code is expected to be written,
6. what gold-standard delivery looks like,
7. how changes should be approached in a banking-grade, production-critical platform.

It must also define the working expectations that already guide Lotus delivery, including:

1. always look for opportunities to reduce complexity and improve the codebase,
2. make the code cleaner, more readable, more maintainable, and more modular,
3. make code and test improvements that materially improve reliability and maintainability,
4. add or update documentation wherever necessary,
5. leave the codebase cleaner than you found it,
6. always write meaningful, high-value tests and never superficial ones,
7. keep making small, meaningful commits,
8. ensure every UI feature is genuinely backed by supported backend functionality and is not implemented superficially.

It must also capture the ecosystem standards we want:

1. significantly stronger tests,
2. better reusability,
3. better consistency,
4. higher scalability,
5. better performance,
6. lower latency,
7. greater modularity,
8. stronger reliability,
9. clean code and maintainable design,
10. polished, production-ready finish,
11. enterprise-grade engineering quality.

## Agent Operating Expectations

The context system must define how an agent is expected to work in Lotus.

Required topics:

1. what skills, patterns, and working methods the agent should use,
2. how the agent chooses and applies the right skills for a task,
3. how the agent recognizes repeatable patterns and turns them into reusable practice,
4. how the agent updates or adds guidance when a new repeatable pattern emerges,
5. how the context system references other important standards, RFCs, runbooks, and local docs.

### Mandatory agent posture

The agent is expected to behave as a banking-grade engineer, not a generic coding assistant.

That means:

1. it acts with domain awareness,
2. it prefers truthful implementation over surface-level output,
3. it chooses reusable patterns over local hacks,
4. it treats architecture, naming, standards, and tests as part of the implementation, not documentation-only concerns.

## Naming and Vocabulary Standards

The context system must define how naming and terminology should work across the Lotus estate.

Required topics:

1. file naming,
2. function naming,
3. type and object naming,
4. attribute naming,
5. API naming,
6. domain vocabulary,
7. business-language posture.

The guidance must explicitly instruct agents to use:

1. private banking language,
2. portfolio analytics language,
3. advisory and investment workflow language,
4. risk, performance, and reporting domain-correct terminology,
5. institutional, front-office, and banking-grade wording rather than generic SaaS language.

## Documentation Maintenance and Drift Control

This RFC requires explicit maintenance rules.

### Mandatory update rule

When platform reality changes, the relevant context documents must be updated in the same slice.

Examples:

1. architectural relationships change,
2. repository responsibilities change,
3. startup or validation commands change,
4. CI lane expectations change,
5. reusable patterns become durable enough to codify,
6. naming or vocabulary standards evolve,
7. operating guidance in `AGENTS.md` changes.

### Central vs local update rule

If the change is platform-wide:

1. update the central context documents.

If the change is repository-specific:

1. update the repository-local context document.

If both platform truth and repository truth changed:

1. update both.

### Cross-link maintenance rule

`AGENTS.md` must always point to:

1. the quickstart context,
2. the central engineering context,
3. the reference map,
4. the repository-local context.

Repository-local context documents must point back to the central context and reference map.

## Additional Measures to Improve Agent Efficiency and Quality

This RFC does not stop at prose documentation. It explicitly recognizes that better agent performance also depends on structure and tooling.

### Required supporting improvements

The target-state system should support:

1. layered reading order,
2. machine-readable manifest consumption,
3. task-type routing guidance,
4. reusable pattern capture,
5. future context-drift validation.

### Quickstart layer

The quickstart document should reduce ramp-up time in new sessions by giving a minimal but correct working set.

### Task-routing guidance

The central context and reference map should help the agent decide what to read for:

1. frontend work,
2. backend work,
3. cross-app validation work,
4. documentation and RFC work,
5. platform automation and CI work.

### Pattern promotion rule

If a repeatable pattern emerges across tasks or repositories, it should be promoted into one of:

1. a standard,
2. a runbook,
3. a repository context update,
4. a central context update,
5. a skill update or new skill where appropriate.

This is how Lotus turns repeated explanation into durable engineering memory.

## Required `AGENTS.md` Changes

This RFC requires a full rework of `AGENTS.md`.

The revised `AGENTS.md` must:

1. act as the short operational entrypoint,
2. define the mandatory reading order,
3. cross-link the central and repository-local context documents,
4. define mandatory operating rules and delivery expectations,
5. require context maintenance when platform or repo reality changes,
6. stay short enough to remain trustworthy and actively used.

`AGENTS.md` must not try to duplicate the full central context.

## Implementation Slices

### Slice 1: Central context architecture

Outcome:

1. the central context document set exists,
2. naming, placement, and ownership are standardized,
3. the machine-readable manifest exists.

Acceptance criteria:

1. `lotus-platform/context/` contains the approved central context files,
2. the central context documents cross-link correctly,
3. the manifest has an initial full ecosystem inventory.

### Slice 2: `AGENTS.md` modernization

Outcome:

1. `AGENTS.md` becomes the short operational contract,
2. it links to the governed context set,
3. it includes context maintenance obligations.

Acceptance criteria:

1. `AGENTS.md` references the new context system,
2. `AGENTS.md` does not duplicate the full context body,
3. mandatory reading order is explicit.

### Slice 3: Repository-local context rollout

Outcome:

1. every Lotus repository contains a standardized repository-local engineering context document,
2. repo-local truth is explicit and discoverable.

Acceptance criteria:

1. all in-scope repositories have `REPOSITORY-ENGINEERING-CONTEXT.md`,
2. each repo-local document links to the central context system,
3. each repo-local document includes repo-native commands and local architecture context.

### Slice 4: Reference map and task-routing hardening

Outcome:

1. the central reference map is complete,
2. task-type guidance reduces context search and onboarding waste.

Acceptance criteria:

1. the reference map routes agents to the right standards, RFCs, and repo docs,
2. the quickstart and engineering context docs include task-routing guidance.

### Slice 5: Drift control and validation foundation

Outcome:

1. context drift becomes visible rather than silent,
2. the context system is treated as maintained engineering infrastructure.

Acceptance criteria:

1. platform validation includes at least basic checks for context-system presence and cross-link correctness,
2. maintenance rules are enforced through platform-owned governance or documentation contract tests.

## Risks and Trade-Offs

1. If the central context document becomes too large, agents will stop using it effectively.
2. If repo-local documents restate platform-wide material, drift will accelerate.
3. If `AGENTS.md` tries to hold all knowledge, it will become noisy and stale.
4. If no maintenance rule exists, the context system will decay quickly.
5. If no machine-readable layer exists, future automation value will be reduced.

Mitigations:

1. keep context layered,
2. keep central versus local ownership explicit,
3. keep `AGENTS.md` concise,
4. use the reference map to reduce duplication,
5. add validation and drift-control mechanisms in later slices.

## Acceptance Criteria

This RFC is complete when:

1. Lotus has a platform-owned central engineering context system,
2. every Lotus repository has a repository-local engineering context document,
3. `AGENTS.md` is revised to cross-link and govern the system,
4. the central context documents define engineering, delivery, naming, documentation, testing, observability, and production-readiness expectations,
5. the machine-readable manifest exists and is usable,
6. maintenance rules are explicit,
7. context becomes a durable and trusted onboarding foundation for future agent sessions.

## Approval Requested

Approve this RFC if the team agrees that:

1. Lotus should treat engineering context as governed platform infrastructure,
2. the right target state is a layered context system rather than one oversized file,
3. `lotus-platform` should own the central context documents and manifest,
4. each repository should own its local engineering context document,
5. `AGENTS.md` should become the operational entrypoint and not the full knowledge base,
6. this system should be implemented before further relying on ad hoc session memory for cross-repository engineering work.
