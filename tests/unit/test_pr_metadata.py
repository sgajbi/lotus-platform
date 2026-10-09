from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from automation import validate_pr_metadata as gate

ROOT = Path(__file__).resolve().parents[2]
REPO = "sgajbi/lotus-platform"
HEAD = "a" * 40
BODY = "Related issue: #609\nRemaining acceptance: Keep #609 open.\nIntended closures: none\n"


def page(body=BODY, nodes=None, total=0, more=False, cursor=None):
    return {
        "number": 943,
        "title": "Enforce metadata policy",
        "body": body,
        "headRefOid": HEAD,
        "baseRefName": "main",
        "state": "OPEN",
        "updatedAt": "2026-10-10T01:00:00Z",
        "url": f"https://github.com/{REPO}/pull/943",
        "closingIssuesReferences": {
            "nodes": nodes or [],
            "totalCount": total,
            "pageInfo": {"hasNextPage": more, "endCursor": cursor},
        },
    }


def node(number, repo=REPO):
    return {"number": number, "repository": {"nameWithOwner": repo}}


@pytest.mark.parametrize(
    "unsafe",
    [
        "This PR does not close #188",  # Archive PR190 incident
        "This PR must not close #609",  # Performance PR639 incident
        "Do not resolve sgajbi/lotus-platform#609",
        "Never fixes https://github.com/sgajbi/lotus-performance/issues/609",
        "Closes https://github.com/sgajbi/lotus-platform/issues/invalid",
        "Closes #0",
        "Closes #abc",
        "Closes #609 and #610",
        "fixes #609",
        "```\nCloses #609\n```",
        "> Closes #609",
        "`Closes #609`",
        "Closes #609",  # unapproved affirmative closure
    ],
)
def test_candidate_refuses_ambiguous_or_unintended_closure(unsafe):
    with pytest.raises(gate.MetadataError):
        gate.validate_candidate("Bounded slice", BODY + unsafe, REPO)


@pytest.mark.parametrize(
    "ref",
    [
        "#609",
        "sgajbi/lotus-performance#609",
        "https://github.com/sgajbi/lotus-archive/issues/188",
    ],
)
def test_candidate_accepts_authorized_standalone_completion(ref):
    body = f"Related issue: #609\nIntended closures: {ref}\nCloses {ref}\n"
    assert gate.validate_candidate("Complete bounded issue", body, REPO) == {
        gate.reference(ref, REPO)
    }


def test_neutral_keep_open_and_unicode():
    assert (
        gate.validate_candidate("Metadata safety — bounded slice", BODY, REPO) == set()
    )
    crlf = BODY.replace("\n", "\r\n")
    assert (
        gate.validate_candidate("Metadata safety — bounded slice", crlf, REPO) == set()
    )
    assert gate.validate_live(REPO, 943, HEAD, lambda *_: page(crlf))["complete"]
    with pytest.raises(gate.MetadataError):
        gate.validate_candidate("Two\rlines", BODY, REPO)


@pytest.mark.parametrize(
    "title,body,repo",
    [
        ("", BODY, REPO),
        ("two\nlines", BODY, REPO),
        ("Closes #609", BODY, REPO),
        ("Title", "No issue here\nIntended closures: none", REPO),
        ("Title", "Related issue: #609", REPO),
        ("Title", BODY + "Intended closures: none\n", REPO),
        ("Title", BODY.replace("none", "#abc"), REPO),
        ("Title", BODY + "Related issue: unknown/repo#5", REPO),
        ("Title", BODY, "unknown/repo"),
    ],
)
def test_candidate_fails_closed(title, body, repo):
    with pytest.raises(gate.MetadataError):
        gate.validate_candidate(title, body, repo)


def test_live_empty_actual_is_distinct_from_offline_policy():
    calls = []

    def fetch(repo, number, cursor):
        calls.append(cursor)
        return page()

    result = gate.validate_live(REPO, 943, HEAD, fetch)
    assert result["complete"] and result["mode"] == "live"
    assert result["closing_references"] == [] and calls == [None, None]


def test_live_paginates_all_references_and_binds_current_identity():
    body = "Intended closures: #609, sgajbi/lotus-archive#188\nCloses #609\nCloses sgajbi/lotus-archive#188"
    first = page(body, [node(609)], 2, True, "next")
    second = page(body, [node(188, "sgajbi/lotus-archive")], 2)
    calls = []

    def fetch(repo, number, cursor):
        calls.append(cursor)
        return second if cursor else first

    result = gate.validate_live(REPO, 943, HEAD, fetch)
    assert len(result["closing_references"]) == 2 and calls == [None, "next", None]


@pytest.mark.parametrize(
    "mutation",
    [
        lambda p: p.pop("closingIssuesReferences"),
        lambda p: p.update(headRefOid="b" * 40),
        lambda p: p.update(number=944),
        lambda p: p.update(url="https://github.com/other/repo/pull/943"),
        lambda p: p.update(state="MERGED"),
        lambda p: p.update(baseRefName="develop"),
        lambda p: p.pop("body"),
        lambda p: p["closingIssuesReferences"].pop("pageInfo"),
        lambda p: p["closingIssuesReferences"].update(totalCount=1),
        lambda p: p["closingIssuesReferences"].update(totalCount=True),
        lambda p: p["closingIssuesReferences"].update(nodes=[{}]),
        lambda p: p["closingIssuesReferences"].update(
            nodes=[node(1, "unknown/repo")], totalCount=1
        ),
        lambda p: p["closingIssuesReferences"].update(nodes=[node(609)], totalCount=1),
        lambda p: p["closingIssuesReferences"]["pageInfo"].update(hasNextPage=True),
        lambda p: p["closingIssuesReferences"]["pageInfo"].pop("endCursor"),
    ],
)
def test_live_rejects_missing_malformed_unknown_or_contradictory_evidence(mutation):
    payload = page()
    mutation(payload)
    with pytest.raises(gate.MetadataError):
        gate.validate_live(REPO, 943, HEAD, lambda *_: payload)


@pytest.mark.parametrize(
    "field,value",
    [
        ("body", BODY + "New text"),
        ("headRefOid", "b" * 40),
        ("updatedAt", "later"),
        ("title", "New title"),
    ],
)
def test_fresh_read_rejects_metadata_changed_after_collection(field, value):
    original, changed = page(), page()
    changed[field] = value
    replies = iter([original, changed])
    with pytest.raises(gate.MetadataError):
        gate.validate_live(REPO, 943, HEAD, lambda *_: next(replies))


def test_pagination_failure_and_repeated_cursor_fail_closed():
    first = page(nodes=[node(1)], total=3, more=True, cursor="repeat")
    second = page(nodes=[node(2)], total=3, more=True, cursor="repeat")
    replies = iter([first, second])
    with pytest.raises(gate.MetadataError, match="progress"):
        gate.collect_current(REPO, 943, HEAD, lambda *_: next(replies))

    def failed(*args):
        raise gate.MetadataError("Pagination API failure")

    with pytest.raises(gate.MetadataError):
        gate.collect_current(
            REPO,
            943,
            HEAD,
            lambda repo, number, cursor: failed() if cursor else first,
        )


@pytest.mark.parametrize(
    "stdout,returncode",
    [('{"errors":[{}]}', 0), ("{}", 0), ("not json", 0), ('{"data":null}', 0), ("", 1)],
)
def test_graphql_transport_or_partial_response_never_passes(
    monkeypatch, stdout, returncode
):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a, returncode, stdout, "hidden"),
    )
    with pytest.raises(gate.MetadataError):
        gate.github_page(REPO, 943, None)


def test_live_uses_current_body_not_stale_event_body():
    # No event body is accepted by the API: current unsafe body rejects even
    # when a prior event body was safe, and repaired current body can pass.
    bad = page(BODY + "This PR must not close #609")
    with pytest.raises(gate.MetadataError):
        gate.validate_live(REPO, 943, HEAD, lambda *_: bad)
    assert gate.validate_live(REPO, 943, HEAD, lambda *_: page())["complete"]


def test_absolute_candidate_invocation_from_application_without_automation(tmp_path):
    body = tmp_path / "body.txt"
    body.write_text(BODY, encoding="utf-8-sig")
    env = dict(os.environ, LOTUS_PR_TITLE="Metadata safety — bounded slice")
    command = [
        sys.executable,
        str(ROOT / "automation/validate_pr_metadata.py"),
        "--repo",
        "sgajbi/lotus-workbench",
        "candidate",
        "--title-env",
        "LOTUS_PR_TITLE",
        "--body-file",
        str(body),
    ]
    result = subprocess.run(
        command, cwd=tmp_path, env=env, capture_output=True, text=True
    )
    assert (
        result.returncode == 0 and json.loads(result.stdout)["github_evidence"] is False
    )
    body.write_text(BODY + "does not close #188", encoding="utf-8")
    rejected = subprocess.run(
        command, cwd=tmp_path, env=env, capture_output=True, text=True
    )
    assert rejected.returncode == 1


def test_required_lane_is_live_and_refreshes_metadata_edits():
    workflow = (ROOT / ".github/workflows/pr-merge-gate.yml").read_text()
    contracts = workflow.split("  repo-contracts:", 1)[1]
    assert "opened, synchronize, reopened, edited, ready_for_review" in workflow
    assert "Validate current PR metadata" in contracts
    assert (
        "validate_pr_metadata.py" in contracts
        and 'live --pr "$PR_NUMBER" --expected-head "$PR_HEAD"' in contracts
    )
    assert "pull-requests: read" in workflow and "issues: read" in workflow
    native = (ROOT / "automation/Invoke-PlatformRepoChecks.ps1").read_text()
    assert "Invoke-CheckedCommand $toolingPython -m pytest tests/unit -q" in native
