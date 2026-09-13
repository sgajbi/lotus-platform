"""The fixed-range ledger records what a rolling window forgets.

Measured on 2026-09-13: the scheduled seven-day audit reported 174 examined / 116 ungated on
09-12 and 116 / 79 one day later. Thirty-seven revisions with no verdict left the window with
no record. `--range BASE..END` makes the range the claim - exact endpoints, first-parent walk,
no cap - and `--ledger-out` writes the verdicts so a reviewed pull request can commit them.

Git is real here because the walk is the subject; only the run lookup is faked, at the
function boundary, since the rolling-window tests already cover that transport.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from automation import audit_main_gate_coverage as audit


def _environment(tmp_path: Path) -> dict[str, str]:
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


class Repo:
    def __init__(self, tmp_path: Path) -> None:
        self.path = tmp_path / "repo"
        self.path.mkdir()
        self.environment = _environment(tmp_path)
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.path, env=self.environment, capture_output=True, text=True, check=True
        ).stdout.strip()

    def commit(self, subject: str) -> str:
        self.git("commit", "-q", "--allow-empty", "-m", subject)
        return self.git("rev-parse", "HEAD")

    def publish_main(self) -> None:
        """origin/main is what the audit judges against; point it at HEAD."""
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Repo:
    repository = Repo(tmp_path)
    monkeypatch.chdir(repository.path)
    for name, value in repository.environment.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(audit.shutil, "which", lambda name: "/usr/bin/gh")
    return repository


def _audit(monkeypatch: pytest.MonkeyPatch, argv: list[str]) -> int:
    monkeypatch.setattr("sys.argv", ["audit_main_gate_coverage.py", *argv])
    return audit.main()


def _fake_runs(monkeypatch: pytest.MonkeyPatch, runs: dict[str, object]) -> None:
    def conclusions(sha: str) -> list[str] | None:
        entry = runs.get(sha, [])
        return None if entry == "unfetchable" else list(entry)  # type: ignore[arg-type]

    monkeypatch.setattr(audit, "_run_conclusions", conclusions)


def test_the_range_walks_first_parent_oldest_first_and_excludes_the_baseline(
    repo: Repo, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    base = repo.commit("baseline, gated by an earlier range")
    first = repo.commit("first")
    second = repo.commit("second")
    third = repo.commit("third")
    fourth = repo.commit("fourth")
    repo.publish_main()
    _fake_runs(
        monkeypatch,
        {
            base: ["success"],
            first: ["success"],
            second: [],
            third: ["failure"],
            fourth: ["cancelled"],
        },
    )
    ledger = tmp_path / "ledger.json"

    exit_code = _audit(monkeypatch, ["--range", f"{base}..{fourth}", "--ledger-out", str(ledger)])

    assert exit_code == 0, "report-only mode writes the ledger and does not fail"
    payload = json.loads(ledger.read_text(encoding="utf-8"))
    assert payload["schema_version"] == audit.LEDGER_SCHEMA_VERSION
    assert payload["range"] == {"baseline_sha": base, "end_sha": fourth}
    assert [entry["sha"] for entry in payload["revisions"]] == [first, second, third, fourth]
    assert [entry["verdict"] for entry in payload["revisions"]] == [
        "passing",
        "ungated",
        "failing",
        "unknown",
    ]
    assert payload["counts"] == {"examined": 4, "passing": 1, "failing": 1, "ungated": 1, "unknown": 1}
    assert payload["dispositions"] == []
    assert payload["measured_at_utc"].endswith("Z")


def test_gaps_in_the_range_fail_closed_when_asked(repo: Repo, monkeypatch: pytest.MonkeyPatch) -> None:
    base = repo.commit("baseline")
    tip = repo.commit("ungated tip")
    repo.publish_main()
    _fake_runs(monkeypatch, {tip: []})

    assert _audit(monkeypatch, ["--range", f"{base}..{tip}", "--fail-on-gap"]) == 1
    _fake_runs(monkeypatch, {tip: ["success"]})
    assert _audit(monkeypatch, ["--range", f"{base}..{tip}", "--fail-on-gap"]) == 0


def test_hand_recorded_dispositions_survive_re_measurement(
    repo: Repo, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The tool owns the measurements; the reviewer owns what a gap means."""
    base = repo.commit("baseline")
    tip = repo.commit("tip")
    repo.publish_main()
    _fake_runs(monkeypatch, {tip: []})
    ledger = tmp_path / "ledger.json"
    disposition = {
        "verdict": "ungated",
        "class": "accepted-historical-gap",
        "reason": "predates per-revision dispatch",
        "recorded_at_utc": "2026-09-13T00:00:00Z",
    }
    ledger.write_text(json.dumps({"dispositions": [disposition]}), encoding="utf-8")

    _audit(monkeypatch, ["--range", f"{base}..{tip}", "--ledger-out", str(ledger)])

    payload = json.loads(ledger.read_text(encoding="utf-8"))
    assert payload["dispositions"] == [disposition]
    assert payload["revisions"][0]["verdict"] == "ungated"


@pytest.mark.parametrize(
    "shape",
    ["baseline-not-an-ancestor", "merge-commit-inside", "end-not-on-main", "unresolvable-endpoint"],
)
def test_a_range_that_is_not_main_history_is_refused_before_any_lookup(
    repo: Repo, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str], shape: str
) -> None:
    root = repo.commit("root")
    if shape == "baseline-not-an-ancestor":
        repo.git("checkout", "-q", "-b", "side")
        base = repo.commit("on a side branch")
        repo.git("checkout", "-q", "main")
        end = repo.commit("on main")
        repo.publish_main()
    elif shape == "merge-commit-inside":
        repo.git("checkout", "-q", "-b", "feature")
        repo.commit("feature work")
        repo.git("checkout", "-q", "main")
        repo.commit("main work")
        repo.git("merge", "-q", "--no-ff", "-m", "merge feature", "feature")
        base, end = root, repo.git("rev-parse", "HEAD")
        repo.publish_main()
    elif shape == "end-not-on-main":
        repo.publish_main()
        repo.git("checkout", "-q", "-b", "unmerged")
        base, end = root, repo.commit("never landed")
    else:
        repo.publish_main()
        base, end = root, "0" * 40
    looked_up: list[str] = []
    monkeypatch.setattr(audit, "_run_conclusions", lambda sha: looked_up.append(sha) or [])
    ledger = tmp_path / "ledger.json"

    exit_code = _audit(monkeypatch, ["--range", f"{base}..{end}", "--ledger-out", str(ledger)])

    assert exit_code == 1
    assert "REFUSED" in capsys.readouterr().out
    assert looked_up == [], "a refused range must not consult run evidence"
    assert not ledger.exists()


def test_a_ledger_of_a_rolling_window_is_refused(repo: Repo, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A ledger that ages out is the thing the ledger exists to end."""
    with pytest.raises(SystemExit) as excinfo:
        _audit(monkeypatch, ["--ledger-out", str(tmp_path / "ledger.json")])
    assert excinfo.value.code == 2

    with pytest.raises(SystemExit) as excinfo:
        _audit(monkeypatch, ["--since-days", "7", "--range", "a..b"])
    assert excinfo.value.code == 2


def test_the_committed_ledger_is_a_fixed_range_with_every_revision_classified() -> None:
    root = Path(__file__).resolve().parents[2]
    ledger_path = root / "quality" / "main-gate-coverage-ledger.v1.json"
    payload = json.loads(ledger_path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == audit.LEDGER_SCHEMA_VERSION
    assert payload["repository"] == "sgajbi/lotus-platform"
    assert len(payload["range"]["baseline_sha"]) == 40 and len(payload["range"]["end_sha"]) == 40
    verdicts = [entry["verdict"] for entry in payload["revisions"]]
    assert set(verdicts) <= {"passing", "failing", "ungated", "unknown"}
    assert payload["counts"]["examined"] == len(verdicts)
    for verdict in ("passing", "failing", "ungated", "unknown"):
        assert payload["counts"][verdict] == verdicts.count(verdict)
    assert payload["counts"]["ungated"] > 0, "the ledger exists because there are gaps to record"
    recorded = {disposition["verdict"] for disposition in payload["dispositions"]}
    assert {"ungated", "failing"} <= recorded, "every gap class present has a recorded disposition"
    assert not any(entry["verdict"] == "unknown" for entry in payload["revisions"]), (
        "an unknown in a committed ledger is an unfinished measurement, not a record"
    )
