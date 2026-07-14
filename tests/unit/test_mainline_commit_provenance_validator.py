from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from automation.validate_mainline_commit_provenance import validate_commit_provenance


def _write_exceptions(path: Path, exceptions: list[dict]) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "lotus.mainline-commit-provenance-exceptions.v1",
                "exceptions": exceptions,
            }
        ),
        encoding="utf-8",
    )


def test_mainline_commit_provenance_accepts_github_verified_commit(tmp_path: Path) -> None:
    exceptions = tmp_path / "exceptions.json"
    _write_exceptions(exceptions, [])

    result = validate_commit_provenance(
        repository="sgajbi/lotus-platform",
        commit_sha="a" * 40,
        verification={"verified": True, "reason": "valid"},
        verification_source="github",
        exception_path=exceptions,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert result.status == "verified"
    assert result.findings == ()


def test_mainline_commit_provenance_rejects_unsigned_without_exception(tmp_path: Path) -> None:
    exceptions = tmp_path / "exceptions.json"
    _write_exceptions(exceptions, [])

    result = validate_commit_provenance(
        repository="sgajbi/lotus-platform",
        commit_sha="b" * 40,
        verification={"verified": False, "reason": "unsigned"},
        verification_source="github",
        exception_path=exceptions,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert result.status == "failed"
    assert result.findings == (
        "sgajbi/lotus-platform@bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb "
        "is not GitHub-verified (reason=unsigned, source=github)",
    )


def test_mainline_commit_provenance_accepts_exact_unexpired_exception(tmp_path: Path) -> None:
    exceptions = tmp_path / "exceptions.json"
    _write_exceptions(
        exceptions,
        [
            {
                "repository": "sgajbi/lotus-platform",
                "commit_sha": "c" * 40,
                "verification_reason": "unsigned",
                "owner": "platform-ci-governance",
                "issue_url": "https://github.com/sgajbi/lotus-platform/issues/505",
                "reason": "Historical rebase merge provenance loss under investigation.",
                "expires_on_utc": "2026-08-14T00:00:00Z",
            }
        ],
    )

    result = validate_commit_provenance(
        repository="sgajbi/lotus-platform",
        commit_sha="c" * 40,
        verification={"verified": False, "reason": "unsigned"},
        verification_source="github",
        exception_path=exceptions,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert result.status == "excepted"
    assert result.exception_owner == "platform-ci-governance"
    assert result.findings == ()


def test_mainline_commit_provenance_rejects_expired_exception(tmp_path: Path) -> None:
    exceptions = tmp_path / "exceptions.json"
    _write_exceptions(
        exceptions,
        [
            {
                "repository": "sgajbi/lotus-platform",
                "commit_sha": "d" * 40,
                "verification_reason": "unsigned",
                "owner": "platform-ci-governance",
                "expires_on_utc": "2026-07-01T00:00:00Z",
            }
        ],
    )

    result = validate_commit_provenance(
        repository="sgajbi/lotus-platform",
        commit_sha="d" * 40,
        verification={"verified": False, "reason": "unsigned"},
        verification_source="github",
        exception_path=exceptions,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert result.status == "failed"
    assert result.exception_owner is None


def test_mainline_commit_provenance_rejects_reason_mismatch_exception(tmp_path: Path) -> None:
    exceptions = tmp_path / "exceptions.json"
    _write_exceptions(
        exceptions,
        [
            {
                "repository": "sgajbi/lotus-platform",
                "commit_sha": "e" * 40,
                "verification_reason": "unknown_key",
                "owner": "platform-ci-governance",
                "expires_on_utc": "2026-08-14T00:00:00Z",
            }
        ],
    )

    result = validate_commit_provenance(
        repository="sgajbi/lotus-platform",
        commit_sha="e" * 40,
        verification={"verified": False, "reason": "unsigned"},
        verification_source="github",
        exception_path=exceptions,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert result.status == "failed"
    assert result.exception_owner is None


def test_mainline_commit_provenance_rejects_exception_without_issue_evidence(
    tmp_path: Path,
) -> None:
    exceptions = tmp_path / "exceptions.json"
    _write_exceptions(
        exceptions,
        [
            {
                "repository": "sgajbi/lotus-platform",
                "commit_sha": "f" * 40,
                "verification_reason": "unsigned",
                "owner": "platform-ci-governance",
                "expires_on_utc": "2026-08-14T00:00:00Z",
            }
        ],
    )

    result = validate_commit_provenance(
        repository="sgajbi/lotus-platform",
        commit_sha="f" * 40,
        verification={"verified": False, "reason": "unsigned"},
        verification_source="github",
        exception_path=exceptions,
        today=datetime(2026, 7, 14, tzinfo=UTC),
    )

    assert result.status == "failed"
    assert result.exception_owner is None
