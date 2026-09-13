"""A pin refresh is a reviewed change, tool-produced, and fail-closed.

`--refresh` rewrites every pin to the sibling's current default-branch revision for a pull
request to carry. It must move every pin or none: a manifest that is half new and half old
describes an estate that never existed together, so an unreadable sibling refuses the write.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from datetime import UTC, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMMITTED_MANIFEST = (
    ROOT / "platform-contracts" / "ci-governance" / "sibling-source-manifest.v1.json"
)
COMMITTED_REGISTRY = ROOT / "automation" / "repos.json"
VALIDATOR_PATH = ROOT / "automation" / "validate_sibling_source_manifest.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_sibling_source_manifest", VALIDATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_validator()


def _manifest_copy(tmp_path: Path) -> tuple[Path, dict]:
    payload = json.loads(COMMITTED_MANIFEST.read_text(encoding="utf-8"))
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path, payload


def _branch_answers(payload: dict, *, move: dict[str, str], unreadable: set[str] = frozenset()):
    """A scripted GitHub boundary: each sibling's main is its pin unless moved or unreadable."""
    github_to_repo = {s["github"]: s["repository"] for s in payload["sources"]}
    pins = {s["repository"]: s["revision"] for s in payload["sources"]}

    def gh_json(*args: str):
        path = args[0]
        for github, repository in github_to_repo.items():
            if path.startswith(f"repos/{github}/branches/"):
                if repository in unreadable:
                    return None
                sha = move.get(repository, pins[repository])
                return {"commit": {"sha": sha, "commit": {"committer": {"date": "2026-09-13T09:00:00Z"}}}}
        raise AssertionError(f"unexpected gh api call: {path}")

    return gh_json


def test_refresh_moves_every_pin_to_current_main_and_stamps_the_refresh(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, payload = _manifest_copy(tmp_path)
    moved = {"lotus-core": "1" * 40, "lotus-report": "2" * 40}
    monkeypatch.setattr(validator, "_gh_json", _branch_answers(payload, move=moved))
    sources, _ = validator.load_manifest(manifest, validator.registered_siblings(COMMITTED_REGISTRY))

    refreshes, errors = validator.refresh_manifest(
        manifest, sources, now=datetime(2026, 9, 13, 9, 30, tzinfo=UTC)
    )

    assert errors == []
    written = json.loads(manifest.read_text(encoding="utf-8"))
    assert written["recorded_at_utc"] == "2026-09-13T09:30:00Z"
    by_repo = {s["repository"]: s for s in written["sources"]}
    assert by_repo["lotus-core"]["revision"] == "1" * 40
    assert by_repo["lotus-report"]["revision"] == "2" * 40
    assert all(s["committed_at_utc"] == "2026-09-13T09:00:00Z" for s in written["sources"])
    # Everything that is not a pin is untouched.
    assert written["schema_version"] == payload["schema_version"]
    assert [s["github"] for s in written["sources"]] == [s["github"] for s in payload["sources"]]
    assert sum(1 for r in refreshes if r.previous != r.current) == 2
    # The refreshed file still validates.
    _, errors_after = validator.load_manifest(manifest, validator.registered_siblings(COMMITTED_REGISTRY))
    assert errors_after == []


def test_an_unreadable_sibling_refuses_the_whole_refresh(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, payload = _manifest_copy(tmp_path)
    before = manifest.read_bytes()
    monkeypatch.setattr(
        validator,
        "_gh_json",
        _branch_answers(payload, move={"lotus-core": "1" * 40}, unreadable={"lotus-ai"}),
    )
    sources, _ = validator.load_manifest(manifest, validator.registered_siblings(COMMITTED_REGISTRY))

    refreshes, errors = validator.refresh_manifest(manifest, sources, now=datetime.now(UTC))

    assert refreshes == []
    assert errors == ["lotus-ai: current revision or commit date unreadable"]
    assert manifest.read_bytes() == before, "a partial refresh must not be written"


def test_a_commit_without_a_date_is_unreadable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest, payload = _manifest_copy(tmp_path)
    monkeypatch.setattr(
        validator, "_gh_json", lambda *args: {"commit": {"sha": "3" * 40, "commit": {}}}
    )
    sources, _ = validator.load_manifest(manifest, validator.registered_siblings(COMMITTED_REGISTRY))

    _, errors = validator.refresh_manifest(manifest, sources, now=datetime.now(UTC))

    assert len(errors) == len(sources)


def _cli(monkeypatch: pytest.MonkeyPatch, manifest: Path) -> tuple[int, str]:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_sibling_source_manifest.py",
            "--manifest", str(manifest),
            "--registry", str(COMMITTED_REGISTRY),
            "--refresh",
        ],
    )
    captured = io.StringIO()
    with redirect_stdout(captured):
        exit_code = validator.main()
    return exit_code, captured.getvalue()


def test_cli_refresh_reports_moved_and_unchanged_pins_and_revalidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, payload = _manifest_copy(tmp_path)
    monkeypatch.setattr(validator, "_gh_json", _branch_answers(payload, move={"lotus-risk": "4" * 40}))

    exit_code, out = _cli(monkeypatch, manifest)

    assert exit_code == 0
    assert "moved     lotus-risk:" in out
    assert "unchanged lotus-core:" in out
    assert "Refreshed 12 pin(s); 1 moved." in out


def test_cli_refresh_fails_closed_and_leaves_the_manifest_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, payload = _manifest_copy(tmp_path)
    before = manifest.read_bytes()
    monkeypatch.setattr(validator, "_gh_json", _branch_answers(payload, move={}, unreadable={"lotus-idea"}))

    exit_code, out = _cli(monkeypatch, manifest)

    assert exit_code == 1
    assert "Refresh refused; the manifest is unchanged" in out
    assert manifest.read_bytes() == before
