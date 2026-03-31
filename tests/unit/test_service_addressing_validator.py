from __future__ import annotations

import json
from pathlib import Path

from automation.validate_service_addressing import validate_service_addressing


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_validate_service_addressing_accepts_canonical_hostnames(tmp_path: Path) -> None:
    platform = tmp_path / "lotus-platform"
    workbench = tmp_path / "lotus-workbench"
    gateway = tmp_path / "lotus-gateway"

    _write_text(
        platform / "Local Development Runbook.md",
        "gateway.dev.lotus\nworkbench.dev.lotus\nmanage.dev.lotus\nperformance.dev.lotus\n",
    )
    _write_text(
        platform / "platform-stack" / "README.md",
        "gateway.dev.lotus\nworkbench.dev.lotus\n",
    )
    _write_text(workbench / "README.md", "gateway.dev.lotus\nworkbench.dev.lotus\n")
    _write_text(workbench / "docs" / "demo" / "README.md", "gateway.dev.lotus\nworkbench.dev.lotus\n")
    _write_text(gateway / "README.md", "gateway.dev.lotus\n")
    _write_text(gateway / "docs" / "demo" / "README.md", "gateway.dev.lotus\n")
    _write_text(workbench / "src" / "features" / "workbench" / "api.ts", 'const base = "http://gateway.dev.lotus";\n')
    _write_text(workbench / "src" / "app" / "workbench" / "page.tsx", 'const base = "http://gateway.dev.lotus";\n')
    _write_text(workbench / "src" / "apps" / "portfolio" / "api.ts", 'const base = "http://gateway.dev.lotus";\n')
    _write_text(
        workbench / "src" / "apps" / "performance" / "performance-analytics-page.tsx",
        'const base = "http://gateway.dev.lotus";\n',
    )
    _write_text(
        workbench / "src" / "app" / "api" / "bff" / "[...path]" / "route.ts",
        'const base = "http://gateway.dev.lotus";\n',
    )

    repos_path = tmp_path / "repos.json"
    repos_path.write_text(
        json.dumps(
            [
                {"name": "lotus-platform", "path": str(platform)},
                {"name": "lotus-workbench", "path": str(workbench)},
                {"name": "lotus-gateway", "path": str(gateway)},
            ]
        ),
        encoding="utf-8",
    )

    result = validate_service_addressing(repos_path)

    assert result["result"] == "ok"
    assert result["failed_count"] == 0


def test_validate_service_addressing_flags_port_based_drift(tmp_path: Path) -> None:
    platform = tmp_path / "lotus-platform"
    workbench = tmp_path / "lotus-workbench"
    gateway = tmp_path / "lotus-gateway"

    _write_text(
        platform / "Local Development Runbook.md",
        "http://localhost:3000\nhttp://host.docker.internal:8100\n",
    )
    _write_text(platform / "platform-stack" / "README.md", "http://localhost:8100\n")
    _write_text(workbench / "README.md", "http://127.0.0.1:3000\n")
    _write_text(workbench / "docs" / "demo" / "README.md", "http://127.0.0.1:3000\n")
    _write_text(gateway / "README.md", "http://127.0.0.1:8100\n")
    _write_text(gateway / "docs" / "demo" / "README.md", "http://127.0.0.1:8100\n")
    _write_text(workbench / "src" / "features" / "workbench" / "api.ts", 'const base = "http://localhost:8100";\n')
    _write_text(workbench / "src" / "app" / "workbench" / "page.tsx", 'const base = "http://localhost:8100";\n')
    _write_text(workbench / "src" / "apps" / "portfolio" / "api.ts", 'const base = "http://localhost:8100";\n')
    _write_text(
        workbench / "src" / "apps" / "performance" / "performance-analytics-page.tsx",
        'const base = "http://localhost:8100";\n',
    )
    _write_text(
        workbench / "src" / "app" / "api" / "bff" / "[...path]" / "route.ts",
        'const base = "http://localhost:8100";\n',
    )

    repos_path = tmp_path / "repos.json"
    repos_path.write_text(
        json.dumps(
            [
                {"name": "lotus-platform", "path": str(platform)},
                {"name": "lotus-workbench", "path": str(workbench)},
                {"name": "lotus-gateway", "path": str(gateway)},
            ]
        ),
        encoding="utf-8",
    )

    result = validate_service_addressing(repos_path)

    assert result["result"] == "failed"
    assert result["failed_count"] > 0
    failed_ids = {check["check_id"] for check in result["checks"] if not check["passed"]}
    assert "platform_runbook_drops_host_docker_internal" in failed_ids
    assert "workbench_runtime_no_longer_embeds_localhost_gateway_fallbacks" in failed_ids
