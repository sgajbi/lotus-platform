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
    controlled root installs are part of the image build contract.
13. Governed PR completion should be linear and non-squash. Scaffolded
    repositories should enable rebase merge, disable squash and merge-commit
    completion, require branch linear history, and queue auto-merge with
    `gh pr merge --auto --rebase`.
