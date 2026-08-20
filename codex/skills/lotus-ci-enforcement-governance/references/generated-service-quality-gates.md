# Generated Service Quality Gates

Use this reference when changing `automation/New-Lotus-Service.ps1`, generated backend service
Makefiles, generated GitHub workflows, generated contract gates, or scaffolded quality packs.

## Contents

1. CI contract gate defaults
2. Endpoint example parity
3. Seven-gate quality pack
4. Runtime composition boundary
5. Cleanup utility contract
6. Suite target overrides

## CI Contract Gate Defaults

For newly scaffolded backend services, treat `make ci-contract-gate` as the default anti-drift
gate. It should remain blocking through `make lint` when it is worktree-clean and validates only
concrete lane wiring: required Makefile targets, approved workflow action majors, least-privilege
workflow permissions, 99% merge/releasability coverage, Docker validation, release evidence,
endpoint-certification, supported-feature, implementation-truth, security-audit, architecture/
OpenAPI gates, safe generated-artifact cleanup wiring, bounded job-level timeouts, and no
`continue-on-error: true` in critical lanes.

Rebase auto-merge must use a non-`GITHUB_TOKEN` merge actor such as `LOTUS_AUTOMERGE_TOKEN`;
otherwise GitHub suppresses the `pull_request_target.closed` event that dispatches post-merge main
releasability proof. The generated CI contract gate should enforce the token reference, explicit
missing-token warning-and-skip behavior, bounded workflow timeouts, no-soft-fail critical workflow
posture, implementation-truth guard presence, safe `make clean` delegation to
`scripts/clean_generated_artifacts.py`, scoped test-target variables (`UNIT_TESTS`,
`INTEGRATION_TESTS`, and `E2E_TESTS`) for repo-native focused validation, and the merged-PR
main-releasability dispatcher together. Missing `LOTUS_AUTOMERGE_TOKEN` must not create a permanent
red helper check; it should skip automatic rebase merge and require an authorized human or release
actor to merge.

Merged-PR main releasability dispatchers must validate shell execution semantics, not only YAML
substring presence. Immutable dispatch-ref creation must run synchronously in the foreground, must
not be failure-masked with fallback operators such as `|| true`, must not append shell chaining or
control flow such as `; exit 0` or `&& ...`, must reject non-POST `gh api` method overrides such as
`--method GET` or `-XGET`, must reject input-body overrides such as `--input`, and must bind exact
`ref` and `sha` payload fields to the same
`gh api repos/$GITHUB_REPOSITORY/git/refs` command that creates the tag. Explicit POST overrides
such as `--method POST`, `--method=POST`, `-X POST`, and `-XPOST` are acceptable because they
preserve the required ref-creation method. The existing-ref lookup guard must be recognized only
when it is on an executed path before creation; a canonical guard hidden in an uninvoked function or
otherwise unreachable construct is not protection, while executed `if` bodies and shell command
groups can remain valid when the validator can prove they run before creation. The looked-up
`existing_ref_sha` value must flow directly into the mismatch comparison without an intervening
top-level reassignment, and the absent-ref branch must contain exactly one guarded immutable-ref
creation invocation so redeliveries cannot skip collision detection or fail before dispatch. The
`main-releasability.yml` dispatch command must run only after the absent-ref creation branch has
completed, must be a real outer-shell-scope command rather than an unreachable or nested guard, must
not be failure-masked, backgrounded, or chained, and must bind both `--ref "$dispatch_ref"` and exact
`-f expected_sha="$MERGE_COMMIT_SHA"` arguments so downstream exact-main validation cannot be skipped,
emptied, or redirected to another revision. The immutable `dispatch_ref` value must not be reassigned
between its merge-SHA initialization and the dispatch command. Contract-gate tests should include
negative cases for
split run steps, commented payload fields, separated payload-field echoes, masked creation failure,
backgrounded creation, chained creation commands, duplicate guarded creation commands, lookup-SHA
mutation before mismatch comparison, non-POST creation overrides, input-body overrides, dispatch
before absent-ref creation, masked dispatch failure, nested dispatch commands, wrong or empty
`expected_sha` dispatch arguments, dispatch-ref reassignment before workflow dispatch, and
unreachable/function-scoped lookup guards before promoting the workflow as release-evidence ready.

GitHub workflows should call the repo-native targets that developers and agents run locally. For
generated backend services, Feature Lane should use `make test-unit`, PR/Main suite matrices should
use `make test-${{ matrix.suite }}-coverage`, and `make ci-contract-gate` should fail if an agent
reintroduces raw workflow-level `./.venv/bin/python -m pytest` commands or bypasses suite coverage
targets.

## Endpoint Example Parity

Generated endpoint-certification gates should require certified business/operator endpoints to cite
bounded operation-event test evidence in the endpoint ledger. Baseline health/metadata endpoints
can remain `baseline_certified` without operation-event evidence, but once an endpoint is marked
`certified`, API contract evidence and supportability telemetry proof must move together.

The same gate should parse and structurally compare every `baseline_certified` or `certified`
success example with a source-safe route invocation or deterministic code-owned callable. Fail
missing/stale fields, alias drift, blocker drift, scalar-type drift, and value drift. Dynamic
values must use an explicit RFC 6901 pointer plus an approved narrow normalizer; governance fields
remain exact. Keep the comparator with scaffold automation and add behavioral mutation tests so a
stale but parseable example cannot pass.

The canonical comparator source is `scripts/endpoint_example_parity.py`; keep changes to comparison
semantics, the machine-readable platform contract, scaffold copying, and focused comparator tests in
the same delivery slice.

## Seven-Gate Quality Pack

New backend scaffolds should generate and run this seven-gate quality pack through `make lint`:
`make maintainability-gate`, `make documentation-contract-gate`, `make quality-scorecard-gate`,
`make monetary-float-guard`, `make source-observability-contract-gate`,
`make operation-metric-contract-gate`, and `make implementation-truth-gate`.

The maintainability gate should block oversized source, test, and script files/functions against
conservative thresholds calibrated above the initial scaffold baseline. The documentation contract
gate should scan required README, repository context, standards, runbooks, quality, evidence, and
wiki surfaces for presence, minimum substance, required operating anchors, and placeholder erosion.
The quality-scorecard gate should scan the bank-buyable control matrix for required rows, approved
readiness statuses, non-empty evidence/gap/next-slice cells, implementation-backed evidence
anchors, and stale scaffold-era scorecard underclaims once certified business endpoints exist.

The monetary-float guard should be AST-backed and block money-like `float` annotations, literals,
return annotations, and conversions while allowing non-monetary operational floats such as timeout
seconds. The source-observability contract gate should block raw `print()`, direct Python logging,
and low-level `log_event` bypasses in `src/app` so generated and agent-authored feature code uses
central observability helpers and route-template request diagnostics.

The operation metric contract gate should block sensitive or unbounded operation metric names,
labels, and attributes so future business-operation telemetry starts source-safe before dashboards,
alerts, or supported-feature claims exist. The implementation-truth gate should scan current-state
README, repository context, operations/demo docs, quality docs, and wiki source for unqualified
claims of demo readiness, production support, certification, live source ingestion, Gateway/
Workbench support, or client-ready publication before supported-feature evidence exists. It should
also block stale scaffold-era demo underclaims after implementation and CI evidence prove a stronger
current posture. Keep RFC target-state planning text out of this blocking scan.

## Runtime Composition Boundary

The generated architecture boundary gate should also protect `src/app/runtime` as the process-local
composition layer for repositories, adapters, publishers, workers, and proof generators; runtime
composition must not import API routes, HTTP DTOs, FastAPI, or Starlette.

## Cleanup Utility Contract

The generated cleanup utility should be tested and dependency-light: `make clean` should call
`python scripts/clean_generated_artifacts.py`, prune `.git`, `.venv`, and `node_modules`, and
remove only known local cache, build, and coverage artifacts. The generated CI contract gate should
fail if an agent replaces the utility with an inline Makefile command or deletes the script.

## Suite Target Overrides

Generated test targets should be efficient without bypassing governance: `make test-unit`,
`make test-integration`, and `make test-e2e` should default to full suites while accepting
`UNIT_TESTS=<path>`, `INTEGRATION_TESTS=<path>`, and `E2E_TESTS=<path>` overrides. The CI contract
gate should fail if those scoped target variables, suite coverage targets, workflow Make calls, or
target commands are removed.
