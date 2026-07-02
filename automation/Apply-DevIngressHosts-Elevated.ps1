param(
  [switch]$NoPause
)

$ErrorActionPreference = "Stop"

$platformRoot = Split-Path -Parent $PSScriptRoot
$syncScript = Join-Path $PSScriptRoot "Sync-Dev-Ingress-Hosts.ps1"

function Test-IsAdministrator {
  $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = [Security.Principal.WindowsPrincipal]::new($identity)
  return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-HostsApply {
  Set-Location -LiteralPath $platformRoot
  & $syncScript -Apply
  if ($LASTEXITCODE -ne 0) {
    throw "Sync-Dev-Ingress-Hosts.ps1 -Apply failed with exit code $LASTEXITCODE."
  }
  ipconfig /flushdns | Out-Host
}

if (Test-IsAdministrator) {
  Invoke-HostsApply
  if (-not $NoPause) {
    Read-Host "Dev ingress hosts applied. Press Enter to close"
  }
  return
}

$pauseLine = if ($NoPause) { "" } else { "Read-Host 'Dev ingress hosts applied. Press Enter to close';" }
$command = @"
`$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath '$platformRoot'
& '$syncScript' -Apply
if (`$LASTEXITCODE -ne 0) { throw "Sync-Dev-Ingress-Hosts.ps1 -Apply failed with exit code `$LASTEXITCODE." }
ipconfig /flushdns
$pauseLine
"@

$encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
Start-Process -FilePath "powershell.exe" `
  -Verb RunAs `
  -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $encodedCommand)
