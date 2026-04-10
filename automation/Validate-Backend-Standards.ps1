param(
    [string]$ReposPath = "automation/repos.json",
    [string]$OutputJsonPath = "output/backend-standards-conformance.json",
    [string]$OutputMarkdownPath = "output/backend-standards-conformance.md"
)

$ErrorActionPreference = "Stop"

$reposConfig = Get-Content -Raw $ReposPath | ConvertFrom-Json
$repoEntries = if ($reposConfig -is [System.Array]) { $reposConfig } elseif ($reposConfig.repositories) { $reposConfig.repositories } else { @() }
$backendRepos = @(
    $repoEntries |
        Where-Object {
            $_.name -like "lotus-*" -and
            $_.name -ne "lotus-platform" -and
            ((("" + $_.preflight_fast_command) -match "python|make") -or (("" + $_.preflight_full_command) -match "python|make"))
        } |
        ForEach-Object { [string]$_.name }
)
$requiredMakeTargets = @("lint", "typecheck", "test", "ci", "security-audit", "migration-smoke", "migration-apply")
$requiredCiPatterns = @(
    "make lint|ruff check",
    "make typecheck|mypy",
    "make security-audit|pip_audit|dependency",
    "make migration-smoke|migration contract smoke|postgres-migration-smoke",
    "pytest|make test|make check",
    "coverage report|cov-fail-under|fail-under|make test-coverage|make coverage-gate"
)
$featureLaneNames = @("feature-lane.yml", "feature-lane.yaml")
$prMergeGateNames = @("pr-merge-gate.yml", "pr-merge-gate.yaml")
$mainReleasabilityNames = @("main-releasability.yml", "main-releasability.yaml")
$legacyCiNames = @("ci.yml", "ci.yaml", "backend-ci.yml", "pipeline.yml")

function Get-MakeTargets {
    param([string]$MakefilePath)
    if (-not (Test-Path $MakefilePath)) { return @() }
    $targets = @()
    foreach ($line in Get-Content $MakefilePath) {
        if ($line -match '^[a-zA-Z0-9_.-]+\s*:') {
            $targets += (($line -split ':')[0]).Trim()
        }
    }
    return $targets | Select-Object -Unique
}

function Find-WorkflowFile {
    param([string]$WorkflowDir, [string[]]$Names)
    foreach ($name in $Names) {
        $candidate = Join-Path $WorkflowDir $name
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

function Test-AnyPattern {
    param([string]$Content, [string[]]$Patterns)
    foreach ($pattern in $Patterns) {
        if ($Content -match $pattern) { return $true }
    }
    return $false
}

if (-not (Test-Path $ReposPath)) {
    throw "Repos config not found: $ReposPath"
}

$repos = $repoEntries
$results = @()

foreach ($repo in $repos) {
    if ($backendRepos -notcontains $repo.name) { continue }

    $repoPath = $repo.path
    $missing = New-Object System.Collections.Generic.List[string]

    if (-not (Test-Path $repoPath)) {
        $results += [pscustomobject]@{
            repo = $repo.name
            path = $repoPath
            exists = $false
            makefile = $false
            make_targets_ok = $false
            mypy_config = $false
            pre_commit = $false
            feature_lane_workflow = $false
            pr_merge_gate_workflow = $false
            main_releasability_workflow = $false
            legacy_ci_workflow = $false
            lane_workflow_mode = "missing"
            pr_auto_merge_workflow = $false
            ci_gates_ok = $false
            status = "missing-repo"
            missing = @("repo")
        }
        continue
    }

    $makefilePath = Join-Path $repoPath "Makefile"
    $makeTargets = Get-MakeTargets -MakefilePath $makefilePath
    $missingMakeTargets = @($requiredMakeTargets | Where-Object { $_ -notin $makeTargets })

    $hasMypyConfig = (Test-Path (Join-Path $repoPath "mypy.ini")) -or (Test-Path (Join-Path $repoPath "pyproject.toml"))
    $hasPreCommit = Test-Path (Join-Path $repoPath ".pre-commit-config.yaml")
    $hasMigrationContractDoc = Test-Path (Join-Path $repoPath "docs/standards/migration-contract.md")
    $hasDataModelOwnershipDoc = Test-Path (Join-Path $repoPath "docs/standards/data-model-ownership.md")

    $workflowDir = Join-Path $repoPath ".github/workflows"
    $featureLaneWorkflow = $null
    $prMergeGateWorkflow = $null
    $mainReleasabilityWorkflow = $null
    $ciWorkflow = $null
    $prAutoMergeWorkflow = $null
    $ciGatesOk = $false
    $laneWorkflowMode = "missing"

    if (Test-Path $workflowDir) {
        $featureLaneWorkflow = Find-WorkflowFile -WorkflowDir $workflowDir -Names $featureLaneNames
        $prMergeGateWorkflow = Find-WorkflowFile -WorkflowDir $workflowDir -Names $prMergeGateNames
        $mainReleasabilityWorkflow = Find-WorkflowFile -WorkflowDir $workflowDir -Names $mainReleasabilityNames
        $ciWorkflow = Find-WorkflowFile -WorkflowDir $workflowDir -Names $legacyCiNames
        $prAutoMergeWorkflow = Find-WorkflowFile -WorkflowDir $workflowDir -Names @("pr-auto-merge.yml", "pr-auto-merge.yaml")

        if ($featureLaneWorkflow -and $prMergeGateWorkflow -and $mainReleasabilityWorkflow) {
            $laneWorkflowMode = "explicit"
        }
        elseif ($ciWorkflow) {
            $laneWorkflowMode = "legacy"
        }

        $gatingWorkflow = if ($prMergeGateWorkflow) { $prMergeGateWorkflow } else { $ciWorkflow }
        if ($gatingWorkflow) {
            $ciContent = (Get-Content -Raw $gatingWorkflow)
            $hits = 0
            foreach ($pattern in $requiredCiPatterns) {
                $options = $pattern -split '\|'
                if (Test-AnyPattern -Content $ciContent -Patterns $options) { $hits += 1 }
            }
            $ciGatesOk = ($hits -eq $requiredCiPatterns.Count)
        }
    }

    if (-not (Test-Path $makefilePath)) { $missing.Add("Makefile") }
    if ($missingMakeTargets.Count -gt 0) { $missing.Add("make-targets: " + ($missingMakeTargets -join ", ")) }
    if (-not $hasMypyConfig) { $missing.Add("mypy-config") }
    if (-not $hasPreCommit) { $missing.Add(".pre-commit-config.yaml") }
    if (-not $hasMigrationContractDoc) { $missing.Add("docs/standards/migration-contract.md") }
    if (-not $hasDataModelOwnershipDoc) { $missing.Add("docs/standards/data-model-ownership.md") }
    if ($laneWorkflowMode -eq "missing") {
        $missing.Add("feature-lane-workflow")
        $missing.Add("pr-merge-gate-workflow")
        $missing.Add("main-releasability-workflow")
    }
    elseif ($laneWorkflowMode -eq "legacy") {
        $missing.Add("explicit-lane-workflows")
    }
    if (-not $prAutoMergeWorkflow) { $missing.Add("pr-auto-merge-workflow") }
    if (-not $ciGatesOk) { $missing.Add("ci-required-gates") }

    $status = if ($missing.Count -eq 0) { "ok" } elseif ($missing.Count -le 2) { "partial" } else { "gap" }

    $results += [pscustomobject]@{
        repo = $repo.name
        path = $repoPath
        exists = $true
        makefile = (Test-Path $makefilePath)
        make_targets_ok = ($missingMakeTargets.Count -eq 0)
        mypy_config = $hasMypyConfig
        pre_commit = $hasPreCommit
        migration_contract_doc = $hasMigrationContractDoc
        data_model_ownership_doc = $hasDataModelOwnershipDoc
        feature_lane_workflow = [bool]$featureLaneWorkflow
        pr_merge_gate_workflow = [bool]$prMergeGateWorkflow
        main_releasability_workflow = [bool]$mainReleasabilityWorkflow
        legacy_ci_workflow = [bool]$ciWorkflow
        lane_workflow_mode = $laneWorkflowMode
        pr_auto_merge_workflow = [bool]$prAutoMergeWorkflow
        ci_gates_ok = $ciGatesOk
        status = $status
        missing = @($missing)
    }
}

if (-not (Test-Path "output")) {
    New-Item -ItemType Directory -Path "output" | Out-Null
}

$summary = [pscustomobject]@{
    generated_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
    backend_repos = $backendRepos
    required_make_targets = $requiredMakeTargets
    results = $results
}

$summary | ConvertTo-Json -Depth 8 | Set-Content -Path $OutputJsonPath

$lines = @()
$lines += "# Backend Standards Conformance"
$lines += ""
$lines += "- Generated: $($summary.generated_at)"
$lines += "- Scope: $($backendRepos -join ', ')"
$lines += ""
$lines += "| Repo | Status | Make Targets | Mypy | Pre-commit | Migration Contract Doc | Data Model Doc | Feature Lane | PR Merge Gate | Main Releasability | Legacy CI | Lane Mode | PR Auto Merge | CI Gates | Missing |"
$lines += "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
foreach ($row in $results) {
    $missingText = if ($row.missing.Count -eq 0) { "-" } else { ($row.missing -join "; ") }
    $lines += "| $($row.repo) | $($row.status) | $($row.make_targets_ok) | $($row.mypy_config) | $($row.pre_commit) | $($row.migration_contract_doc) | $($row.data_model_ownership_doc) | $($row.feature_lane_workflow) | $($row.pr_merge_gate_workflow) | $($row.main_releasability_workflow) | $($row.legacy_ci_workflow) | $($row.lane_workflow_mode) | $($row.pr_auto_merge_workflow) | $($row.ci_gates_ok) | $missingText |"
}

Set-Content -Path $OutputMarkdownPath -Value ($lines -join "`n")
Write-Host "Wrote $OutputJsonPath"
Write-Host "Wrote $OutputMarkdownPath"



