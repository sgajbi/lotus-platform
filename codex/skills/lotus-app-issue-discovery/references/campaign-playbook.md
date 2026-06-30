# Lotus App Issue-Discovery Campaign Playbook

Use this playbook when starting or resuming a Lotus defect-discovery campaign. It turns the skill
into an operating loop that a future agent can follow without prior chat context.

## 1. Start Or Resume

1. Resolve the target repository from the user request, current working directory, or latest active
   ledger.
2. Run `git status --short --branch` in the target repo and identify user or agent changes that
   must not be touched.
3. Read the mandatory context in the order required by the repo `AGENTS.md`.
4. Read the target repo `REPOSITORY-ENGINEERING-CONTEXT.md` to confirm the app's source-of-truth
   responsibility and non-ownership boundaries.
5. Find the app ledger issue:
   `gh issue list --repo <owner>/<repo> --state open --search "\"Issue Discovery Ledger\"" --json number,title,url`
6. If no ledger exists, create `<repo> Issue Discovery Ledger` using
   `references/lens-coverage-ledger-template.md`.
7. Read the ledger comments or table before choosing a lens. Do not rely on chat memory.

Use this quick command set at the start of a resumed campaign:

```powershell
git status --short --branch
gh issue list --repo <owner>/<repo> --state open --search "\"Issue Discovery Ledger\"" --json number,title,url
gh issue list --repo <owner>/<repo> --state open --label issue-discovery --limit 100 --json number,title,labels,url
gh pr list --repo <owner>/<repo> --state open --json number,title,headRefName,url
```

If the worktree is dirty, identify whether the changed files overlap the next lens. If they do,
inspect the diff and mark the lens `Blocked By Active Fix` or `Needs Recheck` unless a distinct
root cause can be proven from stable files.

## 2. Pick The Next Lens

Choose the next lens using this order:

1. user's explicit lens or requested issue category,
2. active ledger gaps marked `In Review`, `Needs Recheck`, or `Blocked By Active Fix` whose blocker
   has merged,
3. baseline queue in `references/review-lenses.md`,
4. highest-value adjacent lens revealed by recent defects.

Prefer a complete lens pass over a larger issue count. A complete pass includes source inspection,
docs or standards comparison, duplicate checks, labels, issue creation or no-issue decision, and a
ledger update.

## 3. Build A Lens Evidence Packet

For every candidate finding, assemble this packet before filing:

- Lens and canonical `lens/*` label.
- Standard: docs KB page, platform standard, repo context, RFC, contract, public standard, or accepted
  domain practice.
- Evidence: exact files, symbols, routes, contracts, migrations, workflows, tests, or runtime output.
- Impact: correctness, security, operability, performance, architecture, supportability, or domain
  consequence.
- Duplicate searches: broad lens terms and concrete symbol terms across open and closed issues.
- Fix direction: smallest coherent implementation slice.
- Acceptance criteria: tests, contract checks, docs/context updates, runtime proof, or gate evidence.
- Owner boundary: why this repository owns the fix, or why this is an integration/publication
  contract issue rather than a wrong-owner domain issue.

Do not file if evidence or duplicate search is missing. Do not file style preferences, future product
ideas, or broad refactoring wishes without a specific failing behavior.

Before filing, ask this final gate:

1. Would a competent implementation agent know where to start?
2. Can the fix be merged as one coherent slice?
3. Can tests or contract checks prove it?
4. Would the issue still matter if the user did not ask for more issue count?

If any answer is no, refine, split, or ledger the candidate instead of filing.

## 4. Inspect Code Like A Review Lead

Use `rg` first, then open files. A strong pass normally touches:

1. delivery/runtime entry point,
2. domain or application path,
3. adapter, repository, client, workflow, middleware, or migration when relevant,
4. tests or the absence of tests,
5. README, wiki source, RFC, API contract, workflow, or operational docs when truth is affected.

Use docs repo knowledge as a standard, not decoration:

- `docs/docs/products/` for product, transaction, position, lifecycle, instrument, cash-flow,
  source-ownership, and calculation lenses.
- `docs/docs/technical/` for architecture, API, data products, CI/CD, runtime, observability,
  security, performance, testing, documentation, DevOps, and SRE lenses.
- `docs/docs/reference/` for wealth platform architecture, operating-model, and domain-engineering
  lenses.

If a repo's responsibility does not include the domain being inspected, do not create wrong-owner
issues. Instead, ledger the boundary and inspect the integration contract.

Prefer current source-owned evidence over generated artifacts. Use generated OpenAPI, catalogs,
scorecards, proof files, or output evidence only when those artifacts are the consumer-facing or
operator-facing contract under review.

## 5. Handle Active Fixes

When another agent has an active branch, PR, or dirty worktree in the same area:

1. inspect the diff before relying on older evidence,
2. search for the owning issue or PR,
3. comment on that issue or PR if the gap is within the active fix's acceptance criteria,
4. file a new issue only for a distinct root cause,
5. mark the lens `Blocked By Active Fix` or `Needs Recheck` when stable evidence depends on the
   active work landing.

Never edit or revert active fix files during issue discovery.

## 6. File GitHub Issues

Before creating issues:

```powershell
python <skill-dir>/scripts/ensure_issue_discovery_labels.py --repo <owner>/<repo>
```

Create one issue per root cause:

```powershell
gh issue create --repo <owner>/<repo> `
  --title "<specific failing behavior>" `
  --body-file <body.md> `
  --label "issue-discovery" `
  --label "lens/<canonical-label>" `
  --label "impact/<primary-impact>"
```

Use exactly one primary `lens/*` label unless the repository has a stricter convention. Mention
secondary lenses in the issue body.

Use these title patterns:

- `Add <missing control> for <specific route/workflow/model>`
- `Move <leaking responsibility> out of <layer> into <target layer/port>`
- `Enforce <domain/contract rule> for <lifecycle/calculation/publication path>`
- `Make <diagnostic/evidence/capability> reproducible from <runtime/source>`

Avoid titles like `Improve architecture`, `Fix observability`, or `Clean up code`.

## 7. Update The Ledger Every Time

After every lens pass, add a compact ledger comment with:

- lens and status,
- issue numbers created or reused,
- proof flags: `Code`, `Docs`, `Dup`, `Labels`, `Ledger`,
- code and docs inspected,
- duplicate search queries and result summary,
- active-fix blockers,
- residual risk,
- next suggested lens.
- recommendation: continue this app, wait for active fixes, or move to another app.

Use status consistently:

- `Issues Raised`: findings exist, but the lens may still have residual review.
- `Covered For Now`: representative inspection, docs comparison, duplicate searches, and residual
  notes are complete for current campaign depth.
- `Blocked By Active Fix`: same area is changing now.
- `Needs Recheck`: evidence may be stale after a merge or broad fix.

## 8. Work In Time Boxes

If the user gives a time box:

1. choose lenses that can be completed within the time,
2. avoid starting broad archaeology near the end,
3. file fewer but stronger issues,
4. ledger partial findings as residual risk,
5. report what is complete, what is blocked, and what should happen next.

## 9. Report Progress To The User

Keep updates concise:

- current lens,
- context or code being inspected,
- whether a finding is becoming issue-worthy,
- issue numbers and ledger updates when filed,
- next lens suggestion.

When asked "are we done?", answer with:

- lenses covered,
- open issues raised from the campaign,
- active-fix blockers,
- remaining high-value lenses,
- recommendation to continue or move to another app.

Use the ledger, not memory, to answer coverage questions. Include approximate completion only as a
ledger-backed statement such as "12 of 33 lenses have a completed or issue-raised pass; 4 are
blocked by active fixes; the remaining high-value lenses are X, Y, Z."

## 10. Improve The Skill When Learning Repeats

Promote learning into the platform-owned skill when any of these recur:

- a new lens or label is needed,
- duplicate checks missed a class of issue,
- ledger status or proof flags are insufficient,
- agents file broad issues without implementation-ready acceptance criteria,
- docs KB anchors should be mandatory for a lens,
- GitHub issue labels or ledger behavior are inconsistent across apps.
- a Lotus-specific review area keeps being forced into a generic label, such as capability
  publication or evidence/proof contracts.
- agents need the same GitHub issue searches, issue-body structure, or ledger fields repeatedly.

Update the source under `lotus-platform/codex/skills/lotus-app-issue-discovery`, validate it, commit
it, raise a PR, merge it, sync local skills, and return `lotus-platform` to clean `main`.

