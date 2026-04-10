param(
    [string]$VenvPath = ".venv-platform-automation",
    [string]$RequirementsPath = "automation/requirements.platform-automation.lock.txt"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$venvRoot = Join-Path $repoRoot $VenvPath
$requirementsFile = Join-Path $repoRoot $RequirementsPath

function Resolve-VenvPythonExecutable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$VirtualEnvironmentRoot
    )

    foreach ($candidatePath in @(
        (Join-Path $VirtualEnvironmentRoot "Scripts/python.exe"),
        (Join-Path $VirtualEnvironmentRoot "Scripts/python"),
        (Join-Path $VirtualEnvironmentRoot "bin/python"),
        (Join-Path $VirtualEnvironmentRoot "bin/python3")
    )) {
        if (Test-Path $candidatePath) {
            return $candidatePath
        }
    }

    return $null
}

$pythonExecutable = Resolve-VenvPythonExecutable -VirtualEnvironmentRoot $venvRoot

if (-not $pythonExecutable) {
    python -m venv $venvRoot
    $pythonExecutable = Resolve-VenvPythonExecutable -VirtualEnvironmentRoot $venvRoot
    if (-not $pythonExecutable) {
        throw "Unable to resolve the platform automation Python executable from '$venvRoot'."
    }
}

& $pythonExecutable -m pip install --upgrade pip | Out-Null
& $pythonExecutable -m pip install -r $requirementsFile | Out-Null

Write-Output $pythonExecutable
