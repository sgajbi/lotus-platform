# Issue Fix QA Loop State Machine

States:
- `dev_in_progress`
- `pr_raised`
- `merged_pending_qa`
- `qa_failed`
- `qa_passed_closed`

Transitions:
1. `dev_in_progress -> pr_raised`
2. `pr_raised -> merged_pending_qa`
3. `merged_pending_qa -> qa_passed_closed`
4. `merged_pending_qa -> qa_failed`
5. `qa_failed -> dev_in_progress`

Rules:
- Never transition directly from `pr_raised` to `qa_passed_closed`.
- Require merged PR before QA verification.
- Require QA evidence reference for `qa_failed` and `qa_passed_closed`.
- Keep all cycle updates in the same GitHub issue thread.
