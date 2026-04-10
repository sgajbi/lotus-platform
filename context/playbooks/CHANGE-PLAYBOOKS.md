# Change Playbooks

Use these playbooks to choose the right implementation path for the task type.

## Backend API And Domain-Service Change Playbook

Use this when the primary change belongs in `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise`, `lotus-manage`, `lotus-report`, `lotus-ai`, or the API-composition layer in `lotus-gateway`.

Sequence:

1. read [Lotus Engineering Context](../LOTUS-ENGINEERING-CONTEXT.md)
2. read the owning repository `REPOSITORY-ENGINEERING-CONTEXT.md`
3. confirm domain authority before changing any contract
4. identify whether the change affects OpenAPI, vocabulary, migrations, runtime, or cross-app behavior
5. implement the smallest correct change in the authoritative layer
6. add or update meaningful unit, contract, and integration coverage
7. update repo-local docs and platform docs if implementation truth changed
8. run the smallest truthful local proof before pushing

Non-negotiables:

1. do not bury domain fixes in consumers
2. do not weaken governance checks to get green faster
3. prefer root-cause fixes over suppression or allowlist expansion unless the allowlist is the truthful state

## Frontend And Product-Surface Change Playbook

Use this when the primary change belongs in `lotus-workbench` or another Lotus UI surface.

Sequence:

1. read [Lotus Engineering Context](../LOTUS-ENGINEERING-CONTEXT.md)
2. read [Task Routing Guide](../TASK-ROUTING-GUIDE.md)
3. read `lotus-workbench/REPOSITORY-ENGINEERING-CONTEXT.md`
4. identify the backing gateway and upstream capability owners
5. confirm the UI behavior is genuinely supported by backend truth
6. implement the smallest clean UI change without page-local hacks
7. add or update meaningful component, route, and browser coverage
8. update docs when product behavior, route coverage, or operating assumptions change

Non-negotiables:

1. do not fake unsupported backend behavior in the UI
2. do not duplicate interpretation or figures where the product already shows them clearly
3. keep loading, empty, partial, ready, and error states explicit

## Cross-Repository Integration Change Playbook

Use this when the slice spans more than one repo or when a user-facing behavior crosses app boundaries.

Sequence:

1. read [Lotus Engineering Context](../LOTUS-ENGINEERING-CONTEXT.md)
2. read [Ecosystem Registries](../ECOSYSTEM-REGISTRIES.md)
3. confirm authoritative domain ownership and participating services
4. apply the change in the owning service first
5. update gateway or UI composition only where required
6. validate at the participating repo layer
7. run cross-app or platform validation when the flow is canonical or user-facing

## RFC-Driven Slice Playbook

Use this when a change is explicitly driven by an RFC rollout.

Sequence:

1. read the RFC and its implementation checklist
2. confirm which slice is active and which slices must remain untouched
3. review the previously completed slice for obvious drift or quality gaps before moving on
4. implement the current slice cleanly
5. update the checklist in the same change
6. add or extend contract tests and validators where the RFC introduces new governed artifacts
7. do not claim later slices are complete early
