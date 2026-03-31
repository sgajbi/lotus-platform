from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPOS_PATH = ROOT / "automation" / "repos.json"
DEFAULT_OUTPUT_JSON = ROOT / "output" / "service-addressing.json"
DEFAULT_OUTPUT_MD = ROOT / "output" / "service-addressing.md"


@dataclass(frozen=True)
class RepoConfig:
    name: str
    path: Path


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_repo_configs(path: Path) -> dict[str, RepoConfig]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload if isinstance(payload, list) else payload.get("repositories", [])
    return {
        entry["name"]: RepoConfig(name=entry["name"], path=Path(entry["path"]))
        for entry in entries
    }


def _result(check_id: str, passed: bool, message: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "passed": passed,
        "message": message,
        "evidence": evidence,
    }


def _contains_all(text: str, required: list[str]) -> bool:
    return all(item in text for item in required)


def _contains_none(text: str, forbidden: list[str]) -> bool:
    return all(item not in text for item in forbidden)


def validate_service_addressing(repos_path: Path) -> dict[str, Any]:
    repo_configs = _load_repo_configs(repos_path)
    platform_root = repo_configs["lotus-platform"].path
    workbench_root = repo_configs["lotus-workbench"].path
    gateway_root = repo_configs["lotus-gateway"].path

    platform_runbook = platform_root / "Local Development Runbook.md"
    platform_stack_readme = platform_root / "platform-stack" / "README.md"
    workbench_readme = workbench_root / "README.md"
    workbench_demo = workbench_root / "docs" / "demo" / "README.md"
    gateway_readme = gateway_root / "README.md"
    gateway_demo = gateway_root / "docs" / "demo" / "README.md"
    workbench_api = workbench_root / "src" / "features" / "workbench" / "api.ts"
    workbench_entry = workbench_root / "src" / "app" / "workbench" / "page.tsx"
    workbench_portfolio_api = workbench_root / "src" / "apps" / "portfolio" / "api.ts"
    workbench_performance_page = (
        workbench_root / "src" / "apps" / "performance" / "performance-analytics-page.tsx"
    )
    workbench_bff_route = workbench_root / "src" / "app" / "api" / "bff" / "[...path]" / "route.ts"

    runbook_text = _load_text(platform_runbook)
    platform_stack_text = _load_text(platform_stack_readme)
    workbench_readme_text = _load_text(workbench_readme)
    workbench_demo_text = _load_text(workbench_demo)
    gateway_readme_text = _load_text(gateway_readme)
    gateway_demo_text = _load_text(gateway_demo)

    checks = [
        _result(
            "platform_runbook_defines_canonical_dev_hostnames",
            _contains_all(
                runbook_text,
                [
                    "gateway.dev.lotus",
                    "workbench.dev.lotus",
                    "manage.dev.lotus",
                    "performance.dev.lotus",
                ],
            ),
            "Local Development Runbook defines canonical environment-scoped service identities for the Phase A local stack.",
            [str(platform_runbook)],
        ),
        _result(
            "platform_runbook_drops_host_docker_internal",
            _contains_none(runbook_text, ["host.docker.internal"]),
            "Local Development Runbook no longer uses host.docker.internal as the canonical service identity model.",
            [str(platform_runbook)],
        ),
        _result(
            "platform_stack_readme_advertises_canonical_hostnames",
            _contains_all(platform_stack_text, ["gateway.dev.lotus", "workbench.dev.lotus"]),
            "platform-stack README advertises canonical service hostnames instead of raw ports as the primary operator contract.",
            [str(platform_stack_readme)],
        ),
        _result(
            "workbench_docs_advertise_gateway_service_identity",
            _contains_all(
                workbench_readme_text + "\n" + workbench_demo_text,
                ["gateway.dev.lotus", "workbench.dev.lotus"],
            ),
            "lotus-workbench docs point operators to environment-scoped service URLs for UI and gateway.",
            [str(workbench_readme), str(workbench_demo)],
        ),
        _result(
            "gateway_docs_advertise_gateway_service_identity",
            _contains_all(gateway_readme_text + "\n" + gateway_demo_text, ["gateway.dev.lotus"]),
            "lotus-gateway docs point operators to the gateway service identity rather than raw localhost port mappings.",
            [str(gateway_readme), str(gateway_demo)],
        ),
        _result(
            "workbench_runtime_no_longer_embeds_localhost_gateway_fallbacks",
            all(
                "http://localhost:8100"
                not in _load_text(path)
                for path in [
                    workbench_api,
                    workbench_entry,
                    workbench_portfolio_api,
                    workbench_performance_page,
                    workbench_bff_route,
                ]
            ),
            "lotus-workbench runtime entry points no longer embed localhost gateway fallbacks and instead centralize service addressing.",
            [
                str(workbench_api),
                str(workbench_entry),
                str(workbench_portfolio_api),
                str(workbench_performance_page),
                str(workbench_bff_route),
            ],
        ),
    ]

    failures = [check for check in checks if not check["passed"]]
    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "result": "ok" if not failures else "failed",
        "checks": checks,
        "failed_count": len(failures),
    }


def _write_markdown(output_path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Service Addressing Validation",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Result: {payload['result']}",
        f"- Failed checks: {payload['failed_count']}",
        "",
        "| Check | Passed | Message |",
        "|---|---|---|",
    ]
    for check in payload["checks"]:
        passed = "true" if check["passed"] else "false"
        lines.append(f"| {check['check_id']} | {passed} | {check['message']} |")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos-path", type=Path, default=DEFAULT_REPOS_PATH)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    payload = validate_service_addressing(args.repos_path)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(args.output_markdown, payload)

    print(f"Wrote {args.output_json}")
    print(f"Wrote {args.output_markdown}")
    return 0 if payload["result"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
