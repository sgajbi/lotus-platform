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

An interrupted or failed reserved refresh stays pending under the original reservation.
Ordinary finish/proof/recovery cannot clear it. Use an explicit reviewed refresh recovery
receipt to complete the exact prepared transition or abort after exact original restoration.
Do not blindly rerun, regrant, or claim live acceptance from hermetic tests. The coordinating
owner must capture bounded live refresh, strict proof and teardown evidence.

`Service-Refresh.ps1` fails closed when Docker rejects `compose up` or when `docker compose ps`
cannot prove the selected services are running with their governed health and published-port
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


