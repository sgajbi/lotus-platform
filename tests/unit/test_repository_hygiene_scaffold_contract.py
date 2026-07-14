from __future__ import annotations

import importlib.util
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


def _load_generated_ci_contract_gate(repo_root: Path):
    script_path = repo_root / "scripts" / "ci_contract_gate.py"
    spec = importlib.util.spec_from_file_location(
        "generated_ci_contract_gate", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _assert_api_contract_governance(
    repo_root: Path,
    endpoint_certification: dict[str, object],
    endpoint_gate_output: str,
) -> None:
    main_py = (repo_root / "src/app/main.py").read_text(encoding="utf-8")
    baseline_responses = (repo_root / "src/app/api/baseline_responses.py").read_text(
        encoding="utf-8"
    )
    endpoint_certification_gate = (
        repo_root / "scripts/endpoint_certification_gate.py"
    ).read_text(encoding="utf-8")
    openapi_gate = (repo_root / "scripts/openapi_quality_gate.py").read_text(
        encoding="utf-8"
    )
    supported_features_gate = (
        repo_root / "scripts/supported_features_gate.py"
    ).read_text(encoding="utf-8")
    endpoint_example_parity = (
        repo_root / "scripts/endpoint_example_parity.py"
    ).read_text(encoding="utf-8")
    route_instrumentation_contract = (
        repo_root / "tests/unit/test_route_instrumentation_contract.py"
    ).read_text(encoding="utf-8")

    assert "from app.api.baseline_responses import" in main_py
    assert "return health_response()" in main_py
    assert "def health_response" in baseline_responses
    assert "def metadata_response" in baseline_responses
    assert "include_in_schema=False" in main_py
    assert main_py.index('@app.get(\n    "/metadata"') < main_py.index(
        "Instrumentator().instrument(app).expose(app, include_in_schema=False)"
    )
    assert (
        "Register all baseline and service-specific business routes before Prometheus"
        in main_py
    )
    assert "do not append APIRouter objects directly" in main_py
    assert "register_example_business_routes(app)" in route_instrumentation_contract
    assert "Instrumentator().instrument(app).expose(app, include_in_schema=False)" in (
        route_instrumentation_contract
    )
    assert '"/business/example" in route_paths' in route_instrumentation_contract
    assert "APIRouter" in route_instrumentation_contract
    assert 'tags=["Health"]' in main_py
    assert 'summary="Get service health"' in main_py
    assert 'summary="Get readiness"' in main_py
    assert 'tags=["Metadata"]' in main_py
    assert "validation_exception_handler" in main_py
    assert "unhandled_exception_handler" in main_py
    assert "emit_request_diagnostic_event" in main_py
    assert "_route_template(request)" in main_py
    assert "path=str(request.url.path)" not in main_py
    assert "Request validation failed. Correct the request fields and retry." in main_py
    assert "missing summary" in openapi_gate
    assert "missing success response example" in openapi_gate
    assert "Supported-features gate passed" in supported_features_gate
    assert "implemented feature missing promotion_evidence" in supported_features_gate
    assert "Endpoint certification gate passed" in endpoint_certification_gate
    assert "missing endpoint certification ledger entry" in endpoint_certification_gate
    assert "stale endpoint certification ledger entry" in endpoint_certification_gate
    assert "OPERATION_EVENT_TEST_TERMS" in endpoint_certification_gate
    assert (
        "certified endpoint must reference bounded operation-event test evidence"
        in endpoint_certification_gate
    )
    assert "compare_endpoint_examples" in endpoint_certification_gate
    assert "PARITY_REQUIRED_STATUSES" in endpoint_certification_gate
    assert "def compare_endpoint_examples" in endpoint_example_parity
    assert "Endpoint certification gate passed" in endpoint_gate_output
    endpoints = endpoint_certification["endpoints"]
    assert isinstance(endpoints, list)
    assert all(endpoint["response_example_parity"]["cases"] for endpoint in endpoints)
    assert all(
        case["source"] == "deterministic_no_io_example_factory"
        and case["callable"].startswith("app.api.baseline_responses:")
        for endpoint in endpoints
        for case in endpoint["response_example_parity"]["cases"]
    )

    endpoint_ledger_path = (
        repo_root / "docs/operations/endpoint-certification-ledger.json"
    )
    original_endpoint_ledger = endpoint_ledger_path.read_text(encoding="utf-8")
    stale_endpoint_ledger = json.loads(original_endpoint_ledger)
    stale_endpoint_ledger["endpoints"][0]["response_examples"] = [
        '{"status":"legacy","service":"lotus-hygiene-demo"}'
    ]
    endpoint_ledger_path.write_text(
        json.dumps(stale_endpoint_ledger, indent=2) + "\n",
        encoding="utf-8",
    )
    stale_endpoint_gate = subprocess.run(
        [sys.executable, "scripts/endpoint_certification_gate.py"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    endpoint_ledger_path.write_text(original_endpoint_ledger, encoding="utf-8")
    assert stale_endpoint_gate.returncode == 1
    assert "value_mismatch" in stale_endpoint_gate.stdout


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
    platform_checks_script = (
        ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1"
    ).read_text(encoding="utf-8")
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
    main_releasability_template = (
        ROOT
        / "platform-standards"
        / "templates"
        / "workflows"
        / "main-releasability.backend.template.yml"
    ).read_text(encoding="utf-8")
    merged_pr_dispatch_template = (
        ROOT
        / "platform-standards"
        / "templates"
        / "workflows"
        / "merged-pr-main-releasability.template.yml"
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
    assert "PIP_ROOT_USER_ACTION=ignore" in scaffold_script
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
    assert "tests/unit/test_no_sensitive_content_guard.py" in scaffold_script
    assert "scripts/source_observability_contract_gate.py" in scaffold_script
    assert "scripts/operation_metric_contract_gate.py" in scaffold_script
    assert "scripts/ci_contract_gate.py" in scaffold_script
    assert "scripts/clean_generated_artifacts.py" in scaffold_script
    assert "tests/unit/test_clean_generated_artifacts.py" in scaffold_script
    assert "scripts/documentation_contract_gate.py" in scaffold_script
    assert "merged-pr-main-releasability.template.yml" in scaffold_script
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
    assert (
        "retry, backoff, timeout, and circuit-breaker policy primitives"
        in scaffold_script
    )
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
    assert "function Invoke-CheckedCommand" in platform_checks_script
    assert "$LASTEXITCODE -ne 0" in platform_checks_script
    assert "Command failed with exit code" in platform_checks_script
    assert (
        'require_response_headers = @("x-correlation-id", "x-trace-id")'
        in scaffold_script
    )
    assert (
        '[string[]]$RequiredLogPatterns = @("correlation", "trace", "service")'
        in scaffold_script
    )
    assert 'response.headers["X-Trace-Id"] = trace_id' in scaffold_script
    assert "OPERATION_METRIC_LABELS" in scaffold_script
    assert "FORBIDDEN_OPERATION_FIELD_KEYS" in scaffold_script
    assert "emit_operation_event" in scaffold_script
    assert "monetary-float-guard:" in makefile_template
    assert "$(MAKE) monetary-float-guard" in makefile_template
    assert "ci-contract-gate:" in makefile_template
    assert "$(MAKE) ci-contract-gate" in makefile_template
    assert "maintainability-gate:" in makefile_template
    assert "$(MAKE) maintainability-gate" in makefile_template
    assert "scripts/maintainability_gate.py" in scaffold_script
    assert "documentation-contract-gate:" in makefile_template
    assert "$(MAKE) documentation-contract-gate" in makefile_template
    assert "scripts/documentation_contract_gate.py" in scaffold_script
    assert "quality-scorecard-gate:" in makefile_template
    assert "$(MAKE) quality-scorecard-gate" in makefile_template
    assert "scripts/quality_scorecard_gate.py" in scaffold_script
    assert "no-sensitive-content-guard:" in makefile_template
    assert "$(MAKE) no-sensitive-content-guard" in makefile_template
    assert "source-observability-contract-gate:" in makefile_template
    assert "$(MAKE) source-observability-contract-gate" in makefile_template
    assert "operation-metric-contract-gate:" in makefile_template
    assert "$(MAKE) operation-metric-contract-gate" in makefile_template
    assert "implementation-truth-gate:" in makefile_template
    assert "$(MAKE) implementation-truth-gate" in makefile_template
    assert "supported-features-gate:" in makefile_template
    assert "$(MAKE) supported-features-gate" in makefile_template
    assert "endpoint-certification-gate:" in makefile_template
    assert "$(MAKE) endpoint-certification-gate" in makefile_template
    assert "architecture-boundary-gate:" in makefile_template
    assert "scripts/architecture_boundary_gate.py --mode blocking" in makefile_template
    assert "architecture-boundary-report:" in makefile_template
    assert (
        "scripts/architecture_boundary_gate.py --mode report-only" in makefile_template
    )
    assert "quality-baseline: architecture-boundary-report" in makefile_template
    assert "scripts/generate_quality_baseline.py" in makefile_template
    assert "coverage-gate:" in makefile_template
    assert "$(VENV_PYTHON) scripts/coverage_gate.py" in makefile_template
    assert "UNIT_TESTS ?= tests/unit" in makefile_template
    assert "INTEGRATION_TESTS ?= tests/integration" in makefile_template
    assert "E2E_TESTS ?= tests/e2e" in makefile_template
    assert "$(VENV_PYTHON) -m pytest $(UNIT_TESTS)" in makefile_template
    assert "$(VENV_PYTHON) -m pytest $(INTEGRATION_TESTS)" in makefile_template
    assert "$(VENV_PYTHON) -m pytest $(E2E_TESTS)" in makefile_template
    assert "test-unit-coverage:" in makefile_template
    assert "test-integration-coverage:" in makefile_template
    assert "test-e2e-coverage:" in makefile_template
    assert (
        "$(VENV_PYTHON) -m pytest $(UNIT_TESTS) --cov=src --cov-report="
        in makefile_template
    )
    assert "REQUIRED_TEST_SELECTORS" in scaffold_script
    assert '"test-unit": "$(VENV_PYTHON) -m pytest $(UNIT_TESTS)"' in scaffold_script
    assert "expected_command not in _target_block(makefile, target)" in scaffold_script
    assert (
        'for target in ("test-unit-coverage", "test-integration-coverage", "test-e2e-coverage")'
        in scaffold_script
    )
    assert "Makefile test-coverage target must depend on" in scaffold_script
    assert "clean:" in makefile_template
    assert "python scripts/clean_generated_artifacts.py" in makefile_template
    for workflow_template in (
        feature_lane_template,
        pr_merge_template,
        main_releasability_template,
    ):
        assert "Architecture Boundary Gate" in workflow_template
        assert "make architecture-boundary-gate" in workflow_template
        assert "timeout-minutes:" in workflow_template
    assert (
        "$(VENV_PYTHON) -m pip_audit -r requirements/shared-runtime.lock.txt -r requirements/ci-tooling.lock.txt"
        in makefile_template
    )
    assert "run: make test-unit" in feature_lane_template
    assert "run: ./.venv/bin/python -m pytest tests/unit" not in feature_lane_template
    assert "gh workflow run main-releasability.yml" in merged_pr_dispatch_template
    assert "--ref main" in merged_pr_dispatch_template
    assert "github.event.pull_request.merged == true" in merged_pr_dispatch_template
    assert "timeout-minutes: 10" in merged_pr_dispatch_template
    assert "suite: [unit, integration, e2e]" in pr_merge_template
    assert "run: make test-${{ matrix.suite }}-coverage" in pr_merge_template
    assert "matrix.path" not in pr_merge_template
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
    ci_contract_gate_result = subprocess.run(
        [sys.executable, "scripts/ci_contract_gate.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    maintainability_gate_result = subprocess.run(
        [sys.executable, "scripts/maintainability_gate.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    documentation_contract_gate_result = subprocess.run(
        [sys.executable, "scripts/documentation_contract_gate.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    quality_scorecard_gate_result = subprocess.run(
        [sys.executable, "scripts/quality_scorecard_gate.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    monetary_float_guard_result = subprocess.run(
        [sys.executable, "scripts/check_monetary_float_usage.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    source_observability_gate_result = subprocess.run(
        [sys.executable, "scripts/source_observability_contract_gate.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    operation_metric_gate_result = subprocess.run(
        [sys.executable, "scripts/operation_metric_contract_gate.py"],
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
    assert not (repo_root / "quality/architecture_boundary_report.json").exists()
    architecture_report = subprocess.run(
        [
            sys.executable,
            "scripts/architecture_boundary_gate.py",
            "--mode",
            "report-only",
        ],
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
    clean_architecture_boundary_report = json.loads(
        (repo_root / "quality/architecture_boundary_report.json").read_text(
            encoding="utf-8"
        )
    )
    architecture_failure_report = subprocess.run(
        [
            sys.executable,
            "scripts/architecture_boundary_gate.py",
            "--mode",
            "report-only",
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    bad_boundary.unlink()
    bad_runtime_boundary = repo_root / "src/app/runtime/bad_runtime_boundary.py"
    bad_runtime_boundary.write_text(
        "from app.api import health\n",
        encoding="utf-8",
    )
    runtime_architecture_failure = subprocess.run(
        [sys.executable, "scripts/architecture_boundary_gate.py", "--mode", "blocking"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    bad_runtime_boundary.unlink()
    bad_observability = repo_root / "src/app/api/raw_logging.py"
    bad_observability.write_text(
        "def leak() -> None:\n    print('raw request')\n",
        encoding="utf-8",
    )
    source_observability_failure = subprocess.run(
        [sys.executable, "scripts/source_observability_contract_gate.py"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    bad_observability.unlink()
    generated_cache = repo_root / "htmlcov"
    generated_cache.mkdir(parents=True, exist_ok=True)
    (generated_cache / "index.html").write_text("coverage", encoding="utf-8")
    local_coverage_artifact = repo_root / "coverage.xml"
    local_coverage_artifact.write_text("<coverage />", encoding="utf-8")
    venv_cache = repo_root / ".venv" / "Lib" / "__pycache__"
    venv_cache.mkdir(parents=True)
    venv_marker = venv_cache / "dependency.cpython-313.pyc"
    venv_marker.write_bytes(b"dependency bytecode")
    cleanup_result = subprocess.run(
        [sys.executable, "scripts/clean_generated_artifacts.py"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    bad_money = repo_root / "src/app/domain/bad_money.py"
    bad_money.write_text(
        "market_value: float = 1\n"
        "cash_balance = 100.25\n"
        "def parse_price(raw: str) -> object:\n"
        "    return float(raw)\n"
        "def notional_value() -> float:\n"
        "    return 1\n",
        encoding="utf-8",
    )
    monetary_float_failure = subprocess.run(
        [sys.executable, "scripts/check_monetary_float_usage.py"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    bad_money.unlink()
    subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "src", "tests"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    result = json.loads(output_json.read_text(encoding="utf-8"))
    makefile = (repo_root / "Makefile").read_text(encoding="utf-8")
    dockerfile = (repo_root / "Dockerfile").read_text(encoding="utf-8")
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
    sensitive_content_guard = (
        repo_root / "scripts/no_sensitive_content_guard.py"
    ).read_text(encoding="utf-8")
    sensitive_content_guard_tests = (
        repo_root / "tests/unit/test_no_sensitive_content_guard.py"
    ).read_text(encoding="utf-8")
    monetary_float_guard = (
        repo_root / "scripts/check_monetary_float_usage.py"
    ).read_text(encoding="utf-8")
    source_observability_contract_gate = (
        repo_root / "scripts/source_observability_contract_gate.py"
    ).read_text(encoding="utf-8")
    clean_generated_artifacts = (
        repo_root / "scripts/clean_generated_artifacts.py"
    ).read_text(encoding="utf-8")
    implementation_truth_gate = (
        repo_root / "scripts/implementation_truth_gate.py"
    ).read_text(encoding="utf-8")
    documentation_contract_gate = (
        repo_root / "scripts/documentation_contract_gate.py"
    ).read_text(encoding="utf-8")
    quality_scorecard_gate = (
        repo_root / "scripts/quality_scorecard_gate.py"
    ).read_text(encoding="utf-8")
    ci_contract_gate = (repo_root / "scripts/ci_contract_gate.py").read_text(
        encoding="utf-8"
    )
    merged_pr_dispatch_workflow = (
        repo_root / ".github/workflows/merged-pr-main-releasability.yml"
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
    wiki_pages = {path.name for path in (repo_root / "wiki").glob("*.md")}
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
    assert "ENV PIP_ROOT_USER_ACTION=ignore" in dockerfile
    assert "monetary-float-guard:" in makefile
    assert "$(MAKE) monetary-float-guard" in makefile
    assert "ci-contract-gate:" in makefile
    assert "$(MAKE) ci-contract-gate" in makefile
    assert "maintainability-gate:" in makefile
    assert "$(MAKE) maintainability-gate" in makefile
    assert (repo_root / "scripts/maintainability_gate.py").exists()
    assert "documentation-contract-gate:" in makefile
    assert "$(MAKE) documentation-contract-gate" in makefile
    assert (repo_root / "scripts/documentation_contract_gate.py").exists()
    assert "quality-scorecard-gate:" in makefile
    assert "$(MAKE) quality-scorecard-gate" in makefile
    assert (repo_root / "scripts/quality_scorecard_gate.py").exists()
    assert "no-sensitive-content-guard:" in makefile
    assert "$(MAKE) no-sensitive-content-guard" in makefile
    assert "validate_no_sensitive_content" in sensitive_content_guard
    assert "test_no_sensitive_content_guard_blocks_sensitive_artifact_markers" in (
        sensitive_content_guard_tests
    )
    assert "test_no_sensitive_content_guard_honors_absolute_allowlist" in (
        sensitive_content_guard_tests
    )
    assert "source-observability-contract-gate:" in makefile
    assert "$(MAKE) source-observability-contract-gate" in makefile
    assert (repo_root / "scripts/source_observability_contract_gate.py").exists()
    assert "operation-metric-contract-gate:" in makefile
    assert "$(MAKE) operation-metric-contract-gate" in makefile
    assert (repo_root / "scripts/operation_metric_contract_gate.py").exists()
    assert "OPERATION_METRIC_LABELS" in (
        repo_root / "src/app/observability/logging.py"
    ).read_text(encoding="utf-8")
    assert "clean:" in makefile
    assert "python scripts/clean_generated_artifacts.py" in makefile
    assert (repo_root / "scripts/clean_generated_artifacts.py").exists()
    assert "implementation-truth-gate:" in makefile
    assert "$(MAKE) implementation-truth-gate" in makefile
    assert "supported-features-gate:" in makefile
    assert "$(MAKE) supported-features-gate" in makefile
    assert "endpoint-certification-gate:" in makefile
    assert "$(MAKE) endpoint-certification-gate" in makefile
    assert "architecture-boundary-gate:" in makefile
    assert "scripts/architecture_boundary_gate.py --mode blocking" in makefile
    assert "architecture-boundary-report:" in makefile
    assert "scripts/architecture_boundary_gate.py --mode report-only" in makefile
    assert "quality-baseline: architecture-boundary-report" in makefile
    assert "scripts/generate_quality_baseline.py" in makefile
    assert "check: lint typecheck architecture-boundary-gate" in makefile
    assert "ci: lint typecheck architecture-boundary-gate" in makefile
    assert "coverage-gate:" in makefile
    assert "$(VENV_PYTHON) scripts/coverage_gate.py" in makefile
    assert (repo_root / "src/app/api/__init__.py").exists()
    assert (repo_root / "src/app/application/__init__.py").exists()
    assert (repo_root / "src/app/domain/__init__.py").exists()
    assert (repo_root / "src/app/ports/__init__.py").exists()
    assert (repo_root / "src/app/infrastructure/__init__.py").exists()
    assert (repo_root / "src/app/runtime/__init__.py").exists()
    assert (repo_root / "src/app/observability/__init__.py").exists()
    assert (repo_root / "src/app/security/__init__.py").exists()
    assert (repo_root / "src/app/resilience/__init__.py").exists()
    assert not (repo_root / "contracts/domain-data-products").exists()
    assert not (repo_root / "contracts/trust-telemetry").exists()
    assert "Expected dependency flow" in app_readme
    assert "`runtime` owns process-local composition" in app_readme
    assert "`resilience` provides retry, backoff, timeout" in app_readme
    assert 'name="domain-service"' in domain_profile
    assert "Domain-authoritative backend service" in domain_profile
    assert "current_service_profile" in application_profile
    assert "configure_logging" in observability_init
    assert "emit_request_diagnostic_event" in observability_init
    assert "emit_operation_event" in observability_init
    assert "ProblemDetails" in errors_py
    assert "Product-safe remediation guidance" in errors_py
    assert "json.dumps(payload, sort_keys=True, default=str)" in observability_py
    assert '"event": event_name' in observability_py
    assert "REQUEST_DIAGNOSTIC_EVENTS" in observability_py
    assert "route must be a route template without query string" in observability_py
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
    assert "Scaffold creation provides only health, readiness, metadata" in demo_claims
    assert "No business workflow is implemented by the scaffold" not in demo_claims
    assert "Architecture and maintainability enforcement | `Implemented`" in demo_claims
    assert "Keep broad quality metrics report-only" not in demo_claims
    assert "Mesh certification | `Planned`" in demo_claims
    assert "\x07" not in demo_claims
    assert "STALE_SCAFFOLD_PATTERNS" in implementation_truth_gate
    assert "stale scaffold current-state" in implementation_truth_gate
    assert "Status: Planned" in durability_standard
    assert "not implemented by the scaffold" in durability_standard
    assert "FORBIDDEN_PATTERNS" in sensitive_content_guard
    assert "request_body" in sensitive_content_guard
    assert "response_body" in sensitive_content_guard
    assert "validate_monetary_float_usage" in monetary_float_guard
    assert "monetary float annotation detected" in monetary_float_guard
    assert "monetary float return annotation detected" in monetary_float_guard
    assert "ALLOWED_LOGGING_MODULES" in source_observability_contract_gate
    assert "print() is prohibited in application " in source_observability_contract_gate
    assert (
        "source; use bounded structured logging" in source_observability_contract_gate
    )
    assert "low-level log_event" in source_observability_contract_gate
    assert "def build_cleanup_plan" in clean_generated_artifacts
    assert "def clean_generated_artifacts" in clean_generated_artifacts
    assert "PRUNED_DIR_NAMES" in clean_generated_artifacts
    assert '"node_modules"' in clean_generated_artifacts
    _assert_api_contract_governance(
        repo_root,
        endpoint_certification,
        endpoint_gate.stdout,
    )
    assert "CI contract gate passed" in ci_contract_gate_result.stdout
    assert "Maintainability gate passed" in maintainability_gate_result.stdout
    assert (
        "Documentation contract gate passed"
        in documentation_contract_gate_result.stdout
    )
    assert "Quality scorecard gate passed" in quality_scorecard_gate_result.stdout
    assert "Monetary float guard passed" in monetary_float_guard_result.stdout
    assert (
        "Source observability contract gate passed"
        in source_observability_gate_result.stdout
    )
    assert (
        "Operation metric contract gate passed" in operation_metric_gate_result.stdout
    )
    assert "Removed " in cleanup_result.stdout
    assert "generated directories" in cleanup_result.stdout
    assert not generated_cache.exists()
    assert not local_coverage_artifact.exists()
    assert venv_marker.exists()
    assert "monetary float annotation detected" in monetary_float_failure.stdout
    assert "monetary float literal detected" in monetary_float_failure.stdout
    assert "monetary float conversion detected" in monetary_float_failure.stdout
    assert "monetary float return annotation detected" in monetary_float_failure.stdout
    assert (
        "print() is prohibited in application source"
        in source_observability_failure.stdout
    )
    assert "WORKFLOW_EXPECTATIONS" in ci_contract_gate
    assert "documentation-contract-gate" in ci_contract_gate
    assert "quality-scorecard-gate" in ci_contract_gate
    assert "source-observability-contract-gate" in ci_contract_gate
    assert "operation-metric-contract-gate" in ci_contract_gate
    assert "clean_generated_artifacts.py" in ci_contract_gate
    assert "Makefile clean target must call" in ci_contract_gate
    assert "coverage report --fail-under=99" in ci_contract_gate
    assert "secrets.LOTUS_AUTOMERGE_TOKEN" in ci_contract_gate
    assert "LOTUS_AUTOMERGE_TOKEN is required" in ci_contract_gate
    assert (
        "Skipping auto-merge; use an authorized human or release actor"
        in ci_contract_gate
    )
    assert "merged-pr-main-releasability.yml" in ci_contract_gate
    assert "gh workflow run main-releasability.yml" in ci_contract_gate
    assert "workflow_dispatch:" in ci_contract_gate
    assert "_validate_job_timeouts" in ci_contract_gate
    assert "continue-on-error:" in ci_contract_gate
    assert '"test-unit-coverage"' in ci_contract_gate
    assert '"make test-${{ matrix.suite }}-coverage"' in ci_contract_gate
    assert '"run: ./.venv/bin/python -m pytest"' in ci_contract_gate
    assert "must define at least one parseable job" in ci_contract_gate
    generated_ci_contract_gate = _load_generated_ci_contract_gate(repo_root)
    weakened_makefile_errors = generated_ci_contract_gate.validate_makefile(
        makefile.replace(
            "python scripts/clean_generated_artifacts.py",
            'python -c "pass"',
        )
    )
    assert (
        "Makefile clean target must call `python scripts/clean_generated_artifacts.py`"
        in weakened_makefile_errors
    )
    mutated_workflow_dir = tmp_path / "mutated-generated-workflows"
    shutil.copytree(repo_root / ".github" / "workflows", mutated_workflow_dir)
    feature_lane = mutated_workflow_dir / "feature-lane.yml"
    original_feature_lane = feature_lane.read_text(encoding="utf-8")
    feature_lane.write_text(
        original_feature_lane.replace("jobs:", "jobs: # generated lanes", 1).replace(
            "    timeout-minutes: 10\n", "", 1
        ),
        encoding="utf-8",
    )
    timeout_errors = generated_ci_contract_gate.validate_workflows(mutated_workflow_dir)
    assert (
        "feature-lane.yml job `workflow-lint` missing timeout-minutes" in timeout_errors
    )
    feature_lane.write_text(
        original_feature_lane.replace(
            "    timeout-minutes: 10\n",
            "    timeout-minutes: 10\n    continue-on-error: ${{ true }}\n",
            1,
        ),
        encoding="utf-8",
    )
    soft_fail_errors = generated_ci_contract_gate.validate_workflows(
        mutated_workflow_dir
    )
    assert "feature-lane.yml must not contain `continue-on-error:`" in soft_fail_errors
    feature_lane.write_text(
        original_feature_lane.replace(
            "run: make test-unit",
            "run: ./.venv/bin/python -m pytest tests/unit",
        ),
        encoding="utf-8",
    )
    raw_pytest_errors = generated_ci_contract_gate.validate_workflows(
        mutated_workflow_dir
    )
    assert (
        "feature-lane.yml must not contain `run: ./.venv/bin/python -m pytest`"
        in raw_pytest_errors
    )
    assert "Merged PR Main Releasability Dispatch" in merged_pr_dispatch_workflow
    assert "gh workflow run main-releasability.yml" in merged_pr_dispatch_workflow
    assert "--ref main" in merged_pr_dispatch_workflow
    assert "timeout-minutes: 10" in merged_pr_dispatch_workflow
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
    assert "Architecture boundary gate passed" in architecture_gate.stdout
    assert "Architecture boundary report passed" in architecture_report.stdout
    assert "Wrote" in quality_baseline.stdout
    assert "passed" in quality_baseline_markdown
    assert "passed" in quality_baseline_report["architecture_boundary_report_status"]
    assert quality_baseline_report["architecture_boundary_report_exists"] is True
    assert architecture_failure.returncode == 1
    assert (
        "Architecture boundary gate found 1 violation(s)."
        in architecture_failure.stdout
    )
    assert "fastapi" in architecture_failure.stdout
    assert clean_architecture_boundary_report["mode"] == "report-only"
    assert clean_architecture_boundary_report["status"] == "passed"
    assert (
        "Architecture boundary report found 1 violation(s)."
        in architecture_failure_report.stdout
    )
    assert "Domain must stay framework-free" in architecture_boundary_gate
    assert '"runtime": {' in architecture_boundary_gate
    assert (
        '"forbidden_prefixes": ("fastapi", "starlette", "app.api")'
        in architecture_boundary_gate
    )
    assert runtime_architecture_failure.returncode == 1
    assert "Architecture boundary gate found 1 violation(s)." in (
        runtime_architecture_failure.stdout
    )
    assert "app.runtime.bad_runtime_boundary" in runtime_architecture_failure.stdout
    assert "app.api" in runtime_architecture_failure.stdout
    assert "mode" in quality_baseline_script
    assert architecture_boundary_report["repository"] == service_name
    assert architecture_boundary_report["mode"] == "report-only"
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
    assert "make ci-contract-gate" in readme
    assert "make maintainability-gate" in readme
    assert "make documentation-contract-gate" in readme
    assert "make quality-scorecard-gate" in readme
    assert "make source-observability-contract-gate" in readme
    assert "make operation-metric-contract-gate" in readme
    assert "make implementation-truth-gate" in readme
    assert "Quality scorecard and refactor decisions: quality/" in readme
    assert "Demo claims ledger: docs/demo/demo-claims.md" in readme
    assert "API certification guide: docs/operations/api-certification.md" in readme
    assert "Observability guide: docs/operations/observability.md" in readme
    assert (
        "RFC implementation evidence guide: evidence/rfc-implementation/README.md"
        in readme
    )
    assert "src/app/resilience" in readme
    assert "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md" in repo_context
    assert "Service profile: `domain-service`" in repo_context
    assert "`src/app/domain/`: framework-free domain models" in repo_context
    assert "`src/app/resilience/`: retry, backoff, timeout" in repo_context
    assert "quality scorecard under `quality/`" in repo_context
    assert "`make ci-contract-gate` is blocking through `make lint`" in repo_context
    assert "`make maintainability-gate` prevents oversized source" in repo_context
    assert "`make documentation-contract-gate` keeps README" in repo_context
    assert (
        "`make quality-scorecard-gate` keeps the bank-buyable control matrix"
        in repo_context
    )
    assert "`make source-observability-contract-gate` blocks raw print" in repo_context
    assert (
        "`make operation-metric-contract-gate` keeps operation metric vocabulary"
        in repo_context
    )
    assert "`make implementation-truth-gate` keeps current-state README" in repo_context
    assert {
        "_Sidebar.md",
        "Home.md",
        "Overview.md",
        "Architecture.md",
        "Getting-Started.md",
        "Development-Workflow.md",
        "Validation-And-CI.md",
        "Operations-Runbook.md",
        "Security-And-Governance.md",
        "Integrations.md",
        "Roadmap.md",
        "Supported-Features.md",
    }.issubset(wiki_pages)
    assert "bank-buyable quality scorecard starts under quality/" in wiki_home
    assert "Service profile: `domain-service`" in wiki_home
    assert "demo claims must stay Planned" in wiki_home
    assert "Validation And CI" in wiki_home
    assert "delete completed local and remote feature branches after merge" in (
        repo_root / "wiki/Development-Workflow.md"
    ).read_text(encoding="utf-8")
    assert "Do not downgrade current action versions" in (
        repo_root / "wiki/Validation-And-CI.md"
    ).read_text(encoding="utf-8")
    assert "make ci-contract-gate" in (
        repo_root / "wiki/Validation-And-CI.md"
    ).read_text(encoding="utf-8")
    assert "make maintainability-gate" in (
        repo_root / "wiki/Validation-And-CI.md"
    ).read_text(encoding="utf-8")
    assert "make documentation-contract-gate" in (
        repo_root / "wiki/Validation-And-CI.md"
    ).read_text(encoding="utf-8")
    assert "make quality-scorecard-gate" in (
        repo_root / "wiki/Validation-And-CI.md"
    ).read_text(encoding="utf-8")
    assert "make source-observability-contract-gate" in (
        repo_root / "wiki/Validation-And-CI.md"
    ).read_text(encoding="utf-8")
    assert "make operation-metric-contract-gate" in (
        repo_root / "wiki/Validation-And-CI.md"
    ).read_text(encoding="utf-8")
    assert "make implementation-truth-gate" in (
        repo_root / "wiki/Validation-And-CI.md"
    ).read_text(encoding="utf-8")
    assert "No business feature is supported by scaffold creation alone" in (
        repo_root / "wiki/Supported-Features.md"
    ).read_text(encoding="utf-8")
    assert "Bank-Buyable Quality Scorecard" in quality_scorecard
    assert "Repository: lotus-hygiene-demo" in quality_scorecard
    assert "Service profile: domain-service" in quality_scorecard
    assert "Control Area" in quality_scorecard
    assert "make ci-contract-gate" in ci_quality_gates
    assert "make maintainability-gate" in ci_quality_gates
    assert "make documentation-contract-gate" in ci_quality_gates
    assert "make quality-scorecard-gate" in ci_quality_gates
    assert "make source-observability-contract-gate" in ci_quality_gates
    assert "make operation-metric-contract-gate" in ci_quality_gates
    assert "make implementation-truth-gate" in ci_quality_gates
    assert "REQUIRED_SURFACES" in documentation_contract_gate
    assert "contains placeholder text" in documentation_contract_gate
    assert "REQUIRED_CONTROLS" in quality_scorecard_gate
    assert "stale scaffold-era scorecard claim" in quality_scorecard_gate
    assert "stale scaffold-era demo underclaims" in ci_quality_gates
    assert "Architecture" in quality_scorecard
    assert (
        "Layered package skeleton, blocking architecture-boundary gate, blocking maintainability thresholds"
        in quality_scorecard
    )
    assert "Security and privacy" in quality_scorecard
    assert "Observability and supportability" in quality_scorecard
    assert "source-observability contract enforcement" in quality_scorecard
    assert "`src/app/api` routers/controllers stay thin" in architecture_rules
    assert "`src/app/resilience` owns retry, backoff, timeout" in architecture_rules
    assert (
        "Run `make architecture-boundary-gate` for blocking CI enforcement"
        in architecture_rules
    )
    assert (
        "Promote stricter gates only after the signal is measured" in ci_quality_gates
    )
    assert "make architecture-boundary-gate" in ci_quality_gates
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
