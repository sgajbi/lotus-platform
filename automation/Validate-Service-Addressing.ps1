param(
    [string]$ReposPath = "automation/repos.json",
    [string]$OutputJsonPath = "output/service-addressing.json",
    [string]$OutputMarkdownPath = "output/service-addressing.md"
)

$ErrorActionPreference = "Stop"

python automation/validate_service_addressing.py `
  --repos-path $ReposPath `
  --output-json $OutputJsonPath `
  --output-markdown $OutputMarkdownPath
