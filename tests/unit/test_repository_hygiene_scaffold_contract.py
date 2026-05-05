from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _powershell_executable() -> str:
    if sys.platform.startswith("win"):
        return "powershell"
    candidate = shutil.which("pwsh") or shutil.which("powershell")
    if candidate is None:
        raise AssertionError(
            "PowerShell executable not available for scaffold contract test"
        )
    return candidate


def test_repository_hygiene_standard_and_templates_exist() -> None:
    standards_readme = (ROOT / "platform-standards" / "README.md").read_text(
        encoding="utf-8"
    )
    hygiene_standard = (
        ROOT
        / "platform-standards"
        / "Repository-Hygiene-and-Dependency-Model-Standard.md"
    ).read_text(encoding="utf-8")
    scaffold_script = (ROOT / "automation" / "New-Lotus-Service.ps1").read_text(
        encoding="utf-8"
    )
    makefile_template = (
        ROOT / "platform-standards" / "templates" / "Makefile.backend.template"
    ).read_text(encoding="utf-8")
    feature_lane_template = (
        ROOT
        / "platform-standards"
        / "templates"
        / "workflows"
        / "feature-lane.backend.template.yml"
    ).read_text(encoding="utf-8")
    pr_merge_template = (
        ROOT
        / "platform-standards"
        / "templates"
        / "workflows"
        / "pr-merge-gate.backend.template.yml"
    ).read_text(encoding="utf-8")

    assert "Repository-Hygiene-and-Dependency-Model-Standard.md" in standards_readme
    assert ".editorconfig" in hygiene_standard
    assert ".gitattributes" in hygiene_standard
    assert ".gitignore" in hygiene_standard
    assert ".dockerignore" in hygiene_standard
    assert "pyproject.toml" in hygiene_standard
    assert "requirements/shared-runtime.lock.txt" in hygiene_standard
    assert "requirements/ci-tooling.lock.txt" in hygiene_standard
    assert 'preflight_fast_command = "make check"' in scaffold_script
    assert 'preflight_full_command = "make ci"' in scaffold_script
    assert (
        'Copy-Item (Join-Path $templateRoot ".editorconfig.backend.template")'
        in scaffold_script
    )
    assert (
        'Copy-Item (Join-Path $templateRoot ".gitattributes.backend.template")'
        in scaffold_script
    )
    assert (
        'Copy-Item (Join-Path $templateRoot ".gitignore.backend.template")'
        in scaffold_script
    )
    assert (
        'Copy-Item (Join-Path $templateRoot ".dockerignore.backend.template")'
        in scaffold_script
    )
    assert (
        'Copy-Item (Join-Path $templateRoot "requirements.shared-runtime.lock.template.txt")'
        in scaffold_script
    )
    assert (
        'Copy-Item (Join-Path $templateRoot "requirements.ci-tooling.lock.template.txt")'
        in scaffold_script
    )
    assert "Ensure-GitInitialCommit" in scaffold_script
    assert "git -C $TargetRepoRoot push -u origin main" in scaffold_script
    assert "missing summary" in scaffold_script
    assert "missing description" in scaffold_script
    assert "missing success response example" in scaffold_script
    assert "include_in_schema=False" in scaffold_script
    assert 'tags=["Health"]' in scaffold_script
    assert 'tags=["Metadata"]' in scaffold_script
    assert "ProblemDetails" in scaffold_script
    assert "problem_response" in scaffold_script
    assert "structured JSON application events" in scaffold_script
    assert "supported-features/supported-features.json" in scaffold_script
    assert "evidence/rfc-implementation/README.md" in scaffold_script
    assert (
        "evidence/rfc-implementation/evidence-manifest.template.json" in scaffold_script
    )
    assert '"slice_closure"' in scaffold_script
    assert '"api_certification"' in scaffold_script
    assert '"state_machine_review"' in scaffold_script
    assert '"supported_features_review"' in scaffold_script
    assert '"wiki_publication"' in scaffold_script
    assert '"downstream_realization"' in scaffold_script
    assert "docs/operations/api-certification.md" in scaffold_script
    assert "scripts/no_sensitive_content_guard.py" in scaffold_script
    assert "scripts/supported_features_gate.py" in scaffold_script
    assert (
        'require_response_headers = @("x-correlation-id", "x-trace-id")'
        in scaffold_script
    )
    assert (
        '[string[]]$RequiredLogPatterns = @("correlation", "trace", "service")'
        in scaffold_script
    )
    assert 'response.headers["X-Trace-Id"] = trace_id' in scaffold_script
    assert "monetary-float-guard:" in makefile_template
    assert "$(MAKE) monetary-float-guard" in makefile_template
    assert "no-sensitive-content-guard:" in makefile_template
    assert "$(MAKE) no-sensitive-content-guard" in makefile_template
    assert "supported-features-gate:" in makefile_template
    assert "$(MAKE) supported-features-gate" in makefile_template
    assert "coverage-gate:" in makefile_template
    assert "$(VENV_PYTHON) scripts/coverage_gate.py" in makefile_template
    assert (
        "$(VENV_PYTHON) -m pip_audit -r requirements/shared-runtime.lock.txt -r requirements/ci-tooling.lock.txt"
        in makefile_template
    )
    assert "run: ./.venv/bin/python -m pytest tests/unit" in feature_lane_template
    assert (
        "run: ./.venv/bin/python -m pytest ${{ matrix.path }} --cov=src --cov-report="
        in pr_merge_template
    )
    assert "./.venv/bin/python -m coverage combine coverage-data" in pr_merge_template
    assert 'Set-Content -Path (Join-Path $target ".gitignore")' not in scaffold_script


def test_scaffolded_repo_matches_repository_hygiene_baseline(tmp_path: Path) -> None:
    destination_root = tmp_path / "generated"
    destination_root.mkdir()
    service_name = "lotus-hygiene-demo"
    scaffold_script = ROOT / "automation" / "New-Lotus-Service.ps1"
    validator_script = ROOT / "automation" / "validate_repository_hygiene.py"
    repo_root = destination_root / service_name
    output_json = tmp_path / "repository-hygiene-validation.json"

    subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(scaffold_script),
            "-ServiceName",
            service_name,
            "-DestinationRoot",
            str(destination_root),
            "-SkipAutomationRegistration",
            "-Force",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            sys.executable,
            str(validator_script),
            "--repo-root",
            str(repo_root),
            "--output-json",
            str(output_json),
            "--output-markdown",
            str(tmp_path / "repository-hygiene-validation.md"),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    result = json.loads(output_json.read_text(encoding="utf-8"))
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    main_py = (repo_root / "src/app/main.py").read_text(encoding="utf-8")
    errors_py = (repo_root / "src/app/errors.py").read_text(encoding="utf-8")
    observability_py = (repo_root / "src/app/observability.py").read_text(
        encoding="utf-8"
    )
    correlation_middleware = (
        repo_root / "src/app/middleware/correlation.py"
    ).read_text(encoding="utf-8")
    health_tests = (repo_root / "tests/integration/test_health.py").read_text(
        encoding="utf-8"
    )
    service_contract_tests = (
        repo_root / "tests/unit/test_service_contract.py"
    ).read_text(encoding="utf-8")
    openapi_gate = (repo_root / "scripts/openapi_quality_gate.py").read_text(
        encoding="utf-8"
    )
    sensitive_content_guard = (
        repo_root / "scripts/no_sensitive_content_guard.py"
    ).read_text(encoding="utf-8")
    supported_features_gate = (
        repo_root / "scripts/supported_features_gate.py"
    ).read_text(encoding="utf-8")
    supported_features = json.loads(
        (repo_root / "supported-features/supported-features.json").read_text(
            encoding="utf-8"
        )
    )
    evidence_readme = (repo_root / "evidence/rfc-implementation/README.md").read_text(
        encoding="utf-8"
    )
    evidence_manifest_template = json.loads(
        (
            repo_root / "evidence/rfc-implementation/evidence-manifest.template.json"
        ).read_text(encoding="utf-8")
    )
    observability_doc = (repo_root / "docs/operations/observability.md").read_text(
        encoding="utf-8"
    )
    api_certification_doc = (
        repo_root / "docs/operations/api-certification.md"
    ).read_text(encoding="utf-8")
    assert result["ok"] is True
    assert result["dependency_authority"] == "pyproject"
    assert result["editorconfig_exists"] is True
    assert result["gitattributes_exists"] is True
    assert result["shared_runtime_lock_exists"] is True
    assert result["ci_tooling_lock_exists"] is True
    assert result["editorconfig_missing_patterns"] == []
    assert result["gitattributes_missing_patterns"] == []
    assert result["gitignore_missing_patterns"] == []
    assert result["dockerignore_missing_patterns"] == []
    assert "monetary-float-guard:" in makefile
    assert "$(MAKE) monetary-float-guard" in makefile
    assert "no-sensitive-content-guard:" in makefile
    assert "$(MAKE) no-sensitive-content-guard" in makefile
    assert "supported-features-gate:" in makefile
    assert "$(MAKE) supported-features-gate" in makefile
    assert "coverage-gate:" in makefile
    assert "$(VENV_PYTHON) scripts/coverage_gate.py" in makefile
    assert "include_in_schema=False" in main_py
    assert 'tags=["Health"]' in main_py
    assert 'summary="Get service health"' in main_py
    assert 'summary="Get readiness"' in main_py
    assert 'tags=["Metadata"]' in main_py
    assert "validation_exception_handler" in main_py
    assert "unhandled_exception_handler" in main_py
    assert "Request validation failed. Correct the request fields and retry." in main_py
    assert "ProblemDetails" in errors_py
    assert "Product-safe remediation guidance" in errors_py
    assert "json.dumps(payload, sort_keys=True, default=str)" in observability_py
    assert '"event": event_name' in observability_py
    assert "request.state.correlation_id = correlation_id" in correlation_middleware
    assert "request.state.trace_id = trace_id" in correlation_middleware
    assert (
        'response.headers["X-Correlation-Id"] = correlation_id'
        in correlation_middleware
    )
    assert 'response.headers["X-Trace-Id"] = trace_id' in correlation_middleware
    assert "test_correlation_and_trace_header_propagation" in health_tests
    assert "test_correlation_and_trace_headers_are_generated" in health_tests
    assert "test_not_found_error_is_product_safe" in health_tests
    assert "test_problem_details_are_product_safe" in service_contract_tests
    assert "test_supported_features_policy_starts_unpromoted" in service_contract_tests
    assert "missing summary" in openapi_gate
    assert "missing success response example" in openapi_gate
    assert "FORBIDDEN_PATTERNS" in sensitive_content_guard
    assert "request_body" in sensitive_content_guard
    assert "response_body" in sensitive_content_guard
    assert "Supported-features gate passed" in supported_features_gate
    assert "implemented feature missing promotion_evidence" in supported_features_gate
    assert supported_features == {
        "repository": service_name,
        "features": [],
        "policy": "Only implementation-backed behavior may be promoted to supported.",
    }
    evidence_readme_normalized = " ".join(evidence_readme.split())
    assert "machine-readable implementation evidence" in evidence_readme
    assert "client, portfolio, holding" in evidence_readme_normalized
    assert evidence_manifest_template["repository"] == service_name
    assert evidence_manifest_template["rfc_id"] == "RFC-0000"
    assert evidence_manifest_template["slice_id"] == "slice-0"
    assert evidence_manifest_template["slice_closure"] == {
        "implementation_complete": False,
        "tests_complete": False,
        "documentation_complete": False,
        "review_complete": False,
        "unsupported_claims_removed": False,
        "notes": "Replace with the slice closure decision.",
    }
    assert evidence_manifest_template["api_certification"] == {
        "openapi_gate": "not_run",
        "certified_endpoints": [],
        "degraded_error_examples_reviewed": False,
        "attribute_examples_reviewed": False,
    }
    assert evidence_manifest_template["state_machine_review"] == {
        "applies": False,
        "transition_matrix_path": None,
        "allowed_transition_tests": [],
        "rejected_transition_tests": [],
    }
    assert evidence_manifest_template["supported_features_review"] == {
        "supported_features_path": "supported-features/supported-features.json",
        "promoted_features": [],
        "deferred_features": [],
        "no_aspirational_claims": False,
    }
    assert evidence_manifest_template["wiki_publication"] == {
        "wiki_source_changed": False,
        "check_only_status": "not_run",
        "publish_required_after_merge": False,
        "published_commit": None,
    }
    assert (
        evidence_manifest_template["validation_commands"][0]["command"] == "make check"
    )
    assert (
        evidence_manifest_template["artifacts"][0]["hash"]
        == "sha256:replace-after-generation"
    )
    assert evidence_manifest_template["cross_app_evidence"] == []
    assert evidence_manifest_template["downstream_realization"] == []
    assert "structured JSON application events" in observability_doc
    assert "must not include client names" in observability_doc
    assert "clear what/when/how description" in api_certification_doc
    assert "product-safe error examples" in api_certification_doc
    assert "Source-Degraded And Reconciliation Endpoints" in api_certification_doc
    assert "explicit source-owner fields" in api_certification_doc
    assert (
        "READY, DEGRADED, BLOCKED, and NOT_SUPPORTED examples" in api_certification_doc
    )
    assert (
        "does not clone calculations owned by another Lotus app"
        in api_certification_doc
    )
    assert (
        "$(VENV_PYTHON) -m pip_audit -r requirements/shared-runtime.lock.txt -r requirements/ci-tooling.lock.txt"
        in makefile
    )
