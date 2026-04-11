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

$arguments = @(
    "-ExecutionPolicy", "Bypass",
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

& powershell @arguments
$syncExitCode = $LASTEXITCODE
if ($syncExitCode -ne 0) {
    exit $syncExitCode
}

if ($ValidateAfterSync) {
    $validateArguments = @(
        "-ExecutionPolicy", "Bypass",
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

    & powershell @validateArguments
    exit $LASTEXITCODE
}

exit 0
