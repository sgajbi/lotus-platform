---
name: lotus-methodology-doc-v3
description: Upgrade risk/performance/analytics methodology documents to a strict v3 standard with explicit variable dictionary, formulas, deterministic computation steps, validation and failure behavior, and tabular worked examples. Use when editing metric methodology docs in Lotus apps (for example `docs/methodologies/metrics/*.md`), when users say documentation is unclear or not auditable, or when standardizing methodology writeups across repositories.
---

# Lotus Methodology Doc V3

## Overview
Use this skill to make methodology docs precise, auditable, and implementation-aligned across Lotus repositories.

## Workflow
1. Identify scope.
- Prefer one-metric-at-a-time unless user asks for batch rewrite.
- Target files under `docs/methodologies/metrics/*.md`.
2. Read implementation first.
- Inspect the engine/service code that computes the metric.
- Extract exact behavior (units, transformations, error handling, edge cases).
3. Rewrite the metric doc to v3 structure.
- Follow the required section order in `references/v3-template.md`.
- Use concrete formulas with symbols matching code behavior.
- Include deterministic algorithm steps.
- Include validation and failure behavior from actual code/contracts.
- Include tabular worked example with intermediate values.
4. Run quality gate.
- Apply checklist from `references/review-checklist.md`.
- Ensure no generic placeholder wording remains.
5. Report clearly.
- State file changed.
- State what was improved.
- Ask whether to continue with next metric.

## Hard Rules
- Do not invent formulas not used by implementation.
- Do not mix units silently; state pp vs decimal explicitly.
- Do not omit edge cases (insufficient data, zero denominator, alignment empty).
- Keep naming aligned with API payload fields and domain vocabulary.
- Prefer short precise language over narrative prose.

## References
- Template: `references/v3-template.md`
- Quality checklist: `references/review-checklist.md`
