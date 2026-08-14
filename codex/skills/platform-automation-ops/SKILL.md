---
name: platform-automation-ops
description: Run and monitor async, repeatable cross-repo platform automation tasks using lotus-platform automation scripts. Use when the user asks to offload builds/tests/linting/docker refresh/seeding outside chat, run tasks in parallel, track background execution, or check automation status while implementation continues.
---

# Platform Automation Ops

Use `lotus-platform/automation` as the system of record for operational automation.

Execute scripts from the local `lotus-platform` workspace root, not from `automation/`.

Before launching or summarizing detached work, use
`lotus-platform/context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md` and the contract in
`lotus-platform/platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json`.
For governed multi-agent delegation, also use
`lotus-platform/platform-contracts/agent-engineering/delegation-policy-contract.v1.json`.
Preserve `engineering_task_id`, repository, branch, PR number, commit SHA, check name, RFC id, file
path, endpoint, contract name, portfolio id, and task status exactly when those identifiers are
present.

## Execute Background Profiles

1. Run detached tasks:
```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Start-Background-Run.ps1 -Profile fast-feedback -MaxParallel 3
```
2. Check status on demand:
```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Check-Background-Runs.ps1
```
3. Watch status:
```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Check-Background-Runs.ps1 -Watch -IntervalSeconds 20
```
4. Cancel one exact local task:
```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Cancel-Background-Run.ps1 `
  -EngineeringTaskId <engineering_task_id> -Reason <reason> -Actor <operator>
```

## Execute A Repository-Native Target

Use repository mode when one governed Make, NPM, Python, or PowerShell target is long-running but
does not belong in the shared cross-repository profile catalog:

```powershell
$head = git -C <repository-root> rev-parse HEAD
powershell -ExecutionPolicy Bypass -File automation\Start-Background-Run.ps1 `
  -Repository <repo-name> -TargetType make -Target <make-target> `
  -ExpectedHead $head -RequireClean -RequiredArtifact <repo-relative-pattern>
```

The repository name must exist exactly once in `automation/repos.json`. Do not pass a shell command
string. The typed launcher serializes target arguments, rechecks repository identity and source
fences in the detached process, and writes exact job/result artifacts. From PowerShell, pass
multiple arguments with `-TargetArgument @("one", "two")`; from a native caller, use
`-TargetArgumentsJson '["one","two"]'`.

Declare cancellation cleanup posture at launch. Use `-NoExternalCleanupRequired` for process-only
work. For Docker-backed work, pass a `-ComposeCleanupPlanPath` that declares exact project,
working-directory, and Compose-file provenance. Do not infer cleanup ownership after launch.

## Run Foreground Parallel Profiles

Use this for immediate feedback in current terminal:

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Run-Parallel-Tasks.ps1 -Profile fast-feedback -MaxParallel 3
```

## Refresh Only Impacted Services

Use changed-files mapping for selective restart:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath <lotus-app-repo> -ChangedOnly -BaseRef origin/main
```

Use explicit services when needed:

```powershell
powershell -ExecutionPolicy Bypass -File automation\Service-Refresh.ps1 -ProjectPath <lotus-app-repo> -Services <service-name>
```

## Report Artifacts

Read and summarize:
- `output/background-runs.json`
- `output/heartbeat/heartbeat-status.json`
- `output/heartbeat/heartbeat-status.md`
- `output/heartbeat/heartbeat-issues.json`
- `output/heartbeat/heartbeat-state.json`
- `output/task-runs/*.json`
- `output/task-runs/*.md`
- `output/task-runs/*.out.log`
- `output/task-runs/*.err.log`

For `output/background-runs.json`, report the governed lifecycle status without translation:

- `RUNNING`: launched process is still active,
- `SUCCEEDED`: expected result artifact exists and all child task exit codes are zero,
- `FAILED`: result artifact exists but failed or could not be parsed,
- `LOST`: process ended before expected result evidence was written.
- `CANCELLED`: exact process ownership was verified and the task was terminated; inspect
  `cleanup_state` and the cancellation receipt separately.

Treat `LOST` as an operational finding that needs cleanup or rerun evidence. GitHub Actions remains
the source of truth for GitHub check status; the background-run ledger is local automation evidence.
`Check-Background-Runs.ps1` also reconciles older wrapped `output/background-runs.json` entries into
normal task-ledger rows before status evaluation. Do not treat legacy wrapper shape as a manual
blocker; run the checker and use the normalized ledger it writes back.

Never cancel by broad process matching or Docker cleanup. The governed command verifies PID plus
start identity, terminates only the owned tree, preserves `LOST` for vanished or reused processes,
and writes an atomic receipt. Compose cleanup runs only for launch-declared projects with exact live
label provenance. `cleanup_state=DONE` requires passed cleanup; ambiguous or failed cleanup is
`BLOCKED`.

## Generate Heartbeat Attention Artifacts

Use this for an advisory RFC-0095 attention snapshot across configured local evidence sources:

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Run-Heartbeat.ps1
```

Use deterministic metadata when preserving proof in an RFC, PR, or handoff:

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Run-Heartbeat.ps1 -GeneratedAtUtc 2026-04-21T00:00:00Z -Branch <branch>
```

Heartbeat output is derived advisory evidence. It does not replace GitHub, the RFC-0094
background-run ledger, mesh certification, wiki source, context validators, or `lotus-ai`
workflow-pack runtime APIs as source truth. Suppressed items remain visible; blocking findings are
not suppressible.

## Govern Delegated Work

Use the RFC-0096 delegation policy before launching, resuming, or summarizing delegated work:

1. choose one governed profile: `exploration`, `implementation`, `validation`, `review_support`,
   `documentation`, or `ci_triage`,
2. record read scope and explicit write scope, or `none` for no-write profiles,
3. include forbidden actions: no unrelated reverts, no broad cleanup, no PR merge, and no wiki
   publication without main-agent review,
4. require returned evidence: files changed, checks run, evidence refs, blockers, remaining risks,
   follow-up posture, unrelated-work preservation, and patch summary by write scope,
5. keep the main agent accountable for diff review, integration, tests, PR posture, wiki
   publication, and final communication.

Do not delegate immediate critical-path blockers, broad repo cleanup, overlapping write scopes, or
hidden-state work that cannot be reconstructed from contracts, ledgers, files, tests, or GitHub.

## Close PR Loop

Use this when asked to monitor PRs, queue merges, and clean branches without manual repetition:

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Close-PR-Loop.ps1
```

Continuous mode:

```powershell
cd <lotus-platform>
powershell -ExecutionPolicy Bypass -File automation\Close-PR-Loop.ps1 -Watch -IntervalSeconds 30
```

## Safety and Operating Rules

- Keep stack stable; do not restart entire platform unless explicitly requested.
- Prefer repository mode over a terminal-session fallback for long repo-native checks that are not
  shared profiles; include exact-HEAD, clean-tree, and required-artifact fences for certification.
- Prefer `-ChangedOnly` or specific services for refresh.
- Check logs first when failures occur.
- Keep documentation updates in `lotus-platform` synchronized with script behavior.
- For RFC closure, supported-feature promotion, or other mainline-certified canonical front-office
  proof, use `automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -RequireMainlineSources`
  after a read-only `-CleanPlanOnly` review. This delegates Workbench's fail-closed exact-main
  source preflight and records `require_mainline_sources` in the platform wrapper summary.
- For canonical DPM command-center seed failures against `lotus-manage`, use
  `automation/Invoke-DpmCommandCenterSeed.ps1 -PreflightOnly` first when the stack is already
  running. A 403 on the preflight means the platform seed actor, role, service identity, or
  capability contract is wrong; fix the caller contract and preserve Manage fail-closed
  authorization rather than disabling authz for local/demo evidence. After preflight passes, treat
  `DPM_CORE_CONTEXT_INCOMPLETE` as source-readiness evidence: preserve the response body from
  `dpm-command-center-seed-latest.json`, probe Core `DpmSourceReadiness:v1` for the governed
  portfolio/as-of date, and link or create the Core owner issue instead of reopening auth work.
- When automation script behavior changes, update:
  - `automation/README.md`
  - `automation/docs/Automation-Guide.md`
  - `docs/operations/Local Development Runbook.md`
  - this skill reference file if command flow changed
  - heartbeat context/wiki guidance when RFC-0095 operator behavior changes
  - delegation context/wiki guidance when RFC-0096 operating behavior changes
- Do not summarize detached work from chat memory alone when a task-ledger or GitHub evidence source
  exists.

For profile definitions and expected behavior, read `references/profile-guide.md`.
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


