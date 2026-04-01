from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from core_performance_cross_app_validation import (
    ValidationConfig,
    _build_expected_posture,
    run_validation,
)


def _write_result_artifact(result: dict, output_path: Path | None) -> None:
    if output_path is None:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")


def _build_execution_failure_result(
    scenario_id: str, attempts: int, error: str
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "result": "failed",
        "attempts": attempts,
        "expected_posture": _build_expected_posture(
            expected_status="pass",
            expectation_met=False,
            posture="scenario_execution_failed",
            issue_reference=None,
            expected_failed_core_checks=[],
            actual_failed_core_checks=[],
            expected_failed_performance_checks=[],
            actual_failed_performance_checks=[],
        ),
        "error": error,
        "failed_core_checks": [],
        "failed_performance_checks": [],
    }


def _run_scenario_with_retries(
    config: ValidationConfig, scenario_path: Path, max_attempts: int
) -> dict[str, Any]:
    last_error: str | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            result = run_validation(config, scenario_path, output_path=None)
            result["attempts"] = attempt
            return result
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            if attempt < max_attempts:
                time.sleep(2)
    if last_error is None:
        raise AssertionError("Scenario retry loop exited without a result or error.")
    return _build_execution_failure_result(
        scenario_id=scenario_path.stem,
        attempts=max_attempts,
        error=last_error,
    )


def _summarize_suite_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [result for result in results if result["result"] != "ok"]
    expectation_failures = [
        result
        for result in results
        if not result["expected_posture"]["expectation_met"]
    ]
    posture_counts: dict[str, int] = {}
    for result in results:
        posture = result["expected_posture"]["posture"]
        posture_counts[posture] = posture_counts.get(posture, 0) + 1
    return {
        "suite": "core-performance-cross-app",
        "scenario_count": len(results),
        "passed_count": len(results) - len(failed),
        "failed_count": len(failed),
        "expectation_met_count": len(results) - len(expectation_failures),
        "expectation_failed_count": len(expectation_failures),
        "posture_counts": posture_counts,
        "result": "ok" if not expectation_failures else "failed",
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the full lotus-core -> lotus-performance cross-app scenario suite."
    )
    parser.add_argument(
        "--scenarios-dir",
        default="automation/scenarios/core-performance",
    )
    parser.add_argument("--ingestion-url", default="http://core-ingestion.dev.lotus")
    parser.add_argument("--query-control-plane-url", default="http://core-control.dev.lotus")
    parser.add_argument("--performance-url", default="http://performance.dev.lotus")
    parser.add_argument("--timeout-seconds", type=int, default=420)
    parser.add_argument("--poll-interval-seconds", type=float, default=2.0)
    parser.add_argument("--scenario-max-attempts", type=int, default=2)
    parser.add_argument(
        "--output",
        default="output/core-performance-cross-app/suite-latest.json",
    )
    args = parser.parse_args()

    config = ValidationConfig(
        ingestion_url=args.ingestion_url,
        query_control_plane_url=args.query_control_plane_url,
        performance_url=args.performance_url,
        timeout_seconds=args.timeout_seconds,
        poll_interval_seconds=args.poll_interval_seconds,
    )

    scenario_paths = sorted(Path(args.scenarios_dir).glob("*.json"))
    results: list[dict[str, Any]] = []
    for scenario_path in scenario_paths:
        results.append(
            _run_scenario_with_retries(config, scenario_path, args.scenario_max_attempts)
        )

    suite_result = _summarize_suite_results(results)
    _write_result_artifact(suite_result, Path(args.output) if args.output else None)
    print(json.dumps(suite_result, indent=2))
    return 0 if suite_result["result"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
