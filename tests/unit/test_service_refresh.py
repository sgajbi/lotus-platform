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
                "if ($line -eq 'compose ps --format json lotus-gateway') {",
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
    assert _command_log(tmp_path) == [
        "compose up -d --build lotus-gateway",
        "compose ps --format json lotus-gateway",
    ]


def test_service_refresh_preserves_successful_explicit_service_refresh(
    tmp_path: Path,
) -> None:
    fake_docker = _fake_docker(
        tmp_path,
        "\n".join(
            [
                "if ($line -eq 'compose ps --format json lotus-gateway') {",
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
        "compose ps --format json lotus-gateway",
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
                "if ($line -eq 'compose ps --format json lotus-manage') {",
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
        "compose ps --format json lotus-manage",
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
                "if ($line -eq 'compose ps --format json lotus-manage') {",
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
