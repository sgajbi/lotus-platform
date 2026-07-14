from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCEPTION_PATH = (
    ROOT
    / "platform-contracts"
    / "ci-governance"
    / "mainline-commit-provenance-exceptions.v1.json"
)
OUTPUT_JSON = ROOT / "output" / "mainline-commit-provenance-validation.json"
OUTPUT_MD = ROOT / "output" / "mainline-commit-provenance-validation.md"


@dataclass(frozen=True)
class CommitProvenanceResult:
    repository: str
    commit_sha: str
    status: str
    verification_source: str
    verified: bool
    verification_reason: str
    branch_signatures_required: bool | None
    branch_signature_policy_source: str
    exception_owner: str | None
    exception_expires_on: str | None
    findings: tuple[str, ...]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _default_repository() -> str:
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if repository:
        return repository
    result = _run(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"])
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return "sgajbi/lotus-platform"


def _default_commit_sha() -> str:
    explicit_sha = os.environ.get("LOTUS_PROVENANCE_COMMIT_SHA", "").strip()
    if explicit_sha:
        return explicit_sha
    commit_sha = os.environ.get("GITHUB_SHA", "").strip()
    if commit_sha:
        return commit_sha
    result = _run(["git", "rev-parse", "HEAD"])
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError("Unable to resolve current commit SHA")
    return result.stdout.strip()


def _default_branch_name() -> str:
    ref_name = os.environ.get("GITHUB_REF_NAME", "").strip()
    return ref_name or "main"


def _github_verification(repository: str, commit_sha: str) -> tuple[str, dict[str, Any]] | None:
    result = _run(
        [
            "gh",
            "api",
            f"repos/{repository}/commits/{commit_sha}",
            "--jq",
            ".commit.verification",
        ]
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        return None
    return "github", payload


def _local_git_verification(commit_sha: str) -> tuple[str, dict[str, Any]]:
    result = _run(["git", "verify-commit", commit_sha])
    if result.returncode == 0:
        return "local-git", {"verified": True, "reason": "valid"}
    return "local-git", {
        "verified": False,
        "reason": "unsigned",
        "stderr": result.stderr.strip(),
    }


def resolve_verification(
    *,
    repository: str,
    commit_sha: str,
    verification_path: Path | None = None,
) -> tuple[str, dict[str, Any]]:
    if verification_path is not None:
        return "fixture", _load_json(verification_path)
    github_result = _github_verification(repository, commit_sha)
    if github_result is not None:
        return github_result
    return _local_git_verification(commit_sha)


def _github_required_signatures_enabled(repository: str, branch: str) -> bool | None:
    result = _run(
        [
            "gh",
            "api",
            f"repos/{repository}/branches/{branch}/protection/required_signatures",
            "--jq",
            ".enabled",
        ]
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.strip().lower() == "true"


def _declared_required_signatures_enabled() -> bool | None:
    value = os.environ.get("LOTUS_BRANCH_SIGNATURES_REQUIRED", "").strip().lower()
    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False
    return None


def resolve_branch_signature_policy(repository: str, branch: str) -> tuple[bool | None, str]:
    github_policy = _github_required_signatures_enabled(repository, branch)
    if github_policy is not None:
        return github_policy, "github-branch-protection"

    declared_policy = _declared_required_signatures_enabled()
    if declared_policy is not None:
        return declared_policy, "declared-environment"

    return None, "unavailable"


def _exception_entries(exception_path: Path) -> list[dict[str, Any]]:
    payload = _load_json(exception_path)
    entries = payload.get("exceptions", [])
    return [entry for entry in entries if isinstance(entry, dict)]


def _expired(expires_on: object, *, today: datetime) -> bool:
    if not isinstance(expires_on, str):
        return True
    try:
        expiry = datetime.fromisoformat(expires_on.replace("Z", "+00:00"))
    except ValueError:
        return True
    return expiry < today


def _matching_exception(
    *,
    repository: str,
    commit_sha: str,
    verification_reason: str,
    exception_path: Path,
    today: datetime,
) -> dict[str, Any] | None:
    for entry in _exception_entries(exception_path):
        if entry.get("repository") != repository:
            continue
        if entry.get("commit_sha") != commit_sha:
            continue
        if entry.get("verification_reason") != verification_reason:
            continue
        if not _exception_has_required_evidence(entry):
            continue
        if _expired(entry.get("expires_on_utc"), today=today):
            continue
        return entry
    return None


def _exception_has_required_evidence(entry: dict[str, Any]) -> bool:
    required_text_fields = ("owner", "issue_url", "reason")
    for field in required_text_fields:
        value = entry.get(field)
        if not isinstance(value, str) or len(value.strip()) < 10:
            return False
    return str(entry.get("issue_url", "")).startswith("https://github.com/")


def validate_commit_provenance(
    *,
    repository: str,
    commit_sha: str,
    verification: dict[str, Any],
    verification_source: str,
    branch_signatures_required: bool | None = True,
    branch_signature_policy_source: str = "input",
    exception_path: Path = DEFAULT_EXCEPTION_PATH,
    today: datetime | None = None,
) -> CommitProvenanceResult:
    verified = verification.get("verified") is True
    reason = str(verification.get("reason") or "unknown")
    effective_today = today or datetime.now(UTC)
    findings: list[str] = []
    exception = None
    unsigned_allowed_by_branch_policy = (
        verification_source == "github"
        and reason == "unsigned"
        and branch_signatures_required is False
    )
    if not verified and not unsigned_allowed_by_branch_policy:
        exception = _matching_exception(
            repository=repository,
            commit_sha=commit_sha,
            verification_reason=reason,
            exception_path=exception_path,
            today=effective_today,
        )
        if exception is None:
            findings.append(
                f"{repository}@{commit_sha} is not GitHub-verified "
                f"(reason={reason}, source={verification_source})"
            )

    status = (
        "verified"
        if verified
        else "unsigned_allowed_by_branch_policy"
        if unsigned_allowed_by_branch_policy
        else "excepted"
        if exception
        else "failed"
    )
    return CommitProvenanceResult(
        repository=repository,
        commit_sha=commit_sha,
        status=status,
        verification_source=verification_source,
        verified=verified,
        verification_reason=reason,
        branch_signatures_required=branch_signatures_required,
        branch_signature_policy_source=branch_signature_policy_source,
        exception_owner=str(exception.get("owner")) if exception else None,
        exception_expires_on=str(exception.get("expires_on_utc")) if exception else None,
        findings=tuple(findings),
    )


def _write_outputs(result: CommitProvenanceResult) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    lines = [
        "# Mainline Commit Provenance Validation",
        "",
        f"- Repository: `{result.repository}`",
        f"- Commit SHA: `{result.commit_sha}`",
        f"- Status: `{result.status}`",
        f"- Verification source: `{result.verification_source}`",
        f"- Verification reason: `{result.verification_reason}`",
        f"- Branch signatures required: `{result.branch_signatures_required}`",
        f"- Branch signature policy source: `{result.branch_signature_policy_source}`",
        f"- Exception owner: `{result.exception_owner or '-'}`",
        f"- Exception expires: `{result.exception_expires_on or '-'}`",
        f"- Findings: `{'; '.join(result.findings) or '-'}`",
    ]
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate GitHub commit verification for the exact mainline commit."
    )
    parser.add_argument("--repository", default=None)
    parser.add_argument("--commit-sha", default=None)
    parser.add_argument("--branch", default=None)
    parser.add_argument("--exception-path", type=Path, default=DEFAULT_EXCEPTION_PATH)
    parser.add_argument(
        "--verification-json",
        type=Path,
        help="Optional fixture containing a GitHub commit verification object.",
    )
    args = parser.parse_args(argv)

    repository = args.repository or _default_repository()
    commit_sha = args.commit_sha or _default_commit_sha()
    branch = args.branch or _default_branch_name()
    source, verification = resolve_verification(
        repository=repository,
        commit_sha=commit_sha,
        verification_path=args.verification_json,
    )
    branch_signatures_required, policy_source = resolve_branch_signature_policy(repository, branch)
    result = validate_commit_provenance(
        repository=repository,
        commit_sha=commit_sha,
        verification=verification,
        verification_source=source,
        branch_signatures_required=branch_signatures_required,
        branch_signature_policy_source=policy_source,
        exception_path=args.exception_path,
    )
    _write_outputs(result)
    if result.findings:
        print("Mainline commit provenance validation failed:")
        for finding in result.findings:
            print(f"- {finding}")
        return 1
    print(f"Mainline commit provenance validation {result.status}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
