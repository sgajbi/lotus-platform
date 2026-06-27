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


def test_quality_surface_is_wired_into_repo_checks_and_artifacts() -> None:
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(encoding="utf-8")
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

    baseline = json.loads((ROOT / "quality" / "baseline_report.json").read_text(encoding="utf-8"))
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

    assert any(error.startswith("Invalid quality/baseline_report.json") for error in errors)


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
        assert "generate_enterprise_backend_quality_baseline.py" in text or "quality/baseline_report.md" in text

    sidebar = (ROOT / "wiki" / "_Sidebar.md").read_text(encoding="utf-8")
    assert "Enterprise-Backend-Refactor-Quality" in sidebar
