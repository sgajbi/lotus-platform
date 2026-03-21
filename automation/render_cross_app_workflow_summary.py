from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


_JSON_BY_TARGET = {
    "baseline": "core-performance-baseline-validation.json",
    "twr_benchmark": "core-performance-twr-benchmark-validation.json",
    "returns_series": "core-performance-returns-series-validation.json",
    "contribution": "core-performance-contribution-validation.json",
    "attribution": "core-performance-attribution-validation.json",
    "mwr": "core-performance-mwr-validation.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _bullet(label: str, value: Any) -> str:
    return f"- {label}: `{value}`"


def _format_defects(defects: list[dict[str, Any]]) -> list[str]:
    if not defects:
        return ["- none"]
    lines: list[str] = []
    for defect in defects:
        app = defect.get("app", "unknown")
        code = defect.get("code", "UNKNOWN")
        message = defect.get("message", "")
        lines.append(f"- `{app}` `{code}`: {message}")
    return lines


def _render_baseline(target: str, payload: dict[str, Any]) -> str:
    validators = payload.get("validators", [])
    defects = payload.get("defects", [])
    lines = [
        f"## Cross-App Validation Summary: `{target}`",
        "",
        _bullet("Status", payload.get("status", "unknown")),
        _bullet("Mode", payload.get("mode", "unknown")),
        _bullet("Shared scenario suffix", payload.get("shared_scenario_suffix", "n/a")),
        _bullet("MWR scenario suffix", payload.get("mwr_scenario_suffix", "n/a")),
        "",
        "### Validators",
        "",
    ]
    if isinstance(validators, list) and validators:
        for validator in validators:
            if not isinstance(validator, dict):
                continue
            lines.append(
                f"- `{validator.get('key', 'unknown')}` status=`{validator.get('status', 'unknown')}` exit_code=`{validator.get('exit_code', 'unknown')}`"
            )
    else:
        lines.append("- none")
    lines.extend(["", "### Defects", ""])
    if isinstance(defects, list):
        lines.extend(_format_defects([item for item in defects if isinstance(item, dict)]))
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def _render_single(target: str, payload: dict[str, Any]) -> str:
    performance = payload.get("performance", {})
    core = payload.get("core", {})
    scenario = payload.get("scenario", {})
    performance_defects = performance.get("defects", []) if isinstance(performance, dict) else []
    core_defects = payload.get("core_defects", [])

    lines = [
        f"## Cross-App Validation Summary: `{target}`",
        "",
        _bullet("Status", payload.get("status", "unknown")),
        _bullet("Scenario seed mode", payload.get("scenario_seed_mode", "unknown")),
        _bullet("Portfolio", scenario.get("portfolio_id", "n/a") if isinstance(scenario, dict) else "n/a"),
        _bullet("Benchmark", scenario.get("benchmark_id", "n/a") if isinstance(scenario, dict) else "n/a"),
    ]

    if isinstance(core, dict):
        if "portfolio_timeseries_observations" in core:
            lines.append(_bullet("Portfolio timeseries observations", core["portfolio_timeseries_observations"]))
        if "position_timeseries_rows" in core:
            lines.append(_bullet("Position timeseries rows", core["position_timeseries_rows"]))

    if isinstance(performance, dict):
        benchmark_context = performance.get("benchmark_context")
        if isinstance(benchmark_context, dict):
            lines.append(_bullet("Resolved benchmark", benchmark_context.get("benchmark_id", "n/a")))
            lines.append(_bullet("Benchmark return source", benchmark_context.get("return_source", "n/a")))
        for metric_key in (
            "twr_itd_portfolio_base_return",
            "twr_itd_benchmark_base_return",
            "twr_itd_relative_base_return",
            "benchmark_endpoint_itd_base_return",
            "mwr_percent_return",
            "contribution_total_portfolio_return",
            "contribution_total_contribution",
            "attribution_total_active_return",
        ):
            if metric_key in performance:
                lines.append(_bullet(metric_key, performance[metric_key]))

    lines.extend(["", "### Defects", ""])
    merged_defects: list[dict[str, Any]] = []
    if isinstance(performance_defects, list):
        merged_defects.extend(item for item in performance_defects if isinstance(item, dict))
    if isinstance(core_defects, list):
        merged_defects.extend(item for item in core_defects if isinstance(item, dict))
    lines.extend(_format_defects(merged_defects))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target",
        required=True,
        choices=sorted(_JSON_BY_TARGET.keys()),
    )
    parser.add_argument("--artifact-dir", default="output/cross-app")
    parser.add_argument("--output-markdown")
    args = parser.parse_args()

    artifact_dir = Path(args.artifact_dir)
    payload = _load_json(artifact_dir / _JSON_BY_TARGET[args.target])
    markdown = (
        _render_baseline(args.target, payload)
        if args.target == "baseline"
        else _render_single(args.target, payload)
    )

    if args.output_markdown:
        Path(args.output_markdown).write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
