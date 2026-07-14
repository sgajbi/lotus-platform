from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "platform-contracts" / "deployment-promotion"
SCHEMA_PATH = CONTRACT_DIR / "deployment-promotion-manifest.schema.json"
EXAMPLES_DIR = CONTRACT_DIR / "examples"
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_errors(schema_path: Path, manifest_path: Path) -> list[str]:
    schema = _load(schema_path)
    errors: list[str] = []
    _validate_schema_node(_load(manifest_path), schema, [manifest_path.name], errors)
    return errors


def _validate_schema_node(
    value: Any,
    schema: dict[str, Any],
    path: list[str],
    errors: list[str],
) -> None:
    if "const" in schema and value != schema["const"]:
        errors.append(f"{'.'.join(path)}: must be {schema['const']!r}")
        return

    expected_type = schema.get("type")
    if expected_type is not None and not _matches_schema_type(value, expected_type):
        errors.append(f"{'.'.join(path)}: invalid type")
        return

    enum = schema.get("enum")
    if enum is not None and value not in enum:
        errors.append(f"{'.'.join(path)}: must be one of {', '.join(enum)}")

    if isinstance(value, str):
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and not re.search(pattern, value):
            errors.append(f"{'.'.join(path)}: does not match pattern {pattern}")
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            errors.append(f"{'.'.join(path)}: is shorter than {min_length} characters")
        max_length = schema.get("maxLength")
        if isinstance(max_length, int) and len(value) > max_length:
            errors.append(f"{'.'.join(path)}: is longer than {max_length} characters")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for field in required:
            if field not in value:
                errors.append(f"{'.'.join(path)}: '{field}' is a required property")
        if schema.get("additionalProperties") is False:
            unexpected = sorted(set(value) - set(properties))
            if unexpected:
                quoted = ", ".join(repr(field) for field in unexpected)
                errors.append(
                    f"{'.'.join(path)}: Additional properties are not allowed ({quoted})"
                )
        for field, field_schema in properties.items():
            if field in value and isinstance(field_schema, dict):
                _validate_schema_node(value[field], field_schema, [*path, field], errors)

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{'.'.join(path)}: must contain at least {min_items} items")
        if schema.get("uniqueItems") is True:
            canonical_items = [json.dumps(item, sort_keys=True) for item in value]
            if len(set(canonical_items)) != len(canonical_items):
                errors.append(f"{'.'.join(path)}: items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_schema_node(item, item_schema, [*path, str(index)], errors)


def _matches_schema_type(value: Any, expected_type: str | list[str]) -> bool:
    if isinstance(expected_type, list):
        return any(_matches_schema_type(value, item) for item in expected_type)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    return False


def _image_ref_digest(image_ref: object) -> str | None:
    if not isinstance(image_ref, str) or image_ref.count("@sha256:") != 1:
        return None
    image_name, digest = image_ref.rsplit("@sha256:", 1)
    if not image_name or not HEX_SHA256.fullmatch(digest):
        return None
    final_component = image_name.rsplit("/", 1)[-1]
    if ":" in final_component:
        return None
    return f"sha256:{digest}"


def _has_digest_tag(image_ref: object) -> bool:
    if not isinstance(image_ref, str) or "@" not in image_ref:
        return False
    image_name = image_ref.split("@", 1)[0]
    return ":" in image_name.rsplit("/", 1)[-1]


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    release = manifest.get("release_evidence")
    if not isinstance(release, dict):
        return ["release_evidence must be an object"]

    release_digest = release.get("image_digest")
    if not isinstance(release_digest, str) or not SHA256.fullmatch(release_digest):
        errors.append("release_evidence.image_digest must be a lowercase SHA-256 digest")

    release_ref_digest = _image_ref_digest(release.get("image_ref"))
    if release_ref_digest is None:
        errors.append("release_evidence.image_ref must use image@sha256:<digest> without a tag")
    elif release_ref_digest != release_digest:
        errors.append("release_evidence.image_ref digest must match image_digest")

    policy = manifest.get("promotion_policy")
    if not isinstance(policy, dict):
        errors.append("promotion_policy must be an object")
    else:
        if policy.get("same_digest_required") is not True:
            errors.append("promotion_policy.same_digest_required must be true")
        if policy.get("mutable_tags_allowed") is not False:
            errors.append("promotion_policy.mutable_tags_allowed must be false")
        if policy.get("rebuild_between_environments_allowed") is not False:
            errors.append(
                "promotion_policy.rebuild_between_environments_allowed must be false"
            )

    if manifest.get("production_certification_claimed") is not False:
        errors.append(
            "production_certification_claimed must remain false until live deployment proof exists"
        )

    repository = manifest.get("repository")
    first_proof_set = manifest.get("first_proof_set")
    migration_order = manifest.get("migration_order")
    if isinstance(first_proof_set, list) and repository not in first_proof_set:
        errors.append("repository must appear in first_proof_set for this proof manifest")
    if not isinstance(migration_order, list) or repository not in migration_order:
        errors.append("repository must appear in migration_order")

    environments = manifest.get("environments")
    if not isinstance(environments, list):
        return errors + ["environments must be a list"]

    names = {
        env.get("name")
        for env in environments
        if isinstance(env, dict) and isinstance(env.get("name"), str)
    }
    included_digests: dict[str, str] = {}
    for index, env in enumerate(environments):
        if not isinstance(env, dict):
            errors.append(f"environments[{index}] must be an object")
            continue
        name = env.get("name", f"[{index}]")
        scope = env.get("scope")
        if env.get("rebuilt_in_environment") is not False:
            errors.append(f"environments[{index}] {name}: rebuilt_in_environment must be false")
        if scope == "included":
            errors.extend(_validate_included_environment(index, env, names, release_digest))
            digest = env.get("deployed_digest")
            if isinstance(name, str) and isinstance(digest, str):
                included_digests[name] = digest
        elif scope == "out_of_scope":
            errors.extend(_validate_out_of_scope_environment(index, env))
        else:
            errors.append(f"environments[{index}] {name}: scope must be included or out_of_scope")

    if len(set(included_digests.values())) > 1:
        errors.append("included environments must all deploy the same release digest")
    return errors


def _validate_included_environment(
    index: int,
    env: dict[str, Any],
    environment_names: set[str],
    release_digest: object,
) -> list[str]:
    errors: list[str] = []
    name = env.get("name", f"[{index}]")
    if env.get("promotion_mode") not in {
        "initial_deploy_from_release_evidence",
        "same_digest_promotion",
    }:
        errors.append(f"environments[{index}] {name}: promotion_mode is not included proof")
    deployed_digest = env.get("deployed_digest")
    if not isinstance(deployed_digest, str) or not SHA256.fullmatch(deployed_digest):
        errors.append(f"environments[{index}] {name}: deployed_digest must be a SHA-256 digest")
    deployed_ref_digest = _image_ref_digest(env.get("deployed_image_ref"))
    if deployed_ref_digest is None:
        errors.append(
            f"environments[{index}] {name}: deployed_image_ref must use image@sha256:<digest> "
            "without a tag"
        )
    elif deployed_ref_digest != deployed_digest:
        errors.append(f"environments[{index}] {name}: deployed_image_ref digest mismatch")
    if _has_digest_tag(env.get("deployed_image_ref")):
        errors.append(f"environments[{index}] {name}: mutable image tag is not allowed")
    if deployed_digest != release_digest:
        errors.append(f"environments[{index}] {name}: deployed_digest must match release evidence")
    if env.get("release_evidence_image_digest") != release_digest:
        errors.append(
            f"environments[{index}] {name}: release_evidence_image_digest must match "
            "release evidence"
        )
    source = env.get("source_environment")
    if env.get("promotion_mode") == "same_digest_promotion":
        if not isinstance(source, str) or source not in environment_names or source == name:
            errors.append(
                f"environments[{index}] {name}: same_digest_promotion requires a valid "
                "source_environment"
            )
    if env.get("out_of_scope_reason") is not None:
        errors.append(f"environments[{index}] {name}: included environment cannot be out_of_scope")
    return errors


def _validate_out_of_scope_environment(index: int, env: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    name = env.get("name", f"[{index}]")
    if env.get("promotion_mode") != "out_of_scope":
        errors.append(f"environments[{index}] {name}: out_of_scope must use out_of_scope mode")
    if env.get("deployed_image_ref") is not None or env.get("deployed_digest") is not None:
        errors.append(
            f"environments[{index}] {name}: out_of_scope must not declare deployed image proof"
        )
    reason = env.get("out_of_scope_reason")
    if not isinstance(reason, str) or len(reason.strip()) < 40:
        errors.append(f"environments[{index}] {name}: out_of_scope_reason is required")
    return errors


def validate_manifest_path(manifest_path: Path) -> list[str]:
    errors = _schema_errors(SCHEMA_PATH, manifest_path)
    if errors:
        return errors
    errors.extend(validate_manifest(_load(manifest_path)))
    return errors


def validate_all_manifests() -> list[str]:
    errors: list[str] = []
    for manifest_path in sorted(EXAMPLES_DIR.glob("*.json")):
        errors.extend(validate_manifest_path(manifest_path))
    if not list(EXAMPLES_DIR.glob("*.json")):
        errors.append("no deployment promotion manifest examples found")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Lotus deployment promotion manifests."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Manifest to validate. Defaults to all governed examples.",
    )
    args = parser.parse_args(argv)

    errors = validate_manifest_path(args.manifest) if args.manifest else validate_all_manifests()
    if errors:
        print("Deployment promotion manifest validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Deployment promotion manifests validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
