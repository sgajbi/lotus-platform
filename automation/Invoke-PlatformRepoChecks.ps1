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

function Assert-LastExitCode {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CommandDisplay
    )

    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $CommandDisplay"
    }
}

Push-Location $repoRoot
try {
    $toolingPython = & (Join-Path $PSScriptRoot "Resolve-PlatformAutomationPython.ps1")

    Invoke-CheckedCommand $toolingPython -m pytest tests/unit -q
    Invoke-CheckedCommand $toolingPython automation/validate_engineering_context_system.py
    Invoke-CheckedCommand $toolingPython automation/validate_agent_engineering_contracts.py
    Invoke-CheckedCommand $toolingPython automation/validate_heartbeat_contracts.py
    Invoke-CheckedCommand $toolingPython automation/validate_lifecycle_authority_contracts.py
    Invoke-CheckedCommand $toolingPython automation/validate_bank_readiness_control_catalog.py
    Invoke-CheckedCommand $toolingPython automation/validate_lotus_skill_alignment.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_observability_contract.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_ecosystem_completion.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_ecosystem_hardening.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_ecosystem_final_closure.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_scaffold_ci_enforcement.py
    Invoke-CheckedCommand $toolingPython automation/validate_canonical_front_office_demo_data_contract.py
    Invoke-CheckedCommand $toolingPython automation/validate_workflow_security.py
    Invoke-CheckedCommand $toolingPython automation/validate_auto_merge_releasability.py --require-local-repos
    Invoke-CheckedCommand $toolingPython automation/validate_workflow_action_runtime.py
    Invoke-CheckedCommand $toolingPython automation/validate_container_build_baseline.py
    Invoke-CheckedCommand $toolingPython automation/validate_deployment_promotion_manifest.py
    Invoke-CheckedCommand $toolingPython automation/validate_platform_validation_coverage.py
    Invoke-CheckedCommand $toolingPython automation/generate_enterprise_backend_quality_baseline.py --check
    Invoke-CheckedCommand $toolingPython automation/generate_automation_inventory.py --check
    Invoke-CheckedCommand $toolingPython automation/mesh_certification_gate.py --mode advisory --generated-at-utc 2026-04-20T00:00:00Z --skip-publication-checks
    $agentContractScript = Join-Path $PSScriptRoot "Sync-AgentOperatingContract.ps1"
    & $agentContractScript -CheckOnly
    Assert-LastExitCode "$agentContractScript -CheckOnly"

    $repoWikiSyncScript = Join-Path $PSScriptRoot "Sync-RepoWikis.ps1"
    & $repoWikiSyncScript -CheckOnly -Repository "lotus-platform" -AllowUnpublishedSourceChanges
    Assert-LastExitCode "$repoWikiSyncScript -CheckOnly -Repository lotus-platform -AllowUnpublishedSourceChanges"

    if ($Lane -in @("pr-merge", "main-releasability")) {
        $backendStandardsScript = Join-Path $repoRoot "automation\Validate-Backend-Standards.ps1"
        & $backendStandardsScript
        Assert-LastExitCode $backendStandardsScript
    }

    if ($Lane -eq "main-releasability") {
        Invoke-CheckedCommand $toolingPython automation/validate_mainline_commit_provenance.py
    }
}
finally {
    Pop-Location
}
