"""Validate cross-application API vocabulary conformance.

This gate enforces a hybrid model:
1. Per-application inventories remain implementation-owned.
2. Platform-level validation ensures no semantic/canonical drift across apps.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

INVENTORY_GLOB = "*-api-vocabulary.v1.json"
SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
LEGACY_TERM_MAP: dict[str, str] = {
    "cif_id": "client_id",
    "booking_center": "booking_center_code",
}


@dataclass(frozen=True)
class AttrRef:
    application: str
    semantic_id: str
    canonical_term: str
    preferred_name: str


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _inventory_paths(root: Path) -> list[Path]:
    return sorted(p for p in root.glob(INVENTORY_GLOB) if p.is_file())


def validate_inventory_file(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    app = str(payload.get("application", "<missing-application>"))
    attrs = payload.get("attributeCatalog", [])
    if not isinstance(attrs, list):
        return [f"{path.name}: attributeCatalog must be a list"]

    seen_semantic: set[str] = set()
    for raw in attrs:
        if not isinstance(raw, dict):
            errors.append(f"{path.name}: attributeCatalog entries must be objects")
            continue
        semantic_id = str(raw.get("semanticId", "")).strip()
        canonical_term = str(raw.get("canonicalTerm", "")).strip()
        preferred_name = str(raw.get("preferredName", "")).strip()
        if not semantic_id:
            errors.append(f"{path.name}: missing semanticId entry in {app}")
            continue
        if semantic_id in seen_semantic:
            errors.append(f"{path.name}: duplicate semanticId in app inventory: {semantic_id}")
        seen_semantic.add(semantic_id)
        if canonical_term != preferred_name:
            errors.append(
                f"{path.name}: canonicalTerm/preferredName mismatch for {semantic_id}"
            )
        if not SNAKE_CASE_RE.fullmatch(canonical_term):
            errors.append(
                f"{path.name}: canonicalTerm must be snake_case for {semantic_id}: {canonical_term}"
            )
    return errors


def validate_cross_app(payloads: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    semantic_to_terms: dict[str, set[str]] = defaultdict(set)
    term_to_semantics: dict[str, set[str]] = defaultdict(set)
    term_to_apps: dict[str, set[str]] = defaultdict(set)
    refs: list[AttrRef] = []

    for payload in payloads:
        app = str(payload.get("application", "<missing-application>"))
        attrs = payload.get("attributeCatalog", [])
        if not isinstance(attrs, list):
            continue
        for raw in attrs:
            if not isinstance(raw, dict):
                continue
            semantic_id = str(raw.get("semanticId", "")).strip()
            canonical_term = str(raw.get("canonicalTerm", "")).strip()
            preferred_name = str(raw.get("preferredName", "")).strip()
            if not semantic_id or not canonical_term:
                continue
            refs.append(
                AttrRef(
                    application=app,
                    semantic_id=semantic_id,
                    canonical_term=canonical_term,
                    preferred_name=preferred_name,
                )
            )
            semantic_to_terms[semantic_id].add(canonical_term)
            term_to_semantics[canonical_term].add(semantic_id)
            term_to_apps[canonical_term].add(app)

    for semantic_id, terms in semantic_to_terms.items():
        if len(terms) > 1:
            errors.append(
                "cross-app drift: same semanticId has multiple canonical terms: "
                f"{semantic_id} -> {sorted(terms)}"
            )

    for canonical_term, semantic_ids in term_to_semantics.items():
        if len(semantic_ids) > 1:
            errors.append(
                "cross-app drift: same canonicalTerm maps to multiple semanticIds: "
                f"{canonical_term} -> {sorted(semantic_ids)}"
            )

    for legacy_term, canonical_term in LEGACY_TERM_MAP.items():
        if legacy_term in term_to_semantics and canonical_term in term_to_semantics:
            legacy_apps = ",".join(sorted(term_to_apps.get(legacy_term, set())))
            canonical_apps = ",".join(sorted(term_to_apps.get(canonical_term, set())))
            errors.append(
                "legacy/canonical conflict across inventories: "
                f"{legacy_term} (apps={legacy_apps}) vs {canonical_term} (apps={canonical_apps})"
            )

    return errors


def main() -> int:
    root = Path(__file__).resolve().parent
    paths = _inventory_paths(root)
    if not paths:
        print(f"No inventory files found under {root} using {INVENTORY_GLOB}")
        return 1

    payloads: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in paths:
        payload = _load_json(path)
        payloads.append(payload)
        errors.extend(validate_inventory_file(path, payload))

    errors.extend(validate_cross_app(payloads))

    if errors:
        print("API vocabulary catalog validation failed:")
        for err in errors:
            print(f" - {err}")
        return 1

    app_names = [str(p.get("application", "<unknown>")) for p in payloads]
    print(
        "API vocabulary catalog validation passed for apps: "
        + ", ".join(sorted(app_names))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
