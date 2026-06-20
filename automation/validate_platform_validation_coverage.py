from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTOMATION_ROOT = ROOT / "automation"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_profiles() -> dict[str, object]:
    return json.loads((AUTOMATION_ROOT / "platform-validation-profiles.json").read_text(encoding="utf-8"))


def _validate_profile_targets(
    *,
    errors: list[str],
    name: str,
    targets: object,
) -> None:
    if not isinstance(targets, list) or not targets:
        errors.append(f"platform-validation-profiles.json: profile `{name}` missing non-empty `targets`")
        return

    for target in targets:
        if not isinstance(target, dict):
            errors.append(f"platform-validation-profiles.json: profile `{name}` has a non-object target")
            continue
        for field in ("name", "uses_shared_suffix", "uses_mwr_suffix"):
            if field not in target:
                errors.append(
                    f"platform-validation-profiles.json: profile `{name}` target missing `{field}`"
                )


def _validate_profile_references(
    *,
    errors: list[str],
    name: str,
    workflow: str,
    entrypoint: str,
    standard: str,
) -> None:
    if name not in workflow:
        errors.append(
            f"platform-end-to-end-validation.yml: profile option `{name}` missing from workflow dispatch"
        )
    if name not in entrypoint:
        errors.append(
            f"Invoke-PlatformValidationLane.ps1: profile `{name}` missing from validation entrypoint"
        )
    if name not in standard:
        errors.append(
            f"Platform-End-to-End-Validation-Coverage-Standard.md: profile `{name}` missing from standard"
        )


def _validate_profile(
    *,
    errors: list[str],
    profile: object,
    workflow: str,
    entrypoint: str,
    standard: str,
) -> None:
    if not isinstance(profile, dict):
        errors.append("platform-validation-profiles.json: each profile must be an object")
        return

    name = profile.get("name")
    description = profile.get("description")
    required_artifacts = profile.get("required_artifacts")

    if not isinstance(name, str) or not name:
        errors.append("platform-validation-profiles.json: each profile requires a non-empty `name`")
        return

    if not isinstance(description, str) or not description:
        errors.append(f"platform-validation-profiles.json: profile `{name}` missing `description`")

    _validate_profile_targets(errors=errors, name=name, targets=profile.get("targets"))

    if not isinstance(required_artifacts, list) or not required_artifacts:
        errors.append(
            f"platform-validation-profiles.json: profile `{name}` missing non-empty `required_artifacts`"
        )

    _validate_profile_references(
        errors=errors,
        name=name,
        workflow=workflow,
        entrypoint=entrypoint,
        standard=standard,
    )


def _validate_manifest_driven_entrypoint(
    entrypoint: str,
    errors: list[str],
) -> None:
    if "platform-validation-profiles.json" not in entrypoint:
        errors.append("Invoke-PlatformValidationLane.ps1: must resolve profiles from platform-validation-profiles.json")
    if "$validationRuns = @($selectedProfile.targets)" not in entrypoint:
        errors.append("Invoke-PlatformValidationLane.ps1: must execute targets from the manifest-driven profile")
    if "$target = $validationRun.name" not in entrypoint:
        errors.append("Invoke-PlatformValidationLane.ps1: must read target names from the manifest-driven profile")


def validate_platform_validation_coverage() -> list[str]:
    errors: list[str] = []
    manifest = _load_profiles()
    workflow = _read_text(ROOT / ".github" / "workflows" / "platform-end-to-end-validation.yml")
    entrypoint = _read_text(AUTOMATION_ROOT / "Invoke-PlatformValidationLane.ps1")
    standard = _read_text(
        ROOT / "platform-standards" / "Platform-End-to-End-Validation-Coverage-Standard.md"
    )

    profiles = manifest.get("profiles", [])
    if not isinstance(profiles, list) or not profiles:
        errors.append("platform-validation-profiles.json: missing non-empty `profiles` list")
        return errors

    for profile in profiles:
        _validate_profile(
            errors=errors,
            profile=profile,
            workflow=workflow,
            entrypoint=entrypoint,
            standard=standard,
        )

    _validate_manifest_driven_entrypoint(entrypoint, errors)

    return errors


def main() -> int:
    errors = validate_platform_validation_coverage()
    if errors:
        print("Platform validation coverage contract failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Platform validation coverage contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
