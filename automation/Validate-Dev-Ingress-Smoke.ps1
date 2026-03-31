param(
    [string]$OutputJsonPath = "output/dev-ingress-smoke.json",
    [string]$OutputMarkdownPath = "output/dev-ingress-smoke.md",
    [int]$TimeoutSeconds = 10
)

$ErrorActionPreference = "Stop"

python automation/validate_dev_ingress_smoke.py `
  --output-json $OutputJsonPath `
  --output-markdown $OutputMarkdownPath `
  --timeout-seconds $TimeoutSeconds
