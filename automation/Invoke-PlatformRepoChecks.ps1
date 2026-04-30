param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("feature", "pr-merge", "main-releasability")]
    [string]$Lane
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $repoRoot
try {
    $toolingPython = & (Join-Path $PSScriptRoot "Resolve-PlatformAutomationPython.ps1")

    & $toolingPython -m pytest tests/unit -q
    & $toolingPython automation/validate_engineering_context_system.py
    & $toolingPython automation/validate_agent_engineering_contracts.py
    & $toolingPython automation/validate_heartbeat_contracts.py
    & $toolingPython automation/validate_lotus_skill_alignment.py
    & $toolingPython automation/validate_analytics_ui_observability_contract.py
    & $toolingPython automation/validate_analytics_ui_ecosystem_completion.py
    & $toolingPython automation/validate_analytics_ui_ecosystem_hardening.py
    & $toolingPython automation/validate_analytics_ui_scaffold_ci_enforcement.py
    & $toolingPython automation/validate_workflow_security.py
    & $toolingPython automation/validate_workflow_action_runtime.py
    & $toolingPython automation/validate_container_build_baseline.py
    & $toolingPython automation/validate_platform_validation_coverage.py
    & $toolingPython automation/mesh_certification_gate.py --mode advisory --generated-at-utc 2026-04-20T00:00:00Z --skip-publication-checks
    & (Join-Path $PSScriptRoot "Sync-AgentOperatingContract.ps1") -CheckOnly
    & (Join-Path $PSScriptRoot "Sync-RepoWikis.ps1") -CheckOnly -Repository "lotus-platform" -AllowUnpublishedSourceChanges

    if ($Lane -in @("pr-merge", "main-releasability")) {
        & (Join-Path $repoRoot "automation\Validate-Backend-Standards.ps1")
    }
}
finally {
    Pop-Location
}
