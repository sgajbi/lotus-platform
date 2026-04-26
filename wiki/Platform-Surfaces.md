# Platform Surfaces

## Purpose

This page explains which major `lotus-platform` surface owns which kind of work.

Use it to avoid putting the right content or logic in the wrong place.

## Ownership map

### `automation/`

Use when the work is about:

- repo checks
- platform validation
- PR loops and background runs
- ingress diagnostics
- QA entrypoints
- cross-app validation wrappers

### `context/`

Use when the work is about:

- central engineering context
- reading order and routing guidance
- registries and manifests
- playbooks and procedural memory
- governed operating contract content

### `platform-standards/`

Use when the work is about:

- reusable standards
- scaffold templates
- workflow baselines
- backend repo convergence expectations

### `platform-stack/`

Use when the work is about:

- shared local ingress
- shared local infrastructure support
- observability support surfaces
- environment-scoped service routing
- production-like local persistence wiring for services in the shared stack, such as
  `lotus-report-postgres` for `lotus-report` report-job and batch ledger readiness

Do not use it as the canonical populated front-office proof path when `lotus-workbench` already
owns that runtime.

### `codex/skills/`

Use when the work is about:

- Lotus-specific skills
- governed skill distribution
- durable guidance for recurring agent workflows

### `rfcs/`

Use when the work is about:

- architectural and governance decisions
- implementation posture for major cross-repo changes
- slice-by-slice platform rollout evidence

## Fast routing rules

- cross-repo operator workflow:
  start in `automation/`
- context or agent guidance:
  start in `context/`
- reusable rule or template:
  start in `platform-standards/`
- local ingress or shared environment support:
  start in `platform-stack/`
- recurring agent workflow:
  start in `codex/skills/`
- major governance decision:
  start in `rfcs/`

## Related pages

- [Architecture](Architecture)
- [Operations Runbook](Operations-Runbook)
- [Troubleshooting](Troubleshooting)
