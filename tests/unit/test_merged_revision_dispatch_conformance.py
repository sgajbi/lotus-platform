"""The merged-revision dispatch conformance contract, proven against the forms the estate ships.

`validate_auto_merge_releasability.py` judged dispatchers by shell spelling. That reported
lotus-performance's shell-array range dispatcher as broken and turned this repository's own
gate red with no platform change (#772, #858), and it reported lotus-idea's and lotus-workbench's
program dispatchers under the same two violation names it uses for a measured defect.

These tests hold the validator to `merged-revision-dispatch-conformance.v1.json`: every shell
form is accepted and its representative mutations are still refused; a program is verified through
a declaration bound to the entrypoint the workflow invokes, or reported as `unverified`, which is a
status and not a defect; and the contract's advisory findings are reported beside a verdict rather
than as violations.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from automation import validate_auto_merge_releasability as validator
from automation.validate_auto_merge_releasability import validate_repositories

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = (
    ROOT / "platform-contracts" / "ci-governance" / "merged-revision-dispatch-conformance.v1.json"
)
EXCEPTIONS_PATH = (
    ROOT / "platform-contracts" / "ci-governance" / "auto-merge-releasability-exceptions.v1.json"
)
TODAY = datetime(2026, 9, 13, tzinfo=UTC)

# lotus-performance main 8f933a842397, comments stripped: the dispatcher the recognizer
# rejected. Kept verbatim so the acceptance is of the shipped form, not of a restatement.
PERFORMANCE_ARRAY_DISPATCH = """\
name: Merged PR Main Releasability Dispatch
on:
  pull_request_target:
    types: [closed]
permissions:
  actions: write
  contents: write
jobs:
  dispatch-main-releasability:
    name: Dispatch Main Releasability
    if: >
      github.event.pull_request.merged == true &&
      github.event.pull_request.base.ref == 'main'
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - name: Dispatch every landed revision
        env:
          BASE_SHA: ${{ github.event.pull_request.base.sha }}
          COMMIT_COUNT: ${{ github.event.pull_request.commits }}
          GH_TOKEN: ${{ github.token }}
          MERGE_COMMIT_SHA: ${{ github.event.pull_request.merge_commit_sha }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: |
          set -euo pipefail
          if [ -z "$BASE_SHA" ] || [ -z "$MERGE_COMMIT_SHA" ]; then
            echo "::error::base.sha and merge_commit_sha are required for exact landed-range dispatch"
            exit 1
          fi
          merge_methods="$(gh api "repos/$GITHUB_REPOSITORY" \\
            --jq '[.allow_squash_merge, .allow_merge_commit, .allow_rebase_merge] | @csv')"
          if [ "$merge_methods" != "false,false,true" ]; then
            echo "::error::Per-commit enumeration requires rebase-only merges; observed $merge_methods"
            exit 1
          fi
          git fetch origin main --quiet
          git checkout --quiet --detach FETCH_HEAD
          if ! git merge-base --is-ancestor "$BASE_SHA" "$MERGE_COMMIT_SHA"; then
            echo "::error::PR base $BASE_SHA is not an ancestor of landed tip $MERGE_COMMIT_SHA"
            exit 1
          fi
          mapfile -t revisions < <(git rev-list --reverse "$BASE_SHA..$MERGE_COMMIT_SHA")
          if [ "${#revisions[@]}" -ne "$COMMIT_COUNT" ]; then
            echo "::error::Landed range has ${#revisions[@]} revision(s), but PR event reports $COMMIT_COUNT"
            exit 1
          fi
          for revision in "${revisions[@]}"; do
            if ! git merge-base --is-ancestor "$revision" HEAD; then
              echo "::error::Refusing to dispatch non-main revision $revision"
              exit 1
            fi
            dispatch_ref="main-releasability-${revision}"
            existing_ref_sha=""
            if existing_ref_sha="$(gh api "repos/$GITHUB_REPOSITORY/git/ref/tags/$dispatch_ref" --jq .object.sha 2>/dev/null)"; then
              if [ "$existing_ref_sha" != "$revision" ]; then
                echo "::error::Dispatch ref $dispatch_ref points to $existing_ref_sha, expected $revision"
                exit 1
              fi
            else
              existing_ref_sha=""
            fi
            if [ -z "$existing_ref_sha" ]; then
              gh api "repos/$GITHUB_REPOSITORY/git/refs" \\
                -f ref="refs/tags/$dispatch_ref" \\
                -f sha="$revision" >/dev/null
            fi
            gh workflow run main-releasability.yml \\
              --repo "$GITHUB_REPOSITORY" \\
              --ref "$dispatch_ref" \\
              -f expected_sha="$revision" \\
              -f triggering_pr="$PR_NUMBER"
          done
"""

AUTO_MERGE = """\
name: PR Auto Merge
on:
  pull_request_target:
    types: [opened, ready_for_review]
permissions:
  contents: read
jobs:
  queue:
    runs-on: ubuntu-latest
    steps:
      - env:
          GH_TOKEN: ${{ secrets.LOTUS_AUTOMERGE_TOKEN }}
        run: gh pr merge "$PR_NUMBER" --repo "$GITHUB_REPOSITORY" --auto --rebase --delete-branch
"""

MAIN_RELEASABILITY = """\
name: Main Releasability Gate
on:
  workflow_dispatch:
    inputs:
      expected_sha:
        required: false
        type: string
permissions:
  contents: read
concurrency:
  group: ${{ github.workflow }}-${{ inputs.expected_sha || github.sha }}
  cancel-in-progress: true
jobs:
  exact-revision-assertion:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          ref: ${{ inputs.expected_sha || github.sha }}
      - env:
          EXPECTED_SHA: ${{ inputs.expected_sha }}
        run: |
          actual_sha="$(git rev-parse HEAD)"
          git fetch origin main --quiet
          if [ -z "$EXPECTED_SHA" ]; then
            exit 0
          fi
          if [ "$actual_sha" != "$EXPECTED_SHA" ]; then
            exit 1
          fi
          if ! git merge-base --is-ancestor "$EXPECTED_SHA" FETCH_HEAD; then
            exit 1
          fi
"""


def _script_workflow(command: str, *, contents: str = "read", merged_condition: bool = True) -> str:
    condition = (
        "    if: >\n"
        "      github.event.pull_request.merged == true &&\n"
        "      github.event.pull_request.base.ref == 'main'\n"
        if merged_condition
        else ""
    )
    return (
        "name: Merged PR Main Releasability Dispatch\n"
        "on:\n"
        "  pull_request_target:\n"
        "    types: [closed]\n"
        "permissions:\n"
        "  actions: write\n"
        f"  contents: {contents}\n"
        "jobs:\n"
        "  dispatch-main-releasability:\n"
        f"{condition}"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@v7\n"
        "        with:\n"
        "          fetch-depth: 0\n"
        "      - name: Dispatch main releasability gate for every merged revision\n"
        "        env:\n"
        "          GH_TOKEN: ${{ github.token }}\n"
        f"        run: {command}\n"
    )


def _repository(tmp_path: Path, dispatch: str) -> tuple[Path, Path, Path]:
    """A registered repository with aligned side workflows and the given dispatcher."""
    repos_root = tmp_path / "repos"
    repo_root = repos_root / "lotus-example"
    workflows = repo_root / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "pr-auto-merge.yml").write_text(AUTO_MERGE, encoding="utf-8")
    (workflows / "main-releasability.yml").write_text(MAIN_RELEASABILITY, encoding="utf-8")
    (workflows / "merged-pr-main-releasability.yml").write_text(dispatch, encoding="utf-8")
    policy = tmp_path / "policy.json"
    policy.write_text(
        json.dumps({"repos": [{"name": "lotus-example", "default_branch": "main"}]}),
        encoding="utf-8",
    )
    exceptions = tmp_path / "exceptions.json"
    exceptions.write_text(
        json.dumps({"schema_version": "lotus.auto-merge-releasability-exceptions.v1", "exceptions": []}),
        encoding="utf-8",
    )
    return repos_root, policy, exceptions


def _result(tmp_path: Path, dispatch: str) -> validator.RepositoryAutoMergeResult:
    repos_root, policy, exceptions = _repository(tmp_path, dispatch)
    return validate_repositories(
        policy_path=policy, exception_path=exceptions, repos_root=repos_root, today=TODAY
    )[0]


def _write_declaration(repo_root: Path, **overrides: object) -> Path:
    """A valid declaration for `node scripts/dispatch.mjs`, with the files it names present."""
    (repo_root / "scripts").mkdir(exist_ok=True)
    (repo_root / "scripts" / "dispatch.mjs").write_text("// dispatcher\n", encoding="utf-8")
    (repo_root / "tests").mkdir(exist_ok=True)
    (repo_root / "tests" / "dispatch.test.mjs").write_text("// proof\n", encoding="utf-8")
    payload: dict[str, object] = {
        "schema_version": validator._DECLARATION_SCHEMA_VERSION,
        "form": "script",
        "entrypoint": "node scripts/dispatch.mjs",
        "tested_source_identity": "mainline-ref",
        "enumeration": "range",
        "count_cross_check": "asymmetric",
        "semantics": {semantic: True for semantic in validator._CONTRACT_SEMANTICS},
        "proofs": ["tests/dispatch.test.mjs"],
    }
    payload.update(overrides)
    path = repo_root / validator._DECLARATION_PATH
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# --- the contract itself ---------------------------------------------------


def test_the_contract_names_exactly_the_semantics_forms_and_codes_the_validator_enforces() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    assert contract["schema_version"] == "lotus.merged-revision-dispatch-conformance.v1"
    assert set(contract["semantics"]) == set(validator._CONTRACT_SEMANTICS)
    assert set(contract["forms"]) == {"shell-single-step", "shell-matrix", "shell-array", "script"}
    declaration = contract["script_declaration"]
    assert declaration["path"] == validator._DECLARATION_PATH.as_posix()
    assert declaration["schema_version"] == validator._DECLARATION_SCHEMA_VERSION
    assert set(contract["finding_codes"]["advisory_findings"]) == {
        validator.ADVISORY_COUNT_BOUNDED,
        validator.ADVISORY_STRICT_EQUALITY,
    }
    assert contract["finding_codes"]["status_not_defect"] == ["merged-pr-dispatch.unverified"]
    assert set(contract["audit_evidence_binding"]) >= set(validator._TESTED_SOURCE_IDENTITIES)


def test_no_exception_remains_for_the_recognizer_mismatch_class() -> None:
    """The three #772 exceptions were due to expire on 2026-09-19 and take every platform PR
    gate red with them; the contract makes them unnecessary, so none may remain."""
    register = json.loads(EXCEPTIONS_PATH.read_text(encoding="utf-8"))

    assert all("issues/772" not in str(entry.get("issue_url")) for entry in register["exceptions"])


# --- shell-array form: the dispatcher lotus-performance ships ---------------


def test_the_performance_shell_array_dispatcher_is_recognised(tmp_path: Path) -> None:
    result = _result(tmp_path, PERFORMANCE_ARRAY_DISPATCH)

    assert result.violations == (), result.violations
    assert result.status == "aligned"
    assert result.form == "shell-array"
    # Strict count equality refuses an ordinary rebase-drop: reported, not refused.
    assert result.advisories == (validator.ADVISORY_STRICT_EQUALITY,)


@pytest.mark.parametrize(
    ("original", "replacement", "expected"),
    [
        (
            '            if ! git merge-base --is-ancestor "$revision" HEAD; then\n',
            '            if false; then\n',
            "merged-pr-dispatch.wrong-main-releasability-target",
        ),
        (
            "          BASE_SHA: ${{ github.event.pull_request.base.sha }}\n",
            "          BASE_SHA: 0000000000000000000000000000000000000000\n",
            "merged-pr-dispatch.wrong-main-releasability-target",
        ),
        (
            '              -f expected_sha="$revision" \\\n',
            "",
            "merged-pr-dispatch.missing-expected-sha-input",
        ),
        (
            '          for revision in "${revisions[@]}"; do\n',
            '          for revision in "${other[@]}"; do\n',
            "merged-pr-dispatch.wrong-main-releasability-target",
        ),
    ],
    ids=["no-ancestry-guard", "hard-coded-base", "no-expected-sha", "loop-over-another-array"],
)
def test_a_mutated_shell_array_dispatcher_is_still_refused(
    tmp_path: Path, original: str, replacement: str, expected: str
) -> None:
    assert PERFORMANCE_ARRAY_DISPATCH.count(original) == 1
    mutated = PERFORMANCE_ARRAY_DISPATCH.replace(original, replacement)

    result = _result(tmp_path, mutated)

    assert result.status == "drift"
    assert expected in result.violations, result.violations


def test_an_asymmetric_count_check_carries_no_advisory(tmp_path: Path) -> None:
    asymmetric = PERFORMANCE_ARRAY_DISPATCH.replace(
        '          if [ "${#revisions[@]}" -ne "$COMMIT_COUNT" ]; then\n',
        '          if [ "${#revisions[@]}" -gt "$COMMIT_COUNT" ]; then\n',
    )

    result = _result(tmp_path, asymmetric)

    assert result.status == "aligned"
    assert result.advisories == ()


def test_the_count_bounded_walk_is_reported_as_an_advisory_not_a_violation(tmp_path: Path) -> None:
    """#859's form: accepted by policy, visible in the report."""
    count_bounded = PERFORMANCE_ARRAY_DISPATCH.replace(
        '          mapfile -t revisions < <(git rev-list --reverse "$BASE_SHA..$MERGE_COMMIT_SHA")\n'
        '          if [ "${#revisions[@]}" -ne "$COMMIT_COUNT" ]; then\n'
        '            echo "::error::Landed range has ${#revisions[@]} revision(s), but PR event reports $COMMIT_COUNT"\n'
        "            exit 1\n"
        "          fi\n"
        '          for revision in "${revisions[@]}"; do\n',
        '          revisions="$(git rev-list -n "$COMMIT_COUNT" "$MERGE_COMMIT_SHA" | tac)"\n'
        "          for revision in $revisions; do\n",
    )
    assert count_bounded != PERFORMANCE_ARRAY_DISPATCH

    result = _result(tmp_path, count_bounded)

    assert result.status == "aligned"
    assert result.form == "shell-single-step"
    assert result.advisories == (validator.ADVISORY_COUNT_BOUNDED,)


# --- script form: verified through a bound declaration, or unverified --------


def test_a_program_dispatcher_without_a_declaration_is_unverified_not_broken(tmp_path: Path) -> None:
    result = _result(tmp_path, _script_workflow("node scripts/dispatch.mjs"))

    assert result.status == "unverified"
    assert result.form == "script"
    assert result.violations == ()
    assert "merged-pr-dispatch.missing-expected-sha-input" not in result.violations
    assert "merged-pr-dispatch.wrong-main-releasability-target" not in result.violations
    # A mainline-ref dispatcher writes no refs; contents: read is not a missing permission.
    assert "merged-pr-dispatch.missing-contents-write" not in result.violations


def test_a_program_dispatcher_with_a_bound_declaration_is_aligned(tmp_path: Path) -> None:
    repos_root, policy, exceptions = _repository(tmp_path, _script_workflow("node scripts/dispatch.mjs"))
    _write_declaration(repos_root / "lotus-example")

    result = validate_repositories(
        policy_path=policy, exception_path=exceptions, repos_root=repos_root, today=TODAY
    )[0]

    assert result.status == "aligned", result.violations
    assert result.form == "script"
    assert result.advisories == ()


def test_an_immutable_ref_declaration_still_needs_contents_write(tmp_path: Path) -> None:
    repos_root, policy, exceptions = _repository(tmp_path, _script_workflow("node scripts/dispatch.mjs"))
    _write_declaration(repos_root / "lotus-example", tested_source_identity="immutable-ref")

    result = validate_repositories(
        policy_path=policy, exception_path=exceptions, repos_root=repos_root, today=TODAY
    )[0]

    assert result.status == "drift"
    assert result.violations == ("merged-pr-dispatch.missing-contents-write",)


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        ({"entrypoint": "node scripts/other.mjs"}, "merged-pr-dispatch.declaration.entrypoint-mismatch"),
        ({"proofs": ["tests/missing.test.mjs"]}, "merged-pr-dispatch.declaration.proof-missing"),
        ({"proofs": []}, "merged-pr-dispatch.declaration.proof-missing"),
        (
            {"semantics": {s: (s != "empty-enumeration-refusal") for s in validator._CONTRACT_SEMANTICS}},
            "merged-pr-dispatch.declaration.semantic-missing",
        ),
        ({"schema_version": "lotus.merged-revision-dispatch-declaration.v0"}, "merged-pr-dispatch.declaration.invalid"),
        ({"tested_source_identity": "somewhere"}, "merged-pr-dispatch.declaration.invalid"),
        ({"form": "shell-single-step"}, "merged-pr-dispatch.declaration.invalid"),
    ],
    ids=[
        "entrypoint-mismatch",
        "proof-missing",
        "no-proofs",
        "semantic-false",
        "wrong-schema",
        "unknown-identity",
        "wrong-form",
    ],
)
def test_a_declaration_that_does_not_bind_the_program_is_a_measured_defect(
    tmp_path: Path, overrides: dict, expected: str
) -> None:
    repos_root, policy, exceptions = _repository(tmp_path, _script_workflow("node scripts/dispatch.mjs"))
    _write_declaration(repos_root / "lotus-example", **overrides)

    result = validate_repositories(
        policy_path=policy, exception_path=exceptions, repos_root=repos_root, today=TODAY
    )[0]

    assert result.status == "drift"
    assert expected in result.violations, result.violations


def test_a_declared_program_that_does_not_exist_is_a_measured_defect(tmp_path: Path) -> None:
    repos_root, policy, exceptions = _repository(tmp_path, _script_workflow("node scripts/dispatch.mjs"))
    _write_declaration(repos_root / "lotus-example")
    (repos_root / "lotus-example" / "scripts" / "dispatch.mjs").unlink()

    result = validate_repositories(
        policy_path=policy, exception_path=exceptions, repos_root=repos_root, today=TODAY
    )[0]

    assert "merged-pr-dispatch.declaration.entrypoint-missing" in result.violations


def test_declared_weak_forms_are_advisories_on_an_aligned_program(tmp_path: Path) -> None:
    repos_root, policy, exceptions = _repository(tmp_path, _script_workflow("python scripts/dispatch.py"))
    repo_root = repos_root / "lotus-example"
    _write_declaration(
        repo_root,
        entrypoint="python scripts/dispatch.py",
        tested_source_identity="immutable-ref",
        enumeration="count",
        count_cross_check="strict-equality",
    )
    (repo_root / "scripts" / "dispatch.py").write_text("# dispatcher\n", encoding="utf-8")
    (repo_root / ".github" / "workflows" / "merged-pr-main-releasability.yml").write_text(
        _script_workflow("python scripts/dispatch.py", contents="write"), encoding="utf-8"
    )

    result = validate_repositories(
        policy_path=policy, exception_path=exceptions, repos_root=repos_root, today=TODAY
    )[0]

    assert result.status == "aligned", result.violations
    assert set(result.advisories) == {
        validator.ADVISORY_COUNT_BOUNDED,
        validator.ADVISORY_STRICT_EQUALITY,
    }


def test_a_program_outside_the_merged_main_job_is_not_a_dispatcher(tmp_path: Path) -> None:
    """An unrelated program step cannot launder a missing dispatcher into `unverified`."""
    result = _result(
        tmp_path, _script_workflow("python scripts/lint.py", merged_condition=False)
    )

    assert result.status == "drift"
    assert result.form == "unknown"
    assert "merged-pr-dispatch.wrong-main-releasability-target" in result.violations


# --- lane posture ---------------------------------------------------------


def test_unverified_passes_the_per_commit_lane_and_fails_only_when_asked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repos_root, policy, exceptions = _repository(tmp_path, _script_workflow("node scripts/dispatch.mjs"))
    monkeypatch.setattr(validator, "OUTPUT_JSON", tmp_path / "out.json")
    monkeypatch.setattr(validator, "OUTPUT_MD", tmp_path / "out.md")
    base = [
        "validate_auto_merge_releasability.py",
        "--policy-path", str(policy),
        "--exception-path", str(exceptions),
        "--repos-root", str(repos_root),
        "--require-local-repos",
    ]

    monkeypatch.setattr(sys, "argv", base)
    assert validator.main() == 0

    monkeypatch.setattr(sys, "argv", [*base, "--fail-on-unverified"])
    assert validator.main() == 1

    report = (tmp_path / "out.md").read_text(encoding="utf-8")
    assert "| `lotus-example` | `unverified` | `script` |" in report
