# Lotus Service Scaffold Lessons

This file records reusable scaffold lessons discovered while creating new Lotus
repositories. Promote repeated lessons into `New-Lotus-Service.ps1`,
`LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md`, and platform standards instead of
solving them only in the generated app.

## 2026-06-21 - lotus-idea

1. Large RFC programs should use a per-RFC folder under `docs/rfcs/` so the
   master RFC and slice evidence files stay together. The top-level RFC index
   should link into that folder.
2. Generated evidence templates must not contain sensitive-content marker strings
   that the generated no-sensitive-content guard rejects. Use business-safe
   wording such as `raw HTTP payload`.
3. Generated Starlette/FastAPI response tests should coerce `response.body` with
   `bytes(response.body)` before decoding so mypy handles the `bytes |
   memoryview[int]` type correctly.
4. New service repositories should distinguish foundation-supported behavior
   from planned business capability in README, wiki, demo claims, and
   supported-features from the first commit.
5. Generated runtime dependency pins must pass `pip-audit` on the first remote
   CI run. For the FastAPI scaffold, keep `fastapi`, `starlette`,
   `pydantic-settings`, and `prometheus-fastapi-instrumentator` as a compatible
   secure set rather than pinning one transitive dependency in isolation.
6. Generated tests must satisfy the configured 99 percent coverage gate without
   lowering the threshold. Scaffold coverage should prove service profile,
   product-safe errors, logging, downstream client failures, idempotency, audit,
   health, readiness, metadata, and correlation behavior.
7. Product-safe handlers for validation, framework HTTP exceptions, and
   unhandled exceptions belong in the scaffold from day one so raw entitlement
   or internal details cannot leak through default framework responses.
8. Platform registration must stay machine-readable. The scaffold should
   normalize comma-delimited dependency input into JSON arrays, register the new
   repository in AGENTS synchronization scope, and ensure any generated
   `*.dev.lotus` QA target has a matching hosts entry, Caddy route, platform
   compose service, and `.env.example` repo-path variable.
9. Scaffold dependency pins should track latest stable compatible releases, not
   stale known-good versions. A dependency refresh is acceptable only when a
   disposable generated service passes `make ci`, `pip-audit`, and warning
   promotion for known framework deprecations.
10. Scaffold workflow action majors should track the current platform-approved
    runtime baseline. When GitHub runner warnings identify deprecated Node
    runtimes, update live platform workflows, backend workflow templates,
    `Workflow-Action-Runtime-and-Version-Baseline.md`, and
    `automation/validate_workflow_action_runtime.py` in the same slice.
11. Release-evidence commands must be exercised against the latest stable
    tooling. For `cyclonedx-bom` 7.x, generate SBOM evidence with the
    `cyclonedx-py` console command from the generated virtual environment,
    not the removed `cyclonedx_py` Python module invocation.
12. CI logs should be warning-quiet where the repository owns the cause. Set
    workflow Git config so `actions/checkout` does not emit default-branch
    hints, and set `PIP_ROOT_USER_ACTION=ignore` in Docker build stages where
    controlled root installs are part of the image build contract. Coverage
    aggregation jobs that invoke the approved `actions/download-artifact@v8`
    baseline should set `NODE_OPTIONS=--no-deprecation` until the upstream
    action runtime no longer emits Node `Buffer()` deprecation noise.
13. Governed PR completion should be linear and non-squash. Scaffolded
    repositories should enable rebase merge, disable squash and merge-commit
    completion, require branch linear history, and queue auto-merge with
    `gh pr merge --auto --rebase` when `LOTUS_AUTOMERGE_TOKEN` is configured.
    When the token is absent, the auto-merge helper should warn and skip rather
    than leaving a red helper check; a human or release actor then performs the
    required rebase merge.
14. Scaffolded backend repositories need an anti-drift gate for the lane
    contract itself. `make ci-contract-gate` should run through `make lint` and
    fail if agent or scaffold changes remove required Makefile targets,
    least-privilege workflow permissions, approved workflow action majors,
    merge/releasability coverage, Docker validation, release evidence,
    endpoint-certification, supported-feature, security-audit, architecture, or
    OpenAPI controls.
15. Scaffolded backend repositories also need an implementation-truth gate from
    day one. `make implementation-truth-gate` should run through `make lint`
    and block unqualified current-state README/docs/wiki claims that imply demo
    readiness, production support, certification, live source ingestion,
    Gateway/Workbench support, or client-ready publication before supported
    feature evidence exists. It should also block stale scaffold-era demo
    underclaims once implementation and CI evidence prove a stronger current
    posture.
16. Scaffolded backend repositories also need a maintainability gate from day
    one. `make maintainability-gate` should run through `make lint` and block
    oversized source, test, and script files/functions before agent-authored
    bloat becomes normalized.
17. Scaffolded backend repositories also need a documentation contract gate from
    day one. `make documentation-contract-gate` should run through `make lint`
    and block deletion, thinning, missing anchors, or placeholder erosion in the
    README, repository context, standards, runbooks, quality, evidence, and wiki
    surfaces that future operators and implementation agents depend on.
18. Scaffolded backend repositories also need a quality scorecard truth gate
    from day one. `make quality-scorecard-gate` should run through `make lint`
    and block missing bank-buyable control rows, unsupported status vocabulary,
    missing evidence anchors, and stale scaffold-era scorecard underclaims once
    certified business endpoint evidence exists.
19. Certified business/operator endpoints should not be able to pass endpoint
    certification without supportability telemetry proof. The generated
    endpoint-certification gate should require bounded operation-event test
    evidence for endpoints marked `certified`, while health/readiness/metadata
    endpoints remain `baseline_certified`.
20. Scaffolded backend repositories also need a source-observability contract
    gate from day one. Generated app code should use the central observability
    module for route-template request diagnostics and must block raw `print()`,
    direct Python logging, or low-level `log_event` bypasses in `src/app`.
21. Scaffolded backend repositories also need an operation metric contract gate
    from day one. Generated observability code should define a bounded
    `*_operation_events_total` vocabulary, safe label set, and forbidden
    sensitive operation attribute keys before service-specific workflows add
    business-operation telemetry. This gate is telemetry hygiene only; it must
    not claim dashboards, alerts, data-mesh certification, or supported-feature
    promotion.
22. Scaffolded backend repositories should generate an AST-backed
    monetary-float guard, not a string-only search. The guard should block
    money-like `float` annotations, literals, return annotations, and
    conversions while allowing operational floats such as timeout seconds, and
    scaffold tests should execute both clean and failing generated-guard paths.
23. Scaffolded backend repositories should generate pass/fail unit tests for
    no-sensitive-content artifact guarding. A blocking artifact-leak guard is
    not enough by itself; the generated service should prove clean artifacts,
    forbidden marker detection, allowlisted documentation, and binary artifact
    handling from day one.
24. Scaffolded backend repositories should generate a real cleanup utility
    instead of an inline Makefile one-liner. `make clean` should call
    `python scripts/clean_generated_artifacts.py`, prune `.git`, `.venv`, and
    `node_modules`, remove only known cache/build/coverage artifacts, and be
    protected by `make ci-contract-gate` plus generated unit tests.
25. Scaffolded backend repositories should make focused validation efficient
    without bypassing repo-native targets. Generate `UNIT_TESTS`,
    `INTEGRATION_TESTS`, and `E2E_TESTS` Makefile variables so agents can run
    `make test-unit UNIT_TESTS=<path>` during fix-forward work while full-suite
    defaults remain intact for PR and CI evidence.
26. Scaffolded backend repositories should include a `src/app/runtime` package
    for process-local dependency composition once repositories, adapters,
    publishers, workers, or proof generators need runtime wiring. The generated
    architecture boundary gate should block `runtime` from importing API routes,
    HTTP DTOs, FastAPI, or Starlette so composition code does not drift into the
    presentation layer.
