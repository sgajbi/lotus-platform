from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class ValidatorSpec:
    key: str
    script_name: str
    output_json_name: str
    output_markdown_name: str
    scenario_mode: str
    ingestion_base_url_arg: str
    query_base_url_arg: str


_VALIDATORS: tuple[ValidatorSpec, ...] = (
    ValidatorSpec(
        key="twr_benchmark",
        script_name="core_performance_twr_benchmark_validation.py",
        output_json_name="core-performance-twr-benchmark-validation.json",
        output_markdown_name="core-performance-twr-benchmark-validation.md",
        scenario_mode="shared",
        ingestion_base_url_arg="--ingestion-base-url",
        query_base_url_arg="--control-base-url",
    ),
    ValidatorSpec(
        key="returns_series",
        script_name="core_performance_returns_series_validation.py",
        output_json_name="core-performance-returns-series-validation.json",
        output_markdown_name="core-performance-returns-series-validation.md",
        scenario_mode="shared",
        ingestion_base_url_arg="--core-ingestion-base-url",
        query_base_url_arg="--core-query-base-url",
    ),
    ValidatorSpec(
        key="contribution",
        script_name="core_performance_contribution_validation.py",
        output_json_name="core-performance-contribution-validation.json",
        output_markdown_name="core-performance-contribution-validation.md",
        scenario_mode="shared",
        ingestion_base_url_arg="--core-ingestion-base-url",
        query_base_url_arg="--core-query-base-url",
    ),
    ValidatorSpec(
        key="attribution",
        script_name="core_performance_attribution_validation.py",
        output_json_name="core-performance-attribution-validation.json",
        output_markdown_name="core-performance-attribution-validation.md",
        scenario_mode="shared",
        ingestion_base_url_arg="--core-ingestion-base-url",
        query_base_url_arg="--core-query-base-url",
    ),
    ValidatorSpec(
        key="mwr",
        script_name="core_performance_mwr_validation.py",
        output_json_name="core-performance-mwr-validation.json",
        output_markdown_name="core-performance-mwr-validation.md",
        scenario_mode="mwr",
        ingestion_base_url_arg="--core-ingestion-base-url",
        query_base_url_arg="--core-query-base-url",
    ),
)


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _infer_suffix_from_artifact(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        payload = _read_json(path)
    except Exception:
        return None
    scenario = payload.get("scenario")
    if not isinstance(scenario, dict):
        return None
    portfolio_id = scenario.get("portfolio_id")
    if not isinstance(portfolio_id, str) or "_" not in portfolio_id:
        return None
    return portfolio_id.rsplit("_", 1)[-1]


def _resolve_suffixes(
    *,
    output_dir: Path,
    shared_scenario_suffix: str | None,
    mwr_scenario_suffix: str | None,
    skip_seed: bool,
) -> tuple[str | None, str | None]:
    if not skip_seed:
        return shared_scenario_suffix, mwr_scenario_suffix

    resolved_shared = shared_scenario_suffix or _infer_suffix_from_artifact(
        output_dir / "core-performance-twr-benchmark-validation.json"
    )
    resolved_mwr = mwr_scenario_suffix or _infer_suffix_from_artifact(
        output_dir / "core-performance-mwr-validation.json"
    )
    return resolved_shared, resolved_mwr


def _run_validator(
    *,
    repo_root: Path,
    output_dir: Path,
    spec: ValidatorSpec,
    skip_seed: bool,
    scenario_suffix: str | None,
    core_ingestion_base_url: str,
    core_query_base_url: str,
    performance_base_url: str,
) -> dict[str, object]:
    output_json = output_dir / spec.output_json_name
    output_markdown = output_dir / spec.output_markdown_name
    command = [
        sys.executable,
        str(repo_root / "automation" / spec.script_name),
        "--output-json",
        str(output_json),
        "--output-markdown",
        str(output_markdown),
        spec.ingestion_base_url_arg,
        core_ingestion_base_url,
        spec.query_base_url_arg,
        core_query_base_url,
        "--performance-base-url",
        performance_base_url,
    ]
    if skip_seed:
        command.append("--skip-seed")
    if scenario_suffix:
        command.extend(["--scenario-suffix", scenario_suffix])

    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )

    result_payload: dict[str, object]
    if output_json.exists():
        result_payload = _read_json(output_json)
    else:
        result_payload = {
            "status": "failed",
            "performance": {
                "defects": [
                    {
                        "app": "lotus-platform",
                        "code": "VALIDATOR_DID_NOT_WRITE_OUTPUT",
                        "message": f"{spec.key} validator did not produce its JSON artifact.",
                        "evidence": completed.stderr or completed.stdout or "no_output",
                    }
                ]
            },
        }

    return {
        "key": spec.key,
        "script": spec.script_name,
        "scenario_mode": spec.scenario_mode,
        "scenario_suffix": scenario_suffix,
        "exit_code": completed.returncode,
        "status": result_payload.get("status", "failed"),
        "output_json": str(output_json),
        "output_markdown": str(output_markdown),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "result": result_payload,
    }


def _write_outputs(summary: dict[str, object], *, output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Cross-App Core -> Performance Baseline Validation",
        "",
        f"- Generated: {summary['generated_at_utc']}",
        f"- Status: {summary['status']}",
        f"- Mode: {summary['mode']}",
        f"- Shared scenario suffix: {summary['shared_scenario_suffix']}",
        f"- MWR scenario suffix: {summary['mwr_scenario_suffix']}",
        "",
        "## What This Covers",
        "",
        "- TWR + benchmark",
        "- returns-series",
        "- contribution",
        "- attribution",
        "- MWR",
        "",
        "## Validators",
        "",
    ]

    validators = summary["validators"]
    assert isinstance(validators, list)
    for validator in validators:
        assert isinstance(validator, dict)
        lines.extend(
            [
                f"- `{validator['key']}` status=`{validator['status']}` exit_code=`{validator['exit_code']}` scenario_suffix=`{validator['scenario_suffix']}`",
                f"  - JSON: `{validator['output_json']}`",
                f"  - Markdown: `{validator['output_markdown']}`",
            ]
        )

    lines.extend(["", "## Defects", ""])
    defects = summary["defects"]
    assert isinstance(defects, list)
    if defects:
        for defect in defects:
            assert isinstance(defect, dict)
            lines.extend(
                [
                    f"- `{defect['validator']}` `{defect['app']}` `{defect['code']}`: {defect['message']}",
                    f"  - Evidence: `{defect['evidence']}`",
                ]
            )
    else:
        lines.append("- none")

    output_markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-seed", action="store_true", help="Reuse existing seeded scenarios instead of ingesting fresh data.")
    parser.add_argument("--shared-scenario-suffix", help="Suffix for shared scenario validators (TWR, returns-series, contribution, attribution).")
    parser.add_argument("--mwr-scenario-suffix", help="Suffix for the MWR validator.")
    parser.add_argument("--core-ingestion-base-url", default="http://core-ingestion.dev.lotus")
    parser.add_argument("--core-query-base-url", default="http://core-control.dev.lotus")
    parser.add_argument("--performance-base-url", default="http://performance.dev.lotus")
    parser.add_argument("--output-json", default="output/cross-app/core-performance-baseline-validation.json")
    parser.add_argument("--output-markdown", default="output/cross-app/core-performance-baseline-validation.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output_dir = repo_root / "output" / "cross-app"
    shared_suffix, mwr_suffix = _resolve_suffixes(
        output_dir=output_dir,
        shared_scenario_suffix=args.shared_scenario_suffix,
        mwr_scenario_suffix=args.mwr_scenario_suffix,
        skip_seed=args.skip_seed,
    )

    if args.skip_seed and (shared_suffix is None or mwr_suffix is None):
        missing = []
        if shared_suffix is None:
            missing.append("shared_scenario_suffix")
        if mwr_suffix is None:
            missing.append("mwr_scenario_suffix")
        raise SystemExit(
            f"Stable baseline mode needs existing scenario suffixes or prior artifacts to infer them. Missing: {', '.join(missing)}"
        )

    validator_runs: list[dict[str, object]] = []
    defects: list[dict[str, object]] = []
    for spec in _VALIDATORS:
        scenario_suffix = shared_suffix if spec.scenario_mode == "shared" else mwr_suffix
        run = _run_validator(
            repo_root=repo_root,
            output_dir=output_dir,
            spec=spec,
            skip_seed=args.skip_seed,
            scenario_suffix=scenario_suffix,
            core_ingestion_base_url=args.core_ingestion_base_url,
            core_query_base_url=args.core_query_base_url,
            performance_base_url=args.performance_base_url,
        )
        validator_runs.append(run)
        result_payload = run["result"]
        if isinstance(result_payload, dict):
            performance = result_payload.get("performance")
            if isinstance(performance, dict):
                performance_defects = performance.get("defects")
                if isinstance(performance_defects, list):
                    for defect in performance_defects:
                        if isinstance(defect, dict):
                            defects.append({"validator": spec.key, **defect})
            core_defects = result_payload.get("core_defects")
            if isinstance(core_defects, list):
                for defect in core_defects:
                    if isinstance(defect, dict):
                        defects.append({"validator": spec.key, **defect})

    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "status": "failed" if defects else "passed",
        "mode": "reused_existing" if args.skip_seed else "fresh_seeded",
        "shared_scenario_suffix": shared_suffix,
        "mwr_scenario_suffix": mwr_suffix,
        "validators": [
            {
                key: value
                for key, value in run.items()
                if key not in {"stdout", "stderr", "result"}
            }
            for run in validator_runs
        ],
        "defects": defects,
    }

    _write_outputs(
        summary,
        output_json=repo_root / args.output_json,
        output_markdown=repo_root / args.output_markdown,
    )
    print(json.dumps(summary, indent=2))
    return 1 if defects else 0


if __name__ == "__main__":
    raise SystemExit(main())
