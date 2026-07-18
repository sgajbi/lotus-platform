# Profile Guide

Profiles are defined in:

`<lotus-platform>/automation/task-profiles.json`

Current profiles:

- `fast-feedback`: fast lint/typecheck/check loops across repos
- `docker-build`: targeted docker rebuild/start per app
- `ci-parity`: local CI-parity checks
- `platform-smoke`: platform demo loader and health smoke

Core scripts:

- `automation/Run-Parallel-Tasks.ps1`
- `automation/Start-Background-Run.ps1`
- `automation/repository_background_task.py`
- `automation/Check-Background-Runs.ps1`
- `automation/Service-Refresh.ps1`

`Start-Background-Run.ps1` has two mutually exclusive modes:

- `-Profile <name>` launches a shared catalog profile through `Run-Parallel-Tasks.ps1`;
- `-Repository <name> -TargetType <make|npm|python|powershell> -Target <target>` launches one
  repository-native target through a JSON job specification and argv-only runner.

Use repository mode for a long validation that should not require editing `task-profiles.json`.
Use `-ExpectedHead`, `-RequireClean`, and `-RequiredArtifact` for exact-source certification. A
required artifact must be repo-relative and must be written during the run.

Status and artifacts:

- `output/background-runs.json`, using RFC-0094 fields such as `engineering_task_id`,
  `task_kind`, `status`, `cleanup_state`, and `evidence_refs`
- `output/task-runs/*.json`
- `output/task-runs/*.md`
- `output/task-runs/*.out.log`
- `output/task-runs/*.err.log`
- `output/task-runs/*.job.json`
- `output/task-runs/*.result.json`

Use lifecycle values from
`platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json`: `RUNNING`,
`SUCCEEDED`, `FAILED`, `TIMED_OUT`, `CANCELLED`, `LOST`, and `SUPERSEDED`. Do not translate `LOST`
into success; it means expected evidence was not written.
