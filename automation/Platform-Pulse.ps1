param(
  [string]$ConfigPath = "automation/repos.json",
  [switch]$IncludeConformance
)

$ErrorActionPreference = "Stop"

powershell -ExecutionPolicy Bypass -File "automation/Sync-Repos.ps1" -ConfigPath $ConfigPath
powershell -ExecutionPolicy Bypass -File "automation/PR-Monitor.ps1" -ConfigPath $ConfigPath -IncludeChecks

if ($IncludeConformance) {
  powershell -ExecutionPolicy Bypass -File "automation/Validate-Backend-Standards.ps1"
  powershell -ExecutionPolicy Bypass -File "automation/Validate-OpenAPI-Conformance.ps1"
  powershell -ExecutionPolicy Bypass -File "automation/Validate-Domain-Vocabulary.ps1"
  powershell -ExecutionPolicy Bypass -File "automation/Validate-Shared-Infrastructure-Ownership.ps1"
  powershell -ExecutionPolicy Bypass -File "automation/Validate-Service-Addressing.ps1"
  powershell -ExecutionPolicy Bypass -File "automation/Verify-Repo-Metadata.ps1"
}

