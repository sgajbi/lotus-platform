# Lotus Context System

This directory contains the platform-owned central context system defined by [RFC-0073](../rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md).

## Reading Order

Use the files in this order:

1. [LOTUS-QUICKSTART-CONTEXT.md](./LOTUS-QUICKSTART-CONTEXT.md)
2. [LOTUS-ENGINEERING-CONTEXT.md](./LOTUS-ENGINEERING-CONTEXT.md)
3. the target repository's `REPOSITORY-ENGINEERING-CONTEXT.md`
4. [CONTEXT-REFERENCE-MAP.md](./CONTEXT-REFERENCE-MAP.md)
5. [AGENTS-OPERATING-CONTRACT.md](./AGENTS-OPERATING-CONTRACT.md) for the governed short-form agent contract

## Central Ownership

Platform-wide truth belongs here in `lotus-platform/context/`.

Repository-specific truth belongs in each repository's `REPOSITORY-ENGINEERING-CONTEXT.md`.

Do not duplicate full platform policy prose into repository-local docs unless local interpretation is required.

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
7. [AGENTS-OPERATING-CONTRACT.md](./AGENTS-OPERATING-CONTRACT.md)
   Source-of-truth content for the deployed global `AGENTS.md`.
8. [Repository-Engineering-Context-Contract.md](./Repository-Engineering-Context-Contract.md)
   Required section contract for repository-local engineering context documents.
9. [platform-engineering-ledger.md](./platform-engineering-ledger.md)
   Human-maintained engineering memory for recurring platform lessons.
10. [recent-architectural-decisions-digest.md](./recent-architectural-decisions-digest.md)
   High-signal summary of current architectural reality.

## Maintenance Rules

Update this directory when:

1. platform-wide architecture or ownership changes,
2. canonical runtime or validation flow changes,
3. cross-repository delivery expectations change,
4. important repeated patterns should become durable guidance,
5. the ecosystem inventory or authority model changes.

If a change is repository-local only, update the repository-local context document instead.

Use `automation/Sync-AgentOperatingContract.ps1` to synchronize the deployed global `AGENTS.md` from the governed source contract.
