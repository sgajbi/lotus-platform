from __future__ import annotations

import argparse
from pathlib import Path

from domain_product_certification import write_certification_report
from domain_product_discovery import (
    DEFAULT_CATALOG_PATH,
    DEFAULT_GRAPH_PATH,
    DEFAULT_OUTPUT_DIRECTORY,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate Lotus domain-product trust certification report artifacts from the "
            "generated catalog and dependency graph."
        )
    )
    parser.add_argument(
        "--catalog",
        default=DEFAULT_CATALOG_PATH,
        type=Path,
        help="Path to generated domain-product-catalog.json.",
    )
    parser.add_argument(
        "--graph",
        default=DEFAULT_GRAPH_PATH,
        type=Path,
        help="Path to generated domain-product-dependency-graph.json.",
    )
    parser.add_argument(
        "--output-directory",
        default=DEFAULT_OUTPUT_DIRECTORY,
        type=Path,
        help="Directory where certification report artifacts should be written.",
    )
    parser.add_argument(
        "--generated-at-utc",
        default=None,
        help="Optional UTC timestamp to stamp into generated outputs.",
    )
    args = parser.parse_args(argv)

    write_certification_report(
        args.output_directory,
        catalog_path=args.catalog,
        graph_path=args.graph,
        generated_at_utc=args.generated_at_utc,
    )
    print(
        "Generated domain-product certification report artifacts in "
        f"{args.output_directory.resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
