param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("feature", "pr-merge", "main-releasability")]
    [string]$Lane
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Command,

        [Parameter(Position = 1, ValueFromRemainingArguments = $true)]
        [object[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $Command $($Arguments -join ' ')"
    }
}

Push-Location $repoRoot
try {
    $toolingPython = & (Join-Path $PSScriptRoot "Resolve-PlatformAutomationPython.ps1")

    Invoke-CheckedCommand $toolingPython -m pytest tests/unit -q
    Invoke-CheckedCommand $toolingPython automation/validate_engineering_context_system.py
    Invoke-CheckedCommand $toolingPython automation/validate_agent_engineering_contracts.py
    Invoke-CheckedCommand $toolingPython automation/validate_heartbeat_contracts.py
    Invoke-CheckedCommand $toolingPython automation/validate_lotus_skill_alignment.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_observability_contract.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_ecosystem_completion.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_ecosystem_hardening.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_ecosystem_final_closure.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_scaffold_ci_enforcement.py
    Invoke-CheckedCommand $toolingPython automation/validate_workflow_security.py
    Invoke-CheckedCommand $toolingPython automation/validate_workflow_action_runtime.py
    Invoke-CheckedCommand $toolingPython automation/validate_container_build_baseline.py
    Invoke-CheckedCommand $toolingPython automation/validate_platform_validation_coverage.py
    Invoke-CheckedCommand $toolingPython automation/generate_enterprise_backend_quality_baseline.py --check
    Invoke-CheckedCommand $toolingPython automation/generate_automation_inventory.py --check
    Invoke-CheckedCommand $toolingPython automation/mesh_certification_gate.py --mode advisory --generated-at-utc 2026-04-20T00:00:00Z --skip-publication-checks
    Invoke-CheckedCommand (Join-Path $PSScriptRoot "Sync-AgentOperatingContract.ps1") -Arguments @("-CheckOnly")
    Invoke-CheckedCommand (Join-Path $PSScriptRoot "Sync-RepoWikis.ps1") -Arguments @("-CheckOnly", "-Repository", "lotus-platform", "-AllowUnpublishedSourceChanges")

    if ($Lane -in @("pr-merge", "main-releasability")) {
        Invoke-CheckedCommand (Join-Path $repoRoot "automation\Validate-Backend-Standards.ps1")
    }
}
finally {
    Pop-Location
}
