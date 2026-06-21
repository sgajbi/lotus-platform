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


def _run_scaffold(
    *,
    destination_root: Path,
    service_name: str,
    service_profile: str | None = None,
    include_mesh_placeholders: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    command = [
        _powershell_executable(),
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "automation" / "New-Lotus-Service.ps1"),
        "-ServiceName",
        service_name,
        "-DestinationRoot",
        str(destination_root),
        "-SkipAutomationRegistration",
        "-Force",
    ]
    if service_profile is not None:
        command.extend(["-ServiceProfile", service_profile])
    if include_mesh_placeholders:
        command.append("-IncludeMeshPlaceholders")
    return subprocess.run(
        command,
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


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
    assert '"quality",' in scaffold_script
    assert "quality/quality_scorecard.md" in scaffold_script
    assert "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md" in scaffold_script
    assert "evidence/rfc-implementation/README.md" in scaffold_script
    assert (
        "evidence/rfc-implementation/evidence-manifest.template.json" in scaffold_script
    )
    assert '"slice_closure"' in scaffold_script
    assert '"api_certification"' in scaffold_script
    assert '"state_machine_review"' in scaffold_script
    assert '"supported_features_review"' in scaffold_script
    assert '"wiki_publication"' in scaffold_script
    assert '"upstream_realization"' in scaffold_script
    assert '"source_contract_realization"' in scaffold_script
    assert '"downstream_realization"' in scaffold_script
    assert "docs/operations/api-certification.md" in scaffold_script
    assert "scripts/no_sensitive_content_guard.py" in scaffold_script
    assert "scripts/supported_features_gate.py" in scaffold_script
    assert "scripts/endpoint_certification_gate.py" in scaffold_script
    assert '[string]$ServiceProfile = ""' in scaffold_script
    assert '"domain-service"' in scaffold_script
    assert '"experience-api"' in scaffold_script
    assert '"shared-capability-service"' in scaffold_script
    assert '"client-facing-service"' in scaffold_script
    assert "src/app/api" in scaffold_script
    assert "src/app/application" in scaffold_script
    assert "src/app/domain" in scaffold_script
    assert "src/app/ports" in scaffold_script
    assert "src/app/infrastructure" in scaffold_script
    assert "src/app/observability" in scaffold_script
    assert "src/app/security" in scaffold_script
    assert "src/app/resilience" in scaffold_script
    assert "src/app/security/caller_context.py" in scaffold_script
    assert "src/app/infrastructure/downstream_client.py" in scaffold_script
    assert "src/app/domain/idempotency.py" in scaffold_script
    assert "src/app/domain/audit.py" in scaffold_script
    assert "tests/unit/test_security_caller_context.py" in scaffold_script
    assert "tests/unit/test_downstream_client.py" in scaffold_script
    assert "tests/unit/test_idempotency_audit.py" in scaffold_script
    assert "docs/demo/demo-claims.md" in scaffold_script
    assert "Status: Planned" in scaffold_script
    assert "[switch]$IncludeMeshPlaceholders" in scaffold_script
    assert "contracts/domain-data-products" in scaffold_script
    assert "not_certified" in scaffold_script
    assert "scripts/architecture_boundary_gate.py" in scaffold_script
    assert "scripts/generate_quality_baseline.py" in scaffold_script
    assert "architecture-boundary-report:" in scaffold_script
    assert "quality-baseline: architecture-boundary-report" in scaffold_script
    assert "architecture_boundary_report_exists" in scaffold_script
    assert "quality/architecture_boundary_report.json is missing" in scaffold_script
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
    assert "endpoint-certification-gate:" in makefile_template
    assert "$(MAKE) endpoint-certification-gate" in makefile_template
    assert "architecture-boundary-report:" in makefile_template
    assert (
        "scripts/architecture_boundary_gate.py --mode report-only" in makefile_template
    )
    assert "quality-baseline: architecture-boundary-report" in makefile_template
    assert "scripts/generate_quality_baseline.py" in makefile_template
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
    validator_script = ROOT / "automation" / "validate_repository_hygiene.py"
    repo_root = destination_root / service_name
    output_json = tmp_path / "repository-hygiene-validation.json"

    _run_scaffold(destination_root=destination_root, service_name=service_name)

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
    endpoint_gate = subprocess.run(
        [sys.executable, "scripts/endpoint_certification_gate.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    missing_architecture_quality_baseline = subprocess.run(
        [sys.executable, "scripts/generate_quality_baseline.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    missing_architecture_quality_report = json.loads(
        (repo_root / "quality/baseline_report.json").read_text(encoding="utf-8")
    )
    architecture_gate = subprocess.run(
        [sys.executable, "scripts/architecture_boundary_gate.py", "--mode", "blocking"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    quality_baseline = subprocess.run(
        [sys.executable, "scripts/generate_quality_baseline.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    bad_boundary = repo_root / "src/app/domain/bad_boundary.py"
    bad_boundary.write_text("from fastapi import FastAPI\n", encoding="utf-8")
    architecture_failure = subprocess.run(
        [sys.executable, "scripts/architecture_boundary_gate.py", "--mode", "blocking"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    bad_boundary.unlink()
    subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "src", "tests"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    result = json.loads(output_json.read_text(encoding="utf-8"))
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    main_py = (repo_root / "src/app/main.py").read_text(encoding="utf-8")
    errors_py = (repo_root / "src/app/errors.py").read_text(encoding="utf-8")
    app_readme = (repo_root / "src/app/README.md").read_text(encoding="utf-8")
    domain_profile = (repo_root / "src/app/domain/service_profile.py").read_text(
        encoding="utf-8"
    )
    application_profile = (
        repo_root / "src/app/application/service_profile.py"
    ).read_text(encoding="utf-8")
    observability_init = (repo_root / "src/app/observability/__init__.py").read_text(
        encoding="utf-8"
    )
    observability_py = (repo_root / "src/app/observability/logging.py").read_text(
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
    security_caller_context = (
        repo_root / "src/app/security/caller_context.py"
    ).read_text(encoding="utf-8")
    downstream_client = (
        repo_root / "src/app/infrastructure/downstream_client.py"
    ).read_text(encoding="utf-8")
    idempotency_model = (repo_root / "src/app/domain/idempotency.py").read_text(
        encoding="utf-8"
    )
    audit_model = (repo_root / "src/app/domain/audit.py").read_text(encoding="utf-8")
    security_tests = (
        repo_root / "tests/unit/test_security_caller_context.py"
    ).read_text(encoding="utf-8")
    downstream_client_tests = (
        repo_root / "tests/unit/test_downstream_client.py"
    ).read_text(encoding="utf-8")
    idempotency_audit_tests = (
        repo_root / "tests/unit/test_idempotency_audit.py"
    ).read_text(encoding="utf-8")
    demo_claims = (repo_root / "docs/demo/demo-claims.md").read_text(encoding="utf-8")
    durability_standard = (
        repo_root / "docs/standards/durability-consistency.md"
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
    endpoint_certification_gate = (
        repo_root / "scripts/endpoint_certification_gate.py"
    ).read_text(encoding="utf-8")
    architecture_boundary_gate = (
        repo_root / "scripts/architecture_boundary_gate.py"
    ).read_text(encoding="utf-8")
    quality_baseline_script = (
        repo_root / "scripts/generate_quality_baseline.py"
    ).read_text(encoding="utf-8")
    supported_features = json.loads(
        (repo_root / "supported-features/supported-features.json").read_text(
            encoding="utf-8"
        )
    )
    endpoint_certification = json.loads(
        (repo_root / "docs/operations/endpoint-certification-ledger.json").read_text(
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
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    repo_context = (repo_root / "REPOSITORY-ENGINEERING-CONTEXT.md").read_text(
        encoding="utf-8"
    )
    wiki_home = (repo_root / "wiki/Home.md").read_text(encoding="utf-8")
    quality_scorecard = (repo_root / "quality/quality_scorecard.md").read_text(
        encoding="utf-8"
    )
    architecture_rules = (repo_root / "quality/architecture_rules.md").read_text(
        encoding="utf-8"
    )
    ci_quality_gates = (repo_root / "quality/ci_quality_gates.md").read_text(
        encoding="utf-8"
    )
    refactor_decisions = (repo_root / "quality/refactor_decisions.md").read_text(
        encoding="utf-8"
    )
    architecture_boundary_report = json.loads(
        (repo_root / "quality/architecture_boundary_report.json").read_text(
            encoding="utf-8"
        )
    )
    quality_baseline_report = json.loads(
        (repo_root / "quality/baseline_report.json").read_text(encoding="utf-8")
    )
    quality_baseline_markdown = (repo_root / "quality/baseline_report.md").read_text(
        encoding="utf-8"
    )
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
    assert "endpoint-certification-gate:" in makefile
    assert "$(MAKE) endpoint-certification-gate" in makefile
    assert "architecture-boundary-report:" in makefile
    assert "scripts/architecture_boundary_gate.py --mode report-only" in makefile
    assert "quality-baseline: architecture-boundary-report" in makefile
    assert "scripts/generate_quality_baseline.py" in makefile
    assert "ci: lint typecheck openapi-gate" in makefile
    assert "coverage-gate:" in makefile
    assert "$(VENV_PYTHON) scripts/coverage_gate.py" in makefile
    assert (repo_root / "src/app/api/__init__.py").exists()
    assert (repo_root / "src/app/application/__init__.py").exists()
    assert (repo_root / "src/app/domain/__init__.py").exists()
    assert (repo_root / "src/app/ports/__init__.py").exists()
    assert (repo_root / "src/app/infrastructure/__init__.py").exists()
    assert (repo_root / "src/app/observability/__init__.py").exists()
    assert (repo_root / "src/app/security/__init__.py").exists()
    assert (repo_root / "src/app/resilience/__init__.py").exists()
    assert not (repo_root / "contracts/domain-data-products").exists()
    assert not (repo_root / "contracts/trust-telemetry").exists()
    assert "Expected dependency flow" in app_readme
    assert 'name="domain-service"' in domain_profile
    assert "Domain-authoritative backend service" in domain_profile
    assert "current_service_profile" in application_profile
    assert (
        "from app.observability.logging import configure_logging, log_event"
        in observability_init
    )
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
    assert "CallerContext" in security_caller_context
    assert "CapabilityPolicy" in security_caller_context
    assert "PermissionDeniedError" in security_caller_context
    assert "permission_denied_response" in security_caller_context
    assert "permission_denied" in security_caller_context
    assert "raw entitlement" in security_tests
    assert "portfolio:write" in security_tests
    assert "DownstreamClientConfig" in downstream_client
    assert "build_trace_headers" in downstream_client
    assert "upstream_timeout" in downstream_client
    assert "upstream_rejected_request" in downstream_client
    assert "upstream_unavailable" in downstream_client
    assert "upstream_malformed_response" in downstream_client
    assert "test_invalid_base_url_is_rejected" in downstream_client_tests
    assert "test_timeout_maps_to_safe_upstream_error" in downstream_client_tests
    assert "test_malformed_response_maps_to_safe_error" in downstream_client_tests
    assert "IdempotencyDecision" in idempotency_model
    assert "IdempotencyPolicy" in idempotency_model
    assert "AuditEvent" in audit_model
    assert "FORBIDDEN_ATTRIBUTE_KEYS" in audit_model
    assert (
        "test_same_key_same_payload_replays_existing_record" in idempotency_audit_tests
    )
    assert "test_same_key_different_payload_conflicts" in idempotency_audit_tests
    assert "test_audit_event_rejects_sensitive_attributes" in idempotency_audit_tests
    assert "Allowed status vocabulary" in demo_claims
    assert "`Implemented`" in demo_claims
    assert "`Partially implemented`" in demo_claims
    assert "`Planned`" in demo_claims
    assert "`Not applicable`" in demo_claims
    assert "`Unknown - requires owner review`" in demo_claims
    assert "Service-specific business workflow | `Planned`" in demo_claims
    assert "Mesh certification | `Planned`" in demo_claims
    assert "\x07" not in demo_claims
    assert "Status: Planned" in durability_standard
    assert "not implemented by the scaffold" in durability_standard
    assert "missing summary" in openapi_gate
    assert "missing success response example" in openapi_gate
    assert "FORBIDDEN_PATTERNS" in sensitive_content_guard
    assert "request_body" in sensitive_content_guard
    assert "response_body" in sensitive_content_guard
    assert "Supported-features gate passed" in supported_features_gate
    assert "implemented feature missing promotion_evidence" in supported_features_gate
    assert "Endpoint certification gate passed" in endpoint_certification_gate
    assert "missing endpoint certification ledger entry" in endpoint_certification_gate
    assert "stale endpoint certification ledger entry" in endpoint_certification_gate
    assert "Endpoint certification gate passed" in endpoint_gate.stdout
    assert (
        "WARNING: quality/architecture_boundary_report.json is missing"
        in missing_architecture_quality_baseline.stdout
    )
    assert (
        missing_architecture_quality_report["architecture_boundary_report_exists"]
        is False
    )
    assert (
        missing_architecture_quality_report["architecture_boundary_report_status"]
        == "missing"
    )
    assert "Architecture boundary report passed" in architecture_gate.stdout
    assert "Wrote" in quality_baseline.stdout
    assert "passed" in quality_baseline_markdown
    assert "passed" in quality_baseline_report["architecture_boundary_report_status"]
    assert quality_baseline_report["architecture_boundary_report_exists"] is True
    assert architecture_failure.returncode == 1
    assert "fastapi" in architecture_failure.stdout
    assert "Domain must stay framework-free" in architecture_boundary_gate
    assert "mode" in quality_baseline_script
    assert architecture_boundary_report["repository"] == service_name
    assert architecture_boundary_report["mode"] == "blocking"
    assert architecture_boundary_report["status"] == "failed"
    assert architecture_boundary_report["violations"][0]["import"] == "fastapi"
    assert quality_baseline_report["repository"] == service_name
    assert quality_baseline_report["mode"] == "report-only"
    assert quality_baseline_report["service_profile"] == "domain-service"
    assert quality_baseline_report["python_files"] > 0
    assert "Service profile: `domain-service`" in quality_baseline_markdown
    assert supported_features == {
        "repository": service_name,
        "features": [],
        "policy": "Only implementation-backed behavior may be promoted to supported.",
    }
    assert endpoint_certification["repository"] == service_name
    assert (
        endpoint_certification["policy"]
        == "Every public OpenAPI operation requires certification evidence before promotion."
    )
    assert {
        (endpoint["method"], endpoint["path"])
        for endpoint in endpoint_certification["endpoints"]
    } == {
        ("GET", "/health"),
        ("GET", "/health/live"),
        ("GET", "/health/ready"),
        ("GET", "/metadata"),
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
    assert evidence_manifest_template["upstream_realization"] == []
    assert evidence_manifest_template["source_contract_realization"] == []
    assert evidence_manifest_template["downstream_realization"] == []
    assert "structured JSON application events" in observability_doc
    assert "must not include client names" in observability_doc
    assert "clear what/when/how description" in api_certification_doc
    assert "product-safe error examples" in api_certification_doc
    assert "endpoint-certification-ledger.json" in api_certification_doc
    assert "Source-Degraded And Reconciliation Endpoints" in api_certification_doc
    assert "explicit source-owner fields" in api_certification_doc
    assert (
        "source-contract and downstream consumer realization evidence"
        in api_certification_doc
    )
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
    assert "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md" in readme
    assert "Service profile: `domain-service`" in readme
    assert "make architecture-boundary-report" in readme
    assert "make quality-baseline" in readme
    assert "Quality scorecard and refactor decisions: quality/" in readme
    assert "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md" in repo_context
    assert "Service profile: `domain-service`" in repo_context
    assert "`src/app/domain/`: framework-free domain models" in repo_context
    assert "quality scorecard under `quality/`" in repo_context
    assert "bank-buyable quality scorecard starts under quality/" in wiki_home
    assert "Service profile: `domain-service`" in wiki_home
    assert "demo claims must stay Planned" in wiki_home
    assert "Bank-Buyable Quality Scorecard" in quality_scorecard
    assert "Repository: lotus-hygiene-demo" in quality_scorecard
    assert "Service profile: domain-service" in quality_scorecard
    assert "Control Area" in quality_scorecard
    assert "Architecture" in quality_scorecard
    assert (
        "Layered package skeleton plus report-only architecture-boundary report"
        in quality_scorecard
    )
    assert "Security and privacy" in quality_scorecard
    assert "Observability and supportability" in quality_scorecard
    assert "`src/app/api` routers/controllers stay thin" in architecture_rules
    assert (
        "Run `make architecture-boundary-report` for report-only evidence"
        in architecture_rules
    )
    assert (
        "Promote stricter gates only after the signal is measured" in ci_quality_gates
    )
    assert "make quality-baseline" in ci_quality_gates
    assert "Do not use this file for aspirational claims." in refactor_decisions


def test_scaffold_service_profiles_and_invalid_profile(tmp_path: Path) -> None:
    destination_root = tmp_path / "profiles"
    destination_root.mkdir()
    profiles = {
        "domain-service": ("lotus-profile-domain", True),
        "experience-api": ("lotus-profile-experience", False),
        "shared-capability-service": ("lotus-profile-shared", False),
        "client-facing-service": ("lotus-profile-client", True),
    }

    for profile, (service_name, write_capable) in profiles.items():
        _run_scaffold(
            destination_root=destination_root,
            service_name=service_name,
            service_profile=profile,
        )
        repo_root = destination_root / service_name
        readme = (repo_root / "README.md").read_text(encoding="utf-8")
        repo_context = (repo_root / "REPOSITORY-ENGINEERING-CONTEXT.md").read_text(
            encoding="utf-8"
        )
        wiki_home = (repo_root / "wiki/Home.md").read_text(encoding="utf-8")
        domain_profile = (repo_root / "src/app/domain/service_profile.py").read_text(
            encoding="utf-8"
        )

        assert f"Service profile: `{profile}`" in readme
        assert f"Service profile: `{profile}`" in repo_context
        assert f"Service profile: `{profile}`" in wiki_home
        assert f'name="{profile}"' in domain_profile
        assert not (repo_root / "contracts/domain-data-products").exists()

        idempotency_path = repo_root / "src/app/domain/idempotency.py"
        audit_path = repo_root / "src/app/domain/audit.py"
        idempotency_test_path = repo_root / "tests/unit/test_idempotency_audit.py"
        assert idempotency_path.exists() is write_capable
        assert audit_path.exists() is write_capable
        assert idempotency_test_path.exists() is write_capable

    invalid_result = _run_scaffold(
        destination_root=destination_root,
        service_name="lotus-profile-invalid",
        service_profile="unsupported-profile",
        check=False,
    )
    invalid_output = invalid_result.stdout + invalid_result.stderr
    assert invalid_result.returncode != 0
    assert "ServiceProfile must be one of:" in invalid_output
    assert "domain-service" in invalid_output
    assert "experience-api" in invalid_output
    assert "shared-capability-service" in invalid_output
    assert "client-facing-service" in invalid_output


def test_scaffold_mesh_placeholders_are_opt_in(tmp_path: Path) -> None:
    destination_root = tmp_path / "mesh"
    destination_root.mkdir()
    default_service = "lotus-mesh-default"
    mesh_service = "lotus-mesh-opt-in"

    _run_scaffold(destination_root=destination_root, service_name=default_service)
    default_repo = destination_root / default_service
    assert not (default_repo / "contracts/domain-data-products").exists()
    assert not (default_repo / "contracts/trust-telemetry").exists()
    assert not (default_repo / "contracts/mesh-slo").exists()
    assert not (default_repo / "docs/operations/mesh-placeholder.md").exists()

    _run_scaffold(
        destination_root=destination_root,
        service_name=mesh_service,
        include_mesh_placeholders=True,
    )
    mesh_repo = destination_root / mesh_service
    placeholder_paths = [
        mesh_repo / "contracts/domain-data-products/producer-consumer-placeholder.json",
        mesh_repo / "contracts/trust-telemetry/trust-telemetry-placeholder.json",
        mesh_repo / "contracts/mesh-slo/slo-policy-placeholder.json",
        mesh_repo / "contracts/mesh-access/access-policy-placeholder.json",
        mesh_repo / "contracts/mesh-evidence/evidence-policy-placeholder.json",
        mesh_repo / "docs/operations/mesh-placeholder.md",
    ]
    for placeholder_path in placeholder_paths:
        assert placeholder_path.exists()
        content = placeholder_path.read_text(encoding="utf-8")
        assert "Planned" in content
        assert "not_certified" in content or "not certified" in content
