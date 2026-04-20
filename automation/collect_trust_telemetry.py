from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Literal

from validate_trust_telemetry import (
    DEFAULT_CATALOG_PATH,
    _iter_telemetry_paths,
    _load_validation_context,
    validate_trust_telemetry_snapshot,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIRECTORY = ROOT / "output" / "trust-telemetry" / "collection"
SNAPSHOT_DIRECTORY_NAME = "snapshots"
COLLECTION_MANIFEST_FILENAME = "trust-telemetry-collection-manifest.json"
SourceMode = Literal["runtime", "static_fixture"]

REQUIRED_PRODUCTS = {
    "lotus-core:PortfolioStateSnapshot:v1": "lotus-core",
    "lotus-performance:ReturnsSeriesBundle:v1": "lotus-performance",
    "lotus-risk:RiskMetricsReport:v1": "lotus-risk",
    "lotus-advise:AdvisoryProposalLifecycleRecord:v1": "lotus-advise",
}
DEFAULT_RUNTIME_DIRECTORIES = [
    ROOT.parent / repository / "output" / "trust-telemetry" / "runtime"
    for repository in sorted(set(REQUIRED_PRODUCTS.values()))
]
DEFAULT_FIXTURE_DIRECTORIES = [
    ROOT.parent / repository / "contracts" / "trust-telemetry"
    for repository in sorted(set(REQUIRED_PRODUCTS.values()))
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _product_safe_name(product_id: str) -> str:
    return (
        product_id.replace(":", "__")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )


def _candidate_paths(paths: list[Path]) -> list[Path]:
    discovered: list[Path] = []
    for path in paths:
        if path.exists():
            discovered.extend(_iter_telemetry_paths(path))
    return sorted(set(discovered))


def _add_issue(
    issues: list[dict[str, str]],
    *,
    code: str,
    severity: Literal["error", "warning", "info"],
    product_id: str | None,
    detail: str,
    source_path: Path | str,
) -> None:
    issues.append(
        {
            "code": code,
            "severity": severity,
            "product_id": product_id or "unknown",
            "detail": detail,
            "source_path": str(source_path).replace("\\", "/"),
        }
    )


def _load_candidates(
    *,
    paths: list[Path],
    source_mode: SourceMode,
    context: dict[str, Any],
    issues: list[dict[str, str]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for path in _candidate_paths(paths):
        try:
            payload = _load_json(path)
        except json.JSONDecodeError as exc:
            _add_issue(
                issues,
                code="invalid_json",
                severity="error",
                product_id=None,
                detail=f"Invalid trust telemetry JSON: {exc}",
                source_path=path,
            )
            continue

        product_id = payload.get("product_id")
        if not isinstance(product_id, str) or not product_id:
            _add_issue(
                issues,
                code="missing_product_id",
                severity="error",
                product_id=None,
                detail="Trust telemetry snapshot must include product_id.",
                source_path=path,
            )
            continue

        validation_issues = validate_trust_telemetry_snapshot(
            path,
            payload,
            context=context,
        )
        if validation_issues:
            for validation_issue in validation_issues:
                _add_issue(
                    issues,
                    code="invalid_snapshot",
                    severity="error",
                    product_id=product_id,
                    detail=validation_issue,
                    source_path=path,
                )
            continue

        candidates.append(
            {
                "product_id": product_id,
                "producer_repository": payload.get("producer_repository"),
                "source_mode": source_mode,
                "source_path": path,
                "payload": payload,
            }
        )
    return candidates


def _select_candidates(
    candidates: list[dict[str, Any]],
    issues: list[dict[str, str]],
) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for candidate in sorted(
        candidates,
        key=lambda item: (
            0 if item["source_mode"] == "runtime" else 1,
            item["product_id"],
            item["source_path"].as_posix(),
        ),
    ):
        product_id = candidate["product_id"]
        if product_id in selected:
            if candidate["source_mode"] == selected[product_id]["source_mode"]:
                _add_issue(
                    issues,
                    code="duplicate_snapshot",
                    severity="error",
                    product_id=product_id,
                    detail=(
                        "Multiple snapshots exist for the same product and source mode; "
                        "publish one authoritative snapshot."
                    ),
                    source_path=candidate["source_path"],
                )
            continue
        selected[product_id] = candidate
    return selected


def collect_trust_telemetry(
    *,
    runtime_directories: list[Path] | None = None,
    fixture_directories: list[Path] | None = None,
    output_directory: Path = DEFAULT_OUTPUT_DIRECTORY,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    generated_at_utc: str,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    context = _load_validation_context(catalog_path=catalog_path)
    runtime_paths = runtime_directories or DEFAULT_RUNTIME_DIRECTORIES
    fixture_paths = fixture_directories or DEFAULT_FIXTURE_DIRECTORIES
    candidates = [
        *_load_candidates(
            paths=runtime_paths,
            source_mode="runtime",
            context=context,
            issues=issues,
        ),
        *_load_candidates(
            paths=fixture_paths,
            source_mode="static_fixture",
            context=context,
            issues=issues,
        ),
    ]
    selected = _select_candidates(candidates, issues)

    snapshot_output_directory = output_directory / SNAPSHOT_DIRECTORY_NAME
    if snapshot_output_directory.exists():
        shutil.rmtree(snapshot_output_directory)
    snapshot_output_directory.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, Any]] = []
    for product_id in sorted(selected):
        candidate = selected[product_id]
        collected_path = (
            snapshot_output_directory / f"{_product_safe_name(product_id)}.json"
        )
        shutil.copy2(candidate["source_path"], collected_path)
        source_mode = candidate["source_mode"]
        entries.append(
            {
                "product_id": product_id,
                "producer_repository": candidate["producer_repository"],
                "selected_source_mode": source_mode,
                "source_path": candidate["source_path"].as_posix(),
                "collected_path": collected_path.as_posix(),
                "fixture_fallback": source_mode == "static_fixture",
                "fallback_reason": (
                    "No runtime telemetry snapshot was available for this product."
                    if source_mode == "static_fixture"
                    else None
                ),
            }
        )

    for product_id, repository in REQUIRED_PRODUCTS.items():
        if product_id not in selected:
            _add_issue(
                issues,
                code="missing_required_product",
                severity="error",
                product_id=product_id,
                detail=(
                    "No runtime or static fixture telemetry snapshot was found for "
                    f"required producer {repository}."
                ),
                source_path=repository,
            )

    manifest = {
        "contract_id": "lotus-trust-telemetry-collection-manifest",
        "contract_version": "1.0.0",
        "governed_by_rfcs": ["RFC-0087", "RFC-0091"],
        "generated_at_utc": generated_at_utc,
        "source_selection_policy": "runtime_preferred_static_fixture_fallback",
        "summary": {
            "selected_snapshot_count": len(entries),
            "runtime_snapshot_count": sum(
                1 for entry in entries if entry["selected_source_mode"] == "runtime"
            ),
            "static_fixture_snapshot_count": sum(
                1
                for entry in entries
                if entry["selected_source_mode"] == "static_fixture"
            ),
            "missing_required_product_count": sum(
                1 for issue in issues if issue["code"] == "missing_required_product"
            ),
            "issue_count": len(issues),
            "error_count": sum(1 for issue in issues if issue["severity"] == "error"),
        },
        "runtime_directories": [path.as_posix() for path in runtime_paths],
        "fixture_directories": [path.as_posix() for path in fixture_paths],
        "snapshots": entries,
        "issues": sorted(
            issues,
            key=lambda issue: (
                {"error": 0, "warning": 1, "info": 2}[issue["severity"]],
                issue["product_id"],
                issue["code"],
            ),
        ),
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    (output_directory / COLLECTION_MANIFEST_FILENAME).write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Collect RFC-0087 trust telemetry snapshots for RFC-0091 certification. "
            "Runtime snapshots are preferred; static fixtures are explicit fallbacks."
        )
    )
    parser.add_argument("--runtime-directory", action="append", type=Path, default=[])
    parser.add_argument("--fixture-directory", action="append", type=Path, default=[])
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
    )
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--generated-at-utc", required=True)
    args = parser.parse_args(argv)

    manifest = collect_trust_telemetry(
        runtime_directories=args.runtime_directory or None,
        fixture_directories=args.fixture_directory or None,
        output_directory=args.output_directory,
        catalog_path=args.catalog,
        generated_at_utc=args.generated_at_utc,
    )
    summary = manifest["summary"]
    print(
        "Collected "
        f"{summary['selected_snapshot_count']} trust telemetry snapshot(s): "
        f"{summary['runtime_snapshot_count']} runtime, "
        f"{summary['static_fixture_snapshot_count']} static fixture fallback(s)."
    )
    print(
        "Wrote trust telemetry collection manifest to "
        f"{(args.output_directory / COLLECTION_MANIFEST_FILENAME).resolve()}"
    )
    return 1 if summary["error_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
