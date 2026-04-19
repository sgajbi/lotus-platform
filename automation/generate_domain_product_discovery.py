from __future__ import annotations

import argparse
from pathlib import Path

from domain_product_discovery import (
    DEFAULT_DECLARATION_DIRECTORY,
    DEFAULT_OUTPUT_DIRECTORY,
    DEFAULT_SOURCE_MANIFEST_PATH,
    check_discovery_artifacts,
    write_discovery_artifacts,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate Lotus domain-product discovery catalog and dependency graph artifacts."
    )
    parser.add_argument(
        "--declaration-directory",
        default=DEFAULT_DECLARATION_DIRECTORY,
        type=Path,
        help="Directory containing governed *-products.v1.json and *-consumers.v1.json declarations.",
    )
    parser.add_argument(
        "--output-directory",
        default=DEFAULT_OUTPUT_DIRECTORY,
        type=Path,
        help="Directory where generated discovery artifacts should be written.",
    )
    parser.add_argument(
        "--generated-at-utc",
        default=None,
        help="Optional UTC timestamp to stamp into generated outputs. Useful for deterministic tests.",
    )
    parser.add_argument(
        "--source-manifest",
        default=DEFAULT_SOURCE_MANIFEST_PATH,
        type=Path,
        help="Governed source manifest describing platform mirror and repo-native declaration sources.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether generated discovery artifacts are current without rewriting them.",
    )
    args = parser.parse_args(argv)

    if args.check:
        if args.generated_at_utc is None:
            parser.error("--check requires --generated-at-utc so output comparison is deterministic")
        issues = check_discovery_artifacts(
            args.output_directory,
            args.declaration_directory,
            generated_at_utc=args.generated_at_utc,
            source_manifest_path=args.source_manifest,
        )
        if issues:
            for issue in issues:
                print(issue)
            return 1
        print("Generated domain-product discovery artifacts are current")
        return 0

    write_discovery_artifacts(
        args.output_directory,
        args.declaration_directory,
        generated_at_utc=args.generated_at_utc,
        source_manifest_path=args.source_manifest,
    )
    print(
        "Generated domain-product discovery artifacts in "
        f"{args.output_directory.resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
