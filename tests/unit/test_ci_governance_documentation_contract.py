from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_rfc_0072_foundation_artifacts_are_present_and_cross_referenced() -> None:
    rfc = (ROOT / "rfcs" / "RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md").read_text(
        encoding="utf-8"
    )
    standard = (
        ROOT
        / "docs"
        / "standards"
        / "Continuous Integration, Validation, and Release Governance Standard.md"
    ).read_text(encoding="utf-8")
    checklist = (ROOT / "rfcs" / "RFC-0072-implementation-checklist.md").read_text(encoding="utf-8")
    mapping = (ROOT / "platform-standards" / "Repository-CI-Lane-Mapping-Baseline.md").read_text(
        encoding="utf-8"
    )
    gap_audit = (ROOT / "platform-standards" / "Repository-CI-Convergence-Gap-Audit.md").read_text(
        encoding="utf-8"
    )
    template_contract = (ROOT / "platform-standards" / "Backend-CI-Lane-Template-Contract.md").read_text(
        encoding="utf-8"
    )
    hygiene_standard = (
        ROOT / "platform-standards" / "Repository-Hygiene-and-Dependency-Model-Standard.md"
    ).read_text(encoding="utf-8")
    workflow_security_standard = (
        ROOT / "platform-standards" / "Workflow-Security-and-Permissions-Standard.md"
    ).read_text(encoding="utf-8")
    workflow_action_runtime_standard = (
        ROOT / "platform-standards" / "Workflow-Action-Runtime-and-Version-Baseline.md"
    ).read_text(encoding="utf-8")
    container_build_standard = (
        ROOT / "platform-standards" / "Container-Build-and-Image-Engineering-Standard.md"
    ).read_text(encoding="utf-8")
    platform_validation_coverage_standard = (
        ROOT / "platform-standards" / "Platform-End-to-End-Validation-Coverage-Standard.md"
    ).read_text(encoding="utf-8")
    release_evidence_standard = (
        ROOT / "platform-standards" / "Release-Evidence-and-SBOM-Foundation-Standard.md"
    ).read_text(encoding="utf-8")
    scaffold_script = (ROOT / "automation" / "New-Lotus-Service.ps1").read_text(encoding="utf-8")
    auto_merge_template = (
        ROOT / "platform-standards" / "templates" / "workflows" / "pr-auto-merge.template.yml"
    ).read_text(encoding="utf-8")
    merged_pr_dispatch_template = (
        ROOT
        / "platform-standards"
        / "templates"
        / "workflows"
        / "merged-pr-main-releasability.template.yml"
    ).read_text(encoding="utf-8")

    assert "Scaffolding-by-Default Requirement" in rfc
    assert "Remote Feature Lane" in rfc
    assert "Pull Request Merge Gate" in rfc
    assert "Main Releasability Gate" in rfc
    assert "Platform End-to-End Validation Lane" in rfc

    assert "Scaffold-by-Default Policy" in standard
    assert "Skill Alignment Requirement" in standard

    assert "Slice 1 | Governance and documentation foundation | Complete" in checklist
    assert "Slice 2 | Repository workflow classification and gap audit | Complete" in checklist
    assert "Slice 3 | Standardized workflow convergence | Complete" in checklist
    assert "Slice 3B | Scaffold and template convergence | Complete" in checklist
    assert "Slice 3C | Backend rollout wave 1 (`lotus-manage`, `lotus-report`) | Complete" in checklist
    assert "Slice 3D | Experience-layer rollout wave (`lotus-gateway`, `lotus-workbench`) | Complete" in checklist
    assert "Slice 3E | Analytics-domain rollout wave (`lotus-performance`, `lotus-risk`) | Complete" in checklist
    assert "Slice 3F | Shared capability rollout wave (`lotus-ai`) | Complete" in checklist
    assert "Slice 3G | Advisory-domain rollout wave (`lotus-advise`) | Complete" in checklist
    assert "Slice 3H | Core-domain rollout wave (`lotus-core`) | Complete" in checklist
    assert "Slice 4A | Platform repo lane foundation | Complete" in checklist
    assert "Slice 4B | Platform validation lane normalization | Complete" in checklist
    assert "Slice 4C | Repository governance policy normalization | Complete" in checklist
    assert "Slice 4D | Repository governance rollout and validation | Complete" in checklist
    assert "Slice 5A | Repository hygiene and dependency-model baseline | Complete" in checklist
    assert "Slice 5B | Workflow security and permissions baseline | Complete" in checklist
    assert "Slice 5C | Release evidence and SBOM scaffold baseline | Complete" in checklist
    assert "Slice 5D | Container build and image baseline enforcement | Complete" in checklist
    assert "Slice 4E | Platform validation coverage manifest and contract | Complete" in checklist
    assert "Slice 5E | Companion dependency lock scaffold baseline | Complete" in checklist
    assert "Slice 5F | Platform automation runtime isolation baseline | Complete" in checklist
    assert "Slice 5G | Repository text and line-ending hygiene scaffold baseline | Complete" in checklist
    assert "Slice 5H | Workflow action runtime baseline | Complete" in checklist
    assert "Slice 5I | Implementation-state reconciliation and governance drift cleanup | Complete" in checklist
    assert "Slice 6A | PR readiness and conflict cleanup | Complete" in checklist
    assert "Slice 6B | Single-developer governance closeout | Complete" in checklist
    assert "stale red gateway PR #84 was closed with branch preserved" in checklist
    assert "workbench PR #77 was updated from `main`, conflict-resolved, and returned to green" in checklist
    assert "There are no RFC-0072 implementation deviations" in checklist
    assert "required approving review count is `0` for the single-developer operating model" in checklist
    assert "Current scaffold source of truth" in checklist

    assert "| `lotus-core` | Domain API | `.github/workflows/feature-lane.yml`, `.github/workflows/pr-merge-gate.yml`, `.github/workflows/main-releasability.yml`, `.github/workflows/pr-auto-merge.yml`" in mapping
    assert "lotus-workbench" in mapping
    assert "lotus-gateway" in mapping
    assert "lotus-platform" in mapping
    assert ".github/workflows/feature-lane.yml" in mapping
    assert ".github/workflows/pr-merge-gate.yml" in mapping
    assert ".github/workflows/main-releasability.yml" in mapping
    assert "feature-lane.backend.template.yml" in mapping
    assert "pr-merge-gate.backend.template.yml" in mapping
    assert "main-releasability.backend.template.yml" in mapping
    assert "merged-pr-main-releasability.template.yml" in mapping

    for repo_name in (
        "lotus-workbench",
        "lotus-gateway",
        "lotus-core",
        "lotus-performance",
        "lotus-risk",
        "lotus-advise",
        "lotus-manage",
        "lotus-report",
        "lotus-ai",
        "lotus-platform",
    ):
        assert repo_name in gap_audit

    assert "P0" in gap_audit
    assert "P1" in gap_audit
    assert "Application and service repositories covered by RFC-0072 have now converged to explicit lane workflows." in gap_audit
    assert "Platform validation is normalized and must keep expanding with product coverage" in gap_audit
    assert "Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `pr-auto-merge.yml` now exist" in gap_audit
    assert "Explicit `feature-lane.yml`, `pr-merge-gate.yml`, `main-releasability.yml`, and `platform-end-to-end-validation.yml` now exist" in gap_audit
    assert "platform-end-to-end-validation.yml" in gap_audit
    assert "Strong explicit lane split while retaining heavy gates for load, latency, Docker smoke, coverage, and institutional sign-off evidence" in gap_audit
    assert "branch protection is governed through `repository-governance-policy.json`" in gap_audit
    assert "branch-protection rollout must be applied" not in gap_audit
    assert "Workflow names still drift" not in gap_audit

    assert "Generated Workflow Files" in template_contract
    assert "PR Merge Gate / Workflow Lint" in template_contract
    assert "Main Releasability / Validate Docker Build" in template_contract
    assert "merged-pr-main-releasability.yml" in template_contract
    assert "workflow_dispatch" in template_contract
    assert "make ci-contract-gate" in template_contract

    assert "Repository-Native Command Policy" in hygiene_standard
    assert ".editorconfig" in hygiene_standard
    assert ".gitattributes" in hygiene_standard
    assert ".gitignore" in hygiene_standard
    assert ".dockerignore" in hygiene_standard
    assert "pyproject.toml" in hygiene_standard
    assert "requirements/shared-runtime.lock.txt" in hygiene_standard
    assert "requirements/ci-tooling.lock.txt" in hygiene_standard
    assert "pull_request_target" in workflow_security_standard
    assert "write-capable workflows" in workflow_security_standard
    assert "least-privilege" in workflow_security_standard
    assert "actions/checkout" in workflow_action_runtime_standard
    assert "actions/setup-python" in workflow_action_runtime_standard
    assert "actions/setup-node" in workflow_action_runtime_standard
    assert "actions/upload-artifact" in workflow_action_runtime_standard
    assert "NODE_OPTIONS=--no-deprecation" in workflow_action_runtime_standard
    assert "Dependency SBOM Baseline" in release_evidence_standard
    assert "release-evidence.json" in release_evidence_standard
    assert "main-releasability-release-evidence" in release_evidence_standard
    assert "BuildKit Cache Mounts" in container_build_standard
    assert "docker/setup-buildx-action" in container_build_standard
    assert "run as non-root" in container_build_standard
    assert "core-performance-baseline" in platform_validation_coverage_standard
    assert "core-performance-green-lanes" in platform_validation_coverage_standard
    assert "platform-validation-profiles.json" in platform_validation_coverage_standard

    assert "feature-lane.backend.template.yml" in scaffold_script
    assert "pr-merge-gate.backend.template.yml" in scaffold_script
    assert "main-releasability.backend.template.yml" in scaffold_script
    assert "merged-pr-main-releasability.template.yml" in scaffold_script
    assert "scripts/ci_contract_gate.py" in scaffold_script
    assert ".gitignore.backend.template" in scaffold_script
    assert ".dockerignore.backend.template" in scaffold_script
    assert "requirements.shared-runtime.lock.template.txt" in scaffold_script
    assert "requirements.ci-tooling.lock.template.txt" in scaffold_script
    assert 'preflight_fast_command = "make check"' in scaffold_script
    assert 'preflight_full_command = "make ci"' in scaffold_script
    assert "ci.backend.template.yml" not in scaffold_script
    assert "--rebase --delete-branch" in auto_merge_template
    assert "--merge --delete-branch" not in auto_merge_template
    assert "--squash" not in auto_merge_template
    assert "secrets.LOTUS_AUTOMERGE_TOKEN" in auto_merge_template
    assert "LOTUS_AUTOMERGE_TOKEN is required" in auto_merge_template
    assert "github.token" not in auto_merge_template
    assert "gh workflow run main-releasability.yml" in merged_pr_dispatch_template
    assert "--ref main" in merged_pr_dispatch_template
    assert "github.event.pull_request.merged == true" in merged_pr_dispatch_template


def test_platform_standards_and_runbook_point_to_rfc_0072_sources() -> None:
    standards_readme = (ROOT / "platform-standards" / "README.md").read_text(encoding="utf-8")
    docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    scaffold_guide = (
        ROOT / "docs" / "onboarding" / "LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md"
    ).read_text(encoding="utf-8")
    wiki_scaffold = (ROOT / "wiki" / "New-Backend-Service-Scaffold.md").read_text(
        encoding="utf-8"
    )
    wiki_sidebar = (ROOT / "wiki" / "_Sidebar.md").read_text(encoding="utf-8")
    bank_buyable_contract = (
        ROOT / "platform-standards" / "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md"
    ).read_text(encoding="utf-8")
    workflow_standard = (ROOT / "platform-standards" / "Development-Workflow-and-CI-Strategy-Standard.md").read_text(
        encoding="utf-8"
    )
    local_runbook = (
        ROOT / "docs" / "operations" / "Local Development Runbook.md"
    ).read_text(encoding="utf-8")

    assert "docs/standards/Continuous Integration, Validation, and Release Governance Standard.md" in standards_readme
    assert "RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md" in standards_readme
    assert "Backend-CI-Lane-Template-Contract.md" in standards_readme
    assert "Repository-Hygiene-and-Dependency-Model-Standard.md" in standards_readme
    assert ".editorconfig.backend.template" in standards_readme
    assert ".gitattributes.backend.template" in standards_readme
    assert "requirements.shared-runtime.lock.template.txt" in standards_readme
    assert "requirements.ci-tooling.lock.template.txt" in standards_readme
    assert "Workflow-Security-and-Permissions-Standard.md" in standards_readme
    assert "Workflow-Action-Runtime-and-Version-Baseline.md" in standards_readme
    assert "Release-Evidence-and-SBOM-Foundation-Standard.md" in standards_readme
    assert "merged-pr-main-releasability.template.yml" in standards_readme
    assert "Platform-End-to-End-Validation-Coverage-Standard.md" in standards_readme
    assert "Repository-CI-Lane-Mapping-Baseline.md" in standards_readme
    assert "Repository-CI-Convergence-Gap-Audit.md" in standards_readme
    assert "LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md" in standards_readme
    assert "LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md" in standards_readme
    assert "LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md" in docs_readme
    assert "LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md" in automation_readme
    assert "Service Profiles" in scaffold_guide
    assert "Generated Repository Shape" in scaffold_guide
    assert "merged-pr-main-releasability.yml" in scaffold_guide
    assert "Starting Runtime Features" in scaffold_guide
    assert "Starting Governance And Quality Features" in scaffold_guide
    assert "What The Scaffold Does Not Provide" in scaffold_guide
    assert "make architecture-boundary-report" in scaffold_guide
    assert "make quality-baseline" in scaffold_guide
    assert "New Backend Service Scaffold" in wiki_sidebar
    assert "Lotus Backend Service Scaffold Guide" in wiki_scaffold

    assert "Do not fake compliance" in bank_buyable_contract
    assert "docs/standards/Continuous Integration, Validation, and Release Governance Standard.md" in bank_buyable_contract
    assert "docs/standards/Platform Observability Standards.md" in bank_buyable_contract
    assert "`Continuous Integration, Validation, and Release Governance Standard.md`" not in bank_buyable_contract
    assert "Remote Feature Lane" in bank_buyable_contract
    assert "Pull Request Merge Gate" in bank_buyable_contract
    assert "Main Releasability Gate" in bank_buyable_contract
    assert "Platform End-to-End Validation" in bank_buyable_contract
    assert "Unknown - requires owner review" in bank_buyable_contract
    assert "merged-to-main and validated as the definition of done" in bank_buyable_contract

    assert "Authoritative CI governance now lives in" in workflow_standard
    assert "docs/standards/Continuous Integration, Validation, and Release Governance Standard.md" in workflow_standard
    assert "`Continuous Integration, Validation, and Release Governance Standard.md`" not in workflow_standard
    assert "Remote Feature Lane" in workflow_standard
    assert "Platform End-to-End Validation Lane" in workflow_standard

    assert "RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md" in local_runbook


def test_backend_lane_templates_exist_and_define_explicit_lane_names() -> None:
    workflows_dir = ROOT / "platform-standards" / "templates" / "workflows"
    feature_lane = (workflows_dir / "feature-lane.backend.template.yml").read_text(encoding="utf-8")
    pr_merge_gate = (workflows_dir / "pr-merge-gate.backend.template.yml").read_text(encoding="utf-8")
    main_releasability = (workflows_dir / "main-releasability.backend.template.yml").read_text(encoding="utf-8")
    standards_validator = (ROOT / "automation" / "Validate-Backend-Standards.ps1").read_text(encoding="utf-8")

    assert "name: Remote Feature Lane" in feature_lane
    assert "Feature Lane / Tests (unit)" in feature_lane
    assert "make lint" in feature_lane

    assert "name: Pull Request Merge Gate" in pr_merge_gate
    assert "PR Merge Gate / Coverage Gate (Combined)" in pr_merge_gate
    assert "NODE_OPTIONS: --no-deprecation" in pr_merge_gate

    assert "name: Main Releasability Gate" in main_releasability
    assert "Main Releasability / Validate Docker Build" in main_releasability
    assert "NODE_OPTIONS: --no-deprecation" in main_releasability

    assert "feature-lane-workflow" in standards_validator
    assert "pr-merge-gate-workflow" in standards_validator
    assert "main-releasability-workflow" in standards_validator
    assert "explicit-lane-workflows" in standards_validator


def test_platform_repo_lane_workflows_and_shared_entrypoint_exist() -> None:
    feature_lane = (ROOT / ".github" / "workflows" / "feature-lane.yml").read_text(encoding="utf-8")
    pr_merge_gate = (ROOT / ".github" / "workflows" / "pr-merge-gate.yml").read_text(encoding="utf-8")
    main_releasability = (ROOT / ".github" / "workflows" / "main-releasability.yml").read_text(
        encoding="utf-8"
    )
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(encoding="utf-8")

    assert "name: Remote Feature Lane" in feature_lane
    assert "Feature Lane / Platform Repo Contracts" in feature_lane
    assert "repository: sgajbi/lotus-render" in feature_lane
    assert "repository: sgajbi/lotus-archive" in feature_lane
    assert "timeout-minutes: 10" in feature_lane
    assert "timeout-minutes: 45" in feature_lane

    assert "name: Pull Request Merge Gate" in pr_merge_gate
    assert "PR Merge Gate / Platform Repo Contracts" in pr_merge_gate
    assert "repository: sgajbi/lotus-render" in pr_merge_gate
    assert "repository: sgajbi/lotus-archive" in pr_merge_gate
    assert "timeout-minutes: 10" in pr_merge_gate
    assert "timeout-minutes: 45" in pr_merge_gate

    assert "name: Main Releasability Gate" in main_releasability
    assert "Main Releasability / Platform Repo Contracts" in main_releasability
    assert "repository: sgajbi/lotus-render" in main_releasability
    assert "repository: sgajbi/lotus-archive" in main_releasability
    assert "timeout-minutes: 10" in main_releasability
    assert "timeout-minutes: 45" in main_releasability

    assert 'ValidateSet("feature", "pr-merge", "main-releasability")' in repo_checks
    assert "Resolve-PlatformAutomationPython.ps1" in repo_checks
    assert "Invoke-CheckedCommand $toolingPython -m pytest tests/unit -q" in repo_checks
    assert (
        "Invoke-CheckedCommand $toolingPython automation/validate_workflow_security.py"
        in repo_checks
    )
    assert (
        "Invoke-CheckedCommand $toolingPython automation/validate_workflow_action_runtime.py"
        in repo_checks
    )
    assert (
        "Invoke-CheckedCommand $toolingPython automation/validate_container_build_baseline.py"
        in repo_checks
    )
    assert (
        "Invoke-CheckedCommand $toolingPython automation/validate_platform_validation_coverage.py"
        in repo_checks
    )
    assert "Validate-Backend-Standards.ps1" in repo_checks


def test_platform_validation_lane_workflow_and_shared_entrypoint_exist() -> None:
    platform_validation = (ROOT / ".github" / "workflows" / "platform-end-to-end-validation.yml").read_text(
        encoding="utf-8"
    )
    validation_entrypoint = (ROOT / "automation" / "Invoke-PlatformValidationLane.ps1").read_text(
        encoding="utf-8"
    )

    assert "name: Platform End-to-End Validation" in platform_validation
    assert "core-performance-green-lanes" in platform_validation
    assert "core-performance-baseline" in platform_validation
    assert "Invoke-PlatformValidationLane.ps1" in platform_validation
    assert 'ValidateSet("core-performance-baseline", "core-performance-green-lanes")' in validation_entrypoint
    assert "platform-validation-profiles.json" in validation_entrypoint
    assert "Resolve-PlatformAutomationPython.ps1" in validation_entrypoint
    assert "core_performance_ci_entrypoint.py" in validation_entrypoint
    assert "render_cross_app_workflow_summary.py" in validation_entrypoint


def test_backend_governance_policy_tracks_wave_one_repo_lane_names() -> None:
    policy = (ROOT / "automation" / "repository-governance-policy.json").read_text(encoding="utf-8")
    governance_enforcer = (ROOT / "automation" / "Enforce-Repository-Governance.ps1").read_text(encoding="utf-8")
    governance_validator = (ROOT / "automation" / "validate_repository_governance.py").read_text(encoding="utf-8")
    hygiene_validator = (ROOT / "automation" / "validate_repository_hygiene.py").read_text(encoding="utf-8")
    workflow_validator = (ROOT / "automation" / "validate_workflow_security.py").read_text(encoding="utf-8")
    workflow_action_validator = (ROOT / "automation" / "validate_workflow_action_runtime.py").read_text(
        encoding="utf-8"
    )

    assert '"name":  "lotus-manage"' in policy
    assert '"name":  "lotus-report"' in policy
    assert '"name":  "lotus-gateway"' in policy
    assert '"name":  "lotus-workbench"' in policy
    assert "PR Merge Gate / Workflow Lint" in policy
    assert "PR Merge Gate / Lint Typecheck Security" in policy
    assert "PR Merge Gate / Coverage Gate (Combined)" in policy
    assert "PR Merge Gate / Lint Typecheck Unit" in policy
    assert "PR Merge Gate / CI Local Docker Parity" in policy
    assert "PR Merge Gate / Lint Typecheck Coverage Build" in policy
    assert "PR Merge Gate / Playwright Smoke" in policy
    assert '"name":  "lotus-performance"' in policy
    assert '"name":  "lotus-risk"' in policy
    assert '"name":  "lotus-ai"' in policy
    assert '"name":  "lotus-advise"' in policy
    assert '"name":  "lotus-platform"' in policy
    assert "PR Merge Gate / Lint Typecheck Contracts Security" in policy
    assert "PR Merge Gate / Tests (unit-db)" in policy
    assert "PR Merge Gate / Tests (ops-contract)" in policy
    assert "PR Merge Gate / Tests (transaction-buy-contract)" in policy
    assert "PR Merge Gate / Tests (transaction-sell-contract)" in policy
    assert "PR Merge Gate / Tests (transaction-dividend-contract)" in policy
    assert "PR Merge Gate / Tests (transaction-interest-contract)" in policy
    assert "PR Merge Gate / Tests (transaction-fx-contract)" in policy
    assert "PR Merge Gate / Tests (transaction-portfolio-flow-bundle-contract)" in policy
    assert "PR Merge Gate / E2E Smoke" in policy
    assert "PR Merge Gate / Docker Smoke Contract" in policy
    assert "PR Merge Gate / Latency Gate" in policy
    assert "PR Merge Gate / Performance Load Gate (Fast)" in policy
    assert "PR Merge Gate / Test Pyramid Gate" in policy
    assert "PR Merge Gate / Runtime Mode Smoke" in policy
    assert "PR Merge Gate / Postgres Migration Smoke" in policy
    assert "PR Merge Gate / Production Profile Startup Smoke" in policy
    assert "PR Merge Gate / Production Profile Guardrail Negatives" in policy
    assert "PR Merge Gate / Platform Repo Contracts" in policy
    assert "Cross-App Vocabulary Gate" in policy
    assert "automation/repository-governance-policy.json" in governance_enforcer
    assert "required_linear_history = $true" in governance_enforcer
    assert "allow_squash_merge=false" in governance_enforcer
    assert "allow_merge_commit=false" in governance_enforcer
    assert "allow_rebase_merge=true" in governance_enforcer
    assert "required_conversation_resolution = $true" in governance_enforcer
    assert "required_approving_review_count = 0" in governance_enforcer
    assert "Repository Governance Enforcement" in governance_enforcer
    assert "repository-governance-validation" in (ROOT / "automation" / "task-profiles.json").read_text(encoding="utf-8")
    assert "def fetch_repository_governance" in governance_validator
    assert "allow_auto_merge" in governance_validator
    assert "required_conversation_resolution" in governance_validator
    assert "determine_dependency_authority" in hygiene_validator
    assert "REQUIRED_GITIGNORE_PATTERNS" in hygiene_validator
    assert "ALLOWLIST" in workflow_validator
    assert "pull_request_target" in workflow_validator
    assert "ACTION_MAJOR_BASELINE" in workflow_action_validator
    assert "actions/setup-node" in workflow_action_validator
