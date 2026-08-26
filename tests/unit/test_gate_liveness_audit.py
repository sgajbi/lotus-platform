"""A gate is only real if it is reachable, can fail, and fails on empty input.

Each test here is anchored to a measured instance in the estate rather than to a hypothetical, so
the rules cannot be argued away as theoretical:

- ORPHAN: `lotus-performance#477` - `container-vulnerability-gate` is written with `--exit-code 1`
  and invoked by no target and no workflow, while CI runs the `--exit-code 0` report beside it.
- CANNOT_FAIL (radon): `lotus-risk#225` - `complexity-gate` runs `radon cc` and `radon mi`, neither
  of which has a failing exit code, from the blocking `ci` lane.
- CANNOT_FAIL (trivy): the same shape in container scanning, where the blocking form is the
  `--exit-code 1` variant.
- INSPECTED NOTHING: `lotus-risk#232` and `lotus-platform#728` - a guard whose source root is absent
  reports success. This module's subject obeys that rule about itself.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.gate_liveness_audit import (
    _make_invoked_targets,
    audit_repository,
    blocking_workflow_invocations,
    main,
    parse_makefile,
    reachable_targets,
)


def _write_repo(
    root: Path, makefile: str, workflows: dict[str, str] | None = None
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "Makefile").write_text(makefile, encoding="utf-8")
    workflow_dir = root / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    for name, body in (workflows or {}).items():
        (workflow_dir / name).write_text(body, encoding="utf-8")
    return root


def test_parse_makefile_reads_prerequisites_and_recipe() -> None:
    targets = parse_makefile(
        "ci: lint typecheck\n\techo one\n\techo two\n\nlint:\n\truff check .\n"
    )

    assert targets["ci"].prerequisites == ("lint", "typecheck")
    assert [line.strip() for line in targets["ci"].recipe] == ["echo one", "echo two"]


def test_parse_makefile_folds_continued_prerequisites() -> None:
    targets = parse_makefile(
        "ci: lint \\\n  release-gate\n\nlint:\n\truff check .\n\nrelease-gate:\n\tpython g.py\n"
    )

    assert targets["ci"].prerequisites == ("lint", "release-gate")


def test_reachability_follows_prerequisites_and_recursive_make() -> None:
    targets = parse_makefile(
        "ci: lint\n\t$(MAKE) deep-gate\n\nlint:\n\truff check .\n\ndeep-gate:\n\tpython g.py\n"
    )

    assert reachable_targets(targets, ("ci",)) == {"ci", "lint", "deep-gate"}


def test_a_name_only_in_phony_is_not_treated_as_invoked() -> None:
    """The orphan signature: the target appears in .PHONY and in its own definition, nowhere else."""

    makefile = ".PHONY: ci lonely-gate\n\nci: lint\n\nlint:\n\truff check .\n\nlonely-gate:\n\tpython g.py\n"
    targets = parse_makefile(makefile)

    assert "lonely-gate" not in reachable_targets(targets, ("ci", "check", "lint"))


def test_orphan_gate_is_reported(tmp_path: Path) -> None:
    """lotus-performance#477: a blocking gate wired to nothing, beside a non-blocking report."""

    repo = _write_repo(
        tmp_path / "svc",
        ".PHONY: ci container-vulnerability-gate\n"
        "ci: container-supply-chain-evidence\n\n"
        "container-supply-chain-evidence:\n"
        "\ttrivy image --exit-code 0 --format json app:ci\n\n"
        "container-vulnerability-gate:\n"
        "\ttrivy image --exit-code 1 app:ci\n",
    )

    findings, gate_count = audit_repository("svc", repo)

    assert gate_count == 1
    orphans = [f for f in findings if f.kind == "ORPHAN"]
    assert [f.target for f in orphans] == ["container-vulnerability-gate"]
    assert "never runs" in orphans[0].detail


def test_a_gate_invoked_only_by_a_workflow_is_not_an_orphan(tmp_path: Path) -> None:
    """Wiring can legitimately live in the lane rather than in an aggregate target."""

    repo = _write_repo(
        tmp_path / "svc",
        "ci: lint\n\nlint:\n\truff check .\n\nrelease-gate:\n\tpython g.py\n",
        {"main.yml": "jobs:\n  gate:\n    steps:\n      - run: make release-gate\n"},
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "ORPHAN"] == []


def test_radon_in_a_blocking_lane_cannot_fail(tmp_path: Path) -> None:
    """lotus-risk#225: radon has no failing exit code, so this gate passes unconditionally."""

    repo = _write_repo(
        tmp_path / "svc",
        "ci: complexity-gate\n\ncomplexity-gate:\n\tpython -m radon cc src -s -n C\n\tpython -m radon mi src -s\n",
    )

    findings, _ = audit_repository("svc", repo)

    cannot_fail = [f for f in findings if f.kind == "CANNOT_FAIL"]
    assert len(cannot_fail) == 1
    assert all("radon" in f.detail for f in cannot_fail)


def test_a_thresholded_scanner_is_not_flagged(tmp_path: Path) -> None:
    """The working pattern: a script that exits non-zero on a threshold breach."""

    repo = _write_repo(
        tmp_path / "svc",
        "ci: complexity-gate\n\ncomplexity-gate:\n\tpython scripts/complexity_inventory.py --max-cc 8\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "CANNOT_FAIL"] == []


@pytest.mark.parametrize(
    "recipe",
    [
        "\ttrivy image app:ci\n",
        "\tpython g.py --exit-code 0\n",
        "\tpython g.py || true\n",
        "\tpython g.py || exit 0\n",
        "\t-python g.py\n",
    ],
)
def test_each_discarded_verdict_form_is_detected(tmp_path: Path, recipe: str) -> None:
    repo = _write_repo(tmp_path / "svc", f"ci: some-gate\n\nsome-gate:\n{recipe}")

    findings, _ = audit_repository("svc", repo)

    assert [f.kind for f in findings if f.kind == "CANNOT_FAIL"] == ["CANNOT_FAIL"]


def test_trivy_with_a_failing_exit_code_is_not_flagged(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: scan-gate\n\nscan-gate:\n\ttrivy image --severity HIGH --exit-code 1 app:ci\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "CANNOT_FAIL"] == []


def test_the_audit_fails_when_it_inspected_nothing(tmp_path: Path, capsys) -> None:
    """The rule this tool enforces, applied to the tool. Silence is never a pass."""

    empty = tmp_path / "empty"
    empty.mkdir()

    exit_code = main(["--repo-path", str(empty)])

    assert exit_code == 1
    assert "must fail" in capsys.readouterr().err


def test_the_audit_fails_when_a_repository_declares_no_gates(
    tmp_path: Path, capsys
) -> None:
    """A Makefile with no gate targets is indistinguishable from a scan that did not run."""

    _write_repo(tmp_path / "svc", "ci: test\n\ntest:\n\tpytest\n")

    exit_code = main(["--repo-path", str(tmp_path / "svc")])

    assert exit_code == 1
    stderr = capsys.readouterr().err
    assert "Repositories declaring no gate targets: ['svc']" in stderr
    assert "must fail" in stderr


def test_fail_on_findings_controls_the_exit_code(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        ".PHONY: ci orphan-gate\nci: lint\n\nlint:\n\truff check .\n\norphan-gate:\n\tpython g.py\n",
    )

    assert main(["--repo-path", str(repo)]) == 0
    assert main(["--repo-path", str(repo), "--fail-on-findings"]) == 1


def test_fleet_mode_reads_repos_json(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: lint\n\nlint:\n\truff check .\n\norphan-gate:\n\tpython g.py\n",
    )
    repos_json = tmp_path / "repos.json"
    repos_json.write_text(
        json.dumps([{"name": "svc", "path": str(repo)}]), encoding="utf-8"
    )

    assert main(["--repos-json", str(repos_json), "--fail-on-findings"]) == 1


def test_workflow_invocation_extraction_ignores_unknown_targets() -> None:
    targets = parse_makefile("ci:\n\techo hi\n\nreal-gate:\n\tpython g.py\n")

    invoked = blocking_workflow_invocations(
        "- run: make real-gate\n- run: make not-a-target\n", targets
    )

    assert invoked == {"real-gate"}


def test_a_missing_fleet_path_fails_rather_than_being_skipped(
    tmp_path: Path, capsys
) -> None:
    """The defect this tool reports, in the tool.

    A `repos.json` naming a path that is missing, stale, or not mounted used to be skipped in
    silence, so a fleet run could report clean having never opened one of the repositories it was
    asked about - and `--fail-on-findings` would still exit 0.
    """

    present = _write_repo(
        tmp_path / "present",
        "ci: real-gate\n\nreal-gate:\n\tpython scripts/g.py --max 0\n",
    )
    repos_json = tmp_path / "repos.json"
    repos_json.write_text(
        json.dumps(
            [
                {"name": "present", "path": str(present)},
                {"name": "absent", "path": str(tmp_path / "not-checked-out")},
            ]
        ),
        encoding="utf-8",
    )

    exit_code = main(["--repos-json", str(repos_json), "--fail-on-findings"])

    assert exit_code == 1
    stderr = capsys.readouterr().err
    assert "could not be inspected" in stderr
    assert "absent" in stderr


def test_a_gate_named_only_in_a_comment_is_still_an_orphan(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: lint\n\nlint:\n\truff check .\n\nrelease-gate:\n\tpython g.py\n",
        {
            "main.yml": "jobs:\n  gate:\n    steps:\n      # - run: make release-gate\n      - run: echo hi\n"
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "ORPHAN"] == ["release-gate"]


def test_a_continue_on_error_step_does_not_make_a_gate_reachable(
    tmp_path: Path,
) -> None:
    """A step that cannot fail the job does not enforce anything."""

    repo = _write_repo(
        tmp_path / "svc",
        "ci: lint\n\nlint:\n\truff check .\n\nrelease-gate:\n\tpython g.py\n",
        {
            "main.yml": (
                "jobs:\n  gate:\n    steps:\n      - name: soft\n"
                "        continue-on-error: true\n        run: make release-gate\n"
            )
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "ORPHAN"] == ["release-gate"]


def test_a_continue_on_error_job_does_not_make_a_gate_reachable(
    tmp_path: Path,
) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: lint\n\nlint:\n\truff check .\n\nrelease-gate:\n\tpython g.py\n",
        {
            "main.yml": (
                "jobs:\n  gate:\n    continue-on-error: true\n    steps:\n"
                "      - run: make release-gate\n"
            )
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "ORPHAN"] == ["release-gate"]


def test_a_continued_trivy_command_is_not_flagged(tmp_path: Path) -> None:
    r"""A trivy command continued with a trailing backslash is one command.

    Judging only its first physical line reports a valid `--exit-code 1` gate as unable to fail.
    """

    repo = _write_repo(
        tmp_path / "svc",
        "ci: scan-gate\n\nscan-gate:\n\ttrivy image \\n\t\t--severity HIGH \\n\t\t--exit-code 1 app:ci\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "CANNOT_FAIL"] == []


def test_the_silent_and_ignore_prefixes_combine(tmp_path: Path) -> None:
    """`@-python g.py` ignores the failure exactly as `-python g.py` does."""

    repo = _write_repo(
        tmp_path / "svc", "ci: some-gate\n\nsome-gate:\n\t@-python g.py\n"
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.kind for f in findings] == ["CANNOT_FAIL"]


def test_a_piped_gate_cannot_fail(tmp_path: Path) -> None:
    """Make sees the pipeline's status, which is `tee`'s, not the gate's."""

    repo = _write_repo(
        tmp_path / "svc", "ci: some-gate\n\nsome-gate:\n\tpython g.py | tee gate.log\n"
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.kind for f in findings] == ["CANNOT_FAIL"]


def test_a_trailing_command_after_a_semicolon_masks_the_status(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc", "ci: some-gate\n\nsome-gate:\n\tpython g.py; echo completed\n"
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.kind for f in findings] == ["CANNOT_FAIL"]


def test_an_ignored_cleanup_before_the_gate_is_not_flagged(tmp_path: Path) -> None:
    """`cleanup || true; python g.py` still returns the gate's status."""

    repo = _write_repo(
        tmp_path / "svc",
        "ci: some-gate\n\nsome-gate:\n\trm -rf out || true; python g.py --max 0\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "CANNOT_FAIL"] == []


def test_a_prerequisite_only_gate_is_counted_and_checked(tmp_path: Path) -> None:
    """`orphan-gate: scan` with no recipe of its own is still a gate."""

    repo = _write_repo(
        tmp_path / "svc",
        ".PHONY: ci orphan-gate\nci: lint\n\nlint:\n\truff check .\n\nscan:\n\tpython s.py\n\norphan-gate: scan\n",
    )

    findings, gate_count = audit_repository("svc", repo)

    assert gate_count == 1
    assert [f.target for f in findings if f.kind == "ORPHAN"] == ["orphan-gate"]


def test_lint_is_not_a_blocking_root_unless_something_invokes_it(
    tmp_path: Path,
) -> None:
    """A gate hanging off an uninvoked `lint` is not enforced by anything."""

    repo = _write_repo(
        tmp_path / "svc",
        ".PHONY: lint style-gate\nlint: style-gate\n\nstyle-gate:\n\tpython g.py\n\nbuild:\n\techo build\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "ORPHAN"] == ["style-gate"]


def test_lint_is_a_blocking_root_when_ci_reaches_it(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: lint\n\nlint: style-gate\n\nstyle-gate:\n\tpython g.py --max 0\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "ORPHAN"] == []


def test_an_inline_recipe_after_a_semicolon_is_a_recipe_not_a_prerequisite(
    tmp_path: Path,
) -> None:
    """GNU Make allows `target: prereqs ; command`.

    Storing the whole tail as prerequisites left the recipe empty, so the target counted as a gate
    and looked reachable while its non-failing command was never inspected.
    """

    repo = _write_repo(
        tmp_path / "svc",
        "ci: security-gate\n\nsecurity-gate: ; trivy image --exit-code 0 app\n",
    )

    findings, gate_count = audit_repository("svc", repo)

    assert gate_count == 1
    cannot_fail = [f for f in findings if f.kind == "CANNOT_FAIL"]
    assert len(cannot_fail) == 1
    # The trivy rule matches before the generic `--exit-code 0` one, so the detail names it.
    assert "trivy without --exit-code 1" in cannot_fail[0].detail
    assert cannot_fail[0].evidence == "trivy image --exit-code 0 app"


def test_an_inline_recipe_keeps_its_prerequisites(tmp_path: Path) -> None:
    targets = parse_makefile("build-gate: dep-one dep-two ; python g.py --max 0\n")

    assert targets["build-gate"].prerequisites == ("dep-one", "dep-two")
    assert targets["build-gate"].recipe == ("python g.py --max 0",)


def test_a_pipeline_under_pipefail_is_not_flagged(tmp_path: Path) -> None:
    """`pipefail` makes the pipeline return the first non-zero stage, so the gate can fail."""

    repo = _write_repo(
        tmp_path / "svc",
        "ci: scan-gate\n\nscan-gate:\n\tbash -o pipefail -c 'python g.py | tee gate.log'\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "CANNOT_FAIL"] == []


def test_a_pipeline_without_pipefail_is_still_flagged(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: scan-gate\n\nscan-gate:\n\tbash -c 'python g.py | tee gate.log'\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.kind for f in findings if f.kind == "CANNOT_FAIL"] == ["CANNOT_FAIL"]


def test_a_gate_with_only_no_op_recipes_is_unable_to_enforce(tmp_path: Path) -> None:
    """A declared gate that only prints or prepares directories produces no verdict."""

    repo = _write_repo(
        tmp_path / "svc",
        "ci: evidence-gate\n\nevidence-gate:\n\t@echo collecting\n\tmkdir -p output\n",
    )

    findings, _ = audit_repository("svc", repo)

    cannot_fail = [f for f in findings if f.kind == "CANNOT_FAIL"]
    assert [f.target for f in cannot_fail] == ["evidence-gate"]
    assert "only comments, setup, or no-op recipes" in cannot_fail[0].detail


def test_setup_prefix_does_not_hide_a_failing_validator(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: release-gate\n\nrelease-gate:\n\tmkdir -p output && python gate.py\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "CANNOT_FAIL"] == []


def test_unknown_pipeline_consumer_is_treated_as_status_masking(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: release-gate\n\nrelease-gate:\n\tpython gate.py | sed 's/x/y/'\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "CANNOT_FAIL"] == ["release-gate"]


def test_make_options_are_skipped_before_workflow_targets(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: lint\n\nlint:\n\truff check .\n\nrelease-gate:\n\tpython g.py\n",
        {
            "main.yml": "jobs:\n  gate:\n    steps:\n      - run: make --silent release-gate\n"
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "ORPHAN"] == []


def test_make_options_are_skipped_before_recursive_targets() -> None:
    targets = parse_makefile(
        "ci:\n\t@$(MAKE) -s --directory . release-gate\n\nrelease-gate:\n\tpython g.py\n"
    )

    assert reachable_targets(targets, ("ci",)) == {"ci", "release-gate"}


def test_optional_make_option_does_not_consume_the_target() -> None:
    targets = parse_makefile(
        "ci:\n\t$(MAKE) --output-sync release-gate\n\nrelease-gate:\n\tpython g.py\n"
    )

    assert reachable_targets(targets, ("ci",)) == {"ci", "release-gate"}


def test_quoted_make_text_is_not_treated_as_an_invocation() -> None:
    targets = parse_makefile(
        'ci:\n\t@echo "run make release-gate manually"\n\n'
        "release-gate:\n\tpython g.py\n"
    )

    assert reachable_targets(targets, ("ci",)) == {"ci"}


def test_unquoted_echoed_make_text_is_not_treated_as_an_invocation() -> None:
    targets = parse_makefile(
        "ci:\n\t@echo run make release-gate manually\n\nrelease-gate:\n\tpython g.py\n"
    )

    assert reachable_targets(targets, ("ci",)) == {"ci"}


def test_shell_comment_does_not_add_targets_after_the_command() -> None:
    assert _make_invoked_targets("make release-gate # documentation only") == (
        "release-gate",
    )


def test_malformed_workflow_is_fail_closed_for_gate_reachability() -> None:
    targets = parse_makefile("release-gate:\n\tpython g.py\n")

    assert blocking_workflow_invocations("jobs: [", targets) == set()


def test_workflow_step_name_is_not_treated_as_a_make_invocation(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci:\n\tpython check.py\n\nrelease-gate:\n\tpython g.py\n",
        {
            "main.yml": (
                "jobs:\n  gate:\n    steps:\n"
                "      - name: make release-gate visible to operators\n"
                "        run: echo not-running-the-gate\n"
            )
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "ORPHAN"] == ["release-gate"]


def test_multiline_workflow_run_invokes_a_gate(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci:\n\tpython check.py\n\nrelease-gate:\n\tpython g.py\n",
        {
            "main.yml": (
                "jobs:\n  gate:\n    steps:\n"
                "      - name: governed gate\n"
                "        run: |\n"
                "          echo preparing\n"
                "          make release-gate\n"
            )
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "ORPHAN"] == []


def test_multiline_workflow_run_honors_default_errexit(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci:\n\tpython check.py\n\nrelease-gate:\n\tpython g.py\n",
        {
            "main.yml": (
                "jobs:\n  gate:\n    steps:\n"
                "      - run: |\n"
                "          make release-gate\n"
                "          echo completed\n"
            )
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "ORPHAN"] == []


def test_inline_workflow_shell_comment_does_not_invoke_a_gate(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci:\n\tpython check.py\n\nrelease-gate:\n\tpython g.py\n",
        {
            "main.yml": (
                "jobs:\n  gate:\n    steps:\n"
                "      - run: make ci # make release-gate manually\n"
            )
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "ORPHAN"] == ["release-gate"]


def test_folded_workflow_run_scalar_invokes_a_gate(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci:\n\tpython check.py\n\nrelease-gate:\n\tpython g.py\n",
        {
            "main.yml": (
                "jobs:\n  gate:\n    steps:\n"
                "      - run: >\n"
                "          make\n"
                "          release-gate\n"
            )
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "ORPHAN"] == []


def test_quoted_inline_workflow_run_scalar_invokes_a_gate(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci:\n\tpython check.py\n\nrelease-gate:\n\tpython g.py\n",
        {
            "main.yml": (
                "jobs:\n  gate:\n    steps:\n"
                '      - run: "make release-gate"\n'
            )
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "ORPHAN"] == []


def test_target_capability_combines_prerequisites_and_reporting_recipes(
    tmp_path: Path,
) -> None:
    """A failing prerequisite keeps an aggregate live despite a best-effort report line."""

    repo = _write_repo(
        tmp_path / "svc",
        "ci: aggregate-gate\n\n"
        "aggregate-gate: scanner\n\tpython report.py | tee report.log\n\n"
        "scanner:\n\tpython scanner.py --max-findings 0\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "CANNOT_FAIL"] == []


def test_one_failure_propagating_recipe_makes_the_whole_gate_capable(
    tmp_path: Path,
) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: evidence-gate\n\n"
        "evidence-gate:\n\tpython gate.py --max-findings 0\n\tpython report.py | tee report.log\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "CANNOT_FAIL"] == []


@pytest.mark.parametrize(
    "make_options",
    ["-C tools", "--directory=tools", "-f tools.mk", "--file=tools.mk"],
)
def test_an_alternate_makefile_does_not_credit_a_root_target(
    tmp_path: Path, make_options: str
) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci:\n\treal-check\n\nrelease-gate:\n\tpython gate.py\n",
        {
            "main.yml": (
                "jobs:\n  gate:\n    steps:\n"
                f"      - run: make {make_options} release-gate\n"
            )
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "ORPHAN"] == ["release-gate"]


def test_an_explicit_root_makefile_still_credits_the_root_target(
    tmp_path: Path,
) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci:\n\treal-check\n\nrelease-gate:\n\tpython gate.py\n",
        {
            "main.yml": (
                "jobs:\n  gate:\n    steps:\n"
                "      - run: make -C . --file=./Makefile release-gate\n"
            )
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "ORPHAN"] == []


def test_an_empty_gate_declaration_is_counted_and_cannot_enforce(
    tmp_path: Path,
) -> None:
    repo = _write_repo(tmp_path / "svc", "ci: security-gate\n\nsecurity-gate:\n")

    findings, gate_count = audit_repository("svc", repo)

    assert gate_count == 1
    assert [f.target for f in findings if f.kind == "CANNOT_FAIL"] == ["security-gate"]


def test_every_target_in_a_multi_target_rule_is_audited(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: hidden-gate\n\nfoo hidden-gate: ; trivy image --exit-code 0 app\n",
    )

    findings, gate_count = audit_repository("svc", repo)

    assert gate_count == 1
    assert [f.target for f in findings if f.kind == "CANNOT_FAIL"] == ["hidden-gate"]


def test_a_gate_in_the_final_pipeline_stage_propagates_its_status(
    tmp_path: Path,
) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: scan-gate\n\nscan-gate:\n\tgenerate-input | python gate.py\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "CANNOT_FAIL"] == []


@pytest.mark.parametrize("fallback", [":", "echo skipped"])
def test_a_terminal_always_successful_or_fallback_masks_the_gate(
    tmp_path: Path, fallback: str
) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        f"ci: scan-gate\n\nscan-gate:\n\tpython gate.py || {fallback}\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "CANNOT_FAIL"] == ["scan-gate"]


def test_an_ignored_echo_fallback_before_the_gate_does_not_mask_it(
    tmp_path: Path,
) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: scan-gate\n\nscan-gate:\n\tprepare || echo skipped; python gate.py\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "CANNOT_FAIL"] == []


@pytest.mark.parametrize(
    "invocation",
    [
        "make release-gate || true",
        "make release-gate || :",
        "make release-gate || echo skipped",
        "make release-gate; true",
        "make release-gate; python report.py",
        "make release-gate | tee gate.log",
    ],
)
def test_a_workflow_make_invocation_with_discarded_status_is_not_blocking(
    tmp_path: Path, invocation: str
) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci:\n\tpython check.py\n\nrelease-gate:\n\tpython gate.py\n",
        {"main.yml": f"jobs:\n  gate:\n    steps:\n      - run: {invocation}\n"},
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "ORPHAN"] == ["release-gate"]


@pytest.mark.parametrize(
    "invocation",
    [
        "make release-gate && echo completed",
        "set -e; make release-gate; echo completed",
    ],
)
def test_a_workflow_make_invocation_with_propagated_status_is_blocking(
    tmp_path: Path, invocation: str
) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci:\n\tpython check.py\n\nrelease-gate:\n\tpython gate.py\n",
        {"main.yml": f"jobs:\n  gate:\n    steps:\n      - run: {invocation}\n"},
    )

    findings, _ = audit_repository("svc", repo)

    assert [f for f in findings if f.kind == "ORPHAN"] == []


@pytest.mark.parametrize(
    "make_option", ["--ignore-errors", "--dry-run", "--just-print", "-i", "-n"]
)
def test_non_enforcing_make_modes_do_not_credit_a_workflow_gate(
    tmp_path: Path, make_option: str
) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci:\n\tpython check.py\n\nrelease-gate:\n\tpython gate.py\n",
        {
            "main.yml": (
                "jobs:\n  gate:\n    steps:\n"
                f"      - run: make {make_option} release-gate\n"
            )
        },
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "ORPHAN"] == ["release-gate"]


def test_ruff_exit_zero_is_report_only(tmp_path: Path) -> None:
    repo = _write_repo(
        tmp_path / "svc",
        "ci: lint-gate\n\nlint-gate:\n\truff check --exit-zero .\n",
    )

    findings, _ = audit_repository("svc", repo)

    assert [f.target for f in findings if f.kind == "CANNOT_FAIL"] == ["lint-gate"]
