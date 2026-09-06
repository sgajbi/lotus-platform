# Task Routing Guide

Use this guide when you need to choose the smallest correct Lotus context set for a task.

This guide is intentionally task-first. Use it after the [Lotus Quickstart Context](./LOTUS-QUICKSTART-CONTEXT.md) and before opening low-signal documents that do not materially affect the task.

## Frontend And Product-Surface Work

Use this path for `lotus-workbench` UI, user journeys, product interaction quality, and browser-facing validation.

Start from the common startup set. The `lotus-workbench` repository context then names the
product contract, validation guide, and source boundaries needed for the surface. Add
[Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md) only when the change crosses a
repository boundary, and use the [Context Reference Map](./CONTEXT-REFERENCE-MAP.md) to locate a
specific cross-repository contract.

Then load only what the task needs:

1. `lotus-gateway/REPOSITORY-ENGINEERING-CONTEXT.md` when the UI change depends on gateway contract or composition behavior
2. RFC-0070 when product-surface ownership or presentation standards are the main concern
3. RFC-0072 and platform validation references when browser proof, CI posture, or full-stack validation is required

Operating rule:

1. UI features must be backed by supported gateway and backend capability
2. do not implement superficial UI-only behavior to mask missing domain support

## Backend API And Domain-Service Work

Use this path for service-side behavior, contracts, domain models, validation logic, and runtime-hardening work.

Start from the common startup set. The owning repository context is already part of that set. Add
[Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md) when ownership is unclear, and add
[Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md) only when the change crosses a
repository boundary or changes shared engineering policy.

Then load only what the task needs:

1. RFC-0067 and vocabulary-quality standards when the change affects API contracts or business-language modeling
2. RFC-0072 and repo-local CI expectations when delivery or merge-gate posture matters
3. upstream or downstream repo-local context documents only when the change crosses a domain boundary

Operating rule:

1. fix the authoritative service or governed composition layer, not the most convenient consumer

## Cross-App Integration And Platform Validation Work

Use this path for ingress, canonical runtime, seeded data, gateway aggregation, cross-app payload consistency, and demo-readiness validation.

Add these sources after the common startup set:

1. [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md) for cross-repository architecture
2. [Context Reference Map](./CONTEXT-REFERENCE-MAP.md)
3. [Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md)
4. [lotus-context-manifest.json](./lotus-context-manifest.json)

Then load only what the task needs:

1. RFC-0071 for ingress and canonical service-addressing governance
2. RFC-0072 for CI, validation-lane, and releasability posture
3. `lotus-platform/REPOSITORY-ENGINEERING-CONTEXT.md`
4. repo-local context documents for the participating services

Operating rule:

1. treat runtime validation as a governed operator flow, not ad hoc app-by-app debugging

## Standards, RFC, And Governance Work

Use this path for platform standards, rollout governance, RFC implementation, documentation-system work, and quality-contract changes.

Add these sources after the common startup set:

1. [Context Reference Map](./CONTEXT-REFERENCE-MAP.md) to locate the specific authority
2. [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md) when the change sets policy across repositories
3. [Platform Engineering Ledger](./platform-engineering-ledger.md)
4. [Recent Architectural Decisions Digest](./recent-architectural-decisions-digest.md)

Then load only what the task needs:

1. the specific RFC or standard being changed
2. [Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md) when ownership, domain authority, or active-RFC posture matters
3. repo-local context documents only where the change materially affects local implementation truth

Operating rule:

1. central context owns platform truth
2. repository context owns local truth
3. do not fork policy prose across both unless the local repository needs explicit interpretation

## README, Wiki, And Documentation Work

Use this path when the task is specifically about repository front-door docs, repo-local wiki
structure, documentation layering, or moving content cleanly between `README.md`, `wiki/`, deep
`docs/`, and platform `context/`.

Start from the common startup set, which already includes the target repository context and skill
routing map. Add [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
for document responsibilities and portability. Add
[Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md) only when documentation changes shared
architecture or policy across repositories.

Then load only what the task needs:

1. the target repo `README.md`
2. the target repo `wiki/` source when present
3. only the deeper `docs/` pages needed to keep the README and wiki truthful
4. the `lotus-readme-wiki-governance` skill when the task is about standardization or cross-repo consistency

Operating rule:

1. keep README concise and truthful
2. keep repo-local `wiki/` as the authored source when a GitHub wiki exists
3. run
   `lotus-platform/automation/Sync-RepoWikis.ps1 -CheckOnly -Repository <repo-name> -AllowUnpublishedSourceChanges`
   before merge when the branch intentionally changes wiki source, then publish with `-Publish`
   after merge and run strict `-CheckOnly` parity verification
4. keep deep technical truth in `docs/`
5. update `context/` only when the lesson becomes platform-wide guidance

## Async Execution And Heavy Validation Routing

When the task requires expensive CI, browser, or platform validation:

1. run only the smallest truthful local proof first
2. push early when GitHub or shared automation can execute the heavy matrix more efficiently
3. monitor checks asynchronously and fix forward from real failure logs

Use this model especially for:

1. full PR merge-gate validation
2. browser smoke and end-to-end validation
3. platform-wide runtime or cross-app validation
4. long-running Docker or dependency-health sweeps

## Escalation Rule

If you are unsure what to read next:

1. use the [Context Reference Map](./CONTEXT-REFERENCE-MAP.md) for narrative routing
2. use [Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md) for human-readable structured lookups
3. use [lotus-context-manifest.json](./lotus-context-manifest.json) for deterministic machine-readable routing
