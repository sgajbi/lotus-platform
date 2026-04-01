param(
    [string]$SmokeJsonPath = "output/dev-ingress-smoke.json",
    [string]$StagedHostsPath = "output/hosts-preview/hosts.merged",
    [string]$OutputJsonPath = "output/dev-ingress-status.json",
    [string]$OutputMarkdownPath = "output/dev-ingress-status.md"
)

$ErrorActionPreference = "Stop"

python automation/explain_dev_ingress_status.py `
  --smoke-json-path $SmokeJsonPath `
  --staged-hosts-path $StagedHostsPath `
  --output-json $OutputJsonPath `
  --output-markdown $OutputMarkdownPath

exit $LASTEXITCODE
