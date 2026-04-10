# RFC-0073 Implementation Checklist

This checklist tracks delivery of RFC-0073, `Lotus Ecosystem Engineering Context and Agent Guidance System`.

## Slice Status

- `Slice 1 | Central context architecture | Complete`
- `Slice 2 | AGENTS.md modernization | Complete`
- `Slice 3 | Repository-local context rollout | Pending`
- `Slice 3A | Repository-local context contract and platform pilot | Complete`
- `Slice 4 | Reference map and task-routing hardening | Pending`
- `Slice 5 | Drift control and validation foundation | Pending`
- `Slice 6 | Skills, automation, and procedural memory alignment | Pending`

## Slice Notes

### Slice 1 | Central context architecture

Implemented:

1. `context/LOTUS-QUICKSTART-CONTEXT.md`
2. `context/LOTUS-ENGINEERING-CONTEXT.md`
3. `context/CONTEXT-REFERENCE-MAP.md`
4. `context/lotus-context-manifest.json`
5. `context/platform-engineering-ledger.md`
6. `context/recent-architectural-decisions-digest.md`
7. a documentation contract test for central context presence and cross-linking

Current source of truth:

1. central ecosystem context is owned in `lotus-platform/context/`
2. repository-local context rollout is deferred to later slices

### Slice 2 | AGENTS.md modernization

Implemented:

1. `context/AGENTS-OPERATING-CONTRACT.md` as the governed source-of-truth operating contract,
2. cross-links from the central context system to the short-form contract,
3. deployed `AGENTS.md` synchronization from the governed source,
4. contract-test coverage for mandatory reading order, cross-links, and maintenance obligations
5. `automation/Sync-AgentOperatingContract.ps1` for repeatable synchronization and drift checks

### Slice 3A | Repository-local context contract and platform pilot

Implemented:

1. `context/Repository-Engineering-Context-Contract.md`,
2. `context/templates/REPOSITORY-ENGINEERING-CONTEXT.template.md`,
3. `lotus-platform/REPOSITORY-ENGINEERING-CONTEXT.md` as the pilot implementation,
4. manifest and reference-map updates to show rollout state,
5. contract-test coverage for the template and pilot document.
