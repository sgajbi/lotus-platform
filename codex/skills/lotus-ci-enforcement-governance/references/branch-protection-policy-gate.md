# Branch Protection Policy Gate

Live branch protection is configuration that nothing exercises: if `enforce_admins`, required
contexts, or conversation resolution were silently weakened, every merge would still look normal.
An undocumented protection exception is indistinguishable from a misconfiguration, and a policy
document that outlives the configuration it describes is worse than none. This pattern turns the
delivery-control posture into a daily-asserted fitness function.

## Contents

1. [Shape](#shape)
2. [Token requirement and trust boundary](#token-requirement-and-trust-boundary)
3. [One authority per field](#one-authority-per-field)
4. [Bootstrapping a new or renamed required context](#bootstrapping-a-new-or-renamed-required-context)
5. [Adoption record](#adoption-record)

## Shape

One declarative policy table plus one lifted checker; the table is the only repository-specific
input, so a sibling adopts the script and test verbatim and edits the table. A lift is a copy,
and copies drift: the canonical implementation lives with the reference adopter
(`lotus-gateway`'s `scripts/check_branch_protection_policy.py` and its unit tests) until the
checker moves into `lotus-platform` with the federated unification named below, and each
adopter's scheduled supplement performs a parity check — fetch the canonical file at `main`,
compare content hashes, fail on divergence — so a checker fix propagates deliberately to every
adopter instead of silently forking an estate-wide control. The lift delivers
the **implemented baseline** only: the table, the live field-by-field comparison, the offline
shape tests, and the wiring and token rules below. The central-comparison, re-evaluation,
ruleset-binding, and checker-parity mechanics in this reference are **specified extensions**
with no canonical implementation anywhere yet — an adopter gains the anti-drift baseline and must not claim the
anti-spoofing or freshness guarantees until those extensions land.

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
Authenticate with a repository PAT secret carrying `administration: read` and fail closed when
it is missing or unauthorized; a silent pass without the token is the gate-liveness violation
this reference exists to prevent. **Provisioning that secret is an explicit adoption
prerequisite, not an assumption**: measured on 2026-09-06, no Lotus repository holds any Actions,
Dependabot, or environment secret, so an adoption that assumes an existing automerge PAT wires a
step that can never authenticate. Confirm the secret exists in the adopting repository before
declaring the gate live.

Wiring the step is itself a gate-liveness surface. The checker's exit code must reach the step's
exit code: a step written as `python check_branch_protection_policy.py | tee log.txt` reports the
exit status of `tee`, so the checker can raise on every run while the step stays green. Run the
checker bare, or capture `${PIPESTATUS[0]}` under `set -o pipefail` and exit with it. This is not
hypothetical — the reference implementation shipped with the piped form and was fail-open from
the day it landed until 2026-09-06, its traceback visible in every run beneath a green check.

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
workflow identity, not name — a "required workflows" rule, which GitHub configures through an
organization ruleset (repository-level rulesets do not offer it, so organization
administration access is part of this adoption ask), pinning the specific workflow file, or a check produced by a dedicated GitHub App with that App
recorded as the required check's expected source (`required_status_checks.checks[].app_id`)
— producing the check from the App without binding the source leaves the name-spoofing
path open, and the central `Enforce-Repository-Governance.ps1` apply path must be extended to
write the checks-with-`app_id` shape before this option is adopted, or its next apply strips
the binding — and record the binding in the policy table so its removal, on either the
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
existing estate-wide authority, and its overlap with the repo-local table is nearly total: the
authoritative field set is whatever `expected_governance()` and the
`Enforce-Repository-Governance.ps1` apply path declare — read them rather than trusting any
enumeration here, since the set includes per-repo required checks, strictness, approvals,
stale-review dismissal, conversation resolution, linear history, force-push/deletion and
merge-method posture, and grows with the enforcer. For **every** field both declare, the
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
authority even though it matches live. The central input is obtained by fetching the central
declaration from the platform repository at `main` at check time (the branch-protection PAT
already reads it), failing closed when unreachable — never a vendored copy, which would be a
second authority going stale, the exact defect this section forbids. Two prerequisites gate the
implementation. First, `repository-governance-policy.json` today carries only repositories,
branches, and required checks — the posture constants are hard-coded in `expected_governance()`
and the enforcer — so the first implementer must lift those constants into the central JSON
(with validator and enforcer reading them from it) rather than duplicate them into yet another
authority. Second, a completed sibling verdict is not invalidated by a later central change:
GitHub does not re-run finished checks, so an open PR validated against the old declaration
keeps its green and can still merge. Floating `main` therefore converges legitimately
coordinated changes (central merges before the repo-local table) but does not police that
window — the platform must dispatch a re-evaluation of open adopter PRs when the central
declaration changes (`repository_dispatch` or equivalent), with the scheduled supplement as the
post-merge backstop. The same staleness applies to every comparison input: a verdict binds live
protection, the central declaration, and the candidate table at evaluation time, and GitHub
never revokes a finished check, so an operator weakening live protection after a candidate went
green leaves that candidate mergeable against the old state. Police this with a workflow on the
`branch_protection_rule` event (created/edited/deleted) that re-runs the comparison for every
open candidate, so a live edit invalidates stale greens within minutes instead of at the next
scheduled run. That event covers repository branch-protection rules only: an organization
ruleset edit — which can silently remove the required-workflow identity binding and reopen the
name-spoofing path — emits the `repository_ruleset` webhook, which is not an Actions trigger.
Where that binding is in use, wire an organization webhook receiver that forwards ruleset
changes as `repository_dispatch` re-evaluations, or — in an estate with no receiver — couple
the ruleset-editing runbook to firing that dispatch by hand, with the scheduled supplement
(which re-reads rulesets) as the bounded-delay backstop. Neither current adopter implements this comparison yet — it is
a specified extension each adopter owes, not something to claim as enforced before it lands. What the repo-local pattern adds is only what the
central file does not carry: the review-authority prose, `documented_exceptions` with `retires_when`, bypass
allowances, CODEOWNERS posture, the blocking per-PR home, and the candidate-policy comparison.
An adopter copies the central declaration rather than re-deriving it; folding the two into one
federated authority is legitimate follow-up work, not something to duplicate silently in the
meantime.

## Bootstrapping a new or renamed required context

The base-ref-checker/candidate-policy split deadlocks a single PR that both introduces a context
and requires it, so roll out in ordered steps: (1) merge the workflow change that emits the
new context — for a sibling adopter this lands first, because the platform enforcer's
source-only validation requires the adopter's default branch to already emit any newly declared
check; live protection and the repo-local table do not require the context yet; (1b) merge the
central `repository-governance-policy.json` addition in the platform repository — before the
repo-local update, which under mechanical centrality cannot merge while the central declaration
still lists the old checks (within the platform repository itself, 1 and 1b can be one merge);
(2) an operator
adds the context to live protection — the comparison on open PRs now also reports the live
addition as undocumented; (3) merge the policy-table update listing the context, validated
against the now-matching live state. The red window spans (1b) through (3), not just step 2:
once the central comparison and its re-evaluation dispatch are implemented, (1b) itself reddens
every open candidate whose table does not yet list the new context — so do those steps
adjacently, coordinate open PRs for the outage, and treat the window as the drift-first
transition rule in miniature. A rename is an addition (steps 1-3) followed by a removal in the **reverse**
order: the central policy drops the old context first — while it stays centrally required, the
local-table removal cannot pass the central comparison, and the central Apply would re-add
whatever an operator removed — then the operator drops it from live protection, the policy-table
update removing it merges next, and only then does the workflow stop emitting it — stopping
emission while the context is still required would block every PR. The drift-first transition rule above covers the brief step-2 window.

## Adoption record

Both adoptions implement the baseline; none of the specified extensions are implemented yet.
Neither adoption has ever completed a live comparison: the PAT the checker needs exists in no
Lotus repository (measured 2026-09-06), so the live step cannot authenticate anywhere until an
operator provisions it.

- `lotus-gateway#737` — reference implementation: policy table, checker
  (`scripts/check_branch_protection_policy.py`), five offline unit tests, Quality Baseline step;
  documents the deliberate zero-approval exception (single accepted collaborator) with its
  compensating controls and retirement condition. Its Quality Baseline step piped the checker
  through `tee`, so from landing until the follow-up fix the step reported success while the
  checker raised `CalledProcessError` on an empty `GH_TOKEN` — wired blocking, but unable to
  fail. Treat it as the worked example of both defects above, not as a clean template.
- `lotus-render#281` — verbatim lift, wired into the daily coverage-audit workflow and invoked
  bare, so its exit code is honest. The drift it reported (`required_pull_request_reviews block
  presence: live=ABSENT policy=present` — the exact undetected `render#66` drift that motivated
  the pattern) came from a local run against live protection; the CI step had not yet executed
  as of 2026-09-06, and will fail closed on the absent PAT when it does.
