from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ValidationTarget:
    script_name: str
    output_json_name: str
    output_markdown_name: str
    supports_shared_suffix: bool
    supports_mwr_suffix: bool
    ingestion_base_url_arg: str
    query_base_url_arg: str


_TARGETS: dict[str, ValidationTarget] = {
    "baseline": ValidationTarget(
        script_name="core_performance_baseline_validation.py",
        output_json_name="core-performance-baseline-validation.json",
        output_markdown_name="core-performance-baseline-validation.md",
        supports_shared_suffix=True,
        supports_mwr_suffix=True,
        ingestion_base_url_arg="--core-ingestion-base-url",
        query_base_url_arg="--core-query-base-url",
    ),
    "twr_benchmark": ValidationTarget(
        script_name="core_performance_twr_benchmark_validation.py",
        output_json_name="core-performance-twr-benchmark-validation.json",
        output_markdown_name="core-performance-twr-benchmark-validation.md",
        supports_shared_suffix=True,
        supports_mwr_suffix=False,
        ingestion_base_url_arg="--ingestion-base-url",
        query_base_url_arg="--control-base-url",
    ),
    "returns_series": ValidationTarget(
        script_name="core_performance_returns_series_validation.py",
        output_json_name="core-performance-returns-series-validation.json",
        output_markdown_name="core-performance-returns-series-validation.md",
        supports_shared_suffix=True,
        supports_mwr_suffix=False,
        ingestion_base_url_arg="--core-ingestion-base-url",
        query_base_url_arg="--core-query-base-url",
    ),
    "contribution": ValidationTarget(
        script_name="core_performance_contribution_validation.py",
        output_json_name="core-performance-contribution-validation.json",
        output_markdown_name="core-performance-contribution-validation.md",
        supports_shared_suffix=True,
        supports_mwr_suffix=False,
        ingestion_base_url_arg="--core-ingestion-base-url",
        query_base_url_arg="--core-query-base-url",
    ),
    "attribution": ValidationTarget(
        script_name="core_performance_attribution_validation.py",
        output_json_name="core-performance-attribution-validation.json",
        output_markdown_name="core-performance-attribution-validation.md",
        supports_shared_suffix=True,
        supports_mwr_suffix=False,
        ingestion_base_url_arg="--core-ingestion-base-url",
        query_base_url_arg="--core-query-base-url",
    ),
    "mwr": ValidationTarget(
        script_name="core_performance_mwr_validation.py",
        output_json_name="core-performance-mwr-validation.json",
        output_markdown_name="core-performance-mwr-validation.md",
        supports_shared_suffix=False,
        supports_mwr_suffix=True,
        ingestion_base_url_arg="--core-ingestion-base-url",
        query_base_url_arg="--core-query-base-url",
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target",
        required=True,
        choices=sorted(_TARGETS.keys()),
        help="Cross-app validator target to execute.",
    )
    parser.add_argument(
        "--scenario-mode",
        choices=("fresh_seed", "skip_seed"),
        default="skip_seed",
        help="Use fresh ingestion or reuse an existing stable scenario.",
    )
    parser.add_argument("--shared-scenario-suffix")
    parser.add_argument("--mwr-scenario-suffix")
    parser.add_argument("--core-ingestion-base-url", default="http://127.0.0.1:8200")
    parser.add_argument("--core-query-base-url", default="http://127.0.0.1:8202")
    parser.add_argument("--performance-base-url", default="http://127.0.0.1:8002")
    parser.add_argument("--output-dir", default="output/cross-app")
    args = parser.parse_args()

    target = _TARGETS[args.target]
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = repo_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        str(repo_root / "automation" / target.script_name),
        "--output-json",
        str(output_dir / target.output_json_name),
        "--output-markdown",
        str(output_dir / target.output_markdown_name),
        target.ingestion_base_url_arg,
        args.core_ingestion_base_url,
        target.query_base_url_arg,
        args.core_query_base_url,
        "--performance-base-url",
        args.performance_base_url,
    ]

    if args.scenario_mode == "skip_seed":
        command.append("--skip-seed")
    if target.supports_shared_suffix and args.shared_scenario_suffix:
        suffix_arg = "--shared-scenario-suffix" if args.target == "baseline" else "--scenario-suffix"
        command.extend([suffix_arg, args.shared_scenario_suffix])
    if target.supports_mwr_suffix and args.mwr_scenario_suffix:
        suffix_arg = "--mwr-scenario-suffix" if args.target == "baseline" else "--scenario-suffix"
        command.extend([suffix_arg, args.mwr_scenario_suffix])

    completed = subprocess.run(command, cwd=repo_root, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
