param(
    [string]$ReposPath = "automation/repos.json",
    [string]$OutputJsonPath = "output/shared-infra-ownership.json",
    [string]$OutputMarkdownPath = "output/shared-infra-ownership.md"
)

$ErrorActionPreference = "Stop"

python automation/validate_shared_infra_ownership.py `
  --repos-path $ReposPath `
  --output-json $OutputJsonPath `
  --output-markdown $OutputMarkdownPath
