from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import automation.generate_enterprise_backend_quality_baseline as baseline_generator
from automation.generate_enterprise_backend_quality_baseline import (
    QUALITY_DOCS,
    build_baseline,
    render_baseline_report,
    render_health_report,
    render_scorecard,
    validate_quality_surface,
)


ROOT = Path(__file__).resolve().parents[2]


def test_quality_baseline_collects_required_enterprise_signals() -> None:
    baseline = build_baseline()

    assert baseline["repository"] == "lotus-platform"
    assert baseline["code_size"]["source_file_count"] > 0
    assert baseline["code_size"]["python_file_count"] > 0
    assert baseline["function_hotspots"]["python_function_count"] > 0
    assert "ruff" in baseline["quality_tooling"]
    assert "mypy" in baseline["quality_tooling"]
    assert "bandit" in baseline["quality_tooling"]
    assert "pip_audit" in baseline["quality_tooling"]
    assert "collected_tests" in baseline["tests"]
    assert "secret_keyword_review_candidates_sample" in baseline["security"]
    assert baseline["openapi"]["platform_business_api_owned"] is False


def test_quality_reports_render_before_after_scorecard_and_guidance_review() -> None:
    baseline = build_baseline()

    baseline_report = render_baseline_report(baseline)
    scorecard = render_scorecard(baseline)
    health_report = render_health_report(baseline)

    assert "Enterprise Backend Quality Baseline" in baseline_report
    assert "Function And Complexity Hotspots" in baseline_report
    assert "Tooling Baseline" in baseline_report
    assert "Security Baseline" in baseline_report
    assert "Enterprise Refactor Quality Scorecard" in scorecard
    assert "Before" in scorecard
    assert "Target After" in scorecard
    assert "Current max complexity" in scorecard
    assert "Conscious Guidance Review" in health_report
    assert "lotus-ci-enforcement-governance" in health_report
    assert "108. Analytics UI feature-milestone validator extraction" in health_report
    assert "109. Proof-artifact guardrail hardening" in health_report
    assert (
        "110. Certified endpoint response-example parity enforcement" in health_report
    )
    assert "Parseable examples could drift from runtime response truth" in scorecard


def test_quality_surface_is_wired_into_repo_checks_and_artifacts() -> None:
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(
        encoding="utf-8"
    )
    assert "generate_enterprise_backend_quality_baseline.py --check" in repo_checks

    for file_name in {
        "baseline_report.json",
        "baseline_report.md",
        "quality_scorecard.md",
        "refactor_health_report.md",
        *QUALITY_DOCS.keys(),
    }:
        path = ROOT / "quality" / file_name
        assert path.exists(), f"Missing quality artifact: {path}"
        assert path.read_text(encoding="utf-8").strip()

    baseline = json.loads(
        (ROOT / "quality" / "baseline_report.json").read_text(encoding="utf-8")
    )
    assert "code_size" in baseline
    assert "function_hotspots" in baseline
    assert "tests" in baseline
    assert validate_quality_surface() == []


def test_quality_surface_reports_invalid_baseline_json(
    tmp_path: Path,
    monkeypatch,
) -> None:
    quality_dir = tmp_path / "quality"
    quality_dir.mkdir()
    for file_name in {
        "baseline_report.md",
        "quality_scorecard.md",
        "refactor_health_report.md",
        *QUALITY_DOCS.keys(),
    }:
        (quality_dir / file_name).write_text("present", encoding="utf-8")
    (quality_dir / "baseline_report.json").write_text("{", encoding="utf-8")
    monkeypatch.setattr(baseline_generator, "QUALITY_DIR", quality_dir)

    errors = baseline_generator.validate_quality_surface()

    assert any(
        error.startswith("Invalid quality/baseline_report.json") for error in errors
    )


def test_quality_surface_reports_missing_required_baseline_keys(
    tmp_path: Path,
    monkeypatch,
) -> None:
    quality_dir = tmp_path / "quality"
    quality_dir.mkdir()
    for file_name in {
        "baseline_report.md",
        "quality_scorecard.md",
        "refactor_health_report.md",
        *QUALITY_DOCS.keys(),
    }:
        (quality_dir / file_name).write_text("present", encoding="utf-8")
    (quality_dir / "baseline_report.json").write_text(
        json.dumps({"code_size": {}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(baseline_generator, "QUALITY_DIR", quality_dir)

    errors = baseline_generator.validate_quality_surface()

    assert "quality/baseline_report.json missing `function_hotspots`" in errors
    assert "quality/baseline_report.json missing `quality_tooling`" in errors
    assert "quality/baseline_report.json missing `tests`" in errors
    assert "quality/baseline_report.json missing `security`" in errors


def test_quality_surface_reports_stale_material_baseline_metrics(
    tmp_path: Path,
    monkeypatch,
) -> None:
    quality_dir = tmp_path / "quality"
    quality_dir.mkdir()
    for file_name in {
        "baseline_report.md",
        "quality_scorecard.md",
        "refactor_health_report.md",
        *QUALITY_DOCS.keys(),
    }:
        (quality_dir / file_name).write_text("present", encoding="utf-8")
    accepted = {
        "code_size": {
            "source_file_count": 1,
            "total_source_lines": 10,
            "python_file_count": 1,
        },
        "function_hotspots": {
            "python_function_count": 1,
            "max_complexity": 5,
            "max_function_lines": 20,
        },
        "quality_tooling": {},
        "tests": {"collected_tests": 1},
        "security": {},
    }
    current = json.loads(json.dumps(accepted))
    current["function_hotspots"]["max_complexity"] = 6
    current["tests"]["collected_tests"] = 4
    (quality_dir / "baseline_report.json").write_text(
        json.dumps(accepted),
        encoding="utf-8",
    )
    monkeypatch.setattr(baseline_generator, "QUALITY_DIR", quality_dir)
    monkeypatch.setattr(baseline_generator, "build_baseline", lambda: current)

    errors = baseline_generator.validate_quality_surface()

    assert any("function_hotspots.max_complexity" in error for error in errors)
    assert any("tests.collected_tests" in error for error in errors)
    assert all("generated_at_utc" not in error for error in errors)


def test_quality_surface_tolerates_small_collection_count_variance(
    tmp_path: Path,
    monkeypatch,
) -> None:
    quality_dir = tmp_path / "quality"
    quality_dir.mkdir()
    for file_name in {
        "baseline_report.md",
        "quality_scorecard.md",
        "refactor_health_report.md",
        *QUALITY_DOCS.keys(),
    }:
        (quality_dir / file_name).write_text("present", encoding="utf-8")
    accepted = {
        "code_size": {
            "source_file_count": 1,
            "total_source_lines": 10,
            "python_file_count": 1,
        },
        "function_hotspots": {
            "python_function_count": 1,
            "max_complexity": 5,
            "max_function_lines": 20,
        },
        "quality_tooling": {},
        "tests": {"collected_tests": 716},
        "security": {},
    }
    current = json.loads(json.dumps(accepted))
    current["tests"]["collected_tests"] = 715
    (quality_dir / "baseline_report.json").write_text(
        json.dumps(accepted),
        encoding="utf-8",
    )
    monkeypatch.setattr(baseline_generator, "QUALITY_DIR", quality_dir)
    monkeypatch.setattr(baseline_generator, "build_baseline", lambda: current)

    assert baseline_generator.validate_quality_surface() == []


def test_quality_write_preserves_generated_timestamp_when_metrics_match() -> None:
    accepted = {
        "generated_at_utc": "2026-07-13T00:00:00Z",
        "code_size": {
            "source_file_count": 1,
            "total_source_lines": 10,
            "python_file_count": 1,
        },
        "function_hotspots": {
            "python_function_count": 1,
            "max_complexity": 5,
            "max_function_lines": 20,
        },
        "tests": {"collected_tests": 1},
    }
    current = json.loads(json.dumps(accepted))
    current["generated_at_utc"] = "2026-07-14T00:00:00Z"

    preserved = baseline_generator._preserve_generated_at_when_metrics_match(
        current,
        accepted,
    )
    current["function_hotspots"]["max_complexity"] = 6
    changed = baseline_generator._preserve_generated_at_when_metrics_match(
        current,
        accepted,
    )

    assert preserved["generated_at_utc"] == "2026-07-13T00:00:00Z"
    assert changed["generated_at_utc"] == "2026-07-14T00:00:00Z"


def test_quality_foundation_is_discoverable_from_docs_context_wiki_and_skill() -> None:
    expected_refs = [
        ROOT / "README.md",
        ROOT / "REPOSITORY-ENGINEERING-CONTEXT.md",
        ROOT / "context" / "LOTUS-ENGINEERING-CONTEXT.md",
        ROOT / "context" / "CONTEXT-REFERENCE-MAP.md",
        ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md",
        ROOT / "codex" / "skills" / "lotus-ci-enforcement-governance" / "SKILL.md",
        ROOT / "wiki" / "Home.md",
        ROOT / "wiki" / "Validation-and-CI.md",
        ROOT / "wiki" / "Enterprise-Backend-Refactor-Quality.md",
    ]

    for path in expected_refs:
        text = path.read_text(encoding="utf-8")
        assert (
            "generate_enterprise_backend_quality_baseline.py" in text
            or "quality/baseline_report.md" in text
        )

    sidebar = (ROOT / "wiki" / "_Sidebar.md").read_text(encoding="utf-8")
    assert "Enterprise-Backend-Refactor-Quality" in sidebar


def test_recorded_failed_collection_is_reported_by_the_quality_surface(
    monkeypatch,
) -> None:
    """A baseline carrying a failed collection must not validate as accepted.

    pytest prints a collected count and exits nonzero when a module fails to
    import, so the count alone cannot distinguish a full run from a partial one.
    A baseline accepted before this was enforced would otherwise remain the
    reference for every later comparison.
    """
    accepted = json.loads(
        (ROOT / "quality" / "baseline_report.json").read_text(encoding="utf-8")
    )
    assert accepted["tests"]["returncode"] == 0, "committed baseline is a healthy run"

    partial = json.loads(json.dumps(accepted))
    partial["tests"]["returncode"] = 2

    monkeypatch.setattr(
        baseline_generator, "_load_baseline_report", lambda errors: partial
    )
    errors = validate_quality_surface()

    assert any("returncode 2" in error for error in errors), errors


def test_healthy_collection_is_not_reported_as_partial(monkeypatch) -> None:
    """The guard must accept the shape it is supposed to accept."""
    accepted = json.loads(
        (ROOT / "quality" / "baseline_report.json").read_text(encoding="utf-8")
    )
    monkeypatch.setattr(
        baseline_generator, "_load_baseline_report", lambda errors: accepted
    )

    assert not [error for error in validate_quality_surface() if "returncode" in error]


def test_quality_write_refuses_partial_test_collection(monkeypatch, capsys) -> None:
    """A failed collection cannot overwrite the accepted quality artifacts."""
    partial = {"tests": {"collected_tests": 12, "returncode": 2}}
    write_attempted = False

    def record_write(_baseline: dict[str, object]) -> None:
        nonlocal write_attempted
        write_attempted = True

    monkeypatch.setattr(baseline_generator, "build_baseline", lambda: partial)
    monkeypatch.setattr(baseline_generator, "write_quality_artifacts", record_write)
    monkeypatch.setattr(baseline_generator.sys, "argv", ["quality-baseline", "--write"])

    assert baseline_generator.main() == 1
    assert write_attempted is False
    assert "partial run" in capsys.readouterr().err


def test_successful_collection_summary_excludes_volatile_duration(monkeypatch) -> None:
    monkeypatch.setattr(
        baseline_generator,
        "_run_command",
        lambda _args, **_kwargs: {
            "available": True,
            "command": ["pytest"],
            "returncode": 0,
            "summary": "1293 tests collected in 1.29s",
        },
    )

    result = baseline_generator._count_pytest_tests()

    assert result["collected_tests"] == 1293
    assert result["summary"] == "1293 tests collected"


def test_collection_freshness_compares_one_count_on_every_runner() -> None:
    """The collected-test count is a property of the tree, not of the host.

    A per-platform record cannot be maintained from a single machine: the other
    runner's number can only be transcribed from a log, and that log was written
    against a different tree. One number compared everywhere is both simpler and
    the only form this repository can keep honest.
    """
    accepted = {"tests": {"collected_tests": 1299}}

    within = {"tests": {"collected_tests": 1298}}
    assert baseline_generator._baseline_freshness_differences(accepted, within) == []

    drifted = {"tests": {"collected_tests": 1288}}
    assert any(
        "tests.collected_tests" in difference
        for difference in baseline_generator._baseline_freshness_differences(
            accepted, drifted
        )
    ), "a count that has moved beyond the tolerance must be reported"


@pytest.mark.parametrize("count", [10, 11, 12])
def test_collection_diagnostic_is_quiet_within_existing_tolerance(
    monkeypatch, capsys, count
):
    monkeypatch.setattr(
        baseline_generator,
        "_load_baseline_report",
        lambda _errors: {"tests": {"collected_tests": 10}},
    )
    baseline_generator._emit_collection_diagnostic(
        {"collected_tests": count, "returncode": 0}, ""
    )
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize(
    "stdout,returncode,count,status",
    [
        ("tests/unit/test_a.py::test_a\n", 0, 1, "complete"),
        (
            "tests/unit/test_a.py::test_a\ntests/unit/test_a.py::test_a\n",
            0,
            2,
            "duplicate-inventory",
        ),
        ("tests/../foreign.py::test_a\n", 0, 1, "malformed-inventory"),
        ("tests/unit/test_a.py::test_a\n", 0, 2, "inconsistent-inventory"),
        ("tests/unit/test_a.py::test_a\n", 2, 1, "partial-or-unavailable"),
        (None, None, 0, "missing-inventory"),
        ("x" * 1_048_577, 0, 1, "truncated-inventory"),
    ],
    ids=[
        "complete",
        "duplicate",
        "malformed",
        "inconsistent",
        "partial",
        "missing",
        "truncated",
    ],
)
def test_collection_diagnostic_labels_exact_and_bad_inventories(
    monkeypatch, capsys, stdout, returncode, count, status
):
    monkeypatch.setattr(
        baseline_generator,
        "_load_baseline_report",
        lambda _errors: {"tests": {"collected_tests": 10}},
    )
    baseline_generator._emit_collection_diagnostic(
        {"collected_tests": count, "returncode": returncode}, stdout
    )
    lines = capsys.readouterr().err.splitlines()
    assert lines[0] == "BEGIN LOTUS COLLECTION DIAGNOSTIC"
    assert lines[-1] == "END LOTUS COLLECTION DIAGNOSTIC"
    diagnostic = json.loads(lines[1])
    diagnostic["node_ids"] = [json.loads(line)["node_id"] for line in lines[2:-1]]
    assert status in diagnostic["status"]
    assert diagnostic["returncode"] == returncode
    assert diagnostic["parsed_count"] == count
    assert diagnostic["raw_node_count"] == len(diagnostic["node_ids"])
    assert diagnostic["unique_node_count"] == len(set(diagnostic["node_ids"]))
    assert diagnostic["accepted_count"] == 10
    assert diagnostic["python"] and diagnostic["platform"]
    if status == "complete":
        assert diagnostic["node_ids"] == ["tests/unit/test_a.py::test_a"]
    else:
        assert diagnostic["status"] != "complete"
    assert baseline_generator._baseline_freshness_differences(
        {"tests": {"collected_tests": 10}}, {"tests": {"collected_tests": count}}
    ), "diagnostics cannot accept the original discrepancy"


def test_default_command_payload_and_timeout_remain_unchanged(monkeypatch):
    monkeypatch.setattr(
        baseline_generator.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            ["tool"], 7, "first\nlast\n"
        ),
    )
    result = baseline_generator._run_command(["tool"])
    assert result == {
        "available": True,
        "command": ["tool"],
        "returncode": 7,
        "summary": "last",
    }

    def timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(["tool"], 120)

    monkeypatch.setattr(baseline_generator.subprocess, "run", timeout)
    result = baseline_generator._run_command(["tool"], retain_stdout=True)
    assert result["returncode"] is None
    assert "stdout" not in result
    assert result["summary"] == "timed out after 120 seconds"


def test_real_collection_diagnostic_reuses_subprocess_and_stays_out_of_artifacts(
    tmp_path, monkeypatch, capsys
):
    accepted = json.loads(
        (ROOT / "quality/baseline_report.json").read_text(encoding="utf-8")
    )
    suite = tmp_path / "tests/unit"
    suite.mkdir(parents=True)
    (suite / "test_tiny.py").write_text(
        "def test_tiny():\n    assert 2 + 2 == 4\n", encoding="utf-8"
    )
    monkeypatch.setattr(baseline_generator, "ROOT", tmp_path)
    monkeypatch.setattr(
        baseline_generator, "_load_baseline_report", lambda _errors: accepted
    )
    real_run = subprocess.run
    calls = []

    def record_run(args, **kwargs):
        calls.append(args)
        return real_run(args, **kwargs)

    monkeypatch.setattr(baseline_generator.subprocess, "run", record_run)
    measured = baseline_generator._count_pytest_tests()
    assert len(calls) == 1
    assert calls[0][1:] == ["-m", "pytest", "--collect-only", "-q", "tests/unit"]
    assert measured["returncode"] == 0
    assert measured["collected_tests"] == 1
    assert measured["summary"] == "1 tests collected"
    assert "stdout" not in measured and "node_ids" not in measured
    lines = capsys.readouterr().err.splitlines()
    diagnostic = json.loads(lines[1])
    assert diagnostic["status"] == "complete"
    assert [json.loads(line)["node_id"] for line in lines[2:-1]] == [
        "tests/unit/test_tiny.py::test_tiny"
    ]
    quality_dir = tmp_path / "quality"
    monkeypatch.setattr(baseline_generator, "QUALITY_DIR", quality_dir)
    accepted["tests"] = measured
    baseline_generator.write_quality_artifacts(accepted)
    written = json.loads(
        (quality_dir / "baseline_report.json").read_text(encoding="utf-8")
    )
    assert written["tests"] == measured
    assert "LOTUS COLLECTION DIAGNOSTIC" not in (
        quality_dir / "baseline_report.json"
    ).read_text(encoding="utf-8")

    # A real import failure must remain failed, not become a healthy inventory.
    (suite / "test_tiny.py").write_text(
        "raise RuntimeError('representative broken collection')\n", encoding="utf-8"
    )
    monkeypatch.setattr(
        baseline_generator,
        "_load_baseline_report",
        lambda _errors: {"tests": {"collected_tests": 10}},
    )
    calls.clear()
    failed = baseline_generator._count_pytest_tests()
    assert len(calls) == 1
    assert failed["returncode"] == 2
    diagnostic = json.loads(capsys.readouterr().err.splitlines()[1])
    assert "partial-or-unavailable" in diagnostic["status"]
    assert diagnostic["status"] != "complete"
    assert diagnostic["returncode"] == 2
