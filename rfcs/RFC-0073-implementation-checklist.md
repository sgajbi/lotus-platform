# RFC-0073 Implementation Checklist

This checklist tracks delivery of RFC-0073, `Lotus Ecosystem Engineering Context and Agent Guidance System`.

Implementation posture: `Complete`

## Slice Status

- `Slice 1 | Central context architecture | Complete`
- `Slice 2 | AGENTS.md modernization | Complete`
- `Slice 2A | Repo-root AGENTS deployment and drift control | Complete`
- `Slice 3 | Repository-local context rollout | Complete`
- `Slice 3A | Repository-local context contract and platform pilot | Complete`
- `Slice 3B | Repository-local context rollout wave 1 (`lotus-workbench`, `lotus-gateway`, `lotus-core`) | Complete`
- `Slice 3C | Repository-local context rollout wave 2 (`lotus-performance`, `lotus-risk`, `lotus-advise`, `lotus-manage`, `lotus-report`, `lotus-ai`) | Complete`
- `Slice 4 | Reference map and task-routing hardening | Complete`
- `Slice 5 | Drift control and validation foundation | Complete`
- `Slice 6 | Skills, automation, and procedural memory alignment | Complete`

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

Conscious no-change boundary at the time:

1. Slice 2 synchronized the governed contract to the deployed local runtime copy,
2. it did not yet roll out repo-root `AGENTS.md` files across every Lotus repository.

### Slice 2A | Repo-root AGENTS deployment and drift control

Implemented:

1. add synchronized repo-root `AGENTS.md` to every Lotus repository,
2. extend `automation/Sync-AgentOperatingContract.ps1` so it can target repo roots as well as the
   deployed local runtime copy,
3. extend drift visibility so repo-root copies are checked in addition to `C:\Users\Sandeep\.codex\AGENTS.md`,
4. add or update contract tests for repo-root presence and synchronization.

Scope guardrails:

1. do not add repo-specific policy text to repo-root `AGENTS.md`,
2. keep repository-local truth in `REPOSITORY-ENGINEERING-CONTEXT.md`,
3. treat `lotus-platform/context/AGENTS-OPERATING-CONTRACT.md` as the only authored policy source,
4. record the exact in-scope repository inventory in the slice evidence,
5. do not move to the next implementation slice until Slice 2A has been reviewed for simplification,
   maintainability, drift risk, documentation follow-through, and meaningful test coverage.

Review outcome:

1. the rollout stayed on one synchronization path rather than introducing a second AGENTS copy
   mechanism,
2. repo-root drift is now visible through the platform validator when those repositories are present
   in the workspace and through explicit repo-root checks in `Invoke-PlatformRepoChecks.ps1` for
   `lotus-platform`,
3. no repo-specific policy was added to repo-root `AGENTS.md`; local truth remains in
   `REPOSITORY-ENGINEERING-CONTEXT.md`.

### Slice 3A | Repository-local context contract and platform pilot

Implemented:

1. `context/Repository-Engineering-Context-Contract.md`,
2. `context/templates/REPOSITORY-ENGINEERING-CONTEXT.template.md`,
3. `lotus-platform/REPOSITORY-ENGINEERING-CONTEXT.md` as the pilot implementation,
4. manifest and reference-map updates to show rollout state,
5. contract-test coverage for the template and pilot document.

### Slice 3B | Repository-local context rollout wave 1 (`lotus-workbench`, `lotus-gateway`, `lotus-core`)

Implemented:

1. maintenance-rule hardening in the repository-context contract and template,
2. `REPOSITORY-ENGINEERING-CONTEXT.md` in `lotus-workbench`,
3. `REPOSITORY-ENGINEERING-CONTEXT.md` in `lotus-gateway`,
4. `REPOSITORY-ENGINEERING-CONTEXT.md` in `lotus-core`,
5. manifest rollout-status updates for the wave-1 repositories.

### Slice 3C | Repository-local context rollout wave 2 (`lotus-performance`, `lotus-risk`, `lotus-advise`, `lotus-manage`, `lotus-report`, `lotus-ai`)

Implemented:

1. `REPOSITORY-ENGINEERING-CONTEXT.md` in `lotus-performance`,
2. `REPOSITORY-ENGINEERING-CONTEXT.md` in `lotus-risk`,
3. `REPOSITORY-ENGINEERING-CONTEXT.md` in `lotus-advise`,
4. `REPOSITORY-ENGINEERING-CONTEXT.md` in `lotus-manage`,
5. `REPOSITORY-ENGINEERING-CONTEXT.md` in `lotus-report`,
6. `REPOSITORY-ENGINEERING-CONTEXT.md` in `lotus-ai`,
7. README cross-links added for the wave-2 repositories,
8. manifest rollout-status updates for the remaining repositories.

### Slice 4 | Reference map and task-routing hardening

Implemented:

1. `context/TASK-ROUTING-GUIDE.md` as the task-first routing layer for frontend, backend, cross-app validation, and governance work,
2. `context/ECOSYSTEM-REGISTRIES.md` as the human-readable registry view generated from the governed manifest,
3. cross-link hardening in the quickstart, engineering context, context README, and reference map,
4. manifest enrichment so standards and active-RFC registries carry richer current-state truth,
5. documentation-contract coverage proving the routing docs, generated registries, and manifest stay aligned.

### Slice 5 | Drift control and validation foundation

Implemented:

1. `automation/validate_engineering_context_system.py` as the platform-owned validator for the RFC-0073 context contract,
2. `tests/unit/test_engineering_context_validator.py` for direct validator coverage,
3. feature-lane enforcement in `automation/Invoke-PlatformRepoChecks.ps1`,
4. `Sync-AgentOperatingContract.ps1 -CheckOnly` integration so deployed `AGENTS.md` drift is visible in the operational repo gate,
5. automation documentation updates so the context validator is discoverable and repeatable.

Follow-on completed by Slice 2A:

1. repo-root `AGENTS.md` drift visibility now exists through the context validator when the relevant
   repositories are present in the workspace.

### Slice 6 | Skills, automation, and procedural memory alignment

Implemented:

1. `context/PROCEDURAL-MEMORY-INDEX.md` as the entrypoint for governed playbooks,
2. governed playbooks for:
   - `context/playbooks/CHANGE-PLAYBOOKS.md`
   - `context/playbooks/PR-LOOP-PLAYBOOK.md`
   - `context/playbooks/VALIDATION-PLAYBOOK.md`
   - `context/playbooks/FIX-FORWARD-PATTERNS.md`
3. central context and reference-map updates so the procedural-memory layer is discoverable,
4. manifest enrichment so procedural memory is machine-readable and owned in the central context system,
5. local Lotus skill updates to align backend, frontend, PR, and validation workflows to the governed context system and playbooks,
6. validator and contract-test coverage so procedural memory stays linked and governed.
