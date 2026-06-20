from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTOMATION_DIR = ROOT / "automation"
QUALITY_DIR = ROOT / "quality"
INVENTORY_JSON = QUALITY_DIR / "automation_inventory.json"
INVENTORY_MD = QUALITY_DIR / "automation_inventory.md"

SCRIPT_SUFFIXES = {".ps1", ".py"}
REFERENCE_ROOTS = (
    "automation",
    "tests",
    "context",
    "docs",
    "wiki",
)
REFERENCE_FILES = (
    ROOT / "README.md",
    ROOT / "REPOSITORY-ENGINEERING-CONTEXT.md",
)
TEXT_SUFFIXES = {".json", ".md", ".ps1", ".py", ".txt", ".yaml", ".yml"}
EXCLUDED_PARTS = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__", "output"}


@dataclass(frozen=True)
class AutomationEntry:
    path: str
    suffix: str
    reference_count: int
    test_reference_count: int
    operator_doc_reference_count: int
    classification: str


def _is_text_file(path: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    return path.is_file() and path.suffix.lower() in TEXT_SUFFIXES


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def _iter_reference_files() -> list[Path]:
    files: list[Path] = []
    for root_name in REFERENCE_ROOTS:
        root = ROOT / root_name
        if root.exists():
            files.extend(path for path in root.rglob("*") if _is_text_file(path))
    files.extend(path for path in REFERENCE_FILES if path.exists())
    return sorted(set(files))


def _classify(reference_count: int, test_reference_count: int, operator_doc_reference_count: int) -> str:
    if reference_count <= 1:
        return "review"
    if test_reference_count == 0 and operator_doc_reference_count == 0:
        return "undocumented"
    return "covered"


def collect_inventory() -> dict[str, object]:
    scripts = sorted(
        path
        for path in AUTOMATION_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SCRIPT_SUFFIXES
    )
    reference_files = _iter_reference_files()
    reference_text = {
        path: _read_text(path)
        for path in reference_files
    }

    entries: list[AutomationEntry] = []
    for script in scripts:
        name = script.name
        reference_tokens = {name, script.stem}
        references = [
            path
            for path, text in reference_text.items()
            if path != script and any(token in text for token in reference_tokens)
        ]
        test_references = [path for path in references if "tests" in path.relative_to(ROOT).parts]
        operator_doc_references = [
            path
            for path in references
            if path == ROOT / "README.md"
            or path == ROOT / "REPOSITORY-ENGINEERING-CONTEXT.md"
            or path.relative_to(ROOT).parts[0] in {"context", "docs", "wiki"}
        ]
        entries.append(
            AutomationEntry(
                path=script.relative_to(ROOT).as_posix(),
                suffix=script.suffix.lower(),
                reference_count=len(references),
                test_reference_count=len(test_references),
                operator_doc_reference_count=len(operator_doc_references),
                classification=_classify(
                    len(references),
                    len(test_references),
                    len(operator_doc_references),
                ),
            )
        )

    classification_counts: dict[str, int] = {}
    for entry in entries:
        classification_counts[entry.classification] = classification_counts.get(entry.classification, 0) + 1

    return {
        "generated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "script_count": len(entries),
        "classification_counts": classification_counts,
        "entries": [asdict(entry) for entry in entries],
    }


def render_inventory_markdown(inventory: dict[str, object]) -> str:
    entries = list(inventory["entries"])
    review_entries = [
        entry
        for entry in entries
        if entry["classification"] in {"review", "undocumented"}
    ]
    review_entries = sorted(
        review_entries,
        key=lambda entry: (entry["reference_count"], entry["path"]),
    )[:30]
    rows = [
        "| Script | References | Tests | Operator docs | Classification |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for entry in review_entries:
        rows.append(
            "| {path} | {reference_count} | {test_reference_count} | "
            "{operator_doc_reference_count} | {classification} |".format(**entry)
        )
    if not review_entries:
        rows.append("| None | 0 | 0 | 0 | covered |")

    counts = inventory["classification_counts"]
    return f"""# Automation Inventory

Generated: `{inventory["generated_at_utc"]}`

This report is a cleanup aid. `review` and `undocumented` entries are candidates for
documentation, consolidation, tests, or removal after behavior-specific evidence is inspected.

## Summary

- Scripts inventoried: `{inventory["script_count"]}`
- Covered: `{counts.get("covered", 0)}`
- Undocumented: `{counts.get("undocumented", 0)}`
- Review candidates: `{counts.get("review", 0)}`

## Lowest-Discoverability Scripts

{chr(10).join(rows)}
"""


def write_inventory(inventory: dict[str, object]) -> None:
    QUALITY_DIR.mkdir(exist_ok=True)
    INVENTORY_JSON.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    INVENTORY_MD.write_text(render_inventory_markdown(inventory), encoding="utf-8")


def validate_inventory_surface() -> list[str]:
    errors: list[str] = []
    for path in (INVENTORY_JSON, INVENTORY_MD):
        if not path.exists():
            errors.append(f"missing automation inventory artifact: {path.relative_to(ROOT).as_posix()}")
    if not errors:
        inventory = json.loads(INVENTORY_JSON.read_text(encoding="utf-8"))
        if inventory.get("script_count", 0) <= 0:
            errors.append("automation inventory has no scripts")
        if "entries" not in inventory:
            errors.append("automation inventory missing entries")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or validate Lotus platform automation inventory.")
    parser.add_argument("--write", action="store_true", help="Write quality/automation_inventory.* artifacts.")
    parser.add_argument("--check", action="store_true", help="Validate that inventory artifacts exist and are shaped.")
    args = parser.parse_args()

    if args.write:
        write_inventory(collect_inventory())
        print("Automation inventory generated.")

    if args.check:
        errors = validate_inventory_surface()
        if errors:
            for error in errors:
                print(error)
            return 1
        print("Automation inventory validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
