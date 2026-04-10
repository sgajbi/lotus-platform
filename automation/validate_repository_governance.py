from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = ROOT / "automation" / "repository-governance-policy.json"
OUTPUT_JSON = ROOT / "output" / "repository-governance-validation.json"
OUTPUT_MD = ROOT / "output" / "repository-governance-validation.md"


@dataclass(frozen=True)
class ExpectedRepositoryGovernance:
    name: str
    default_branch: str
    required_checks: tuple[str, ...]


def load_policy(policy_path: Path) -> list[ExpectedRepositoryGovernance]:
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    return [
        ExpectedRepositoryGovernance(
            name=repo["name"],
            default_branch=repo["default_branch"],
            required_checks=tuple(repo["required_checks"]),
        )
        for repo in payload["repos"]
    ]


def run_gh_json(*args: str) -> dict[str, Any] | None:
    completed = subprocess.run(
        ["gh", "api", *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if completed.returncode != 0:
        if "Branch not protected" in completed.stderr:
            return None
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return json.loads(completed.stdout)


def normalize_actual_governance(payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {
            "protected": False,
            "required_checks": [],
            "strict": False,
            "approvals": 0,
            "dismiss_stale_reviews": False,
            "require_conversation_resolution": False,
            "required_linear_history": False,
            "allow_force_pushes": False,
            "allow_deletions": False,
            "allow_auto_merge": False,
        }

    review_requirements = payload.get("required_pull_request_reviews") or {}
    required_status_checks = payload.get("required_status_checks") or {}
    required_conversation_resolution = payload.get("required_conversation_resolution") or {}
    required_linear_history = payload.get("required_linear_history") or {}
    allow_force_pushes = payload.get("allow_force_pushes") or {}
    allow_deletions = payload.get("allow_deletions") or {}

    return {
        "protected": True,
        "required_checks": sorted(required_status_checks.get("contexts") or []),
        "strict": bool(required_status_checks.get("strict")),
        "approvals": int(review_requirements.get("required_approving_review_count") or 0),
        "dismiss_stale_reviews": bool(review_requirements.get("dismiss_stale_reviews")),
        "require_conversation_resolution": bool(required_conversation_resolution.get("enabled")),
        "required_linear_history": bool(required_linear_history.get("enabled")),
        "allow_force_pushes": bool(allow_force_pushes.get("enabled")),
        "allow_deletions": bool(allow_deletions.get("enabled")),
        "allow_auto_merge": False,
    }


def fetch_repository_governance(org: str, expected: ExpectedRepositoryGovernance) -> dict[str, Any]:
    protection = run_gh_json(f"repos/{org}/{expected.name}/branches/{expected.default_branch}/protection")
    repository = run_gh_json(f"repos/{org}/{expected.name}")
    normalized = normalize_actual_governance(protection)
    normalized["allow_auto_merge"] = bool(repository["allow_auto_merge"])
    return normalized


def expected_governance(expected: ExpectedRepositoryGovernance) -> dict[str, Any]:
    return {
        "protected": True,
        "required_checks": sorted(expected.required_checks),
        "strict": True,
        "approvals": 1,
        "dismiss_stale_reviews": True,
        "require_conversation_resolution": True,
        "required_linear_history": False,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "allow_auto_merge": True,
    }


def compare_governance(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    drifts: list[str] = []
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            drifts.append(f"{key}: expected={expected_value!r} actual={actual_value!r}")
    return drifts


def write_outputs(results: list[dict[str, Any]]) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")

    lines = [
        "# Repository Governance Validation",
        "",
        "| Repository | Branch | Status | Drift Count |",
        "|---|---|---|---:|",
    ]
    for result in results:
        lines.append(
            f"| {result['repository']} | {result['branch']} | {result['status']} | {len(result['drift'])} |"
        )
        if result["drift"]:
            lines.append("")
            for drift in result["drift"]:
                lines.append(f"- `{result['repository']}`: {drift}")
            lines.append("")

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate GitHub branch protection against Lotus repository governance policy.")
    parser.add_argument("--org", default="sgajbi")
    parser.add_argument("--policy-path", type=Path, default=DEFAULT_POLICY_PATH)
    args = parser.parse_args()

    results: list[dict[str, Any]] = []
    has_drift = False
    for repo in load_policy(args.policy_path):
        actual = fetch_repository_governance(args.org, repo)
        expected = expected_governance(repo)
        drift = compare_governance(expected, actual)
        if drift:
            has_drift = True
        results.append(
            {
                "repository": repo.name,
                "branch": repo.default_branch,
                "status": "drift" if drift else "aligned",
                "drift": drift,
            }
        )

    write_outputs(results)
    return 1 if has_drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
