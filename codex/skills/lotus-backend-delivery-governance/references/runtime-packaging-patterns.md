# Runtime Packaging Patterns

Use this reference when Docker/runtime behavior, package metadata, Compose mounts, service app
imports, worker entrypoints, migration assets, or image file closure are in scope.

## Contents

1. Service package import truth
2. App-owned Compose stacks
3. Distribution consolidation
4. Runtime asset closure

## Service Package Import Truth

When Docker/runtime behavior, package metadata, compose mounts, or service app imports are in
scope, verify package import truth before relying on repo-root tests. Code inside a deployable
service app package must not import its own app through a repo-root path such as
`src.services.<same_service>.app...`; prefer relative imports for same-service modules, shared
libraries or ports for durable cross-service contracts, and a focused runtime proof such as
`PYTHONPATH="src/services/<service>:src/libs/portfolio-common" python -c "import app.main"` in a
POSIX shell, or
`$env:PYTHONPATH = "src/services/<service>;src/libs/portfolio-common"; python -c "import app.main"`
in PowerShell, for the affected service.

## App-Owned Compose Stacks

When an application owns an app-local Compose stack, keep it independently operable instead of
requiring Workbench or platform orchestration to supply missing persistence or migration behavior.
For a database-backed service, prove the app-owned stack starts the database, waits for health,
runs one bounded migration job to successful completion, starts API and worker roles against the
same explicit durable URL, and survives both a repeated Compose start and an API-container restart
without data loss or migration replay. Keep in-memory adapters limited to explicit test or
ephemeral developer paths. Validate the actual major-version image, not only YAML: official image
volume layout, initialization, health commands, and upgrade posture can change across PostgreSQL
majors. Local migration convenience must still be pending-only, transactionally fenced, and
checksum-drift aware; it must not weaken or impersonate release-attested staging/production
migration evidence.

## Distribution Consolidation

Before consolidating Python services into one deployable, inspect each distribution's wheel
contents and declared top-level packages. Do not co-install distributions that expose overlapping
namespaces such as `core`, `consumers`, or `repositories`: installation order can silently replace
modules. Prefer one target distribution with durable shared libraries or a bounded transitional
source closure; do not copy the repository's entire source tree to make imports pass. Prove the
installed image imports the target entrypoint and expected modules, excludes unrelated services,
and add a deterministic package/image contract test for the closure.

## Runtime Asset Closure

When Compose declares a worker, manifest, migration, schema, or operator asset that the image
must read, verify the complete image file closure: every Dockerfile `COPY`, every `.dockerignore`
exception, and every imported helper script required by the entrypoint must be present in the
build context and in the built image. Repository tests are not enough for this check. Build the
affected image and run the real entrypoint's bounded `--check-only` or equivalent contract mode
inside the image before accepting runtime evidence; add a deterministic repository gate for the
closure when the asset is production or canonical-stack relevant.
