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
    audit_repository,
    main,
    parse_makefile,
    reachable_targets,
    workflow_invoked_targets,
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
    assert len(cannot_fail) == 2
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
    assert "inspected 1 repositories and 0 gate targets" in stderr


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

    invoked = workflow_invoked_targets(
        "- run: make real-gate\n- run: make not-a-target\n", targets
    )

    assert invoked == {"real-gate"}
