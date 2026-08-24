from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]
SOURCE_STACK = ROOT / "platform-stack"
SECRET_NAMES = {
    "LOTUS_CORE_POSTGRES_PASSWORD",
    "LOTUS_MANAGE_POSTGRES_PASSWORD",
    "LOTUS_REPORT_POSTGRES_PASSWORD",
    "GRAFANA_ADMIN_PASSWORD",
}


def _read_env(path: Path) -> dict[str, str]:
    return {
        key: value
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line and not line.startswith("#") and "=" in line
        for key, value in [line.split("=", maxsplit=1)]
    }


def _run_bootstrap(stack: Path, workspace: Path) -> subprocess.CompletedProcess[str]:
    shell = shutil.which("pwsh") or shutil.which("powershell")
    assert shell is not None, "PowerShell is required to verify the Windows bootstrap"
    return subprocess.run(
        [
            shell,
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


def test_windows_bootstrap_generates_once_and_preserves_operator_values(tmp_path: Path) -> None:
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


def test_bootstrap_scripts_never_embed_tracked_secret_defaults() -> None:
    template = _read_env(SOURCE_STACK / ".env.example")
    powershell = (SOURCE_STACK / "bootstrap.ps1").read_text(encoding="utf-8")
    posix = (SOURCE_STACK / "bootstrap.sh").read_text(encoding="utf-8")

    assert all(template[name] == "" for name in SECRET_NAMES)
    assert "RandomNumberGenerator" in powershell
    assert "openssl rand -hex 32" in posix
    assert "chmod 600" in posix
    assert posix.index("umask 077") < posix.index('cp "$template_path" "$env_path"')


@pytest.mark.skipif(os.name == "nt", reason="POSIX path semantics are verified on Linux CI")
def test_posix_bootstrap_resolves_relative_workspace_before_writing_paths(tmp_path: Path) -> None:
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
