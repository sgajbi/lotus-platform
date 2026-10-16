from __future__ import annotations

import shutil
import subprocess
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SERVICE_REFRESH = ROOT / "automation" / "Service-Refresh.ps1"
TARGETED_REFRESH_SKILL = (
    ROOT / "codex" / "skills" / "targeted-service-refresh" / "SKILL.md"
)
AUTOMATION_GUIDE = ROOT / "automation" / "docs" / "Automation-Guide.md"
SERVICE_MAP = ROOT / "automation" / "service-map.json"


def _powershell_executable() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    assert executable is not None, (
        "pwsh or powershell is required for service refresh tests"
    )
    return executable


def _powershell_command(script: Path, *arguments: str) -> list[str]:
    command = [_powershell_executable(), "-NoProfile"]
    if "powershell" in Path(command[0]).name.lower():
        command.extend(["-ExecutionPolicy", "Bypass"])
    command.extend(["-File", str(script), *arguments])
    return command


def _fake_docker(tmp_path: Path, body: str) -> Path:
    command_log = tmp_path / "docker-commands.log"
    script = tmp_path / "fake-docker.ps1"
    script.write_text(
        "\n".join(
            [
                "param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)",
                f"$commandLog = {str(command_log)!r}",
                "$line = $Args -join ' '",
                "Add-Content -Path $commandLog -Value $line",
                body,
            ]
        ),
        encoding="utf-8",
    )
    return script


def _run_service_refresh(
    tmp_path: Path,
    fake_docker: Path,
    service: str,
    *,
    project_name: str = "lotus-gateway",
    map_path: Path | None = None,
    dry_run: bool = False,
) -> subprocess.CompletedProcess[str]:
    project = tmp_path / project_name
    project.mkdir()
    arguments = [
        "-ProjectPath",
        str(project),
        "-Services",
        service,
        "-DockerCommand",
        str(fake_docker),
        "-HealthTimeoutSeconds",
        "0",
    ]
    if map_path is not None:
        arguments.extend(["-MapPath", str(map_path)])
    if dry_run:
        arguments.append("-DryRun")
    return subprocess.run(
        _powershell_command(SERVICE_REFRESH, *arguments),
        text=True,
        capture_output=True,
        check=False,
    )


def _command_log(tmp_path: Path) -> list[str]:
    log_path = tmp_path / "docker-commands.log"
    if not log_path.exists():
        return []
    return log_path.read_text(encoding="utf-8").splitlines()


def test_service_refresh_fails_before_ps_when_compose_up_rejects_service(
    tmp_path: Path,
) -> None:
    fake_docker = _fake_docker(
        tmp_path,
        "\n".join(
            [
                "if ($line -like 'compose up*missing-service*') {",
                "  [Console]::Error.WriteLine('no such service: missing-service')",
                "  exit 17",
                "}",
                "if ($line -like 'compose ps*') {",
                "  Add-Content -Path $commandLog -Value 'unexpected-ps-after-up-failure'",
                "}",
                "exit 0",
            ]
        ),
    )

    result = _run_service_refresh(tmp_path, fake_docker, "missing-service")

    assert result.returncode != 0
    assert "docker compose up failed; service refresh did not complete" in result.stderr
    assert _command_log(tmp_path) == ["compose up -d --build missing-service"]


def test_service_refresh_fails_when_compose_ps_fails(tmp_path: Path) -> None:
    fake_docker = _fake_docker(
        tmp_path,
        "\n".join(
            [
                "if ($line -eq 'compose ps --no-trunc --format json lotus-gateway') {",
                "  [Console]::Error.WriteLine('compose ps unavailable')",
                "  exit 23",
                "}",
                "exit 0",
            ]
        ),
    )

    result = _run_service_refresh(tmp_path, fake_docker, "lotus-gateway")

    assert result.returncode != 0
    assert "docker compose ps failed after service refresh" in result.stderr
    assert "compose ps unavailable" in result.stderr
    assert _command_log(tmp_path) == [
        "compose up -d --build lotus-gateway",
        "compose ps --no-trunc --format json lotus-gateway",
    ]


def test_service_refresh_preserves_successful_explicit_service_refresh(
    tmp_path: Path,
) -> None:
    fake_docker = _fake_docker(
        tmp_path,
        "\n".join(
            [
                "if ($line -eq 'compose ps --no-trunc --format json lotus-gateway') {",
                '  Write-Output \'{"Service":"lotus-gateway","State":"running","Health":"healthy","Publishers":[]}\'',
                "}",
                "exit 0",
            ]
        ),
    )

    result = _run_service_refresh(tmp_path, fake_docker, "lotus-gateway")

    assert result.returncode == 0, result.stderr
    assert _command_log(tmp_path) == [
        "compose up -d --build lotus-gateway",
        "compose ps --no-trunc --format json lotus-gateway",
    ]


def test_service_refresh_keeps_compose_stderr_out_of_json_state(tmp_path: Path) -> None:
    fake_docker = _fake_docker(
        tmp_path,
        "\n".join(
            [
                "if ($line -eq 'compose ps --no-trunc --format json lotus-gateway') {",
                "  [Console]::Error.WriteLine('compose warning: obsolete attribute')",
                '  Write-Output \'{"Service":"lotus-gateway","State":"running","Health":"healthy","Publishers":[]}\'',
                "}",
                "exit 0",
            ]
        ),
    )

    result = _run_service_refresh(tmp_path, fake_docker, "lotus-gateway")

    assert result.returncode == 0, result.stderr
    assert "compose warning: obsolete attribute" in result.stderr
    assert "invalid JSON service state" not in result.stderr
    assert _command_log(tmp_path) == [
        "compose up -d --build lotus-gateway",
        "compose ps --no-trunc --format json lotus-gateway",
    ]


def test_service_refresh_applies_manage_canonical_environment_and_verifies_port(
    tmp_path: Path,
) -> None:
    fake_docker = _fake_docker(
        tmp_path,
        "\n".join(
            [
                "if ($line -like 'compose up*') {",
                '  Add-Content -Path $commandLog -Value "env:$env:LOTUS_MANAGE_HOST_PORT|$env:DPM_CORE_BASE_URL|$env:DPM_CORE_QUERY_BASE_URL|$env:DPM_WORKFLOW_ENABLED"',
                "}",
                "if ($line -eq 'compose ps --no-trunc --format json lotus-manage') {",
                '  Write-Output \'{"Service":"lotus-manage","State":"running","Health":"healthy","Publishers":[{"TargetPort":8000,"PublishedPort":8001}]}\'',
                "}",
                "exit 0",
            ]
        ),
    )

    result = _run_service_refresh(
        tmp_path,
        fake_docker,
        "lotus-manage",
        project_name="lotus-manage",
    )

    assert result.returncode == 0, result.stderr
    assert "Verified service readiness: lotus-manage" in result.stdout
    assert _command_log(tmp_path) == [
        "compose up -d --build lotus-manage",
        "env:8001|http://host.docker.internal:8202|http://host.docker.internal:8201|true",
        "compose ps --no-trunc --format json lotus-manage",
    ]


def test_service_refresh_dry_run_reports_manage_environment_and_port(
    tmp_path: Path,
) -> None:
    fake_docker = _fake_docker(tmp_path, "exit 0")

    result = _run_service_refresh(
        tmp_path,
        fake_docker,
        "lotus-manage",
        project_name="lotus-manage",
        dry_run=True,
    )

    assert result.returncode == 0, result.stderr
    assert "LOTUS_MANAGE_HOST_PORT=8001" in result.stdout
    assert "DPM_CORE_BASE_URL=http://host.docker.internal:8202" in result.stdout
    assert "Expected published port: lotus-manage 8001:8000" in result.stdout
    assert _command_log(tmp_path) == []


@pytest.mark.parametrize(
    "environment_name",
    [
        "API_TOKEN",
        "DB_PASS",
        "GIT_SSH_COMMAND",
        "LD_PRELOAD",
        "PYTHONPATH",
        "DPM_API_TOKEN",
        "LOTUS_DB_PASSWORD",
        "LOTUS_DB_PASS",
    ],
)
def test_service_refresh_rejects_ungoverned_environment_mapping(
    tmp_path: Path,
    environment_name: str,
) -> None:
    unsafe_map = tmp_path / "unsafe-service-map.json"
    unsafe_map.write_text(
        json.dumps(
            {
                "repos": [
                    {
                        "name": "unsafe-app",
                        "composeEnvironment": {environment_name: "must-not-log"},
                        "defaultServices": ["unsafe-service"],
                        "rules": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    fake_docker = _fake_docker(tmp_path, "exit 0")

    result = _run_service_refresh(
        tmp_path,
        fake_docker,
        "unsafe-service",
        project_name="unsafe-app",
        map_path=unsafe_map,
    )

    assert result.returncode != 0
    assert "cannot be governed by service refresh" in result.stderr
    assert "must-not-log" not in result.stdout
    assert _command_log(tmp_path) == []


def test_service_refresh_rejects_manage_port_mismatch(tmp_path: Path) -> None:
    fake_docker = _fake_docker(
        tmp_path,
        "\n".join(
            [
                "if ($line -eq 'compose ps --no-trunc --format json lotus-manage') {",
                '  Write-Output \'{"Service":"lotus-manage","State":"running","Health":"healthy","Publishers":[{"TargetPort":8000,"PublishedPort":8000}]}\'',
                "}",
                "exit 0",
            ]
        ),
    )

    result = _run_service_refresh(
        tmp_path,
        fake_docker,
        "lotus-manage",
        project_name="lotus-manage",
    )

    assert result.returncode != 0
    assert "does not publish required port 8001:8000" in result.stderr


def test_service_refresh_fail_closed_behavior_is_documented() -> None:
    skill = TARGETED_REFRESH_SKILL.read_text(encoding="utf-8")
    guide = AUTOMATION_GUIDE.read_text(encoding="utf-8")
    service_map = json.loads(SERVICE_MAP.read_text(encoding="utf-8"))
    manage = next(
        repo for repo in service_map["repos"] if repo["name"] == "lotus-manage"
    )

    assert "fails closed when Docker rejects `compose up`" in skill
    assert "governed non-secret Compose environment" in guide
    assert "published-port" in skill
    assert manage["composeEnvironment"]["LOTUS_MANAGE_HOST_PORT"] == "8001"
    assert manage["serviceVerification"]["lotus-manage"] == {
        "requireHealthy": True,
        "publishedPorts": [{"target": 8000, "published": 8001}],
    }


def test_performance_source_refresh_includes_every_long_running_code_consumer() -> None:
    service_map = json.loads(SERVICE_MAP.read_text(encoding="utf-8"))
    performance = next(
        repo for repo in service_map["repos"] if repo["name"] == "lotus-performance"
    )
    expected_services = {
        "performance-analytics",
        "performance-compute-executor",
        "performance-lineage-worker",
    }

    assert set(performance["defaultServices"]) == expected_services
    production_rule = next(
        rule for rule in performance["rules"] if "app/" in rule["pathPrefixes"]
    )
    assert set(production_rule["services"]) == expected_services


def test_core_query_control_plane_source_refreshes_its_runtime() -> None:
    service_map = json.loads(SERVICE_MAP.read_text(encoding="utf-8"))
    core = next(repo for repo in service_map["repos"] if repo["name"] == "lotus-core")
    qcp_rule = next(
        rule
        for rule in core["rules"]
        if "src/services/query_control_plane_service/" in rule["pathPrefixes"]
    )

    assert qcp_rule["services"] == ["query_control_plane_service"]


@pytest.mark.parametrize("shell_name", ["powershell", "pwsh"])
def test_one_shot_completion_policy_and_state_controls(tmp_path: Path, shell_name: str) -> None:
    shell = shutil.which(shell_name)
    if shell is None:
        pytest.skip(f"{shell_name} unavailable")
    command = f"""
$ErrorActionPreference='Stop'
$tokens=$null; $errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile('{SERVICE_REFRESH}',[ref]$tokens,[ref]$errors)
if ($errors.Count) {{ throw 'Adapter parse failure' }}
foreach ($name in @('Get-ServiceVerification','Get-ServiceCompletionPolicy','Get-InspectedComposeServiceContainer','Test-OneShotCompletion','Get-ServiceReadinessFailures')) {{
  $node=$ast.Find({{param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name}},$true)
  Invoke-Expression $node.Extent.Text
}}
$config='{{"serviceVerification":{{"job":{{"completionPolicy":"exited-zero"}}}}}}' | ConvertFrom-Json
$expected=@{{service='job';project='core';imageId='sha256:{'c' * 64}';sourceRevision='{'a' * 40}';repository='lotus-core';checkout='reviewed'}}
function ControlledInspect {{ $global:LASTEXITCODE=0; return ConvertTo-Json -InputObject @($global:container) -Depth 12 -Compress }}
$cases=@('valid','running','created','nonzero','oom','restart','missing-exit','string-exit','missing-oom','missing-running','string-restart','unknown',
         'project','service','container','image','source','repository','checkout','container-drift','ps-identity','ps-short-identity','ps-missing-identity','error')
foreach ($case in $cases) {{
  $global:container=@{{Id='{'b' * 64}';Image=$expected.imageId;RestartCount=0;Config=@{{Labels=@{{
    'com.docker.compose.project'='core';'com.docker.compose.service'='job';'com.docker.compose.oneoff'='False';'org.opencontainers.image.revision'=$expected.sourceRevision;
    'org.opencontainers.image.source'='lotus-core';'com.lotus.repository.checkout'='reviewed'
  }}}};State=@{{Status='exited';ExitCode=0;OOMKilled=$false;Running=$false;Error=''}}}}
  $state=@{{Service='job';State='exited';ID='{'b' * 64}'}}
  $observed=''
  switch ($case) {{
    'running' {{ $container.State.Status='running';$container.State.Running=$true;$state.State='running' }}
    'created' {{ $container.State.Status='created';$state.State='created' }}
    'nonzero' {{ $container.State.ExitCode=1 }}
    'oom' {{ $container.State.OOMKilled=$true }}
    'restart' {{ $container.RestartCount=1 }}
    'missing-exit' {{ $container.State.Remove('ExitCode') }}
    'string-exit' {{ $container.State.ExitCode='0' }}
    'missing-oom' {{ $container.State.Remove('OOMKilled') }}
    'missing-running' {{ $container.State.Remove('Running') }}
    'string-restart' {{ $container.RestartCount='0' }}
    'unknown' {{ $container.State.Status='dead' }}
    'project' {{ $container.Config.Labels.'com.docker.compose.project'='foreign' }}
    'service' {{ $container.Config.Labels.'com.docker.compose.service'='foreign' }}
    'container' {{ $container.Id='{'d' * 64}' }}
    'image' {{ $container.Image='sha256:{'d' * 64}' }}
    'source' {{ $container.Config.Labels.'org.opencontainers.image.revision'='{'d' * 40}' }}
    'repository' {{ $container.Config.Labels.'org.opencontainers.image.source'='foreign' }}
    'checkout' {{ $container.Config.Labels.'com.lotus.repository.checkout'='foreign' }}
    'container-drift' {{ $observed='{'d' * 64}' }}
    'ps-identity' {{ $state.ID='malformed' }}
    'ps-short-identity' {{ $state.ID=$state.ID.Substring(0,12) }}
    'ps-missing-identity' {{ $state.Remove('ID') }}
    'error' {{ $container.State.Error='execution failed' }}
  }}
  $failure=$null; $complete=$null
  try {{ $complete=Test-OneShotCompletion -Command ControlledInspect -State $state -ExpectedImage $expected -Service job -ObservedContainer $observed }}
  catch {{ $failure=$_.Exception.Message }}
  if ($case -eq 'valid') {{ if ($failure -or -not $complete) {{ throw "Valid completion refused: $failure" }} }}
  elseif ($case -in @('running','created')) {{ if ($failure -or $complete) {{ throw "Pending completion mishandled: $case $failure" }} }}
  elseif (-not $failure) {{ throw "Bad completion accepted: $case" }}
  Write-Output "CONTROL_PASS:$case"
}}
foreach ($policy in @('unknown',0,$null,@{{}})) {{
  $config.serviceVerification.job.completionPolicy=$policy
  $refused=$false
  try {{ Get-ServiceCompletionPolicy -RepositoryConfig $config -Service job | Out-Null }} catch {{ $refused=$true }}
  if (-not $refused) {{ throw 'Malformed policy accepted' }}
}}
$daemon=@{{Service='daemon';State='exited';Health='healthy';ExitCode=0}}
if (@(Get-ServiceReadinessFailures -States @($daemon) -ServiceNames @('daemon') -RepositoryConfig $config).Count -ne 1) {{ throw 'Exited daemon accepted' }}
if ((Get-ServiceCompletionPolicy -RepositoryConfig $config -Service daemon) -ne 'running') {{ throw 'Daemon default weakened' }}
"""
    result = subprocess.run([shell, "-NoProfile", "-Command", command], text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.count("CONTROL_PASS:") == 24


def test_declared_one_shot_requires_prepared_reserved_path(tmp_path: Path) -> None:
    fake_docker = _fake_docker(tmp_path, "exit 0")
    result = _run_service_refresh(tmp_path, fake_docker, "migration-runner", project_name="lotus-core")
    assert result.returncode == 1
    assert "requires a reviewed reserved plan and prepared immutable images" in result.stderr
    assert _command_log(tmp_path) == []


def test_daemon_refresh_does_not_query_stopped_compose_run_containers(tmp_path: Path) -> None:
    running = {"Service": "lotus-gateway", "State": "running", "Health": "healthy", "Publishers": []}
    stale_run = {"Service": "lotus-gateway", "State": "exited", "ExitCode": 0, "Name": "historical-run"}
    fake_docker = _fake_docker(tmp_path, "\n".join([
        "if ($line -like 'compose ps*') {",
        f"  if ($Args -contains '--all') {{ Write-Output '{json.dumps([stale_run, running])}' }}",
        f"  else {{ Write-Output '{json.dumps(running)}' }}",
        "}",
        "exit 0",
    ]))
    result = _run_service_refresh(tmp_path, fake_docker, "lotus-gateway")
    assert result.returncode == 0, result.stderr
    assert _command_log(tmp_path) == ["compose up -d --build lotus-gateway", "compose ps --no-trunc --format json lotus-gateway"]
