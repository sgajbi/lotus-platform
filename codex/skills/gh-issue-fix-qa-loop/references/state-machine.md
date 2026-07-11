# Issue Fix QA Loop State Machine

States:
- `status/in-progress`
- `status/fixed-locally`
- `status/pr-open`
- `status/merged-to-main`
- `status/blocked` when the failure blocks progress
- issue closed, with `status/merged-to-main` retained for filtering

Transitions:
1. `status/in-progress -> status/fixed-locally`
2. `status/fixed-locally -> status/pr-open`
3. `status/pr-open -> status/merged-to-main`
4. `status/merged-to-main -> issue closed`
5. `status/merged-to-main -> status/blocked`
6. `status/blocked -> status/in-progress`

Rules:
- Never transition directly from `status/pr-open` to issue closed.
- Never transition directly from `status/in-progress` to `status/pr-open`; record `status/fixed-locally` when a committed, locally validated fix exists.
- Require merged PR before QA verification.
- Require post-merge main validation evidence before applying `status/merged-to-main`.
- Require QA evidence reference for `qa_failed` and `qa_passed_closed`.
- Keep all cycle updates in the same GitHub issue thread.
- Keep `status/*` labels mutually exclusive except when `status/blocked` is temporarily useful alongside a non-terminal state for triage.
