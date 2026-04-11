# Operations

Core scripts:

- `automation/Sync-Repos.ps1`
- `automation/PR-Monitor.ps1`
- `automation/Platform-Pulse.ps1`
- `automation/Run-Agent.ps1`

Behavior:

- Sync skips pull on dirty worktrees
- PR monitor queries `author:@me state:open` via `gh`
- Agent loop writes a markdown status snapshot each iteration
