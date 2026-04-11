param(
    [ValidateSet("fast", "extended", "platform")]
    [string]$Profile = "fast",
    [string]$WorkspaceRoot = "",
    [string]$OutputDirectory = "output",
    [string]$SkillTargetPath = "",
    [string]$AgentsTargetPath = "",
    [switch]$ValidateAfterSync
)

$ErrorActionPreference = "Stop"

function Resolve-PowerShellExecutable {
    $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($pwsh) {
        return $pwsh.Source
    }

    $windowsPowerShell = Get-Command powershell -ErrorAction SilentlyContinue
    if ($windowsPowerShell) {
        return $windowsPowerShell.Source
    }

    throw "Unable to locate pwsh or powershell for bootstrap validation."
}

$powerShellExecutable = Resolve-PowerShellExecutable
$basePowerShellArguments = @("-NoProfile")
if ($env:OS -eq "Windows_NT") {
    $basePowerShellArguments += @("-ExecutionPolicy", "Bypass")
}

$arguments = $basePowerShellArguments + @(
    "-File", (Join-Path $PSScriptRoot "Validate-LotusDeveloperEnvironment.ps1"),
    "-Mode", "Sync",
    "-Profile", $Profile,
    "-OutputDirectory", $OutputDirectory
)

if ($WorkspaceRoot) {
    $arguments += @("-WorkspaceRoot", $WorkspaceRoot)
}
if ($SkillTargetPath) {
    $arguments += @("-SkillTargetPath", $SkillTargetPath)
}
if ($AgentsTargetPath) {
    $arguments += @("-AgentsTargetPath", $AgentsTargetPath)
}

& $powerShellExecutable @arguments
$syncExitCode = $LASTEXITCODE
if ($syncExitCode -ne 0) {
    exit $syncExitCode
}

if ($ValidateAfterSync) {
    $validateArguments = $basePowerShellArguments + @(
        "-File", (Join-Path $PSScriptRoot "Validate-LotusDeveloperEnvironment.ps1"),
        "-Mode", "Validate",
        "-Profile", $Profile,
        "-OutputDirectory", $OutputDirectory
    )
    if ($WorkspaceRoot) {
        $validateArguments += @("-WorkspaceRoot", $WorkspaceRoot)
    }
    if ($SkillTargetPath) {
        $validateArguments += @("-SkillTargetPath", $SkillTargetPath)
    }
    if ($AgentsTargetPath) {
        $validateArguments += @("-AgentsTargetPath", $AgentsTargetPath)
    }

    & $powerShellExecutable @validateArguments
    exit $LASTEXITCODE
}

exit 0
