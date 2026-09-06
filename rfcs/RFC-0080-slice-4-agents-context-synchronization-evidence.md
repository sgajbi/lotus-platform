# RFC-0080 Slice 4 Evidence: AGENTS and Context Synchronization

- RFC: `RFC-0080-lotus-agent-runtime-demo-skill-pack-and-guidance-hardening.md`
- Date: `2026-04-11`
- Scope:
  - `lotus-platform`
  - deployed `<codex-home>/AGENTS.md`

## What changed

Slice 4 synchronizes the new routing posture into the small set of documents that materially shape
future agent behavior:

1. `context/AGENTS-OPERATING-CONTRACT.md`
2. `context/LOTUS-ENGINEERING-CONTEXT.md`
3. `docs/onboarding/LOTUS-AGENT-RAMP-UP.md`
4. `<codex-home>/AGENTS.md`

## Synchronization outcomes

### AGENTS operating contract

The governed operating contract now:

1. points agents to `LOTUS-SKILL-ROUTING-MAP.md` before choosing between overlapping skills,
2. explicitly routes canonical populated Workbench and demo-proof tasks to
   `lotus-front-office-runtime`,
3. requires routing-map maintenance when platform-wide skill boundaries change,
4. cross-links the routing map alongside the rest of the central context system.

### Engineering context

The central engineering context now:

1. treats `lotus-front-office-runtime` as the preferred route for governed front-office runtime
   work,
2. lists the skill explicitly in the skill-selection section,
3. points future agents to `LOTUS-SKILL-ROUTING-MAP.md` when routing boundaries are ambiguous.

### Agent ramp-up guide

The ramp-up guide now:

1. includes the routing map in the governed reading set,
2. adds a first-turn routing check before loading broader skills,
3. lists `lotus-front-office-runtime` in the common skill routes,
4. states that front-office runtime tasks should use the runtime skill first and broader skills
   only as supporting guidance.

### Deployed AGENTS copy

The deployed `<codex-home>/AGENTS.md` copy was updated in the same slice so future
sessions pick up the new routing rule immediately instead of waiting for a later manual sync.

## Why this slice is in the right shape

This slice avoids broad doc churn.

It updates only the guidance surfaces that:

1. materially affect future session ramp-up,
2. materially affect skill routing behavior,
3. need a durable maintenance rule for routing drift.

It does not copy operational runbooks into AGENTS or onboarding docs; it cross-links to the
governed runtime path instead.

## Verification

```text
python -m pytest tests\unit\test_rfc_0080_agent_runtime_guidance_contract.py tests\unit\test_engineering_context_system_contract.py -q
```

## Review outcome

Slice 4 is complete and does not require broader documentation churn before moving on.

The conscious no-change decisions in this slice are:

1. leave `docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md` unchanged because it already covers async
   GitHub posture for developers and does not drive first-turn agent routing,
2. leave `context/CONTEXT-REFERENCE-MAP.md` unchanged because the new routing boundary is better
   represented in `LOTUS-SKILL-ROUTING-MAP.md` than in a broad index document.
