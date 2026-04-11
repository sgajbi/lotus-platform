# RFC-0080 Slice 2 Evidence: New Front-Office Runtime Skill

- RFC: `RFC-0080-lotus-agent-runtime-demo-skill-pack-and-guidance-hardening.md`
- Date: `2026-04-11`
- Scope:
  - `lotus-platform`

## What changed

Slice 2 introduces the dedicated governed skill required by RFC-0080.

Artifacts added or updated:

1. `codex/skills/lotus-front-office-runtime/SKILL.md`
2. `codex/skills/lotus-front-office-runtime/agents/openai.yaml`
3. `codex/skills/lotus-skill-manifest.json`
4. `codex/skills/README.md`
5. `rfcs/RFC-0080-slice-2-front-office-runtime-skill-evidence.md`

## Design choices

### Skill boundary

The new skill is deliberately narrow.

It owns:

1. governed front-office runtime routing,
2. canonical populated-panel proof,
3. screenshot-plus-machine-readable evidence expectations.

It does not own:

1. generic backend QA,
2. PR merge workflow,
3. repo-local implementation governance,
4. product or service contracts.

Those boundaries stay with the existing Lotus skills.

### Source-of-truth posture

The skill routes to:

1. `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`
2. `lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1`
3. RFC-0076 and RFC-0077 contract artifacts

The skill does not duplicate full runbook content. It stays concise and directive.

### Evidence posture

The skill explicitly rejects screenshot-only success.

It requires:

1. screenshot artifacts,
2. `live-validation-summary.json`,
3. `SHOT-INDEX.md`,
4. truthful panel classifications.

That is the key routing-quality improvement of Slice 2.

## Cleanup and stale-guidance review

Slice 2 also removed stale wording from `codex/skills/README.md`.

The previous `Current Boundary` section still claimed that skill synchronization automation was not
implemented. That is no longer true after the RFC-0074 bootstrap work, so it was replaced with an
accurate runtime-boundary statement tied to the governed bootstrap scripts.

## Verification

```text
python -m pytest tests\unit\test_rfc_0080_agent_runtime_guidance_contract.py tests\unit\test_engineering_context_system_contract.py -q
```

The targeted assertions for Slice 2 confirm:

1. the new skill exists,
2. the manifest includes it,
3. the skill inventory remains governed and synchronized from `lotus-platform`.

## Review outcome

Slice 2 is complete and in the right shape.

The conscious decisions for this slice are:

1. add only one new skill,
2. keep the skill concise,
3. avoid broad edits to existing skills until Slice 3,
4. remove one clearly stale README statement because leaving it behind would create routing drift.
