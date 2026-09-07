from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _qa_entry(repo_name: str) -> dict:
    qa_matrix = json.loads((ROOT / "automation" / "qa-matrix.json").read_text(encoding="utf-8"))
    return next(item for item in qa_matrix["repositories"] if item["repo"] == repo_name)


def _pattern_names(repo_name: str) -> list[str]:
    """The patterns a repository asserts, whichever form they are declared in.

    Invariants gained a probe in #828, so they are objects rather than bare
    strings. What each repository asserts did not change, and that is what these
    checks are about.
    """
    return [
        invariant if isinstance(invariant, str) else invariant["pattern"]
        for invariant in _qa_entry(repo_name)["checks"]["observability"]["required_log_patterns"]
    ]


def test_generic_log_probes_use_request_completion_not_audit_tail() -> None:
    for repo_name in ["lotus-advise", "lotus-manage"]:
        assert _pattern_names(repo_name) == ["correlation", "request.completed", "service"]


def test_audit_generating_services_keep_audit_log_expectations() -> None:
    assert "audit" in _pattern_names("lotus-report")


def test_request_lifecycle_invariants_are_provoked_rather_than_searched_for() -> None:
    """An invariant a health request exercises must name that request.

    Matching a bare word against a log window satisfies `service` from startup
    output and fails `audit` on a healthy service, so the assertion said nothing
    about the request path either way.
    """
    lifecycle = {"correlation", "request.completed", "service", "latency_ms", "duration", "request", "trace"}
    matrix = json.loads((ROOT / "automation" / "qa-matrix.json").read_text(encoding="utf-8"))

    unprovoked: list[str] = []
    for entry in matrix["repositories"]:
        observability = entry.get("checks", {}).get("observability", {})
        for invariant in observability.get("required_log_patterns", []):
            if isinstance(invariant, str) and invariant in lifecycle:
                unprovoked.append(f"{entry['repo']}:{invariant}")

    assert unprovoked == [], unprovoked
