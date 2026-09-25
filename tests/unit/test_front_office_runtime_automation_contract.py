from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]
CLIENT_EXCLUSION = {
    "proofScope": "idea.presentation_backed_downstream_capacity_probe",
    "reasonCode": "NON_CERTIFYING_CAPACITY_PROBE_EXCLUDED",
    "owningIssue": "sgajbi/lotus-idea#1345",
    "claimBoundary": "No Idea downstream-capacity acceptance or full-profile certification",
}


def test_governed_workbench_pin_supports_forwarded_demo_profile() -> None:
    manifest = json.loads(
        (ROOT / "platform-contracts/ci-governance/sibling-source-manifest.v1.json").read_text(
            encoding="utf-8"
        )
    )
    pinned = next(
        entry["revision"] for entry in manifest["sources"] if entry["repository"] == "lotus-workbench"
    )
    checkout = Path(os.environ.get("LOTUS_PRINCIPAL_PROOF_CHECKOUT", ROOT.parent / "lotus-workbench"))
    actual = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    assert actual == pinned, "Platform's governed Workbench checkout must equal its manifest pin"
    for script_name in (
        "Start-LotusFrontOfficeCanonical.ps1",
        "Validate-LotusFrontOfficeCanonical.ps1",
    ):
        script = (checkout / "scripts/live" / script_name).read_text(encoding="utf-8")
        assert "[ValidateSet('full', 'client-demo')][string]$ValidationProfile = 'full'" in script
        if script_name == "Start-LotusFrontOfficeCanonical.ps1":
            assert "-OutputDirectory $canonicalEvidenceRoot" in script


def test_canonical_qa_wrapper_forwards_bounded_profile_and_receipt_boundary() -> None:
    wrapper = (ROOT / "automation" / "Invoke-Canonical-FrontOffice-QA.ps1").read_text(encoding="utf-8")
    assert "[ValidateSet('full', 'client-demo')][string]$ValidationProfile = 'full'" in wrapper
    assert "ValidationProfile = $ValidationProfile" in wrapper
    assert "New-CanonicalQaBringUpArguments" in wrapper
    assert "-Arguments $bringUpArguments" in wrapper
    assert "$arguments.RunValidation = $true" in wrapper
    assert "StartDate = $resolvedReportStartDate" in wrapper
    assert "AsOfDate = $canonicalAsOfDate" in wrapper
    assert (
        "if (-not $BringUp -and -not $Clean -and -not $CleanPlanOnly -and $ValidationProfile -eq 'full')"
        in wrapper
    )
    assert "if (-not $BringUp)" in wrapper
    assert "-Arguments $validationArguments" in wrapper
    assert "validation_profile = $ValidationProfile" in wrapper
    assert "excluded_proofs =" in wrapper
    assert "idea.presentation_backed_downstream_capacity_probe" in wrapper
    assert "sgajbi/lotus-idea#1345" in wrapper
    assert "Assert-CanonicalQaLiveProfile -LiveSummary $liveSummary" in wrapper
    assert "No Idea downstream-capacity acceptance or full-profile certification" in wrapper
    assert "if (-not $BringUp -and $dpmCommandCenterSeedEnabled)" in wrapper
    assert "if ($dpmCommandCenterSeedEnabled)" in wrapper


def test_canonical_qa_wiring_is_non_seeding_for_standalone_and_forwards_full_run() -> None:
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    assert powershell is not None
    script = r"""
$ErrorActionPreference = 'Stop'
$ast = [Management.Automation.Language.Parser]::ParseFile(
  (Join-Path (Get-Location) 'automation/Invoke-Canonical-FrontOffice-QA.ps1'),
  [ref]$null, [ref]$null
)
foreach ($name in @('Resolve-CanonicalQaDpmSeedEnabled', 'New-CanonicalQaBringUpArguments')) {
  $definition = $ast.Find({ param($node)
    $node -is [Management.Automation.Language.FunctionDefinitionAst] -and
    $node.Name -eq $name
  }, $true)
  if (-not $definition) { throw "Shipped function is missing: $name" }
  . ([scriptblock]::Create($definition.Extent.Text))
}
$common = @{
  ProjectsRoot='C:\workspace'
  PortfolioId='PB_SG_GLOBAL_BAL_001'
  BenchmarkCode='BMK_PB_GLOBAL_BALANCED_60_40'
  StartDate='2025-03-31'
  AsOfDate='2026-04-10'
  ValidationProfile='full'
  ScreenshotDirectory='C:\evidence'
  CanonicalEvidenceDirectory='C:\qa-output'
}
$forwarded = New-CanonicalQaBringUpArguments `
  -CommonArguments $common `
  -AiEnvFile '.env.example' `
  -ShouldBuildImages $true `
  -ShouldRequireMainlineSources $true `
  -ShouldCleanCoreState $false `
  -WaitSeconds 321
@{
  standaloneSeedEnabled=(Resolve-CanonicalQaDpmSeedEnabled -IsBringUp $false -SkipRequested $false)
  bringUpSeedEnabled=(Resolve-CanonicalQaDpmSeedEnabled -IsBringUp $true -SkipRequested $false)
  forwarded=$forwarded
  commonWasNotMutated=(-not $common.ContainsKey('RunValidation'))
} | ConvertTo-Json -Depth 5 -Compress
"""
    result = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", script],
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    observed = json.loads(result.stdout)
    assert observed["standaloneSeedEnabled"] is False
    assert observed["bringUpSeedEnabled"] is True
    assert observed["commonWasNotMutated"] is True
    assert observed["forwarded"] == {
        "AsOfDate": "2026-04-10",
        "BenchmarkCode": "BMK_PB_GLOBAL_BALANCED_60_40",
        "BuildImages": True,
        "CanonicalEvidenceDirectory": "C:\\qa-output",
        "LotusAiEnvFile": ".env.example",
        "PortfolioId": "PB_SG_GLOBAL_BAL_001",
        "ProjectsRoot": "C:\\workspace",
        "RequireMainlineSources": True,
        "RunValidation": True,
        "ScreenshotDirectory": "C:\\evidence",
        "SeedWaitSeconds": 321,
        "StartDate": "2025-03-31",
        "ValidationProfile": "full",
    }


def test_canonical_qa_wrapper_forwards_and_records_governed_report_start() -> None:
    wrapper = (ROOT / "automation" / "Invoke-Canonical-FrontOffice-QA.ps1").read_text(encoding="utf-8")
    assert '[string]$ReportStartDate = ""' in wrapper
    assert "StartDate = $resolvedReportStartDate" in wrapper
    assert "AsOfDate = $canonicalAsOfDate" in wrapper
    assert "report_start_date = $resolvedReportStartDate" in wrapper
    assert "report_end_date = $canonicalAsOfDate" in wrapper
    assert "Resolve-CanonicalReportStartDate" in wrapper
    assert "Assert-CanonicalQaLiveWindow -LiveSummary $liveSummary" in wrapper


@pytest.mark.parametrize(
    ("mutation", "expected_success"),
    [
        ("none", True),
        ("wrong_risk_start", False),
        ("wrong_performance_end", False),
        ("missing_advisor", False),
        ("duplicate_risk_start", False),
        ("missing_risk_calculation", False),
        ("wrong_portfolio", False),
    ],
)
def test_canonical_qa_live_window_guard_binds_receipt_to_observed_checks(
    mutation: str, expected_success: bool
) -> None:
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    assert powershell is not None
    script = r"""
$ErrorActionPreference = 'Stop'
$ast = [Management.Automation.Language.Parser]::ParseFile(
  (Join-Path (Get-Location) 'automation/Invoke-Canonical-FrontOffice-QA.ps1'),
  [ref]$null, [ref]$null
)
$definition = $ast.Find({ param($node)
  $node -is [Management.Automation.Language.FunctionDefinitionAst] -and
  $node.Name -eq 'Assert-CanonicalQaLiveWindow'
}, $true)
if (-not $definition) { throw 'Shipped live-window guard is missing' }
. ([scriptblock]::Create($definition.Extent.Text))
$inputValue = [Console]::In.ReadToEnd() | ConvertFrom-Json
try {
  Assert-CanonicalQaLiveWindow -LiveSummary $inputValue.liveSummary `
    -PortfolioId 'PB_SG_GLOBAL_BAL_001' -StartDate '2025-08-25' -EndDate '2026-04-10'
  'accepted'
} catch {
  'refused'
}
"""
    portfolio = "PB_SG_GLOBAL_BAL_001"
    base = f"http://gateway.dev.lotus/api/v1/workbench/{portfolio}"
    window = "report_start_date=2025-08-25&report_end_date=2026-04-10"
    checks = [
        {
            "description": "Performance summary evidence readiness",
            "status": "ready",
            "url": f"{base}/performance/summary?{window}",
        },
        {
            "description": "Risk summary",
            "status": 200,
            "url": f"{base}/risk/summary?{window}",
        },
        {
            "description": "Advisor brief",
            "status": 200,
            "url": f"{base}/performance/advisor-brief?{window}",
        },
    ]
    calculation_checks = [
        {"description": "Performance calculation sanity"},
        {"description": "Risk calculation sanity"},
    ]
    if mutation == "wrong_risk_start":
        checks[1]["url"] = checks[1]["url"].replace("2025-08-25", "2025-03-31")
    elif mutation == "wrong_performance_end":
        checks[0]["url"] = checks[0]["url"].replace("2026-04-10", "2026-04-09")
    elif mutation == "missing_advisor":
        checks.pop()
    elif mutation == "duplicate_risk_start":
        checks[1]["url"] += "&report_start_date=2025-08-25"
    elif mutation == "missing_risk_calculation":
        calculation_checks.pop()
    observed_portfolio = "OTHER_PORTFOLIO" if mutation == "wrong_portfolio" else portfolio
    result = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", script],
        input=json.dumps(
            {
                "liveSummary": {
                    "portfolioId": observed_portfolio,
                    "apiChecks": checks,
                    "calculationChecks": calculation_checks,
                }
            }
        ),
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == ("accepted" if expected_success else "refused")


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("", "2025-03-31"),
        ("2025-08-25", "2025-08-25"),
        ("2026-04-10", "2026-04-10"),
        ("2025-03-30", None),
        ("2026-04-11", None),
        ("2025-02-30", None),
        ("2025-8-25", None),
        ("2025-08-25T00:00:00Z", None),
    ],
)
def test_canonical_report_window_rejects_invalid_or_out_of_seed_range_before_runtime(
    requested: str, expected: str | None
) -> None:
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    assert powershell is not None, "PowerShell is required for the shipped report-window guard"
    script = r"""
$ErrorActionPreference = 'Stop'
$ast = [Management.Automation.Language.Parser]::ParseFile(
  (Join-Path (Get-Location) 'automation/Invoke-Canonical-FrontOffice-QA.ps1'),
  [ref]$null, [ref]$null
)
$definition = $ast.Find({ param($node)
  $node -is [Management.Automation.Language.FunctionDefinitionAst] -and
  $node.Name -eq 'Resolve-CanonicalReportStartDate'
}, $true)
if (-not $definition) { throw 'Shipped report-window guard is missing' }
. ([scriptblock]::Create($definition.Extent.Text))
$inputValue = [Console]::In.ReadToEnd() | ConvertFrom-Json
try {
  $value = Resolve-CanonicalReportStartDate -RequestedDate $inputValue.requested `
    -DatePolicy $inputValue.datePolicy
  @{ status='accepted'; value=$value } | ConvertTo-Json -Compress
} catch {
  @{ status='refused'; value='' } | ConvertTo-Json -Compress
}
"""
    result = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", script],
        input=json.dumps(
            {
                "requested": requested,
                "datePolicy": {
                    "seed_start_date": "2025-03-31",
                    "canonical_as_of_date": "2026-04-10",
                },
            }
        ),
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    observed = json.loads(result.stdout)
    assert observed == {
        "status": "accepted" if expected is not None else "refused",
        "value": expected or "",
    }


def test_invalid_report_window_refuses_before_canonical_qa_output(
    tmp_path: Path,
) -> None:
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    assert powershell is not None
    output_dir = tmp_path / "must-not-be-created"
    result = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(ROOT / "automation" / "Invoke-Canonical-FrontOffice-QA.ps1"),
            "-BringUp",
            "-ReportStartDate",
            "2025-02-30",
            "-OutputDirectory",
            str(output_dir),
        ],
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    assert result.returncode != 0
    assert "not a valid calendar date" in result.stderr
    assert not output_dir.exists()


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        ([], "Full validation must be run with -BringUp"),
        (
            ["-BringUp", "-SkipDpmCommandCenterSeed"],
            "-SkipDpmCommandCenterSeed cannot be combined with -BringUp",
        ),
        (
            ["-BringUp", "-ValidationProfile", "client-demo"],
            "-ValidationProfile client-demo cannot be combined with -BringUp",
        ),
    ],
)
def test_canonical_profile_guards_refuse_before_output_or_runtime(
    tmp_path: Path, arguments: list[str], expected: str
) -> None:
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    assert powershell is not None
    output_dir = tmp_path / "must-not-be-created"
    result = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(ROOT / "automation" / "Invoke-Canonical-FrontOffice-QA.ps1"),
            *arguments,
            "-OutputDirectory",
            str(output_dir),
        ],
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    assert result.returncode != 0
    assert expected in result.stderr
    assert not output_dir.exists()


@pytest.mark.parametrize(
    ("profile", "live_profile", "exclusions", "expected_success"),
    [
        ("full", "full", [], True),
        ("client-demo", "client-demo", [CLIENT_EXCLUSION], True),
        ("client-demo", "full", [CLIENT_EXCLUSION], False),
        ("full", "full", [CLIENT_EXCLUSION], False),
        ("client-demo", "client-demo", [], False),
        (
            "client-demo",
            "client-demo",
            [{**CLIENT_EXCLUSION, "claimBoundary": "Capacity certified"}],
            False,
        ),
    ],
)
def test_canonical_qa_live_profile_guard_rejects_cross_profile_or_weakened_evidence(
    profile: str,
    live_profile: str,
    exclusions: list[dict[str, str]],
    expected_success: bool,
) -> None:
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    assert powershell is not None, "PowerShell is required for the shipped profile guard test"
    script = r"""
$ErrorActionPreference = 'Stop'
$ast = [Management.Automation.Language.Parser]::ParseFile(
  (Join-Path (Get-Location) 'automation/Invoke-Canonical-FrontOffice-QA.ps1'),
  [ref]$null, [ref]$null
)
$definition = $ast.Find({ param($node)
  $node -is [Management.Automation.Language.FunctionDefinitionAst] -and
  $node.Name -eq 'Assert-CanonicalQaLiveProfile'
}, $true)
if (-not $definition) { throw 'Shipped QA profile guard is missing' }
. ([scriptblock]::Create($definition.Extent.Text))
$inputValue = [Console]::In.ReadToEnd() | ConvertFrom-Json
$expected = @()
if ($inputValue.profile -eq 'client-demo') {
  $expected = @([pscustomobject]@{
    proofScope='idea.presentation_backed_downstream_capacity_probe'
    reasonCode='NON_CERTIFYING_CAPACITY_PROBE_EXCLUDED'
    owningIssue='sgajbi/lotus-idea#1345'
    claimBoundary='No Idea downstream-capacity acceptance or full-profile certification'
  })
}
try {
  Assert-CanonicalQaLiveProfile -LiveSummary $inputValue.liveSummary `
    -ValidationProfile $inputValue.profile -ExpectedExclusions $expected
  'accepted'
} catch {
  'refused'
}
"""
    result = subprocess.run(
        [powershell, "-NoProfile", "-Command", script],
        input=json.dumps(
            {
                "profile": profile,
                "liveSummary": {
                    "validationProfile": live_profile,
                    "excludedProofs": exclusions,
                },
            }
        ),
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == ("accepted" if expected_success else "refused")


def test_platform_qa_core_gate_uses_canonical_front_office_verifier() -> None:
    qa_matrix = json.loads((ROOT / "automation" / "qa-matrix.json").read_text(encoding="utf-8"))
    core_entry = next(item for item in qa_matrix["repositories"] if item["repo"] == "lotus-core")
    custom_checks = core_entry["checks"]["custom_checks"]
    canonical_check = next(
        item for item in custom_checks if item["id"] == "canonical-front-office-analytics-maturity"
    )

    command = canonical_check["command"]
    assert "front_office_portfolio_seed.py" in command
    assert "--verify-only" in command
    assert "PB_SG_GLOBAL_BAL_001" in command
    assert "BMK_PB_GLOBAL_BALANCED_60_40" not in command
    assert "core_seeded_analytics_maturity_validation.py" not in command


def test_front_office_qa_wrapper_is_wired_into_platform_profile_and_docs() -> None:
    wrapper = (ROOT / "automation" / "Invoke-Canonical-FrontOffice-QA.ps1").read_text(encoding="utf-8")
    profiles_doc = json.loads((ROOT / "automation" / "task-profiles.json").read_text(encoding="utf-8"))
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    automation_guide = (ROOT / "automation" / "docs" / "Automation-Guide.md").read_text(encoding="utf-8")
    local_dev_runbook = (ROOT / "docs" / "operations" / "Local Development Runbook.md").read_text(
        encoding="utf-8"
    )
    engineering_context = (ROOT / "context" / "LOTUS-ENGINEERING-CONTEXT.md").read_text(encoding="utf-8")
    skill_routing_map = (ROOT / "context" / "LOTUS-SKILL-ROUTING-MAP.md").read_text(encoding="utf-8")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for operator_guide in (automation_readme, automation_guide, local_dev_runbook):
        assert "DPM_CORE_CONTEXT_INCOMPLETE" in operator_guide
        assert "sgajbi/lotus-manage#711" in operator_guide
        assert "Core DPM source-readiness families must be fixed" not in operator_guide
    docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    wiki_home = (ROOT / "wiki" / "Home.md").read_text(encoding="utf-8")
    wiki_overview = (ROOT / "wiki" / "Overview.md").read_text(encoding="utf-8")
    wiki_platform_surfaces = (ROOT / "wiki" / "Platform-Surfaces.md").read_text(encoding="utf-8")
    wiki_sidebar = (ROOT / "wiki" / "_Sidebar.md").read_text(encoding="utf-8")
    hosts_helper = (ROOT / "automation" / "Apply-DevIngressHosts-Elevated.ps1").read_text(encoding="utf-8")
    directory_map = (ROOT / "automation" / "docs" / "Directory-Map.md").read_text(encoding="utf-8")
    profile_reference = (ROOT / "automation" / "docs" / "Profile-Reference.md").read_text(encoding="utf-8")

    assert "Start-LotusFrontOfficeCanonical.ps1" in wrapper
    assert "Validate-LotusFrontOfficeCanonical.ps1" in wrapper
    assert "Stop-LotusFrontOfficeCanonical.ps1" in wrapper
    assert "Invoke-DpmCommandCenterSeed.ps1" in wrapper
    assert "PB_SG_GLOBAL_BAL_001" in wrapper
    assert "output/front-office-qa" in wrapper
    assert "[string]$ScreenshotDirectory" in wrapper
    assert "screenshot_directory" in wrapper
    assert "runtime_transcript" in wrapper
    assert "canonical-front-office-qa-$timestamp.log" in wrapper
    assert "latest.log" in wrapper
    assert "Start-Transcript" in wrapper
    assert "Stop-Transcript" in wrapper
    assert "output\\playwright\\live-canonical" in wrapper
    assert "live-validation-summary.json" in wrapper
    assert "canonical_contract" in wrapper
    assert "canonicalContract" in wrapper
    assert "[switch]$Clean" in wrapper
    assert "[switch]$CleanPlanOnly" in wrapper
    assert "[switch]$BuildImages" in wrapper
    assert "[switch]$RequireMainlineSources" in wrapper
    assert "RequireMainlineSources requires -BringUp" in wrapper
    assert "if ($RequireMainlineSources -and -not $BuildImages)" in wrapper
    assert "$BuildImages = $true" in wrapper
    assert "require_mainline_sources = [bool]$RequireMainlineSources" in wrapper
    assert "mainline_source_preflight = $null" in wrapper
    assert "$summary.mainline_source_preflight = [ordered]@{" in wrapper
    assert "Invoke-MainlineSourceProvenancePreflight" in wrapper
    assert "mainline-source-provenance.mjs" in wrapper
    assert "failed before cleanup, Docker build, seed, or validation was started" in wrapper
    assert "mainline-source-provenance-preflight-latest.json" in wrapper
    assert '$summary.steps += "mainline-source-preflight"' in wrapper
    assert "$arguments.RequireMainlineSources = $true" in wrapper
    assert "-not $RequireMainlineSources -or $certifiedSourcePreflightPassed" in wrapper
    assert "Require mainline sources:" in wrapper
    assert "Mainline source preflight:" in wrapper
    assert "[switch]$RemoveImages" in wrapper
    assert "[switch]$IncludeLotusIdea" not in wrapper
    assert "[switch]$SkipDpmCommandCenterSeed" in wrapper
    assert "canonical_docker_ownership.py" in wrapper
    assert "Get-CanonicalDockerCleanupPlan" in wrapper
    assert "Assert-NoOwnedDockerArtifacts" in wrapper
    assert "docker_ownership_policy" in wrapper
    assert "docker_cleanup_plan_path" in wrapper
    assert "ownership_provenance" in wrapper
    assert "ownership_conflicts" in wrapper
    assert "repository_checkout=" in wrapper
    assert "Canonical clean blocked by Compose ownership conflicts" in wrapper
    assert "Get-LotusDockerArtifacts" not in wrapper
    assert "Remove-LotusDockerArtifacts" not in wrapper
    assert '$_ -match "^(lotus|pbwm|performance)"' not in wrapper
    assert "docker rm -f" not in wrapper
    assert "docker volume rm" not in wrapper
    assert "docker image rm -f" not in wrapper
    assert "Invoke-LotusIdeaDockerBringUp" not in wrapper
    assert "Invoke-LotusIdeaValidation" in wrapper
    assert "Assert-NoUnownedHostPortListener" not in wrapper
    assert "docker compose up -d --build" not in wrapper
    assert '$composeArguments = @("compose", "up", "-d")' not in wrapper
    assert '$composeArguments += "--build"' not in wrapper
    assert "preserving governed runtime started and seeded by canonical Workbench startup" in wrapper
    assert "Stop-Process" not in wrapper
    assert '$summary.status = "failed"' in wrapper
    assert "http://127.0.0.1:8330/health/ready" in wrapper
    assert "http://idea.dev.lotus/health/ready" in wrapper
    assert "lotus_idea" in wrapper
    assert "docker_before" in wrapper
    assert "docker_after_clean" in wrapper
    assert "Docker Evidence" in wrapper
    assert "include_lotus_idea = $true" in wrapper
    assert "canonical_core_demo_pack_enabled = $false" in wrapper
    assert "Canonical core demo pack enabled" in wrapper
    assert "dpm_command_center_seed_summary" in wrapper
    assert "DPM command-center seed status" in wrapper
    assert "Screenshot directory" in wrapper
    assert "Runtime transcript" in wrapper
    assert "Canonical contract:" in wrapper
    assert "Governed by:" in wrapper
    assert '$summary.steps -contains "bring-up" -or $summary.steps -contains "validate"' in wrapper
    assert "validation did not produce a live summary" in wrapper
    assert "validation summary is stale" in wrapper
    assert "Apply-DevIngressHosts-Elevated.ps1" in automation_readme
    assert "Apply-DevIngressHosts-Elevated.ps1" in automation_guide
    assert "Sync-Dev-Ingress-Hosts.ps1" in hosts_helper
    assert "-Apply" in hosts_helper
    assert "ipconfig /flushdns" in hosts_helper
    assert "Start-Process" in hosts_helper
    assert "-Verb RunAs" in hosts_helper

    dpm_seed = (ROOT / "automation" / "Invoke-DpmCommandCenterSeed.ps1").read_text(encoding="utf-8")
    assert "canonical-front-office-demo-data-contract.json" in dpm_seed
    assert "dpm_command_center" in dpm_seed
    assert "MANDATE_PB_SG_GLOBAL_BAL_001" not in dpm_seed
    assert "refresh-from-core" in dpm_seed
    assert "/api/v1/dpm/monitoring/run-once" in dpm_seed
    assert "manage-monitoring-run-once" in dpm_seed
    assert "resolve_canonical_cash_evidence.py" in dpm_seed
    assert "gateway-date-aligned-cash-evidence" in dpm_seed
    assert "cash_weight = [string]$summary.cash_evidence.normalized_cash_weight" in dpm_seed
    assert 'cash_weight = "0.05"' not in dpm_seed
    assert "manage-campaign-definition-upsert" in dpm_seed
    assert "function Upsert-CampaignDefinition" in dpm_seed
    assert "Existing Manage campaign definition" in dpm_seed
    assert "Refreshing the seed-owned definition" in dpm_seed
    assert "Assert-CampaignDefinitionMatchesSeed" in dpm_seed
    assert "DpmPortfolioUniverseCandidate:v1" in dpm_seed
    assert "campaignCandidateSelectionBasis" in dpm_seed
    assert "selection_basis" in dpm_seed
    assert "source-owned selection_basis evidence" in dpm_seed
    assert "campaign_candidate_selection_basis" in dpm_seed
    assert "Supersede-LegacyCampaignDefinitions" in dpm_seed
    assert "manage-campaign-definition-supersede-legacy" in dpm_seed
    assert "source-owned candidate selection-basis evidence" in dpm_seed
    assert "/api/v1/mandates/by-portfolio/$resolvedPortfolioId" in dpm_seed
    assert "/api/v1/dpm/command-center/mandates/by-portfolio/$resolvedPortfolioId" in dpm_seed
    assert "/api/v1/dpm/command-center/waves/campaign-definitions" in dpm_seed
    assert "/api/v1/dpm/command-center/waves/campaign-discovery" in dpm_seed
    assert "dpm-command-center-seed-latest.json" in dpm_seed
    assert "posture_checks" in dpm_seed
    assert "ready-populated-command-center" in dpm_seed
    assert "gateway-command-center-partial-posture" in dpm_seed
    assert "gateway-command-center-empty-posture" in dpm_seed
    assert "DPM command-center posture validation failed" in dpm_seed
    assert "New-CanonicalOutcomeReviewGatewayBody" in dpm_seed
    assert "gateway-outcome-review-create" in dpm_seed
    assert "gateway-outcome-review-list" in dpm_seed
    assert "canonical-dpm-outcome-review:${resolvedPortfolioId}:${resolvedAsOfDate}" in dpm_seed
    assert "/api/v1/dpm/command-center/outcome-reviews" in dpm_seed
    assert '-CorrelationId "corr-canonical-dpm-outcome-review-$resolvedPortfolioId-' in dpm_seed
    assert "-ExtraHeaders @{" in dpm_seed
    assert '"Idempotency-Key" = $outcomeReviewIdempotencyKey' in dpm_seed
    assert "limit=50" in dpm_seed
    assert "$outcomeReviewRebalanceRunId" in dpm_seed
    assert "$outcomeReviewWaveId" in dpm_seed
    assert "gateway_outcome_review_verified_item" in dpm_seed
    assert "observedRunId -eq $outcomeReviewRebalanceRunId" in dpm_seed
    assert "observedWaveId -eq $outcomeReviewWaveId" in dpm_seed
    assert "Assert-OutcomeReviewPageContainsSeed" in dpm_seed
    assert "CanonicalDpmOutcomeExpectedEvidence" in dpm_seed
    assert "DpmRealizedOutcomeSnapshot:v1" in dpm_seed
    assert '"canonical-dpm-outcome-review:${resolvedPortfolioId}:${resolvedAsOfDate}:" +' in dpm_seed
    assert "[string]$contract.contract_version" in dpm_seed
    assert "outcome_review_idempotency_key = $outcomeReviewIdempotencyKey" in dpm_seed
    assert "[switch]$PreflightOnly" in dpm_seed
    assert "Invoke-ManageWriteAuthorizationPreflight" in dpm_seed
    assert "manage-refresh-authorization-preflight" in dpm_seed
    assert "action_register_workflow_response" in dpm_seed
    assert "manage-action-register-workflow-posture" in dpm_seed
    assert "$workflowRequiresReview" in dpm_seed
    assert "manage-action-register-workflow-not-required" in dpm_seed
    assert "DPM_WORKFLOW_NOT_REQUIRED_FOR_RUN_STATUS" in dpm_seed
    assert "does not fabricate an approval decision" in dpm_seed
    assert "authorized_validation_rejected_side_effect_free_probe" in dpm_seed
    assert "authorized_unexpected_success" not in dpm_seed
    assert "observed unexpected 2xx success" in dpm_seed
    assert "may have reached the write operation" in dpm_seed
    assert "$ErrorRecord.ErrorDetails" in dpm_seed
    assert "$errorDetails.Message" in dpm_seed
    assert "ReadAsStringAsync().GetAwaiter().GetResult()" in dpm_seed
    assert "New-ManageRequestHeaders" in dpm_seed
    assert "$resolvedCampaignTenantId" in dpm_seed
    assert "$resolvedWorkbenchCallerTenantId" in dpm_seed
    assert "workbench_caller_tenant_id = $resolvedWorkbenchCallerTenantId" in dpm_seed
    assert "$resolvedTenantId -cne $resolvedWorkbenchCallerTenantId" in dpm_seed
    assert "-TenantId $resolvedWorkbenchCallerTenantId" in dpm_seed
    assert "-Headers $gatewayHeaders" in dpm_seed
    assert "&tenant_id=$resolvedTenantId" not in dpm_seed
    assert "campaign_tenant_id = $resolvedCampaignTenantId" in dpm_seed
    assert '"X-Role" = $manageSeedRole' in dpm_seed
    assert '"X-Service-Identity" = $manageSeedServiceIdentity' in dpm_seed
    assert '"X-Capabilities" = $manageSeedCapability' in dpm_seed
    assert '$manageSeedCapability = "manage.write"' in dpm_seed
    assert "service_identity = $manageSeedServiceIdentity" in dpm_seed
    assert "capabilities = @($manageSeedCapability)" in dpm_seed
    assert "preflight_only = [bool]$PreflightOnly" in dpm_seed
    assert '-Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-refresh-' in dpm_seed
    assert '-Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-monitoring-' in dpm_seed
    assert (
        '-Headers (New-ManageRequestHeaders -CorrelationId "corr-canonical-dpm-health-recalculate-'
        in dpm_seed
    )
    assert "-Headers (New-ManageRequestHeaders `" in dpm_seed
    assert "corr-canonical-dpm-action-register-review-" in dpm_seed
    assert "corr-canonical-dpm-campaign-upsert-" in dpm_seed
    assert "corr-canonical-dpm-campaign-supersede-" in dpm_seed
    assert dpm_seed.count("-TenantId $resolvedCampaignTenantId") == 3
    assert dpm_seed.count("-Headers $campaignHeaders") == 4

    action_register = dpm_seed.split("recording stateful action-register simulation evidence", 1)[1].split(
        "persisting source-backed campaign definition", 1
    )[0]
    assert "$resolvedActionRegisterTenantId = Resolve-ActionRegisterSourceTenant `" in dpm_seed
    assert "-Portfolio $contract.portfolio `" in dpm_seed
    assert "-PortfolioId $resolvedPortfolioId" in dpm_seed
    assert 'action_register_tenant_authority = "portfolio.source_tenant_id"' in dpm_seed
    assert "tenant_id = $resolvedActionRegisterTenantId" in action_register
    assert action_register.count("-TenantId $resolvedActionRegisterTenantId") == 3

    cash_preflight = dpm_seed.index("resolving date-aligned canonical cash evidence before persistent writes")
    persistent_refresh = dpm_seed.index("refreshing $resolvedMandateId from lotus-core through lotus-manage")
    assert cash_preflight < persistent_refresh
    assert "Assert-MandateHealthMatchesSeed" in dpm_seed
    assert "manage-mandate-health-date-match" in dpm_seed
    assert "gateway-mandate-health-date-match" in dpm_seed
    assert dpm_seed.index("Manage mandate-health recalculation") < dpm_seed.index(
        "manage-mandate-health-date-match"
    )
    assert dpm_seed.index("Gateway command-center mandate health") < dpm_seed.index(
        "gateway-mandate-health-date-match"
    )

    profiles = {profile["name"]: profile for profile in profiles_doc["profiles"]}
    qa_profile_commands = {task["command"] for task in profiles["qa-platform-readiness"]["tasks"]}
    assert (
        "powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp"
        in qa_profile_commands
    )
    clean_core_profile_commands = {
        task["command"] for task in profiles["qa-platform-readiness-clean-core"]["tasks"]
    }
    assert (
        "powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 "
        "-BringUp -CleanCoreState -LotusAiEnvFile .env.example -SeedWaitSeconds 1200"
        in clean_core_profile_commands
    )
    clean_core_build_profile_commands = {
        task["command"] for task in profiles["qa-platform-readiness-clean-core-build"]["tasks"]
    }
    assert (
        "powershell -ExecutionPolicy Bypass -File automation/Invoke-Canonical-FrontOffice-QA.ps1 "
        "-BringUp -CleanCoreState -BuildImages -LotusAiEnvFile .env.example -SeedWaitSeconds 1200"
        in clean_core_build_profile_commands
    )

    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp" in automation_readme
    assert "`qa-platform-readiness-clean-core`" in automation_readme
    assert "`qa-platform-readiness-clean-core-build`" in automation_readme
    assert "-LotusAiEnvFile .env.example" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 `" in automation_readme
    # A documented example must not carry a personal checkout path: it fails
    # for every other reader, and an absolute path suppresses the link and
    # path checks that would otherwise catch rot beneath it.
    assert "$screenshotDirectory = Join-Path ([IO.Path]::GetTempPath())" in automation_readme
    assert "-BringUp -ScreenshotDirectory $screenshotDirectory" in automation_readme
    assert "<temp-dir>" not in automation_readme
    assert "Users\\Sandeep" not in automation_readme
    assert "canonical contract identity and version" in automation_readme
    assert "calculationChecks" in automation_readme
    assert "panelClassifications" in automation_readme
    assert "runtime transcript" in automation_readme
    assert "DPM command-center seed" in automation_readme
    assert "-IncludeLotusIdea" not in automation_readme
    assert "source-backed DPM campaign definition" in automation_readme
    assert "source-owned selection-basis evidence" in automation_readme
    assert "DpmPortfolioUniverseCandidate:v1" in automation_readme
    assert "DPM_CORE_CONTEXT_INCOMPLETE" in automation_readme
    assert "sgajbi/lotus-core#840" in automation_readme
    assert "Inspect the admitted request" in automation_guide
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages" in automation_readme
    assert (
        "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -RequireMainlineSources" in automation_readme
    )
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -RemoveImages" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly" in automation_readme
    assert "cleanup-plan-latest.json" in automation_readme
    assert "name is never sufficient" in automation_readme
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp" in automation_guide
    assert "Canonical front-office screenshot pack" in automation_guide
    assert "caller-resolved absolute screenshot directory" in automation_guide
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -Clean -BringUp -BuildImages" in automation_guide
    assert (
        "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -RequireMainlineSources" in automation_guide
    )
    assert "-BringUp -RequireMainlineSources" in engineering_context
    assert "require_mainline_sources" in engineering_context
    assert "mainline_source_preflight" in engineering_context
    assert "forces image builds" in engineering_context
    assert "-BringUp -RequireMainlineSources" in skill_routing_map
    assert "mainline-certified front-office proof" in skill_routing_map
    assert (
        "automation/Invoke-Canonical-FrontOffice-QA.ps1 -BringUp -RequireMainlineSources" in local_dev_runbook
    )
    assert "require_mainline_sources" in local_dev_runbook
    assert "mainline_source_preflight" in local_dev_runbook
    assert "already-running canonical stack" in local_dev_runbook
    assert "forces image builds" in automation_guide
    assert "mainline_source_preflight" in automation_guide
    assert "must not tear down an existing canonical stack" in (
        ROOT / "codex" / "skills" / "platform-automation-ops" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "automation/Invoke-Canonical-FrontOffice-QA.ps1 -CleanPlanOnly" in automation_guide
    assert "name-prefix cleanup is forbidden" in automation_guide
    assert "canonical_orphan_retirement.py" in automation_guide
    assert "-IncludeLotusIdea" not in automation_guide
    assert "lotus-idea" in automation_guide
    assert "DEMO_DATA_PACK_ENABLED=false" in automation_guide
    assert "latest.log" in automation_guide
    assert "DPM seed" in automation_guide
    assert "Standalone `client-demo` leaves DPM seeding disabled" in automation_guide
    assert "Invoke-Canonical-FrontOffice-QA.ps1" in directory_map
    assert "Invoke-DpmCommandCenterSeed.ps1" in directory_map
    assert "`qa-platform-readiness`" in profile_reference
    assert "`qa-platform-readiness-clean-core`" in profile_reference
    assert "`qa-platform-readiness-clean-core-build`" in profile_reference
    assert "Governed front-office runtime bring-up and populated UI proof" in profile_reference
    assert "Reader Paths" in root_readme
    assert "Human approval reviews are optional" in root_readme
    assert "canonical private-banking seed data excludes the demo pack by default" in root_readme
    assert "`lotus-idea` is included by default in canonical platform QA" in root_readme
    assert "Canonical front-office proof and demo boundaries" in docs_readme
    assert "Documentation in this directory must stay implementation-backed" in docs_readme
    assert "Reader Paths" in wiki_home
    assert "`lotus-idea` runtime" in wiki_home
    assert "the demo pack is not part of canonical PB seed by default" in wiki_home
    assert "Included by default in canonical platform QA" in wiki_overview
    assert "Canonical front-office QA includes `lotus-idea` by default" in wiki_platform_surfaces
    assert "## Product And Demo" in wiki_sidebar
    assert "## Operations" in wiki_sidebar
    assert "## Governance" in wiki_sidebar


def test_front_office_docs_distinguish_governed_ui_qa_from_backend_runtime_qa() -> None:
    automation_readme = (ROOT / "automation" / "README.md").read_text(encoding="utf-8")
    automation_guide = (ROOT / "automation" / "docs" / "Automation-Guide.md").read_text(encoding="utf-8")

    for content in (automation_readme, automation_guide):
        assert "governed `lotus-workbench` runtime" in content
        assert (
            "backend/runtime QA readiness automation" in content
            or "Backend/runtime QA readiness validation" in content
        )
        assert "Invoke-Platform-QA.ps1 -BringUp" in content
        assert "Invoke-Canonical-FrontOffice-QA.ps1 -BringUp" in content
