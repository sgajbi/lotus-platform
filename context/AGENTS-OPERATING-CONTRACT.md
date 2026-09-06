# Lotus Agent Operating Contract

This is the governed operating contract for Lotus agent work.

Repo-root `AGENTS.md` files across Lotus repositories and the deployed local `AGENTS.md` should
remain synchronized copies of this file.

Use `automation/Sync-AgentOperatingContract.ps1` to synchronize or verify that deployed copy.

## Mandatory Reading Order

Before doing substantial work, load context in this order:

1. `AGENTS.md`
2. `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`
3. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
4. the target repository's `REPOSITORY-ENGINEERING-CONTEXT.md`
5. `lotus-platform/context/CONTEXT-REFERENCE-MAP.md`
6. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md` when the task is primarily about how work should be executed

Use the smallest correct working set. Do not load broad context blindly if the task is narrow.

## Target Repository Root Rule

Do not assume the inherited shell working directory is the task repository. VS Code multi-root
workspaces can start Codex in the first workspace folder, even when the user asks for another Lotus
repository.

Before substantial work:

1. infer the target repository from the user request, active goal, issue, PR, branch, file path, or
   explicit repo name,
2. if the target is a Lotus repository and the current working directory is a different Lotus
   repository, switch command `workdir` to that target repo before reading repo-local context,
   running tests, inspecting git state, editing files, or creating issues,
3. use `lotus-platform` only for central context, automation, platform contracts, skill source, and
   cross-repo governance unless the task explicitly targets `lotus-platform`,
4. for multi-repo work, state the active repo for each command group and never let one repo's
   `AGENTS.md` or `REPOSITORY-ENGINEERING-CONTEXT.md` stand in for another repo's local truth,
5. when delegating or launching background work, pass the exact repository name, absolute repo root,
   branch, read/write scope, and expected evidence so child agents do not inherit the wrong cwd.

If the inherited cwd conflicts with the named target repo, announce the correction briefly and keep
all subsequent repo-local commands anchored to the target repo.

## Mandatory Operating Rules

Always:

1. reduce complexity where possible,
2. improve readability, maintainability, and modularity as part of the slice,
3. make code and test improvements that materially improve reliability and maintainability,
4. update documentation when platform or repository truth changes,
5. leave the codebase cleaner than you found it,
6. write meaningful, high-value tests and avoid superficial coverage,
7. keep commits small, meaningful, and truthful,
8. remove dead code, duplicate logic, and stale non-standard handling when encountered,
9. ensure every UI feature is genuinely backed by supported backend functionality,
10. treat "merged to `main` and validated" as the definition of done; ensure
    RFC/docs/wiki/context/contract closure truth is present on `main`, not stranded on an
    unmerged side branch.

For RFC, documentation, wiki, context, contract, supported-features, API-governance, migration, or
CI-workflow changes, run stranded-truth reconciliation before starting implementation, before final
closure, and before moving to the next RFC:

1. `git fetch origin --prune`,
2. `git branch -r --no-merged origin/main`,
3. inspect unmerged branches that touch durable governance paths,
4. classify each as `must-merge`, `cherry-pick`, `superseded`, `delete`, or `active`,
5. merge, cherry-pick, explicitly supersede, or delete unique durable truth before claiming closure.

## Evidence And Guard Integrity

Each rule is carried with the case that produced it. A rule without its evidence reads as a
preference and gets dropped by the next person under time pressure.

### Never write file content through a shell heredoc

The shell rewrites backslash escapes before the interpreter sees the file: `\b` becomes 0x08,
`\f` 0x0c, `\e` 0x1b, `\t` a tab. Write the file with an editor tool, or write a patch script to
a file and run it by path.

Prose is the more consequential half, because nothing in Markdown rendering signals a problem. A
`lotus-report` guard compiled to `'\x08([A-Z][a-z]+)-only\x08'` and passed on the exact defect it
was written to catch; a `lotus-render` guard against source syntax reaching a client page could
never fire; and corruptions sit committed on `lotus-core` main where escapes ate the first letter
of real identifiers, so a review ledger names fields that do not exist.

Byte-scan before pushing. 0x08 renders invisibly, so reading the source cannot find it — only the
bytes or the compiled form can.

### Never pipe a gate through `tee` or `tail`

A pipeline exits with the status of its **last** command, so the gate's verdict is discarded and
the step reports success whatever it decided. `bash -e` does not catch it, because the pipeline
succeeded. Run the gate bare, or set `-o pipefail` before it, or capture `${PIPESTATUS[0]}` and
exit with it.

Six steps across two `lotus-gateway` workflows carried this shape, including `make test-coverage`
and `make security-audit`; one had been raising an exception under a green check since the day it
landed.

### Prove a guard can fail, after every edit

A guard is known-good only on the exact bytes you last proved it failing on. Run it against a
known-bad input and confirm it fails; passing on good input proves nothing. Cosmetic edits count —
a refactor or a rename is exactly when nobody re-checks, and that is when the `lotus-report`
corruption entered, after its original falsification.

### Test a guard against two shapes of its class, and assert what it must accept

A guard naming a class must be proved against at least two different shapes of that class. Three
separate narrowings in one day left holes of identical shape: a route detector that classified
`config.get(...)` as a route and exempted its arguments, a `-only` scan that caught the string
which prompted it and would have missed the same pattern in an adjacent field, and a pipeline
exclusion that read `echo "$(gate.py)" | tee log` as verdict-free.

Assert both directions. A classifier tested only on what it must reject can be widened until it
rejects everything — its own cases stay green while every legitimate input fails, broken in the
direction its tests never look.

### State a rule, then try to break it

Before recording a rule, name a case already in hand that would falsify it, and measure that case.
Four rules about a single CI failure died this way in one day, each refuted by a repository its
author had not sampled. Reasoning harder about the repositories already examined produced none of
those refutations.

### Lifted files are compared by blob SHA on committed refs

A file lifted verbatim between repositories is compared with `git rev-parse <ref>:<path>`, never by
hashing a working tree: a checkout may normalise line endings, and a tree can be repaired locally
while the merged state is still stale. Lift only from a canonical's **merged** state, never an open
pull request, and never edit the file on arrival — if a local formatter or type checker forces an
edit, fix the canonical instead.

A `lotus-render` checker sat 102 lines behind the canonical after two local annotations, so its
offline gate would have passed a policy gutted of required fields.

### `gh issue close --comment` discards the comment on an already-closed issue

The command succeeds and the evidence is silently dropped. Use `gh issue comment`, then verify the
comment count moved. Closure evidence was lost this way on issues in two repositories.

### Workflow-touching pull requests land single-commit

The merged-PR dispatcher creates one tag per revision so each gate run's head SHA is the revision.
That tag write is refused when the tagged commit's workflow tree differs from the default branch
tip's, so a multi-commit pull request that edits `.github/workflows` loses per-commit gating on its
intermediate commits.

Keep such a pull request to one commit, or make every workflow edit in the first commit and never
touch those files again in that pull request. State of evidence: this is a measured rule with
prospective confirmations, not a documented API behaviour, and four earlier explanations of the
same refusal were falsified. Treat it as a working rule, not a settled mechanism.

## Where Repository-Scoped Practice Lives

`AGENTS.md` is deployed identically to every repository from this contract and checked by
`automation/Sync-AgentOperatingContract.ps1 -CheckOnly`. Nothing repository-specific belongs in it:
editing one repository's copy forks a governed file.

Repository-scoped working practice — the hazards, conventions and command shapes that are true of
one repository and not the estate — belongs in that repository's
`REPOSITORY-ENGINEERING-CONTEXT.md`, under a section that names it as practice rather than
architecture. Every Lotus repository has that file and each owns its own copy, so it needs no new
convention and no synchronisation. `CLAUDE.md` is not the home for it: only one repository has one,
and it is read by a single agent runtime rather than all of them.

## Delivery Posture

Operate as a banking-grade engineer, not a generic coding assistant.

That means:

1. prefer truthful implementation over cosmetic output,
2. prefer reusable patterns over local hacks,
3. treat naming, contracts, tests, docs, and validation as part of the implementation,
4. use domain-correct private banking, portfolio, advisory, performance, and risk language.

## Skills, Automation, And Async Execution

When the task matches an available Lotus skill, use it.

Before choosing between overlapping Lotus skills, consult
`lotus-platform/context/LOTUS-SKILL-ROUTING-MAP.md`.

Prefer:

1. standards, validators, and runbooks before inventing a new pattern,
2. repo-native commands before ad hoc command sequences,
3. targeted local checks for quick proof,
4. GitHub-backed heavy execution for expensive full validation,
5. async monitoring and fix-forward work rather than blocking on long reruns.

For long-running, delegated, async, or context-compacted work, use
`lotus-platform/context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md`. Preserve operational
identifiers exactly, including repository, branch, PR number, commit SHA, check name, RFC id, file
path, endpoint, contract name, portfolio id, `engineering_task_id`, and task status. Treat
`output/background-runs.json` as local automation evidence and GitHub Actions as GitHub check truth.

For multi-agent delegation, use the governed profiles and envelopes in
`lotus-platform/platform-contracts/agent-engineering/delegation-policy-contract.v1.json`.
Delegate only bounded non-blocking work with explicit read scope, explicit write scope or `none`,
required evidence, and a required return envelope. Keep the main agent accountable for diff review,
integration, tests, PR posture, wiki publication, and final communication. Do not delegate broad
repo cleanup, immediate critical-path blockers, overlapping write scopes, PR merge, or wiki
publication unless the main agent explicitly owns and reviews the final action.

## Wiki Publication Rule

When documentation, RFC, context, runbook, or operator-facing truth changes:

1. update the repo-local `wiki/` source in the same PR when wiki truth changed,
2. record an explicit no-wiki-change decision when no wiki update is needed,
3. before merge, run
   `lotus-platform/automation/Sync-RepoWikis.ps1 -CheckOnly -Repository <repo-name> -AllowUnpublishedSourceChanges`
   when the branch intentionally changes repo-local `wiki/` source,
4. after merge to `main`, publish with
   `lotus-platform/automation/Sync-RepoWikis.ps1 -Publish -Repository <repo-name>`,
5. after publishing, run strict parity verification with
   `lotus-platform/automation/Sync-RepoWikis.ps1 -CheckOnly -Repository <repo-name>`,
6. use `-AllRepositories` only for platform-wide audits or coordinated publication sweeps.

Repo-local `wiki/` is the authored source of truth. The separate GitHub `*.wiki.git` repository is
only the publication target and must not receive hand-edited truth that is absent from repo source.

When a task is explicitly about canonical populated Workbench surfaces, demo screenshots, or
`PB_SG_GLOBAL_BAL_001`, choose `lotus-front-office-runtime` first and use broader QA or delivery
skills only as supporting guidance.

## Front-Office Runtime Routing Rule

When the task is about:

1. local front-office runtime bring-up,
2. populated Workbench screens,
3. panel validation,
4. demo screenshots,
5. canonical UI proof,

use the governed `lotus-workbench` runtime and validation flow first:

1. `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`
2. `npm run live:stack:up`
3. `npm run live:validate`
4. `npm run live:stack:down`
5. `lotus-platform/automation/Invoke-Canonical-FrontOffice-QA.ps1 -ScreenshotDirectory <path>` when the task needs platform-owned validation evidence and a caller-directed demo screenshot pack
6. `lotus-platform/context/contracts/canonical-front-office-demo-data-contract.json`
7. `lotus-platform/context/contracts/canonical-front-office-demo-data-invariants.json`

Use `PB_SG_GLOBAL_BAL_001` as the governed seeded front-office portfolio unless the task explicitly requires another dataset.

Treat the RFC-0076 contract files as the source of truth for canonical portfolio identity, benchmark
identity, governed as-of date, and minimum supportability thresholds. Runtime evidence should carry
contract provenance instead of relying on implicit repo convention.

Canonical platform QA includes `lotus-idea` by default. Do not reintroduce an opt-in flag or skip
`lotus-idea` readiness and teardown evidence unless the task explicitly asks for a diagnostic
partial run.

Do not treat `lotus-platform/platform-stack` as the canonical front-office product bring-up path. It owns shared ingress and infrastructure support, not the full governed product-surface flow.

Do not capture or share demo-ready screenshots before canonical API, calculation, and panel validation pass. If a pre-validation capture is necessary for diagnosis, label it with a `diagnostic-` prefix and keep it separate from demo evidence.

## Context Maintenance Rule

Keep the context system up to date as Lotus changes.

Update the relevant context artifacts when:

1. platform architecture changes,
2. repository responsibilities change,
3. canonical commands or validation flows change,
4. CI or governance expectations change,
5. a repeatable pattern should become durable guidance,
6. domain vocabulary or operating assumptions materially change.

If the change is platform-wide:

1. update the central context system in `lotus-platform/context/`.
2. update `LOTUS-SKILL-ROUTING-MAP.md` if task routing expectations changed.

If the change is repository-local:

1. update that repository's `REPOSITORY-ENGINEERING-CONTEXT.md`.

If both changed:

1. update both in the same slice.

## Cross-Links

Central context system:

1. `<lotus-platform>/context/LOTUS-QUICKSTART-CONTEXT.md`
2. `<lotus-platform>/context/LOTUS-ENGINEERING-CONTEXT.md`
3. `<lotus-platform>/context/CONTEXT-REFERENCE-MAP.md`
4. `<lotus-platform>/context/PROCEDURAL-MEMORY-INDEX.md`
5. `<lotus-platform>/context/LOTUS-SKILL-ROUTING-MAP.md`
6. `<lotus-platform>/context/lotus-context-manifest.json`
7. `<lotus-platform>/context/platform-engineering-ledger.md`
8. `<lotus-platform>/context/recent-architectural-decisions-digest.md`
9. `<lotus-platform>/docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md`
10. `<lotus-platform>/docs/onboarding/LOTUS-AGENT-RAMP-UP.md`

Repository-local context:

1. `REPOSITORY-ENGINEERING-CONTEXT.md` in the repository you are changing

When the central contract changes, keep both this source file and the deployed `AGENTS.md` synchronized.
