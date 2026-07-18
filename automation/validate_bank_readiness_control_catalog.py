from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = (
    ROOT
    / "platform-contracts"
    / "bank-readiness"
    / "bank-ready-control-catalog.v1.json"
)
LENS_CATALOG = (
    ROOT
    / "codex"
    / "skills"
    / "lotus-app-issue-discovery"
    / "references"
    / "review-lenses.md"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version",
    "catalog_id",
    "catalog_version",
    "authority",
    "claim_boundary",
    "status_vocabulary",
    "maturity_levels",
    "completion_layers",
    "evidence_classes",
    "enforcement_postures",
    "repository_profiles",
    "environment_model",
    "external_references",
    "controls",
}
EXPECTED_STATUS_VOCABULARY = {
    "Implemented",
    "Partially implemented",
    "Planned",
    "Not applicable",
    "Unknown - requires owner review",
}
EXPECTED_COMPLETION_LAYERS = {
    "documented_design",
    "implementation_or_configuration",
    "positive_and_negative_verification",
    "regression_enforcement",
    "discoverable_evidence",
    "accountable_ownership",
}
EXPECTED_EVIDENCE_CLASSES = {
    "source_design_contract",
    "local_test_execution",
    "ci_execution",
    "runtime_execution",
    "deployment",
    "production_certification",
}
EXPECTED_ENFORCEMENT_POSTURES = {
    "report-only",
    "regression-blocking-candidate",
    "blocking-required-where-applicable",
}
EXPECTED_PROFILE_IDS = {
    "platform-governance",
    "product-ui",
    "experience-api",
    "source-domain-service",
    "analytics-service",
    "workflow-service",
    "shared-capability-service",
    "ai-capability",
}
EXPECTED_ENVIRONMENT_IDS = {
    "local",
    "ci",
    "shared-development",
    "test-uat",
    "production",
    "recovery",
}
EXPECTED_CONTROL_IDS = {f"BR-{index:03d}" for index in range(1, 26)}
EXPECTED_AUTHORITY = {
    "owner_repository": "lotus-platform",
    "human_standard": "platform-standards/LOTUS_BANK_READY_ENGINEERING_IMPLEMENTATION_PLAYBOOK.md",
    "standing_contract": "platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md",
    "validator": "automation/validate_bank_readiness_control_catalog.py",
}
CONTROL_KEYS = {
    "control_id",
    "slug",
    "title",
    "risk",
    "applicable_profiles",
    "applicability_condition",
    "local_expectations",
    "ci_expectations",
    "production_expectations",
    "evidence_requirements",
    "minimum_evidence_class",
    "issue_discovery_lenses",
    "external_reference_ids",
    "default_enforcement_posture",
    "owner_roles",
}
FORBIDDEN_UNQUALIFIED_CLAIMS = (
    "iso 27001 certified",
    "soc 2 certified",
    "soc 2 attested",
    "regulatory compliant",
    "regulator approved",
    "bank approved",
    "bank accepted",
    "penetration-test approved",
    "production certified",
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: root must be a JSON object")
    return payload


def _non_empty_strings(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def _ids(items: Any, key: str, path: str, errors: list[str]) -> set[str]:
    if not isinstance(items, list):
        errors.append(f"{path}: must be a list")
        return set()
    values: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get(key), str) or not item[key].strip():
            errors.append(f"{path}[{index}].{key}: must be a non-empty string")
            continue
        values.append(item[key])
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        errors.append(f"{path}: duplicate {key} values: {', '.join(duplicates)}")
    return set(values)


def _catalog_lens_labels(path: Path, errors: list[str]) -> set[str]:
    if not path.exists():
        errors.append(f"issue-discovery lens catalog is missing: {path}")
        return set()
    return set(re.findall(r"`(lens/[a-z0-9-]+)`", path.read_text(encoding="utf-8")))


def _validate_fixed_vocabulary(catalog: dict[str, Any], errors: list[str]) -> None:
    exact_sets = {
        "status_vocabulary": EXPECTED_STATUS_VOCABULARY,
        "completion_layers": EXPECTED_COMPLETION_LAYERS,
        "evidence_classes": EXPECTED_EVIDENCE_CLASSES,
        "enforcement_postures": EXPECTED_ENFORCEMENT_POSTURES,
    }
    for key, expected in exact_sets.items():
        value = catalog.get(key)
        actual = set(value) if isinstance(value, list) and all(isinstance(item, str) for item in value) else set()
        if actual != expected:
            errors.append(
                f"{key}: expected {sorted(expected)}, found {sorted(actual)}"
            )

    maturity = catalog.get("maturity_levels")
    maturity_ids = _ids(maturity, "id", "maturity_levels", errors)
    if maturity_ids != {f"M{index}" for index in range(6)}:
        errors.append(f"maturity_levels: expected M0 through M5, found {sorted(maturity_ids)}")
    if isinstance(maturity, list):
        evidence_by_id = {
            item.get("id"): item.get("minimum_evidence_class")
            for item in maturity
            if isinstance(item, dict)
        }
        expected_evidence = {
            "M0": "source_design_contract",
            "M1": "source_design_contract",
            "M2": "local_test_execution",
            "M3": "ci_execution",
            "M4": "runtime_execution",
            "M5": "production_certification",
        }
        if evidence_by_id != expected_evidence:
            errors.append(
                "maturity_levels: evidence progression must be source design, local tests, CI, "
                "runtime, and independent production certification"
            )


def _validate_profiles_and_environments(catalog: dict[str, Any], errors: list[str]) -> set[str]:
    profile_ids = _ids(catalog.get("repository_profiles"), "id", "repository_profiles", errors)
    if profile_ids != EXPECTED_PROFILE_IDS:
        errors.append(
            f"repository_profiles: expected {sorted(EXPECTED_PROFILE_IDS)}, found {sorted(profile_ids)}"
        )

    environment_ids = _ids(catalog.get("environment_model"), "id", "environment_model", errors)
    if environment_ids != EXPECTED_ENVIRONMENT_IDS:
        errors.append(
            f"environment_model: expected {sorted(EXPECTED_ENVIRONMENT_IDS)}, found {sorted(environment_ids)}"
        )
    for index, environment in enumerate(catalog.get("environment_model", [])):
        if not isinstance(environment, dict):
            continue
        for key in ("purpose", "data_boundary"):
            if not isinstance(environment.get(key), str) or not environment[key].strip():
                errors.append(f"environment_model[{index}].{key}: must be a non-empty string")
    return profile_ids


def _validate_external_references(catalog: dict[str, Any], errors: list[str]) -> set[str]:
    references = catalog.get("external_references")
    reference_ids = _ids(references, "id", "external_references", errors)
    if isinstance(references, list):
        for index, reference in enumerate(references):
            if not isinstance(reference, dict):
                continue
            for key in ("name", "url", "use_boundary"):
                if not isinstance(reference.get(key), str) or not reference[key].strip():
                    errors.append(f"external_references[{index}].{key}: must be a non-empty string")
            url = reference.get("url")
            if isinstance(url, str) and not url.startswith("https://"):
                errors.append(f"external_references[{index}].url: must use https")
    return reference_ids


def _walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for child in value for item in _walk_strings(child)]
    if isinstance(value, dict):
        return [item for child in value.values() for item in _walk_strings(child)]
    return []


def _validate_controls(
    catalog: dict[str, Any],
    profile_ids: set[str],
    reference_ids: set[str],
    lens_labels: set[str],
    errors: list[str],
) -> None:
    controls = catalog.get("controls")
    control_ids = _ids(controls, "control_id", "controls", errors)
    if control_ids != EXPECTED_CONTROL_IDS:
        errors.append(f"controls: expected BR-001 through BR-025, found {sorted(control_ids)}")
    if not isinstance(controls, list):
        return

    slugs: list[str] = []
    for index, control in enumerate(controls):
        path = f"controls[{index}]"
        if not isinstance(control, dict):
            errors.append(f"{path}: must be an object")
            continue
        keys = set(control)
        if keys != CONTROL_KEYS:
            missing = sorted(CONTROL_KEYS - keys)
            unexpected = sorted(keys - CONTROL_KEYS)
            errors.append(f"{path}: missing keys {missing}; unexpected keys {unexpected}")

        control_id = control.get("control_id")
        if not isinstance(control_id, str) or not re.fullmatch(r"BR-\d{3}", control_id):
            errors.append(f"{path}.control_id: must match BR-NNN")
        slug = control.get("slug")
        if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            errors.append(f"{path}.slug: must be lowercase hyphen-case")
        elif slug in slugs:
            errors.append(f"{path}.slug: duplicate slug {slug}")
        else:
            slugs.append(slug)

        for key in ("title", "risk", "applicability_condition"):
            if not isinstance(control.get(key), str) or not control[key].strip():
                errors.append(f"{path}.{key}: must be a non-empty string")
        for key in (
            "applicable_profiles",
            "local_expectations",
            "ci_expectations",
            "production_expectations",
            "evidence_requirements",
            "issue_discovery_lenses",
            "external_reference_ids",
            "owner_roles",
        ):
            if not _non_empty_strings(control.get(key)):
                errors.append(f"{path}.{key}: must be a non-empty list of non-empty strings")

        unknown_profiles = sorted(set(control.get("applicable_profiles", [])) - profile_ids)
        if unknown_profiles:
            errors.append(f"{path}.applicable_profiles: unknown profiles {unknown_profiles}")
        unknown_references = sorted(set(control.get("external_reference_ids", [])) - reference_ids)
        if unknown_references:
            errors.append(f"{path}.external_reference_ids: unknown references {unknown_references}")
        unknown_lenses = sorted(set(control.get("issue_discovery_lenses", [])) - lens_labels)
        if unknown_lenses:
            errors.append(f"{path}.issue_discovery_lenses: unknown lenses {unknown_lenses}")
        if control.get("minimum_evidence_class") not in EXPECTED_EVIDENCE_CLASSES:
            errors.append(f"{path}.minimum_evidence_class: unsupported evidence class")
        if control.get("default_enforcement_posture") not in EXPECTED_ENFORCEMENT_POSTURES:
            errors.append(f"{path}.default_enforcement_posture: unsupported posture")

        for text in _walk_strings(control):
            lowered = text.lower()
            for phrase in FORBIDDEN_UNQUALIFIED_CLAIMS:
                if phrase in lowered:
                    errors.append(f"{path}: unsupported unqualified claim contains '{phrase}'")


def validate_catalog(
    catalog: dict[str, Any],
    *,
    lens_catalog_path: Path = LENS_CATALOG,
) -> list[str]:
    errors: list[str] = []
    keys = set(catalog)
    if keys != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            f"catalog: missing keys {sorted(EXPECTED_TOP_LEVEL_KEYS - keys)}; "
            f"unexpected keys {sorted(keys - EXPECTED_TOP_LEVEL_KEYS)}"
        )
    if catalog.get("schema_version") != "1.0":
        errors.append("schema_version: expected 1.0")
    if catalog.get("catalog_id") != "lotus.bank-readiness.control-catalog":
        errors.append("catalog_id: expected lotus.bank-readiness.control-catalog")
    if not isinstance(catalog.get("catalog_version"), str) or not re.fullmatch(
        r"\d+\.\d+\.\d+", catalog["catalog_version"]
    ):
        errors.append("catalog_version: must be semantic version N.N.N")
    if catalog.get("authority") != EXPECTED_AUTHORITY:
        errors.append(f"authority: expected {EXPECTED_AUTHORITY}")
    boundary = catalog.get("claim_boundary")
    if not isinstance(boundary, str) or "does not claim" not in boundary.lower():
        errors.append("claim_boundary: must explicitly state that the catalog does not claim certification")

    _validate_fixed_vocabulary(catalog, errors)
    profile_ids = _validate_profiles_and_environments(catalog, errors)
    reference_ids = _validate_external_references(catalog, errors)
    lens_labels = _catalog_lens_labels(lens_catalog_path, errors)
    _validate_controls(catalog, profile_ids, reference_ids, lens_labels, errors)
    return errors


def validate_catalog_path(
    path: Path = DEFAULT_CATALOG,
    *,
    lens_catalog_path: Path = LENS_CATALOG,
) -> list[str]:
    try:
        catalog = _load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    return validate_catalog(catalog, lens_catalog_path=lens_catalog_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Lotus bank-readiness control catalog and its issue-discovery mappings."
    )
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--lens-catalog", type=Path, default=LENS_CATALOG)
    args = parser.parse_args()

    errors = validate_catalog_path(args.catalog, lens_catalog_path=args.lens_catalog)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Validated bank-readiness control catalog: {args.catalog}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
