from __future__ import annotations

import ast
import copy
import sys
import subprocess
import tomllib
import zipfile
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


@pytest.fixture
def tracked_package(tmp_path, monkeypatch):
    from automation import verify_principal_runtime_distribution as distribution

    def git(*args):
        return subprocess.run(["git", *args], cwd=tmp_path, capture_output=True, check=True).stdout

    package = tmp_path / "packages/principal-authority"
    package.mkdir(parents=True)
    (tmp_path / ".gitignore").write_text("__pycache__/\n*.egg-info/\n", encoding="utf-8")
    files = {"pyproject.toml": b"# tracked config\n", "src/lotus_principal_authority/__init__.py": b"# tracked module\n",
             "build inputs/notes.txt": b"# tracked input with spaces\n"}
    for relative, data in files.items():
        path = package / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    hooks = tmp_path / "empty-hooks"
    hooks.mkdir()
    git("init", "--object-format=sha1", "--template", str(hooks))
    git("config", "core.hooksPath", str(hooks))
    git("config", "core.autocrlf", "false")
    git("add", ".")
    git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
        "commit", "-m", "Tracked package inputs")
    monkeypatch.setattr(distribution, "ROOT", tmp_path)
    monkeypatch.setattr(distribution, "PACKAGE", package)
    return distribution, package, files, git


def test_package_inputs_ignore_generated_files_and_bind_every_tracked_blob(tracked_package, tmp_path):
    distribution, package, files, git = tracked_package
    for relative in ["src/lotus_principal_authority/__pycache__/generated.pyc", "src/generated.egg-info/PKG-INFO"]:
        path = package / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"generated")
    assert git("status", "--porcelain") == b""
    receipt = {"commands": [], "working_tree_status": ""}
    inputs = distribution.record_package_inputs(receipt)
    expected = {"packages/principal-authority/" + relative for relative in files}
    assert set(inputs) == set(receipt["source_files"]) == set(receipt["build_source_blobs"]) == expected
    for relative in expected:
        assert receipt["build_source_blobs"][relative] == git("rev-parse", "HEAD:" + relative).decode().strip()
    destination = tmp_path / "staged"
    # Staging uses the recorded bytes, even if the checkout changes afterwards.
    (package / "pyproject.toml").write_bytes(b"later edit")
    distribution.stage_package_inputs(inputs, destination)
    assert {p.relative_to(destination).as_posix(): p.read_bytes() for p in destination.rglob("*") if p.is_file()} == files


def test_package_inputs_refuse_missing_tracked_file(tracked_package):
    distribution, package, _, git = tracked_package
    (package / "pyproject.toml").unlink()
    with pytest.raises(FileNotFoundError):
        distribution.record_package_inputs({"commands": [], "working_tree_status": git("status", "--porcelain").decode()})


def test_package_inputs_refuse_clean_status_blob_mismatch(tracked_package):
    distribution, package, _, git = tracked_package
    git("update-index", "--assume-unchanged", "packages/principal-authority/pyproject.toml")
    (package / "pyproject.toml").write_bytes(b"changed behind clean status\n")
    assert git("status", "--porcelain") == b""
    with pytest.raises(ValueError, match="differs from selected committed blob"):
        distribution.record_package_inputs({"commands": [], "working_tree_status": ""})


def test_package_inputs_preserve_dirty_checkout_and_lf_staging(tracked_package, tmp_path):
    distribution, package, _, git = tracked_package
    (package / "pyproject.toml").write_bytes(b"changed checkout\r\n")
    status = git("status", "--porcelain").decode()
    assert status
    inputs = distribution.record_package_inputs({"commands": [], "working_tree_status": status})
    distribution.stage_package_inputs(inputs, tmp_path / "staged")
    assert (tmp_path / "staged/pyproject.toml").read_bytes() == b"changed checkout\n"


@pytest.mark.parametrize("case,expected_exit", [("valid", 0), ("missing", 1), ("altered", 1),
                                                ("malformed", 1), ("wrong-metadata", 1), ("changed-source", 1)])
def test_principal_wheel_guard_retains_native_exit_contract(tmp_path, case, expected_exit):
    from automation import verify_principal_runtime_distribution as distribution

    wheel = tmp_path / "runtime.whl"
    metadata = ("Name: lotus-principal-authority\nVersion: 0.1.0\nRequires-Python: >=3.12\n"
                "Requires-Dist: cryptography==49.0.0\n")
    if case == "wrong-metadata":
        metadata = metadata.replace("Version: 0.1.0", "Version: 9.9.9")
    with zipfile.ZipFile(wheel, "w") as archive:
        prefix = "lotus_principal_authority-0.1.0.dist-info/"
        archive.writestr(prefix + "METADATA", metadata)
        archive.writestr(prefix + "WHEEL", "Root-Is-Purelib: true\nTag: py3-none-any\n")
        for name in ["__init__", "verifier", "cli"]:
            path = "lotus_principal_authority/" + name + ".py"
            data = (distribution.PACKAGE / "src" / path).read_bytes().replace(b"\r\n", b"\n")
            if case == "changed-source" and name == "verifier":
                data += b"# altered module\n"
            archive.writestr(path, data)
    if case == "malformed":
        wheel.write_bytes(b"not a wheel")
    expected_sha = distribution.digest(wheel)
    if case == "altered":
        wheel.write_bytes(wheel.read_bytes() + b"altered")
    if case == "missing":
        wheel.unlink()
    result = subprocess.run([sys.executable, str(AUTOMATION / "verify_principal_runtime_distribution.py"),
                             "--wheel", str(wheel), "--sha256", expected_sha], cwd=tmp_path, capture_output=True)
    assert result.returncode == expected_exit, result.stderr.decode()
