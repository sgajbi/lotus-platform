# Development Workflow

Current scope: the governed Platform delivery workflow, evidence requirements and feature-label
intake. Use the linked source profile for authorized label reconciliation; this page is operator
guidance and does not certify a repository or product.

| Reader | Start here |
| --- | --- |
| Requirement owner | [Feature scope and labels](#feature-scope-and-labels) |
| Delivery engineer | [Normal working loop](#normal-working-loop) and [Common commands](#common-commands) |
| Governance reviewer | [Stranded governance truth](#stranded-governance-truth) |

## Normal working loop

1. load the smallest correct context set
2. use repo-native commands first
3. run targeted local checks
4. reconcile stranded governance truth before RFC/docs/wiki/context/contract closure
5. push early for GitHub-backed heavy validation
6. monitor asynchronously and fix forward
7. update context, skills, or validators when learning becomes durable

## Stranded governance truth

Before RFC tightening, implementation start, final closure, post-merge audit, supported-feature
promotion, or moving to the next RFC:

```powershell
git fetch origin --prune
git branch -r --no-merged origin/main
```

Inspect unmerged branches that touch RFCs, wiki source, README, context, AGENTS, contracts,
standards, OpenAPI/vocabulary inventories, migrations, CI workflows, or supported-feature truth.
Classify each branch as `must-merge`, `cherry-pick`, `superseded`, `delete`, or `active`.

Do not claim RFC closure or product support while durable governance truth exists only on an
unmerged side branch.

For RFC-driven or proof-driven slices, keep a compact slice closure manifest in the PR, RFC ledger,
task ledger, or repo-local proof document. It should name blockers cleared, blockers preserved,
proof artifacts, commands, docs/wiki and supported-feature decisions, merge method, post-merge
validation, and branch cleanup evidence.

Before deleting a local or remote branch, verify that it is merged or explicitly superseded with PR
state plus `git log origin/main..<branch>`, `git diff origin/main..<branch>`, or cherry-pick
evidence. Branch cleanup is required, but code and durable truth preservation comes first.

## Feature scope and labels

Use the existing [issue-discovery feature-label profile](https://github.com/sgajbi/lotus-platform/blob/main/codex/skills/lotus-app-issue-discovery/references/campaign-playbook.md#canonical-feature-label-reconciliation)
to preview canonical metadata, reconcile only authorized catalogue scope and add single/shared
feature labels without removing legacy selectors or unrelated labels. Feature membership does
not prove issue closure, independent QA or product readiness; one shared change retains one
accountable implementation. Label writes and issue assignment require their own authorization.

## Common commands

```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane pr-merge
python -m pytest tests/unit -q
python automation/validate_engineering_context_system.py
python automation/validate_lotus_skill_alignment.py
```

## Documentation workflow rule

For `lotus-platform`, README and wiki changes are not free-form prose work. They must stay aligned
with:

- the current repo role and boundaries
- central context system cross-links
- onboarding and automation references
- documentation contract tests

Use:

- [Lotus Documentation Layering](https://github.com/sgajbi/lotus-platform/blob/main/docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Task Routing Guide](https://github.com/sgajbi/lotus-platform/blob/main/context/TASK-ROUTING-GUIDE.md)
- [Lotus Skill Routing Map](https://github.com/sgajbi/lotus-platform/blob/main/context/LOTUS-SKILL-ROUTING-MAP.md)

When the task is specifically README/wiki standardization across Lotus repos, use the governed
`lotus-readme-wiki-governance` workflow instead of treating the change as ordinary prose cleanup.

## Async GitHub posture

Prefer targeted local proof plus GitHub for the heavy matrix.

Useful commands:

```powershell
gh pr checks <pr-number> --watch=false
gh run list --limit 10
gh run view <run-id> --log-failed
```
