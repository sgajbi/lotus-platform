# Issue Fix QA Loop State Machine

States:
- `dev_in_progress` (`status/in-progress`)
- `fixed_local` (`status/fixed-local`)
- `pr_raised` (`status/pr-open`)
- `merged_pending_qa` (`status/merged-main`)
- `qa_failed` (`status/blocked` when the failure blocks progress)
- `qa_passed_closed` (GitHub issue closed, with `status/merged-main` retained for filtering)

Transitions:
1. `dev_in_progress -> fixed_local`
2. `fixed_local -> pr_raised`
3. `pr_raised -> merged_pending_qa`
4. `merged_pending_qa -> qa_passed_closed`
5. `merged_pending_qa -> qa_failed`
6. `qa_failed -> dev_in_progress`

Rules:
- Never transition directly from `pr_raised` to `qa_passed_closed`.
- Never transition directly from `dev_in_progress` to `pr_raised`; record `fixed_local` when a committed, locally validated fix exists.
- Require merged PR before QA verification.
- Require QA evidence reference for `qa_failed` and `qa_passed_closed`.
- Keep all cycle updates in the same GitHub issue thread.
- Keep `status/*` labels mutually exclusive except when `status/blocked` is temporarily useful alongside a non-terminal state for triage.
