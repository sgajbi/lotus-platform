from __future__ import annotations

import json
from pathlib import Path

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


def test_recorded_failed_collection_is_reported_by_the_quality_surface(monkeypatch) -> None:
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
        lambda _args: {
            "available": True,
            "command": ["pytest"],
            "returncode": 0,
            "summary": "1293 tests collected in 1.29s",
        },
    )

    result = baseline_generator._count_pytest_tests()

    assert result["collected_tests"] == 1293
    assert result["summary"] == "1293 tests collected"
