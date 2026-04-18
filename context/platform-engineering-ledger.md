# Platform Engineering Ledger

This ledger records cross-repository engineering lessons, recurring quality patterns, and important ecosystem fixes that future sessions should treat as already-learned knowledge.

## How To Use This Ledger

Add entries when a change reveals:

1. a repeatable quality failure,
2. a recurring architectural cleanup theme,
3. a cross-repo delivery pattern that should influence future work,
4. a governance or validation lesson that should not remain trapped in chat history.

Keep entries concise and operational.

## Current Ledger Entries

### 2026-04-11 | Canonical local runtime must be treated as a governed operator flow

The local Lotus bring-up path only became repeatable once:

1. direct ingress, managed host mappings, and canonical service addresses were treated as one governed system,
2. startup and teardown were scripted rather than improvised,
3. seeded data validation was included as part of the runtime contract,
4. UI validation checked real screens and sub-screens rather than only health endpoints.

Implication:

Future runtime or demo work should use canonical automation and validation instead of hand-built service startup sequences.

### 2026-04-11 | Front-office product proof must route through the governed workbench runtime

The ecosystem already has a governed front-office runtime under `lotus-workbench` for:

1. seeded `PB_SG_GLOBAL_BAL_001` data,
2. canonical `*.dev.lotus` product routing,
3. populated Workbench surface validation,
4. demo and screenshot evidence capture.

Implication:

Future agent and operator guidance must route front-office bring-up, panel validation, and screenshot work to the governed `lotus-workbench` runtime instead of improvising from `lotus-platform/platform-stack`.

### 2026-04-11 | CI should use GitHub for heavy execution, not repeated expensive local reruns

RFC-0072 rollout work demonstrated that productivity improves when:

1. local checks are targeted and truthful,
2. GitHub Actions carries the expensive full matrix,
3. PRs are raised early,
4. failures are fixed forward from GitHub logs asynchronously.

Implication:

Future work should prefer targeted local proof plus GitHub-backed heavy execution rather than blocking on repeated full local reruns.

### 2026-04-11 | Platform standards become durable only when backed by scaffold and validators

Standards such as CI lane structure, workflow permissions, action baselines, repository hygiene, and container build rules were only durable once they were backed by:

1. scaffold templates,
2. validators,
3. documentation contract tests,
4. platform-owned repo checks.

Implication:

When a pattern matters ecosystem-wide, do not stop at prose. Promote it into executable truth where practical.

### 2026-04-18 | README and wiki quality improves when mixed API conventions are shown, not merely described

Cross-repo README and wiki rollout work showed that short prose warnings are not enough when a repo
still exposes mixed query names, compatibility aliases, or transitional request-body shapes.

The documentation became materially safer once:

1. the README stayed concise and delegated detailed examples into the repo-local `wiki/`,
2. the wiki remained the canonical authored source inside the main repository,
3. API-surface pages included copy-paste-ready examples for the currently supported parameter shapes,
4. repo-local engineering context explicitly called out this documentation requirement where it
   mattered.

Implication:

Future README/wiki work should add executable examples for mixed public contracts and keep that rule
in the platform documentation skill, not only in one repo.

### 2026-04-18 | Product-UI docs must separate active surfaces from legacy or capability-disabled routes

Workbench documentation tightening showed that route inventories can easily drift into historical
topology instead of current product truth.

The documentation became materially more truthful once:

1. active supported surfaces were stated explicitly,
2. compatibility redirects were called out as compatibility-only instead of live product ownership,
3. capability-disabled shell entries were not described as active routes simply because the labels
   still exist in the shell model,
4. canonical runtime examples used the governed seeded portfolio and validation output paths.

Implication:

Future README/wiki work for product UIs should document supported surfaces, compatibility routes,
disabled navigation entries, and canonical evidence paths separately.

### 2026-04-18 | Legacy Lotus wiki material should be mined by ownership boundary before reuse

Reviewing the older `lotus-core` wiki showed that legacy Lotus documentation can contain useful
business framing, market context, and platform rationale even when its repo ownership and technical
topology are outdated.

The documentation became safer once:

1. historical pages were treated as source material instead of as a direct structure template,
2. reusable ecosystem background was separated from current repo truth,
3. stale service-specific or legacy-naming material was not copied into platform-governance docs,
4. rewritten docs used current Lotus vocabulary, architecture, and ownership boundaries.

Implication:

Future README/wiki work should classify legacy material into current repo truth, ecosystem
background, migrated ownership, or retirement before reusing it.
