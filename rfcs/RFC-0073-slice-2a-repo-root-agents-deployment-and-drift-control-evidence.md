# RFC-0073 Slice 2A Evidence: Repo-root AGENTS Deployment and Drift Control

- RFC: `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`
- Date: `2026-04-18`
- Scope:
  - `lotus-platform`
  - `lotus-workbench`
  - `lotus-gateway`
  - `lotus-core`
  - `lotus-performance`
  - `lotus-risk`
  - `lotus-advise`
  - `lotus-manage`
  - `lotus-report`
  - `lotus-ai`
  - deployed `<codex-home>/AGENTS.md`

## What changed

Slice 2A closes the remaining gap from RFC-0073 Slice 2.

The governed operating contract now has three synchronized entrypoint forms:

1. canonical authored source in `lotus-platform/context/AGENTS-OPERATING-CONTRACT.md`,
2. repo-root `AGENTS.md` copies across the in-scope Lotus repositories,
3. the deployed local runtime copy at `<codex-home>/AGENTS.md`.

## Implementation outcomes

### Sync automation

`automation/Sync-AgentOperatingContract.ps1` now supports:

1. explicit target paths,
2. repo-root targeting by repository name,
3. all-repo-root rollout in one invocation,
4. optional inclusion of the deployed local runtime copy in the same invocation,
5. check-only verification for repo-root and deployed targets.

The rollout deliberately reuses this one script rather than adding a second AGENTS sync path.

### Drift visibility

Drift visibility now exists in two places:

1. `automation/validate_engineering_context_system.py`
   - verifies `lotus-platform/AGENTS.md`
   - verifies additional repo-root `AGENTS.md` copies when those repositories are present in the
     local workspace
2. `automation/Invoke-PlatformRepoChecks.ps1`
   - checks the deployed local `AGENTS.md`

This keeps CI realistic for the single-repo environment while avoiding duplicate platform-root
checks; the validator already owns repo-root verification when the repositories are present in a
normal Lotus workspace.

### Repo inventory synchronized

The following repo roots were synchronized from the governed contract in this slice:

1. `lotus-platform`
2. `lotus-workbench`
3. `lotus-gateway`
4. `lotus-core`
5. `lotus-performance`
6. `lotus-risk`
7. `lotus-advise`
8. `lotus-manage`
9. `lotus-report`
10. `lotus-ai`

## Review outcome

The mandatory slice review was completed before moving forward.

### Improvements made in the same slice

1. the sync logic stayed centralized in one script instead of being duplicated in validators or
   bootstrap scripts,
2. the validator now reasons over repo-root `AGENTS.md` synchronization using the existing
   manifest-backed repository inventory,
3. repo-root copies remain byte-for-byte synchronized with the governed source.

### Conscious no-change decisions

1. no repo-specific content was added to repo-root `AGENTS.md`,
2. `REPOSITORY-ENGINEERING-CONTEXT.md` remains the only repository-local truth surface,
3. onboarding and ramp-up guides were left unchanged because their routing posture did not need to
   change for this slice.

### Deferred opportunities

1. cross-repository CI verification for every repo-root `AGENTS.md` remains deferred because the
   current platform feature lane executes in a single-repo environment,
2. if Lotus later adds a workspace-wide governance runner, it should call the sync script in
   `-CheckOnly -AllRepoRoots` mode rather than introducing another validation path.
