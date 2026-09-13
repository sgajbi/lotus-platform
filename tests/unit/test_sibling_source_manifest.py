"""The sibling source manifest pins what the per-commit lanes read, and the pins are measured.

`Main Releasability Gate` certifies one lotus-platform commit while reading twelve
sibling repositories. Unpinned, its verdict was a function of every sibling's main
at run time (#858, #708). The manifest makes those inputs part of the revision under
test; these tests prove the validator refuses every way the manifest or a checkout
could quietly fall back to "whatever the default branch is now".
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMMITTED_MANIFEST = (
    ROOT / "platform-contracts" / "ci-governance" / "sibling-source-manifest.v1.json"
)
COMMITTED_REGISTRY = ROOT / "automation" / "repos.json"
VALIDATOR_PATH = ROOT / "automation" / "validate_sibling_source_manifest.py"
LANE_WORKFLOWS = ("feature-lane.yml", "pr-merge-gate.yml", "main-releasability.yml")


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_sibling_source_manifest", VALIDATOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Dataclasses resolve postponed annotations through sys.modules; an
    # unregistered module makes that lookup return None at class creation.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


manifest_validator = _load_validator()


def _registry() -> dict[str, manifest_validator.RegisteredSibling]:
    return manifest_validator.registered_siblings(COMMITTED_REGISTRY)


def _committed_manifest() -> dict:
    return json.loads(COMMITTED_MANIFEST.read_text(encoding="utf-8"))


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _errors(tmp_path: Path, payload: dict) -> list[str]:
    _sources, errors = manifest_validator.load_manifest(_write(tmp_path, payload), _registry())
    return errors


def test_the_committed_manifest_pins_every_registered_sibling_exactly_once() -> None:
    sources, errors = manifest_validator.load_manifest(COMMITTED_MANIFEST, _registry())

    assert errors == []
    assert sorted(source.repository for source in sources) == sorted(_registry())
    assert all(manifest_validator.FULL_SHA.fullmatch(source.revision) for source in sources)


def test_a_missing_sibling_is_refused_because_an_unpinned_checkout_falls_back(
    tmp_path: Path,
) -> None:
    """The failure this exists to end: no entry means `actions/checkout` takes the
    default branch, silently, which is the unpinned lane again."""
    payload = _committed_manifest()
    dropped = payload["sources"].pop()

    errors = _errors(tmp_path, payload)

    assert any(dropped["repository"] in error and "no pin" in error for error in errors), errors


@pytest.mark.parametrize(
    ("mutation", "fragment"),
    [
        (lambda entry: entry.update(revision=entry["revision"][:12]), "full lowercase commit SHA"),
        (lambda entry: entry.update(revision=entry["revision"].upper()), "full lowercase commit SHA"),
        (lambda entry: entry.update(github="sgajbi/lotus-elsewhere"), "github must be"),
        (lambda entry: entry.update(branch="develop"), "registered default"),
        (lambda entry: entry.update(committed_at_utc="yesterday"), "committed_at_utc"),
    ],
)
def test_a_pin_that_cannot_name_one_revision_is_refused(tmp_path: Path, mutation, fragment) -> None:
    payload = _committed_manifest()
    mutation(payload["sources"][0])

    errors = _errors(tmp_path, payload)

    assert any(fragment in error for error in errors), errors


def test_a_sibling_pinned_twice_or_unregistered_is_refused(tmp_path: Path) -> None:
    payload = _committed_manifest()
    payload["sources"].append(dict(payload["sources"][0]))
    payload["sources"].append({**payload["sources"][1], "repository": "lotus-unknown"})

    errors = _errors(tmp_path, payload)

    assert any("pinned more than once" in error for error in errors), errors
    assert any("lotus-unknown" in error and "not a registered sibling" in error for error in errors)


def test_a_wrong_schema_or_timestamp_is_refused(tmp_path: Path) -> None:
    payload = _committed_manifest()
    payload["schema_version"] = "lotus.sibling-source-manifest.v0"
    payload["recorded_at_utc"] = "2026-09-13T05:18:26+08:00"

    errors = _errors(tmp_path, payload)

    assert any("schema_version" in error for error in errors)
    assert any("recorded_at_utc" in error for error in errors)


def test_github_output_carries_every_pin_under_its_repository_name(tmp_path: Path) -> None:
    """Each checkout step binds `ref:` to this output, so the name is the contract."""
    sources, errors = manifest_validator.load_manifest(COMMITTED_MANIFEST, _registry())
    assert errors == []
    output = tmp_path / "github_output"
    output.write_text("earlier=kept\n", encoding="utf-8")

    manifest_validator.emit_github_output(sources, output)

    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "earlier=kept", "GITHUB_OUTPUT is appended to, never truncated"
    assert dict(line.split("=", 1) for line in lines[1:]) == {
        source.repository: source.revision for source in sources
    }


def _git_environment(tmp_path: Path) -> dict[str, str]:
    empty = tmp_path / "gitconfig"
    empty.touch()
    return {
        **os.environ,
        "GIT_CONFIG_GLOBAL": str(empty),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }


def _repository_with_two_commits(tmp_path: Path, name: str) -> tuple[Path, str, str]:
    environment = _git_environment(tmp_path)
    path = tmp_path / name
    path.mkdir()

    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=path, env=environment, capture_output=True, text=True, check=True
        ).stdout.strip()

    git("init", "-q", "-b", "main")
    git("commit", "-q", "--allow-empty", "-m", "pinned")
    pinned = git("rev-parse", "HEAD")
    git("commit", "-q", "--allow-empty", "-m", "moved past the pin")
    moved = git("rev-parse", "HEAD")
    return path, pinned, moved


def test_verify_checkouts_measures_head_against_the_pin(tmp_path: Path) -> None:
    """A checkout at any other revision -- including the default branch the pin was
    taken from after it moved -- is a mismatch, and a missing checkout is not a pass."""
    federated = tmp_path / "federated"
    federated.mkdir()
    path, pinned, moved = _repository_with_two_commits(federated, "lotus-core")
    sources = [
        manifest_validator.SiblingSource("lotus-core", "sgajbi/lotus-core", "main", pinned, "2026-09-11T06:07:23Z"),
        manifest_validator.SiblingSource("lotus-risk", "sgajbi/lotus-risk", "main", moved, "2026-09-08T13:54:13Z"),
    ]

    at_moved_head = manifest_validator.verify_checkouts(sources, federated)
    assert any("lotus-core" in error and pinned in error and moved in error for error in at_moved_head)
    assert any("lotus-risk" in error and "no checkout" in error for error in at_moved_head)

    subprocess.run(
        ["git", "checkout", "-q", "--detach", pinned],
        cwd=path,
        env=_git_environment(tmp_path),
        check=True,
        capture_output=True,
    )
    at_pin = manifest_validator.verify_checkouts(sources[:1], federated)
    assert at_pin == []


@pytest.mark.parametrize(
    ("current", "ahead_by", "behind_by", "refresh_age_days", "expected", "fails"),
    [
        ("c" * 40, 0, 0, 2, "CURRENT", False),
        # A sibling quiet for a month whose pin still equals its main is not stale,
        # however old the refresh: there is nothing a refresh would change.
        ("c" * 40, 0, 0, 400, "CURRENT", False),
        ("b" * 40, 3, 0, 2, "DRIFTED", False),
        ("b" * 40, 3, 0, 19, "STALE", True),
        ("b" * 40, None, 0, 1, "UNRESOLVED", True),
        ("b" * 40, 3, None, 1, "UNRESOLVED", True),
        # A comparison that calls two different SHAs identical is not trustworthy.
        ("b" * 40, 0, 0, 1, "UNRESOLVED", True),
        ("b" * 40, 0, 2, 1, "BEHIND", True),
        ("b" * 40, 2, 1, 1, "DIVERGED", True),
        # Divergence is a finding about the sibling's history, never softened by age.
        ("b" * 40, 2, 1, 400, "DIVERGED", True),
        (None, None, None, 1, "UNREAD", True),
    ],
    ids=[
        "current",
        "quiet-but-current",
        "drifted-fresh",
        "stale",
        "no-ahead-count",
        "no-behind-count",
        "identical-compare-unequal-shas",
        "rolled-back-main",
        "diverged",
        "diverged-old-refresh",
        "unread",
    ],
)
def test_every_drift_posture_is_explicit_and_only_positive_answers_pass(
    current: str | None,
    ahead_by: int | None,
    behind_by: int | None,
    refresh_age_days: int,
    expected: str,
    fails: bool,
) -> None:
    """Unequal SHAs need a trustworthy two-way comparison; a missing, one-sided or
    self-contradicting one is a finding, not `CURRENT`, and staleness is measured from the
    manifest refresh, which a refresh clears."""
    drift = manifest_validator.PinDrift(
        "lotus-core", "c" * 40, current, ahead_by, behind_by, refresh_age_days
    )

    posture = drift.posture(max_pin_age_days=14)

    assert posture == expected
    assert (posture in manifest_validator.FAILING_POSTURES) is fails
    assert f"| lotus-core |" in manifest_validator.drift_markdown([drift], max_pin_age_days=14)
    assert f"| {expected} |" in manifest_validator.drift_markdown([drift], max_pin_age_days=14)


def test_refresh_age_comes_from_the_manifest_not_the_pinned_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The reviewer's case: a pin committed long ago, manifest refreshed today, main unchanged."""
    payload = _committed_manifest()
    payload["recorded_at_utc"] = "2026-09-30T00:00:00Z"
    payload["sources"] = [dict(payload["sources"][0], committed_at_utc="2026-01-01T00:00:00Z")]
    manifest = _write(tmp_path, payload)
    pinned = payload["sources"][0]["revision"]
    monkeypatch.setattr(
        manifest_validator,
        "_gh_json",
        lambda *args: {"commit": {"sha": pinned}} if "/branches/" in args[0] else None,
    )
    sources = [
        manifest_validator.SiblingSource(
            s["repository"], s["github"], s["branch"], s["revision"], s["committed_at_utc"]
        )
        for s in payload["sources"]
    ]

    drifts = manifest_validator.report_drift(
        sources,
        now=datetime(2026, 9, 30, 12, tzinfo=UTC),
        recorded_at=manifest_validator.manifest_recorded_at(manifest),
    )

    assert drifts[0].refresh_age_days == 0
    assert drifts[0].posture(max_pin_age_days=14) == "CURRENT"
    assert manifest_validator.manifest_recorded_at(tmp_path / "absent.json") is None


@pytest.mark.parametrize("workflow", LANE_WORKFLOWS)
def test_every_per_commit_lane_binds_each_sibling_checkout_to_the_manifest(workflow: str) -> None:
    """The lanes must not retype a revision: each `ref:` is the manifest's output
    for that repository, and the checkouts are verified against the pin afterwards."""
    text = (ROOT / ".github" / "workflows" / workflow).read_text(encoding="utf-8")

    assert "validate_sibling_source_manifest.py --github-output" in text
    for repository in _registry():
        assert f"repository: sgajbi/{repository}" in text
        assert f"ref: ${{{{ steps.sibling-pins.outputs.{repository} }}}}" in text, (
            f"{workflow}: {repository} is checked out without its manifest pin"
        )
    assert "validate_sibling_source_manifest.py --verify-checkouts _federated" in text
    assert text.index("--github-output") < text.index("--verify-checkouts")


def test_the_fleet_lane_reads_current_mains_on_purpose_and_reports_pin_drift() -> None:
    text = (ROOT / ".github" / "workflows" / "fleet-conformance.yml").read_text(encoding="utf-8")

    assert "schedule:" in text
    assert "ref: ${{ steps.sibling-pins" not in text, "the fleet lane is the unpinned view"
    assert "-Lane fleet-conformance" in text
    # Evidence reaches the owner even when the lane fails.
    assert "if: always()" in text and "path: output/" in text


def test_the_fleet_lane_runs_every_check_to_completion_and_fails_on_the_aggregate() -> None:
    """A drift finding must not hide the conformance verdicts behind it, and no
    check may pass on the strength of an earlier one having thrown."""
    runner = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(encoding="utf-8")
    fleet = runner.split('if ($Lane -eq "fleet-conformance")')[1].split("\n        return\n")[0]

    assert "Invoke-CheckedCommand" not in fleet, "a throwing runner stops the later checks"
    for check in (
        "sibling-pin-drift",
        "auto-merge-releasability",
        "workflow-pipeline-exit-codes",
        "canonical-front-office-demo-data",
    ):
        assert f'-Name "{check}"' in fleet, f"{check} is not run as a recorded check"
    # The native exit code is read straight after the invocation and before
    # anything else can reset it, then recorded per check.
    assert "$exitCode = $LASTEXITCODE" in fleet and "$fleetOutcomes[$Name] = $exitCode" in fleet
    # Evidence: only one validator writes its own report under output/; the rest
    # speak on stdout, so each check's combined output is captured to a log the
    # lane uploads, the drift table is always written there, and so is the
    # outcome table.
    assert "2>&1 | Tee-Object -FilePath $log" in fleet
    assert 'output/fleet-conformance' in fleet
    assert '"pin-drift.md"' in fleet and '"outcomes.md"' in fleet
    assert '"--summary", $driftReport' in fleet, "the drift table must be evidence, not only a step summary"
    assert 'throw "Fleet conformance failed:' in fleet
    assert fleet.index("Fleet conformance outcomes") < fleet.index('throw "Fleet conformance failed:'), (
        "the outcome table must be published before the aggregate failure is raised"
    )


# --- the CLI boundary: what the fleet lane actually runs --------------------


def _drift_cli(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    recorded_at_utc: str,
    current_by_repo: dict[str, str | None],
    compare_by_repo: dict[str, object],
) -> tuple[int, str, str]:
    """Run `--report-drift` end to end with the GitHub boundary scripted per sibling."""
    payload = _committed_manifest()
    payload["recorded_at_utc"] = recorded_at_utc
    manifest = _write(tmp_path, payload)
    github_of = {source["repository"]: source["github"] for source in payload["sources"]}
    repo_of = {github: repository for repository, github in github_of.items()}

    def gh_json(*args: str) -> object | None:
        path = args[0]
        for github, repository in repo_of.items():
            if path.startswith(f"repos/{github}/branches/"):
                current = current_by_repo.get(repository, "pinned")
                if current == "pinned":
                    current = next(s["revision"] for s in payload["sources"] if s["repository"] == repository)
                return None if current is None else {"commit": {"sha": current}}
            if path.startswith(f"repos/{github}/compare/"):
                return compare_by_repo.get(repository)
        raise AssertionError(f"unexpected gh api call: {path}")

    monkeypatch.setattr(manifest_validator, "_gh_json", gh_json)
    summary = tmp_path / "summary.md"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_sibling_source_manifest.py",
            "--manifest", str(manifest),
            "--registry", str(COMMITTED_REGISTRY),
            "--report-drift",
            "--summary", str(summary),
        ],
    )
    import io
    from contextlib import redirect_stdout

    captured = io.StringIO()
    with redirect_stdout(captured):
        exit_code = manifest_validator.main()
    return exit_code, captured.getvalue(), summary.read_text(encoding="utf-8")


def test_cli_an_unavailable_comparison_is_unresolved_and_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exit_code, out, summary = _drift_cli(
        tmp_path,
        monkeypatch,
        recorded_at_utc="2026-09-13T00:00:00Z",
        current_by_repo={"lotus-core": "b" * 40},
        compare_by_repo={"lotus-core": None},
    )

    assert exit_code == 1
    assert "lotus-core=UNRESOLVED" in out
    assert "| lotus-core |" in summary and "| UNRESOLVED |" in summary
    assert "CURRENT" not in [line.split("|")[-2].strip() for line in summary.splitlines() if "lotus-core" in line]


def test_cli_an_old_refresh_with_unchanged_current_shas_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The reviewer's case at the boundary: nothing to refresh, so nothing is stale."""
    exit_code, out, summary = _drift_cli(
        tmp_path,
        monkeypatch,
        recorded_at_utc="2026-01-01T00:00:00Z",
        current_by_repo={},
        compare_by_repo={},
    )

    assert exit_code == 0
    assert "Fleet drift findings" not in out
    assert summary.count("| CURRENT |") == len(_registry())


@pytest.mark.parametrize(
    ("compare", "expected"),
    [
        ({"ahead_by": 0, "behind_by": 3}, "BEHIND"),
        ({"ahead_by": 4, "behind_by": 2}, "DIVERGED"),
        ({"ahead_by": 0, "behind_by": 0}, "UNRESOLVED"),
        ({"ahead_by": "many", "behind_by": 0}, "UNRESOLVED"),
    ],
    ids=["rolled-back", "diverged", "identical-claim", "malformed-count"],
)
def test_cli_behind_diverged_and_malformed_comparisons_fail_with_their_own_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, compare: dict, expected: str
) -> None:
    exit_code, out, _summary = _drift_cli(
        tmp_path,
        monkeypatch,
        recorded_at_utc="2026-09-13T00:00:00Z",
        current_by_repo={"lotus-risk": "d" * 40},
        compare_by_repo={"lotus-risk": compare},
    )

    assert exit_code == 1
    assert f"lotus-risk={expected}" in out


def test_cli_combined_failures_are_all_named_and_information_is_not(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exit_code, out, summary = _drift_cli(
        tmp_path,
        monkeypatch,
        recorded_at_utc="2026-09-13T00:00:00Z",
        current_by_repo={"lotus-ai": None, "lotus-render": "e" * 40, "lotus-report": "f" * 40},
        compare_by_repo={
            "lotus-render": {"ahead_by": 2, "behind_by": 1},
            "lotus-report": {"ahead_by": 5, "behind_by": 0},
        },
    )

    assert exit_code == 1
    findings = next(line for line in out.splitlines() if line.startswith("Fleet drift findings:"))
    assert "lotus-ai=UNREAD" in findings and "lotus-render=DIVERGED" in findings
    assert "lotus-report" not in findings, "DRIFTED is information, not a finding"
    assert "| lotus-report |" in summary and "| DRIFTED |" in summary
