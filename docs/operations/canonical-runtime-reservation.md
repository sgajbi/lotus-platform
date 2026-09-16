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

An expired live record cannot be silently removed. `reclaim` requires a new named holder, purpose, future expiry, the exact prior scope and handover receipt even if inventory is empty. The prior reservation is retained as `reclaimed`; events preserve the decision. The original holder may teardown an expired lease, but may not start another change. `recover` requires the same unexpired holder, exact source/scope and explicit fresh handover receipt; it reconciles an interrupted operation or changed inventory. Wrong/missing identities, ports, nested/foreign checkout paths, overlapping records, stale receipts and arbitrary finish tokens refuse without persisting a mutation.

Status, teardown and reclaim retain the acquired physical/source scope even when checkouts have advanced. They do not substitute new HEADs for old resource authority. A new change or proof still requires the current exact source vector; after releasing the old window, explicitly acquire the new one. This permits safe cleanup without labeling older images as the new source.

Recovery/reclaim acquire the whole-operation fence before the book lock; a live adapter cannot be displaced even after expiry. Outcome publication restores the caller's incoming native status, so successfully writing failure evidence cannot turn a failed teardown green. Cross-language PowerShell/.NET versus Python contention and real native exit-23 regressions exercise these shipped boundaries.

Canonical-labelled containers are inventoried even when stopped; incidental created test containers with merely configured but unbound canonical ports are not live claims. A running incidental project binding a reserved port is a blocking foreign conflict, not permission to stop it. Existing resource-only image/volume ownership and orphan-retirement controls are unchanged.

Before cleanup, run `automation/Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly` from Platform and review `output/front-office-qa/cleanup-plan-latest.json`. With PowerShell Core use `pwsh -NoProfile -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly`; this read-only Docker plan is portable. Exact project/checkout provenance is necessary but is not holder admission. Never replace either check with prefix matching, daemon-wide prune or manually stopping an unlabelled resource. Publish acquisition/refusal and final release receipts on the coordinating issue in addition to the machine book.

## Evidence boundaries

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

Adapter and process-boundary tests are not canonical acceptance. Re-run the full governed
runtime, including Idea, supported APIs, independent persistence checks, DPM/browser proof
and teardown, before claiming the consumer has accepted a source-qualified correction.

Hermetic tests use real temporary Git revisions, actual OS/file transactions and the shipped PowerShell adapter. The supplier control is response-ready until Workbench's shipped scripts and required checks accept it. Live acquisition/control proof is separate from Level A receipt evidence, Level B canonical validation, historical CI revision coverage and production IAM. Core's PARTIAL/null-epoch seed boundary does not become ready because a reservation or CI gate passed.
