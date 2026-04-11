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

- `output/background-runs.json`
- `output/task-runs/*.json`
- `output/task-runs/*.md`
- `output/task-runs/*.out.log`
- `output/task-runs/*.err.log`
