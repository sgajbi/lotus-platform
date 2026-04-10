# Validation Playbook

Use this playbook to choose the right validation depth for the change.

## Validation Layers

### Repository-Local Proof

Use when:

1. the change is local to one repo,
2. no canonical user-facing behavior changed,
3. cross-app composition did not move.

Typical proof:

1. lint
2. typecheck
3. targeted unit tests
4. targeted contract or integration tests

### PR Merge-Gate Proof

Use when:

1. the change is headed for merge,
2. GitHub already owns the repo’s expensive validation matrix,
3. browser, Docker, coverage, or full integration proof is required.

Typical proof:

1. local targeted proof first,
2. GitHub PR merge-gate checks for the heavy matrix,
3. fix-forward from GitHub logs if failures surface.

### Platform End-To-End Proof

Use when:

1. canonical routes or panels changed,
2. ingress, runtime, or seeded demo flows changed,
3. gateway and upstream payload alignment matters,
4. a demo-readiness or full-stack operator claim is being made.

Typical proof:

1. canonical stack bring-up
2. canonical DNS and ingress validation
3. seeded data checks
4. route, screen, sub-screen, and panel validation
5. cross-app payload consistency checks

## State-Handling Rule

Every UI or surfaced data module should be validated for:

1. loading
2. empty
3. partial
4. ready
5. error

## Artifact Rule

When the validation claim matters operationally, produce retained evidence such as:

1. GitHub check records
2. validation summary JSON or Markdown
3. browser artifacts or screenshots
4. QA summaries

## Escalation Rule

If a repo-local proof passes but the canonical flow is still at risk:

1. escalate to platform validation,
2. do not assume local green means ecosystem green.
