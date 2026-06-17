from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _qa_entry(repo_name: str) -> dict:
    qa_matrix = json.loads((ROOT / "automation" / "qa-matrix.json").read_text(encoding="utf-8"))
    return next(item for item in qa_matrix["repositories"] if item["repo"] == repo_name)


def test_generic_log_probes_use_request_completion_not_audit_tail() -> None:
    for repo_name in ["lotus-advise", "lotus-manage"]:
        patterns = _qa_entry(repo_name)["checks"]["observability"]["required_log_patterns"]

        assert patterns == ["correlation", "request.completed", "service"]


def test_audit_generating_services_keep_audit_log_expectations() -> None:
    patterns = _qa_entry("lotus-report")["checks"]["observability"]["required_log_patterns"]

    assert "audit" in patterns

