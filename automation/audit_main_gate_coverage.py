"""Audit which commits on main the Main Releasability Gate actually evaluated.

The gate is dispatched per merged pull request; this repository merges by
rebase, so a pull request holding N commits puts N on main and every one of
them must have a gate run - a commit that was never head becomes the deployed
tree on rollback and bisect. A run that is never created is not a failure, so
nothing else reports the loss; this audit does.

Two windows, because they answer different questions:

- ``--since-days N`` (the scheduled audit): every commit on ``origin/main`` from
  the last N days. A rolling window says whether *recent* main is gated. It
  cannot say what happened to a gap once the window moved past it: measured on
  2026-09-13, the same audit reported 174 examined / 116 ungated on 09-12 and
  116 / 79 one day later - thirty-seven ungated revisions left the window with
  no verdict and no record.
- ``--range BASE..END`` (the fixed ledger): every first-parent commit after
  ``BASE`` up to and including ``END``, both exact. The range is the claim, so
  there is no cap and nothing can age out. With ``--ledger-out`` the verdicts
  are written as a versioned JSON ledger that a reviewed pull request commits;
  hand-recorded ``dispositions`` in an existing ledger survive re-measurement.

Fail-closed by design (a watchdog that can pass while verifying nothing is
the same liveness defect it exists to catch):

- a missing ``gh`` binary is a failure under ``--fail-on-gap``, never a skip;
- a commit whose run listing cannot be fetched (rate limit, token scope,
  transient API failure) is UNKNOWN, and unknown commits fail the audit under
  ``--fail-on-gap`` - they are unverified, not implicitly fine;
- only runs that reached a verdict (success or failure) count as evaluation:
  a run cancelled seconds after dispatch evaluated nothing. In-progress runs
  count as pending (unknown), not as coverage.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

WORKFLOW = "main-releasability.yml"
LEDGER_SCHEMA_VERSION = "lotus.main-gate-coverage-ledger.v1"
_VERDICT_CONCLUSIONS = {"success", "failure"}
_RANGE = re.compile(r"^(?P<base>[^.\s]+)\.\.(?P<end>[^.\s]+)$")


def _git(*args: str) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _git_succeeds(*args: str) -> bool:
    return subprocess.run(["git", *args], capture_output=True, text=True).returncode == 0


def _run_conclusions(sha: str) -> list[str] | None:
    """Conclusions of every gate run for one commit, or None when unknowable."""

    completed = subprocess.run(
        [
            "gh",
            "run",
            "list",
            "--workflow",
            WORKFLOW,
            "--commit",
            sha,
            "--json",
            "conclusion,status",
        ],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    try:
        runs = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError:
        return None
    return [str(run.get("conclusion") or run.get("status") or "") for run in runs]


def _classify(conclusions: list[str] | None) -> str:
    """One verdict vocabulary for both windows, so the ledger and the scheduled
    audit cannot disagree about what counts as coverage."""
    if conclusions is None:
        return "unknown"
    verdicts = [conclusion for conclusion in conclusions if conclusion in _VERDICT_CONCLUSIONS]
    if verdicts:
        return "passing" if "success" in verdicts else "failing"
    return "unknown" if conclusions else "ungated"


def _rolling_window(since_days: int, limit: int) -> tuple[list[str], bool]:
    # Probe one past the cap: a window holding exactly `limit` commits was fully
    # examined, so only a (limit + 1)th commit proves the span was truncated.
    # `--since` STOPS traversal at the first commit older than the cutoff, so a
    # newer-dated ancestor sitting behind an older-dated commit is silently
    # omitted and its coverage never examined - a green audit for a window it
    # never walked. `--since-as-filter` visits every commit and filters, so the
    # claimed window is the audited window regardless of date monotonicity.
    probed = _git(
        "log",
        f"--since-as-filter={since_days} days ago",
        f"-{limit + 1}",
        "--format=%H %h %s",
        "origin/main",
    )
    # A prefix of the window is not the window: if the cap was exceeded, older
    # commits inside the requested span went unexamined and their coverage is
    # unknown, not proven.
    return probed[:limit], len(probed) > limit


def _resolve_commit(reference: str) -> str | None:
    try:
        return _git("rev-parse", "--verify", f"{reference}^{{commit}}")[0]
    except (subprocess.CalledProcessError, IndexError):
        return None


def _fixed_range(base: str, end: str) -> tuple[list[str], str, str | None]:
    """(commits oldest first, resolved baseline SHA, refusal reason or None).

    The range is the claim, so its endpoints must be exact and its walk must
    be the walk main took: a base that is not an ancestor of the end names no
    interval; a merge commit inside it means first-parent skipped revisions
    that are on main; an end that is not on origin/main is not main history.
    """
    base_sha, end_sha = _resolve_commit(base), _resolve_commit(end)
    if base_sha is None or end_sha is None:
        return [], "", f"range endpoints must resolve to commits: {base}..{end}"
    if not _git_succeeds("merge-base", "--is-ancestor", base_sha, end_sha):
        return [], base_sha, f"baseline {base_sha} is not an ancestor of end {end_sha}; no interval"
    if not _git_succeeds("merge-base", "--is-ancestor", end_sha, "origin/main"):
        return [], base_sha, f"end {end_sha} is not reachable from origin/main; not main history"
    if _git("rev-list", "--merges", f"{base_sha}..{end_sha}"):
        return [], base_sha, (
            f"{base_sha}..{end_sha} contains a merge commit; a first-parent walk would skip main revisions"
        )
    commits = _git("log", "--reverse", "--first-parent", "--format=%H %h %s", f"{base_sha}..{end_sha}")
    return commits, base_sha, None


def _repository_name() -> str:
    configured = os.environ.get("GITHUB_REPOSITORY", "")
    if configured:
        return configured
    try:
        url = _git("remote", "get-url", "origin")[0]
    except (subprocess.CalledProcessError, IndexError):
        return "unknown"
    match = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
    return match.group(1) if match else url


def _write_ledger(
    path: Path,
    *,
    baseline_sha: str,
    end_sha: str,
    revisions: list[dict[str, object]],
    counts: dict[str, int],
) -> None:
    """Measured facts only. A `dispositions` list in an existing ledger is the
    reviewer's record of what a gap means; it is carried over, never rewritten."""
    dispositions: list[object] = []
    if path.exists():
        try:
            previous = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(previous, dict) and isinstance(previous.get("dispositions"), list):
                dispositions = previous["dispositions"]
        except (OSError, json.JSONDecodeError):
            dispositions = []
    payload = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "repository": _repository_name(),
        "workflow": WORKFLOW,
        "range": {"baseline_sha": baseline_sha, "end_sha": end_sha},
        "measured_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": counts,
        "dispositions": dispositions,
        "revisions": revisions,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    window = parser.add_mutually_exclusive_group()
    window.add_argument(
        "--since-days",
        type=int,
        default=None,
        help=(
            "audit every commit on origin/main from the last N days (default 7); a time "
            "window, not a commit count, so a busy day cannot age a commit out unexamined"
        ),
    )
    window.add_argument(
        "--range",
        metavar="BASE..END",
        help=(
            "audit every first-parent commit after BASE up to and including END, both "
            "exact; the range is the claim, so nothing ages out of it"
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=400,
        help=(
            "safety cap on commits examined in the rolling window; reaching it means the "
            "window was truncated, which is unverified coverage and fails under --fail-on-gap"
        ),
    )
    parser.add_argument(
        "--ledger-out",
        type=Path,
        help="with --range, write the verdicts as a versioned JSON ledger at this path",
    )
    parser.add_argument(
        "--fail-on-gap",
        action="store_true",
        help=(
            "exit non-zero when a commit has no verdict-bearing releasability run "
            "OR when any commit could not be verified (unknown fails closed)"
        ),
    )
    arguments = parser.parse_args()
    if arguments.ledger_out is not None and arguments.range is None:
        parser.error("--ledger-out requires --range: a ledger of a rolling window ages out")

    if shutil.which("gh") is None:
        print("gh is not available; cannot ask which commits the gate evaluated.")
        return 1 if arguments.fail_on_gap else 0

    baseline_sha = ""
    if arguments.range is not None:
        match = _RANGE.match(arguments.range)
        if match is None:
            parser.error("--range must be BASE..END")
        commits, baseline_sha, refusal = _fixed_range(match.group("base"), match.group("end"))
        if refusal is not None:
            print(f"REFUSED  {refusal}")
            return 1
        truncated = False
        since_days = None
    else:
        since_days = 7 if arguments.since_days is None else arguments.since_days
        commits, truncated = _rolling_window(since_days, arguments.limit)

    ungated: list[str] = []
    unknown: list[str] = []
    failing: list[str] = []
    passing = 0
    ledger_revisions: list[dict[str, object]] = []

    for entry in commits:
        sha, short, subject = entry.split(" ", 2)
        conclusions = _run_conclusions(sha)
        verdict = _classify(conclusions)
        ledger_revisions.append(
            {
                "sha": sha,
                "short": short,
                "subject": subject,
                "verdict": verdict,
                "run_conclusions": list(conclusions or []),
            }
        )
        if conclusions is None:
            unknown.append(short)
            print(f"UNKNOWN  {short}  (run listing could not be fetched)")
            continue
        if verdict == "passing":
            passing += 1
            continue
        if verdict == "failing":
            failing.append(f"{short}  {subject[:70]}")
            continue
        if conclusions:
            # Runs exist but none reached a verdict (cancelled / in progress):
            # not proven ungated, but not verified either.
            unknown.append(short)
            print(f"UNKNOWN  {short}  (runs exist without a verdict: {sorted(set(conclusions))})")
            continue
        ungated.append(f"{short}  {subject[:70]}")
        print(f"UNGATED  {short}  {subject[:70]}")

    if arguments.range is not None:
        window_description = f"in range {arguments.range}"
    else:
        window_description = f"from the last {since_days} day(s)"
    print(
        f"\naudited {len(commits)} commit(s) on main {window_description}; "
        f"{len(ungated)} with no verdict-bearing {WORKFLOW} run; "
        f"{len(unknown)} unverifiable; "
        f"{passing} passing, {len(failing)} with a failing verdict."
    )
    if truncated:
        print(
            f"WINDOW TRUNCATED: the cap of {arguments.limit} commit(s) was reached, so "
            f"older commits inside the {since_days}-day window went unexamined. "
            "A prefix of the window is not the window; raise --limit and run again."
        )
    # Coverage is the invariant; the pass/fail split is reported beside it
    # because they are different claims: a failing verdict is information
    # (a backfilled historical tree measured against today's environment, or
    # an intermediate commit that fails its own tests), a missing run is
    # not. The audit fails only on missing/unverifiable coverage.
    for entry in failing:
        print(f"FAILING  {entry}")
    if ungated:
        print(
            "\nBackfill one with:\n"
            "  gh api repos/OWNER/REPO/git/refs "
            "-f ref=refs/tags/main-releasability-SHA -f sha=SHA\n"
            "  gh workflow run main-releasability.yml --ref main-releasability-SHA "
            "-f expected_sha=SHA -f triggering_pr=backfill\n"
        )
    if arguments.ledger_out is not None and commits:
        _write_ledger(
            arguments.ledger_out,
            baseline_sha=baseline_sha,
            end_sha=str(ledger_revisions[-1]["sha"]),
            revisions=ledger_revisions,
            counts={
                "examined": len(commits),
                "passing": passing,
                "failing": len(failing),
                "ungated": len(ungated),
                "unknown": len(unknown),
            },
        )
        print(f"ledger written: {arguments.ledger_out}")
    if arguments.fail_on_gap and (ungated or unknown or truncated):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
