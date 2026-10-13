# Canonical runtime reservation

Platform owns the [v1 coordination contract](../../platform-contracts/runtime/canonical-runtime-reservation.v1.json), Python transaction/control and PowerShell adapter. Workbench owns admission in its shipped startup and teardown scripts. The record is local machine coordination, not an IAM verifier or a grant store. No holder is inferred or defaulted from a project name, repository or business identifier.

## Acquire, inspect and release

Working directory: `lotus-platform`. Set the workspace directory holding the one owned checkout per repository. On Windows PowerShell:

```powershell
$env:LOTUS_WORKSPACE_ROOT = (Split-Path -Parent (Get-Location).Path)
$env:LOTUS_CANONICAL_RUNTIME_HOLDER = 'lotus-platform-47'
python automation/canonical_runtime_reservation.py status --projects-root $env:LOTUS_WORKSPACE_ROOT
python automation/canonical_runtime_reservation.py acquire --projects-root $env:LOTUS_WORKSPACE_ROOT --holder $env:LOTUS_CANONICAL_RUNTIME_HOLDER --purpose 'Platform #849 / Gateway #692 Cycle 6' --expiry-utc '<future-aware-UTC-within-eight-hours>'
python automation/canonical_runtime_reservation.py preflight --projects-root $env:LOTUS_WORKSPACE_ROOT --holder $env:LOTUS_CANONICAL_RUNTIME_HOLDER
powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -BuildImages -RequireMainlineSources -RuntimeHolder $env:LOTUS_CANONICAL_RUNTIME_HOLDER
```

The placeholder expiry must be replaced with the operator's actual bounded window. Startup never acquires a foreign stack. Acquisition writes the single workspace book atomically under an OS lock. `status` reports holder, purpose, start, expiry, exact projects/ports, sources and current resource digests. The current remote main is not substituted for the checkout being evaluated. Actual Compose publications include ports omitted by the old required-port list (for example Report 8301); local Manage/Gateway modes reserve 8001/8111 explicitly.

When using the QA wrapper's supported `-WorkbenchRepoPath` override, acquire and preflight with `--workbench-repo-path` set to that same absolute checkout. The adapter carries the selected path through admission and publication. Each Workbench script requires the selected path to match its executing checkout before I/O; admission cannot approve checkout A while checkout B changes resources. Teardown retains the acquired source authority but still requires the acquired Workbench checkout path.

The provider-owned DPM seed also admits one operation before its authorization/cash pre-reads and
persistent POSTs, then publishes success/failure in `finally`. The QA wrapper forwards workspace,
selected Workbench and holder. Direct seed invocation accepts `-ProjectsRoot`,
`-WorkbenchRepoPath` and `-RuntimeHolder`; it never auto-acquires. The existing `-PreflightOnly`
side-effect-free malformed-payload authorization diagnostic remains distinct from seed execution.
When DPM seed runs inside Workbench startup, execute it in-process and carry that caller's live
exclusive canonical FileStream, admitted holder, workspace, selected checkout and token unchanged.
Only the original exclusive handle registered by `Enter-CanonicalRuntimeOperation` to that token
in the same module instance is admitted. Reopening even the same path exclusively after interruption
does not recreate admission; new-process, replacement, shared, absent/disposed/foreign handles refuse before preflight and I/O. A persisted token survives parent
interruption and is not admission. The caller's synchronous invocation retains its actual fence
through every child pre-read/write; the child neither reacquires nor finishes that operation.

For diagnostic `-CoreManageOnly` startup, acquire/preflight explicitly with `--runtime-mode core-manage`.
Only Core/Manage Compose configurations are required, together with immutable Core, Manage,
executing Workbench and Platform HEADs and ingress provenance. Skipped product checkouts/configuration
are not consulted. Startup carries that explicit mode through begin/finish; its exact scope cannot
substitute for a full lease. Teardown uses the acquired four-source scope and stops only Core/Manage
and admitted ingress/listeners using only acquired ports, leaving skipped-service listeners untouched.
DPM seed writes require the full Gateway/Advise scope: partial startup returns before DPM invocation,
and explicit partial DPM execution refuses before admission/pre-reads/writes rather than manufacturing
broader service authority. This partial mode never establishes populated canonical Level B acceptance.

The PowerShell adapter admits an operation before runtime I/O and holds an exclusive operation handle through completion. Native failures must remain failures; `finally` publishes the observed inventory with its truthful outcome. A terminated process leaves its durable operation unfinished and new admission refuses. A finish token cannot be manufactured from a path, project name or request body. Validation inside startup uses `preflight-operation` with the admitted token and fresh source/resource observation. Standalone validation admits and finishes its own fenced operation across DNS, HTTP, evidence reads and browser execution; it does not release a momentary preflight before gathering evidence. Preflight reads do not change the book. Teardown clears the active lease only on success with zero canonical containers/listeners; retained images/volumes are separate from live ownership and still subject to the existing cleanup plan. `-CleanPlanOnly` remains read-only. In a combined `-Clean -BringUp` invocation, cleanup retains the same explicitly acquired window rather than automatically reacquiring.

From `lotus-workbench`, the adopted `npm run live:stack:up`, `live:stack:preflight` and `live:stack:down` require this explicitly set environment holder. The default teardown releases the record. Preflight refuses a missing lease even when ports are free. Read-only Platform status/cleanup planning does not require acquisition. Linux CI can test the pure control and PowerShell adapter; Linux Docker canonical bring-up is not declared supported by this Windows listener observer.

## Handover, interruption and expiry

For preexisting canonical resources, inspect `status` and obtain an explicit operator decision before acquisition. The reviewed handover JSON must contain exactly `holder`, `operator`, `sourceReceipt`, `scopeDigest` and `bindingsDigest`, bound to the fresh status digests. Pass its path with `--handover-receipt`. No command synthesizes this receipt, and possession of the holder name is only the operator's explicit local coordination identity, not production authentication.

An expired live record cannot be silently removed. `reclaim` requires a new named holder, purpose, future expiry, the exact prior scope and handover receipt even if inventory is empty. The prior reservation is retained as `reclaimed`; events preserve the decision. The original holder may teardown an expired lease, but may not start another change. `recover` requires the same unexpired holder, preserves the exact acquired source/scope, and requires an explicit fresh handover receipt bound to the currently observed resources; it reconciles an interrupted ordinary operation or changed inventory even when repository checkouts have since advanced. Recovery does not authorize another change from a stale source vector. Use the reviewed refresh transition below or release and explicitly acquire a new window. Wrong/missing identities, ports, nested/foreign checkout paths, overlapping records, stale receipts and arbitrary finish tokens refuse without persisting a mutation.

Status, ordinary recovery, teardown and reclaim retain the acquired physical/source scope even when checkouts have advanced. They do not substitute new HEADs for old resource authority. A new change or proof still requires the current exact source vector; only a successful reviewed refresh changes that vector within the original window. This permits safe cleanup without labeling older images as the new source.

## Reviewed incremental refresh

Use `automation/Service-Refresh.ps1` from the canonical Platform checkout for one repository/project's selected services. The original reservation ID, holder, start, expiry, projects, ports and runtime mode remain unchanged. The operator reviews a JSON plan and its digest before execution; the command never generates approval or acquires a replacement lease. The exact plan fields are:

| Field | Required value |
| --- | --- |
| `schemaVersion` | `lotus.canonical-runtime.refresh.v1` |
| `reservationId`, `holder` | Original live reservation identity and same unexpired holder |
| `operator`, `sourceReceipt` | Accountable operator and review evidence reference |
| `originalScopeDigest`, `originalBindingsDigest` | Digests from the original reservation/status |
| `targetScope` | Exact reviewed projects/ports/sources; only source SHA values may change |
| `repositoryChanges` | Exact changed repository keys, each with `from`, `to`, and `disposition` (`source-only` or `service-refresh`) |
| `services` | Exact list of `{repository, project, service}` replacements; empty for source-only transitions |
| `composeConfigDigest` | Required for service replacement: digest of the full evaluated Compose JSON before generated image/label overrides; omit for source-only transitions |

The plan digest is `sha256:` plus SHA-256 of UTF-8 JSON with sorted keys and compact separators, as implemented by `canonical_runtime_lease.digest`. Every changed or rebuilt repository must be clean and committed at its reviewed target SHA. Services rebuilding at the same SHA are allowed. A `service-refresh` source change requires a service; `source-only` forbids replacements for that repository. A single Service-Refresh invocation must match the plan's entire service list and one repository/project. Split independent projects into separately reviewed sequential transitions; each next plan binds the newly published scope/bindings.

For a service plan, review the full evaluated Compose model, including interpolated shell/default `.env` inputs, build arguments, commands, mounts and resolved service environment. Capture it with the exact selected project/files and intended environment; do not add the generated refresh override. From canonical Platform, Windows PowerShell or PowerShell Core:

```powershell
$evaluated = & docker compose --project-directory "$env:LOTUS_WORKSPACE_ROOT/lotus-performance" -p $env:LOTUS_REFRESH_COMPOSE_PROJECT -f "$env:LOTUS_WORKSPACE_ROOT/lotus-performance/docker-compose.yml" config --format json
if ($LASTEXITCODE -ne 0) { throw 'Compose review capture failed.' }
[IO.File]::WriteAllText($env:LOTUS_REVIEWED_COMPOSE_JSON, ($evaluated -join "`n"))
python automation/canonical_refresh_inputs.py digest --config $env:LOTUS_REVIEWED_COMPOSE_JSON
if ($LASTEXITCODE -ne 0) { throw 'Compose digest calculation failed.' }
```

Set the acquired project, absolute external JSON path and any additional tracked reviewed Compose files explicitly; the example is for Performance. Apply the intended `APP_GIT_COMMIT_SHA`/`APP_GIT_BRANCH` below during capture as well as execution. Put the printed digest in `composeConfigDigest`, then review and digest the complete plan. The JSON can contain secrets: keep it operator-local and publish only its digest, never its contents. Regenerate/review the plan if any evaluated value changes.

Execution evaluates the original selected files once under the operation fence and rejects any full-model digest mismatch before build/replacement. It freezes that resolved model for subsequent commands with an explicit empty interpolation env file and the original `--project-directory`; Compose's already escaped literal dollars are preserved. Unresolved selected service environment/build-argument values refuse. The generated override changes only selected image tags/source labels, then pins prepared immutable images.

Selected build contexts and Dockerfiles are remapped into an isolated snapshot exported directly from exact committed Git blobs. Ignored/untracked files and dirty working bytes cannot enter it, even when `.dockerignore` would include them; local archive attributes cannot substitute different content. Symlink/submodule tree entries are unsupported and refuse. Snapshot/config files are removed in `finally`, including preview/failure. This bounds local source/config custody; it does not certify external base images, network downloads or runtime bind-mount contents.

Execution order is explicit: review the original reservation and target plan first, advance only the reviewed host checkouts to those exact target commits, then call `begin-refresh` through the adapter. Host checkout advancement does not change containers or rewrite the reservation. During this interval the original grant remains unchanged and ordinary current-source proof refuses; no refresh operation exists until begin admits it. Begin requires the observed source vector already equal `targetScope`, then records the pending operation under the original grant. It does not advance Git on the operator's behalf. Keep plan/receipt files outside changed repositories so they do not dirty the reviewed inputs.

For an approved mainline fast-forward, run this host-only preparation from the canonical `lotus-platform` checkout before either refresh example below. The reviewed target commits must already be present locally. This example refuses a dirty checkout, another branch, a changed original HEAD or a non-fast-forward target; resolve those with the repository owner rather than resetting someone else's checkout. Set `LOTUS_WORKBENCH_REPO_PATH` only when that exact overridden Workbench checkout was acquired.

```powershell
$plan = Get-Content -LiteralPath $env:LOTUS_REFRESH_PLAN -Raw | ConvertFrom-Json
foreach ($entry in $plan.repositoryChanges.PSObject.Properties) {
  $checkout = Join-Path $env:LOTUS_WORKSPACE_ROOT $entry.Name
  if ($entry.Name -eq 'lotus-workbench' -and $env:LOTUS_WORKBENCH_REPO_PATH) { $checkout = $env:LOTUS_WORKBENCH_REPO_PATH }
  $dirty = @(git -C $checkout status --porcelain)
  if ($LASTEXITCODE -ne 0 -or $dirty.Count -gt 0) { throw 'Reviewed checkout must be clean.' }
  $branch = git -C $checkout branch --show-current
  if ($LASTEXITCODE -ne 0 -or $branch -ne 'main') { throw 'This preparation example requires owned main.' }
  $head = git -C $checkout rev-parse HEAD
  if ($LASTEXITCODE -ne 0 -or $head -ne $entry.Value.from) { throw 'Original checkout source differs from review.' }
  git -C $checkout merge-base --is-ancestor $entry.Value.from $entry.Value.to
  if ($LASTEXITCODE -ne 0) { throw 'Reviewed target must be a fast-forward.' }
  git -C $checkout merge --ff-only $entry.Value.to
  if ($LASTEXITCODE -ne 0) { throw 'Reviewed host checkout advance failed.' }
  $head = git -C $checkout rev-parse HEAD
  if ($LASTEXITCODE -ne 0 -or $head -ne $plan.targetScope.sources.($entry.Name)) { throw 'Target checkout differs from review.' }
}
```

Working directory: the canonical `lotus-platform` checkout. Set `LOTUS_WORKSPACE_ROOT`, `LOTUS_CANONICAL_RUNTIME_HOLDER`, `LOTUS_REFRESH_PLAN` (absolute JSON path) and `LOTUS_REFRESH_PLAN_DIGEST` to the reviewed values. Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/Service-Refresh.ps1 -ProjectPath "$env:LOTUS_WORKSPACE_ROOT/lotus-gateway" -ProjectsRoot $env:LOTUS_WORKSPACE_ROOT -RuntimeHolder $env:LOTUS_CANONICAL_RUNTIME_HOLDER -Services lotus-gateway -RefreshPlan $env:LOTUS_REFRESH_PLAN -RefreshPlanDigest $env:LOTUS_REFRESH_PLAN_DIGEST
```

PowerShell Core uses the same parameters with `pwsh -NoProfile -File`. Linux may run the hermetic control/adapter tests; the Windows listener observer still bounds supported live execution. Carry `-WorkbenchRepoPath` and `-RuntimeMode core-manage` when those were acquired. `-ComposeFiles` accepts explicit Compose files; defaults resolve the normal base/override files or `COMPOSE_FILE`. Every supplied/default Compose file must be tracked in the reviewed repository, match its current reviewed commit, and have no reparse-point redirect in its path. External, untracked and modified overrides refuse before build or replacement. The resolved project, selected-service publications, local build context and Dockerfile must stay within the admitted repository and original bindings. Additional build contexts, inline Dockerfiles and reparse-point build inputs or ancestors refuse, including ignored junction directories above an ordinary context or Dockerfile. Compose files and build inputs share the same repository-path guard. Evaluated Compose configuration is inspected in memory, without publishing its potentially secret contents.

Reserved `-DryRun` holds the operation fence while checking the same holder, reviewed digest, target sources, original bindings/images and evaluated Compose inputs as admission. The resolved `ProjectPath` must equal the checkout admitted for the planned project, including when `ProjectsRoot` is supplied independently; another clean same-named checkout refuses before any Compose inspection, build or replacement. It leaves the reservation book unchanged and performs no build, replacement or readiness mutation. Output shows the selected build and bounded replacement commands; immutable image IDs remain subject to verification after the real build. A successful preview is not a durable operation token or permission to skip admission on execution.

Build labels and application build metadata are separate inputs. Performance's existing Compose `x-provenance-build.args` consumes `APP_GIT_COMMIT_SHA` and `APP_GIT_BRANCH`; its Dockerfile puts those values into runtime environment fields used by `/version`. They default to `local`. The refresh override adds labels but does not synthesize or override those build arguments. For a reviewed Performance mainline refresh, bind the existing inputs explicitly after host preparation, from canonical `lotus-platform` (Windows PowerShell or PowerShell Core):

```powershell
$plan = Get-Content -LiteralPath $env:LOTUS_REFRESH_PLAN -Raw | ConvertFrom-Json
$checkout = Join-Path $env:LOTUS_WORKSPACE_ROOT 'lotus-performance'
$head = git -C $checkout rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $head -ne $plan.targetScope.sources.'lotus-performance') { throw 'Performance target SHA differs from review.' }
$branch = git -C $checkout branch --show-current
if ($LASTEXITCODE -ne 0 -or $branch -ne 'main') { throw 'Performance mainline build requires actual main.' }
$previousSha = $env:APP_GIT_COMMIT_SHA
$previousBranch = $env:APP_GIT_BRANCH
try {
  $env:APP_GIT_COMMIT_SHA = $head
  $env:APP_GIT_BRANCH = $branch
  $services = @($plan.services | Where-Object { $_.repository -eq 'lotus-performance' } | ForEach-Object { $_.service })
  & ./automation/Service-Refresh.ps1 -ProjectPath $checkout -ProjectsRoot $env:LOTUS_WORKSPACE_ROOT -RuntimeHolder $env:LOTUS_CANONICAL_RUNTIME_HOLDER -Services $services -RefreshPlan $env:LOTUS_REFRESH_PLAN -RefreshPlanDigest $env:LOTUS_REFRESH_PLAN_DIGEST
  if ($LASTEXITCODE -ne 0) { throw 'Performance refresh failed; inspect the pending operation.' }
} finally {
  $env:APP_GIT_COMMIT_SHA = $previousSha
  $env:APP_GIT_BRANCH = $previousBranch
}
```

Forward the acquired Workbench path/runtime mode if overridden. After replacement, the coordinating owner must compare Performance `/version`'s `git_commit_sha` and `git_branch` with this reviewed SHA and actual `main` as part of live proof. Label verification alone does not establish application-version agreement. Other repositories retain their own supported build-metadata inputs.

The adapter holds the existing exclusive operation fence across admission, selective build, image verification, replacement, health/port verification and finish. Original scope/bindings remain authoritative while pending. A unique operation image tag prevents a selected build from moving an untouched service's shared tag. Build labels bind repository, checkout and target source SHA. `prepare-refresh` resolves immutable image IDs and verifies those labels before any replacement. Replacement pins those IDs and uses `up -d --no-deps --no-build --pull never`. Finish requires the prepared IDs/source labels, unchanged service cardinality and binding shapes, and exact untouched container/host identities and image evidence. A successful finish atomically advances sources/bindings while retaining the original reservation and expiry. It is supplier transition evidence; application validation and live acceptance remain separate.

For a host-tool-only change, review a source-only plan with an empty service list. From the canonical Platform checkout, use the same explicit environment values:

```powershell
Import-Module ./automation/CanonicalRuntimeReservation.psm1
$operation = Enter-CanonicalRuntimeRefresh -ProjectsRoot $env:LOTUS_WORKSPACE_ROOT -Holder $env:LOTUS_CANONICAL_RUNTIME_HOLDER -RefreshPlan $env:LOTUS_REFRESH_PLAN -RefreshPlanDigest $env:LOTUS_REFRESH_PLAN_DIGEST
$outcome = 'failure'
try {
  Assert-CanonicalRuntimeRefresh -Operation $operation | Out-Null
  $outcome = 'success'
} finally {
  Exit-CanonicalRuntimeOperation -Operation $operation -Outcome $outcome
}
```

This path performs observation and coordination only. It requires identical runtime bindings/images and records their actual image revisions separately from the newer host-tool source vector. It does not claim that an older runtime image was rebuilt.

Any failed build, image/source mismatch, readiness failure, interrupted process or failed finish leaves the operation pending and preserves the original grant. Ordinary proof, finish and recovery refuse that pending refresh. Do not blindly rerun or regrant. After the original fence is free, the same unexpired holder may use `recover-refresh --handover-receipt` with exactly `holder`, `operator`, `sourceReceipt`, `scopeDigest`, `bindingsDigest`, `reservationId`, `refreshPlanDigest`, and `disposition`. `complete` requires the exact target sources, prepared replacement images and untouched bindings. `abort` requires the exact restored original sources, bindings and images. Recovery does not repair Docker resources automatically. An expired pending refresh requires accountable reclaim/cleanup rather than an unexpired refresh recovery claim. Publish actual live bounded refresh, strict proof and teardown evidence before closing the refresh issue.

Working directory: canonical `lotus-platform`; `LOTUS_REFRESH_RECOVERY_RECEIPT` is the absolute reviewed recovery JSON path:

```powershell
python automation/canonical_runtime_reservation.py recover-refresh --projects-root $env:LOTUS_WORKSPACE_ROOT --holder $env:LOTUS_CANONICAL_RUNTIME_HOLDER --handover-receipt $env:LOTUS_REFRESH_RECOVERY_RECEIPT
```

Recovery/reclaim acquire the whole-operation fence before the book lock; a live adapter cannot be displaced even after expiry. Outcome publication restores the caller's incoming native status, so successfully writing failure evidence cannot turn a failed teardown green. Cross-language PowerShell/.NET versus Python contention and real native exit-23 regressions exercise these shipped boundaries.

Canonical-labelled containers are inventoried even when stopped; incidental created test containers with merely configured but unbound canonical ports are not live claims. A running incidental project binding a reserved port is a blocking foreign conflict, not permission to stop it. The read-only cleanup plan records the observed foreign project/path separately from the canonical port-owner project/path and exact overlap. Only an exact missing, unregistered labelled checkout can enter the digest-bound one-container retirement flow; that flow re-resolves current Compose port ownership and the live overlap immediately before mutation. Active/registered paths, stopped or noncanonical-port containers, ambiguous owners, broad project cleanup and resource-only image/volume cleanup remain refused.

Before cleanup, run `automation/Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly` from Platform and review `output/front-office-qa/cleanup-plan-latest.json`. With PowerShell Core use `pwsh -NoProfile -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly`; this read-only Docker plan is portable. Exact project/checkout provenance is necessary but is not holder admission. Never replace either check with prefix matching, daemon-wide prune or manually stopping an unlabelled resource. Publish acquisition/refusal and final release receipts on the coordinating issue in addition to the machine book.

## Evidence boundaries

Resource-only images and volumes remain refused by normal cleanup. The separate
[reviewed resource-only recovery workflow](resource-only-recovery.md) requires an explicit
digest-bound operator disposition, complete archival and isolated restore verification before
normal exact retirement. Its presence does not admit anonymous resources or certify live recovery.
Immutable discovery does not grant current I/O: each recovery target requires fresh START-timed
native target/all-consumer observations under the original stream. This fence does not exclude
unrelated Docker clients or establish an application-consistent backup; use a quiet reviewed fixture.

### DPM cash pre-read

`Invoke-DpmCommandCenterSeed.ps1` passes the explicitly configured
`dpm_command_center.workbench_caller_tenant_id` to the cash resolver as
`--caller-tenant-id`. The Gateway Overview route forwards this tenant fence to Core.
It is not Manage's command tenant, a portfolio-derived grant, or production IAM evidence.
The source ownership field `portfolio.source_tenant_id` remains independent.

The existing `-PreflightOnly` diagnostic also validates the caller fence locally before
its side-effect-free Manage authorization probe. This cheap syntax check performs no
Gateway read and does not prove live access or financial readiness. The complete seed
performs the actual date-aligned Gateway read under the original runtime operation fence
before its first persistent write. Missing or ambiguous caller scope, source denial,
degraded evidence, wrong portfolio/date and invalid cash values remain failures.

The child returns a bounded JSON error code to the seed, which retains it in the seed
receipt rather than replacing it with an exit code alone. Unknown native failures or
malformed child output retain only a generic resolver failure; raw response bodies and
child diagnostics are not copied into the receipt. Diagnose `CANONICAL_CASH_SOURCE_HTTP_401`
or `_403` as a refusal, not permission to substitute a tenant. Cash conversion still
preserves Decimal precision and requires confirmed exact-date, non-degraded evidence.
Successful child output must be one complete receipt for the exact requested source, portfolio
and dates. Percentage and normalized ratio must agree exactly; comparison preserves arbitrary
decimal precision and signed zero. Error output must likewise contain one string reason in the
closed vocabulary; arrays or nested values cannot introduce arbitrary diagnostics into evidence.

Adapter and process-boundary tests are not canonical acceptance. Re-run the full governed
runtime, including Idea, supported APIs, independent persistence checks, DPM/browser proof
and teardown, before claiming the consumer has accepted a source-qualified correction.

Hermetic tests use real temporary Git revisions, actual OS/file transactions and the shipped PowerShell adapter. The supplier control is response-ready until Workbench's shipped scripts and required checks accept it. Live acquisition/control proof is separate from Level A receipt evidence, Level B canonical validation, historical CI revision coverage and production IAM. Core's PARTIAL/null-epoch seed boundary does not become ready because a reservation or CI gate passed.
