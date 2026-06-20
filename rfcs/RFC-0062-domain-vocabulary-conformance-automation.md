# RFC-0062: Domain Vocabulary Conformance Automation

## Problem Statement

The platform has a canonical shared vocabulary in `docs/standards/Domain Vocabulary Glossary.md`, but there is no automated enforcement. Drift in naming (for example `portfolio_number` and `pas-snapshot`) increases ambiguity and weakens cross-service contract consistency.

## Decision

Introduce an automated cross-repository vocabulary conformance validator in `lotus-platform` and run it as a standard async/agent check.

Initial enforcement scope:

1. Flag prohibited shared terms:
   - `portfolio_number`
   - `portfolioNumber`
   - `pas-snapshot`
   - `pas_snapshot`
2. Report repository-level counts and sample occurrences.
3. Generate machine-readable and markdown outputs under `output/`.

## Scope

- Cross-cutting validation in `lotus-platform`.
- No runtime service behavior changes in this RFC increment.

## Out of Scope

- Immediate full rename/migration of all historical usages.
- Full semantic vocabulary linting for every domain term in one pass.

## Implementation

1. Add `automation/Validate-Domain-Vocabulary.ps1`.
2. Add async profile `domain-vocabulary-conformance`.
3. Add validator output into `Run-Agent.ps1` status loop.
4. Update runbook and automation docs.

## Risks and Trade-offs

- Pattern-based checks may initially flag legacy examples in docs/tests.
- Some findings may require staged migration RFCs across service repos.

Mitigation:
- Keep findings explicit with file/line samples.
- Triage findings via follow-up service-specific RFCs and PR waves.

## Acceptance Criteria

- One command generates platform-wide vocabulary conformance status.
- Agent loop includes domain vocabulary conformance signal.
- Output provides actionable per-repo findings.

