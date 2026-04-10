param(
    [string]$VenvPath = ".venv-platform-automation",
    [string]$RequirementsPath = "automation/requirements.platform-automation.lock.txt"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$venvRoot = Join-Path $repoRoot $VenvPath
$requirementsFile = Join-Path $repoRoot $RequirementsPath

$windowsPython = Join-Path $venvRoot "Scripts/python.exe"
$posixPython = Join-Path $venvRoot "bin/python"
$pythonExecutable = $null

if (Test-Path $windowsPython) {
    $pythonExecutable = $windowsPython
}
elseif (Test-Path $posixPython) {
    $pythonExecutable = $posixPython
}

if (-not (Test-Path $pythonExecutable)) {
    python -m venv $venvRoot

    if (Test-Path $windowsPython) {
        $pythonExecutable = $windowsPython
    }
    elseif (Test-Path $posixPython) {
        $pythonExecutable = $posixPython
    }
    else {
        throw "Unable to resolve the platform automation Python executable from '$venvRoot'."
    }
}

& $pythonExecutable -m pip install --upgrade pip | Out-Null
& $pythonExecutable -m pip install -r $requirementsFile | Out-Null

Write-Output $pythonExecutable
