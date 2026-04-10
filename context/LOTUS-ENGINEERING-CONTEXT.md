# Lotus Engineering Context

This is the canonical ecosystem context for Lotus engineering work.

Use this file after the [Lotus Quickstart Context](./LOTUS-QUICKSTART-CONTEXT.md). Use the repository-local `REPOSITORY-ENGINEERING-CONTEXT.md` for implementation truth inside a specific repository.

## Purpose

Lotus is a governed private banking technology ecosystem. It is not a loose collection of apps.

The ecosystem is designed to support:

1. portfolio management,
2. performance analytics,
3. risk analytics,
4. advisory workflows,
5. reporting and evidence production,
6. platform-grade runtime, validation, CI, ingress, and governance.

The engineering goal is a premium, production-critical, banking-grade platform where architecture clarity, operational rigor, and domain correctness are non-negotiable.

## Application Roles

### Product and experience layer

1. `lotus-workbench`
   The primary product UI. It should present a coherent banking-grade user experience and consume the unified contract from `lotus-gateway`.

2. `lotus-gateway`
   The experience API and composition layer. It provides the governed client contract for UI experiences and mediates access to domain services.

### Domain-authoritative services

1. `lotus-core`
   Authoritative for portfolio, booking, account, holding, mandate, and transaction domain data.

2. `lotus-performance`
   Authoritative for performance metrics, period analytics, and related review data.

3. `lotus-risk`
   Authoritative for drawdown, attribution, concentration, rolling risk, and related analytics.

4. `lotus-advise`
   Advisory workflow and recommendation capability.

5. `lotus-manage`
   Portfolio-management and operational workflow capability.

6. `lotus-report`
   Reporting and document generation capability.

7. `lotus-ai`
   Shared AI capability service used behind governed product and platform flows.

### Platform and governance

1. `lotus-platform`
   Owner of shared automation, ingress, standards, validation, CI governance, and environment-level operational guidance.

## Architectural Relationships

The canonical relationship model is:

1. `lotus-workbench` consumes `lotus-gateway`,
2. `lotus-gateway` consumes or aggregates domain-authoritative services,
3. domain services remain authoritative for their business domain,
4. `lotus-platform` governs how the ecosystem is run, validated, and standardized.

### Boundary rules

1. UI features must not be superficially invented at the presentation layer.
2. Experience composition belongs in `lotus-gateway`, not scattered into direct UI-to-service coupling.
3. Domain-specific business logic belongs in the authoritative service or a governed view-model layer, not as uncontrolled UI logic.
4. Standards, validators, and platform automation are part of the architecture and should be maintained with the same discipline as product code.

## Engineering Standards

Lotus engineering is expected to be:

1. clean,
2. modular,
3. readable,
4. domain-correct,
5. reliable,
6. scalable,
7. observable,
8. production-ready.

### Required delivery posture

Always:

1. look for opportunities to reduce complexity,
2. make the codebase cleaner, more readable, more maintainable, and more modular,
3. make code and test improvements that materially improve reliability and maintainability,
4. add or update documentation wherever necessary,
5. leave the codebase cleaner than you found it,
6. write meaningful, high-value tests and avoid superficial coverage,
7. keep making small, meaningful commits,
8. remove dead code, duplication, and non-standard legacy handling when encountered,
9. ensure every UI feature is genuinely backed by supported backend functionality.

### Clean code principles

1. prefer explicit, well-scoped responsibilities over convenience coupling,
2. avoid duplicated policy or logic across repositories and layers,
3. prefer shared reusable patterns over page-local or file-local hacks,
4. make naming precise, domain-correct, and stable,
5. remove stale abstractions when the product direction changes,
6. keep public contracts intentional and documented.

### Modular design principles

1. separate platform truth from repository-local truth,
2. separate domain authority from composition and presentation,
3. prefer well-defined modules and validators over ad hoc scripts,
4. treat automation and runbooks as product-quality operational code,
5. push repeatable patterns into standards, templates, skills, or validators once they recur.

## Testing Standards And Validation Model

Lotus follows the test pyramid and meaningful coverage posture defined by platform standards.

Expected validation layers include:

1. fast unit tests for local logic,
2. contract and integration tests for domain boundaries,
3. browser or end-to-end validation where product experience matters,
4. platform validation for canonical stack bring-up, ingress, seeded data, and cross-app flows,
5. CI lane validation with fast feature gates, PR merge gates, main releasability gates, and platform end-to-end validation where applicable.

### Test quality rules

1. test business and contract behavior, not just implementation trivia,
2. add regression tests for every real defect you fix,
3. prefer deterministic, minimal, high-signal tests,
4. remove stale assertions that no longer reflect the product contract,
5. keep repo-native commands truthful to the actual CI contract.

## Documentation Quality Standards

Documentation in Lotus is part of the delivery artifact.

Update docs when:

1. architecture changes,
2. commands change,
3. runtime or validation flow changes,
4. standards or CI rules change,
5. a repeatable pattern is worth codifying,
6. a repository’s current-state reality materially changes.

Central docs own platform truth.

Repository-local docs own repo truth.

Do not duplicate central policy prose into every repo unless repo-local interpretation is required.

## API Quality And UI Alignment

Lotus APIs and product surfaces are expected to be:

1. clear,
2. consistent,
3. domain-correct,
4. fully modeled,
5. documented,
6. aligned with authoritative ownership boundaries.

### API and UI rules

1. use business-language contracts rather than generic field naming,
2. keep gateway contracts governed and explicit,
3. do not ship UI flows that are not supported by backend capability,
4. do not mask backend gaps with decorative UI or fabricated content,
5. keep empty, partial, loading, ready, and error states explicit for data modules.

## Performance, Reliability, And Production Readiness

Lotus delivery should optimize for:

1. front-office trust,
2. operational clarity,
3. performance and low latency,
4. strong reliability,
5. maintainable observability,
6. stable production posture.

This means:

1. avoid unnecessary runtime cost and repeated work,
2. treat latency and performance regressions as product quality issues,
3. keep Docker, ingress, runtime, and validation paths repeatable,
4. provide evidence for readiness through CI artifacts, validation summaries, and truthful checks.

## Naming And Vocabulary Standards

Naming should reflect banking and investment domain reality.

Preferred vocabulary should come from:

1. private banking,
2. portfolio management,
3. performance analytics,
4. risk analytics,
5. advisory workflows,
6. reporting and investment-review language.

### Naming rules

1. file names should describe stable responsibility,
2. functions and objects should use domain-correct verbs and nouns,
3. APIs should prefer explicit business meaning over generic placeholders,
4. avoid generic labels such as `widget`, `thing`, `item`, or `stats` when a domain term exists,
5. use domain-correct terms such as `portfolio`, `benchmark`, `mandate`, `allocation`, `attribution`, `drawdown`, `exposure`, `supportability`, `readiness`, `booking`, `holding`, `proposal`, and `evidence` where appropriate.

## Agent Operating Expectations

Agents working in Lotus are expected to operate like disciplined banking-grade engineers.

### Mandatory posture

1. choose the smallest correct working set of context,
2. use standards, skills, validators, and runbooks before improvising a new local pattern,
3. prefer async GitHub-backed heavy execution when it is more efficient than repeated heavyweight local reruns,
4. promote repeatable patterns into durable guidance,
5. keep repo and platform context current when reality changes.

### Skills and working methods

Use the right skill or workflow for the task:

1. backend delivery governance for backend repos,
2. frontend delivery governance for UI work,
3. PR pre-merge governance for merge preparation,
4. QA or platform validator skills for stack and platform validation,
5. RFC or documentation skills for governance work.

When a repeatable pattern emerges:

1. update the relevant context document,
2. update an existing skill,
3. add a new skill if the pattern is durable and recurring,
4. add a validator or scaffold rule if executable enforcement is valuable.

## Human-Maintained Memory

The central curated memory layer is:

1. [Platform Engineering Ledger](./platform-engineering-ledger.md)
2. [Recent Architectural Decisions Digest](./recent-architectural-decisions-digest.md)

These files exist to preserve high-value practical guidance and recent platform reality across sessions.

## Structured Reusable Context

The machine-readable ecosystem map is:

1. [lotus-context-manifest.json](./lotus-context-manifest.json)

Use the manifest for:

1. ecosystem inventory,
2. repo roles,
3. canonical commands,
4. dependency and authority lookups,
5. context-path discovery.

## Procedural Memory

The governed procedural-memory layer lives in:

1. [Procedural Memory Index](./PROCEDURAL-MEMORY-INDEX.md)

Use it when you need durable guidance for:

1. change execution,
2. PR loops and async monitoring,
3. validation depth selection,
4. fix-forward response patterns.

## Related References

Use the [Context Reference Map](./CONTEXT-REFERENCE-MAP.md) to find:

1. active standards,
2. active RFCs,
3. runbooks,
4. domain references,
5. repository-local context documents.

## Task Routing Guidance

Use the [Task Routing Guide](./TASK-ROUTING-GUIDE.md) when you want the smallest correct reading path for:

1. frontend and product-surface work,
2. backend API and domain-service work,
3. cross-app integration and platform validation work,
4. standards, RFC, and governance work.

Use [Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md) when you need a human-readable view of:

1. application roles and categories,
2. domain authority ownership,
3. standards currently in force,
4. active RFCs that still materially govern the ecosystem.
