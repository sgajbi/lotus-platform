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
3. **Wiring** — the live comparison must run in a **blocking pre-merge lane**: per the Gate
   Liveness Standard's ordering rule, a verdict must arrive before the act it governs, and a
   scheduled-only run cannot stop a merge — drift could permit merges for up to a day before
   detection. A scheduled daily run is a useful supplement (it catches drift between PRs) but
   never the sole home. Offline document-shape checks (including that a zero-approval count
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
exists. In a multi-contributor repository, split the gate instead: run the PAT-authenticated
fetch-and-compare in a context the PR cannot rewrite (a push-to-`main` or scheduled lane, or a
`pull_request_target` job that checks out the base ref's checker), and keep the per-PR lane to
the tokenless offline shape checks. Fork and Dependabot PRs never receive the secret either way.

## Adoption record

- `lotus-gateway#737` — reference implementation: policy table, checker
  (`scripts/check_branch_protection_policy.py`), five offline unit tests, Quality Baseline step;
  documents the deliberate zero-approval exception (single accepted collaborator) with its
  compensating controls and retirement condition.
- `lotus-render#281` — verbatim lift, wired into the daily coverage-audit workflow; on adoption
  the gate immediately reported `required_pull_request_reviews block presence: live=ABSENT
  policy=present` — the exact undetected drift (`render#66`) that motivated the pattern — and
  stays red by design until an operator applies the remediation.
