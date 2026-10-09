# PR metadata enforcement

Platform owns `automation/validate_pr_metadata.py`. It accepts only repository identities already
registered in `automation/repos.json`; the registry's machine-local path is never used for command
resolution. All registered UI, backend, shared-service and Platform profiles use this same shared
capability. Unknown profiles fail closed. Additional application-native gates remain required when
declared by that repository and present; this shared command does not replace them.

## Text contract

Require a nonempty single-line title, nonempty body, an issue reference and exactly one declaration:

```text
Related issue: #609
Remaining acceptance: Keep #609 open for the remaining programme slices.
Intended closures: none
```

For intentionally authorized completion, use a comma-space-separated list and one affirmative
standalone closing line per issue:

```text
Intended closures: #123, sgajbi/lotus-archive#456
Closes #123
Resolves sgajbi/lotus-archive#456
```

Supported references are `#123`, `sgajbi/lotus-archive#456`, and full GitHub issue URLs. References
must identify registered repositories. The declaration records the delivery owner's explicit
intended set; it does not prove acceptance criteria, authorize programme closure, or replace issue
evidence. Empty declarations, duplicate declarations and contradictory closure lines fail.

Candidate policy conservatively rejects closing-keyword/reference lines unless they are exactly
`Closes`, `Fixes` or `Resolves` followed by one authorized reference. This includes negated wording,
quoted/fenced examples and mixed prose. Archive PR190's negative wording for issue188 and
Performance PR639's negative wording for issue609 are regression fixtures. Use neutral related-issue
and remaining-acceptance wording instead. Offline parsing makes no claim about GitHub's parser.

## Invocation from an application checkout

Set `LOTUS_WORKSPACE_ROOT` to the directory holding the checkouts. The working directory is the
target application repository. Save the exact candidate body as UTF-8 (a BOM is accepted) using
the editor. Set the title, repository identity, body path, PR number and expected head to the actual
task values. The absolute validator path is resolved from Platform, never from the application's
`automation/` directory.

PowerShell, from the target application checkout:

```powershell
$metadataGate = (Resolve-Path "$env:LOTUS_WORKSPACE_ROOT/lotus-platform/automation/validate_pr_metadata.py").Path
$targetRepo = 'sgajbi/lotus-workbench'
$env:LOTUS_PR_TITLE = 'Bounded delivery slice'
$bodyPath = (Resolve-Path './pr-body.txt').Path
python $metadataGate --repo $targetRepo candidate --title-env LOTUS_PR_TITLE --body-file $bodyPath
if ($LASTEXITCODE -ne 0) { throw 'Candidate metadata rejected' }
# Only now create/edit the PR or push its head, with this exact title and body.
# After mutation, set $prNumber and $expectedHead to the actual PR and full head SHA.
python $metadataGate --repo $targetRepo live --pr $prNumber --expected-head $expectedHead
if ($LASTEXITCODE -ne 0) { throw 'Live metadata evidence rejected' }
```

Bash, from the target application checkout:

```bash
metadata_gate="$LOTUS_WORKSPACE_ROOT/lotus-platform/automation/validate_pr_metadata.py"
target_repo=sgajbi/lotus-workbench
export LOTUS_PR_TITLE='Bounded delivery slice'
body_path="$PWD/pr-body.txt"
python "$metadata_gate" --repo "$target_repo" candidate --title-env LOTUS_PR_TITLE --body-file "$body_path" || exit $?
# Only now create/edit the PR or push its head, using the exact checked text.
# After mutation, set pr_number and expected_head to the actual PR and full head SHA.
python "$metadata_gate" --repo "$target_repo" live --pr "$pr_number" --expected-head "$expected_head" || exit $?
```

Re-run live immediately before merge. Use authenticated `gh` with repository/issue read access;
never print authentication material. Live mode reads current title/body/head/base/state/update
identity on every page, requires complete pagination and count reconciliation, then re-reads
identity. Missing capability, partial GraphQL results, API failure, unknown repositories,
non-progressing cursors, changed metadata and unintended actual references all fail closed. It
prints identity hashes and reference sets, not body text or subprocess diagnostics. An old workflow
event body cannot substitute for current evidence.

## Enforcement and boundaries

| Surface | Enforcement |
| --- | --- |
| Candidate mode | Offline local precondition in governed premerge instructions, before PR creation/edit/head push; no GitHub evidence. |
| Platform Pull Request Merge Gate | Live check inside the existing required `PR Merge Gate / Platform Repo Contracts` job, before the repository suite. `edited` events refresh metadata checks. |
| Platform feature/PR/main repository suite | `Invoke-PlatformRepoChecks.ps1` collects `tests/unit`, including metadata good/bad, transport and wiring regressions. Feature/main runs do not certify a live open PR. |
| Application CI | Unchanged by this central slice; application owners must adopt current-live metadata checks in their required lanes. |

The current-live check binds the source head from the triggering event and refuses a newer head.
Metadata-only edits trigger a fresh check at that head. Old-run reruns are not proof of the old event
body; the validator always fetches current metadata. GitHub permits metadata changes after a check,
so the immediate premerge live check and postmerge issue-state backstop remain necessary. This
slice does not provide an atomic metadata/merge transaction or prevent a caller bypassing local
instructions. Manual workflow dispatch has no PR metadata and does not certify a PR.

Application adoption and the other skill programme criteria remain owned by open Platform issue
609 (S5 / folded669). Gateway issue673 / PR675 is existing application-native evidence and owns its
lane-specific adoption; it does not establish estate-wide blocking enforcement. Do not copy a
second scanner into each app or claim central delivery makes all application lanes blocking.

From the Platform root, focused proof is `python -m pytest tests/unit/test_pr_metadata.py -q`;
native feature proof is `pwsh -File automation/Invoke-PlatformRepoChecks.ps1 -Lane feature`
(Windows PowerShell may use `powershell -ExecutionPolicy Bypass -File` instead of `pwsh -File`).
