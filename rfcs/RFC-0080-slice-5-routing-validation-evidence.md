# RFC-0080 Slice 5 Evidence: Validation of Agent Routing Behavior

- RFC: `RFC-0080-lotus-agent-runtime-demo-skill-pack-and-guidance-hardening.md`
- Date: `2026-04-11`
- Scope:
  - `lotus-platform`

## What changed

Slice 5 adds an explicit routing-behavior contract test instead of relying only on documentation
review.

Artifacts added or updated:

1. `tests/unit/test_lotus_skill_routing_behavior_contract.py`
2. `rfcs/RFC-0080-implementation-checklist.md`
3. `rfcs/RFC-0080-slice-5-routing-validation-evidence.md`

## Validation outcomes

### New-agent routing proof

The routing-behavior contract now proves that a new agent can select the governed runtime path with
minimal ambiguity by asserting:

1. `LOTUS-SKILL-ROUTING-MAP.md` routes canonical populated Workbench and screenshot-proof tasks to
   `lotus-front-office-runtime`,
2. the AGENTS contract and ramp-up guide reinforce the same routing boundary,
3. the runtime-specific skill and the broader QA or delivery skills agree on that boundary.

### Async GitHub proof

The contract test proves that async GitHub behavior is represented in the relevant guidance:

1. `lotus-pr-premerge-gate`,
2. `lotus-qa-platform-validator`,
3. `lotus-validation-resolution-lifecycle`,
4. `LOTUS-AGENT-RAMP-UP.md`.

### Stale-pattern rejection proof

The contract test proves that older weak behaviors are no longer encouraged:

1. screenshot-only proof is explicitly rejected,
2. diagnostic screenshots are separated from demo evidence,
3. `lotus-platform/platform-stack` is not presented as the canonical populated front-office runtime.

## Why this slice is in the right shape

This slice adds executable protection instead of more narrative.

That is the right balance because:

1. the routing system is already documented,
2. the remaining risk is future drift, not lack of prose,
3. contract tests are the most durable way to guard agent-facing behavior.

## Verification

```text
python -m pytest tests\unit\test_rfc_0080_agent_runtime_guidance_contract.py tests\unit\test_lotus_skill_routing_behavior_contract.py tests\unit\test_engineering_context_system_contract.py -q
```

## Review outcome

Slice 5 is complete and does not need additional documentation changes before moving on.
