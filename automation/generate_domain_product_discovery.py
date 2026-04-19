from __future__ import annotations

import argparse
from pathlib import Path

from domain_product_discovery import (
    DEFAULT_DECLARATION_DIRECTORY,
    DEFAULT_OUTPUT_DIRECTORY,
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
    args = parser.parse_args(argv)

    write_discovery_artifacts(
        args.output_directory,
        args.declaration_directory,
        generated_at_utc=args.generated_at_utc,
    )
    print(
        "Generated domain-product discovery artifacts in "
        f"{args.output_directory.resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
