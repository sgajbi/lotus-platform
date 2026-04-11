# RFC-0080 Implementation Checklist

- RFC: `RFC-0080-lotus-agent-runtime-demo-skill-pack-and-guidance-hardening.md`
- Status: In Progress
- Last updated: 2026-04-11

## Approval Gate

- [x] RFC reviewed and tightened before slice implementation.
- [x] Slice 1 scope constrained to skill inventory review, routing map, checklist, evidence, and platform tests.
- [ ] RFC approved for Slice 2 implementation.

## Slice 1: Skill Inventory Review and Routing Map

- [x] Review current Lotus skill inventory.
- [x] Identify add, keep, tighten, and remove/merge candidates.
- [x] Record routing precedence and governed source-of-truth paths.
- [x] Define trigger boundaries for front-office runtime vs platform QA vs delivery governance.
- [x] Add a durable routing-map artifact.
- [x] Add platform tests validating RFC-0080 structure and slice 1 posture.
- [x] Add slice evidence documenting the inventory review and routing decisions.
- [x] Review slice output for over-modeling before moving on.

## Slice 2: New Front-Office Runtime Skill

- [x] Add `lotus-front-office-runtime`.
- [x] Document trigger phrases and governed paths.
- [x] Keep the skill concise and directive.
- [x] Prove that the skill routes to validation-plus-evidence rather than screenshot-only success.
- [x] Review the skill for overlap with existing QA skills before moving on.

## Slice 3: Hardening Existing Skills

- [x] Tighten `lotus-qa-platform-validator`.
- [x] Tighten `lotus-pr-premerge-gate`.
- [x] Tighten `lotus-frontend-delivery-governance`.
- [x] Tighten `lotus-backend-delivery-governance`.
- [x] Tighten `lotus-validation-resolution-lifecycle` where routing overlap exists.
- [x] Remove stale wording and dead guidance that becomes obsolete.
- [x] Review inventory simplification opportunities before moving on.

## Slice 4: AGENTS and Context Synchronization

- [x] Update AGENTS guidance where the routing changes materially improve future sessions.
- [x] Update central context and onboarding docs where they should point to the governed runtime path.
- [x] Keep context concise and linked rather than duplicative.
- [x] Record conscious no-change decisions where updates are unnecessary.

## Slice 5: Validation of Agent Routing Behavior

- [x] Prove that a new agent can select the governed runtime path with minimal ambiguity.
- [x] Prove that async GitHub behavior is reflected in the updated skills.
- [x] Prove that stale startup or screenshot-only behaviors are no longer encouraged.
- [x] Add or update contract guards where they materially improve reliability.

## Slice 6: Documentation, Agent Context, Skill Alignment, and Branch Hygiene

- [x] Remove dead or obsolete skill content introduced or exposed by earlier slices.
- [x] Validate guidance consistency across skills, AGENTS, and central context.
- [x] Document conscious no-change decisions explicitly.
- [ ] Complete PR evidence hygiene and branch hygiene before closure.

## Final Acceptance

- [x] Lotus has a dedicated governed front-office runtime skill.
- [x] Overlapping Lotus skills route more cleanly and avoid ambiguity.
- [x] AGENTS and central context point to the governed runtime path and async GitHub posture.
- [x] Screenshot-only proof patterns are explicitly rejected.
- [ ] CI evidence is truthful and branch hygiene is complete.
