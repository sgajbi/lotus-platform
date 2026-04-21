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
- `automation/Check-Background-Runs.ps1`
- `automation/Service-Refresh.ps1`

Status and artifacts:

- `output/background-runs.json`, using RFC-0094 fields such as `engineering_task_id`,
  `task_kind`, `status`, `cleanup_state`, and `evidence_refs`
- `output/task-runs/*.json`
- `output/task-runs/*.md`
- `output/task-runs/*.out.log`
- `output/task-runs/*.err.log`

Use lifecycle values from
`platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json`: `RUNNING`,
`SUCCEEDED`, `FAILED`, `TIMED_OUT`, `CANCELLED`, `LOST`, and `SUPERSEDED`. Do not translate `LOST`
into success; it means expected evidence was not written.
