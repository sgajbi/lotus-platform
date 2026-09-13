"""Pin the sibling repositories the per-commit lanes read, and prove each checkout is the pin.

`Main Releasability Gate` certifies one lotus-platform commit, yet its checks read
twelve sibling repositories. Checked out at their default branches, the verdict
was a function of *(this commit) x (every sibling's main at run time)*: re-running
the gate on one revision could answer differently a week later, and a sibling
merge could turn this repository's main red with no change here (#858, #708).

The manifest at `platform-contracts/ci-governance/sibling-source-manifest.v1.json`
records the exact revision of every sibling the lanes read. It is committed, so it
travels with the revision under test and a re-run reproduces the original inputs.
A pin moves only through a reviewed pull request; the scheduled fleet-conformance
lane reads sibling default branches on purpose and reports how far each pin lags.

Three fail-closed responsibilities, each independently useful:

- ``--check`` (always): the manifest names every registered sibling exactly once,
  with a full lowercase revision and a matching GitHub repository. A missing
  entry would let ``actions/checkout`` fall back to the default branch silently,
  which is the unpinned behaviour this file exists to end.
- ``--github-output``: publishes ``<repository>=<revision>`` so each checkout step
  binds ``ref:`` to the manifest rather than to a value retyped in YAML.
- ``--verify-checkouts``: after checkout, ``git rev-parse HEAD`` of every sibling
  must equal its pin. A ref that resolved to something else, or a checkout that
  quietly fell back, fails here rather than feeding the validators.

``--report-drift`` is the fleet lane's view: current default-branch revision per
sibling, commits ahead of the pin, and pin age, with ``--max-pin-age-days`` as the
only failing condition. Drift itself is information; a stale pin is a finding.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_PATH = (
    ROOT / "platform-contracts" / "ci-governance" / "sibling-source-manifest.v1.json"
)
DEFAULT_REGISTRY_PATH = ROOT / "automation" / "repos.json"
SCHEMA_VERSION = "lotus.sibling-source-manifest.v1"
SELF_REPOSITORY = "lotus-platform"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class SiblingSource:
    repository: str
    github: str
    branch: str
    revision: str
    committed_at_utc: str


@dataclass(frozen=True)
class RegisteredSibling:
    github: str
    default_branch: str


def _parse_utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def registered_siblings(registry_path: Path) -> dict[str, RegisteredSibling]:
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    entries = payload if isinstance(payload, list) else payload.get("repositories", [])
    return {
        str(entry["name"]): RegisteredSibling(
            github=str(entry.get("github", "")),
            default_branch=str(entry.get("default_branch", "main")),
        )
        for entry in entries
        if isinstance(entry, dict) and entry.get("name") != SELF_REPOSITORY
    }


def load_manifest(
    manifest_path: Path, registry: dict[str, RegisteredSibling]
) -> tuple[list[SiblingSource], list[str]]:
    """The pinned sources and every reason the manifest cannot be trusted."""
    errors: list[str] = []
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"manifest unreadable: {exc}"]
    if not isinstance(payload, dict):
        return [], ["manifest must be a JSON object"]
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    if _parse_utc(payload.get("recorded_at_utc")) is None:
        errors.append("recorded_at_utc must be an ISO-8601 UTC timestamp ending in Z")

    raw_sources = payload.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        return [], [*errors, "sources must be a non-empty list"]

    sources: list[SiblingSource] = []
    seen: set[str] = set()
    for index, entry in enumerate(raw_sources):
        if not isinstance(entry, dict):
            errors.append(f"sources[{index}] must be an object")
            continue
        repository = entry.get("repository")
        if not isinstance(repository, str) or not repository:
            errors.append(f"sources[{index}] has no repository")
            continue
        if repository in seen:
            errors.append(f"{repository}: pinned more than once")
            continue
        seen.add(repository)
        registered = registry.get(repository)
        if registered is None:
            errors.append(f"{repository}: not a registered sibling in automation/repos.json")
            continue
        github = entry.get("github")
        if github != registered.github:
            errors.append(f"{repository}: github must be {registered.github!r}, not {github!r}")
        branch = entry.get("branch")
        if branch != registered.default_branch:
            errors.append(
                f"{repository}: branch must be the registered default "
                f"{registered.default_branch!r}, not {branch!r}"
            )
        revision = entry.get("revision")
        if not isinstance(revision, str) or FULL_SHA.fullmatch(revision) is None:
            errors.append(f"{repository}: revision must be a full lowercase commit SHA")
        committed_at = entry.get("committed_at_utc")
        if _parse_utc(committed_at) is None:
            errors.append(f"{repository}: committed_at_utc must be an ISO-8601 UTC timestamp")
        sources.append(
            SiblingSource(
                repository=repository,
                github=str(github),
                branch=str(branch),
                revision=str(revision),
                committed_at_utc=str(committed_at),
            )
        )

    for repository in sorted(set(registry) - seen):
        errors.append(
            f"{repository}: registered sibling has no pin; an unpinned checkout falls back "
            "to the default branch"
        )
    return sources, errors


def emit_github_output(sources: list[SiblingSource], output_path: Path) -> None:
    with output_path.open("a", encoding="utf-8") as handle:
        for source in sources:
            handle.write(f"{source.repository}={source.revision}\n")


def verify_checkouts(sources: list[SiblingSource], federated_root: Path) -> list[str]:
    """Every sibling checkout must be at its pin, measured from git rather than assumed."""
    errors: list[str] = []
    for source in sources:
        checkout = federated_root / source.repository
        if not (checkout / ".git").exists():
            errors.append(f"{source.repository}: no checkout at {checkout}")
            continue
        completed = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        head = completed.stdout.strip()
        if completed.returncode != 0 or FULL_SHA.fullmatch(head) is None:
            errors.append(f"{source.repository}: HEAD unreadable at {checkout}")
        elif head != source.revision:
            errors.append(
                f"{source.repository}: checkout is at {head}, manifest pins {source.revision}"
            )
    return errors


def manifest_recorded_at(manifest_path: Path) -> datetime | None:
    """When the pins were last refreshed. Age is measured from here, not from the
    pinned commit's own date: a sibling that has simply been quiet for a month is
    not a stale pin, and refreshing the manifest is what must clear staleness."""
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return _parse_utc(payload.get("recorded_at_utc")) if isinstance(payload, dict) else None


@dataclass(frozen=True)
class PinDrift:
    repository: str
    pinned: str
    current: str | None
    ahead_by: int | None
    behind_by: int | None
    refresh_age_days: int

    def posture(self, *, max_pin_age_days: int) -> str:
        """One word per state, and every state that is not a positive answer fails.

        `CURRENT` needs equal SHAs -- established identity, not an inference.
        Unequal SHAs need a trustworthy comparison in both directions: a missing
        one, or one that claims the two are identical, is `UNRESOLVED`. Main
        ahead of the pin on the pin's own history is `DRIFTED` (information), or
        `STALE` when the manifest itself has not been refreshed within the policy
        age, which a refresh PR clears. Main behind the pin (`BEHIND`, rolled back
        to an ancestor) or on a rewritten history (`DIVERGED`, commits on both
        sides) are findings about the sibling, not about the pin.
        """
        if self.current is None:
            return "UNREAD"
        if self.current == self.pinned:
            return "CURRENT"
        if self.ahead_by is None or self.behind_by is None:
            return "UNRESOLVED"
        if self.ahead_by > 0 and self.behind_by > 0:
            return "DIVERGED"
        if self.behind_by > 0:
            return "BEHIND"
        if self.ahead_by == 0:
            return "UNRESOLVED"
        if self.refresh_age_days > max_pin_age_days:
            return "STALE"
        return "DRIFTED"


FAILING_POSTURES = frozenset({"UNREAD", "UNRESOLVED", "BEHIND", "DIVERGED", "STALE"})
POSTURE_MEANINGS = {
    "UNREAD": "the sibling's current revision could not be read",
    "UNRESOLVED": "the SHAs differ and no trustworthy comparison was obtained",
    "BEHIND": "the sibling's main was rolled back to an ancestor of the pin",
    "DIVERGED": "the sibling's main is on a rewritten history with commits on both sides of the pin",
    "STALE": "main is ahead and the manifest has not been refreshed within the policy age",
}


def _gh_json(*args: str) -> object | None:
    completed = subprocess.run(
        ["gh", "api", *args], capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        return None
    try:
        return json.loads(completed.stdout or "null")
    except json.JSONDecodeError:
        return None


def report_drift(
    sources: list[SiblingSource], *, now: datetime, recorded_at: datetime | None
) -> list[PinDrift]:
    """How far each sibling's default branch has moved past its pin.

    A sibling whose current revision cannot be read is reported with no current
    value rather than silently as unchanged: unread is not the same as identical.
    An unreadable refresh time counts as infinitely old, so a manifest without
    one cannot hide staleness.
    """
    refresh_age_days = max(0, (now - recorded_at).days) if recorded_at else 10**6
    drifts: list[PinDrift] = []
    for source in sources:
        branch = _gh_json(f"repos/{source.github}/branches/{source.branch}")
        current = None
        if isinstance(branch, dict) and isinstance(branch.get("commit"), dict):
            candidate = branch["commit"].get("sha")
            if isinstance(candidate, str) and FULL_SHA.fullmatch(candidate):
                current = candidate
        ahead_by: int | None = None
        behind_by: int | None = None
        if current is not None:
            if current == source.revision:
                ahead_by = behind_by = 0
            else:
                compare = _gh_json(f"repos/{source.github}/compare/{source.revision}...{current}")
                if isinstance(compare, dict):
                    if isinstance(compare.get("ahead_by"), int):
                        ahead_by = int(compare["ahead_by"])
                    if isinstance(compare.get("behind_by"), int):
                        behind_by = int(compare["behind_by"])
        drifts.append(
            PinDrift(
                repository=source.repository,
                pinned=source.revision,
                current=current,
                ahead_by=ahead_by,
                behind_by=behind_by,
                refresh_age_days=refresh_age_days,
            )
        )
    return drifts


def _count(value: int | None) -> str:
    return "?" if value is None else str(value)


def drift_markdown(drifts: list[PinDrift], *, max_pin_age_days: int) -> str:
    lines = [
        "| Repository | Pinned | Current main | Ahead of pin | Behind pin | Refresh age (days) | Posture |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for drift in drifts:
        lines.append(
            f"| {drift.repository} | `{drift.pinned[:12]}` | "
            f"`{(drift.current or 'unread')[:12]}` | "
            f"{_count(drift.ahead_by)} | {_count(drift.behind_by)} | "
            f"{drift.refresh_age_days} | {drift.posture(max_pin_age_days=max_pin_age_days)} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument(
        "--github-output",
        type=Path,
        help="append `<repository>=<revision>` for every pin to this GITHUB_OUTPUT file",
    )
    parser.add_argument(
        "--verify-checkouts",
        type=Path,
        metavar="DIR",
        help="require DIR/<repository> to be checked out at its pinned revision",
    )
    parser.add_argument(
        "--report-drift",
        action="store_true",
        help="read each sibling's current default branch via gh and report pin drift",
    )
    parser.add_argument(
        "--max-pin-age-days",
        type=int,
        default=14,
        help=(
            "with --report-drift, a drifted pin is STALE when the manifest's recorded_at_utc "
            "is older than this many days; a pin equal to current main is never stale"
        ),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        help="with --report-drift, append the drift table as Markdown to this file",
    )
    arguments = parser.parse_args()

    registry = registered_siblings(arguments.registry)
    sources, errors = load_manifest(arguments.manifest, registry)
    if errors:
        print("Sibling source manifest is not trustworthy:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Sibling source manifest pins {len(sources)} registered sibling(s).")

    if arguments.github_output is not None:
        emit_github_output(sources, arguments.github_output)

    if arguments.verify_checkouts is not None:
        mismatches = verify_checkouts(sources, arguments.verify_checkouts)
        if mismatches:
            print("Sibling checkouts do not match the manifest:")
            for mismatch in mismatches:
                print(f"- {mismatch}")
            return 1
        print(f"Every sibling checkout under {arguments.verify_checkouts} is at its pin.")

    if arguments.report_drift:
        now = datetime.now(UTC)
        drifts = report_drift(sources, now=now, recorded_at=manifest_recorded_at(arguments.manifest))
        table = drift_markdown(drifts, max_pin_age_days=arguments.max_pin_age_days)
        print(table)
        if arguments.summary is not None:
            with arguments.summary.open("a", encoding="utf-8") as handle:
                handle.write("## Sibling source pins versus current main\n\n" + table)
        findings = {
            drift.repository: drift.posture(max_pin_age_days=arguments.max_pin_age_days)
            for drift in drifts
        }
        failing = {name: posture for name, posture in findings.items() if posture in FAILING_POSTURES}
        if failing:
            print(
                "Fleet drift findings: "
                + ", ".join(f"{name}={posture}" for name, posture in sorted(failing.items()))
                + ". "
                + " ".join(
                    f"{posture}: {POSTURE_MEANINGS[posture]}."
                    for posture in sorted(set(failing.values()))
                )
                + f" Policy age: {arguments.max_pin_age_days} day(s); a refresh through a reviewed "
                "pull request clears STALE only."
            )
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
