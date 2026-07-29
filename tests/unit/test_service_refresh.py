from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVICE_REFRESH = ROOT / "automation" / "Service-Refresh.ps1"
TARGETED_REFRESH_SKILL = (
    ROOT / "codex" / "skills" / "targeted-service-refresh" / "SKILL.md"
)
AUTOMATION_GUIDE = ROOT / "automation" / "docs" / "Automation-Guide.md"


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
    tmp_path: Path, fake_docker: Path, service: str
) -> subprocess.CompletedProcess[str]:
    project = tmp_path / "app"
    project.mkdir()
    return subprocess.run(
        _powershell_command(
            SERVICE_REFRESH,
            "-ProjectPath",
            str(project),
            "-Services",
            service,
            "-DockerCommand",
            str(fake_docker),
        ),
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
                "if ($line -eq 'compose ps') {",
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
                "if ($line -eq 'compose ps') {",
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
        "compose ps",
    ]


def test_service_refresh_preserves_successful_explicit_service_refresh(
    tmp_path: Path,
) -> None:
    fake_docker = _fake_docker(tmp_path, "exit 0")

    result = _run_service_refresh(tmp_path, fake_docker, "lotus-gateway")

    assert result.returncode == 0, result.stderr
    assert _command_log(tmp_path) == [
        "compose up -d --build lotus-gateway",
        "compose ps",
    ]


def test_service_refresh_fail_closed_behavior_is_documented() -> None:
    skill = TARGETED_REFRESH_SKILL.read_text(encoding="utf-8")
    guide = AUTOMATION_GUIDE.read_text(encoding="utf-8")

    assert "fails closed when Docker rejects `compose up`" in skill
    assert "when `docker compose up` or `docker compose ps` returns non-zero" in guide
