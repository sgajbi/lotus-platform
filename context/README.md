# Lotus Context System

This directory contains the platform-owned central context system defined by [RFC-0073](../rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md).

## Start Small

The repository's `AGENTS.md` is the mandatory operating entry. Then read:

1. [LOTUS-QUICKSTART-CONTEXT.md](./LOTUS-QUICKSTART-CONTEXT.md),
2. the target repository's `REPOSITORY-ENGINEERING-CONTEXT.md`,
3. [LOTUS-SKILL-ROUTING-MAP.md](./LOTUS-SKILL-ROUTING-MAP.md).

Use [TASK-ROUTING-GUIDE.md](./TASK-ROUTING-GUIDE.md) when ownership is unclear. Load engineering
context, reference maps, playbooks, RFCs, and standards only when the selected task route requires
them. The source copy of the shared `AGENTS.md` is
[AGENTS-OPERATING-CONTRACT.md](./AGENTS-OPERATING-CONTRACT.md).

## Central Ownership

Platform-wide truth belongs here in `lotus-platform/context/`.

Repository-specific truth belongs in each repository's `REPOSITORY-ENGINEERING-CONTEXT.md`.

Do not duplicate full platform policy prose into repository-local docs unless local interpretation is required.

For the split between repo `README.md`, repo-local `wiki/`, deep `docs/`, and platform `context/`,
use [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md).

## Contents

1. [LOTUS-QUICKSTART-CONTEXT.md](./LOTUS-QUICKSTART-CONTEXT.md)
   Fast orientation for a new session.
2. [LOTUS-ENGINEERING-CONTEXT.md](./LOTUS-ENGINEERING-CONTEXT.md)
   Canonical ecosystem engineering context.
3. [CONTEXT-REFERENCE-MAP.md](./CONTEXT-REFERENCE-MAP.md)
   Curated routing layer for standards, RFCs, runbooks, and repo docs.
4. [lotus-context-manifest.json](./lotus-context-manifest.json)
   Machine-readable ecosystem map and registry layer.
5. [TASK-ROUTING-GUIDE.md](./TASK-ROUTING-GUIDE.md)
   Task-first routing guide for loading the smallest correct working set.
6. [ECOSYSTEM-REGISTRIES.md](./ECOSYSTEM-REGISTRIES.md)
   Human-readable registry view generated from the manifest.
7. [PROCEDURAL-MEMORY-INDEX.md](./PROCEDURAL-MEMORY-INDEX.md)
   Governed playbooks for change execution, PR loops, validation, fix-forward patterns, agent context preservation, and detached task ledgers.
8. [AGENTS-OPERATING-CONTRACT.md](./AGENTS-OPERATING-CONTRACT.md)
   Source-of-truth content for the deployed global `AGENTS.md`.
9. [Repository-Engineering-Context-Contract.md](./Repository-Engineering-Context-Contract.md)
   Required section contract for repository-local engineering context documents.
10. [platform-engineering-ledger.md](./platform-engineering-ledger.md)
   Human-maintained engineering memory for recurring platform lessons.
11. [recent-architectural-decisions-digest.md](./recent-architectural-decisions-digest.md)
   High-signal summary of current architectural reality.
12. [Enterprise Backend Refactoring Instructions](./playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md)
   Execution pack for enterprise backend refactors; `lotus-platform` uses it with the measured
   quality artifacts under `../quality/`.
13. [Agentic Coding Quality Evaluation Loop](./playbooks/AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md)
   Procedural loop for converting repeated agent-authored code, test, documentation, and CI
   failures into deterministic gates, scorecards, evaluator cases, skills, and context updates.

## Maintenance Rules

Update this directory when:

1. platform-wide architecture or ownership changes,
2. canonical runtime or validation flow changes,
3. cross-repository delivery expectations change,
4. important repeated patterns should become durable guidance,
5. the ecosystem inventory or authority model changes.
6. enterprise refactor quality gates, scorecards, repo organization, or agent workflow expectations
   change.
7. repeated agent-authored quality failures should become durable gates, evaluator cases, skills, or
   context guidance.

If a change is repository-local only, update the repository-local context document instead.

Use `automation/Sync-AgentOperatingContract.ps1` to synchronize the deployed global `AGENTS.md` from the governed source contract.
