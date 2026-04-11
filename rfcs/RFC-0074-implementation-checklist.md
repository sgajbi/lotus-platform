# RFC-0074 Implementation Checklist

This checklist tracks delivery of RFC-0074, `Repeatable Developer and Agent Bootstrap System`.

Implementation posture: `Draft pending approval`

## Slice Status

- `Slice 1 | Onboarding RFC approval and documentation skeleton | Draft`
- `Slice 2 | Developer onboarding guide | Pending`
- `Slice 3 | Agent ramp-up guide and first-prompt standard | Pending`
- `Slice 4 | Skill distribution and synchronization design | Pending`
- `Slice 5 | Bootstrap and validation automation | Pending`
- `Slice 6 | Validation coverage and drift control | Pending`
- `Slice 7 | Repository-local cross-link rollout | Pending`

## Slice Notes

### Slice 1 | Onboarding RFC approval and documentation skeleton

Planned:

1. review and approve RFC-0074,
2. lock naming and target file locations,
3. avoid implementing bootstrap automation before approval.

### Slice 2 | Developer onboarding guide

Planned:

1. create `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`,
2. cover prerequisites, repository layout, GitHub auth, Docker, ingress, DSN posture, skill sync, and validation depth,
3. link to RFC-0071, RFC-0072, RFC-0073, local development runbook, and central context docs.

### Slice 3 | Agent ramp-up guide and first-prompt standard

Planned:

1. create `docs/onboarding/LOTUS-AGENT-RAMP-UP.md`,
2. publish path-specific and path-agnostic first-prompt templates,
3. define small-context-first loading discipline,
4. link to the RFC-0073 context system and procedural memory.

### Slice 4 | Skill distribution and synchronization design

Planned:

1. establish `codex/skills/` or approved equivalent as platform-owned source for Lotus skills,
2. define safe synchronization into the local Codex skill directory,
3. document source-of-truth ownership and drift behavior.

### Slice 5 | Bootstrap and validation automation

Planned:

1. create `automation/Bootstrap-LotusDeveloperEnvironment.ps1`,
2. create `automation/Validate-LotusDeveloperEnvironment.ps1`,
3. support inspect, sync, and validate modes,
4. validate prerequisites and local readiness without printing secrets,
5. keep heavy stack and E2E validation opt-in.

### Slice 6 | Validation coverage and drift control

Planned:

1. add documentation cross-link tests for onboarding entrypoints,
2. add script tests for readiness-report shape and redaction behavior,
3. extend context validators where appropriate.

### Slice 7 | Repository-local cross-link rollout

Planned:

1. update repository-local context documents to link to the central onboarding guide,
2. keep repo-local docs focused on local implementation truth,
3. avoid duplicating the central onboarding procedure across repositories.
