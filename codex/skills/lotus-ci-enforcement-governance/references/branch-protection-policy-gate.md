# Branch Protection Policy Gate

Live branch protection is configuration that nothing exercises: if `enforce_admins`, required
contexts, or conversation resolution were silently weakened, every merge would still look normal.
An undocumented protection exception is indistinguishable from a misconfiguration, and a policy
document that outlives the configuration it describes is worse than none. This pattern turns the
delivery-control posture into a daily-asserted fitness function.

## Shape

One declarative policy table plus one lifted checker; the table is the only repository-specific
input, so a sibling adopts the script and test verbatim and edits the table.

1. **Policy table** — `quality/branch_protection_policy.v1.json` at the repository root (the
   checker resolves `quality/` relative to itself; keep that convention). It records:
   - every protection field the repository asserts (`enforce_admins`, strict contexts and their
     exact names, linear history, force-push/deletion posture, conversation resolution,
     `required_pull_request_reviews` including `bypass_pull_request_allowances`, restrictions,
     CODEOWNERS presence);
   - the review authority in prose: who the review lead is, what an exact-head
     `VERDICT: mergeable` means, and the escalation path;
   - `documented_exceptions` — the load-bearing part. Each deliberate deviation carries `field`,
     `value`, `reason`, `compensating_controls`, and `retires_when`. An exception without a
     retirement condition is a permanent weakness wearing a label.
2. **Checker** — compares live protection against the table field by field and fails in **both**
   drift directions: when protection weakens, and when exception text is removed without the
   configuration strengthening. Absent settings compare as absent, never coerced to false: a
   missing `required_pull_request_reviews` block and a present
   `required_approving_review_count: 0` are different postures and the output must say `ABSENT`.
   Bypass allowances are asserted (an empty list is an assertion, not an omission). CODEOWNERS is
   checked across all three recognized locations (root, `.github/`, `docs/`).
3. **Self-anchoring and its residual** — name the gate's own status context in the policy's
   required-contexts list, so removing it is itself a policy violation the comparison reports.
   That anchor has a residual by construction: once the context is removed from live protection,
   the job still fails but GitHub no longer requires the failure, so the pre-merge block cannot
   stop the exact weakening that removes it. The scheduled supplement exists precisely for this
   residual — it detects the removal within a day — so where this residual matters the
   supplement is not optional, and the audit log of protection changes is the backstop.
4. **Wiring** — the live comparison must run in a **blocking pre-merge lane**: per the Gate
   Liveness Standard's ordering rule, a verdict must arrive before the act it governs, and a
   scheduled-only run cannot stop a merge — drift could permit merges for up to a day before
   detection. A scheduled daily run is a useful supplement (it catches drift between PRs) but
   never the sole steady-state home. One transition state is legitimate: an adoption that begins
   from known drift — exactly when adoption is most valuable — may keep the live comparison
   scheduled-only while the policy states the target posture, provided the blocking pre-merge
   step is a committed, tracked follow-up for the moment the drift remediation lands; a blocking
   live step before then would deadlock every PR on an operator action. The defect is a live gate
   with no blocking home and no such commitment. Offline document-shape checks (including that a
   zero-approval count
   cannot lose its documented exception) run in the repo-native unit gate so the table itself
   cannot rot.

## Token requirement and trust boundary

The workflow `github.token` cannot carry `administration: read`, which the branch-protection
endpoint requires — a step wired to it fails everywhere or, worse, is skipped into a dead gate.
Authenticate with a repository PAT secret (the automerge PAT already present in Lotus repos
qualifies) and fail closed when it is missing or unauthorized; a silent pass without the token is
the gate-liveness violation this reference exists to prevent.

The PAT defines a trust boundary that must be stated, not assumed: a per-PR lane executes the
PR's own checkout, so the checker script — and for same-repository PRs the workflow file itself —
is PR-controlled code running with the secret. That is acceptable only where every same-repo
pusher is already trusted with the PAT's full authority, which holds in the current Lotus
single-accepted-collaborator repositories and must be re-evaluated the moment a second pusher
exists. In a multi-contributor repository, split the gate while keeping the live comparison
**pre-merge** — moving it to a push-to-`main` or scheduled lane would recreate the ordering
defect this reference forbids. The isolated pre-merge shape is a `pull_request_target` job that
checks out the **base ref's checker code** (never the PR's) and holds the PAT, published as a
required context, with the per-PR lane keeping the tokenless offline shape checks. The policy
table, unlike the checker, is read from the **PR head as inert data**: code isolation is about
execution, and the candidate policy is what the merge would make true — comparing live state
against the base's old table would let a policy change merge unvalidated in either direction. Adding
any `pull_request_target` workflow requires the explicit approval that
`platform-standards/Workflow-Security-and-Permissions-Standard.md` mandates — it is prohibited
by default and allowed only for approved, narrowly constrained workflow files — so treat that
approval as part of the adoption, not an implementation detail. Two actor classes need explicit
handling before the secret-backed context becomes required. Dependabot-triggered runs draw from
the separate Dependabot secrets store, so mirror the PAT there or every dependency update
becomes unmergeable against the fail-closed check. Fork PRs stay on the isolated path: a
`pull_request_target` job runs the base branch's workflow and checker with repository secrets
available even for fork-originated runs (the no-secrets rule applies to plain `pull_request`
execution), subject to GitHub's first-time-contributor approval gates — which is exactly why the
base-ref code isolation above is non-negotiable there.

## Adoption record

- `lotus-gateway#737` — reference implementation: policy table, checker
  (`scripts/check_branch_protection_policy.py`), five offline unit tests, Quality Baseline step;
  documents the deliberate zero-approval exception (single accepted collaborator) with its
  compensating controls and retirement condition.
- `lotus-render#281` — verbatim lift, wired into the daily coverage-audit workflow; on adoption
  the gate immediately reported `required_pull_request_reviews block presence: live=ABSENT
  policy=present` — the exact undetected drift (`render#66`) that motivated the pattern — and
  stays red by design until an operator applies the remediation.
