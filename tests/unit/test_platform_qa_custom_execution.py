"""Execute shipped QA dispatch/functions without HTTP, Docker or the full QA sweep."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "automation" / "Invoke-Platform-QA.ps1"
VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"


@pytest.fixture
def core(tmp_path: Path) -> Path:
    """A non-sibling repository with spaces and a real isolated Python interpreter."""
    root = tmp_path / "configured repositories" / "Core with spaces"
    root.mkdir(parents=True)
    venv.EnvBuilder(with_pip=False).create(root / ".venv")
    (root / ".python-version").write_text(VERSION, encoding="utf-8")
    development = root / "scripts" / "development"
    development.mkdir(parents=True)
    # Stand-in for Core's separately governed launcher; exercise cwd, argv and exit
    # propagation through real processes, without copying first-party implementation.
    (development / "repository_python.py").write_text(
        "import pathlib, runpy, sys\n"
        "sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))\n"
        "assert sys.argv[1] in ('-c', 'tools/front_office_portfolio_seed.py')\n"
        "if sys.argv[1] == '-c':\n"
        "    exec(sys.argv[2])\n"
        "else:\n"
        "    sys.argv = sys.argv[1:]\n"
        "    runpy.run_path(sys.argv[0], run_name='__main__')\n",
        encoding="utf-8",
    )
    tools = root / "tools"
    tools.mkdir()
    (tools / "__init__.py").write_text("", encoding="utf-8")
    (tools / "front_office_portfolio_seed.py").write_text(
        "import json, os, pathlib, sys\n"
        "if __name__ == '__main__':\n"
        "    assert '--verify-only' in sys.argv\n"
        "    assert not set(sys.argv) & {'--ingest-only', '--force-ingest', '--target-portfolio-replay', '--reprocess-after-ingest'}\n"
        "    print(json.dumps({'cwd': str(pathlib.Path.cwd()), 'argv': sys.argv[1:], 'platform': os.environ['LOTUS_PLATFORM_REPO']}))\n"
        "    sys.exit(int(os.environ.get('QA_TEST_CHILD_EXIT', '0')))\n",
        encoding="utf-8",
    )
    return root


def _check() -> dict:
    matrix = json.loads((ROOT / "automation" / "qa-matrix.json").read_text())
    return next(
        entry for entry in matrix["repositories"] if entry["repo"] == "lotus-core"
    )["checks"]["custom_checks"][0]


def _run(
    core: Path,
    check: dict | None = None,
    *,
    child_exit: int = 0,
    dry_run=False,
    powershell_override=None,
    additional_checks=(),
    existing_issue_state=None,
) -> dict:
    selected = dict(_check() if check is None else check)
    selected.setdefault("python_version", VERSION)
    if check is None:
        selected["python_version"] = VERSION
    powershell = (
        powershell_override or shutil.which("pwsh") or shutil.which("powershell")
    )
    assert powershell, "PowerShell is required for the shipped QA execution tests"
    # Execute shipped dispatch, finding construction, filing loop and final verdict.
    # Mock every GitHub operation; never execute startup, HTTP, standards or logs.
    command = (
        "$ErrorActionPreference='Stop';"
        "$PSNativeCommandUseErrorActionPreference=$false;"
        "$inputData=[Console]::In.ReadToEnd() | ConvertFrom-Json;"
        "$src=Get-Content -Raw -LiteralPath $inputData.script;"
        "$start=$src.IndexOf('function Invoke-CommandCapture');"
        "$end=$src.IndexOf('function Invoke-HttpCheck');"
        "Invoke-Expression $src.Substring($start,$end-$start);"
        "$DryRun=[bool]$inputData.dryRun;"
        "$repoPath=$inputData.repo; $platformRepoPath=$inputData.platform; $repoName='lotus-core';"
        "$entry=[pscustomobject]@{checks=[pscustomobject]@{custom_checks=@($inputData.check)+@($inputData.additionalChecks)}};"
        "$customCheckResults=New-Object 'System.Collections.Generic.List[object]';"
        "$findings=New-Object 'System.Collections.Generic.List[object]';"
        "$start=$src.IndexOf('function New-Recommendation');"
        "$end=$src.IndexOf('function Get-CausalLogCommand',$start);"
        "Invoke-Expression $src.Substring($start,$end-$start);"
        "$start=$src.IndexOf('function Add-Finding');"
        "$end=$src.IndexOf('function Get-AvailableGitHubLabels',$start);"
        "Invoke-Expression $src.Substring($start,$end-$start);"
        "$start=$src.IndexOf('  if ($entry.checks.custom_checks)');"
        "$end=$src.IndexOf('  if ($entry.startup.log_command)', $start);"
        "Invoke-Expression $src.Substring($start,$end-$start);"
        "$CreateIssues=$true; $BringUp=$false; $githubRepo='fixture/lotus-core';"
        "$runId='offline-fixture'; $evidenceDir=Join-Path $repoPath 'qa-evidence';"
        "$repoResults=New-Object 'System.Collections.Generic.List[object]';"
        "$issueRecords=New-Object 'System.Collections.Generic.List[object]';"
        "$script:issueCalls=New-Object 'System.Collections.Generic.List[object]';"
        "function Get-IssueByExactTitle { param($GitHubRepo,$Title)"
        "$script:issueCalls.Add([pscustomobject]@{operation='lookup';title=$Title});"
        "if ($inputData.existingIssueState) { return [pscustomobject]@{state=$inputData.existingIssueState;number=17;url='https://example.invalid/17'} } };"
        "function New-GitHubIssue { param($GitHubRepo,$Title,$BodyFile,$RequestedLabels)"
        "$script:issueCalls.Add([pscustomobject]@{operation='create';title=$Title});"
        "return [pscustomobject]@{success=$true;labels=@();response='https://example.invalid/18'} };"
        "function gh { if ($args[0] -ne 'issue' -or $args[1] -ne 'reopen') { throw 'Unexpected GitHub operation' };"
        "$script:issueCalls.Add([pscustomobject]@{operation='reopen';number=$args[2]}); $global:LASTEXITCODE=0 };"
        "$start=$src.IndexOf('  $repoFindings =');"
        "$end=$src.IndexOf('  if ($BringUp -and -not $KeepRunning)', $start);"
        "Invoke-Expression $src.Substring($start,$end-$start);"
        "$summary=[pscustomobject]@{finding_count=$findings.Count};"
        "[pscustomobject]@{results=$customCheckResults.ToArray();findings=$findings.ToArray();"
        "repo_results=$repoResults.ToArray();issues=$issueRecords.ToArray();issue_calls=$script:issueCalls.ToArray()} | ConvertTo-Json -Depth 10;"
        "$start=$src.LastIndexOf('if ((-not $DryRun)'); Invoke-Expression $src.Substring($start);"
    )
    environment = dict(os.environ, QA_TEST_CHILD_EXIT=str(child_exit))
    completed = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", command],
        input=json.dumps(
            {
                "script": str(SCRIPT),
                "repo": str(core),
                "platform": str(ROOT),
                "check": selected,
                "dryRun": dry_run,
                "additionalChecks": additional_checks,
                "existingIssueState": existing_issue_state,
            }
        ),
        capture_output=True,
        text=True,
        env=environment,
        timeout=40,
        cwd=ROOT,
        check=False,
    )
    assert completed.returncode in (0, 2), completed.stdout + completed.stderr
    outcome = json.loads(completed.stdout)
    outcome["qa_native_exit"] = completed.returncode
    return outcome


def test_configured_core_path_with_spaces_executes_exact_read_only_arguments(
    core: Path,
) -> None:
    outcome = _run(core)
    result = outcome["results"][0]
    assert result["status"] == "passed"
    assert result["native_exit_code"] == 0
    assert outcome["findings"] == []
    assert outcome["issue_calls"] == []
    assert outcome["qa_native_exit"] == 0
    payload = json.loads(result["output"])
    assert Path(payload["cwd"]) == core
    assert Path(payload["platform"]) == ROOT
    assert payload["argv"] == _check()["arguments"][1:]
    assert Path(result["working_directory"]) == core


@pytest.mark.parametrize("existing_state", [None, "OPEN", "CLOSED"])
def test_native_readiness_failure_is_preserved_separately_from_harness_failure(
    core: Path,
    existing_state: str | None,
) -> None:
    outcome = _run(core, child_exit=7, existing_issue_state=existing_state)
    result = outcome["results"][0]
    assert result["status"] == "verifier_failure"
    assert result["native_exit_code"] == 7
    assert "Verifier exit code 7" == outcome["findings"][0]["actual"]
    assert json.loads(result["output"])["argv"] == _check()["arguments"][1:]
    assert outcome["findings"][0]["type"] == "custom"
    assert outcome["qa_native_exit"] == 2
    expected = {
        None: ["lookup", "create"],
        "OPEN": ["lookup"],
        "CLOSED": ["lookup", "reopen"],
    }
    assert [call["operation"] for call in outcome["issue_calls"]] == expected[
        existing_state
    ]
    assert len(outcome["issues"]) == 1


@pytest.mark.parametrize(
    "missing", ["interpreter", "launcher", "declaration", "imports"]
)
def test_missing_environment_refuses_before_live_verifier(
    core: Path, missing: str
) -> None:
    if missing == "interpreter":
        interpreter = core / (
            ".venv/Scripts/python.exe" if os.name == "nt" else ".venv/bin/python"
        )
        interpreter.unlink()
    elif missing == "launcher":
        (core / "scripts/development/repository_python.py").unlink()
    elif missing == "declaration":
        (core / ".python-version").unlink()
    else:
        (core / "tools/front_office_portfolio_seed.py").write_text(
            "import unavailable_qa_fixture_package\n", encoding="utf-8"
        )
    outcome = _run(core)
    assert outcome["results"][0]["status"] == "harness_failure"
    assert outcome["results"][0]["native_exit_code"] is None
    assert (
        "Harness failure before live verifier evaluation"
        == outcome["findings"][0]["actual"]
    )
    assert '"argv"' not in outcome["results"][0]["output"]
    assert outcome["findings"][0]["type"] == "harness"
    assert outcome["issue_calls"] == []
    assert outcome["issues"] == []
    assert outcome["repo_results"][0]["findings"] == 1
    assert outcome["qa_native_exit"] == 2


def test_wrong_interpreter_version_refuses_before_import_or_verifier(
    core: Path,
) -> None:
    (core / ".python-version").write_text("0.0", encoding="utf-8")
    check = dict(_check(), python_version="0.0")
    outcome = _run(core, check)
    result = outcome["results"][0]
    assert result["status"] == "harness_failure"
    assert result["native_exit_code"] is None
    assert "Repository interpreter must be Python 0.0" in result["output"]
    assert outcome["findings"][0]["type"] == "harness"
    assert outcome["issue_calls"] == []
    assert outcome["qa_native_exit"] == 2


def test_declaration_drift_refuses_even_with_working_interpreter(core: Path) -> None:
    outcome = _run(core, dict(_check(), python_version="0.0"))
    result = outcome["results"][0]
    assert result["status"] == "harness_failure"
    assert "does not match required '0.0'" in result["output"]
    assert outcome["findings"][0]["type"] == "harness"
    assert outcome["issue_calls"] == []
    assert outcome["qa_native_exit"] == 2


def test_dry_run_does_not_require_or_launch_an_environment(tmp_path: Path) -> None:
    result = _run(tmp_path / "absent Core", dry_run=True)["results"][0]
    assert result["status"] == "dry_run"
    assert result["output"].startswith("[dry-run]")


@pytest.mark.skipif(os.name != "nt", reason="existing command checks use cmd.exe")
def test_existing_command_check_keeps_platform_cwd_and_native_exit(core: Path) -> None:
    outcome = _run(
        core,
        {"type": "command", "id": "legacy", "command": "cd", "expected_exit_code": 0},
    )
    result = outcome["results"][0]
    assert result["status"] == "passed"
    assert Path(result["output"]) == ROOT
    assert Path(result["working_directory"]) == ROOT


@pytest.mark.skipif(os.name != "nt", reason="existing command checks use cmd.exe")
def test_existing_command_failure_retains_native_exit_and_finding(core: Path) -> None:
    outcome = _run(
        core,
        {
            "type": "command",
            "id": "legacy",
            "command": "exit /b 9",
            "expected_exit_code": 0,
        },
    )
    result = outcome["results"][0]
    assert result["status"] == "command_failure"
    assert result["native_exit_code"] == 9
    assert outcome["findings"][0]["actual"] == "Exit code 9"
    assert outcome["findings"][0]["type"] == "custom"
    assert [call["operation"] for call in outcome["issue_calls"]] == [
        "lookup",
        "create",
    ]
    assert outcome["qa_native_exit"] == 2


@pytest.mark.skipif(os.name != "nt", reason="existing command checks use cmd.exe")
@pytest.mark.parametrize("existing_state", [None, "CLOSED"])
def test_mixed_findings_file_only_real_application_failure(
    core: Path,
    existing_state: str | None,
) -> None:
    (core / "scripts/development/repository_python.py").unlink()
    outcome = _run(
        core,
        additional_checks=[{"type": "command", "id": "legacy", "command": "exit /b 9"}],
        existing_issue_state=existing_state,
    )
    assert [finding["type"] for finding in outcome["findings"]] == ["harness", "custom"]
    assert outcome["repo_results"][0]["findings"] == 2
    assert outcome["qa_native_exit"] == 2
    assert len(outcome["issues"]) == 1
    assert outcome["issues"][0]["check_id"] == "legacy"
    assert [call["operation"] for call in outcome["issue_calls"]] == (
        ["lookup", "create"] if existing_state is None else ["lookup", "reopen"]
    )
    assert all(
        "legacy" in call["title"] for call in outcome["issue_calls"] if "title" in call
    )


@pytest.mark.skipif(os.name != "nt", reason="Windows PowerShell 5.1 compatibility")
@pytest.mark.parametrize("child_exit", [0, 7])
def test_windows_powershell_preserves_success_and_verifier_failure(
    core: Path, child_exit: int
) -> None:
    executable = shutil.which("powershell")
    assert executable, "Windows PowerShell is required by the public QA command"
    result = _run(core, child_exit=child_exit, powershell_override=executable)[
        "results"
    ][0]
    assert result["status"] == ("passed" if child_exit == 0 else "verifier_failure")
    assert result["native_exit_code"] == child_exit


def test_matrix_retains_verify_only_and_exact_existing_scenario() -> None:
    check = _check()
    assert check["python_version"] == "3.11"
    assert check["type"] == "core-repository-python"
    assert check["arguments"] == [
        "tools/front_office_portfolio_seed.py",
        "--verify-only",
        "--portfolio-id",
        "PB_SG_GLOBAL_BAL_001",
        "--start-date",
        "2025-03-31",
        "--end-date",
        "2026-04-10",
        "--benchmark-start-date",
        "2025-01-06",
        "--ingestion-base-url",
        "http://core-ingestion.dev.lotus",
        "--query-base-url",
        "http://core-query.dev.lotus",
        "--query-control-plane-base-url",
        "http://core-control.dev.lotus",
        "--gateway-base-url",
        "http://gateway.dev.lotus",
        "--wait-seconds",
        "300",
        "--poll-interval-seconds",
        "3",
    ]
