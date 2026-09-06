from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from automation import validate_workflow_pipeline_exit_codes as validator

# A gate that fails, defined as a shell function so the observation needs no
# file on disk, no executable bit, and no working directory the shell can reach.
_GATE = "gate() { printf 'gate ran\\n'; return 7; }\n"


def _usable_bash() -> str | None:
    """The first bash that demonstrably reports exit statuses, or None.

    `shutil.which("bash")` on Windows finds `C:\\Windows\\system32\\bash.exe`
    first: the WSL launcher, which exits 1 for every script when no distribution
    is installed. Trusting it inverted every verdict in these tests while they
    still ran and reported. So the interpreter is asked to prove it can return a
    known failure and a known success before any observation is believed.
    """
    candidates = [
        shutil.which("bash"),
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        "/bin/bash",
        "/usr/bin/bash",
    ]
    for candidate in candidates:
        if not candidate or not Path(candidate).is_file():
            continue
        try:
            fails = subprocess.run(
                [candidate, "-c", _GATE + "gate"], capture_output=True, timeout=60
            )
            passes = subprocess.run(
                [candidate, "-c", "true | tee /dev/null"],
                capture_output=True,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if fails.returncode == 7 and passes.returncode == 0:
            return candidate
    return None


_BASH = _usable_bash()

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


def test_an_earlier_disable_reaches_a_substitution_on_the_same_line() -> None:
    """A substitution inherits the option state where it runs, not where the line starts.

    `set +o pipefail; result=$(gate | tee log)` returns 0. Seeding the
    substitution scan from the line's incoming state, before the outer segments
    applied the disable, let it pass — and masking the substitution then stopped
    the line-level scan from correcting the verdict.
    """
    body = _step(
        """
        set -o pipefail
        set +o pipefail; result=$(gate.py | tee log)
        """
    )

    assert validator.unguarded_pipelines(body) == [
        "set +o pipefail; result=$(gate.py | tee log)"
    ]


def test_a_nested_substitution_is_scanned(tmp_path=None) -> None:
    """`$(echo $(gate | tee log))` hides the gate one level down.

    Read as a single body, the outer substitution's upstream is `echo`, which
    has no verdict to lose. The nested one runs on its own and drops the gate's
    status exactly as the outer would.
    """
    body = _step("result=$(echo $(gate.py | tee log))")

    assert validator.unguarded_pipelines(body) == ["result=$(echo $(gate.py | tee log))"]


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


def _step(body: str) -> str:
    """Wrap shell lines as a workflow step's run: block."""
    indented = "\n".join(f"          {line}" for line in body.strip().splitlines())
    return f"run: |\n{indented}\n"


def test_subshell_pipeline_still_hides_its_gate() -> None:
    """`( gate | tee )` exits with tee's status; the parens change nothing."""
    assert validator.unguarded_pipelines(_step("( gate.py | tee log )")) == [
        "( gate.py | tee log )"
    ]


def test_subshell_that_enables_pipefail_inside_itself_is_accepted() -> None:
    """The option is scoped to the subshell, and the pipeline is inside it too."""
    assert validator.unguarded_pipelines(_step("( set -o pipefail; gate.py | tee log )")) == []


def test_subshell_inherits_an_outer_guard() -> None:
    """pipefail set outside applies inside; reporting this would over-reject."""
    body = _step(
        """
        set -o pipefail
        ( gate.py | tee log )
        """
    )
    assert validator.unguarded_pipelines(body) == []


def test_subshell_propagating_pipestatus_is_accepted() -> None:
    body = _step("( gate.py | tee log; exit ${PIPESTATUS[0]} )")
    assert validator.unguarded_pipelines(body) == []


def test_conditionally_called_enabling_function_does_not_guard() -> None:
    """`cond && enable_strict` may never call it, so the guard is not certain."""
    body = _step(
        """
        enable_strict() { set -o pipefail; }
        [ -n "$STRICT" ] && enable_strict
        gate.py | tee log
        """
    )
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_conditional_pipefail_inside_a_function_does_not_guard() -> None:
    """Calling the function is certain; the `set` inside its `if` is not."""
    body = _step(
        """
        enable_strict() {
        if [ -n "$STRICT" ]; then
        set -o pipefail
        fi
        }
        enable_strict
        gate.py | tee log
        """
    )
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_function_that_disables_pipefail_invalidates_the_guard() -> None:
    """Losing the guard needs no certainty: a call that may disable it is enough."""
    body = _step(
        """
        set -o pipefail
        relax() { set +o pipefail; }
        relax
        gate.py | tee log
        """
    )
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_conditional_literal_pipefail_does_not_guard() -> None:
    """The certainty rule is about position, not only about block depth."""
    body = _step(
        """
        [ -n "$STRICT" ] && set -o pipefail
        gate.py | tee log
        """
    )
    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_an_offending_line_is_reported_once() -> None:
    """A substitution pipeline and its segment are the same defect, not two."""
    body = _step("result=$(gate.py | tee log)")
    assert validator.unguarded_pipelines(body) == ["result=$(gate.py | tee log)"]


# --- Fidelity: the validator's verdict against real shell behaviour ----------
#
# Every rule above is a claim about what Bash does. Two estate rules were
# recently found to be false because nobody ran the thing they described, so
# these shapes are executed rather than argued: a shape is only called a defect
# if a gate that exits 7 really does produce a step status of 0.

_HIDES_THE_STATUS = {
    "plain pipeline": "gate | tee /dev/null",
    "subshell pipeline": "( gate | tee /dev/null )",
    "conditionally called enabler": (
        "enable_strict() { set -o pipefail; }\n"
        'STRICT=""\n'
        '[ -n "$STRICT" ] && enable_strict\n'
        "gate | tee /dev/null"
    ),
    "conditional pipefail in a function": (
        'enable_strict() { if [ -n "$STRICT" ]; then set -o pipefail; fi; }\n'
        'STRICT=""\n'
        "enable_strict\n"
        "gate | tee /dev/null"
    ),
    "function that disables pipefail": (
        "set -o pipefail\n"
        "relax() { set +o pipefail; }\n"
        "relax\n"
        "gate | tee /dev/null"
    ),
    "conditional literal pipefail": (
        'STRICT=""\n[ -n "$STRICT" ] && set -o pipefail\ngate | tee /dev/null'
    ),
    "enabler called inside a subshell": (
        "enable_strict() { set -o pipefail; }\n"
        "( enable_strict )\n"
        "gate | tee /dev/null"
    ),
    "guarded subshell piped into a sink": (
        "( set -o pipefail; gate | tee /dev/null ) | tee /dev/null"
    ),
    "function whose last act disables": (
        "both() { set -o pipefail; set +o pipefail; }\nboth\ngate | tee /dev/null"
    ),
    "multiline subshell enabling for itself only": (
        "(\n  set -o pipefail\n)\ngate | tee /dev/null"
    ),
    "multiline subshell piped onward": (
        "(\n  set -o pipefail\n  gate | tee /dev/null\n) | tee /dev/null"
    ),
    "parenthesis inside a comment": (
        "# phase (\ngate | tee /dev/null\n# )"
    ),
    "outer disabling function called in a subshell": (
        "set -o pipefail\n"
        "relax() { set +o pipefail; }\n"
        "( relax; gate | tee /dev/null )"
    ),
    "failure consumed by a recovery operator": (
        "set -o pipefail\ngate | tee /dev/null || true"
    ),
    "conditional guard inside a substitution": (
        "result=$(if false; then set -o pipefail; fi; gate | tee /dev/null)\n"
        "exit 0"
    ),
}

_PROPAGATES_THE_STATUS = {
    "top-level pipefail": "set -o pipefail\ngate | tee /dev/null",
    "called enabler": (
        "enable_strict() { set -o pipefail; }\nenable_strict\ngate | tee /dev/null"
    ),
    "pipestatus capture": (
        'gate | tee /dev/null\nstatus=${PIPESTATUS[0]}\nexit "$status"'
    ),
    "subshell guarding itself": "( set -o pipefail; gate | tee /dev/null )",
    "subshell inheriting the guard": "set -o pipefail\n( gate | tee /dev/null )",
    "subshell propagating pipestatus": "( gate | tee /dev/null; exit ${PIPESTATUS[0]} )",
    "function that restores what it disabled": (
        "set -o pipefail\n"
        "reset() { set +o pipefail; set -o pipefail; }\n"
        "reset\n"
        "gate | tee /dev/null"
    ),
    "outer pipefail reaches inside a piped subshell": (
        "set -o pipefail\n( gate | tee /dev/null ) | tee /dev/null"
    ),
    "multiline subshell guarding its own pipeline": (
        "(\n  set -o pipefail\n  gate | tee /dev/null\n)"
    ),
    "outer enabling function called in a subshell": (
        "enable_strict() { set -o pipefail; }\n"
        "( enable_strict; gate | tee /dev/null )"
    ),
    "recovery operator that propagates": (
        "set -o pipefail\ngate | tee /dev/null || exit 7"
    ),
}


def _observed_status(script: str) -> int:
    """Run the shape with a failing `gate` and report what the shell exits with."""
    assert _BASH is not None
    return subprocess.run(
        [_BASH, "-c", _GATE + script], capture_output=True, timeout=60
    ).returncode


@pytest.mark.skipif(
    _BASH is None, reason="no bash on this machine could report a known exit status"
)
@pytest.mark.parametrize("label", sorted(_HIDES_THE_STATUS))
def test_reported_shapes_really_do_hide_a_failing_gate(label: str) -> None:
    """A shape is only a defect if a failing gate really yields a passing step."""
    script = _HIDES_THE_STATUS[label]
    assert _observed_status(script) == 0, (
        f"{label}: bash propagated the failure, so this shape is not a defect "
        "and the validator must not report it"
    )
    assert validator.unguarded_pipelines(_step(script)), (
        f"{label}: a gate exiting 7 produced a step status of 0 and the "
        "validator stayed silent"
    )


@pytest.mark.skipif(
    _BASH is None, reason="no bash on this machine could report a known exit status"
)
@pytest.mark.parametrize("label", sorted(_PROPAGATES_THE_STATUS))
def test_accepted_shapes_really_do_propagate_a_failing_gate(label: str) -> None:
    """The other direction: a gate that rejects correct work is a gate people switch off."""
    script = _PROPAGATES_THE_STATUS[label]
    assert _observed_status(script) == 7, (
        f"{label}: bash swallowed the failure, so this shape should be reported"
    )
    assert validator.unguarded_pipelines(_step(script)) == [], (
        f"{label}: bash reported the gate's failure, but the validator "
        "rejected the step anyway"
    )


def test_the_shell_fidelity_harness_found_a_usable_interpreter() -> None:
    """Skipping every fidelity case would be invisible; say so out loud.

    This is a report, not a gate: a machine with no usable bash is a legitimate
    state. What is not legitimate is discovering months later that the fidelity
    evidence has been skipped the whole time.
    """
    if _BASH is None:  # pragma: no cover - depends on the machine
        pytest.skip(
            "no bash on this machine could report a known exit status, so the "
            "shell-fidelity evidence is NOT being collected here"
        )
    assert _observed_status("gate") == 7


def test_a_subshell_piped_into_a_sink_loses_its_own_status() -> None:
    """Guarding the inside does not save the subshell's own exit status.

    `( set -o pipefail; gate | tee a ) | tee b` propagates the gate inside the
    parentheses and then hands the whole subshell's status to the outer `tee`,
    which reports 0. Judging only the interior accepted a step that cannot fail.
    """
    body = _step("( set -o pipefail; gate.py | tee inner ) | tee outer")

    assert validator.unguarded_pipelines(body) == [
        "( set -o pipefail; gate.py | tee inner ) | tee outer"
    ]


def test_a_subshell_not_piped_onwards_is_judged_only_on_its_inside() -> None:
    """The acceptance that stops the rule above from over-rejecting."""
    body = _step("( set -o pipefail; gate.py | tee inner )")

    assert validator.unguarded_pipelines(body) == []


def test_an_outer_guard_covers_a_piped_subshell() -> None:
    body = _step(
        """
        set -o pipefail
        ( gate.py | tee inner ) | tee outer
        """
    )

    assert validator.unguarded_pipelines(body) == []


def test_a_function_that_restores_pipefail_still_guards() -> None:
    """What reaches the caller is the state the function leaves, not every state it passes."""
    body = _step(
        """
        set -o pipefail
        reset() { set +o pipefail; set -o pipefail; }
        reset
        gate.py | tee log
        """
    )

    assert validator.unguarded_pipelines(body) == []


def test_a_function_whose_last_act_disables_pipefail_loses_the_guard() -> None:
    """The other direction, so restoring is read as ordering rather than as leniency."""
    body = _step(
        """
        both() { set -o pipefail; set +o pipefail; }
        both
        gate.py | tee log
        """
    )

    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_a_conditional_restore_does_not_bring_the_guard_back() -> None:
    """Turning the guard back on still requires certainty; turning it off never does."""
    body = _step(
        """
        set -o pipefail
        risky() { set +o pipefail; if [ -n "$STRICT" ]; then set -o pipefail; fi; }
        risky
        gate.py | tee log
        """
    )

    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_a_multiline_subshell_does_not_guard_the_lines_after_it() -> None:
    """Read line by line, `(` alone is an empty subshell and the `set` looks top-level.

    The option was then credited to every pipeline after the closing paren, so
    a gate exiting 7 produced a step status of 0 and nothing was reported. An
    earlier revision of this module documented that limitation as one that could
    only over-report; it could miss.
    """
    body = _step(
        """
        (
        set -o pipefail
        )
        gate.py | tee log
        """
    )

    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_a_multiline_subshell_still_guards_its_own_pipeline() -> None:
    """The acceptance: folding the block must not cost it the guard it really has."""
    body = _step(
        """
        (
        set -o pipefail
        gate.py | tee log
        )
        """
    )

    assert validator.unguarded_pipelines(body) == []


def test_unbalanced_parentheses_are_not_guessed_at() -> None:
    """A quoted paren is not a subshell, and the pipeline after it is still judged."""
    body = _step(
        """
        echo "("
        gate.py | tee log
        """
    )

    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_a_parenthesis_in_a_comment_does_not_open_a_subshell() -> None:
    """Comments used as visual delimiters must not swallow the commands between them.

    Folding a multiline subshell counts parentheses. Counting them inside
    comments too meant `# phase (` began a fold that ran to `# )`, joining every
    command between into one line starting with `#`, which the scanner skips
    wholesale. The pipeline it was meant to judge disappeared.
    """
    body = _step(
        """
        # phase (
        gate.py | tee log
        # )
        """
    )

    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_a_subshell_of_trivial_producers_is_still_trivial() -> None:
    """`( printf x ) | tee log` hides no verdict, exactly as `printf x | tee log` does.

    Standing the subshell in as a synthetic producer discarded what it
    contained, so wrapping a harmless producer in parentheses turned it into a
    reported gate.
    """
    assert validator.unguarded_pipelines(_step("( printf x ) | tee out.txt")) == []
    assert validator.unguarded_pipelines(_step("printf x | tee out.txt")) == []


def test_a_subshell_containing_a_real_gate_is_still_reported() -> None:
    """The acceptance above must not become a way to hide a gate in parentheses."""
    body = _step("( gate.py ) | tee out.txt")

    assert validator.unguarded_pipelines(body) == ["( gate.py ) | tee out.txt"]


def test_a_subshell_inherits_the_functions_defined_outside_it() -> None:
    """A subshell can call a function defined by its caller.

    Recomputing the function tables from the subshell body alone made `relax`
    invisible inside `( relax; gate | tee log )`, so a subshell that really does
    turn the guard off was accepted while Bash returned 0 for a gate exiting 7.
    """
    body = _step(
        """
        set -o pipefail
        relax() { set +o pipefail; }
        ( relax; gate.py | tee log )
        """
    )

    assert validator.unguarded_pipelines(body) == ["( relax; gate.py | tee log )"]


def test_an_inherited_enabling_function_still_guards_inside_a_subshell() -> None:
    """The acceptance: inheriting functions must work in both directions."""
    body = _step(
        """
        enable_strict() { set -o pipefail; }
        ( enable_strict; gate.py | tee log )
        """
    )

    assert validator.unguarded_pipelines(body) == []


def test_a_command_substitution_can_guard_its_own_pipeline() -> None:
    """`$( )` is a scope, not just text: a `set -o pipefail` inside one applies.

    Judging the inside against the outer option state reported a substitution
    whose failure Bash propagates correctly, which is the direction that gets a
    gate switched off.
    """
    body = _step(
        """
        result=$(
        set -o pipefail
        gate.py | tee log
        )
        """
    )

    assert validator.unguarded_pipelines(body) == []


def test_an_unguarded_command_substitution_is_still_reported() -> None:
    """The opposite direction, so the scope rule is not a way to hide a gate."""
    body = _step("result=$(gate.py | tee log)")

    assert validator.unguarded_pipelines(body) == ["result=$(gate.py | tee log)"]


def test_a_pipeline_beside_a_substitution_is_judged_on_its_own() -> None:
    """Masking the substitution must not blind the scan to the rest of the line."""
    body = _step(
        """
        x=$(echo hi)
        gate.py | tee log
        """
    )

    assert validator.unguarded_pipelines(body) == ["gate.py | tee log"]


def test_a_failure_consumed_by_a_recovery_operator_is_reported() -> None:
    """pipefail delivers the status to something that throws it away.

    `gate | tee log || true` reaches the step with the gate's verdict and then
    discards it, so the step passes whatever the gate decided. Reported
    regardless of pipefail, because pipefail is working correctly here — it is
    the operator after it that removes the failure.
    """
    body = _step(
        """
        set -o pipefail
        gate.py | tee log || true
        """
    )

    assert validator.unguarded_pipelines(body) == ["gate.py | tee log || true"]


def test_a_subshell_that_guards_itself_still_loses_a_consumed_status() -> None:
    """The inner scan being clean is not enough: the subshell has its own status.

    `( set -o pipefail; gate | tee log ) || true` propagates correctly inside
    the parentheses and is then discarded outside them, so the interior looks
    right and the step still cannot fail.
    """
    body = _step("( set -o pipefail; gate.py | tee log ) || true")

    assert validator.unguarded_pipelines(body) == [
        "( set -o pipefail; gate.py | tee log ) || true"
    ]


def test_a_trivial_subshell_may_have_its_status_consumed() -> None:
    """`( echo hi ) || true` has no verdict to lose, so consuming it hides nothing."""
    assert validator.unguarded_pipelines(_step("( echo hi ) || true")) == []


def test_a_subshell_whose_status_propagates_is_accepted() -> None:
    body = _step("( set -o pipefail; gate.py | tee log ) || exit 1")

    assert validator.unguarded_pipelines(body) == []


def test_a_recovery_operator_that_propagates_is_accepted() -> None:
    """`|| exit 1` is how a step reports a failure before failing."""
    body = _step(
        """
        set -o pipefail
        gate.py | tee log || exit 1
        """
    )

    assert validator.unguarded_pipelines(body) == []


def test_a_conditional_guard_inside_a_substitution_does_not_count() -> None:
    """A substitution has blocks exactly as the outer shell does.

    Following a `;` makes a command certain to be *reached*, not certain to be
    *executed*, and the substitution-local scan tracked the first without the
    second.
    """
    body = _step("result=$(if false; then set -o pipefail; fi; gate.py | tee log)")

    assert validator.unguarded_pipelines(body) == [
        "result=$(if false; then set -o pipefail; fi; gate.py | tee log)"
    ]


def test_an_unconditional_guard_inside_a_substitution_still_counts() -> None:
    body = _step("result=$(set -o pipefail; gate.py | tee log)")

    assert validator.unguarded_pipelines(body) == []


def test_a_local_definition_shadows_an_inherited_function() -> None:
    """Bash resolves a call to the most recent definition, not to both.

    Keeping the inherited summary let a redefined `relax` go on disabling a
    guard it no longer touches, rejecting a pipeline Bash propagates correctly.
    """
    body = _step(
        """
        set -o pipefail
        relax() { set +o pipefail; }
        ( relax() { :; }; relax; gate.py | tee log )
        """
    )

    assert validator.unguarded_pipelines(body) == []


def test_an_inherited_function_still_applies_when_not_redefined() -> None:
    """The acceptance above must not stop inheritance working at all."""
    body = _step(
        """
        set -o pipefail
        relax() { set +o pipefail; }
        ( relax; gate.py | tee log )
        """
    )

    assert validator.unguarded_pipelines(body) == ["( relax; gate.py | tee log )"]
