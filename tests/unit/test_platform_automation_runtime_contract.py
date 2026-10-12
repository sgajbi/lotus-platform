from __future__ import annotations

import ast
import copy
import sys
import tomllib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
AUTOMATION = ROOT / "automation"

# A module and the distribution that ships it are not always spelled the same,
# so the few that differ are named rather than guessed.
DISTRIBUTION_FOR_MODULE = {"yaml": "PyYAML"}


def _local_module_names() -> set[str]:
    """Modules that live in automation/ and are imported by bare name."""
    packaged = {path.parent.name for path in (ROOT / "packages").glob("*/src/*/__init__.py")}
    return {path.stem for path in AUTOMATION.rglob("*.py")} | {"automation", "tests"} | packaged


def _third_party_imports() -> set[str]:
    local = _local_module_names()
    imported: set[str] = set()
    for path in AUTOMATION.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module.split(".")[0]]
            else:
                continue
            imported.update(
                name
                for name in names
                if name not in sys.stdlib_module_names and name not in local
            )
    return imported


def test_every_third_party_import_in_automation_is_pinned() -> None:
    """The lock must cover what the code actually imports.

    Listing a few known pins cannot notice a new dependency: `cryptography` was
    imported by automation and absent from the lock, so it resolved locally and
    failed in CI with ModuleNotFoundError. An invariant over the real import set
    fails here instead, where the fix is cheap.
    """
    lock = (AUTOMATION / "requirements.platform-automation.lock.txt").read_text(
        encoding="utf-8"
    )
    pinned = {
        line.split("==")[0].strip().lower()
        for line in lock.splitlines()
        if "==" in line and not line.strip().startswith("#")
    }

    unpinned = sorted(
        module
        for module in _third_party_imports()
        if DISTRIBUTION_FOR_MODULE.get(module, module).lower() not in pinned
    )

    assert not unpinned, f"imported by automation/ but absent from the lock: {unpinned}"


def test_the_import_scan_actually_finds_dependencies() -> None:
    """Guards the invariant above against passing on an empty set.

    A scan that matched nothing would report every dependency as pinned, and no
    imports and no unpinned imports are the same green.
    """
    assert {"requests", "yaml"} <= _third_party_imports()


def test_platform_automation_python_runtime_is_locked_and_reused() -> None:
    requirements_lock = (ROOT / "automation" / "requirements.platform-automation.lock.txt").read_text(
        encoding="utf-8"
    )
    resolver = (ROOT / "automation" / "Resolve-PlatformAutomationPython.ps1").read_text(encoding="utf-8")
    repo_checks = (ROOT / "automation" / "Invoke-PlatformRepoChecks.ps1").read_text(encoding="utf-8")
    validation_lane = (ROOT / "automation" / "Invoke-PlatformValidationLane.ps1").read_text(
        encoding="utf-8"
    )
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "pytest==" in requirements_lock
    assert "requests==" in requirements_lock
    assert "PyYAML==" in requirements_lock

    assert ".venv-platform-automation" in resolver
    assert "requirements.platform-automation.lock.txt" in resolver

    assert "Resolve-PlatformAutomationPython.ps1" in repo_checks
    assert "Resolve-PlatformAutomationPython.ps1" in validation_lane
    assert "Sync-RepoWikis.ps1" in repo_checks
    assert "python -m pip install pytest requests PyYAML" not in repo_checks
    assert "python -m pip install requests" not in validation_lane

    assert ".venv-platform-automation/" in gitignore


def test_local_principal_package_is_built_and_installed_before_unit_collection() -> None:
    checks = (AUTOMATION / "Invoke-PlatformRepoChecks.ps1").read_text(encoding="utf-8")
    build = checks.index("Invoke-CheckedCommand $toolingPython automation/verify_principal_runtime_distribution.py")
    install = checks.index("Invoke-CheckedCommand $toolingPython -m pip install --force-reinstall --no-index")
    tests = checks.index("Invoke-CheckedCommand $toolingPython -m pytest tests/unit -q")
    assert build < install < tests
    assert "lotus_principal_authority" in _local_module_names()


def test_principal_distribution_dependency_guard_accepts_governed_and_refuses_drift() -> None:
    from automation.verify_principal_runtime_distribution import validate_dependency_config, BUILD_REQUIREMENTS
    config = tomllib.loads((ROOT / "packages/principal-authority/pyproject.toml").read_text(encoding="utf-8"))
    lock = (AUTOMATION / "requirements.platform-automation.lock.txt").read_text(encoding="utf-8")
    pins = dict(line.split("==") for line in lock.splitlines() if "==" in line)
    installed = {name: pins[name] for name in BUILD_REQUIREMENTS}
    validate_dependency_config(config, lock, installed)
    for bad_lock in (lock.replace("cffi==2.0.0", ""), lock.replace("setuptools==83.0.0", "")):
        with pytest.raises(ValueError):
            validate_dependency_config(config, bad_lock, installed)
    with pytest.raises(ValueError):
        validate_dependency_config(config, lock, dict(installed, wheel="0.0.0"))
    altered = copy.deepcopy(config)
    altered["project"]["dependencies"] = []
    with pytest.raises(ValueError):
        validate_dependency_config(altered, lock, installed)
