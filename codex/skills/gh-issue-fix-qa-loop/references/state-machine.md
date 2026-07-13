# Issue Fix QA Loop State Machine

## Contents

1. Lifecycle states
2. Transitions
3. Evidence gates
4. Invariants

## Lifecycle States

| State | Default label | Issue posture |
| --- | --- | --- |
| `dev_in_progress` | `status/in-progress` | Open |
| `fixed_local` | `status/fixed-local` | Open |
| `pr_raised` | `status/pr-open` | Open |
| `merged_pending_main_validation` | `status/in-progress` | Open; merge is not closure proof |
| `merged_main` | `status/merged-main` | Open pending QA or closed after QA |
| `blocked` | `status/blocked` | Open |
| `qa_failed` | `status/in-progress` | Open or reopened |
| `qa_passed_closed` | retain `status/merged-main` | Closed |

QA states deliberately do not introduce `status:qa-*` labels. QA evidence composes with mainline
truth instead of replacing it.

## Transitions

1. `dev_in_progress -> fixed_local`
2. `fixed_local -> pr_raised`
3. `pr_raised -> merged_pending_main_validation`
4. `merged_pending_main_validation -> merged_main`
5. `merged_main -> qa_passed_closed`
6. `merged_main or qa_passed_closed -> qa_failed -> dev_in_progress`
7. any non-terminal state may become `blocked`; resume at `dev_in_progress`

## Evidence Gates

- `fixed_local`: commit SHA and local validation reference.
- `pr_raised`: GitHub reports the PR as open.
- `merged_pending_main_validation`: GitHub reports the PR as merged and its merge commit matches the
  supplied main SHA.
- `merged_main`: the merged-PR check plus successful primary and security or
  repository-equivalent workflow runs whose `headSha` equals the supplied main SHA, an explicit
  wiki publication/no-change decision, and branch-cleanup evidence.
- `qa_failed`: QA evidence and an expected-versus-actual summary.
- `qa_passed_closed`: QA evidence and an existing merged-main label.

## Invariants

- Validate repository labels before mutation; never create labels implicitly.
- Remove every configured state label and alias when transitioning.
- Never close directly from an active, fixed-local, PR-open, blocked, or pending-main state.
- Never describe merged code as merged-main until exact-main proof passes.
- Closed issues cannot retain active labels; open issues cannot carry terminal merged-main labels.
- Keep every retry and evidence update in the canonical issue thread.
