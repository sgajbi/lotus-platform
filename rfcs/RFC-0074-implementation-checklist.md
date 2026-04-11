# RFC-0074 Implementation Checklist

This checklist tracks delivery of RFC-0074, `Repeatable Developer and Agent Bootstrap System`.

Implementation posture: `Approved | Slice 3 complete`

## Slice Status

- `Slice 1 | Onboarding RFC approval and documentation skeleton | Complete`
- `Slice 2 | Developer onboarding guide | Complete`
- `Slice 3 | Agent ramp-up guide and first-prompt standard | Complete`
- `Slice 4 | Skill distribution and synchronization design | Pending`
- `Slice 5 | Bootstrap and validation automation | Pending`
- `Slice 6 | Validation coverage and drift control | Pending`
- `Slice 7 | Repository-local cross-link rollout | Pending`

## Slice Notes

### Slice 1 | Onboarding RFC approval and documentation skeleton

Implemented:

1. reviewed and approved RFC-0074,
2. locked naming and target file locations,
3. approved source-of-truth boundaries and context-budget tiers,
4. approved readiness report contract and bootstrap safety rules,
5. avoid implementing bootstrap automation before approval.

Current source of truth:

1. RFC-0074 status is `Approved`.
2. implementation must proceed one slice at a time.
3. Slice 2 is the next permitted implementation slice.

### Slice 2 | Developer onboarding guide

Implemented:

1. created `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`,
2. covered prerequisites, repository layout, GitHub auth, Docker, ingress, DSN posture, skill sync, and validation depth,
3. classified prerequisites as required, required for full-stack validation, or optional,
4. separated fast local development from demo/full-stack validation,
5. linked to RFC-0071, RFC-0072, RFC-0073, RFC-0074, local development runbook, and central context docs,
6. linked the onboarding guide from the central context reference map,
7. added contract-test coverage for the Slice 2 onboarding guide.

Current source of truth:

1. the developer onboarding entrypoint is `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`.
2. Slice 3 is the next permitted implementation slice.

### Slice 3 | Agent ramp-up guide and first-prompt standard

Implemented:

1. created `docs/onboarding/LOTUS-AGENT-RAMP-UP.md`,
2. published path-specific and path-agnostic first-prompt templates,
3. defined small-context-first loading discipline,
4. defined Tier 1, Tier 2, and Tier 3 context-budget guidance,
5. added the first-turn checklist for repo, branch, standards, skills, validation lane, and context maintenance,
6. linked to the RFC-0073 context system and procedural memory,
7. linked the agent ramp-up guide from the central context reference map,
8. added contract-test coverage for the Slice 3 agent ramp-up guide.

Current source of truth:

1. the agent ramp-up entrypoint is `docs/onboarding/LOTUS-AGENT-RAMP-UP.md`.
2. Slice 4 is the next permitted implementation slice.

### Slice 4 | Skill distribution and synchronization design

Planned:

1. establish `codex/skills/` or approved equivalent as platform-owned source for Lotus skills,
2. add a skill manifest or equivalent inventory for Lotus-owned skills,
3. define safe synchronization into the local Codex skill directory,
4. preserve local non-Lotus skills,
5. report missing, stale, locally modified, and source-unavailable skill states,
6. document source-of-truth ownership and drift behavior.

### Slice 5 | Bootstrap and validation automation

Planned:

1. create `automation/Bootstrap-LotusDeveloperEnvironment.ps1`,
2. create `automation/Validate-LotusDeveloperEnvironment.ps1`,
3. support inspect, sync, and validate modes,
4. support fast, extended, and explicit platform validation profiles,
5. validate prerequisites and local readiness without printing secrets,
6. emit `output/developer-environment-readiness.json` and `.md`,
7. apply stable statuses and exit semantics,
8. keep heavy stack and E2E validation opt-in.

### Slice 6 | Validation coverage and drift control

Planned:

1. add documentation cross-link tests for onboarding entrypoints,
2. add script tests for readiness-report shape and redaction behavior,
3. add script tests for idempotency and scoped sync behavior,
4. extend context validators where appropriate.

### Slice 7 | Repository-local cross-link rollout

Planned:

1. update repository-local context documents to link to the central onboarding guide,
2. keep repo-local docs focused on local implementation truth,
3. avoid duplicating the central onboarding procedure across repositories.
