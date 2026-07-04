# Lotus App Issue-Discovery Campaign Playbook

Use this playbook when starting or resuming a Lotus defect-discovery campaign. It turns the skill
into an operating loop that a future agent can follow without prior chat context.

## Contents

1. [Start Or Resume](#1-start-or-resume)
2. [Pick The Next Lens](#2-pick-the-next-lens)
3. [Build A Lens Evidence Packet](#3-build-a-lens-evidence-packet)
4. [Inspect Code Like A Review Lead](#4-inspect-code-like-a-review-lead)
5. [Handle Active Fixes](#5-handle-active-fixes)
6. [File GitHub Issues](#6-file-github-issues)
7. [Update The Ledger Every Time](#7-update-the-ledger-every-time)
8. [Work In Time Boxes](#8-work-in-time-boxes)
9. [Report Progress To The User](#9-report-progress-to-the-user)
10. [Improve The Skill When Learning Repeats](#10-improve-the-skill-when-learning-repeats)
11. [Improve The Docs Knowledge Base When Standards Are Missing](#11-improve-the-docs-knowledge-base-when-standards-are-missing)

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

### No-Chat Recovery Packet

When resuming after compaction, handoff, or a fresh prompt, rebuild this packet before inspecting a
new finding:

- Target: local path, GitHub `owner/repo`, branch, dirty worktree files, and open PRs.
- Ledger: ledger issue number, latest ledger comments, covered lenses, blocked lenses, and
  remaining high-value lenses.
- Open defects: current open `issue-discovery` issues with labels, active assignee/PR if visible,
  and whether each lens is waiting for implementation.
- Standards: exact repo context, platform standard, docs KB page, RFC, or contract that governs the
  next lens.
- Evidence scope: source, tests, docs, contracts, workflows, migrations, or runtime artifacts that
  must be read before filing.
- Handoff decision: continue this app, wait for active fixes, or move to another app.

If the packet cannot be reconstructed, write the gap into the ledger and continue with the safest
bounded inspection. Do not infer coverage from old chat.

Use this quick command set at the start of a resumed campaign:

```powershell
git status --short --branch
gh issue list --repo <owner>/<repo> --state open --search "\"Issue Discovery Ledger\"" --json number,title,url
gh issue list --repo <owner>/<repo> --state open --label issue-discovery --limit 100 --json number,title,labels,url
gh pr list --repo <owner>/<repo> --state open --json number,title,headRefName,url
python <skill-dir>\scripts\plan_issue_discovery_campaign.py --repository <owner>/<repo>
```

If the worktree is dirty, identify whether the changed files overlap the next lens. If they do,
inspect the diff and mark the lens `Blocked By Active Fix` or `Needs Recheck` unless a distinct
root cause can be proven from stable files.

### Campaign Autopilot Rules

Use these rules when the user expects you to keep moving:

1. Do not ask which lens to run when the ledger already shows a sensible next lens.
2. Do not count issues as progress unless each issue has evidence, duplicate searches, labels, and
   implementation-ready acceptance criteria.
3. Do not leave a lens half-finished without a ledger comment naming what remains.
4. Do not mark a lens complete from a GitHub search alone; inspect representative code and a
   test/doc/contract/workflow counterpart.
5. Do not treat an active fix branch as stable truth. Inspect its diff, then mark the lens blocked,
   needs recheck, or file only distinct root causes.
6. Do not create cross-app or wrong-owner issues without an owner-boundary note.
7. Do not continue mining low-value issues after the ledger shows the app is waiting on
   implementation for the high-value lenses.

The default useful unit of work is one complete lens pass, not a fixed number of issues.

### One-Pass Execution Recipe

For a normal "continue" turn, complete this recipe before responding:

1. Rebuild state with `git status`, open issue-discovery issues, open PRs, and the ledger issue.
2. Select one primary lens and name any secondary lenses only as context.
3. Read the smallest repo/platform/docs KB sources that define the expected behavior.
4. Inspect source plus one counterpart artifact such as a test, contract, migration, workflow,
   README/wiki source, generated OpenAPI, or runtime proof.
5. Build the evidence packet and classify each candidate as new, duplicate, active-fix feedback,
   residual risk, or no issue.
6. Run duplicate searches with one broad lens query and one concrete symbol/file/query term.
7. Ensure labels, then create or reuse one issue per root cause.
8. Update the ledger with proof flags, issue numbers, inspected paths, searches, blockers,
   residual risk, and a continue/pause/recheck/move-app recommendation.

Do not stop after state discovery unless the repository target or GitHub access is blocked.

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

Avoid repeatedly mining the same area. If a lens already has one or more strong open issues and no
new distinct root cause is visible, mark the lens `Issues Raised` or `Needs Recheck`, then move to
the next ledger gap. The campaign goal is coverage of meaningful risk, not issue volume.

When a user asks for "next 5" or "next 10", treat the number as a ceiling. Choose a coherent lens
group, but stop early when the next candidate is duplicate-heavy, speculative, or too broad. Record
the stopped reason in the ledger so the user understands why more issues were not filed.

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
- Ledger outcome: whether this pass will mark the lens `Issues Raised`, `Covered For Now`,
  `Blocked By Active Fix`, `Needs Recheck`, or `ledger-only residual risk`.

Do not file if evidence or duplicate search is missing. Do not file style preferences, future product
ideas, or broad refactoring wishes without a specific failing behavior.

Before filing, ask this final gate:

1. Would a competent implementation agent know where to start?
2. Can the fix be merged as one coherent slice?
3. Can tests or contract checks prove it?
4. Would the issue still matter if the user did not ask for more issue count?

If any answer is no, refine, split, or ledger the candidate instead of filing.

For high-impact candidates, run this gold pass before opening the issue:

1. **Current-truth proof**: inspect current source plus a counterpart artifact such as tests,
   migrations, contracts, RFCs, wiki source, capability publication, OpenAPI output, runtime
   evidence, or generated proof. Do not file from source or docs alone when the finding is about a
   published capability.
2. **Stateful-workflow proof**: for workflows with state, decisions, side effects, or evidence,
   verify persistence owner, migration/table/collection posture, idempotency, replay, conflict,
   audit, lineage, restart, scale-out, concurrency, and recovery behavior.
3. **Owner-boundary proof**: state why this repository owns the fix, or why the issue is about this
   repository's publication/consumer contract rather than another app's source-owned domain.
4. **Runtime-support proof**: for production-risk issues, inspect runtime wiring, configuration,
   health/readiness, observability, operator diagnostics, and failure behavior enough to make the
   impact concrete.
5. **Fixability proof**: define the smallest implementation slice and tests needed for acceptance.
   If the fix is still a broad aspiration, ledger it as residual risk.

Use this issue outcome decision:

| Candidate State | Action |
| --- | --- |
| New root cause, strong evidence, fixable slice | File one GitHub issue |
| Same root cause already open | Reuse, link, or comment on the existing issue |
| Same root cause in active PR or branch | Comment there or mark the ledger blocked |
| Plausible but not yet proven | Ledger residual risk and inspect later |
| Product idea or style preference | Do not file |

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
python <skill-dir>/scripts/validate_issue_discovery_skill.py
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
- coverage posture: continue, pause for implementation, recheck after merge, or move app.

Also keep the ledger useful for the user:

- include approximate coverage such as `Covered/Issues Raised/Blocked/Needs Recheck/Not Started`;
- name the most important remaining lenses, not every low-value possibility;
- distinguish "issue filed" from "lens complete";
- identify which issues should be rechecked after the implementation agent merges fixes;
- record a no-issue pass when evidence was inspected and the current code met the bar.

Use status consistently:

- `Issues Raised`: findings exist, but the lens may still have residual review.
- `Covered For Now`: representative inspection, docs comparison, duplicate searches, and residual
  notes are complete for current campaign depth.
- `Blocked By Active Fix`: same area is changing now.
- `Needs Recheck`: evidence may be stale after a merge or broad fix.

Use this compact comment skeleton:

```markdown
### Lens pass: <Lens> - <YYYY-MM-DD>

- Status: <Covered For Now | Issues Raised | Blocked By Active Fix | Needs Recheck | ledger-only residual risk>
- Issues: #<new/reused issue numbers or none>
- Proof flags: Code:Y Docs:Y Dup:Y Labels:Y Ledger:Y
- Inspected:
  - `<path>`: <symbol/route/workflow>
- Standards consulted:
  - `<path/standard>`: <why it mattered>
- Duplicate searches:
  - `<query>`: <result>
- Active-fix blockers: <branch/PR/issue or none>
- Residual risk: <specific remaining risk or none>
- Recommendation: <continue this app | wait for fixes | recheck after merge | move app>
- Next suggested lens: <lens and reason>
```

### Move-App Decision

Recommend moving to another app when most high-value lenses are `Covered For Now`, `Issues Raised`
with implementation waiting, or `Blocked By Active Fix`, and the remaining lenses are low-value,
duplicate-heavy, or need runtime evidence that is not currently available. Recommend continuing
when unreviewed lenses still cover source-owned domain behavior, public API contracts, production
supportability, security/privacy, data lifecycle, performance hot paths, or release evidence.

When answering "are we done?", use this structure:

1. what the ledger proves is covered,
2. what open issue-discovery issues are waiting for implementation,
3. what active fixes block recheck,
4. what high-value lenses remain,
5. whether to continue, pause, or move apps.

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
- future agents need a new lens label to avoid forcing a distinct review class into a generic
  category.
- the user asks for a stronger reusable process and the current skill does not fully explain how to
  recover state, select lenses, file labels, update ledgers, or decide app handoff.

Update the source under `lotus-platform/codex/skills/lotus-app-issue-discovery`, validate it, commit
it, raise a PR, merge it, sync local skills, and return `lotus-platform` to clean `main`.

When the user asks to "make the skill powerful" or "make it work like you", improve the durable
workflow, not just prose. Check whether the change belongs in:

- `SKILL.md` for mandatory behavior and trigger-time instructions;
- `references/review-lenses.md` for lens, label, search, and evidence taxonomy;
- `references/lens-coverage-ledger-template.md` for campaign-state visibility;
- `references/campaign-playbook.md` for start/resume, active-fix, issue-count, handoff, and
  self-improvement procedure;
- `scripts/ensure_issue_discovery_labels.py` when labels change.
- `scripts/validate_issue_discovery_skill.py` when catalog, label script, or ledger consistency
  must be enforced.
- `scripts/plan_issue_discovery_campaign.py` when broad campaigns need a repeatable repo/profile
  lens queue and CI-hardening candidate hints.

Then run validation and sync so a fresh future agent can use the deployed skill without reading the
chat that caused the improvement.

## 11. Improve The Docs Knowledge Base When Standards Are Missing

Use the sibling `docs` repository as the durable knowledge base for reusable product, domain, and
technical learning. During issue discovery, update or propose KB improvements when the review
uncovers a knowledge gap that will matter across apps.

Create a separate KB-maintenance slice when:

1. the same defect pattern appears across more than one app and the docs KB lacks a clear standard;
2. an issue depends on domain knowledge that is not documented well enough for a fixing agent to
   implement correctly;
3. the docs KB has stale, duplicate, or weak guidance that future issues would cite;
4. a new lens needs a reusable checklist, worked example, vocabulary guide, or methodology note;
5. a product, lifecycle, transaction, position, data model, calculation, API, security,
   observability, testing, CI, or operations concept should become reusable learning material.

Do not put app-specific bug evidence into the docs KB. Keep current app evidence in GitHub issues,
ledgers, RFCs, repo context, README, wiki, tests, or implementation proof. The docs KB should teach
the general standard and reusable examples.

Use this routing:

- product/domain knowledge: `docs/docs/products/`;
- backend, API, data, CI/CD, infrastructure, observability, security, performance, testing,
  documentation, and SRE knowledge: `docs/docs/technical/`;
- wealth-platform architecture, operating model, strategy, and leadership context:
  `docs/docs/reference/`;
- prompt/agent workflow material: `docs/docs/prompts/`.

When filing an app issue that relies on a newly improved KB page, cite the KB page as the standard
and keep the issue body focused on current repository evidence. When the KB gap is real but outside
the current app issue-discovery scope, record it as ledger residual risk or create a separate docs
repo issue/PR according to the user's direction.

For skill-maintenance slices, include this proof pack in the PR or final note:

- skill files changed and why;
- whether `agents/openai.yaml` was updated because the trigger/default prompt changed;
- confirmation that the manifest changed only if a skill was added, removed, renamed, or moved;
- `python <skill-creator>/scripts/quick_validate.py codex/skills/lotus-app-issue-discovery`;
- `python automation/validate_lotus_skill_alignment.py`;
- `powershell -ExecutionPolicy Bypass -File automation/Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast -ValidateAfterSync`;
- source-to-local parity for `lotus-app-issue-discovery`;
- explicit no-wiki-change decision unless wiki source changed.

