from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationConfig:
    ingestion_url: str
    query_control_plane_url: str
    performance_url: str
    timeout_seconds: int
    poll_interval_seconds: float


def _post_json(
    url: str, payload: dict[str, Any]
) -> tuple[int, dict[str, Any] | list[Any] | str]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        parsed = json.loads(body) if body else body
        return exc.code, parsed


def _poll_until(
    description: str, timeout_seconds: int, poll_interval: float, predicate
):
    deadline = time.time() + timeout_seconds
    last_value = None
    while time.time() < deadline:
        last_value = predicate()
        if last_value is not None:
            return last_value
        time.sleep(poll_interval)
    raise AssertionError(
        f"{description} did not converge within {timeout_seconds}s: {last_value}"
    )


def _load_scenario(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _substitute_tokens(value: Any, tokens: dict[str, str]) -> Any:
    if isinstance(value, str):
        result = value
        for key, replacement in tokens.items():
            result = result.replace(f"{{{{{key}}}}}", replacement)
        return result
    if isinstance(value, list):
        return [_substitute_tokens(item, tokens) for item in value]
    if isinstance(value, dict):
        return {key: _substitute_tokens(item, tokens) for key, item in value.items()}
    return value


def _day_list(start_day: str, end_day: str) -> list[str]:
    current = date.fromisoformat(start_day)
    end = date.fromisoformat(end_day)
    days: list[str] = []
    while current <= end:
        days.append(current.isoformat())
        current = current.fromordinal(current.toordinal() + 1)
    return days


def _assert_ingest_accepted(
    config: ValidationConfig, endpoint: str, payload: dict[str, Any]
) -> None:
    status, body = _post_json(config.ingestion_url.rstrip("/") + endpoint, payload)
    if status != 202:
        raise AssertionError(f"Ingest {endpoint} failed with {status}: {body}")


def _query_reference(
    config: ValidationConfig, portfolio_id: str, as_of_date: str
) -> dict[str, Any]:
    status, body = _post_json(
        config.query_control_plane_url.rstrip("/")
        + f"/integration/portfolios/{portfolio_id}/analytics/reference",
        {"as_of_date": as_of_date, "consumer_system": "lotus-platform-validator"},
    )
    if status != 200:
        raise AssertionError(f"analytics/reference query failed with {status}: {body}")
    return body


def _query_portfolio_timeseries(
    config: ValidationConfig, portfolio_id: str, start_date: str, end_date: str
) -> dict[str, Any]:
    status, body = _post_json(
        config.query_control_plane_url.rstrip("/")
        + f"/integration/portfolios/{portfolio_id}/analytics/portfolio-timeseries",
        {
            "as_of_date": end_date,
            "window": {"start_date": start_date, "end_date": end_date},
            "consumer_system": "lotus-platform-validator",
            "frequency": "daily",
            "page": {"page_size": 200},
        },
    )
    if status != 200:
        raise AssertionError(f"portfolio-timeseries query failed with {status}: {body}")
    return body


def _query_position_timeseries(
    config: ValidationConfig, portfolio_id: str, start_date: str, end_date: str
) -> dict[str, Any]:
    status, body = _post_json(
        config.query_control_plane_url.rstrip("/")
        + f"/integration/portfolios/{portfolio_id}/analytics/position-timeseries",
        {
            "as_of_date": end_date,
            "window": {"start_date": start_date, "end_date": end_date},
            "consumer_system": "lotus-platform-validator",
            "frequency": "daily",
            "dimensions": [],
            "include_cash_flows": True,
            "filters": {},
            "page": {"page_size": 200},
        },
    )
    if status != 200:
        raise AssertionError(f"position-timeseries query failed with {status}: {body}")
    return body


def _position_dates_by_security(
    position_payload: dict[str, Any],
) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in position_payload["rows"]:
        grouped[row["security_id"]].append(row["valuation_date"])
    return {security_id: sorted(dates) for security_id, dates in grouped.items()}


def _normalize_decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _sum_external_flows(cash_flows: list[dict[str, Any]]) -> Decimal:
    total = Decimal("0")
    for flow in cash_flows:
        flow_type = str(
            flow.get("cash_flow_type") or flow.get("category") or ""
        ).lower()
        if flow_type == "external_flow":
            total += _normalize_decimal(flow.get("amount", 0))
    return total


def _portfolio_external_flow_by_date(
    portfolio_payload: dict[str, Any],
) -> dict[str, Decimal]:
    result: dict[str, Decimal] = {}
    for observation in portfolio_payload["observations"]:
        result[observation["valuation_date"]] = sum(
            _normalize_decimal(flow.get("amount", 0))
            for flow in observation.get("cash_flows", [])
            if str(flow.get("cash_flow_type") or flow.get("category") or "").lower()
            == "external_flow"
        )
    return result


def _position_external_flow_by_security_and_date(
    position_payload: dict[str, Any],
) -> dict[tuple[str, str], Decimal]:
    result: dict[tuple[str, str], Decimal] = {}
    for row in position_payload["rows"]:
        result[(row["security_id"], row["valuation_date"])] = _sum_external_flows(
            row.get("cash_flows", [])
        )
    return result


def _evaluate_core_invariants(
    scenario: dict[str, Any],
    portfolio_payload: dict[str, Any],
    position_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    invariants = scenario["core_invariants"]
    expected_seeded_dates = invariants["expected_seeded_dates"]
    observed_portfolio_dates = sorted(
        obs["valuation_date"] for obs in portfolio_payload["observations"]
    )
    observed_position_dates_by_security = _position_dates_by_security(position_payload)
    portfolio_external_by_date = _portfolio_external_flow_by_date(portfolio_payload)
    position_external_by_security_and_date = (
        _position_external_flow_by_security_and_date(position_payload)
    )

    checks: list[dict[str, Any]] = []
    checks.append(
        {
            "check": "portfolio_dates_complete",
            "passed": observed_portfolio_dates == expected_seeded_dates,
            "expected": expected_seeded_dates,
            "actual": observed_portfolio_dates,
        }
    )

    for security_id, observed_dates in observed_position_dates_by_security.items():
        checks.append(
            {
                "check": f"position_dates_complete:{security_id}",
                "passed": observed_dates == expected_seeded_dates,
                "expected": expected_seeded_dates,
                "actual": observed_dates,
            }
        )

    for valuation_date, expected_amount in invariants[
        "expected_portfolio_external_flow_by_date"
    ].items():
        actual_amount = portfolio_external_by_date.get(valuation_date, Decimal("0"))
        expected_decimal = _normalize_decimal(expected_amount)
        checks.append(
            {
                "check": f"portfolio_external_flow:{valuation_date}",
                "passed": actual_amount == expected_decimal,
                "expected": str(expected_decimal),
                "actual": str(actual_amount),
            }
        )

    for expectation in invariants[
        "expected_position_external_flow_by_security_and_date"
    ]:
        security_id = expectation["security_id"]
        valuation_date = expectation["valuation_date"]
        expected_decimal = _normalize_decimal(expectation["expected_external_flow"])
        actual_amount = position_external_by_security_and_date.get(
            (security_id, valuation_date), Decimal("0")
        )
        checks.append(
            {
                "check": f"position_external_flow:{security_id}:{valuation_date}",
                "passed": actual_amount == expected_decimal,
                "expected": str(expected_decimal),
                "actual": str(actual_amount),
            }
        )

    if invariants.get("require_position_external_flow_sum_to_match_portfolio", False):
        for valuation_date, portfolio_amount in portfolio_external_by_date.items():
            position_amount = sum(
                amount
                for (
                    security_id,
                    flow_date,
                ), amount in position_external_by_security_and_date.items()
                if flow_date == valuation_date
            )
            checks.append(
                {
                    "check": f"position_external_flow_sum_matches_portfolio:{valuation_date}",
                    "passed": position_amount == portfolio_amount,
                    "expected": str(portfolio_amount),
                    "actual": str(position_amount),
                }
            )

    return checks


def _post_performance_request(
    config: ValidationConfig, endpoint: str, payload: dict[str, Any]
) -> tuple[int, Any]:
    return _post_json(config.performance_url.rstrip("/") + endpoint, payload)


def _extract_json_path(payload: Any, path: str) -> Any:
    current = payload
    for part in path.split("."):
        if isinstance(current, dict):
            current = current[part]
        elif isinstance(current, list):
            current = current[int(part)]
        else:
            raise KeyError(path)
    return current


def _evaluate_performance_requests(
    config: ValidationConfig,
    scenario: dict[str, Any],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for request_definition in scenario["performance_requests"]:
        status, body = _post_performance_request(
            config, request_definition["endpoint"], request_definition["payload"]
        )
        expectation = request_definition["expectations"]
        request_result: dict[str, Any] = {
            "request_id": request_definition["request_id"],
            "endpoint": request_definition["endpoint"],
            "status": status,
            "passed": status == expectation["expected_status"],
            "response_excerpt": body,
            "checks": [],
        }
        if status == expectation["expected_status"] and isinstance(body, dict):
            if "daily_period_labels" in expectation:
                actual_labels = [
                    item["period"]
                    for item in _extract_json_path(
                        body,
                        "results_by_period.EXPLICIT.portfolio.breakdowns.daily",
                    )
                ]
                request_result["checks"].append(
                    {
                        "check": "daily_period_labels",
                        "passed": actual_labels == expectation["daily_period_labels"],
                        "expected": expectation["daily_period_labels"],
                        "actual": actual_labels,
                    }
                )
            if "daily_dates" in expectation:
                actual_dates = [
                    item["date"]
                    for item in _extract_json_path(
                        body, "results_by_period.EXPLICIT.timeseries"
                    )
                ]
                request_result["checks"].append(
                    {
                        "check": "daily_dates",
                        "passed": actual_dates == expectation["daily_dates"],
                        "expected": expectation["daily_dates"],
                        "actual": actual_dates,
                    }
                )
            for json_expectation in expectation.get("json_checks", []):
                actual_value = _extract_json_path(body, json_expectation["path"])
                check_name = json_expectation.get("name", json_expectation["path"])
                if "expected" in json_expectation:
                    expected_value = json_expectation["expected"]
                    passed = actual_value == expected_value
                else:
                    expected_value = json_expectation["approx"]
                    tolerance = float(json_expectation.get("tolerance", 1e-6))
                    passed = (
                        abs(float(actual_value) - float(expected_value)) <= tolerance
                    )
                request_result["checks"].append(
                    {
                        "check": check_name,
                        "passed": passed,
                        "expected": expected_value,
                        "actual": actual_value,
                    }
                )
            request_result["passed"] = request_result["passed"] and all(
                check["passed"] for check in request_result["checks"]
            )
        results.append(request_result)
    return results


def _failed_performance_check_names(
    failed_performance_checks: list[dict[str, Any]],
) -> list[str]:
    return sorted(
        f"{result['request_id']}:{check['check']}"
        for result in failed_performance_checks
        for check in result["checks"]
        if not check["passed"]
    )


def _build_expected_posture(
    *,
    expected_status: str,
    expectation_met: bool,
    posture: str,
    issue_reference: str | None,
    expected_failed_core_checks: list[str],
    actual_failed_core_checks: list[str],
    expected_failed_performance_checks: list[str],
    actual_failed_performance_checks: list[str],
) -> dict[str, Any]:
    return {
        "expected_status": expected_status,
        "expectation_met": expectation_met,
        "posture": posture,
        "issue_reference": issue_reference,
        "expected_failed_core_checks": expected_failed_core_checks,
        "actual_failed_core_checks": actual_failed_core_checks,
        "expected_failed_performance_checks": expected_failed_performance_checks,
        "actual_failed_performance_checks": actual_failed_performance_checks,
    }


def _evaluate_expected_posture(
    scenario: dict[str, Any],
    failed_core_checks: list[dict[str, Any]],
    failed_performance_checks: list[dict[str, Any]],
) -> dict[str, Any]:
    expected_validation = scenario.get("expected_validation", {"status": "pass"})
    expected_status = expected_validation.get("status", "pass")
    failed_core_check_names = sorted(check["check"] for check in failed_core_checks)
    expected_failed_core_checks = sorted(
        expected_validation.get("expected_failed_core_checks", [])
    )
    actual_failed_performance_checks = _failed_performance_check_names(
        failed_performance_checks
    )
    expected_failed_performance_checks = sorted(
        expected_validation.get("expected_failed_performance_checks", [])
    )
    issue_reference = expected_validation.get("issue_reference")

    if expected_status == "pass":
        expectation_met = (
            not failed_core_checks and not actual_failed_performance_checks
        )
        return _build_expected_posture(
            expected_status=expected_status,
            expectation_met=expectation_met,
            posture="pass" if expectation_met else "unexpected_failure",
            issue_reference=issue_reference,
            expected_failed_core_checks=expected_failed_core_checks,
            actual_failed_core_checks=failed_core_check_names,
            expected_failed_performance_checks=expected_failed_performance_checks,
            actual_failed_performance_checks=actual_failed_performance_checks,
        )

    if expected_status == "known_core_issue":
        if (
            failed_core_check_names == expected_failed_core_checks
            and actual_failed_performance_checks == expected_failed_performance_checks
        ):
            posture = "known_issue_observed"
            expectation_met = True
        elif not failed_core_check_names and not actual_failed_performance_checks:
            posture = "known_issue_resolved"
            expectation_met = False
        elif (
            failed_core_check_names == expected_failed_core_checks
            and actual_failed_performance_checks != expected_failed_performance_checks
        ):
            posture = "unexpected_variation"
            expectation_met = False
        elif failed_core_check_names != expected_failed_core_checks:
            posture = "unexpected_failure"
            expectation_met = False
        else:
            posture = "unexpected_variation"
            expectation_met = False
        return _build_expected_posture(
            expected_status=expected_status,
            expectation_met=expectation_met,
            posture=posture,
            issue_reference=issue_reference,
            expected_failed_core_checks=expected_failed_core_checks,
            actual_failed_core_checks=failed_core_check_names,
            expected_failed_performance_checks=expected_failed_performance_checks,
            actual_failed_performance_checks=actual_failed_performance_checks,
        )

    raise AssertionError(f"Unsupported expected_validation.status: {expected_status}")


def _write_result_artifact(result: dict[str, Any], output_path: Path | None) -> None:
    if output_path is None:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")


def run_validation(
    config: ValidationConfig, scenario_path: Path, output_path: Path | None = None
) -> dict[str, Any]:
    raw_scenario = _load_scenario(scenario_path)
    suffix = uuid.uuid4().hex[:8].upper()
    tokens = {"SUFFIX": suffix}
    scenario = _substitute_tokens(raw_scenario, tokens)

    seed_start = scenario["seed_window"]["start_date"]
    seed_end = scenario["seed_window"]["end_date"]
    seeded_days = _day_list(seed_start, seed_end)
    portfolio = scenario["portfolio"]

    _assert_ingest_accepted(config, "/ingest/portfolios", {"portfolios": [portfolio]})
    _assert_ingest_accepted(
        config, "/ingest/instruments", {"instruments": scenario["instruments"]}
    )
    if scenario["fx_rates"]:
        _assert_ingest_accepted(
            config, "/ingest/fx-rates", {"fx_rates": scenario["fx_rates"]}
        )
    _assert_ingest_accepted(
        config,
        "/ingest/business-dates",
        {"business_dates": [{"business_date": seeded_days[0]}]},
    )
    _assert_ingest_accepted(
        config, "/ingest/transactions", {"transactions": scenario["transactions"]}
    )
    _assert_ingest_accepted(
        config, "/ingest/market-prices", {"market_prices": scenario["market_prices"]}
    )
    _assert_ingest_accepted(
        config,
        "/ingest/business-dates",
        {"business_dates": [{"business_date": day} for day in seeded_days[1:]]},
    )

    def _reference_ready() -> dict[str, Any] | None:
        payload = _query_reference(config, portfolio["portfolio_id"], seed_end)
        return payload if payload.get("performance_end_date") == seed_end else None

    def _portfolio_ready() -> dict[str, Any] | None:
        payload = _query_portfolio_timeseries(
            config, portfolio["portfolio_id"], seed_start, seed_end
        )
        observed_dates = sorted(
            obs["valuation_date"] for obs in payload["observations"]
        )
        return payload if observed_dates == seeded_days else None

    def _position_ready() -> dict[str, Any] | None:
        payload = _query_position_timeseries(
            config, portfolio["portfolio_id"], seed_start, seed_end
        )
        observed_dates = _position_dates_by_security(payload)
        if all(dates == seeded_days for dates in observed_dates.values()):
            return payload
        return None

    reference_payload = _poll_until(
        "analytics reference maturity",
        config.timeout_seconds,
        config.poll_interval_seconds,
        _reference_ready,
    )
    portfolio_payload = _poll_until(
        "portfolio timeseries maturity",
        config.timeout_seconds,
        config.poll_interval_seconds,
        _portfolio_ready,
    )
    position_payload = _poll_until(
        "position timeseries maturity",
        config.timeout_seconds,
        config.poll_interval_seconds,
        _position_ready,
    )

    core_checks = _evaluate_core_invariants(
        scenario, portfolio_payload, position_payload
    )
    performance_checks = _evaluate_performance_requests(config, scenario)
    failed_core_checks = [check for check in core_checks if not check["passed"]]
    failed_performance_checks = [
        result
        for result in performance_checks
        if not result["passed"]
        or any(not check["passed"] for check in result["checks"])
    ]
    expected_posture = _evaluate_expected_posture(
        scenario, failed_core_checks, failed_performance_checks
    )

    result = {
        "scenario_id": scenario["scenario_id"],
        "description": scenario.get("description", ""),
        "portfolio_id": portfolio["portfolio_id"],
        "seeded_days": seeded_days,
        "reference": {
            "performance_end_date": reference_payload["performance_end_date"],
            "resolved_as_of_date": reference_payload["resolved_as_of_date"],
        },
        "core_checks": core_checks,
        "performance_checks": performance_checks,
        "result": "ok"
        if not failed_core_checks and not failed_performance_checks
        else "failed",
        "expected_posture": expected_posture,
        "failed_core_checks": failed_core_checks,
        "failed_performance_checks": failed_performance_checks,
    }
    _write_result_artifact(result, output_path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a reusable lotus-core -> lotus-performance cross-app validation scenario."
    )
    parser.add_argument(
        "--scenario",
        default="automation/scenarios/core-performance/fund_buy_foreign_stock_explicit_window.json",
    )
    parser.add_argument("--ingestion-url", default="http://127.0.0.1:8200")
    parser.add_argument("--query-control-plane-url", default="http://127.0.0.1:8202")
    parser.add_argument("--performance-url", default="http://127.0.0.1:8002")
    parser.add_argument("--timeout-seconds", type=int, default=240)
    parser.add_argument("--poll-interval-seconds", type=float, default=2.0)
    parser.add_argument(
        "--output",
        default="output/core-performance-cross-app/latest.json",
    )
    args = parser.parse_args()

    config = ValidationConfig(
        ingestion_url=args.ingestion_url,
        query_control_plane_url=args.query_control_plane_url,
        performance_url=args.performance_url,
        timeout_seconds=args.timeout_seconds,
        poll_interval_seconds=args.poll_interval_seconds,
    )
    scenario_path = Path(args.scenario)
    output_path = Path(args.output) if args.output else None

    try:
        result = run_validation(config, scenario_path, output_path=output_path)
    except Exception as exc:  # noqa: BLE001
        failure = {
            "result": "failed",
            "scenario_id": scenario_path.stem,
            "error": str(exc),
        }
        _write_result_artifact(failure, output_path)
        print(json.dumps(failure, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0 if result["result"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
