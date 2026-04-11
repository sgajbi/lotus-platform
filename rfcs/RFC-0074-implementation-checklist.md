# RFC-0074 Implementation Checklist

This checklist tracks delivery of RFC-0074, `Repeatable Developer and Agent Bootstrap System`.

Implementation posture: `Complete`

## Slice Status

- `Slice 1 | Onboarding RFC approval and documentation skeleton | Complete`
- `Slice 2 | Developer onboarding guide | Complete`
- `Slice 3 | Agent ramp-up guide and first-prompt standard | Complete`
- `Slice 4 | Skill distribution and synchronization design | Complete`
- `Slice 5 | Bootstrap and validation automation | Complete`
- `Slice 6 | Validation coverage and drift control | Complete`
- `Slice 7 | Repository-local cross-link rollout | Complete`

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

Implemented:

1. established `codex/skills/` as the platform-owned source for Lotus skills,
2. added `codex/skills/lotus-skill-manifest.json` as the governed skill inventory,
3. copied and reviewed Lotus-owned skills and one required supporting GitHub issue-loop skill,
4. removed stale local-machine and legacy `pbwm-platform-docs` references from the governed skill copies,
5. documented source-of-truth ownership, unknown local skill preservation, and future sync states in `codex/skills/README.md`,
6. added contract-test coverage for the skill inventory and stale-reference guardrails.

Current source of truth:

1. the governed Lotus skill source directory is `codex/skills/`.
2. the governed skill inventory is `codex/skills/lotus-skill-manifest.json`.
3. Slice 5 is the next permitted implementation slice.

### Slice 5 | Bootstrap and validation automation

Implemented:

1. created `automation/Bootstrap-LotusDeveloperEnvironment.ps1`,
2. created `automation/Validate-LotusDeveloperEnvironment.ps1`,
3. added inspect, sync, and validate modes,
4. added fast, extended, and explicit platform validation profiles,
5. validate GitHub auth, Docker posture, Python, Node, repository presence, context docs, skill sync, `AGENTS.md` sync, ingress, and DSN posture,
6. emit redacted `output/developer-environment-readiness.json` and `.md` reports,
7. apply stable statuses and validate-mode exit semantics,
8. keep heavy stack and E2E validation opt-in,
9. documented the scripts in onboarding and automation references,
10. added contract-test coverage for the automation entrypoints and safety semantics.

Current source of truth:

1. run `automation/Validate-LotusDeveloperEnvironment.ps1 -Mode Inspect -Profile fast` for read-only readiness checks.
2. run `automation/Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast` to sync governed Lotus Codex skills and `AGENTS.md`.
3. Slice 6 is the next permitted implementation slice.

### Slice 6 | Validation coverage and drift control

Implemented:

1. added documentation and automation entrypoint drift tests for onboarding and bootstrap artifacts,
2. added executable script tests for readiness-report shape and redaction behavior,
3. added executable script tests for idempotency and scoped sync behavior,
4. extended `automation/validate_engineering_context_system.py` to include onboarding and bootstrap entrypoints,
5. hardened bootstrap PowerShell executable resolution for Windows and GitHub/Linux runner compatibility.

Current source of truth:

1. `tests/unit/test_developer_environment_bootstrap.py` covers report redaction, report structure, scoped sync, and idempotency.
2. `automation/validate_engineering_context_system.py` protects onboarding and bootstrap entrypoint drift.
3. Slice 7 is the next permitted implementation slice.

### Slice 7 | Repository-local cross-link rollout

Implemented:

1. updated repository-local context documents to link to the central onboarding guide,
2. added agent ramp-up cross-links beside developer onboarding,
3. kept repo-local docs focused on repository implementation truth and avoided duplicating the central onboarding procedure,
4. replaced machine-specific platform context and RFC references with sibling-relative `../lotus-platform/...` links in application repositories,
5. added platform-side contract coverage for RFC-0074 implemented posture and central repository onboarding links.

Final source of truth:

1. RFC-0074 is implemented and governed.
2. developer onboarding lives at `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`.
3. agent ramp-up lives at `docs/onboarding/LOTUS-AGENT-RAMP-UP.md`.
4. governed Lotus skills live at `codex/skills/`.
5. bootstrap validation emits `output/developer-environment-readiness.json` and `output/developer-environment-readiness.md`.
