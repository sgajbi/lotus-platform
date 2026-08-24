from __future__ import annotations

import json
from pathlib import Path
import os
import shutil
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
SOURCE_STACK = ROOT / "platform-stack"
SECRET_NAMES = {
    "LOTUS_CORE_POSTGRES_PASSWORD",
    "LOTUS_MANAGE_POSTGRES_PASSWORD",
    "LOTUS_REPORT_POSTGRES_PASSWORD",
    "GRAFANA_ADMIN_PASSWORD",
}
REGISTRY_COMMAND_FILES = (
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-audit.txt",
    "scripts/dependency_health_check.py",
    "Dockerfile.ci-local",
)


def _read_env(path: Path) -> dict[str, str]:
    return {
        key: value
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line and not line.startswith("#") and "=" in line
        for key, value in [line.split("=", maxsplit=1)]
    }


def _copy_tracked_repository(destination: Path) -> None:
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    for encoded_path in tracked.split(b"\0"):
        if not encoded_path:
            continue
        relative_path = Path(os.fsdecode(encoded_path))
        source = ROOT / relative_path
        if not source.is_file():
            continue
        target = destination / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _make_copied_registry_paths_portable(
    platform_root: Path, fixture_root: Path
) -> None:
    repos_path = platform_root / "automation" / "repos.json"
    repos = json.loads(repos_path.read_text(encoding="utf-8"))
    registry_root = fixture_root / "registry-repositories"
    for repo in repos:
        repo_root = registry_root / repo["name"]
        repo_root.mkdir(parents=True)
        repo["path"] = repo_root.as_posix()
        commands = " ".join(
            str(repo.get(key, ""))
            for key in ("preflight_fast_command", "preflight_full_command")
        )
        for relative_file in REGISTRY_COMMAND_FILES:
            if relative_file not in commands:
                continue
            command_file = repo_root / relative_file
            command_file.parent.mkdir(parents=True, exist_ok=True)
            command_file.touch()
    repos_path.write_text(json.dumps(repos, indent=2) + "\n", encoding="utf-8")


def _run_bootstrap(
    stack: Path,
    workspace: Path,
    *,
    shell: str | None = None,
) -> subprocess.CompletedProcess[str]:
    resolved_shell = shell or shutil.which("pwsh") or shutil.which("powershell")
    assert resolved_shell is not None, (
        "PowerShell is required to verify the Windows bootstrap"
    )
    return subprocess.run(
        [
            resolved_shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(stack / "bootstrap.ps1"),
            "-WorkspaceRoot",
            str(workspace),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def _run_posix_bootstrap(
    stack: Path,
    workspace: Path,
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    if os.name == "nt":
        shell = shutil.which("sh")
        assert shell is not None, "A POSIX shell is required to verify bootstrap.sh"
        command = [shell, str(stack / "bootstrap.sh"), str(workspace)]
    else:
        command = [str(stack / "bootstrap.sh"), str(workspace)]
    return subprocess.run(
        command,
        cwd=stack,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_windows_bootstrap_generates_once_and_preserves_operator_values(
    tmp_path: Path,
) -> None:
    stack = tmp_path / "platform-stack"
    workspace = tmp_path / "workspace"
    shutil.copytree(SOURCE_STACK, stack, ignore=shutil.ignore_patterns(".env"))
    workspace.mkdir()

    first = _run_bootstrap(stack, workspace)
    assert first.returncode == 0, first.stderr
    generated = _read_env(stack / ".env")

    normalized_workspace = workspace.resolve().as_posix()
    assert generated["LOTUS_WORKSPACE_ROOT"] == normalized_workspace
    assert generated["LOTUS_CORE_REPO_PATH"] == f"{normalized_workspace}/lotus-core"
    assert all(len(generated[name]) == 64 for name in SECRET_NAMES)
    assert len({generated[name] for name in SECRET_NAMES}) == len(SECRET_NAMES)
    assert all(generated[name] not in first.stdout for name in SECRET_NAMES)

    custom_secret = "operator-managed-secret"
    env_path = stack / ".env"
    env_path.write_text(
        env_path.read_text(encoding="utf-8").replace(
            f"GRAFANA_ADMIN_PASSWORD={generated['GRAFANA_ADMIN_PASSWORD']}",
            f"GRAFANA_ADMIN_PASSWORD={custom_secret}",
        ),
        encoding="utf-8",
    )
    second = _run_bootstrap(stack, workspace)

    assert second.returncode == 0, second.stderr
    repeated = _read_env(env_path)
    assert repeated["GRAFANA_ADMIN_PASSWORD"] == custom_secret
    for name in SECRET_NAMES - {"GRAFANA_ADMIN_PASSWORD"}:
        assert repeated[name] == generated[name]
    assert custom_secret not in second.stdout


@pytest.mark.skipif(os.name != "nt", reason="Windows PowerShell 5.1 is Windows-only")
def test_windows_powershell_bootstrap_generates_required_secrets(
    tmp_path: Path,
) -> None:
    windows_powershell = shutil.which("powershell")
    assert windows_powershell is not None, (
        "Windows PowerShell is required for compatibility proof"
    )
    stack = tmp_path / "platform-stack"
    workspace = tmp_path / "workspace"
    shutil.copytree(SOURCE_STACK, stack, ignore=shutil.ignore_patterns(".env"))
    workspace.mkdir()

    completed = _run_bootstrap(stack, workspace, shell=windows_powershell)

    assert completed.returncode == 0, completed.stderr
    generated = _read_env(stack / ".env")
    assert all(len(generated[name]) == 64 for name in SECRET_NAMES)
    assert len({generated[name] for name in SECRET_NAMES}) == len(SECRET_NAMES)


def test_bootstrap_scripts_never_embed_tracked_secret_defaults() -> None:
    template = _read_env(SOURCE_STACK / ".env.example")
    powershell = (SOURCE_STACK / "bootstrap.ps1").read_text(encoding="utf-8")
    posix = (SOURCE_STACK / "bootstrap.sh").read_text(encoding="utf-8")

    assert all(template[name] == "" for name in SECRET_NAMES)
    assert "RandomNumberGenerator]::Create()" in powershell
    assert ".GetBytes($bytes)" in powershell
    assert '.ToString("x2")' in powershell
    assert "RandomNumberGenerator]::Fill" not in powershell
    assert "Convert]::ToHexString" not in powershell
    assert "openssl rand -hex 32" in posix
    assert "chmod 600" in posix
    assert posix.index("umask 077") < posix.index('cp "$template_path" "$env_path"')


def test_local_development_runbook_uses_governed_bootstrap_and_canonical_paths() -> (
    None
):
    runbook = (ROOT / "docs" / "operations" / "Local Development Runbook.md").read_text(
        encoding="utf-8"
    )

    assert ".\\platform-stack\\bootstrap.ps1 -WorkspaceRoot .." in runbook
    assert "./platform-stack/bootstrap.sh .." in runbook
    assert "LOTUS_GATEWAY_REPO_PATH" in runbook
    assert "LOTUS_WORKBENCH_REPO_PATH" in runbook
    assert "Copy-Item .env.example .env" not in runbook
    assert "BFF_REPO_PATH" not in runbook
    assert "UI_REPO_PATH" not in runbook


def test_service_scaffold_uses_canonical_stack_and_bootstrap_anchors() -> None:
    scaffold = (ROOT / "automation" / "New-Lotus-Service.ps1").read_text(
        encoding="utf-8"
    )

    assert "gatewayServiceAnchor" in scaffold
    assert "<<: \\*medium-service" in scaffold
    assert "condition: service_healthy" in scaffold
    assert "<<: *small-service" in scaffold
    assert "dev-ingress/Caddyfile.tls" in scaffold
    assert '$envLine = "$repoPathVariable="' in scaffold
    assert "platform-stack/bootstrap.ps1" in scaffold
    assert "platform-stack/bootstrap.sh" in scaffold
    assert '"  bff:`r`n"' not in scaffold
    assert "condition: service_started" not in scaffold
    assert "c:/Users/Sandeep/projects/$RepoName" not in scaffold
    assert (
        "powershell -ExecutionPolicy Bypass -File $validateAutomation" not in scaffold
    )


def test_service_scaffold_registration_preserves_valid_platform_stack(
    tmp_path: Path,
) -> None:
    platform_root = tmp_path / "lotus-platform"
    workspace_root = tmp_path / "workspace"
    _copy_tracked_repository(platform_root)
    _make_copied_registry_paths_portable(platform_root, tmp_path)
    workspace_root.mkdir()
    service_name = "lotus-scaffold-contract"
    completed = subprocess.run(
        [
            shutil.which("powershell") or shutil.which("pwsh") or "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(platform_root / "automation" / "New-Lotus-Service.ps1"),
            "-ServiceName",
            service_name,
            "-DestinationRoot",
            str(workspace_root),
            "-DevHostName",
            "scaffold-contract",
            "-Port",
            "8999",
            "-Force",
        ],
        cwd=platform_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    compose_path = platform_root / "platform-stack" / "docker-compose.yml"
    compose = compose_path.read_text(encoding="utf-8-sig")
    compose_model = yaml.safe_load(compose)
    services = compose_model["services"]
    assert list(services).count(service_name) == 1
    assert f"  {service_name}:\n    <<: *small-service\n" in compose
    assert services["dev-ingress"]["depends_on"][service_name] == {
        "condition": "service_healthy"
    }
    assert service_name not in services["grafana"]["depends_on"]

    env_lines = (
        (platform_root / "platform-stack" / ".env.example")
        .read_text(encoding="utf-8-sig")
        .splitlines()
    )
    assert "LOTUS_SCAFFOLD_CONTRACT_REPO_PATH=" in env_lines
    powershell_bootstrap = (
        platform_root / "platform-stack" / "bootstrap.ps1"
    ).read_text(encoding="utf-8-sig")
    posix_bootstrap = (platform_root / "platform-stack" / "bootstrap.sh").read_text(
        encoding="utf-8-sig"
    )
    assert (
        'LOTUS_SCAFFOLD_CONTRACT_REPO_PATH = "lotus-scaffold-contract"'
        in powershell_bootstrap
    )
    assert (
        'set_if_empty LOTUS_SCAFFOLD_CONTRACT_REPO_PATH "$workspace_root/lotus-scaffold-contract"'
        in posix_bootstrap
    )
    tls_caddyfile = (
        platform_root / "platform-stack" / "dev-ingress" / "Caddyfile.tls"
    ).read_text(encoding="utf-8-sig")
    assert "https://scaffold-contract.dev.lotus" in tls_caddyfile
    assert "reverse_proxy lotus-scaffold-contract:8999" in tls_caddyfile

    validator = subprocess.run(
        [
            sys.executable,
            str(platform_root / "automation" / "validate_platform_stack.py"),
            "--stack-root",
            str(platform_root / "platform-stack"),
        ],
        cwd=platform_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert validator.returncode == 0, validator.stdout + validator.stderr


@pytest.mark.skipif(
    os.name == "nt", reason="POSIX path semantics are verified on Linux CI"
)
def test_posix_bootstrap_resolves_relative_workspace_before_writing_paths(
    tmp_path: Path,
) -> None:
    stack = tmp_path / "platform-stack"
    workspace = tmp_path / "workspace"
    shutil.copytree(SOURCE_STACK, stack, ignore=shutil.ignore_patterns(".env"))
    workspace.mkdir()
    relative_workspace = Path(os.path.relpath(workspace, start=stack))

    completed = _run_posix_bootstrap(stack, relative_workspace)

    assert completed.returncode == 0, completed.stderr
    generated = _read_env(stack / ".env")
    normalized_workspace = workspace.resolve().as_posix()
    assert generated["LOTUS_WORKSPACE_ROOT"] == normalized_workspace
    assert generated["LOTUS_MANAGE_REPO_PATH"] == f"{normalized_workspace}/lotus-manage"


@pytest.mark.skipif(os.name == "nt", reason="POSIX file modes are verified on Linux CI")
def test_posix_bootstrap_failure_never_leaves_environment_world_readable(
    tmp_path: Path,
) -> None:
    stack = tmp_path / "platform-stack"
    workspace = tmp_path / "workspace"
    fake_bin = tmp_path / "fake-bin"
    shutil.copytree(SOURCE_STACK, stack, ignore=shutil.ignore_patterns(".env"))
    workspace.mkdir()
    fake_bin.mkdir()
    fake_openssl = fake_bin / "openssl"
    fake_openssl.write_text("#!/usr/bin/env sh\nexit 23\n", encoding="utf-8")
    fake_openssl.chmod(0o755)
    environment = os.environ.copy()
    environment["PATH"] = f"{fake_bin}{os.pathsep}{environment['PATH']}"

    completed = _run_posix_bootstrap(stack, workspace, env=environment)

    assert completed.returncode != 0
    assert "Failed to generate LOTUS_CORE_POSTGRES_PASSWORD" in completed.stderr
    env_path = stack / ".env"
    assert env_path.is_file()
    assert env_path.stat().st_mode & 0o077 == 0
