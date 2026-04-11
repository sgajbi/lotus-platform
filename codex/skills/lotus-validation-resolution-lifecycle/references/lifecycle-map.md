# Lifecycle Map

## Phases

1. `validate`
- Bring up app and run QA platform validator.
- Generate artifacts under `lotus-platform/output/qa/<run-id>/`.

2. `syncissues`
- For each failing check, update issue state to `qa_failed` with evidence.
- Optionally close resolved QA issues (`-AutoCloseResolved`).

3. `fullcycle`
- `validate` + `syncissues` in one command.

4. `monitorpr`
- Poll PR state until merged.
- Automatically run post-merge validation and issue sync.

5. `revalidate`
- Re-run validation after code changes and sync issue states.

## Artifacts

- `qa-summary.md`
- `qa-summary.json`
- `qa-issues.json`
- evidence markdown files under `evidence/<repo>/`

## Exit Criteria

- No blocking findings in latest run.
- All QA issues closed with validation evidence.
- Merged PR(s) linked to resolved issues.
