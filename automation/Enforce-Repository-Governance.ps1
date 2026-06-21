param(
    [string]$Org = "sgajbi",
    [string]$PolicyPath = "automation/repository-governance-policy.json",
    [switch]$Apply
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $PolicyPath)) {
    throw "Policy file not found: $PolicyPath"
}

$policy = Get-Content -Raw -Path $PolicyPath | ConvertFrom-Json
$results = @()

foreach ($repo in $policy.repos) {
    $repoName = "$Org/$($repo.name)"
    $branch = "$($repo.default_branch)"
    $checks = @($repo.required_checks)

    $payload = @{
        required_status_checks = @{
            strict = $true
            contexts = $checks
        }
        enforce_admins = $true
        required_pull_request_reviews = @{
            dismiss_stale_reviews = $true
            require_code_owner_reviews = $false
            required_approving_review_count = 0
            require_last_push_approval = $false
        }
        restrictions = $null
        required_linear_history = $true
        allow_force_pushes = $false
        allow_deletions = $false
        block_creations = $false
        required_conversation_resolution = $true
        lock_branch = $false
        allow_fork_syncing = $true
    }

    $status = "planned"
    $errorMessage = $null
    try {
        if ($Apply) {
            gh api "repos/$repoName" -X PATCH -F allow_auto_merge=true -F allow_squash_merge=false -F allow_merge_commit=false -F allow_rebase_merge=true | Out-Null
            $tmp = New-TemporaryFile
            $payload | ConvertTo-Json -Depth 8 | Set-Content -Path $tmp
            gh api "repos/$repoName/branches/$branch/protection" -X PUT --input $tmp | Out-Null
            Remove-Item $tmp -Force -ErrorAction SilentlyContinue
            $status = "applied"
        }
    }
    catch {
        $status = "error"
        $errorMessage = $_.Exception.Message
    }

    $results += [pscustomobject]@{
        repo = $repoName
        branch = $branch
        required_checks_count = $checks.Count
        apply_mode = [bool]$Apply
        status = $status
        error = $errorMessage
    }
}

$outputJson = "output/repository-governance-enforcement.json"
$outputMd = "output/repository-governance-enforcement.md"

$results | ConvertTo-Json -Depth 6 | Set-Content -Path $outputJson

$lines = @(
    "# Repository Governance Enforcement",
    "",
    "- Generated: $(Get-Date -Format o)",
    "- Mode: $(if ($Apply) { "apply" } else { "plan" })",
    "",
    "| Repo | Branch | Checks | Status | Error |",
    "|---|---|---:|---|---|"
)
foreach ($r in $results) {
    $errorValue = if ([string]::IsNullOrWhiteSpace($r.error)) { "-" } else { $r.error }
    $lines += "| $($r.repo) | $($r.branch) | $($r.required_checks_count) | $($r.status) | $errorValue |"
}
$lines -join "`n" | Set-Content -Path $outputMd

Write-Output "Wrote $outputJson"
Write-Output "Wrote $outputMd"

