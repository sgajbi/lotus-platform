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
base-ref code isolation above is non-negotiable there. Publishing the isolated job only as a
named required status context does not by itself preserve that isolation: branch protection
matches checks by context name and creating app, and every Actions workflow shares one app, so
a PR-controlled workflow can emit a same-named check on the candidate SHA and satisfy the
requirement without the trusted job running. In the multi-contributor path, bind the gate to
workflow identity, not name — a repository ruleset "required workflows" entry pinning the
specific workflow file, or a check produced by a dedicated GitHub App with that App
recorded as the required check's expected source (`required_status_checks.checks[].app_id`)
— producing the check from the App without binding the source leaves the name-spoofing
path open — and record the binding in the policy table so its removal, on either the
protection or the ruleset surface, is a reported drift. Two mechanics make the
binding real. First, a `pull_request_target` job's own check suite attaches to the base tip
(`GITHUB_SHA`), while a required context is evaluated on the PR head, so the trusted job must
explicitly publish its verdict against the candidate head SHA
(`github.event.pull_request.head.sha`) through the checks or statuses API — otherwise the
required context simply never completes. That publication needs `statuses: write` or
`checks: write`, which the Workflow Security and Permissions Standard and its validator
restrict, so the permission grant is part of the same explicit approval as the
`pull_request_target` event itself — request both together, never add the write scope as an
unreviewed side effect. Second, the required-workflow binding lives in the
rulesets API, not the branch-protection endpoint, so when the policy table records such a
binding the checker must also read live rulesets and compare it — removing the ruleset rule
restores the spoofing path while the protection comparison stays green.

## One authority per field

`automation/repository-governance-policy.json` with `validate_repository_governance.py` is the
existing estate-wide authority, and its overlap with the repo-local table is nearly total: its
`expected_governance()` hardcodes not just per-repo required checks and strictness but
approvals, stale-review dismissal, conversation resolution, linear history, force-push and
deletion posture, and merge-method posture estate-wide. For **every** field both declare, the
central authority is authoritative and the repo-local table must match it — a disagreement
between the two is itself a finding, whichever file is stale. Any posture change, the
zero-approval retirement included, therefore updates the central policy or validator **and**
the repo-local table in one coordinated change; a repo-local edit alone leaves two authorities
contradicting each other. The central posture fields are currently estate-wide constants with
no per-repository override, so the first repository to diverge — the first retirement, for
example — must extend the central authority to per-repository posture values as part of that
same change; this is the concrete first step of the federated unification named below. The checker enforces this mechanically, not just editorially: for the
fields the central authority owns, the candidate table must equal the central declaration, so
a candidate edited to legitimize already-weakened live protection fails against the central
authority even though it matches live. What the repo-local pattern adds is only what the
central file does not carry: the review-authority prose, `documented_exceptions` with `retires_when`, bypass
allowances, CODEOWNERS posture, the blocking per-PR home, and the candidate-policy comparison.
An adopter copies the central declaration rather than re-deriving it; folding the two into one
federated authority is legitimate follow-up work, not something to duplicate silently in the
meantime.

## Bootstrapping a new or renamed required context

The base-ref-checker/candidate-policy split deadlocks a single PR that both introduces a context
and requires it, so roll out in three green steps: (1) merge the workflow change that emits the
new context, with neither live protection nor the policy table requiring it yet; (2) an operator
adds the context to live protection — from this moment until step 3 lands, the bidirectional
comparison on open PRs honestly reports the live addition as undocumented, so do (2) and (3)
adjacently and treat the brief red window as the drift-first transition rule in miniature; (3) merge the policy-table update listing the context, validated
against the now-matching live state. A rename is an addition followed by a removal in the same
order. The drift-first transition rule above covers the brief step-2 window.

## Adoption record

- `lotus-gateway#737` — reference implementation: policy table, checker
  (`scripts/check_branch_protection_policy.py`), five offline unit tests, Quality Baseline step;
  documents the deliberate zero-approval exception (single accepted collaborator) with its
  compensating controls and retirement condition.
- `lotus-render#281` — verbatim lift, wired into the daily coverage-audit workflow; on adoption
  the gate immediately reported `required_pull_request_reviews block presence: live=ABSENT
  policy=present` — the exact undetected drift (`render#66`) that motivated the pattern — and
  stays red by design until an operator applies the remediation.
