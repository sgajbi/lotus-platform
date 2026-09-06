from __future__ import annotations

import json
from pathlib import Path

from automation import validate_workflow_pipeline_exit_codes as validator

UNGUARDED = """\
name: Example
jobs:
  build:
    steps:
      - name: Enforce Something
        run: |
          mkdir -p output
          python scripts/gate.py 2>&1 | tee output/gate.txt
"""

GUARDED_PIPEFAIL = """\
name: Example
jobs:
  build:
    steps:
      - name: Enforce Something
        run: |
          set -o pipefail
          python scripts/gate.py 2>&1 | tee output/gate.txt
"""

GUARDED_PIPESTATUS = """\
name: Example
jobs:
  build:
    steps:
      - name: Enforce Something
        run: |
          python scripts/gate.py 2>&1 | tee output/gate.txt
          status=${PIPESTATUS[0]}
          exit "${status}"
"""

BARE = """\
name: Example
jobs:
  build:
    steps:
      - name: Enforce Something
        run: python scripts/gate.py
"""


def _repo(root: Path, name: str, workflows: dict[str, str]) -> None:
    workflow_dir = root / name / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    for filename, text in workflows.items():
        (workflow_dir / filename).write_text(text, encoding="utf-8")


def _policy(root: Path, repositories: list[str]) -> Path:
    path = root / "policy.json"
    path.write_text(
        json.dumps({"repos": [{"name": name} for name in repositories]}),
        encoding="utf-8",
    )
    return path


def test_unguarded_pipe_is_reported() -> None:
    assert validator.step_hides_exit_code("run: |\n  python gate.py | tee log.txt")


def test_guards_are_accepted() -> None:
    assert not validator.step_hides_exit_code(GUARDED_PIPEFAIL)
    assert not validator.step_hides_exit_code(GUARDED_PIPESTATUS)
    assert not validator.step_hides_exit_code(BARE)


def test_repository_with_unguarded_step_reports_drift(tmp_path: Path) -> None:
    _repo(tmp_path, "lotus-example", {"gate.yml": UNGUARDED})

    result = validator.validate_repository("lotus-example", repos_root=tmp_path)

    assert result.status == "drift"
    assert [offender.step for offender in result.offenders] == ["Enforce Something"]
    assert result.steps_scanned == 1


def test_repository_with_guarded_step_is_clean(tmp_path: Path) -> None:
    _repo(tmp_path, "lotus-example", {"gate.yml": GUARDED_PIPEFAIL})

    result = validator.validate_repository("lotus-example", repos_root=tmp_path)

    assert result.status == "clean"
    assert result.offenders == ()
    assert result.steps_scanned == 1, "a scan that reads no steps would pass vacuously"


def test_missing_repository_fails_only_when_required(tmp_path: Path) -> None:
    policy = _policy(tmp_path, ["lotus-absent"])
    repositories = validator.policy_repositories(policy)

    _, tolerated = validator.validate_repositories(
        repositories, repos_root=tmp_path, require_local_repos=False
    )
    assert tolerated == []

    _, required = validator.validate_repositories(
        repositories, repos_root=tmp_path, require_local_repos=True
    )
    assert required == ["lotus-absent: repository workflows not available for scanning"]


def test_offenders_are_reported_per_repository(tmp_path: Path) -> None:
    _repo(tmp_path, "lotus-clean", {"gate.yml": GUARDED_PIPEFAIL})
    _repo(tmp_path, "lotus-broken", {"a.yml": UNGUARDED, "b.yml": UNGUARDED})
    policy = _policy(tmp_path, ["lotus-clean", "lotus-broken"])

    _, failures = validator.validate_repositories(
        validator.policy_repositories(policy),
        repos_root=tmp_path,
        require_local_repos=True,
    )

    assert failures == [
        "lotus-broken: a.yml :: Enforce Something",
        "lotus-broken: b.yml :: Enforce Something",
    ]


def test_step_bodies_do_not_bleed_into_the_next_step(tmp_path: Path) -> None:
    """A guard in one step must not silence an unguarded neighbour."""
    workflow = """\
name: Example
jobs:
  build:
    steps:
      - name: Guarded
        run: |
          set -o pipefail
          python a.py | tee a.txt
      - name: Unguarded
        run: |
          python b.py | tee b.txt
"""
    _repo(tmp_path, "lotus-example", {"gate.yml": workflow})

    result = validator.validate_repository("lotus-example", repos_root=tmp_path)

    assert [offender.step for offender in result.offenders] == ["Unguarded"]


def test_the_estate_has_no_step_that_hides_a_gate_exit_code() -> None:
    """The live assertion: no repository on disk may reintroduce the class."""
    repositories = validator.policy_repositories()
    results, failures = validator.validate_repositories(
        repositories, repos_root=validator.ROOT.parent, require_local_repos=False
    )

    scanned = sum(result.steps_scanned for result in results)
    assert scanned > 0, "no workflow steps were scanned: the assertion would be vacuous"
    assert failures == []


UNNAMED = """\
name: Example
jobs:
  build:
    steps:
      - uses: actions/checkout@v6
      - run: python scripts/gate.py 2>&1 | tee output/gate.txt
"""


def test_unnamed_step_with_unguarded_pipe_is_caught(tmp_path: Path) -> None:
    """`- run: gate | tee log` is a valid step; keying on `- name:` would skip it."""
    _repo(tmp_path, "lotus-example", {"gate.yml": UNNAMED})

    result = validator.validate_repository("lotus-example", repos_root=tmp_path)

    assert result.status == "drift"
    assert [offender.step for offender in result.offenders] == ["(unnamed step)"]
    assert result.steps_scanned == 2, "both the uses: and run: steps must be counted"


def test_named_and_unnamed_steps_stay_separate(tmp_path: Path) -> None:
    workflow = """\
name: Example
jobs:
  build:
    steps:
      - name: Guarded
        run: |
          set -o pipefail
          python a.py | tee a.txt
      - run: python b.py | tee b.txt
"""
    _repo(tmp_path, "lotus-example", {"gate.yml": workflow})

    result = validator.validate_repository("lotus-example", repos_root=tmp_path)

    assert [offender.step for offender in result.offenders] == ["(unnamed step)"]


def test_second_pipeline_in_a_step_is_judged_on_its_own() -> None:
    """Guarding one pipeline must not vouch for the next one."""
    body = """run: |
          a.py | tee a.log
          a_status=${PIPESTATUS[0]}
          b.py | tee b.log
          exit "$a_status"
"""
    offenders = validator.unguarded_pipelines(body)
    assert offenders == ["b.py | tee b.log"], (
        "b's failure is discarded whenever a succeeds, so b must be reported"
    )


def test_pipefail_set_after_a_pipeline_does_not_protect_it() -> None:
    body = """run: |
          gate.py | tee gate.log
          set -o pipefail
          other.py | tee other.log
"""
    offenders = validator.unguarded_pipelines(body)
    assert offenders == ["gate.py | tee gate.log"]


def test_pipefail_set_before_protects_following_pipelines() -> None:
    body = """run: |
          set -o pipefail
          gate.py | tee gate.log
          other.py | tee other.log
"""
    assert validator.unguarded_pipelines(body) == []


def test_sinks_beyond_tee_and_tail_are_detected() -> None:
    for sink in ("cat", "head", "sed -n 1p", "awk '{print}'", "sort", "wc -l"):
        body = f"run: gate.py | {sink}\n"
        assert validator.unguarded_pipelines(body), f"{sink} not detected as a sink"


def test_condition_pipelines_are_not_reported() -> None:
    """`if cmd | grep -q x` consumes the status itself; flagging it is noise."""
    for line in (
        'if echo "$output" | grep -qi "already"; then',
        "while read -r line | true; do",
        "! cosign version | grep -q v2.4.1",
    ):
        assert validator.unguarded_pipelines(f"run: |\n          {line}\n") == [], line


def test_assertion_terminal_stages_are_not_reported() -> None:
    """A terminal grep/jq is usually the assertion, and its failure does fail."""
    body = "run: pg_dump --version | grep -Eq ' 16[.]'\n"
    assert validator.unguarded_pipelines(body) == []


def test_condition_pipeline_into_a_sink_is_reported() -> None:
    """`if gate.py | tee log; then` enters the success branch on tee's status."""
    body = "run: |\n          if gate.py | tee gate.log; then\n            echo ok\n          fi\n"
    assert validator.unguarded_pipelines(body) == ["if gate.py | tee gate.log; then"]


def test_condition_pipeline_into_an_assertion_stays_quiet() -> None:
    body = 'run: |\n          if echo "$out" | grep -qi already; then\n            echo ok\n          fi\n'
    assert validator.unguarded_pipelines(body) == []


def test_pipeline_split_across_lines_is_joined() -> None:
    """Bash continues after a trailing pipe; analysing halves would miss it."""
    body = "run: |\n          gate.py |\n            tee gate.log\n"
    assert validator.unguarded_pipelines(body) == ["gate.py | tee gate.log"]


def test_mentioning_pipestatus_is_not_a_guard() -> None:
    body = "run: |\n          gate.py | tee log\n          status=${PIPESTATUS[0]}\n          echo done\n"
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"], (
        "capturing the status without ever exiting on it leaves the step green"
    )


def test_capturing_the_wrong_stage_is_not_a_guard() -> None:
    body = 'run: |\n          gate.py | tee log\n          status=${PIPESTATUS[1]}\n          exit "$status"\n'
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_captured_status_that_reaches_exit_is_a_guard() -> None:
    body = 'run: |\n          gate.py | tee log\n          status=${PIPESTATUS[0]}\n          exit "$status"\n'
    assert validator.unguarded_pipelines(body) == []


def test_direct_exit_on_pipestatus_is_a_guard() -> None:
    body = "run: |\n          gate.py | tee log\n          exit ${PIPESTATUS[0]}\n"
    assert validator.unguarded_pipelines(body) == []


def test_sink_behind_a_runner_prefix_is_detected() -> None:
    for stage in ("sudo tee out.txt", "env tee out.txt", "LC_ALL=C tee out.txt"):
        assert validator.unguarded_pipelines(f"run: gate.py | {stage}\n"), stage


def test_trivial_producers_are_not_gates() -> None:
    """`echo ... | sudo tee file` is the privileged-write idiom, not a hidden gate."""
    for source in ("echo deb-line", 'printf "%s" x', "true"):
        body = f"run: {source} | sudo tee /etc/apt/x.list > /dev/null\n"
        assert validator.unguarded_pipelines(body) == [], source


def test_pipeline_before_a_later_shell_command_is_reported() -> None:
    """`gate.py | tee log; echo done` ends the step on echo, hiding the gate."""
    for line in ("gate.py | tee log; echo done", "gate.py | tee log && echo done"):
        assert validator.unguarded_pipelines(f"run: {line}\n") == [line], line


def test_a_guarded_segment_still_passes_alongside_other_commands() -> None:
    body = "run: |\n          set -o pipefail\n          gate.py | tee log; echo done\n"
    assert validator.unguarded_pipelines(body) == []


def test_bash_pipe_ampersand_operator_is_recognized() -> None:
    """`|&` is shorthand for `2>&1 |` and hides the gate the same way."""
    assert validator.unguarded_pipelines("run: gate.py |& tee log\n") == [
        "gate.py |& tee log"
    ]


def test_a_gate_after_a_trivial_source_is_still_reported() -> None:
    """Only the whole upstream being verdict-free makes a pipeline harmless."""
    line = "printf data | python gate.py | tee log"
    assert validator.unguarded_pipelines(f"run: {line}\n") == [line]


def test_compact_pipefail_option_clusters_are_accepted() -> None:
    """`set -euo pipefail` is the repository idiom; rejecting it blocks valid PRs."""
    for options in ("-o", "-eo", "-euo", "-euxo"):
        body = (
            f"run: |\n          set {options} pipefail\n          gate.py | tee log\n"
        )
        assert validator.unguarded_pipelines(body) == [], options


def test_same_line_set_is_applied_before_the_pipeline_after_it() -> None:
    """Enable first, so a disable that never matched would fail this test.

    Asserting the disabled case alone passes for the wrong reason: pipefail is
    off by default, so the pipeline is reported whether or not `set +o` was
    recognised at all. That is exactly how a broken pattern survived here once.
    """
    disabled = "set -o pipefail; set +o pipefail; gate.py | tee log"
    enabled = "set -o pipefail; gate.py | tee log"
    assert validator.unguarded_pipelines(f"run: |\n          {disabled}\n") == [
        disabled
    ]
    assert validator.unguarded_pipelines(f"run: |\n          {enabled}\n") == []


def test_conditional_disable_invalidates_an_earlier_guard() -> None:
    """A `set +o` inside a branch may execute, so it must cancel the guard."""
    body = (
        "run: |\n"
        "          set -o pipefail\n"
        "          if true; then set +o pipefail; fi\n"
        "          gate.py | tee log\n"
    )
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_commented_propagation_is_not_a_guard() -> None:
    body = "run: |\n          gate.py | tee log\n          # exit ${PIPESTATUS[0]}\n"
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_pipestatus_vouches_only_for_the_last_pipeline_on_the_line() -> None:
    """PIPESTATUS describes the most recent pipeline, not every one on the line."""
    body = (
        "run: |\n"
        "          a.py | tee a; b.py | tee b\n"
        "          s=${PIPESTATUS[0]}\n"
        '          exit "$s"\n'
    )
    assert validator.unguarded_pipelines(body) == ["a.py | tee a; b.py | tee b"], (
        "only b's status is captured, so a can still fail open"
    )


def test_pipefail_inside_an_untaken_branch_is_not_honoured() -> None:
    """`if false; then set -o pipefail; fi` never runs; assuming it did is unsafe."""
    body = (
        "run: |\n"
        "          if false; then set -o pipefail; fi\n"
        "          gate.py | tee log\n"
    )
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_unconditional_pipefail_is_still_honoured() -> None:
    body = "run: |\n          set -o pipefail\n          gate.py | tee log\n"
    assert validator.unguarded_pipelines(body) == []


def test_gate_inside_a_command_substitution_is_reported() -> None:
    """`result="$(gate.py | tee log)"` executes, and the assignment takes tee's status."""
    line = 'result="$(python gate.py | tee gate.log)"'
    assert validator.unguarded_pipelines(f"run: {line}\n") == [line]


def test_value_producing_substitution_pipelines_stay_quiet() -> None:
    """`test "$(find … | wc -l)" -gt 0` asserts on the value; wc is doing its job."""
    line = 'test "$(find coverage-data -type f | wc -l)" -gt 0'
    assert validator.unguarded_pipelines(f"run: {line}\n") == []


def test_sink_behind_a_wrapper_option_is_detected() -> None:
    for stage in ("sudo -n tee log", "sudo -- tee log"):
        assert validator.unguarded_pipelines(f"run: gate.py | {stage}\n"), stage


def test_conditional_exit_is_not_propagation() -> None:
    """`false && exit ${PIPESTATUS[0]}` never runs, so it guards nothing."""
    body = (
        "run: |\n"
        "          gate.py | tee log\n"
        "          false && exit ${PIPESTATUS[0]}\n"
        "          true\n"
    )
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_pipefail_in_an_uncalled_function_does_not_guard() -> None:
    """A function body does not run until called; its `set` never took effect."""
    body = (
        "run: |\n"
        "          enable_strict() { set -o pipefail; }\n"
        "          gate.py | tee log\n"
    )
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_pipefail_in_a_subshell_does_not_escape_it() -> None:
    """`( set -o pipefail )` changes the subshell only; the outer shell is unchanged."""
    body = "run: |\n          ( set -o pipefail )\n          gate.py | tee log\n"
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_pipefail_in_a_called_function_still_guards() -> None:
    """The scope rule must not reject a function that actually runs."""
    body = (
        "run: |\n"
        "          enable_strict() { set -o pipefail; }\n"
        "          enable_strict\n"
        "          gate.py | tee log\n"
    )
    assert validator.unguarded_pipelines(body) == []


def test_pipestatus_clobbered_before_capture_does_not_guard() -> None:
    """PIPESTATUS describes the last pipeline; any command in between replaces it."""
    body = (
        "run: |\n"
        "          gate.py | tee log\n"
        "          echo done; s=${PIPESTATUS[0]}\n"
        '          exit "$s"\n'
    )
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"], (
        "echo runs first, so PIPESTATUS reports echo's status, not the gate's"
    )


def test_pipestatus_captured_first_on_the_line_still_guards() -> None:
    body = (
        "run: |\n"
        "          gate.py | tee log\n"
        "          s=${PIPESTATUS[0]}; echo done\n"
        '          exit "$s"\n'
    )
    assert validator.unguarded_pipelines(body) == []
