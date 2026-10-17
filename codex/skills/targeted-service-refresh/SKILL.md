---
name: targeted-service-refresh
description: Perform minimal-impact Docker rebuild and restart of only changed services. Use when the user asks to keep the full platform running, refresh only impacted services, avoid full stack restarts, or run changed-files-based service refresh.
---

# Targeted Service Refresh

Refresh only impacted services through `automation/Service-Refresh.ps1`.

## Changed-Files Driven Refresh

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath <lotus-app-repo> -ChangedOnly -BaseRef origin/main
```

Dry run:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath <lotus-app-repo> -ChangedOnly -DryRun
```

## Explicit Services

```powershell
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath <lotus-app-repo> -Services <service-name>
```

## Failure Semantics

For a shared canonical workspace, first inspect the original reservation and follow
`lotus-platform/docs/operations/canonical-runtime-reservation.md#reviewed-incremental-refresh`.
Pass explicit `-ProjectsRoot`, `-RuntimeHolder`, `-RefreshPlan` and `-RefreshPlanDigest` to
Service-Refresh (plus the acquired Workbench path/runtime mode when overridden). Review the
exact old/new source vector and repository/project/service allowlist; never auto-acquire or
substitute a new lease. The command holds the existing operation fence through selective build,
immutable image/source verification, pinned replacement and health/port checks. It disables
dependency replacement and preserves untouched resource identities. Changed/rebuilt sources
must be clean committed inputs. The plan's full service list must fit one repository/project.
Service plans require `composeConfigDigest` for the full evaluated Compose model before generated
overrides. Review actual interpolation/build metadata, publish only the digest, and follow the
runbook capture command. Execution freezes that model with original project-directory provenance
and uses committed Git-blob build snapshots, excluding ignored/untracked bytes. Symlink/submodule
entries and unresolved environment/build arguments refuse; do not bypass these checks with labels.
Use the adapter's source-only transition for host-tool changes; retain actual runtime image
revisions rather than claiming the older images were rebuilt.

Core `migration-runner` declares `completionPolicy: exited-zero` in the service map. Refreshing
a declared one-shot requires the reviewed reserved path. Prepare all selected immutable images
first; force-recreate only the migration with dependency expansion, build and pull disabled, and
await inspected exit 0 before replacing the selected applications. `compose ps --all` includes
completed jobs; daemon queries retain the running-only default. Inspect every job candidate's
exact project/service/container identity and `com.docker.compose.oneoff` metadata before selecting
exactly one non-one-off service container. A validated historical `compose run` container cannot
satisfy completion; missing/malformed metadata or multiple real service containers refuse. This
observation filter never removes acquired reservation bindings or changes finish/cardinality rules.
Before build/up, require exactly one acquired resource for each declared job and inspect that
original full ID as the exact project/service with strict `oneoff=False`. Acquired historical runs,
missing/duplicate resources and malformed/foreign identity refuse before mutation. Preserve all
acquired resources and pending authority; readiness-only non-acquired run observations are not
end-to-end finish proof. Reconcile unsupported acquired topology through accountable review.
Created/running jobs are pending within the finite readiness timeout; missing,
duplicate, malformed, nonzero, OOM, restarted or drifting container/project/image/source evidence
refuses. Daemons retain the default running/health/port checks; exited-zero daemons still refuse.
Migration failure replaces no selected applications and leaves the original refresh pending.

An interrupted or failed reserved refresh stays pending under the original reservation.
Ordinary finish/proof/recovery cannot clear it. Use an explicit reviewed refresh recovery
receipt to complete the exact prepared transition or abort after exact original restoration.
Do not blindly rerun, regrant, or claim live acceptance from hermetic tests. The coordinating
owner must capture bounded live refresh, strict proof and teardown evidence.

`Service-Refresh.ps1` fails closed when Docker rejects `compose up` or when `docker compose ps`
cannot prove daemon readiness or declared one-shot completion with the governed published-port
posture. Treat any non-zero exit as failed runtime evidence: inspect the Docker error, correct the
service name, Compose environment, port, or health state, and rerun the refresh before validating
the application. Do not record a targeted refresh as successful from partial console output.

`automation/service-map.json` also owns non-secret canonical Compose environment and service
verification requirements. Always inspect `-DryRun` output before refreshing a shared stack. For
Manage, the output must show host port `8001`, its canonical DPM/Core source settings, and expected
publication `8001:8000`; do not recreate Manage from an ad hoc shell that omits this posture.

## Rules

- Reserved `-DryRun` validates the reviewed plan and Compose inputs under the operation fence without changing the book. Require ProjectPath to equal the admitted project checkout, and all explicit, environment-selected and default Compose files to be committed inputs there; another same-named checkout, external or mutable overrides refuse. Compose/build context/Dockerfile paths reject reparse points on every ancestor within the checkout. Preview grants no durable admission.

- Prefer `-ChangedOnly` first.
- Nonempty resolved-owner `build.secrets` and `build.ssh` refuse before source export/build for direct and shared builders: auxiliary host inputs are not frozen. Do not bypass this with an overlay or disclose auxiliary values. Absent/empty fields remain supported.
- Before advancing a canonical checkout, inspect its committed Compose/build-owner declarations for native support. Reservation status reports acquired scope, not current checkout equality; never reacquire or add an external overlay to hide drift. Image-only consumers require exactly one exact same-image build owner in the digest-reviewed model. Preview lists build owners separately from replacement services. The owner builds once under a unique tag; only selected consumers are prepared and replaced by immutable IDs. Building a migration-owned image executes no migration or dependencies and does not authorize adding the owner to the replacement plan.
- Do not restart full stack unless explicitly requested.
- Use the governed map; never pass credentials, tokens, or process-critical variables through it.
- Check container logs first when service startup fails.

For service mapping details, read `references/mapping.md`.
## Continuous Skill Improvement

At the end of any meaningful use of this skill, decide whether the work exposed a repeatable failure
mode, missing step, weak trigger, validation gap, or context-routing gap. If yes, update the
platform-owned skill source under `lotus-platform/codex/skills/<skill-name>` or its relevant
reference/script in the same delivery slice when the improvement is small and safe. For broader
learning, create a focused follow-up issue or PR instead of relying on chat memory.

Use this decision order:

1. tighten this skill when future agents need different behavior;
2. update `context/LOTUS-SKILL-ROUTING-MAP.md` when routing or overlap changed;
3. update central or repo-local context when source-of-truth changed;
4. add or adjust validators, scaffolds, or gates when deterministic enforcement is better than prose;
5. record an explicit no-change decision in PR evidence, the review ledger, or the task ledger when no durable update is justified.


