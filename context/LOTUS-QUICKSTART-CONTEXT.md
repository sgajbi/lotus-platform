# Lotus Quickstart Context

This is the fastest safe orientation layer for a new Lotus engineering session.

After this file, read the target repository's `REPOSITORY-ENGINEERING-CONTEXT.md` and the
[Lotus Skill Routing Map](./LOTUS-SKILL-ROUTING-MAP.md). That is the default startup set together
with the repository's mandatory `AGENTS.md`.

Use the [Task Routing Guide](./TASK-ROUTING-GUIDE.md) when the correct owner or deeper context is
unclear. Load [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md), the
[Context Reference Map](./CONTEXT-REFERENCE-MAP.md), or the
[Procedural Memory Index](./PROCEDURAL-MEMORY-INDEX.md) only when the task needs cross-repository
architecture, a specialist source, or execution guidance.

## What Lotus Is

Lotus is a private banking and portfolio management ecosystem built as a platform of governed services, shared standards, and a unified product experience.

It supports workflows across:

1. portfolio onboarding and management,
2. performance analytics,
3. risk analytics,
4. advisory and proposal generation,
5. reporting and evidence delivery,
6. platform validation, ingress, and environment operations.

Lotus is being built to banking-grade expectations. Engineering quality, domain correctness, reliability, and operational discipline are part of the product.

## Ecosystem At A Glance

The core application and service landscape is:

1. `lotus-workbench`
   The primary product UI for portfolio, performance, risk, advisory, and evidence workflows.
2. `lotus-gateway`
   The experience API and integration boundary consumed by the UI.
3. `lotus-core`
   The authoritative system for portfolio, booking, transaction, and portfolio-management domain data.
4. `lotus-performance`
   The authoritative service for performance and analytics metrics and related review data.
5. `lotus-risk`
   The authoritative service for risk, drawdown, attribution, and concentration analytics.
6. `lotus-advise`
   The advisory workflow service for portfolio recommendation and related decision-support flows.
7. `lotus-manage`
   The discretionary mandate portfolio-management execution and operational supportability service.
8. `lotus-report`
   The reporting and document-generation service.
9. `lotus-render`
   The deterministic document rendering service for governed reporting artifacts.
10. `lotus-archive`
   The generated-document archive, retrieval, retention, legal hold, and access-audit service.
11. `lotus-idea`
   The wealth opportunity intelligence, idea lifecycle, governed idea evidence, and conversion
   orchestration service.
12. `lotus-ai`
   The shared AI capability service for governed AI-backed features.
13. `lotus-platform`
    The owner of shared standards, automation, ingress, validation, CI governance, and ecosystem runbooks.

## Architecture In One Pass

The standard product path is:

1. users work in `lotus-workbench`,
2. the UI talks to `lotus-gateway`,
3. `lotus-gateway` aggregates or routes to domain-authoritative services,
4. domain services remain authoritative for their business area,
5. `lotus-platform` owns the environment, validation, and governance system around them.

Core operating rules:

1. UI features must be genuinely backed by supported backend functionality.
2. `lotus-workbench` should consume `lotus-gateway`, not direct raw service contracts.
3. domain ownership must stay clear; avoid wrong-layer fixes.
4. standards, runbooks, validators, and repo-native commands are part of the implementation contract.

## How Work Should Be Approached

Lotus work should be executed with this posture:

1. reduce complexity rather than add local hacks,
2. improve readability, modularity, and maintainability as part of every slice,
3. make tests more meaningful, not merely more numerous,
4. update documentation when platform truth or repo truth changes,
5. remove dead code, duplicated logic, and stale patterns,
6. prefer reusable patterns, standards, and validators over repeated ad hoc fixes,
7. keep commits small, meaningful, and truthful,
8. treat performance, latency, observability, and production readiness as first-class quality concerns.

## Gold-Standard Delivery Expectations

A Lotus change is not complete unless it is:

1. architecturally truthful,
2. domain-correct,
3. backed by meaningful tests,
4. documented where behavior or standards changed,
5. cleaner than the prior state,
6. validated through the relevant repo-native and platform-native gates.

## Reading Paths By Task

Every route below starts from the same startup set stated at the top of this
file, and names only what its task adds to it. Nothing here restates that set:
one section defines it so the routes cannot drift away from it again.

1. UI or product-surface work
   Add the `lotus-workbench` repository context, then the gateway and platform
   validation references that context names. Only if the change crosses a
   repository boundary, read
   [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md).
2. Backend API or domain-service work
   Add the standards and contract governance documents that the
   [Context Reference Map](./CONTEXT-REFERENCE-MAP.md) lists for the contract
   being changed. Only when the change crosses a repository boundary or changes
   shared engineering policy, read the
   [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md). Use the
   [Task Routing Guide](./TASK-ROUTING-GUIDE.md) when the owner is unclear.
3. Cross-app integration or validation work
   This is the case the broad context exists for: read
   [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md) for the
   cross-repository architecture, then the
   [Context Reference Map](./CONTEXT-REFERENCE-MAP.md) for the platform
   validation and runbook material the integration touches.
4. RFC, standards, or governance work
   Add the [Context Reference Map](./CONTEXT-REFERENCE-MAP.md) to locate the RFC
   or standard. When the change sets policy across repositories rather than
   inside one, read
   [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md).

## Human-Maintained Memory

The central memory layer for Lotus lives in:

1. [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md)
2. [Platform Engineering Ledger](./platform-engineering-ledger.md)
3. [Recent Architectural Decisions Digest](./recent-architectural-decisions-digest.md)

These files exist so important operating knowledge is not trapped in prior chats.

## Structured Reusable Context

The machine-readable context layer lives in:

1. [lotus-context-manifest.json](./lotus-context-manifest.json)

Use it when you need deterministic ecosystem inventory, repository roles, or canonical context paths.

The human-readable registry companion lives in:

1. [Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md)

The governed procedural-memory layer lives in:

1. [Procedural Memory Index](./PROCEDURAL-MEMORY-INDEX.md)

## Next Read

Work through the startup set named at the top of this file: the target
repository's `REPOSITORY-ENGINEERING-CONTEXT.md`, then the task's skill in the
[Lotus Skill Routing Map](./LOTUS-SKILL-ROUTING-MAP.md).

Then follow only the task-specific links those two sources identify, using the
route above that matches the work. Load
[Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md),
the [Context Reference Map](./CONTEXT-REFERENCE-MAP.md), the
[Task Routing Guide](./TASK-ROUTING-GUIDE.md), or the
[Procedural Memory Index](./PROCEDURAL-MEMORY-INDEX.md) when the route calls for
it, and not before.

