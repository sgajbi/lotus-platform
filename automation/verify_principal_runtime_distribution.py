"""Build and qualify the single principal runtime through an isolated wheel install."""

from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
import os
from email.parser import BytesParser
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages" / "principal-authority"
NAME = "lotus-principal-authority"
VERSION = "0.1.0"
RUNTIME_REQUIREMENTS = ("cryptography==49.0.0", "cffi==2.0.0", "pycparser==3.0")
BUILD_REQUIREMENTS = ("build", "setuptools", "wheel", "packaging", "pyproject_hooks")


def validate_dependency_config(config: dict, lock: str, installed: dict[str, str]) -> None:
    pins = {line.strip() for line in lock.splitlines() if line.strip() and not line.startswith("#")}
    if not set(RUNTIME_REQUIREMENTS) <= pins:
        raise ValueError("runtime closure is not governed by the automation lock")
    project = config["project"]
    if project["name"] != NAME or project["version"] != VERSION or project["dependencies"] != [RUNTIME_REQUIREMENTS[0]]:
        raise ValueError("unexpected package dependency identity")
    if not set(config["build-system"]["requires"]) <= pins:
        raise ValueError("build backend requirements are not locked")
    if set(installed) != set(BUILD_REQUIREMENTS) or any(f"{name}=={version}" not in pins for name, version in installed.items()):
        raise ValueError("installed build tools differ from governed pins")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_wheel(path: Path, expected_sha256: str) -> dict:
    """Refuse absent, altered, malformed and misidentified distributions."""
    if not path.is_file() or digest(path) != expected_sha256:
        raise ValueError("wheel absent or SHA-256 mismatch")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1 or len(names) != len(set(names)):
            raise ValueError("ambiguous wheel metadata")
        metadata = BytesParser().parsebytes(archive.read(metadata_names[0]))
        if (
            metadata["Name"] != NAME or metadata["Version"] != VERSION
            or metadata["Requires-Python"] != ">=3.12"
            or metadata.get_all("Requires-Dist") != ["cryptography==49.0.0"]
        ):
            raise ValueError("unexpected runtime metadata")
        prefix = "lotus_principal_authority/"
        modules = {name for name in names if name.startswith(prefix)}
        expected = {prefix + name + ".py" for name in ("__init__", "verifier", "cli")}
        if modules != expected or any("automation/" in name or "examples/" in name for name in names):
            raise ValueError("unexpected runtime contents")
        for name in modules:
            if archive.read(name) != (PACKAGE / "src" / name).read_bytes().replace(b"\r\n", b"\n"):
                raise ValueError("wheel differs from selected source")
        wheel_metadata = archive.read(metadata_names[0].replace("METADATA", "WHEEL"))
        if b"Root-Is-Purelib: true" not in wheel_metadata or b"Tag: py3-none-any" not in wheel_metadata:
            raise ValueError("wheel is not platform independent")
    return {"name": NAME, "version": VERSION, "sha256": expected_sha256, "path": str(path)}


def checked(argv: list[str], cwd: Path, commands: list[dict], *, source_epoch: str | None = None) -> str:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    if source_epoch is not None:
        environment["SOURCE_DATE_EPOCH"] = source_epoch
    result = subprocess.run(argv, cwd=cwd, env=environment, text=True, capture_output=True)
    commands.append(dict(argv=argv, cwd=str(cwd), native_exit=result.returncode,
                         stdout=result.stdout, stderr=result.stderr))
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {argv[0]}")
    return result.stdout.strip()


def record_package_inputs(receipt: dict) -> dict[str, bytes]:
    """Bind the tracked package inputs once for receipts and build staging."""
    commands = receipt["commands"]
    tracked = checked(["git", "ls-files", "-z", "--", PACKAGE.relative_to(ROOT).as_posix()], ROOT, commands)
    inputs = {relative: (ROOT / relative).read_bytes() for relative in tracked.split("\0") if relative}
    if not inputs:
        raise ValueError("package has no tracked build inputs")
    receipt["source_files"] = {relative: hashlib.sha256(data).hexdigest() for relative, data in inputs.items()}
    receipt["build_source_blobs"] = {}
    for relative, data in inputs.items():
        normalized = data.replace(b"\r\n", b"\n")
        blob = hashlib.sha1(b"blob " + str(len(normalized)).encode() + b"\0" + normalized).hexdigest()
        receipt["build_source_blobs"][relative] = blob
        if not receipt["working_tree_status"]:
            committed = checked(["git", "rev-parse", f"HEAD:{relative}"], ROOT, commands)
            if committed != blob:
                raise ValueError("build input differs from selected committed blob")
    return inputs


def stage_package_inputs(inputs: dict[str, bytes], destination: Path) -> None:
    for relative, data in inputs.items():
        target = destination / (ROOT / relative).relative_to(PACKAGE)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Git's source blobs use LF; build the same pure wheel on Windows/Linux.
        target.write_bytes(data.replace(b"\r\n", b"\n"))


def qualify(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    receipt = dict(status="RUNNING", commands=[])
    commands = receipt["commands"]
    try:
        lock = (ROOT / "automation/requirements.platform-automation.lock.txt").read_text(encoding="utf-8")
        receipt["build_tools"] = {name: metadata.version(name) for name in BUILD_REQUIREMENTS}
        validate_dependency_config(tomllib.loads((PACKAGE / "pyproject.toml").read_text(encoding="utf-8")), lock, receipt["build_tools"])
        receipt["source_commit"] = checked(["git", "rev-parse", "HEAD"], ROOT, commands)
        receipt["source_tree"] = checked(["git", "rev-parse", "HEAD^{tree}"], ROOT, commands)
        receipt["source_date_epoch"] = checked(["git", "show", "-s", "--format=%ct", "HEAD"], ROOT, commands)
        receipt["working_tree_status"] = checked(["git", "status", "--porcelain"], ROOT, commands)
        inputs = record_package_inputs(receipt)
        receipt["dependency_lock_sha256"] = digest(ROOT / "automation/requirements.platform-automation.lock.txt")
        receipt["runtime_requirements"] = list(RUNTIME_REQUIREMENTS)
        with tempfile.TemporaryDirectory(prefix="lotus-principal-proof-") as scratch:
            outside = Path(scratch).resolve()
            build_source = outside / "package"
            stage_package_inputs(inputs, build_source)
            wheels = outside / "wheels"
            checked([sys.executable, "-m", "build", "--wheel", "--no-isolation", "--outdir", str(wheels), str(build_source)], outside, commands,
                    source_epoch=receipt["source_date_epoch"])
            built = list(wheels.glob("*.whl"))
            if len(built) != 1:
                raise ValueError("build must produce exactly one wheel")
            wheel = output / built[0].name
            shutil.copyfile(built[0], wheel)
            receipt["wheel"] = inspect_wheel(wheel, digest(wheel))
            # Execute the guard as a command too: good accepts, all bad cases fail.
            wrong = outside / "wrong-version.whl"
            with zipfile.ZipFile(wheel) as source, zipfile.ZipFile(wrong, "w") as target:
                for entry in source.infolist():
                    data = source.read(entry.filename)
                    if entry.filename.endswith(".dist-info/METADATA"):
                        data = data.replace(b"Version: 0.1.0", b"Version: 9.9.9")
                    target.writestr(entry, data)
            altered = outside / "altered.whl"
            altered.write_bytes(wheel.read_bytes() + b"tampered")
            malformed = outside / "malformed.whl"
            malformed.write_bytes(b"not a wheel")
            changed_source = outside / "changed-source.whl"
            with zipfile.ZipFile(wheel) as source, zipfile.ZipFile(changed_source, "w") as target:
                for entry in source.infolist():
                    data = source.read(entry.filename)
                    if entry.filename == "lotus_principal_authority/verifier.py":
                        data += b"\n# altered module\n"
                    target.writestr(entry, data)
            guards = [(wheel, digest(wheel), 0), (outside / "missing.whl", "0" * 64, 1),
                      (altered, digest(wheel), 1), (wrong, digest(wrong), 1),
                      (malformed, digest(malformed), 1), (changed_source, digest(changed_source), 1)]
            receipt["wheel_guard_cases"] = []
            for candidate, expected, exit_code in guards:
                argv = [sys.executable, str(Path(__file__).resolve()), "--wheel", str(candidate), "--sha256", expected]
                result = subprocess.run(argv, cwd=outside, text=True, capture_output=True)
                case = dict(case=candidate.name, argv=argv, native_exit=result.returncode, expected_exit=exit_code,
                            stdout=result.stdout, stderr=result.stderr)
                receipt["wheel_guard_cases"].append(case)
                if result.returncode != exit_code:
                    raise ValueError("wheel integrity guard failed its premise proof")
            wheelhouse = output / "dependencies"
            wheelhouse.mkdir(exist_ok=True)
            checked([sys.executable, "-m", "pip", "download", "--only-binary=:all:", "--dest", str(wheelhouse), *RUNTIME_REQUIREMENTS], outside, commands)
            receipt["dependency_wheels"] = {path.name: digest(path) for path in sorted(wheelhouse.glob("*.whl"))}
            environment = outside / "isolated"
            checked([sys.executable, "-m", "venv", str(environment)], outside, commands)
            python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            checked([str(python), "-I", "-m", "pip", "install", "--no-index", "--find-links", str(wheelhouse),
                     *RUNTIME_REQUIREMENTS, str(wheel)], outside, commands)
            receipt["installed_dependencies"] = json.loads(checked([str(python), "-I", "-m", "pip", "list", "--format=json"], outside, commands))
            installed = {item["name"].lower(): item["version"] for item in receipt["installed_dependencies"]}
            if any(installed.get(name) != version for name, version in (pin.split("==") for pin in RUNTIME_REQUIREMENTS)):
                raise ValueError("isolated runtime dependencies differ from governed pins")
            checked([str(python), "-I", "-m", "pip", "check"], outside, commands)
            probe = (
                "import pathlib,sys,lotus_principal_authority as p; "
                "import importlib.metadata as m; "
                "assert pathlib.Path(p.__file__).is_relative_to(sys.prefix); "
                "assert m.version('lotus-principal-authority')=='0.1.0'; print(p.__file__)"
            )
            receipt["installed_module"] = checked([str(python), "-I", "-c", probe], outside, commands)
            proof = outside / "capability_proof.py"
            shutil.copyfile(ROOT / "automation/principal_runtime_capability_proof.py", proof)
            receipt["capability_proof_sha256"] = digest(proof)
            checked([str(python), "-I", str(proof)], outside, commands)
            receipt["isolated_proof_cwd"] = str(outside)
        receipt["status"] = "PASS"
        return receipt
    except Exception as error:
        receipt["status"] = "FAIL"
        receipt["failure_type"] = type(error).__name__
        raise
    finally:
        (output / "qualification.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output/principal-runtime")
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--sha256")
    args = parser.parse_args()
    try:
        if args.wheel:
            if not args.sha256:
                raise ValueError("expected SHA-256 is required")
            result = inspect_wheel(args.wheel.resolve(), args.sha256)
        else:
            result = qualify(args.output.resolve())
        print(json.dumps({"status": "PASS", "wheel": result.get("wheel", result)}, sort_keys=True))
        return 0
    except (ValueError, RuntimeError, OSError, KeyError, metadata.PackageNotFoundError, zipfile.BadZipFile) as error:
        print(f"Principal runtime distribution refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
