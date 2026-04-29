param(
  [string]$VectorsPath = "platform-contracts/rounding-golden-vectors.json",
  [string]$OutputJson = "output/rounding-consistency-report.json",
  [string]$OutputMarkdown = "output/rounding-consistency-report.md"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$projectsRoot = Resolve-Path (Join-Path $root "..")

$pythonScript = @'
import json
import sys
from pathlib import Path

projects_root = Path(sys.argv[1])
vectors_path = Path(sys.argv[2])

targets = {
    "pas": ("lotus-core", "src/services/query_service/app", "precision_policy"),
    "lotus-performance": ("lotus-performance", "app", "precision_policy"),
    "dpm": ("lotus-manage", "src/core", "precision_policy"),
    "ras": ("lotus-report", "src/app", "precision_policy"),
    "aea": ("lotus-gateway", "src/app", "precision_policy"),
}

vectors_payload = json.loads(vectors_path.read_text(encoding="utf-8"))
vectors = vectors_payload["vectors"]
policy_version = vectors_payload["policy_version"]

results = {}
for name, (repo, rel_path, module_name) in targets.items():
    module_path = projects_root / repo / rel_path
    sys.path.insert(0, str(module_path))
    mod = __import__(module_name)
    service_results = {}
    for semantic, values in vectors.items():
        quantizer = getattr(mod, f"quantize_{semantic}")
        service_results[semantic] = [str(quantizer(value)) for value in values]
    service_results["rounding_policy_version"] = str(
        getattr(mod, "ROUNDING_POLICY_VERSION", "MISSING")
    )
    results[name] = service_results

baseline_service = next(iter(results.values()))
baseline = {k: v for k, v in baseline_service.items() if k != "rounding_policy_version"}
consistency_failures = []
policy_failures = []
for service_name, values in results.items():
    if values.get("rounding_policy_version") != policy_version:
        policy_failures.append(
            f"{service_name}: expected policy_version={policy_version}, found={values.get('rounding_policy_version')}"
        )
    for semantic, expected in baseline.items():
        actual = values.get(semantic)
        if actual != expected:
            consistency_failures.append(
                f"{service_name}:{semantic}: expected={expected} actual={actual}"
            )

consistent = not consistency_failures and not policy_failures

print(
    json.dumps(
        {
            "consistent": consistent,
            "policy_version": policy_version,
            "baseline": baseline,
            "results": results,
            "consistency_failures": consistency_failures,
            "policy_failures": policy_failures,
        },
        indent=2,
    )
)
'@

$tmpPy = Join-Path $env:TEMP "pbwm-rounding-consistency.py"
Set-Content -Path $tmpPy -Value $pythonScript
$jsonRaw = python $tmpPy "$projectsRoot" "$root/$VectorsPath"
$null = Remove-Item $tmpPy -ErrorAction SilentlyContinue
$jsonData = $jsonRaw | ConvertFrom-Json

$outputObject = [ordered]@{
  generated_at = (Get-Date).ToUniversalTime().ToString("o")
  consistent = [bool]$jsonData.consistent
  policy_version = [string]$jsonData.policy_version
  baseline = $jsonData.baseline
  results = $jsonData.results
  consistency_failures = $jsonData.consistency_failures
  policy_failures = $jsonData.policy_failures
}

$outputDir = Split-Path $OutputJson -Parent
if ($outputDir -and -not (Test-Path $outputDir)) {
  New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
}

$outputObject | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputJson

$lines = @()
$lines += "# Rounding Consistency Report"
$lines += ""
$lines += "- generated_at: $($outputObject.generated_at)"
$lines += "- consistent: $($outputObject.consistent)"
$lines += "- policy_version: $($outputObject.policy_version)"
$lines += ""
$lines += "| service | policy_version | money | price | fx_rate | quantity | performance | risk |"
$lines += "|---|---|---|---|---|---|---|---|"
foreach ($svc in $outputObject.results.PSObject.Properties.Name) {
  $r = $outputObject.results.$svc
  $lines += "| $svc | $($r.rounding_policy_version) | $($r.money -join ', ') | $($r.price -join ', ') | $($r.fx_rate -join ', ') | $($r.quantity -join ', ') | $($r.performance -join ', ') | $($r.risk -join ', ') |"
}
if ($outputObject.consistency_failures.Count -gt 0) {
  $lines += ""
  $lines += "## Consistency Failures"
  foreach ($item in $outputObject.consistency_failures) {
    $lines += "- $item"
  }
}
if ($outputObject.policy_failures.Count -gt 0) {
  $lines += ""
  $lines += "## Policy Version Failures"
  foreach ($item in $outputObject.policy_failures) {
    $lines += "- $item"
  }
}
$lines -join "`n" | Set-Content -Path $OutputMarkdown

if (-not $outputObject.consistent) {
  Write-Error "Rounding consistency check failed."
}

Write-Host "Generated $OutputJson and $OutputMarkdown"
