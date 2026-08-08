from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GH_FIX_CI_SCRIPT = (
    ROOT / "codex" / "skills" / "gh-fix-ci" / "scripts" / "inspect_pr_checks.py"
)
GH_ADDRESS_COMMENTS_SCRIPT = (
    ROOT
    / "codex"
    / "skills"
    / "gh-address-comments"
    / "scripts"
    / "fetch_comments.py"
)


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gh_fix_ci_job_log_decodes_non_utf8_bytes_with_replacement(monkeypatch, tmp_path) -> None:
    module = _load_module(GH_FIX_CI_SCRIPT, "inspect_pr_checks")

    monkeypatch.setattr(module, "fetch_repo_slug", lambda repo_root: "sgajbi/example")

    def fake_run(command, cwd=None, capture_output=False, **kwargs):
        assert command == ["gh", "api", "/repos/sgajbi/example/actions/jobs/88187783077/logs"]
        assert capture_output is True
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout=b"ok\nbad-byte:\x81\nTraceback: boom\n",
            stderr=b"",
        )

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    log_text, error = module.fetch_job_log("88187783077", tmp_path)

    assert error == ""
    assert "Traceback: boom" in log_text
    assert "\ufffd" in log_text


def test_gh_fix_ci_unavailable_log_reports_error_without_splitlines(monkeypatch, tmp_path) -> None:
    module = _load_module(GH_FIX_CI_SCRIPT, "inspect_pr_checks")

    monkeypatch.setattr(module, "fetch_run_metadata", lambda run_id, repo_root: {})
    monkeypatch.setattr(
        module,
        "fetch_check_log",
        lambda *, run_id, job_id, repo_root: ("", "UnicodeDecodeError: bad byte", "error"),
    )

    result = module.analyze_check(
        {
            "name": "Coverage Gate",
            "detailsUrl": "https://github.com/sgajbi/example/actions/runs/123/job/456",
        },
        repo_root=tmp_path,
        max_lines=20,
        context=5,
    )

    assert result["status"] == "log_unavailable"
    assert result["error"] == "UnicodeDecodeError: bad byte"
    assert "logSnippet" not in result


def test_gh_address_comments_forces_utf8_subprocess_decoding(monkeypatch) -> None:
    module = _load_module(GH_ADDRESS_COMMENTS_SCRIPT, "fetch_comments")
    calls: list[dict[str, Any]] = []

    def fake_run(cmd, **kwargs):
        calls.append({"cmd": cmd, **kwargs})
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=0,
            stdout='{"ok":"✓"}',
            stderr=None,
        )

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    output = module._run(["gh", "api", "graphql"], stdin="query")

    assert output == '{"ok":"✓"}'
    assert calls == [
        {
            "cmd": ["gh", "api", "graphql"],
            "input": "query",
            "capture_output": True,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
        }
    ]


def test_gh_address_comments_uses_pull_request_base_repository(monkeypatch) -> None:
    module = _load_module(GH_ADDRESS_COMMENTS_SCRIPT, "fetch_comments_base_repo")

    monkeypatch.setattr(
        module,
        "gh_pr_view_json",
        lambda fields: {
            "number": 655,
            "url": "https://github.com/sgajbi/lotus-platform/pull/655",
            "headRepositoryOwner": {"login": "fork-owner"},
            "headRepository": {"name": "lotus-platform-fork"},
        },
    )

    assert module.get_current_pr_ref() == ("sgajbi", "lotus-platform", 655)


def test_gh_address_comments_stops_fetching_completed_connections(monkeypatch) -> None:
    module = _load_module(GH_ADDRESS_COMMENTS_SCRIPT, "fetch_comments_pagination")
    calls: list[dict[str, Any]] = []

    def fake_graphql(**kwargs):
        calls.append(kwargs)
        call_number = len(calls)
        return {
            "data": {
                "repository": {
                    "pullRequest": {
                        "number": 7,
                        "url": "https://github.com/sgajbi/lotus-platform/pull/7",
                        "title": "Review",
                        "state": "OPEN",
                        "comments": None
                        if not kwargs["include_comments"]
                        else {
                            "pageInfo": {
                                "hasNextPage": call_number == 1,
                                "endCursor": f"comments-{call_number}",
                            },
                            "nodes": [{"id": f"comment-{call_number}"}],
                        },
                        "reviews": None
                        if not kwargs["include_reviews"]
                        else {
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                            "nodes": [{"id": "review-1"}],
                        },
                        "reviewThreads": None
                        if not kwargs["include_threads"]
                        else {
                            "pageInfo": {
                                "hasNextPage": call_number < 3,
                                "endCursor": f"thread-{call_number}",
                            },
                            "nodes": [{"id": f"thread-{call_number}"}],
                        },
                    }
                }
            }
        }

    monkeypatch.setattr(module, "gh_api_graphql", fake_graphql)

    result = module.fetch_all("sgajbi", "lotus-platform", 7)

    assert [item["id"] for item in result["conversation_comments"]] == [
        "comment-1",
        "comment-2",
    ]
    assert [item["id"] for item in result["reviews"]] == ["review-1"]
    assert [item["id"] for item in result["review_threads"]] == [
        "thread-1",
        "thread-2",
        "thread-3",
    ]
    assert calls[1]["include_reviews"] is False
    assert calls[2]["include_comments"] is False
    assert calls[2]["include_reviews"] is False


def test_gh_fix_ci_json_mode_reports_empty_results_when_no_checks_fail(
    monkeypatch, tmp_path, capsys
) -> None:
    module = _load_module(GH_FIX_CI_SCRIPT, "inspect_pr_checks_empty_json")

    monkeypatch.setattr(module, "parse_args", lambda: type("Args", (), {
        "repo": str(tmp_path),
        "pr": "655",
        "max_lines": 20,
        "context": 5,
        "json": True,
    })())
    monkeypatch.setattr(module, "find_git_root", lambda path: tmp_path)
    monkeypatch.setattr(module, "ensure_gh_available", lambda repo_root: True)
    monkeypatch.setattr(module, "resolve_pr", lambda pr, repo_root: pr)
    monkeypatch.setattr(
        module,
        "fetch_checks",
        lambda pr, repo_root: [{"name": "PR Merge Gate", "conclusion": "success"}],
    )

    assert module.main() == 0
    assert json.loads(capsys.readouterr().out) == {"pr": "655", "results": []}
