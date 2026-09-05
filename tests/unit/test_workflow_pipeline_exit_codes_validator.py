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
