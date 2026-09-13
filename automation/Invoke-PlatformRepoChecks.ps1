param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("feature", "pr-merge", "main-releasability", "fleet-conformance")]
    [string]$Lane,

    # A checked-in or caller-supplied manifest is used only to exercise the
    # fleet executor itself.  The production workflow supplies neither value
    # and always runs the static governed validator list below.
    [string]$FleetValidatorManifest,

    [string]$FleetEvidenceDirectory
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

function Get-FleetValidators {
    param([string]$ManifestPath)

    $governed = @(
        [pscustomobject]@{ Name = "sibling-pin-drift"; Arguments = @("automation/validate_sibling_source_manifest.py", "--report-drift", "--summary") },
        [pscustomobject]@{ Name = "auto-merge-releasability"; Arguments = @("automation/validate_auto_merge_releasability.py", "--require-local-repos", "--fail-on-unverified") },
        [pscustomobject]@{ Name = "workflow-pipeline-exit-codes"; Arguments = @("automation/validate_workflow_pipeline_exit_codes.py", "--require-local-repos") },
        [pscustomobject]@{ Name = "canonical-front-office-demo-data"; Arguments = @("automation/validate_canonical_front_office_demo_data_contract.py") }
    )
    if ([string]::IsNullOrWhiteSpace($ManifestPath)) {
        return $governed
    }
    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        throw "Fleet validator manifest does not exist: $ManifestPath"
    }
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    if ($null -eq $manifest.validators -or @($manifest.validators).Count -eq 0) {
        throw "Fleet validator manifest must contain a non-empty validators array."
    }
    $validated = @()
    $validatorNames = @{}
    foreach ($validator in @($manifest.validators)) {
        if ([string]::IsNullOrWhiteSpace([string]$validator.name) -or $null -eq $validator.arguments -or @($validator.arguments).Count -eq 0) {
            throw "Each fleet validator must name itself and provide non-empty arguments."
        }
        $name = [string]$validator.name
        if ($validatorNames.ContainsKey($name)) {
            throw "Fleet validator manifest contains duplicate name: $name"
        }
        $validatorNames[$name] = $true
        $validated += [pscustomobject]@{
            Name = $name
            Arguments = @($validator.arguments | ForEach-Object { [string]$_ })
        }
    }
    return $validated
}

Push-Location $repoRoot
try {
    $toolingPython = & (Join-Path $PSScriptRoot "Resolve-PlatformAutomationPython.ps1")

    if ($Lane -eq "fleet-conformance") {
        # The current-estate view. The per-commit lanes read every sibling at the
        # revision pinned in platform-contracts/ci-governance/sibling-source-manifest.v1.json,
        # which freezes their view of the estate; this lane reads sibling default
        # branches as they are now, so a sibling regression or convergence stays
        # visible somewhere, and reports how far each pin lags. A red here names a
        # fleet owner; it never blocks an unrelated platform pull request.
        #
        # Every check runs to completion whatever the earlier ones found: a drift
        # finding must not hide the conformance verdicts behind it. Only one of
        # the validators writes its own report under output/; the rest speak on
        # stdout, so each check's combined output is captured under
        # output/fleet-conformance/<check>.log with its exit code preserved, and
        # that directory is what the lane uploads. The outcome is the aggregate
        # -- one table, written there too, and a failure if any check failed.
        $evidenceDirectory = if ([string]::IsNullOrWhiteSpace($FleetEvidenceDirectory)) {
            Join-Path $repoRoot "output/fleet-conformance"
        } else {
            $FleetEvidenceDirectory
        }
        New-Item -ItemType Directory -Force -Path $evidenceDirectory | Out-Null
        Get-ChildItem -Path $evidenceDirectory -File | Remove-Item -Force
        $fleetOutcomes = [ordered]@{}
        function Invoke-RecordedFleetCheck {
            param(
                [Parameter(Mandatory = $true)]
                [string]$Name,

                [Parameter(Mandatory = $true)]
                [string[]]$Arguments
            )

            $log = Join-Path $evidenceDirectory "$Name.log"
            Write-Output "::group::fleet-conformance/$Name"
            # Native stderr becomes error records under 2>&1; they are evidence
            # here, not a reason to stop, so the preference is relaxed for the
            # invocation only. $LASTEXITCODE is the native process's, untouched
            # by Tee-Object.
            $ErrorActionPreference = "Continue"
            & $toolingPython @Arguments 2>&1 | Tee-Object -FilePath $log
            $exitCode = $LASTEXITCODE
            $ErrorActionPreference = "Stop"
            $fleetOutcomes[$Name] = $exitCode
            Write-Output "::endgroup::"
        }
        $validators = Get-FleetValidators -ManifestPath $FleetValidatorManifest
        foreach ($validator in $validators) {
            $arguments = @($validator.Arguments)
            if ($validator.Name -eq "sibling-pin-drift" -and [string]::IsNullOrWhiteSpace($FleetValidatorManifest)) {
                $arguments += @("--report-drift", "--summary", (Join-Path $evidenceDirectory "pin-drift.md"))
            }
            Invoke-RecordedFleetCheck -Name $validator.Name -Arguments $arguments
        }

        $summaryLines = @("## Fleet conformance outcomes", "", "| Check | Exit code | Outcome | Evidence |", "| --- | --- | --- | --- |")
        foreach ($entry in $fleetOutcomes.GetEnumerator()) {
            $outcome = if ($entry.Value -eq 0) { "pass" } else { "FAIL" }
            $summaryLines += "| $($entry.Key) | $($entry.Value) | $outcome | ``output/fleet-conformance/$($entry.Key).log`` |"
        }
        $summaryLines | ForEach-Object { Write-Output $_ }
        ($summaryLines + "") | Set-Content -Path (Join-Path $evidenceDirectory "outcomes.md")
        if (-not [string]::IsNullOrWhiteSpace($env:GITHUB_STEP_SUMMARY)) {
            $driftReport = Join-Path $evidenceDirectory "pin-drift.md"
            if (Test-Path $driftReport) {
                Get-Content -Path $driftReport | Add-Content -Path $env:GITHUB_STEP_SUMMARY
            }
            ($summaryLines + "") | Add-Content -Path $env:GITHUB_STEP_SUMMARY
        }
        $failedChecks = @($fleetOutcomes.GetEnumerator() | Where-Object { $_.Value -ne 0 } | ForEach-Object { $_.Key })
        if ($failedChecks.Count -gt 0) {
            throw "Fleet conformance failed: $($failedChecks -join ', ')"
        }
        return
    }

    # Repository-local: the manifest must name every registered sibling exactly
    # once with a full revision, or a lane checkout would fall back to a default
    # branch and the verdict would stop being a function of this commit.
    Invoke-CheckedCommand $toolingPython automation/validate_sibling_source_manifest.py
    Invoke-CheckedCommand $toolingPython -m pytest tests/unit -q
    Invoke-CheckedCommand $toolingPython automation/validate_engineering_context_system.py
    Invoke-CheckedCommand $toolingPython automation/validate_agent_engineering_contracts.py
    Invoke-CheckedCommand $toolingPython automation/validate_heartbeat_contracts.py
    Invoke-CheckedCommand $toolingPython automation/validate_lifecycle_authority_contracts.py
    Invoke-CheckedCommand $toolingPython automation/validate_bff_principal_session_contracts.py
    Invoke-CheckedCommand $toolingPython automation/validate_principal_resolution_contracts.py
    Invoke-CheckedCommand $toolingPython automation/validate_bank_readiness_control_catalog.py
    Invoke-CheckedCommand $toolingPython automation/validate_evidence_class_vocabulary.py
    Invoke-CheckedCommand $toolingPython automation/validate_lotus_skill_alignment.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_observability_contract.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_ecosystem_completion.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_ecosystem_hardening.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_ecosystem_final_closure.py
    Invoke-CheckedCommand $toolingPython automation/validate_analytics_ui_scaffold_ci_enforcement.py
    Invoke-CheckedCommand $toolingPython automation/validate_lotus_idea_rfc0002_platform_proof_consumption.py
    Invoke-CheckedCommand $toolingPython automation/validate_canonical_front_office_demo_data_contract.py
    Invoke-CheckedCommand $toolingPython automation/validate_workflow_security.py
    Invoke-CheckedCommand $toolingPython automation/validate_auto_merge_releasability.py --require-local-repos
    Invoke-CheckedCommand $toolingPython automation/validate_workflow_action_runtime.py
    Invoke-CheckedCommand $toolingPython automation/validate_workflow_pipeline_exit_codes.py
    Invoke-CheckedCommand $toolingPython automation/check_branch_protection_policy.py --offline
    Invoke-CheckedCommand $toolingPython automation/validate_container_build_baseline.py
    Invoke-CheckedCommand $toolingPython automation/validate_platform_stack.py
    Invoke-CheckedCommand $toolingPython automation/validate_vulnerability_exception_register.py
    Invoke-CheckedCommand $toolingPython automation/validate_technology_governance_policy.py
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
        $mainlinePolicyBranch = if ([string]::IsNullOrWhiteSpace($env:LOTUS_MAINLINE_POLICY_BRANCH)) {
            "main"
        } else {
            $env:LOTUS_MAINLINE_POLICY_BRANCH
        }
        Invoke-CheckedCommand $toolingPython automation/validate_mainline_commit_provenance.py --branch $mainlinePolicyBranch
    }
}
finally {
    Pop-Location
}
