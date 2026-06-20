from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE_MANIFEST = ROOT / "automation" / "platform-validation-profiles.json"
DEFAULT_ARTIFACT_DIR = ROOT / "output" / "cross-app"
DEFAULT_OUTPUT_DIR = ROOT / "output" / "demo-readiness" / "platform"

DOMAIN_ASSERTIONS_BY_TARGET = {
    "twr_benchmark": (
        ("performance", "twr_itd_portfolio_base_return"),
        ("performance", "twr_itd_benchmark_base_return"),
        ("performance", "twr_itd_relative_base_return"),
        ("performance", "benchmark_endpoint_itd_base_return"),
    ),
    "returns_series": (
        ("performance", "portfolio_daily_points"),
        ("performance", "benchmark_daily_points"),
        ("performance", "active_daily_points"),
        ("performance", "returns_series_cumulative_portfolio_pct"),
        ("performance", "returns_series_cumulative_benchmark_pct"),
        ("performance", "returns_series_cumulative_active_pct"),
    ),
    "contribution": (
        ("performance", "contribution_total_portfolio_return_pct"),
        ("performance", "contribution_total_pct"),
        ("performance", "summed_position_contribution_pct"),
        ("performance", "twr_total_portfolio_return_pct"),
    ),
    "mwr": (
        ("core", "expected_dietz_return"),
        ("performance", "money_weighted_return"),
        ("performance", "method"),
        ("performance", "input_mode"),
    ),
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _profile_targets(profile_manifest: dict[str, Any], profile_name: str) -> list[dict[str, Any]]:
    for profile in profile_manifest.get("profiles", []):
        if isinstance(profile, dict) and profile.get("name") == profile_name:
            targets = profile.get("targets", [])
            return [target for target in targets if isinstance(target, dict)]
    raise ValueError(f"Unsupported validation profile: {profile_name}")


def _target_payload_path(target_name: str, artifact_dir: Path) -> Path:
    return artifact_dir / {
        "baseline": "core-performance-baseline-validation.json",
        "twr_benchmark": "core-performance-twr-benchmark-validation.json",
        "returns_series": "core-performance-returns-series-validation.json",
        "contribution": "core-performance-contribution-validation.json",
        "mwr": "core-performance-mwr-validation.json",
    }[target_name]


def _nested_value(payload: dict[str, Any], path: tuple[str, str]) -> Any:
    section = payload.get(path[0])
    if not isinstance(section, dict):
        return None
    return section.get(path[1])


def _non_empty(value: Any) -> bool:
    return value is not None and value != ""


def _append_status_assertion(result: dict[str, Any], payload: dict[str, Any]) -> None:
    if payload.get("status") != "passed":
        result["issues"].append(f"validation status is {payload.get('status', 'unknown')}")
    else:
        result["assertions"].append("validation status passed")


def _append_seed_mode_assertion(
    result: dict[str, Any],
    payload: dict[str, Any],
    expected_scenario_seed_mode: str | None,
) -> None:
    if not expected_scenario_seed_mode:
        return
    if payload.get("scenario_seed_mode") != expected_scenario_seed_mode:
        result["issues"].append(
            "scenario_seed_mode expected "
            f"{expected_scenario_seed_mode} but found {payload.get('scenario_seed_mode', 'unknown')}"
        )
        return
    result["assertions"].append(f"scenario seed mode is {expected_scenario_seed_mode}")


def _append_scenario_assertion(result: dict[str, Any], payload: dict[str, Any]) -> None:
    scenario = payload.get("scenario")
    if not isinstance(scenario, dict) or not scenario.get("portfolio_id"):
        result["issues"].append("scenario.portfolio_id is missing")
        return
    result["assertions"].append("scenario portfolio is present")
    result["portfolio_id"] = scenario["portfolio_id"]


def _validation_defects(payload: dict[str, Any]) -> list[dict[str, Any]]:
    defects = []
    performance = payload.get("performance")
    if isinstance(performance, dict) and isinstance(performance.get("defects"), list):
        defects.extend(item for item in performance["defects"] if isinstance(item, dict))
    core_defects = payload.get("core_defects")
    if isinstance(core_defects, list):
        defects.extend(item for item in core_defects if isinstance(item, dict))
    return defects


def _append_defect_assertion(result: dict[str, Any], payload: dict[str, Any]) -> None:
    defects = _validation_defects(payload)
    if defects:
        result["issues"].append(f"validation emitted {len(defects)} defect(s)")
        result["defects"] = defects
        return
    result["assertions"].append("no validation defects emitted")


def _append_domain_figure_assertions(
    result: dict[str, Any],
    payload: dict[str, Any],
    target_name: str,
) -> None:
    for figure_path in DOMAIN_ASSERTIONS_BY_TARGET.get(target_name, ()):
        value = _nested_value(payload, figure_path)
        figure_name = ".".join(figure_path)
        if not _non_empty(value):
            result["issues"].append(f"{figure_name} is missing")
        else:
            result["assertions"].append(f"{figure_name} is present")
            result["domain_figures"][figure_name] = value


def _target_certification(
    *,
    target_name: str,
    payload_path: Path,
    expected_scenario_seed_mode: str | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "target": target_name,
        "artifact_path": str(payload_path),
        "status": "failed",
        "assertions": [],
        "issues": [],
        "domain_figures": {},
    }
    if not payload_path.exists():
        result["issues"].append("validation artifact is missing")
        return result

    try:
        payload = _load_json(payload_path)
    except json.JSONDecodeError as exc:
        result["issues"].append(f"validation artifact is not valid JSON: {exc}")
        return result

    _append_status_assertion(result, payload)
    _append_seed_mode_assertion(result, payload, expected_scenario_seed_mode)
    _append_scenario_assertion(result, payload)
    _append_defect_assertion(result, payload)
    _append_domain_figure_assertions(result, payload, target_name)
    result["status"] = "passed" if not result["issues"] else "failed"
    return result


def build_certification(
    *,
    profile_name: str,
    artifact_dir: Path,
    output_dir: Path,
    validation_exit_code: int,
    expected_scenario_seed_mode: str | None,
    profile_manifest_path: Path = DEFAULT_PROFILE_MANIFEST,
) -> dict[str, Any]:
    profile_manifest = _load_json(profile_manifest_path)
    target_results = [
        _target_certification(
            target_name=str(target["name"]),
            payload_path=_target_payload_path(str(target["name"]), artifact_dir),
            expected_scenario_seed_mode=expected_scenario_seed_mode,
        )
        for target in _profile_targets(profile_manifest, profile_name)
    ]
    issues = []
    if validation_exit_code != 0:
        issues.append(f"validation command exited {validation_exit_code}")
    issues.extend(
        f"{target['target']}: {issue}"
        for target in target_results
        for issue in target["issues"]
    )
    certification = {
        "certification_id": "platform-demo-readiness",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "profile": profile_name,
        "artifact_dir": str(artifact_dir),
        "validation_exit_code": validation_exit_code,
        "gate_posture": "report_only",
        "certification_status": "passed" if not issues else "failed",
        "targets": target_results,
        "issues": issues,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "platform-demo-readiness-certification.json").write_text(
        json.dumps(certification, indent=2),
        encoding="utf-8",
    )
    return certification


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review platform demo-readiness validation artifacts."
    )
    parser.add_argument("--profile", default="core-performance-green-lanes")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--validation-exit-code", type=int, default=0)
    parser.add_argument("--expected-scenario-seed-mode", default="fresh_seeded")
    args = parser.parse_args()

    certification = build_certification(
        profile_name=args.profile,
        artifact_dir=args.artifact_dir,
        output_dir=args.output_dir,
        validation_exit_code=args.validation_exit_code,
        expected_scenario_seed_mode=args.expected_scenario_seed_mode,
    )
    print(json.dumps(certification, indent=2))
    return 0 if certification["certification_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
